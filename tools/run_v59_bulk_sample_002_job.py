#!/usr/bin/env python3
"""Two-command driver for the V59 Sample 002 job."""

from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/"reviews"/"smoltalk-v59-bulk-sample-002"
README=ROOT/"README.md"
DECISIONS=ROOT/"DECISIONS-002.json"
RESULTS=ROOT/"RESULTS-002.md"
PUBLISH=REPO/"tools"/"publish_smoltalk_v59_bulk_sample_002.py"
APPLY=REPO/"tools"/"apply_smoltalk_v59_bulk_sample_002.py"
GOGIT=REPO/"tools"/"gogit_public.py"
AUDIT=REPO/"tools"/"public-audits"/"phase03_v59_bulk_combined_audit.py"
STEP_ID="PHASE03-SMOLTALK-V59-BULK-COMBINED-002"
HISTORY=REPO/"reports"/"assistant-results"/"history"/f"{STEP_ID}.json"

def run(*args):
    p=subprocess.run([sys.executable,*map(str,args)],cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
    if p.stdout: print(p.stdout,end="")
    if p.returncode: raise RuntimeError(f"Subprocess failed with status {p.returncode}")

def prepare():
    if README.is_file():
        print("V59_SAMPLE_002_STATUS: ALREADY_PREPARED")
        return
    run(PUBLISH)

def finalize():
    if HISTORY.is_file():
        print("V59_SAMPLE_002_STATUS: JOB_ALREADY_FINALIZED")
        print("STEP_ID:",STEP_ID)
        return
    if not DECISIONS.is_file():
        raise RuntimeError("DECISIONS-002.json is not present. Semantic review must be published first.")
    data=json.loads(DECISIONS.read_text(encoding="utf-8"))
    if not RESULTS.is_file():
        if data.get("status")!="REVIEW_COMPLETE_PENDING_APPLICATION":
            raise RuntimeError("Sample 002 decisions are not ready for application")
        run(APPLY)
    elif data.get("status")!="REVIEW_APPLIED":
        raise RuntimeError("RESULTS-002 exists but decision state is inconsistent")
    run(GOGIT,"--step",STEP_ID,"--audit",str(AUDIT.relative_to(REPO)))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("prepare","finalize"))
    args=parser.parse_args()
    if args.action=="prepare": prepare()
    else: finalize()

if __name__=="__main__": main()
