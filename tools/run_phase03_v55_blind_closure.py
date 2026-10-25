#!/usr/bin/env python3
"""Resumable one-command runner for Phase 03 V55 global BLIND closure."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"
STEP = "PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001"
AUDIT = "tools/public-audits/phase03_v55_blind_closure.py"
HISTORY = ROOT / "reports/assistant-results/history" / (STEP + ".json")
SOURCE = "Mini-Kuzai Phase 03 designed blind-test corpus"

EXPECTED = {
    "TRAIN_FILES": 19,
    "TRAIN_RECORDS": 107,
    "TRAIN_GROUPS": 29,
    "VALIDATION_RECORDS": 36,
    "VALIDATION_GROUPS": 18,
    "VALIDATION_FREEZE_HISTORIES": 18,
    "VALIDATION_SIGNOFFS": 18,
    "VALIDATION_SEMANTIC_PASSES": 18,
    "VALIDATION_EXACT_PROMPT_DUPLICATES": 0,
    "BLIND_TEST_RECORDS": 36,
    "BLIND_TEST_GROUPS_RESERVED": 18,
    "BLIND_TEST_RECORDS_FROZEN": 36,
    "BLIND_BEHAVIORS_FROZEN": 18,
    "CROSS_SPLIT_ID_COLLISIONS": 0,
    "CROSS_SPLIT_GROUP_COLLISIONS": 0,
    "EXACT_USER_PROMPT_MATCHES": 0,
    "SEMANTIC_VALIDATION_COMPLETE": 1,
    "BLIND_AUTHORING_AUTHORIZED": 1,
    "TRAINING_AUTHORIZED": 0,
}


def run(args, capture=False):
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        check=False,
    )


def git(*args):
    process = run(["git", "-C", str(ROOT), *args], capture=True)
    if process.returncode:
        raise RuntimeError(
            "git {} failed: {}".format(" ".join(args), (process.stdout or "").strip())
        )
    return (process.stdout or "").strip()


def sync():
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Expected branch main")
    if git("status", "--porcelain"):
        raise RuntimeError("Worktree/index must be clean")
    process = run(
        ["git", "-C", str(ROOT), "pull", "--ff-only", "origin", "main"],
        capture=True,
    )
    if process.returncode:
        raise RuntimeError("git pull --ff-only failed: " + (process.stdout or "").strip())
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local main and origin/main differ after synchronization")
    if git("status", "--porcelain"):
        raise RuntimeError("Worktree changed after synchronization")


def verify_history():
    if not HISTORY.is_file():
        return False
    if HISTORY.is_symlink():
        raise RuntimeError("Unsafe closure history symlink")
    report = json.loads(HISTORY.read_text(encoding="utf-8"))
    if report.get("step_id") != STEP:
        raise RuntimeError("BLIND closure STEP_ID mismatch")
    if report.get("source") != SOURCE:
        raise RuntimeError("BLIND closure source mismatch")
    if report.get("semantic_validation_complete") is not True:
        raise RuntimeError("semantic_validation_complete is not true in BLIND closure")
    if report.get("training_authorized") is not False:
        raise RuntimeError("BLIND closure unexpectedly authorizes training")
    metrics = report.get("metrics", {})
    for key, value in EXPECTED.items():
        if metrics.get(key) != value:
            raise RuntimeError(
                "BLIND closure metric mismatch: {} expected {} got {}".format(
                    key, value, metrics.get(key)
                )
            )
    return True


def main():
    try:
        sync()
        if verify_history():
            print(MARKER)
            print("BLIND_CLOSURE_COMPLETE: 1")
            print("BLIND_TEST_RECORDS: 36")
            print("BLIND_BEHAVIORS_FROZEN: 18")
            print("SEMANTIC_VALIDATION_COMPLETE: 1")
            print("TRAINING_AUTHORIZED: 0")
            print("GOGIT: READY")
            return

        files = [
            "tools/gogit_public.py",
            AUDIT,
            "tests/phase-03/test_phase03_v55_blind_closure.py",
            "tools/run_phase03_v55_blind_closure.py",
        ]
        process = run([PY, "-m", "py_compile", *files], capture=True)
        if process.returncode:
            raise RuntimeError("py_compile failed:\n" + (process.stdout or ""))

        process = run(
            [
                PY,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests/phase-03",
                "-p",
                "test_phase03_v55_blind_closure.py",
                "-v",
            ],
            capture=True,
        )
        if process.returncode:
            raise RuntimeError("BLIND closure tests failed:\n" + (process.stdout or ""))

        process = run([PY, AUDIT], capture=True)
        if process.returncode:
            raise RuntimeError("BLIND closure audit failed:\n" + (process.stdout or ""))

        process = run(
            [PY, "tools/gogit_public.py", "--step", STEP, "--audit", AUDIT],
            capture=True,
        )
        if process.returncode:
            raise RuntimeError(
                "BLIND closure GOGIT publication failed:\n" + (process.stdout or "")
            )

        if not verify_history():
            raise RuntimeError("BLIND closure publication succeeded but history is missing")
        git("fetch", "--quiet", "origin", "main")
        if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
            raise RuntimeError("Local/remote divergence after BLIND closure publication")
        if git("status", "--porcelain"):
            raise RuntimeError("Worktree not clean after BLIND closure publication")

        print(MARKER)
        print("BLIND_CLOSURE_COMPLETE: 1")
        print("BLIND_TEST_RECORDS: 36")
        print("BLIND_BEHAVIORS_FROZEN: 18")
        print("SEMANTIC_VALIDATION_COMPLETE: 1")
        print("TRAINING_AUTHORIZED: 0")
        print("GOGIT: READY")
    except Exception as exc:
        print(MARKER)
        print("BLIND_CLOSURE_COMPLETE: 0")
        print("ERROR:", str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
