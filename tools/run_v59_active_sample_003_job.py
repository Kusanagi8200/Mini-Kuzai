#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/"reviews"/"smoltalk-v59-active-sample-003"
README=ROOT/"README.md"
DECISIONS=ROOT/"DECISIONS-003.json"
RESULTS=ROOT/"RESULTS-003.md"
PUBLISH=REPO/"tools"/"publish_smoltalk_v59_active_sample_003.py"
APPLY=REPO/"tools"/"apply_smoltalk_v59_active_sample_003.py"
GOGIT=REPO/"tools"/"gogit_public.py"
AUDIT=REPO/"tools"/"public-audits"/"phase03_v59_active_sample_003_audit.py"
STEP="PHASE03-SMOLTALK-V59-ACTIVE-SAMPLE-003"
HISTORY=REPO/"reports"/"assistant-results"/"history"/f"{STEP}.json"

def run(*args):
    p=subprocess.run([sys.executable,*map(str,args)],cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
    if p.stdout: print(p.stdout,end="")
    if p.returncode: raise RuntimeError(f"Subprocess failed with status {p.returncode}")

def prepare():
    if README.is_file():
        rel=str(README.relative_to(REPO))
        tracked=subprocess.run(["git","-C",str(REPO),"cat-file","-e",f"HEAD:{rel}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False).returncode==0
        if tracked:
            print("V59_ACTIVE003_STATUS: ALREADY_PREPARED")
            return
        subprocess.run(["git","-C",str(REPO),"reset","--quiet","--",str(ROOT.relative_to(REPO))],check=False)
        shutil.rmtree(ROOT,ignore_errors=True)
        print("V59_ACTIVE003_RECOVERY: STALE_LOCAL_PACKET_CLEANED")
    run(PUBLISH)

def finalize():
    if HISTORY.is_file():
        print("V59_ACTIVE003_STATUS: JOB_ALREADY_FINALIZED")
        print("STEP_ID:",STEP)
        return
    if not DECISIONS.is_file():
        raise RuntimeError("DECISIONS-003.json is not present. Semantic review must be published first.")
    data=json.loads(DECISIONS.read_text(encoding="utf-8"))
    if not RESULTS.is_file():
        if data.get("status")!="REVIEW_COMPLETE_PENDING_APPLICATION":
            raise RuntimeError("Sample 003 decisions are not ready for application")
        run(APPLY)
    elif data.get("status")!="REVIEW_APPLIED":
        raise RuntimeError("RESULTS-003 exists but decision state is inconsistent")
    run(GOGIT,"--step",STEP,"--audit",str(AUDIT.relative_to(REPO)))

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("action",choices=("prepare","finalize")); a=ap.parse_args()
    if a.action=="prepare": prepare()
    else: finalize()

if __name__=="__main__": main()
