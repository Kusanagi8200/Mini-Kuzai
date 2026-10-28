#!/usr/bin/env python3
"""Build, freeze and publish the V61 boundary-objective preflight."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENV_PY = Path("/root/Mini-Kuzai/.venv/bin/python")
BUILDER = REPO / "tools" / "phase03_v61_boundary_objective_preflight.py"
GOGIT = REPO / "tools" / "gogit_public.py"
AUDIT = (
    REPO / "tools" / "public-audits"
    / "phase03_v61_boundary_objective_preflight.py"
)

OUT = REPO / "reviews" / "smoltalk-v61-boundary-objective"
FILES = (
    OUT / "OBJECTIVE-001.json",
    OUT / "REPORT-001.json",
    OUT / "RESULTS-001.md",
)

STEP = "PHASE03-SMOLTALK-V61-BOUNDARY-OBJECTIVE-PREFLIGHT-001"
HISTORY = (
    REPO / "reports" / "assistant-results"
    / "history" / f"{STEP}.json"
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


def commit_outputs():
    relative = {
        str(path.relative_to(REPO))
        for path in FILES
        if path.is_file()
    }
    if len(relative) != len(FILES):
        raise RuntimeError("Expected V61 preflight outputs are missing")

    git("add", "--", *sorted(relative))
    staged = set(
        git("diff", "--cached", "--name-only").splitlines()
    )
    if staged != relative:
        raise RuntimeError("Unexpected staged files")

    git("diff", "--cached", "--check")
    git(
        "commit",
        "-m",
        "V61: freeze boundary-aware EOS objective preflight",
    )
    git("push", "origin", "main")
    git("fetch", "--quiet", "origin", "main")

    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Push verification failed")


def main():
    if HISTORY.is_file():
        print("V61_BOUNDARY_OBJECTIVE_PREFLIGHT: ALREADY_PUBLISHED")
        print("STEP_ID:", STEP)
        return

    require_clean_synced()

    if all(path.is_file() and tracked(path) for path in FILES):
        pass
    elif any(path.exists() for path in FILES):
        raise RuntimeError(
            "Partial or untracked V61 preflight output exists"
        )
    else:
        run_python(BUILDER, "--write")
        commit_outputs()

    require_clean_synced()

    run_python(
        GOGIT,
        "--step",
        STEP,
        "--audit",
        str(AUDIT.relative_to(REPO)),
    )

    print("V61_BOUNDARY_OBJECTIVE_PREFLIGHT: COMPLETE")
    print("TRAINING_AUTHORIZED: 0")
    print("TRAINING_STARTED: 0")


if __name__ == "__main__":
    main()
