#!/usr/bin/env python3
"""V66: 8+8 CPU tests; two numeric-only, immutable 30-metric GOGIT pushes.

No change to global 30-metric safety limit. Each public audit reruns read-only
GPU inference against the same frozen V62 checkpoint and VALIDATION data.
On an interrupted second publication, rerun safely: validated Part A is reused.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO))
from tools import phase03_v66_metric_partition as P

PYTHON=Path("/root/Mini-Kuzai/.venv/bin/python")
RUN=Path("/root/Mini-Kuzai/runs/v62-margin-001")
REPORTS=REPO/"reports"/"assistant-results"/"history"
PREFIX="PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-"
FILES={
    "A":"tools/public-audits/phase03_v66_token_prediction_bias_part_a_001.py",
    "B":"tools/public-audits/phase03_v66_token_prediction_bias_part_b_001.py",
}
SAFETY=P.SAFETY_KEYS


def git(*args):
    x=subprocess.run(["git","-C",str(REPO),*args],
                     text=True,capture_output=True,check=False)
    if x.returncode:
        raise RuntimeError(x.stderr.strip() or x.stdout.strip() or "Git command failed")
    return x.stdout.strip()


def require_synced():
    if git("branch","--show-current")!="main" or git("status","--porcelain"):
        raise RuntimeError("Expected clean main before GOGIT run")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local Git main is not synchronized with origin/main")


def read_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe audit/run JSON: "+path.name)
    result=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result,dict):
        raise RuntimeError("Invalid JSON document: "+path.name)
    return result


def preflight():
    if not PYTHON.is_file() or not RUN.is_dir() or RUN.is_symlink():
        raise RuntimeError("Frozen V62 runtime missing")
    if (RUN/".training.lock").exists():
        raise RuntimeError("Stopped checkpoint has an active training lock")
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
        raise RuntimeError("Frozen V62 run no longer satisfies stop gate")
    ck=RUN/"checkpoint-cycle-02.pt"
    if not ck.is_file() or ck.is_symlink():
        raise RuntimeError("Frozen V62 checkpoint not available")
    prior=read_json(REPORTS/"PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001.json")
    m=prior.get("metrics",{})
    if not (
        prior.get("semantic_validation_complete") is False
        and prior.get("training_authorized") is False
        and m.get("V65_FREQ_PASS")==1
        and m.get("V65_FREQ_BLIND_ACCESS")==0
        and m.get("V65_FREQ_VAL_LEXICAL")==9170
        and m.get("V65_FREQ_VAL_EOS_TOP1")==14
    ):
        raise RuntimeError("Immutable V65 prerequisite report invalid")
    P.check_partition()


def step(part):
    return f"{PREFIX}{part}-001"


def history(part):
    return REPORTS/f"{step(part)}.json"


def validate_history(part):
    report=read_json(history(part))
    metrics=report.get("metrics",{})
    fields=P.PART_A_KEYS if part=="A" else P.PART_B_KEYS
    if not (
        report.get("step_id")==step(part)
        and report.get("producer")==FILES[part]
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics,dict)
        and set(metrics)==set(SAFETY)|set(fields)
        and len(metrics)==30
        and all(metrics.get(k)==0 for k in SAFETY)
        and all(type(value) is int and 0<=value<=100_000_000 for value in metrics.values())
    ):
        raise RuntimeError("Published GOGIT Part "+part+" failed immutable-report validation")
    if part=="A" and not (
        metrics.get("V66_BIAS_PASS")==1
        and metrics.get("V66_BIAS_BLIND_ACCESS")==0
        and metrics.get("V66_BIAS_GPU_BF16")==1
        and metrics.get("V66_BIAS_VAL_TOKENS")==9206
        and metrics.get("V66_BIAS_VAL_LEXICAL")==9170
        and metrics.get("V66_BIAS_BYTE_TARGETS")==4876
        and metrics.get("V66_BIAS_MERGE_TARGETS")==4294
        and metrics.get("V66_BIAS_TRAIN_LEXICAL")==294726
        and metrics.get("V66_BIAS_TRAIN_TYPES")==891
        and metrics.get("V66_BIAS_EOS_TOP1")==14
        and abs(metrics.get("V66_BIAS_VAL_CE_X1000",-999)-4733)<=2
        and sum(metrics[f"V66_BIAS_CONF_{gold}_P{pred}"]
                for gold in ("B","M") for pred in ("B","M","S"))==9170
    ):
        raise RuntimeError("V66-A numeric checkpoint or confusion invariants violated")
    return metrics


def validate_combined():
    a=validate_history("A")
    b=validate_history("B")
    result={**a,**b}
    if len(result)!=57 or set(result)!=set(SAFETY)|set(P.ALL_CUSTOM_KEYS):
        raise RuntimeError("The two V66 numeric GOGIT reports are not a complete 57-field partition")
    if sum(result[f"V66_BIAS_{name}_COUNT"] for name in P.BIN_NAMES)!=9170:
        raise RuntimeError("V66 frequency groups do not cover lexical VALIDATION")
    for family,n in (("B",4876),("M",4294)):
        if sum(result[f"V66_BIAS_CONF_{family}_P{k}"] for k in ("B","M","S"))!=n:
            raise RuntimeError("V66 top-1 family confusion row totals differ")
        if abs(sum(result[f"V66_BIAS_MASS_{family}_{k}_BP"] for k in ("B","M","S"))-10000)>2:
            raise RuntimeError("V66 per-class output probability mass does not normalize")
    previous=read_json(REPORTS/"PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001.json")["metrics"]
    for family in ("B","M"):
        buckets={
            "0":result[f"V66_BIAS_{family}0_COUNT"],
            "1_9":result[f"V66_BIAS_{family}1_9_COUNT"],
            "10P":sum(result[f"V66_BIAS_{family}{tier}_COUNT"]
                      for tier in ("10_99","100_999","1000P")),
        }
        for k,n in buckets.items():
            if n!=previous.get(f"V65_FREQ_{family}{k}_COUNT"):
                raise RuntimeError("V66 frequency buckets differ from frozen V65")
    return result


def checked(command,label):
    proc=subprocess.run(command,cwd=REPO,check=False)
    if proc.returncode:
        raise RuntimeError(label+" failed with exit "+str(proc.returncode))


def main():
    require_synced()
    preflight()
    checked([
        str(PYTHON),"-m","unittest","discover","-s","tests",
        "-p","test_phase03_v66_*.py","-v"
    ],"V66 original and partition CPU tests")
    for part in ("A","B"):
        require_synced()
        if history(part).exists():
            validate_history(part)
            print("V66_PART_"+part+": ALREADY_PUBLISHED",flush=True)
            continue
        checked([
            str(PYTHON),"tools/gogit_public.py",
            "--step",step(part),"--audit",FILES[part],
        ],"GOGIT V66 Part "+part)
        require_synced()
        validate_history(part)
    validate_combined()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V66_GOGIT: BOTH_PARTS_PUBLISHED")
    print("PARTS: 2")
    print("NUMERIC_FIELDS_COMPLETE: 57")
    print("PUBLIC_METRICS_EACH: 30")
    print("GLOBAL_METRIC_CAP_UNCHANGED: 30")
    print("TRAINING_RESTARTED: 0")
    print("BLIND_ACCESS: 0")
    print("HEAD:",git("rev-parse","--short","HEAD"))


if __name__=="__main__":
    try:
        main()
    except (RuntimeError,KeyboardInterrupt) as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V66_GOGIT: NOT_CONFIRMED")
        print("ERROR:",str(exc))
        sys.exit(1)
