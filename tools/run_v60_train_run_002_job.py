#!/usr/bin/env python3
"""Resume V60 from RUN 001 milestone and publish RUN 002 with GOGIT."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENV_PY = Path("/root/Mini-Kuzai/.venv/bin/python")
TRAIN = REPO / "tools" / "train_v60_extended.py"
GOGIT = REPO / "tools" / "gogit_public.py"
AUDIT = (
    REPO / "tools" / "public-audits"
    / "phase03_v60_train_run_002.py"
)

RUN_DIR = Path("/root/Mini-Kuzai/runs/v60-extended-001")
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"
MANIFEST = RUN_DIR / "RUN-MANIFEST.json"
CHECKPOINT = RUN_DIR / "checkpoint-last.pt"
CYCLE8 = RUN_DIR / "checkpoint-cycle-08.pt"

RUN1_STEP = "PHASE03-SMOLTALK-V60-TRAIN-RUN-001"
RUN2_STEP = "PHASE03-SMOLTALK-V60-TRAIN-RUN-002"
RUN1_HISTORY = (
    REPO / "reports" / "assistant-results" / "history"
    / f"{RUN1_STEP}.json"
)
RUN2_HISTORY = (
    REPO / "reports" / "assistant-results" / "history"
    / f"{RUN2_STEP}.json"
)

EXPECTED_START_STEPS = 270
EXPECTED_START_TOKENS = 2365162


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


def load_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def require_repo_ready():
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Expected branch main")
    if git("status", "--porcelain"):
        raise RuntimeError("Clean worktree required")

    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local and remote main differ")

    if not VENV_PY.is_file():
        raise RuntimeError("Mini-Kuzai venv Python not found")


def validate_run1_publication():
    report = load_json(RUN1_HISTORY)
    metrics = report.get("metrics")
    if not isinstance(metrics, dict):
        raise RuntimeError("RUN 001 public metrics missing")
    if metrics.get("V60_RUN_OPTIMIZER_STEPS") != EXPECTED_START_STEPS:
        raise RuntimeError("RUN 001 public step baseline changed")
    if metrics.get("V60_RUN_EXPOSURE_TOKENS") != EXPECTED_START_TOKENS:
        raise RuntimeError("RUN 001 public exposure baseline changed")
    if metrics.get("V60_RUN_STOP_MILESTONE") != 1:
        raise RuntimeError("RUN 001 was not the mandatory milestone stop")


def current_state() -> tuple[int, int, str]:
    summary = load_json(SUMMARY)
    if summary.get("schema_version") != "v60-extended-run-summary-1":
        raise RuntimeError("Unexpected V60 run summary schema")
    if summary.get("status") != "STOPPED":
        raise RuntimeError("V60 run is not in a stopped state")
    if summary.get("training_started") is not True:
        raise RuntimeError("V60 run has no training state")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("BLIND TEST access detected")

    return (
        int(summary["optimizer_steps"]),
        int(summary["exposure_tokens"]),
        str(summary["stop_reason"]),
    )


def main():
    if RUN2_HISTORY.is_file():
        print("V60_TRAIN_RUN_002: ALREADY_PUBLISHED")
        print("STEP_ID:", RUN2_STEP)
        return

    require_repo_ready()
    validate_run1_publication()

    for path in (SUMMARY, MANIFEST, CHECKPOINT, CYCLE8):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(
                f"Required RUN 001 artifact missing or unsafe: {path}"
            )

    steps, tokens, stop = current_state()

    if (
        steps == EXPECTED_START_STEPS
        and tokens == EXPECTED_START_TOKENS
    ):
        if stop != "MILESTONE_REVIEW_REQUIRED":
            raise RuntimeError(
                "RUN 001 local state is not the published milestone stop"
            )
        run_python(TRAIN, "--resume")

        steps, tokens, stop = current_state()
        if steps <= EXPECTED_START_STEPS:
            raise RuntimeError("RUN 002 did not advance optimizer steps")
        if tokens <= EXPECTED_START_TOKENS:
            raise RuntimeError("RUN 002 did not advance exposure")

    elif (
        steps > EXPECTED_START_STEPS
        and tokens > EXPECTED_START_TOKENS
    ):
        # Training already completed but publication may have been interrupted.
        pass
    else:
        raise RuntimeError(
            "Local V60 state does not match RUN 001 or a completed RUN 002"
        )

    manifest = load_json(MANIFEST)
    if manifest.get("resume") is not True:
        raise RuntimeError("Final run manifest is not marked as resume")

    run_python(
        GOGIT,
        "--step",
        RUN2_STEP,
        "--audit",
        str(AUDIT.relative_to(REPO)),
    )


if __name__ == "__main__":
    main()
