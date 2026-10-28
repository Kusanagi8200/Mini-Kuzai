#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENV_PY = Path("/root/Mini-Kuzai/.venv/bin/python")

INIT_BUILDER = REPO / "tools" / "phase03_v60_initialization_freeze.py"
PROTOCOL_BUILDER = REPO / "tools" / "phase03_v60_extended_training_protocol.py"
GOGIT = REPO / "tools" / "gogit_public.py"

INIT_AUDIT = (
    REPO / "tools" / "public-audits"
    / "phase03_v60_initialization_freeze.py"
)
PROTOCOL_AUDIT = (
    REPO / "tools" / "public-audits"
    / "phase03_v60_extended_training_protocol.py"
)

INIT_STEP = "PHASE03-SMOLTALK-V60-INITIALIZATION-FREEZE-001"
PROTOCOL_STEP = "PHASE03-SMOLTALK-V60-EXTENDED-TRAINING-PROTOCOL-001"

INIT_OUT = REPO / "reviews" / "smoltalk-v60-initialization-freeze"
PROTOCOL_OUT = REPO / "reviews" / "smoltalk-v60-extended-training-protocol"

EXPECTED = (
    INIT_OUT / "INITIALIZATION-FREEZE-001.json",
    INIT_OUT / "REPORT-001.json",
    INIT_OUT / "RESULTS-001.md",
    PROTOCOL_OUT / "PROTOCOL-001.json",
    PROTOCOL_OUT / "REPORT-001.json",
    PROTOCOL_OUT / "RESULTS-001.md",
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
            or "git command failed"
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


def tracked(path: Path) -> bool:
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


def history_exists(step: str) -> bool:
    return (
        REPO / "reports" / "assistant-results"
        / "history" / f"{step}.json"
    ).is_file()


def main():
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Expected branch main")
    if git("status", "--porcelain"):
        raise RuntimeError("Clean worktree required")

    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local and remote main differ")
    if not VENV_PY.is_file():
        raise RuntimeError("Mini-Kuzai venv Python not found")

    if not all(path.is_file() and tracked(path) for path in EXPECTED):
        if any(path.exists() for path in EXPECTED):
            raise RuntimeError(
                "Partial or untracked V60 freeze/protocol output exists"
            )

        run_python(INIT_BUILDER)
        run_python(PROTOCOL_BUILDER, "--write")

        files = {
            str(path.relative_to(REPO))
            for path in EXPECTED
            if path.is_file()
        }
        if len(files) != len(EXPECTED):
            raise RuntimeError("V60 builders did not create all outputs")

        git("add", "--", *sorted(files))
        staged = set(
            git("diff", "--cached", "--name-only").splitlines()
        )
        if staged != files:
            raise RuntimeError("Unexpected staged files")

        git("diff", "--cached", "--check")
        git(
            "commit",
            "-m",
            "V60: freeze initialization and extended training protocol",
        )
        git("push", "origin", "main")
        git("fetch", "--quiet", "origin", "main")
        if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
            raise RuntimeError("Push verification failed")

    if not history_exists(INIT_STEP):
        run_python(
            GOGIT,
            "--step",
            INIT_STEP,
            "--audit",
            str(INIT_AUDIT.relative_to(REPO)),
        )

    if not history_exists(PROTOCOL_STEP):
        run_python(
            GOGIT,
            "--step",
            PROTOCOL_STEP,
            "--audit",
            str(PROTOCOL_AUDIT.relative_to(REPO)),
        )

    print("V60_INITIALIZATION_AND_PROTOCOL: COMPLETE")


if __name__ == "__main__":
    main()
