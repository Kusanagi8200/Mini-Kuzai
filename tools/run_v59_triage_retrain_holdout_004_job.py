#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/"reviews"/"smoltalk-v59-independent-holdout-004"
README=ROOT/"README.md"; DECISIONS=ROOT/"DECISIONS-004.json"; RESULTS=ROOT/"RESULTS-004.md"; AUDIT_REPORT=ROOT/"AUDIT-004.json"
PUBLISH=REPO/"tools"/"publish_smoltalk_v59_independent_holdout_004.py"
APPLY=REPO/"tools"/"apply_smoltalk_v59_independent_holdout_004.py"
AUDIT=REPO/"tools"/"phase03_v59_triage_retrain_holdout_004_audit.py"
PUBLIC_AUDIT=REPO/"tools"/"public-audits"/"phase03_v59_triage_retrain_holdout_004.py"
GOGIT=REPO/"tools"/"gogit_public.py"
STEP="PHASE03-SMOLTALK-V59-TRIAGE-RETRAIN-HOLDOUT-004"
HISTORY=REPO/"reports"/"assistant-results"/"history"/f"{STEP}.json"

def run(*args):
    p=subprocess.run([sys.executable,*map(str,args)],cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
    if p.stdout: print(p.stdout,end="")
    if p.returncode: raise RuntimeError(f"Subprocess failed with status {p.returncode}")

def git(*args):
    p=subprocess.run(["git","-C",str(REPO),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode:
        detail="\n".join(x for x in (p.stdout.strip(),p.stderr.strip()) if x)
        raise RuntimeError("Git command failed: "+(detail or str(p.returncode)))
    return p.stdout.strip()

def tracked(path):
    rel=str(path.relative_to(REPO))
    return subprocess.run(["git","-C",str(REPO),"cat-file","-e",f"HEAD:{rel}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False).returncode==0

def clean_sync():
    if git("branch","--show-current")!="main": raise RuntimeError("Expected branch main")
    if git("status","--porcelain"): raise RuntimeError("Clean worktree required")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Local and remote main differ")

def prepare():
    clean_sync()
    if README.is_file():
        if tracked(README):
            print("V59_HOLDOUT004_STATUS: ALREADY_PREPARED")
            return
        git("reset","--quiet","--",str(ROOT.relative_to(REPO))); shutil.rmtree(ROOT,ignore_errors=True)
        print("V59_HOLDOUT004_RECOVERY: STALE_LOCAL_PACKET_CLEANED")
    run(PUBLISH)

def finalize():
    if HISTORY.is_file():
        print("V59_HOLDOUT004_STATUS: JOB_ALREADY_FINALIZED")
        print("STEP_ID:",STEP)
        return
    clean_sync()
    if not DECISIONS.is_file(): raise RuntimeError("DECISIONS-004.json is not present. Semantic review must be published first.")
    data=json.loads(DECISIONS.read_text(encoding="utf-8"))
    if not RESULTS.is_file():
        if data.get("status")!="REVIEW_COMPLETE_PENDING_APPLICATION": raise RuntimeError("Holdout 004 decisions are not ready for application")
        run(APPLY)
    elif data.get("status")!="REVIEW_APPLIED":
        raise RuntimeError("RESULTS-004 exists but decision state is inconsistent")

    if not AUDIT_REPORT.is_file():
        run(AUDIT,"--write")
        generated=[AUDIT_REPORT,ROOT/"RANKING-RESULTS-004.md"]
        git("add","--",*(str(p.relative_to(REPO)) for p in generated))
        git("diff","--cached","--check")
        git("commit","-m","V59: publish retrain holdout 004 ranking audit")
        git("push","origin","main")
        git("fetch","--quiet","origin","main")
        if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Audit push verification failed")

    run(GOGIT,"--step",STEP,"--audit",str(PUBLIC_AUDIT.relative_to(REPO)))

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("action",choices=("prepare","finalize")); a=ap.parse_args()
    if a.action=="prepare": prepare()
    else: finalize()

if __name__=="__main__": main()
