#!/usr/bin/env python3
"""Guarded launcher for the explicitly authorized V81 V62 continuation.

Default mode is verification only. Training requires BOTH:
- --execute
- MINI_KUZAI_V81_TRAINING_ENABLED=YES

The actual optimizer work is delegated unchanged to the frozen V62 CLI with
--resume. This launcher does not modify the V62 trainer implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
V62_CLI = REPO / "tools" / "train_v62_margin.py"
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")

AUTH_DIR = REPO / "reviews" / "smoltalk-v81-v62-continuation-authorization"
AUTH = AUTH_DIR / "TRAINING-AUTHORIZATION-001.json"
FREEZE = AUTH_DIR / "CONTINUATION-FREEZE-001.json"
REPORT = AUTH_DIR / "REPORT-001.json"

START_RECEIPT = REPO / "automation" / "dev-flow" / "receipts" / "V81-start.json"
READINESS = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V81-V62-CONTINUATION-READINESS-001.json"
)

MAX_STEPS = 145
MAX_EXPOSURE = 1181664
START_STEPS = 69
START_EXPOSURE = 597982


class LaunchError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise LaunchError(message)


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        fail(f"Missing or unsafe JSON: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LaunchError(f"Invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        fail(f"Expected JSON object: {path}")
    return value


def canonical_sha(value: dict) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _progress_bar(current: int, total: int, width: int = 34) -> str:
    if total <= 0:
        return "[" + ("-" * width) + "]"
    ratio = min(1.0, max(0.0, current / total))
    filled = int(round(ratio * width))
    return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"


def _monitor_training(process: subprocess.Popen, metrics_path: Path) -> None:
    initial_size = metrics_path.stat().st_size if metrics_path.is_file() else 0
    offset = initial_size
    started = time.monotonic()
    last_step = START_STEPS
    last_exposure = START_EXPOSURE
    last_train_loss = None
    last_validation_loss = None
    spinner = "|/-\\"
    spin_index = 0

    while process.poll() is None:
        if metrics_path.is_file():
            try:
                with metrics_path.open(encoding="utf-8") as stream:
                    stream.seek(offset)
                    for raw in stream:
                        if not raw.strip():
                            continue
                        try:
                            row = json.loads(raw)
                        except ValueError:
                            continue
                        if not isinstance(row, dict):
                            continue
                        row_type = row.get("type")
                        if row_type == "train_step":
                            step = int(row.get("step", -1))
                            exposure = int(row.get("exposure_tokens", -1))
                            if step > START_STEPS and exposure >= START_EXPOSURE:
                                last_step = step
                                last_exposure = exposure
                                last_train_loss = float(row["train_loss"])
                        elif row_type == "validation":
                            step = int(row.get("step", -1))
                            if step > START_STEPS:
                                last_validation_loss = float(
                                    row["validation_loss"]
                                )
                    offset = stream.tell()
            except OSError:
                pass

        elapsed = int(time.monotonic() - started)
        if last_step > START_STEPS:
            done = max(0, last_exposure - START_EXPOSURE)
            total = MAX_EXPOSURE - START_EXPOSURE
            pct = min(100.0, done * 100.0 / total)
            loss_text = (
                f"{last_train_loss:.4f}"
                if last_train_loss is not None
                else "-"
            )
            val_text = (
                f"{last_validation_loss:.4f}"
                if last_validation_loss is not None
                else "-"
            )
            line = (
                f"\rV81 TRAIN {_progress_bar(done, total)} "
                f"{pct:6.2f}%  "
                f"step {last_step}/{MAX_STEPS}  "
                f"tokens {last_exposure}/{MAX_EXPOSURE}  "
                f"loss {loss_text}  val {val_text}  "
                f"elapsed {elapsed}s"
            )
        else:
            line = (
                f"\rV81 VERIFY_RUNTIME {spinner[spin_index % len(spinner)]} "
                f"elapsed {elapsed}s"
            )
            spin_index += 1

        print(line, end="", flush=True)
        time.sleep(1.0)

    print()


def verify_authorization() -> str:
    auth = read_json(AUTH)
    freeze = read_json(FREEZE)
    report = read_json(REPORT)
    start = read_json(START_RECEIPT)
    readiness = read_json(READINESS)
    summary = read_json(RUN / "RUN-SUMMARY.json")
    manifest = read_json(RUN / "RUN-MANIFEST.json")

    if (
        auth.get("schema_version") != "v81-v62-continuation-authorization-1"
        or auth.get("status") != "FROZEN"
        or auth.get("authorization_scope")
        != "V81_V62_INITIAL_WINDOW_REMAINDER_ONLY"
        or auth.get("training_authorized") is not True
        or auth.get("training_started") is not False
        or auth.get("blind_test_during_training") is not False
        or auth.get("resume_required") is not True
        or auth.get("max_total_optimizer_steps") != MAX_STEPS
        or auth.get("max_total_exposure_tokens") != MAX_EXPOSURE
        or auth.get("final_review_cycle") != 4
    ):
        fail("V81 training authorization mismatch")

    fingerprint = auth.get("freeze_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        fail("V81 authorization fingerprint invalid")
    if canonical_sha(freeze) != fingerprint:
        fail("V81 continuation freeze fingerprint mismatch")

    if (
        freeze.get("status") != "FROZEN"
        or freeze.get("training_authorized") is not True
        or freeze.get("training_started") is not False
        or freeze.get("resume_required") is not True
        or freeze.get("starting_optimizer_steps") != START_STEPS
        or freeze.get("starting_exposure_tokens") != START_EXPOSURE
        or freeze.get("max_total_optimizer_steps") != MAX_STEPS
        or freeze.get("max_total_exposure_tokens") != MAX_EXPOSURE
        or freeze.get("max_remaining_optimizer_steps") != 76
        or freeze.get("max_remaining_exposure_tokens") != 583682
        or freeze.get("blind_test_during_training") is not False
        or freeze.get("extension_beyond_cycle4_requires_new_protocol") is not True
    ):
        fail("V81 continuation freeze scope mismatch")

    if (
        report.get("status") != "TRAINING_AUTHORIZED_NOT_STARTED"
        or report.get("training_authorized") is not True
        or report.get("training_started") is not False
        or report.get("blind_test_accessed") is not False
    ):
        fail("V81 authorization report mismatch")

    if (
        start.get("command") != "START-DEV-FLOW"
        or start.get("step") != "V81"
        or start.get("status") != "PUBLISHED"
    ):
        fail("V81 START receipt missing or invalid")

    metrics = readiness.get("metrics")
    if (
        readiness.get("step_id")
        != "PHASE03-SMOLTALK-V81-V62-CONTINUATION-READINESS-001"
        or not isinstance(metrics, dict)
        or metrics.get("V81_PASS") != 1
        or metrics.get("TRAINING_AUTHORIZED") != 0
        or metrics.get("TRAINING_STARTED") != 0
        or metrics.get("V81_BLIND_ACCESS") != 0
    ):
        fail("V81 readiness report mismatch")

    if (
        summary.get("status") != "STOPPED"
        or summary.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED"
        or summary.get("optimizer_steps") != START_STEPS
        or summary.get("exposure_tokens") != START_EXPOSURE
        or summary.get("blind_test_accessed") is not False
    ):
        fail("V62 run is not at the authorized resume boundary")

    if (
        manifest.get("status") != "STOPPED"
        or manifest.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED"
        or manifest.get("optimizer_steps") != START_STEPS
        or manifest.get("exposure_tokens") != START_EXPOSURE
        or manifest.get("blind_test_during_training") is not False
    ):
        fail("V62 run manifest is not at the authorized resume boundary")

    if (RUN / ".training.lock").exists():
        fail("Training lock is already active")
    if not PYTHON.is_file() or not os.access(PYTHON, os.X_OK):
        fail("Mini-Kuzai Python environment unavailable")
    if V62_CLI.is_symlink() or not V62_CLI.is_file():
        fail("Frozen V62 training CLI unavailable")

    return fingerprint


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    fingerprint = verify_authorization()

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V81_TRAIN_LAUNCH_PREFLIGHT=PASS")
    print(f"V81_AUTH_FINGERPRINT={fingerprint}")
    print(f"TRAINING_EXECUTE_REQUESTED={int(args.execute)}")
    print("BLIND_ACCESS=0")

    if not args.execute:
        print("TRAINING_STARTED=0")
        print("V81_TRAIN_LAUNCH=DRY_RUN_PASS")
        return 0

    if os.environ.get("MINI_KUZAI_V81_TRAINING_ENABLED") != "YES":
        fail("V81 training live gate is disabled")

    metrics_path = RUN / "metrics.jsonl"
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                str(PYTHON),
                str(V62_CLI),
                "--run-dir",
                str(RUN),
                "--resume",
            ],
            cwd=REPO,
            text=True,
            stdout=log,
            stderr=subprocess.STDOUT,
        )

        try:
            _monitor_training(process, metrics_path)
        except KeyboardInterrupt:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise

        returncode = process.wait()
        log.seek(0)
        output = log.read().strip()

    if returncode != 0:
        detail = output[-4000:] if output else ""
        raise LaunchError(
            "Frozen V62 resume failed"
            + (f": {detail}" if detail else "")
        )

    if output:
        print(output)
    print("V81_TRAIN_LAUNCH=PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LaunchError as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V81_TRAIN_LAUNCH=BLOCKED")
        print(f"ERROR={exc}")
        raise SystemExit(1)
