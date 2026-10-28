#!/usr/bin/env python3
"""Run the first frozen V59 bounded pilot and publish its numeric summary with GOGIT."""
from __future__ import annotations
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENV_PY = Path("/root/Mini-Kuzai/.venv/bin/python")
TRAIN = REPO / "tools" / "train_v59_bounded_pilot.py"
GOGIT = REPO / "tools" / "gogit_public.py"
AUDIT = REPO / "tools" / "public-audits" / "phase03_v59_bounded_pilot_run.py"
RUN_DIR = Path("/root/Mini-Kuzai/runs/v59-bounded-pilot-001")
STEP = "PHASE03-SMOLTALK-V59-BOUNDED-PILOT-RUN-001"
HISTORY = REPO / "reports" / "assistant-results" / "history" / f"{STEP}.json"

def git(*args):
    p = subprocess.run(
        ["git", "-C", str(REPO), *args],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or "git failed")
    return p.stdout.strip()

def run_python(*args):
    p = subprocess.run(
        [str(VENV_PY), *map(str, args)],
        cwd=REPO,
        text=True,
        check=False,
    )
    if p.returncode:
        raise RuntimeError(f"Subprocess failed with status {p.returncode}")

def main():
    if HISTORY.is_file():
        print("V59_BOUNDED_PILOT_RUN: ALREADY_PUBLISHED")
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
            "Canonical V59 run directory already exists; first-run wrapper refuses resume"
        )

    run_python(TRAIN)

    summary = RUN_DIR / "RUN-SUMMARY.json"
    manifest = RUN_DIR / "RUN-MANIFEST.json"
    if not summary.is_file() or not manifest.is_file():
        raise RuntimeError("V59 run did not produce final summary artifacts")

    run_python(
        GOGIT,
        "--step", STEP,
        "--audit", str(AUDIT.relative_to(REPO)),
    )

if __name__ == "__main__":
    main()
