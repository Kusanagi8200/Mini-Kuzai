#!/usr/bin/env python3
"""Non-interactive V63 private-generation -> numeric GOGIT -> remote verify.

No subjective ratings, no prompts for human input, no training, no BLIND.
After publication, ChatGPT can analyze the public numeric report on GitHub.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
PYTHON=Path("/root/Mini-Kuzai/.venv/bin/python")
RUN=Path("/root/Mini-Kuzai/runs/v62-margin-001")
STEP="PHASE03-SMOLTALK-V63-AUTOMATIC-LANGUAGE-SCREEN-001"
AUDIT="tools/public-audits/phase03_v63_automatic_language_screen_001.py"
PRIVATE_GENERATOR="tools/phase03_v63_semantic_generation_review_001.py"
TEST="test_phase03_v63_automatic_language_screen_001.py"
HISTORY=REPO/"reports"/"assistant-results"/"history"/f"{STEP}.json"


def git(*args):
    result=subprocess.run(
        ["git","-C",str(REPO),*args],
        text=True,capture_output=True,check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Git failed")
    return result.stdout.strip()


def verify_git():
    if git("branch","--show-current")!="main" or git("status","--porcelain"):
        raise RuntimeError("Require clean main worktree before publication")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local main is not synchronized with origin/main")


def read_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe report: {path.name}")
    result=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result,dict):
        raise RuntimeError("Expected JSON object")
    return result


def preflight():
    if not PYTHON.is_file():
        raise RuntimeError("Frozen Python virtual environment absent")
    if not RUN.is_dir() or RUN.is_symlink() or (RUN/".training.lock").exists():
        raise RuntimeError("V62 training lock or runtime invalid")
    s=read_json(RUN/"RUN-SUMMARY.json")
    m=read_json(RUN/"RUN-MANIFEST.json")
    if not (
        s.get("schema_version")=="v62-margin-run-summary-1"
        and m.get("schema_version")=="v62-margin-run-1"
        and s.get("status")==m.get("status")=="STOPPED"
        and s.get("stop_reason")=="MILESTONE_REVIEW_REQUIRED"
        and s.get("optimizer_steps")==69
        and s.get("exposure_tokens")==597982
        and s.get("blind_test_accessed") is False
        and m.get("blind_test_during_training") is False
        and m.get("resume") is False
    ):
        raise RuntimeError("V62 frozen cycle-2 run changed")
    ck=RUN/"checkpoint-cycle-02.pt"
    if not ck.is_file() or ck.is_symlink():
        raise RuntimeError("Missing or unsafe checkpoint")
    prior="PHASE03-SMOLTALK-V63-DECODING-ROBUSTNESS-001"
    old=read_json(REPO/"reports"/"assistant-results"/"history"/f"{prior}.json")
    metrics=old.get("metrics",{})
    if not (
        old.get("step_id")==prior
        and old.get("semantic_validation_complete") is True
        and metrics.get("V63_ROB_PASS")==1
        and metrics.get("V63_ROB_BLIND_ACCESS")==0
        and metrics.get("V63_ROB_SEEDS")==8
    ):
        raise RuntimeError("V63 frozen robustness GOGIT prerequisite invalid")


def check_history():
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
        and m.get("V63_AUTO_PASS")==1
        and m.get("V63_AUTO_BLIND_ACCESS")==0
        and m.get("V63_AUTO_HUMAN_RATINGS")==0
        and m.get("V63_AUTO_SAMPLES")==24
    ):
        raise RuntimeError("GOGIT automatic language screening report invalid")


def checked(command,label):
    result=subprocess.run(command,cwd=REPO,check=False)
    if result.returncode:
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")


def main():
    verify_git()
    preflight()
    if HISTORY.exists():
        check_history()
        print("V63_AUTO_GOGIT: ALREADY_PUBLISHED")
        return
    checked([
        str(PYTHON),"-m","unittest","discover","-s","tests",
        "-p",TEST,"-v",
    ],"V63 automated proxy unit tests")
    # Existing sample generator is explicitly non-interactive in prepare mode.
    # It reuses samples-private.json when present. It never touches ratings.
    checked([str(PYTHON),PRIVATE_GENERATOR,"prepare"],"Private GPU sample preparation")
    verify_git()
    checked([
        str(PYTHON),"tools/gogit_public.py",
        "--step",STEP,"--audit",AUDIT
    ],"GOGIT publish")
    verify_git()
    check_history()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V63_AUTO_GOGIT: PUBLISHED")
    print("STEP_ID:",STEP)
    print("SAMPLES: 24")
    print("HUMAN_RATINGS: 0")
    print("TRAINING_RESTARTED: 0")
    print("BLIND_ACCESS: 0")
    print("HEAD:",git("rev-parse","--short","HEAD"))


if __name__=="__main__":
    try:
        main()
    except (RuntimeError,KeyboardInterrupt) as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V63_AUTO_GOGIT: NOT_CONFIRMED")
        print("ERROR:",str(exc))
        sys.exit(1)
