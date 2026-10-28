#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
VENV_PY = Path("/root/Mini-Kuzai/.venv/bin/python")

OUT = (
    REPO
    / "reviews"
    / "smoltalk-v59-persistent-trainer-freeze"
)
REPORT = OUT / "REPORT-001.json"

FREEZE = REPO / "tools" / "phase03_v59_persistent_trainer_freeze.py"
PUBLIC_AUDIT = (
    REPO
    / "tools"
    / "public-audits"
    / "phase03_v59_persistent_trainer_freeze.py"
)
GOGIT = REPO / "tools" / "gogit_public.py"

STEP = "PHASE03-SMOLTALK-V59-PERSISTENT-TRAINER-FREEZE-001"
HISTORY = (
    REPO
    / "reports"
    / "assistant-results"
    / "history"
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
        detail = "\n".join(
            value
            for value in (
                process.stdout.strip(),
                process.stderr.strip(),
            )
            if value
        )
        raise RuntimeError(
            "Git command failed: "
            + (detail or str(process.returncode))
        )
    return process.stdout.strip()


def run_python(*args):
    process = subprocess.run(
        [str(VENV_PY), *map(str, args)],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if process.stdout:
        print(process.stdout, end="")
    if process.returncode:
        raise RuntimeError(
            f"Subprocess failed with status {process.returncode}"
        )


def tracked(path):
    relative = str(path.relative_to(REPO))
    return subprocess.run(
        [
            "git",
            "-C",
            str(REPO),
            "cat-file",
            "-e",
            f"HEAD:{relative}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def main():
    if HISTORY.is_file():
        print("V59_PERSISTENT_TRAINER_FREEZE: ALREADY_COMPLETE")
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

    if REPORT.is_file() and tracked(REPORT):
        print("V59_PERSISTENT_TRAINER_FREEZE: ALREADY_PUBLISHED")
    else:
        if OUT.exists():
            raise RuntimeError(
                "Untracked persistent trainer freeze output already exists"
            )

        run_python(FREEZE, "--write")

        files = {
            str(path.relative_to(REPO))
            for path in OUT.rglob("*")
            if path.is_file()
        }
        if not files:
            raise RuntimeError(
                "No persistent trainer freeze output generated"
            )

        git("add", "--", *sorted(files))
        if (
            set(
                git(
                    "diff",
                    "--cached",
                    "--name-only",
                ).splitlines()
            )
            != files
        ):
            raise RuntimeError("Unexpected staged files")

        git("diff", "--cached", "--check")
        git(
            "commit",
            "-m",
            "V59: freeze persistent bounded pilot trainer",
        )
        git("push", "origin", "main")
        git("fetch", "--quiet", "origin", "main")

        if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
            raise RuntimeError("Push verification failed")

    run_python(
        GOGIT,
        "--step",
        STEP,
        "--audit",
        str(PUBLIC_AUDIT.relative_to(REPO)),
    )


if __name__ == "__main__":
    main()
