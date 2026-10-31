#!/usr/bin/env python3
"""V67 frozen output-token concentration and stable gold-token-rank GOGIT.

No V62 training, checkpoint modification, BLIND corpus or human interaction.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
PYTHON=Path("/root/Mini-Kuzai/.venv/bin/python")
RUN=Path("/root/Mini-Kuzai/runs/v62-margin-001")
STEP="PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001"
AUDIT="tools/public-audits/phase03_v67_output_concentration_001.py"
TEST="test_phase03_v67_output_concentration_001.py"
HISTORY=REPO/"reports"/"assistant-results"/"history"/f"{STEP}.json"


def git(*args):
    p=subprocess.run(["git","-C",str(REPO),*args],
                     text=True,capture_output=True,check=False)
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or "Git failure")
    return p.stdout.strip()


def require_synced():
    if git("branch","--show-current")!="main" or git("status","--porcelain"):
        raise RuntimeError("Expected clean main")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local main differs from origin/main")


def read_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path.name}")
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):
        raise RuntimeError("Invalid JSON")
    return obj


def preflight():
    if not PYTHON.is_file():
        raise RuntimeError("Frozen venv Python missing")
    if not RUN.is_dir() or RUN.is_symlink() or (RUN/".training.lock").exists():
        raise RuntimeError("V62 run directory invalid or locked")
    summary=read_json(RUN/"RUN-SUMMARY.json")
    manifest=read_json(RUN/"RUN-MANIFEST.json")
    if not (
        summary.get("schema_version")=="v62-margin-run-summary-1"
        and manifest.get("schema_version")=="v62-margin-run-1"
        and summary.get("status")==manifest.get("status")=="STOPPED"
        and summary.get("stop_reason")=="MILESTONE_REVIEW_REQUIRED"
        and summary.get("optimizer_steps")==69
        and summary.get("exposure_tokens")==597982
        and summary.get("blind_test_accessed") is False
        and manifest.get("blind_test_during_training") is False
        and manifest.get("resume") is False
    ):
        raise RuntimeError("Frozen V62 cycle-2 stop state changed")
    ck=RUN/"checkpoint-cycle-02.pt"
    if not ck.is_file() or ck.is_symlink():
        raise RuntimeError("Frozen checkpoint missing or unsafe")
    prior="PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-B-001"
    record=read_json(REPO/"reports"/"assistant-results"/"history"/f"{prior}.json")
    m=record.get("metrics",{})
    if not (
        record.get("step_id")==prior
        and record.get("semantic_validation_complete") is False
        and m.get("V66_BIAS_M1000P_COUNT",0)>0
        and m.get("TRAINING_STARTED")==0
        and m.get("TRAINING_AUTHORIZED")==0
    ):
        raise RuntimeError("Required V63 automatic report invalid")


def validate_history():
    data=read_json(HISTORY)
    m=data.get("metrics",{})
    if not (
        data.get("step_id")==STEP
        and data.get("producer")==AUDIT
        and data.get("semantic_validation_complete") is False
        and data.get("training_authorized") is False
        and data.get("private_conversation_data_included") is False
        and m.get("SEMANTIC_VALIDATION_COMPLETE")==0
        and m.get("TRAINING_AUTHORIZED")==0
        and m.get("TRAINING_STARTED")==0
        and m.get("V67_CONC_PASS")==1
        and m.get("V67_CONC_BLIND_ACCESS")==0
        and m.get("V67_CONC_GPU_BF16")==1
        and m.get("V67_CONC_VAL_TOKENS")==9206
        and m.get("V67_CONC_VAL_LEXICAL")==9170
        and m.get("V67_CONC_EOS_TOP1")==14
        and m.get("V67_CONC_VAL_CE_X1000")==4733
        and 0<m.get("V67_CONC_PRED_DISTINCT",0)<=1024
        and 0<m.get("V67_CONC_GOLD_DISTINCT",0)<=1021
        and m.get("V67_CONC_PRED_BYTE_DISTINCT",0)+m.get("V67_CONC_PRED_MERGE_DISTINCT",0)<=m.get("V67_CONC_PRED_DISTINCT",0)
        and all(0<m.get(f"V67_CONC_TOP{k}_SHARE_BP",0)<=10000 for k in (1,5,10,20))
        and m["V67_CONC_TOP1_SHARE_BP"]<=m["V67_CONC_TOP5_SHARE_BP"]<=m["V67_CONC_TOP10_SHARE_BP"]<=m["V67_CONC_TOP20_SHARE_BP"]
        and 1<=m.get("V67_CONC_BYTE_GOLD_MEDIAN_RANK",0)<=1024
        and 1<=m.get("V67_CONC_MERGE_GOLD_MEDIAN_RANK",0)<=1024
        and len(m)==30
    ):
        raise RuntimeError("Published V67 token concentration report invalid")


def checked_run(cmd,label):
    p=subprocess.run(cmd,cwd=REPO,check=False)
    if p.returncode:
        raise RuntimeError(f"{label} failed (exit {p.returncode})")


def main():
    require_synced()
    preflight()
    if HISTORY.exists():
        validate_history()
        print("V67_CONC_GOGIT: ALREADY_PUBLISHED")
        return
    checked_run([
        str(PYTHON),"-m","unittest","discover",
        "-s","tests","-p",TEST,"-v",
    ],"V67 CPU tests")
    require_synced()
    checked_run([
        str(PYTHON),"tools/gogit_public.py",
        "--step",STEP,"--audit",AUDIT,
    ],"V67 GPU concentration and GOGIT publication")
    require_synced()
    validate_history()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V67_CONC_GOGIT: PUBLISHED")
    print("STEP_ID:",STEP)
    print("TRAINING_RESTARTED: 0")
    print("BLIND_ACCESS: 0")
    print("HEAD:",git("rev-parse","--short","HEAD"))


if __name__=="__main__":
    try:
        main()
    except (RuntimeError,KeyboardInterrupt) as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V67_CONC_GOGIT: NOT_CONFIRMED")
        print("ERROR:",str(exc))
        sys.exit(1)
