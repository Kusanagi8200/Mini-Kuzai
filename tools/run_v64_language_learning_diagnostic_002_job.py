#!/usr/bin/env python3
"""V64 optimized once-only frozen-corpus diagnostic, GPU scoring and GOGIT.

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
STEP="PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002"
AUDIT="tools/public-audits/phase03_v64_language_learning_diagnostic_002.py"
TEST="test_phase03_v64_language_learning_diagnostic_002.py"
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
    prior="PHASE03-SMOLTALK-V63-AUTOMATIC-LANGUAGE-SCREEN-001"
    record=read_json(REPO/"reports"/"assistant-results"/"history"/f"{prior}.json")
    m=record.get("metrics",{})
    if not (
        record.get("step_id")==prior
        and record.get("semantic_validation_complete") is False
        and m.get("V63_AUTO_PASS")==1
        and m.get("V63_AUTO_BLIND_ACCESS")==0
        and m.get("V63_AUTO_HUMAN_RATINGS")==0
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
        and m.get("V64_LANG_PASS")==1
        and m.get("V64_LANG_BLIND_ACCESS")==0
        and m.get("V64_LANG_GPU_BF16")==1
        and m.get("V64_LANG_TRAIN_SEGMENTS")==12
        and m.get("V64_LANG_VAL_SEGMENTS")==36
        and m.get("V64_LANG_VAL_TOKENS")==9206
        and m.get("V64_LANG_VAL_EOS_TOP1")==14
    ):
        raise RuntimeError("Published V64 language diagnostic report invalid")


def checked_run(cmd,label):
    p=subprocess.run(cmd,cwd=REPO,check=False)
    if p.returncode:
        raise RuntimeError(f"{label} failed (exit {p.returncode})")


def main():
    require_synced()
    preflight()
    if HISTORY.exists():
        validate_history()
        print("V64_GOGIT: ALREADY_PUBLISHED")
        return
    checked_run([
        str(PYTHON),"-m","unittest","discover",
        "-s","tests","-p",TEST,"-v",
    ],"V64 CPU tests")
    require_synced()
    checked_run([
        str(PYTHON),"tools/gogit_public.py",
        "--step",STEP,"--audit",AUDIT,
    ],"V64 GOGIT GPU audit and publication")
    require_synced()
    validate_history()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V64_GOGIT: PUBLISHED")
    print("STEP_ID:",STEP)
    print("TRAINING_RESTARTED: 0")
    print("BLIND_ACCESS: 0")
    print("HEAD:",git("rev-parse","--short","HEAD"))


if __name__=="__main__":
    try:
        main()
    except (RuntimeError,KeyboardInterrupt) as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V64_GOGIT: NOT_CONFIRMED")
        print("ERROR:",str(exc))
        sys.exit(1)
