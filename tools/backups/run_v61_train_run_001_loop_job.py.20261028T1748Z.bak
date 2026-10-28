#!/usr/bin/env python3
"""Run V61 TRAIN RUN 001 to the mandatory cycle-2 review and publish
both the core run audit and EOS calibration audit through GOGIT.

This job is restart-safe after training: if the canonical run has already
stopped correctly, missing GOGIT reports are published without retraining.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENV_PY = Path("/root/Mini-Kuzai/.venv/bin/python")
TRAIN = REPO / "tools" / "train_v61_boundary.py"
GOGIT = REPO / "tools" / "gogit_public.py"

RUN_AUDIT = (
    REPO / "tools" / "public-audits"
    / "phase03_v61_train_run_001.py"
)
EOS_AUDIT = (
    REPO / "tools" / "public-audits"
    / "phase03_v61_train_run_001_eos_calibration.py"
)

RUN_DIR = Path("/root/Mini-Kuzai/runs/v61-boundary-001")
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"
MANIFEST = RUN_DIR / "RUN-MANIFEST.json"
METRICS = RUN_DIR / "metrics.jsonl"
PROBES = RUN_DIR / "validation-probes.jsonl"
CYCLE2 = RUN_DIR / "checkpoint-cycle-02.pt"
CHECKPOINT = RUN_DIR / "checkpoint-last.pt"

RUN_STEP = "PHASE03-SMOLTALK-V61-TRAIN-RUN-001"
EOS_STEP = "PHASE03-SMOLTALK-V61-TRAIN-RUN-001-EOS-CALIBRATION-001"

RUN_HISTORY = (
    REPO / "reports" / "assistant-results" / "history"
    / f"{RUN_STEP}.json"
)
EOS_HISTORY = (
    REPO / "reports" / "assistant-results" / "history"
    / f"{EOS_STEP}.json"
)


def git(*args):
    process = subprocess.run(
        ["git", "-C", str(REPO), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode:
        raise RuntimeError(
            process.stderr.strip()
            or process.stdout.strip()
            or "git failed"
        )
    return process.stdout.strip()


def run_python(*args):
    process = subprocess.run(
        [str(VENV_PY), *map(str, args)],
        cwd=REPO,
        text=True,
        check=False,
    )
    if process.returncode:
        raise RuntimeError(
            f"Subprocess failed with status {process.returncode}"
        )


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def require_clean_synced():
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Expected branch main")
    if git("status", "--porcelain"):
        raise RuntimeError("Clean worktree required")

    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local and remote main differ")

    if not VENV_PY.is_file():
        raise RuntimeError("Mini-Kuzai venv Python not found")


def validate_completed_run():
    for path in (
        SUMMARY,
        MANIFEST,
        METRICS,
        PROBES,
        CYCLE2,
        CHECKPOINT,
    ):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(
                f"V61 RUN 001 missing required artifact: {path}"
            )

    summary = read_json(SUMMARY)
    manifest = read_json(MANIFEST)

    if summary.get("schema_version") != "v61-boundary-run-summary-1":
        raise RuntimeError("Unexpected V61 summary schema")
    if manifest.get("schema_version") != "v61-boundary-run-1":
        raise RuntimeError("Unexpected V61 manifest schema")
    if summary.get("status") != "STOPPED":
        raise RuntimeError("V61 RUN 001 is not stopped")
    if manifest.get("status") != "STOPPED":
        raise RuntimeError("V61 RUN 001 manifest is not stopped")
    if summary.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED":
        raise RuntimeError(
            "V61 RUN 001 did not stop at mandatory cycle-2 review"
        )
    if summary.get("training_started") is not True:
        raise RuntimeError("V61 RUN 001 did not start training")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("V61 RUN 001 accessed BLIND TEST")
    if manifest.get("blind_test_during_training") is not False:
        raise RuntimeError("V61 RUN 001 manifest permits BLIND TEST")
    if manifest.get("max_optimizer_steps") != 145:
        raise RuntimeError("V61 RUN 001 step ceiling changed")
    if manifest.get("max_exposure_tokens") != 1181664:
        raise RuntimeError("V61 RUN 001 exposure ceiling changed")

    steps = int(summary["optimizer_steps"])
    exposure = int(summary["exposure_tokens"])
    if not 0 < steps < 145:
        raise RuntimeError("V61 RUN 001 step count outside cycle-2 window")
    if not 590832 <= exposure < 1181664:
        raise RuntimeError(
            "V61 RUN 001 exposure is inconsistent with cycle-2 review"
        )


def publish_if_missing(step: str, history: Path, audit: Path):
    if history.is_file():
        print(f"{step}: ALREADY_PUBLISHED")
        return

    require_clean_synced()
    run_python(
        GOGIT,
        "--step",
        step,
        "--audit",
        str(audit.relative_to(REPO)),
    )
    if not history.is_file():
        raise RuntimeError(f"{step}: GOGIT history missing")
    require_clean_synced()
    print(f"{step}: COMPLETE")


def main():
    require_clean_synced()

    if not RUN_DIR.exists():
        run_python(TRAIN)
    else:
        print("V61_TRAIN_RUN_001: EXISTING_RUN_RECOVERY_MODE")

    validate_completed_run()

    publish_if_missing(
        RUN_STEP,
        RUN_HISTORY,
        RUN_AUDIT,
    )
    publish_if_missing(
        EOS_STEP,
        EOS_HISTORY,
        EOS_AUDIT,
    )

    print("V61_TRAIN_RUN_001_LOOP: COMPLETE")
    print("TRAINING_STARTED: 1")
    print("STOP_REASON: MILESTONE_REVIEW_REQUIRED")
    print("BLIND_ACCESS: 0")


if __name__ == "__main__":
    main()
