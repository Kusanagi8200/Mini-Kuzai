#!/usr/bin/env python3
"""Run V60 TRAIN RUN 001 and publish its numeric summary through GOGIT."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENV_PY = Path("/root/Mini-Kuzai/.venv/bin/python")
TRAIN = REPO / "tools" / "train_v60_extended.py"
GOGIT = REPO / "tools" / "gogit_public.py"
AUDIT = (
    REPO / "tools" / "public-audits"
    / "phase03_v60_train_run_001.py"
)
RUN_DIR = Path("/root/Mini-Kuzai/runs/v60-extended-001")
STEP = "PHASE03-SMOLTALK-V60-TRAIN-RUN-001"
HISTORY = (
    REPO / "reports" / "assistant-results" / "history"
    / f"{STEP}.json"
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


def main():
    if HISTORY.is_file():
        print("V60_TRAIN_RUN_001: ALREADY_PUBLISHED")
        print("STEP_ID:", STEP)
        return

    if git("branch", "--show-current") != "main":
        raise RuntimeError("Expected branch main")
    if git("status", "--porcelain"):
        raise RuntimeError("Clean worktree required")

    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local and remote main differ")

    if not VENV_PY.is_file():
        raise RuntimeError("Mini-Kuzai venv Python not found")

    if RUN_DIR.exists():
        raise RuntimeError(
            "Canonical V60 run directory already exists; "
            "RUN 001 wrapper refuses implicit resume"
        )

    run_python(TRAIN)

    summary = RUN_DIR / "RUN-SUMMARY.json"
    manifest = RUN_DIR / "RUN-MANIFEST.json"
    metrics = RUN_DIR / "metrics.jsonl"
    probes = RUN_DIR / "validation-probes.jsonl"
    for path in (summary, manifest, metrics, probes):
        if not path.is_file():
            raise RuntimeError(
                f"V60 run did not produce required artifact: {path}"
            )

    run_python(
        GOGIT,
        "--step",
        STEP,
        "--audit",
        str(AUDIT.relative_to(REPO)),
    )


if __name__ == "__main__":
    main()
