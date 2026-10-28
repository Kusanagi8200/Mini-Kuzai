#!/usr/bin/env python3
"""Build and publish the complete V61 pre-training control plane.

Stages:
1. objective freeze
2. training protocol
3. training authorization
4. persistent trainer freeze

No training is executed.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENV_PY = Path("/root/Mini-Kuzai/.venv/bin/python")
GOGIT = REPO / "tools" / "gogit_public.py"

STAGES = (
    {
        "name": "OBJECTIVE_FREEZE",
        "builder": REPO / "tools" / "phase03_v61_objective_freeze.py",
        "audit": REPO / "tools" / "public-audits"
        / "phase03_v61_objective_freeze.py",
        "step": "PHASE03-SMOLTALK-V61-OBJECTIVE-FREEZE-001",
        "files": (
            REPO / "reviews" / "smoltalk-v61-boundary-objective-freeze"
            / "OBJECTIVE-FREEZE-001.json",
            REPO / "reviews" / "smoltalk-v61-boundary-objective-freeze"
            / "REPORT-001.json",
            REPO / "reviews" / "smoltalk-v61-boundary-objective-freeze"
            / "RESULTS-001.md",
        ),
        "commit": "V61: freeze boundary-aware EOS objective",
    },
    {
        "name": "TRAINING_PROTOCOL",
        "builder": REPO / "tools" / "phase03_v61_training_protocol.py",
        "audit": REPO / "tools" / "public-audits"
        / "phase03_v61_training_protocol.py",
        "step": "PHASE03-SMOLTALK-V61-TRAINING-PROTOCOL-001",
        "files": (
            REPO / "reviews" / "smoltalk-v61-training-protocol"
            / "PROTOCOL-001.json",
            REPO / "reviews" / "smoltalk-v61-training-protocol"
            / "REPORT-001.json",
            REPO / "reviews" / "smoltalk-v61-training-protocol"
            / "RESULTS-001.md",
        ),
        "commit": "V61: freeze short boundary-aware training protocol",
    },
    {
        "name": "TRAINING_AUTHORIZATION",
        "builder": REPO / "tools" / "phase03_v61_training_authorization.py",
        "audit": REPO / "tools" / "public-audits"
        / "phase03_v61_training_authorization.py",
        "step": "PHASE03-SMOLTALK-V61-TRAINING-AUTHORIZATION-001",
        "files": (
            REPO / "reviews" / "smoltalk-v61-training-authorization"
            / "TRAINING-FREEZE-001.json",
            REPO / "reviews" / "smoltalk-v61-training-authorization"
            / "TRAINING-AUTHORIZATION-001.json",
            REPO / "reviews" / "smoltalk-v61-training-authorization"
            / "REPORT-001.json",
            REPO / "reviews" / "smoltalk-v61-training-authorization"
            / "RESULTS-001.md",
        ),
        "commit": "V61: authorize controlled boundary-aware training window",
    },
    {
        "name": "PERSISTENT_TRAINER_FREEZE",
        "builder": REPO / "tools"
        / "phase03_v61_persistent_trainer_freeze.py",
        "audit": REPO / "tools" / "public-audits"
        / "phase03_v61_persistent_trainer_freeze.py",
        "step": "PHASE03-SMOLTALK-V61-PERSISTENT-TRAINER-FREEZE-001",
        "files": (
            REPO / "reviews" / "smoltalk-v61-persistent-trainer-freeze"
            / "TRAINER-FREEZE-001.json",
            REPO / "reviews" / "smoltalk-v61-persistent-trainer-freeze"
            / "REPORT-001.json",
            REPO / "reviews" / "smoltalk-v61-persistent-trainer-freeze"
            / "RESULTS-001.md",
        ),
        "commit": "V61: freeze persistent boundary-aware trainer",
    },
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
    process = subprocess.run(
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
    )
    return process.returncode == 0


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


def history_path(step: str) -> Path:
    return (
        REPO / "reports" / "assistant-results"
        / "history" / f"{step}.json"
    )


def commit_stage(stage):
    files = tuple(stage["files"])
    if not all(path.is_file() for path in files):
        raise RuntimeError(
            f"{stage['name']}: expected outputs are missing"
        )

    relative = {
        str(path.relative_to(REPO))
        for path in files
    }
    git("add", "--", *sorted(relative))

    staged = set(
        git("diff", "--cached", "--name-only").splitlines()
    )
    if staged != relative:
        raise RuntimeError(
            f"{stage['name']}: unexpected staged files"
        )

    git("diff", "--cached", "--check")
    git("commit", "-m", stage["commit"])
    git("push", "origin", "main")
    git("fetch", "--quiet", "origin", "main")

    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError(
            f"{stage['name']}: push verification failed"
        )


def execute_stage(stage):
    require_clean_synced()

    history = history_path(stage["step"])
    if history.is_file():
        print(f"{stage['name']}: ALREADY_PUBLISHED")
        return

    files = tuple(stage["files"])
    existing = [path.exists() for path in files]
    tracked_flags = [
        path.is_file() and tracked(path)
        for path in files
    ]

    if all(tracked_flags):
        pass
    elif any(existing):
        raise RuntimeError(
            f"{stage['name']}: partial or untracked output exists"
        )
    else:
        run_python(stage["builder"], "--write")
        commit_stage(stage)

    require_clean_synced()

    run_python(
        GOGIT,
        "--step",
        stage["step"],
        "--audit",
        str(stage["audit"].relative_to(REPO)),
    )

    if not history.is_file():
        raise RuntimeError(
            f"{stage['name']}: GOGIT history was not produced"
        )

    require_clean_synced()
    print(f"{stage['name']}: COMPLETE")


def main():
    for stage in STAGES:
        execute_stage(stage)

    print("V61_CONTROL_PLANE: COMPLETE")
    print("TRAINING_AUTHORIZED: 1")
    print("TRAINING_STARTED: 0")
    print("BLIND_ACCESS: 0")


if __name__ == "__main__":
    main()
