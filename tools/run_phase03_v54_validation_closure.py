#!/usr/bin/env python3
"""Resumable one-command runner for Phase 03 V54 global VALIDATION closure."""
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PY=sys.executable
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
STEP="PHASE03-SMOLTALK-V54-VALIDATION-CLOSURE-001"
AUDIT="tools/public-audits/phase03_v54_validation_closure.py"
HISTORY=ROOT/"reports/assistant-results/history"/(STEP+".json")
SOURCE="Mini-Kuzai Phase 03 designed validation corpus"

EXPECTED={
    "TRAIN_FILES":19,
    "TRAIN_RECORDS":107,
    "TRAIN_GROUPS":29,
    "VALIDATION_RECORDS":36,
    "VALIDATION_GROUPS":18,
    "VALIDATION_FREEZE_HISTORIES":18,
    "VALIDATION_SIGNOFFS":18,
    "VALIDATION_SEMANTIC_PASSES":18,
    "VALIDATION_EXACT_PROMPT_DUPLICATES":0,
    "CROSS_SPLIT_ID_COLLISIONS":0,
    "CROSS_SPLIT_GROUP_COLLISIONS":0,
    "EXACT_USER_PROMPT_MATCHES":0,
    "BLIND_TEST_RECORDS":0,
    "BLIND_TEST_GROUPS_RESERVED":18,
    "SEMANTIC_VALIDATION_COMPLETE":1,
    "BLIND_AUTHORING_AUTHORIZED":1,
    "TRAINING_AUTHORIZED":0,
}

def run(args,capture=False):
    return subprocess.run(
        args,cwd=ROOT,text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        check=False,
    )

def git(*args):
    p=run(["git","-C",str(ROOT),*args],capture=True)
    if p.returncode:
        raise RuntimeError("git {} failed: {}".format(" ".join(args),(p.stdout or "").strip()))
    return (p.stdout or "").strip()

def sync():
    if git("branch","--show-current")!="main":
        raise RuntimeError("Expected branch main")
    if git("status","--porcelain"):
        raise RuntimeError("Worktree/index must be clean")
    p=run(["git","-C",str(ROOT),"pull","--ff-only","origin","main"],capture=True)
    if p.returncode:
        raise RuntimeError("git pull --ff-only failed: "+(p.stdout or "").strip())
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local main and origin/main differ after synchronization")
    if git("status","--porcelain"):
        raise RuntimeError("Worktree changed after synchronization")

def verify_history():
    if not HISTORY.is_file():
        return False
    if HISTORY.is_symlink():
        raise RuntimeError("Unsafe closure history symlink")
    report=json.loads(HISTORY.read_text(encoding="utf-8"))
    if report.get("step_id")!=STEP:
        raise RuntimeError("Closure STEP_ID mismatch")
    if report.get("source")!=SOURCE:
        raise RuntimeError("Closure source mismatch")
    if report.get("semantic_validation_complete") is not True:
        raise RuntimeError("semantic_validation_complete is not true in closure history")
    if report.get("training_authorized") is not False:
        raise RuntimeError("Closure history unexpectedly authorizes training")
    metrics=report.get("metrics",{})
    for key,value in EXPECTED.items():
        if metrics.get(key)!=value:
            raise RuntimeError("Closure metric mismatch: {} expected {} got {}".format(
                key,value,metrics.get(key)))
    return True

def main():
    try:
        sync()
        if verify_history():
            print(MARKER)
            print("VALIDATION_CLOSURE_COMPLETE: 1")
            print("SEMANTIC_VALIDATION_COMPLETE: 1")
            print("BLIND_AUTHORING_AUTHORIZED: 1")
            print("VALIDATION_RECORDS: 36")
            print("VALIDATION_GROUPS: 18")
            print("TRAINING_AUTHORIZED: 0")
            print("GOGIT: READY")
            return

        files=[
            "tools/gogit_public.py",
            AUDIT,
            "tests/phase-03/test_phase03_v54_validation_closure.py",
            "tools/run_phase03_v54_validation_closure.py",
        ]
        p=run([PY,"-m","py_compile",*files],capture=True)
        if p.returncode:
            raise RuntimeError("py_compile failed:\n"+(p.stdout or ""))

        print("RUN VALIDATION CLOSURE: tests")
        p=run([PY,"-m","unittest","discover","-s","tests/phase-03",
               "-p","test_phase03_v54_validation_closure.py","-v"],capture=True)
        if p.returncode:
            raise RuntimeError("Closure tests failed:\n"+(p.stdout or ""))

        print("RUN VALIDATION CLOSURE: direct audit")
        p=run([PY,AUDIT],capture=True)
        if p.returncode:
            raise RuntimeError("Closure audit failed:\n"+(p.stdout or ""))

        print("RUN VALIDATION CLOSURE: GOGIT publish")
        p=run([PY,"tools/gogit_public.py","--step",STEP,"--audit",AUDIT],capture=True)
        if p.returncode:
            raise RuntimeError("Closure GOGIT publication failed:\n"+(p.stdout or ""))

        if not verify_history():
            raise RuntimeError("Closure publication returned success but history is missing")
        git("fetch","--quiet","origin","main")
        if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
            raise RuntimeError("Local/remote divergence after closure publication")
        if git("status","--porcelain"):
            raise RuntimeError("Worktree not clean after closure publication")

        print(MARKER)
        print("VALIDATION_CLOSURE_COMPLETE: 1")
        print("SEMANTIC_VALIDATION_COMPLETE: 1")
        print("BLIND_AUTHORING_AUTHORIZED: 1")
        print("VALIDATION_RECORDS: 36")
        print("VALIDATION_GROUPS: 18")
        print("TRAINING_AUTHORIZED: 0")
        print("GOGIT: READY")
    except Exception as exc:
        print(MARKER)
        print("VALIDATION_CLOSURE_COMPLETE: 0")
        print("ERROR:",str(exc))
        sys.exit(1)

if __name__=="__main__":
    main()
