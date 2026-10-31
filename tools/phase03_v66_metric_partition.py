#!/usr/bin/env python3
"""Partition complete V66 numeric output into two 30-metric GOGIT audits.

The established GOGIT safety ceiling (30 metrics per audit) is unchanged.
Each part re-evaluates the same frozen checkpoint and VALIDATION to avoid
publishing or trusting a mutable local 57-field cache. This deliberately
trades a second GPU inference pass for isolated, immutable reports.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

V66_SOURCE=REPO/"tools"/"public-audits"/"phase03_v66_token_prediction_bias_001.py"
SAFETY_KEYS=("SEMANTIC_VALIDATION_COMPLETE","TRAINING_AUTHORIZED","TRAINING_STARTED")
FIXED_KEYS=tuple("V66_BIAS_"+x for x in (
    "PASS","BLIND_ACCESS","GPU_BF16","GPU_PEAK_MIB",
    "TRAIN_LEXICAL","TRAIN_TYPES","VAL_TOKENS","VAL_LEXICAL",
    "VAL_CE_X1000","EOS_TOP1","BYTE_TARGETS","MERGE_TARGETS",
))
CONF_KEYS=tuple(
    f"V66_BIAS_CONF_{gold}_P{pred}"
    for gold in ("B","M") for pred in ("B","M","S")
)
MASS_KEYS=tuple(
    f"V66_BIAS_MASS_{gold}_{pred}_BP"
    for gold in ("B","M") for pred in ("B","M","S")
)
BIN_NAMES=(
    "B0","B1_9","B10_99","B100_999","B1000P",
    "M0","M1_9","M10_99","M100_999","M1000P",
)
BIN_KEYS=tuple(
    f"V66_BIAS_{bucket}_{metric}"
    for bucket in BIN_NAMES for metric in ("COUNT","TOP1_BP","NLL_X1000")
)
PART_A_KEYS=FIXED_KEYS+CONF_KEYS+MASS_KEYS+BIN_KEYS[:3]
PART_B_KEYS=BIN_KEYS[3:]
ALL_CUSTOM_KEYS=FIXED_KEYS+CONF_KEYS+MASS_KEYS+BIN_KEYS


def check_partition():
    if not (
        len(PART_A_KEYS)==27 and len(PART_B_KEYS)==27
        and len(ALL_CUSTOM_KEYS)==54
        and set(PART_A_KEYS).isdisjoint(PART_B_KEYS)
        and set(PART_A_KEYS)|set(PART_B_KEYS)==set(ALL_CUSTOM_KEYS)
        and len(set(ALL_CUSTOM_KEYS))==54
    ):
        raise RuntimeError("V66 partition must cover exactly 54 distinct numeric fields")


def read_v66_module():
    if not V66_SOURCE.is_file() or V66_SOURCE.is_symlink():
        raise RuntimeError("Original V66 numeric audit source is unavailable")
    spec=importlib.util.spec_from_file_location("v66_full_metric_source",V66_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load V66 full metric audit")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compute_complete_report() -> dict:
    """Perform immutable V66 checks, then obtain the complete numeric report."""
    check_partition()
    original=read_v66_module()
    v65=original.load_committed("v66_partition_v65",original.V65_SRC)
    helper=original.load_committed("v66_partition_v64",original.V64_SRC)
    prior=helper.read_json(original.HISTORY/f"{original.V65_STEP}.json")
    metrics=prior.get("metrics",{})
    if not (
        prior.get("step_id")==original.V65_STEP
        and prior.get("semantic_validation_complete") is False
        and prior.get("training_authorized") is False
        and metrics.get("V65_FREQ_PASS")==1
        and metrics.get("V65_FREQ_BLIND_ACCESS")==0
        and metrics.get("V65_FREQ_VAL_LEXICAL")==9170
        and metrics.get("V65_FREQ_VAL_EOS_TOP1")==14
    ):
        raise RuntimeError("V66 prerequisite V65 GOGIT report is invalid")
    model,device,streams,validation=helper.preflight()
    train=v65.count_training_tokens(streams)
    torch.cuda.reset_peak_memory_stats(device)
    scored=original.evaluate(model,device,validation,train)
    peak=math.ceil(torch.cuda.max_memory_allocated(device)/(1024*1024))
    report=original.build_report(scored,train,int(peak),prior)
    if not (
        len(report)==57 and set(report)==set(SAFETY_KEYS)|set(ALL_CUSTOM_KEYS)
        and all(type(value) is int and 0<=value<=100_000_000 for value in report.values())
        and all(report[k]==0 for k in SAFETY_KEYS)
        and report["V66_BIAS_PASS"]==1
        and report["V66_BIAS_BLIND_ACCESS"]==0
    ):
        raise RuntimeError("Complete V66 numeric report or safety gate invalid")
    return report


def select_part(report:dict,part:str)->dict:
    check_partition()
    if not (len(report)==57 and set(report)==set(SAFETY_KEYS)|set(ALL_CUSTOM_KEYS)):
        raise RuntimeError("Cannot split an incomplete or unexpected V66 report")
    keys=PART_A_KEYS if part=="A" else PART_B_KEYS if part=="B" else None
    if keys is None:
        raise RuntimeError("Unknown V66 publication part")
    selected={k:report[k] for k in (*SAFETY_KEYS,*keys)}
    if len(selected)!=30 or any(type(v) is not int for v in selected.values()):
        raise RuntimeError("V66 GOGIT publication exceeds 30-metric limit")
    return selected


def publish_part(part:str):
    selected=select_part(compute_complete_report(),part)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key,val in sorted(selected.items()):
        print(f"{key}: {val}")
