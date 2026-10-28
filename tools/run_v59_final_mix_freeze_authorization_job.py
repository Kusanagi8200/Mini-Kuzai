#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
OUT=REPO/"reviews"/"smoltalk-v59-final-mix-freeze-authorization"
REPORT=OUT/"REPORT-001.json"
FREEZE=REPO/"tools"/"phase03_v59_final_mix_freeze_authorization.py"
PUBLIC_AUDIT=REPO/"tools"/"public-audits"/"phase03_v59_final_mix_freeze_authorization.py"
GOGIT=REPO/"tools"/"gogit_public.py"
STEP="PHASE03-SMOLTALK-V59-FINAL-MIX-FREEZE-AUTHORIZATION-001"
HISTORY=REPO/"reports"/"assistant-results"/"history"/f"{STEP}.json"

def git(*args):
    p=subprocess.run(
        ["git","-C",str(REPO),*args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        detail="\n".join(x for x in (p.stdout.strip(),p.stderr.strip()) if x)
        raise RuntimeError("Git command failed: "+(detail or str(p.returncode)))
    return p.stdout.strip()

def run(*args):
    p=subprocess.run(
        [sys.executable,*map(str,args)],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if p.stdout:
        print(p.stdout,end="")
    if p.returncode:
        raise RuntimeError(f"Subprocess failed with status {p.returncode}")

def tracked(path):
    rel=str(path.relative_to(REPO))
    return subprocess.run(
        ["git","-C",str(REPO),"cat-file","-e",f"HEAD:{rel}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode==0

def main():
    if HISTORY.is_file():
        print("V59_FINAL_AUTHORIZATION_JOB: ALREADY_COMPLETE")
        print("STEP_ID:",STEP)
        return

    if git("branch","--show-current")!="main":
        raise RuntimeError("Expected branch main")
    if git("status","--porcelain"):
        raise RuntimeError("Clean worktree required")

    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local and remote main differ")

    if REPORT.is_file() and tracked(REPORT):
        print("V59_FINAL_AUTHORIZATION: ALREADY_PUBLISHED")
    else:
        if OUT.exists():
            raise RuntimeError("Untracked final authorization output already exists")

        run(FREEZE,"--write")

        files={str(p.relative_to(REPO)) for p in OUT.rglob("*") if p.is_file()}
        if not files:
            raise RuntimeError("No final authorization output generated")

        git("add","--",*sorted(files))
        if set(git("diff","--cached","--name-only").splitlines())!=files:
            raise RuntimeError("Unexpected staged files")

        git("diff","--cached","--check")
        git("commit","-m","V59: freeze final mix and authorize bounded pilot")
        git("push","origin","main")
        git("fetch","--quiet","origin","main")

        if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
            raise RuntimeError("Push verification failed")

    run(
        GOGIT,
        "--step",STEP,
        "--audit",str(PUBLIC_AUDIT.relative_to(REPO)),
    )

if __name__=="__main__":
    main()
