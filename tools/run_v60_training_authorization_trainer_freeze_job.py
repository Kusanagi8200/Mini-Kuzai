#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENV_PY = Path("/root/Mini-Kuzai/.venv/bin/python")

AUTH_BUILDER = REPO / "tools" / "phase03_v60_training_authorization.py"
TRAINER_FREEZE_BUILDER = (
    REPO / "tools" / "phase03_v60_persistent_trainer_freeze.py"
)
GOGIT = REPO / "tools" / "gogit_public.py"

AUTH_AUDIT = (
    REPO / "tools" / "public-audits"
    / "phase03_v60_training_authorization.py"
)
TRAINER_AUDIT = (
    REPO / "tools" / "public-audits"
    / "phase03_v60_persistent_trainer_freeze.py"
)

AUTH_STEP = "PHASE03-SMOLTALK-V60-TRAINING-AUTHORIZATION-001"
TRAINER_STEP = "PHASE03-SMOLTALK-V60-PERSISTENT-TRAINER-FREEZE-001"

AUTH_OUT = REPO / "reviews" / "smoltalk-v60-training-authorization"
TRAINER_OUT = (
    REPO / "reviews" / "smoltalk-v60-persistent-trainer-freeze"
)

AUTH_FILES = (
    AUTH_OUT / "TRAINING-FREEZE-001.json",
    AUTH_OUT / "TRAINING-AUTHORIZATION-001.json",
    AUTH_OUT / "REPORT-001.json",
    AUTH_OUT / "RESULTS-001.md",
)
TRAINER_FILES = (
    TRAINER_OUT / "TRAINER-FREEZE-001.json",
    TRAINER_OUT / "REPORT-001.json",
    TRAINER_OUT / "RESULTS-001.md",
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


def commit_outputs(
    files: tuple[Path, ...],
    message: str,
):
    relative = {
        str(path.relative_to(REPO))
        for path in files
        if path.is_file()
    }
    if len(relative) != len(files):
        raise RuntimeError("Expected output files are missing")

    git("add", "--", *sorted(relative))
    staged = set(
        git("diff", "--cached", "--name-only").splitlines()
    )
    if staged != relative:
        raise RuntimeError("Unexpected staged files")

    git("diff", "--cached", "--check")
    git("commit", "-m", message)
    git("push", "origin", "main")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Push verification failed")


def ensure_outputs(
    *,
    files: tuple[Path, ...],
    builder: Path,
    builder_args: tuple[str, ...],
    message: str,
):
    if all(path.is_file() and tracked(path) for path in files):
        return
    if any(path.exists() for path in files):
        raise RuntimeError(
            "Partial or untracked V60 output exists"
        )

    run_python(builder, *builder_args)
    commit_outputs(files, message)


def publish(step: str, audit: Path):
    if history_exists(step):
        return
    run_python(
        GOGIT,
        "--step",
        step,
        "--audit",
        str(audit.relative_to(REPO)),
    )


def main():
    require_clean_synced()

    ensure_outputs(
        files=AUTH_FILES,
        builder=AUTH_BUILDER,
        builder_args=("--write",),
        message="V60: freeze extended-window training authorization",
    )
    publish(AUTH_STEP, AUTH_AUDIT)

    require_clean_synced()

    ensure_outputs(
        files=TRAINER_FILES,
        builder=TRAINER_FREEZE_BUILDER,
        builder_args=("--write",),
        message="V60: freeze persistent extended trainer",
    )
    publish(TRAINER_STEP, TRAINER_AUDIT)

    print("V60_AUTHORIZATION_AND_TRAINER_FREEZE: COMPLETE")
    print("TRAINING_STARTED: 0")


if __name__ == "__main__":
    main()
