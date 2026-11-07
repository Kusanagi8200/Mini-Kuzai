#!/usr/bin/env python3
"""V75 scientific runner with automatic numeric failure-status GOGIT.

On success, the scientific runner publishes the immutable V75 scientific GOGIT.
On failure, this wrapper writes a numeric-only local status artifact and invokes
a separate reviewed GOGIT status audit. Raw stdout/stderr is never published.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
RUNNER = ROOT / "tools" / "run_v75_train_fitted_geometry_transfer_001_job.py"
GOGIT = ROOT / "tools" / "gogit_public.py"
STATUS_AUDIT = ROOT / "tools" / "public-audits" / "phase03_v75_run_status_001.py"
STATUS = Path("/root/Mini-Kuzai/runs/v75-scientific-run-status-001.json")
SCIENTIFIC = (
    ROOT
    / "reports"
    / "assistant-results"
    / "history"
    / "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json"
)
STATUS_STEP = "PHASE03-SMOLTALK-V75-RUN-STATUS-003"


def classify(text: str) -> dict:
    lower = text.lower()
    safe_code = 0
    marker = "v75_safe_failure_code="
    if marker in lower:
        tail = lower.split(marker, 1)[1].split()[0].strip(";,:")
        if tail.isdigit():
            safe_code = min(int(tail), 99)
    flags = {
        "V75_RUN_STATUS_TIMEOUT": int("timed out after 300" in lower or "timeoutexpired" in lower),
        "V75_RUN_STATUS_OOM": int("out of memory" in lower or "cuda oom" in lower),
        "V75_RUN_STATUS_SYNC_FAIL": int(
            "not synchronized" in lower
            or "local and remote main differ" in lower
            or "clean main" in lower
        ),
        "V75_RUN_STATUS_PIN_FAIL": int(
            "blob changed" in lower
            or "fingerprint mismatch" in lower
            or "pinned source" in lower
        ),
        "V75_RUN_STATUS_V62_GATE_FAIL": int(
            "v62 frozen checkpoint/stop gate failed" in lower
            or "frozen v62 run" in lower
        ),
        "V75_RUN_STATUS_CPU_TEST_FAIL": int("cpu regression" in lower),
        "V75_RUN_STATUS_PREREQ_FAIL": int(
            "prerequisite report/fingerprint gate failed" in lower
            or "immutable prerequisite" in lower
        ),
        "V75_RUN_STATUS_GEOMETRY_FAIL": int(
            "geometry" in lower
            or "covariance" in lower
            or "eigen" in lower
            or "spectral axis" in lower
        ),
        "V75_RUN_STATUS_REPLAY_FAIL": int(
            "replay" in lower
            or "frozen v73/v74" in lower
        ),
        "V75_RUN_STATUS_GOGIT_FAIL": int("gogit" in lower),
    }
    ordered = (
        ("V75_RUN_STATUS_TIMEOUT", 2),
        ("V75_RUN_STATUS_OOM", 3),
        ("V75_RUN_STATUS_SYNC_FAIL", 4),
        ("V75_RUN_STATUS_PIN_FAIL", 5),
        ("V75_RUN_STATUS_V62_GATE_FAIL", 6),
        ("V75_RUN_STATUS_CPU_TEST_FAIL", 7),
        ("V75_RUN_STATUS_PREREQ_FAIL", 8),
        ("V75_RUN_STATUS_GEOMETRY_FAIL", 9),
        ("V75_RUN_STATUS_REPLAY_FAIL", 10),
        ("V75_RUN_STATUS_GOGIT_FAIL", 11),
    )
    code = 1
    for key, value in ordered:
        if flags[key]:
            code = value
            break
    return {
        "V75_RUN_STATUS_FAILURE_CODE": code,
        "V75_RUN_STATUS_SAFE_FAILURE_CODE": safe_code,
        **flags,
    }


def publish_status(exit_code: int, output: str) -> int:
    flags = classify(output)
    status = {
        "V75_RUN_STATUS_PASS": 0,
        "V75_RUN_STATUS_ATTEMPTED": 1,
        "V75_RUN_STATUS_RUNNER_EXIT": max(0, min(int(exit_code), 255)),
        **flags,
        "V75_RUN_STATUS_SCIENTIFIC_REPORT_PRESENT": int(SCIENTIFIC.is_file()),
    }
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(status, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    p = subprocess.run(
        [
            str(PYTHON),
            str(GOGIT),
            "--step",
            STATUS_STEP,
            "--audit",
            str(STATUS_AUDIT.relative_to(ROOT)),
        ],
        cwd=ROOT,
        check=False,
    )
    return p.returncode


def main() -> int:
    if not PYTHON.is_file() or not RUNNER.is_file() or not STATUS_AUDIT.is_file():
        raise RuntimeError("V75 reviewed run/status tooling missing")
    if SCIENTIFIC.is_file():
        print("V75 scientific GOGIT already present; no rerun performed")
        return 0

    p = subprocess.run(
        [str(PYTHON), str(RUNNER)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    combined = (p.stdout or "") + "\n" + (p.stderr or "")
    if p.returncode == 0 and SCIENTIFIC.is_file():
        STATUS.unlink(missing_ok=True)
        print(p.stdout, end="")
        return 0

    status_rc = publish_status(p.returncode, combined)
    if status_rc:
        print("V75 run failed and status GOGIT publication also failed", file=sys.stderr)
        return 2
    print("V75 run failed; numeric status GOGIT published")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, ValueError, KeyboardInterrupt) as exc:
        print("V75 status wrapper blocked:", str(exc), file=sys.stderr)
        sys.exit(2)
