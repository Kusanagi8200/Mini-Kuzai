#!/usr/bin/env python3
"""V79 CPU preflight loop with immutable GOGIT diagnostics.

Run repeatedly after assistant-side corrections:
- synchronize clean main
- execute the V79 CPU regression suite
- on failure publish the next numeric-only DIAG-NNN GOGIT
- on success publish the canonical V79 CPU preflight GOGIT

No CUDA execution, training, BLIND access or scientific V79 run is performed.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
TEST_MODULE = "tests.test_phase03_v79_same_path_context_order_control_001"
GOGIT = ROOT / "tools" / "gogit_public.py"
DIAG_AUDIT = (
    ROOT / "tools" / "public-audits" /
    "phase03_v79_cpu_loop_diagnostic_001.py"
)
PREFLIGHT_AUDIT = (
    ROOT / "tools" / "public-audits" /
    "phase03_v79_cpu_preflight_001.py"
)
HISTORY = ROOT / "reports" / "assistant-results" / "history"
PREFLIGHT_STEP = "PHASE03-SMOLTALK-V79-CPU-PREFLIGHT-001"
DIAG_PREFIX = "PHASE03-SMOLTALK-V79-CPU-LOOP-DIAG-"


def run(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        check=False,
    )


def git(*args: str) -> str:
    proc = run("git", "-C", str(ROOT), *args, capture=True)
    if proc.returncode:
        raise RuntimeError("V79 loop git operation failed")
    return (proc.stdout or "").strip()


def synchronize() -> None:
    if git("branch", "--show-current") != "main":
        raise RuntimeError("V79 loop requires main")
    if git("status", "--porcelain"):
        raise RuntimeError("V79 loop requires a clean worktree")

    proc = run(
        "git", "-C", str(ROOT), "fetch", "--no-tags", "origin",
        "refs/heads/main:refs/remotes/origin/main",
        capture=True,
    )
    if proc.returncode:
        raise RuntimeError("V79 loop fetch failed")

    local = git("rev-parse", "HEAD")
    remote = git("rev-parse", "origin/main")
    if local != remote:
        merge = run(
            "git", "-C", str(ROOT), "merge", "--ff-only", "origin/main",
            capture=True,
        )
        if merge.returncode:
            raise RuntimeError("V79 loop fast-forward failed")

    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("V79 loop synchronization mismatch")
    if git("status", "--porcelain"):
        raise RuntimeError("V79 loop worktree changed during synchronization")


def preflight_already_published() -> bool:
    return (HISTORY / f"{PREFLIGHT_STEP}.json").is_file()


def next_diag_step() -> str:
    used = set()
    pattern = re.compile(re.escape(DIAG_PREFIX) + r"(\d{3})\.json\Z")
    for path in HISTORY.glob(f"{DIAG_PREFIX}*.json"):
        match = pattern.fullmatch(path.name)
        if match:
            used.add(int(match.group(1)))

    for number in range(1, 1000):
        if number not in used:
            return f"{DIAG_PREFIX}{number:03d}"
    raise RuntimeError("V79 diagnostic namespace exhausted")


def gogit(step: str, audit: Path) -> int:
    proc = run(
        str(PYTHON),
        str(GOGIT),
        "--step", step,
        "--audit", str(audit.relative_to(ROOT)),
    )
    return proc.returncode


def main() -> int:
    if not PYTHON.is_file():
        raise RuntimeError("V79 reviewed Python interpreter unavailable")
    for path in (GOGIT, DIAG_AUDIT, PREFLIGHT_AUDIT):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("V79 loop dependency missing or unsafe")

    synchronize()

    if preflight_already_published():
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V79_LOOP=COMPLETE")
        print("V79_CPU_PREFLIGHT_GOGIT=ALREADY_PUBLISHED")
        return 0

    tests = run(
        str(PYTHON),
        "-m", "unittest",
        TEST_MODULE,
        "-v",
        capture=True,
    )

    if tests.returncode:
        step = next_diag_step()
        rc = gogit(step, DIAG_AUDIT)
        if rc:
            print("##### SECTION RESULTS FOR ASSISTANT ######")
            print("V79_LOOP=BLOCKED")
            print("DIAGNOSTIC_GOGIT=FAILED")
            return 1
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V79_LOOP=DIAGNOSTIC_PUBLISHED")
        print(f"DIAGNOSTIC_STEP={step}")
        print("NEXT_ACTION=GOGIT")
        return 0

    rc = gogit(PREFLIGHT_STEP, PREFLIGHT_AUDIT)
    if rc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V79_LOOP=BLOCKED")
        print("V79_CPU_PREFLIGHT_GOGIT=FAILED")
        return 1

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V79_LOOP=COMPLETE")
    print("V79_CPU_PREFLIGHT_GOGIT=PUBLISHED")
    print("NEXT_ACTION=GOGIT")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V79_LOOP=BLOCKED")
        print("SAFE_FAILURE=1")
        raise SystemExit(1)
