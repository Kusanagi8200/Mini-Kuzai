#!/usr/bin/env python3
"""V70 read-only FP32 precision control for frozen V69 output-head intervention.

Four comparisons on identical V62 frozen validation hidden states:
BF16 original, FP32 original, HALF equalized FP32, FULL equalized FP32.
The V69 HALF/FULL outputs MUST reproduce exactly; no training or BLIND.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from mini_kuzai import phase03_v62_trainer as T

AUDITS=ROOT/"tools"/"public-audits"
V64_SOURCE=AUDITS/"phase03_v64_language_learning_diagnostic_002.py"
V67_SOURCE=AUDITS/"phase03_v67_output_concentration_001.py"
V69_SOURCE=AUDITS/"phase03_v69_output_norm_counterfactual_001.py"
STEP="PHASE03-SMOLTALK-V69-OUTPUT-NORM-COUNTERFACTUAL-001"
REPORT=ROOT/"reports"/"assistant-results"/"history"/f"{STEP}.json"
MODES=("BF16","FP32","HALF","FULL")
FIELDS=("CE_X1000","PRED_DISTINCT","TOP1_SHARE_BP",
        "MERGE_TOP1_BP","MERGE_TOP5_BP","EOS_TOP1")
BATCH=4


def import_frozen(name,source):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("Reviewed V70 dependency missing")
    spec=importlib.util.spec_from_file_location(name,source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Reviewed V70 dependency invalid")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def require_v69_record(helper):
    report=helper.read_json(REPORT)
    source=V69_SOURCE
    metrics=report.get("metrics",{})
    if not (
        report.get("step_id")==STEP
        and report.get("producer")=="tools/public-audits/phase03_v69_output_norm_counterfactual_001.py"
        and report.get("status")=="PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics,dict)
        and metrics.get("V69_NORM_PASS")==1
        and metrics.get("V69_NORM_BLIND_ACCESS")==0
        and metrics.get("V69_NORM_VAL_LEXICAL")==9170
        and metrics.get("V69_NORM_BASE_CE_X1000")==4733
        and metrics.get("V69_NORM_BASE_PRED_DISTINCT")==4
        and all(metrics.get(k)==0 for k in (
            "SEMANTIC_VALIDATION_COMPLETE","TRAINING_AUTHORIZED","TRAINING_STARTED"
        ))
        and hashlib.sha256(source.read_bytes()).hexdigest()==report.get("producer_sha256")
    ):
        raise RuntimeError("Frozen V69 report or producer hash invalid")
    return metrics


def evaluate(model,device,validation,ranker,v69):
    if (
        len(validation)!=36 or model.lm_head.bias is not None
        or model.lm_head.weight.data_ptr()!=model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("Frozen V62 validation or tied-head invariants invalid")
    weights=model.lm_head.weight.detach().float()
    before=weights.clone()
    v69_mod=import_frozen("v70_v69_norm",V69_SOURCE)
    controls={
        "FP32":weights,
        "HALF":v69_mod.equalize_rows(weights,0.5),
        "FULL":v69_mod.equalize_rows(weights,1.0),
    }
    scored={key:v69_mod.empty() for key in MODES}
    taps=[]
    def capture(_module,inputs):
        if len(inputs)!=1 or inputs[0].ndim!=3:
            raise RuntimeError("Frozen model's head input changed")
        taps.append(inputs[0].detach())
    handle=model.lm_head.register_forward_pre_hook(capture)
    model.eval()
    try:
        with torch.inference_mode():
            for offset in range(0,36,BATCH):
                chunk=validation[offset:offset+BATCH]
                ids=torch.full(
                    (len(chunk),max(len(s.token_ids) for s in chunk)),
                    T.PAD_ID,dtype=torch.long,device=device,
                )
                eos_pos=[]
                for row,seg in enumerate(chunk):
                    if seg.token_ids[0]!=T.BOS_ID or seg.token_ids[-1]!=T.EOS_ID:
                        raise RuntimeError("VALIDATION token boundaries changed")
                    ids[row,:len(seg.token_ids)]=torch.as_tensor(
                        seg.token_ids,dtype=torch.long,device=device
                    )
                    eos_pos.append((row,len(seg.token_ids)-2))
                with torch.autocast(device_type="cuda",dtype=torch.bfloat16):
                    original=model(ids).float()[:,:-1,:]
                if len(taps)!=1 or taps[0].shape[:2]!=ids.shape:
                    raise RuntimeError("Frozen output-head input not captured")
                hidden=taps.pop().float()[:,:-1,:]
                gold=ids[:,1:]
                valid=gold.ne(T.PAD_ID)
                v69_mod.update_stats(scored["BF16"],original,gold,valid,eos_pos,ranker)
                with torch.autocast(device_type="cuda",enabled=False):
                    for mode in ("FP32","HALF","FULL"):
                        logits=F.linear(hidden,controls[mode])
                        v69_mod.update_stats(scored[mode],logits,gold,valid,eos_pos,ranker)
                del hidden,original
    finally:
        handle.remove()
        taps.clear()
    if not torch.equal(weights, before):
        raise RuntimeError("V70 unexpectedly modified frozen output weights")
    result={mode:v69_mod.finalize(scored[mode]) for mode in MODES}
    verify_reproduction(result,v69)
    return result


def verify_reproduction(result,v69):
    if set(result)!=set(MODES):
        raise RuntimeError("V70 comparison modes incomplete")
    # V69 published exactly these BF16 original / HALF / FULL values.
    for v70_mode,v69_mode in (("BF16","BASE"),("HALF","HALF"),("FULL","FULL")):
        for field in FIELDS:
            expected=v69.get(f"V69_NORM_{v69_mode}_{field}")
            if expected is None:
                # V69's original baseline omits EOS_TOP1, but V68 publishes it.
                if v69_mode=="BASE" and field=="EOS_TOP1":
                    continue
                # Other base fields in V69 include those below only.
                if v69_mode=="BASE":
                    continue
                raise RuntimeError("Frozen V69 comparison metric absent")
            if result[v70_mode][field]!=expected:
                raise RuntimeError("V70 failed V69 baseline or normalized-mode replay")
    if not (
        result["BF16"]["CE_X1000"]==4733
        and result["BF16"]["PRED_DISTINCT"]==4
        and result["BF16"]["TOP1_SHARE_BP"]==7258
        and result["BF16"]["MERGE_TOP1_BP"]==326
        and result["BF16"]["MERGE_TOP5_BP"]==685
        and result["BF16"]["EOS_TOP1"]==14
    ):
        raise RuntimeError("V70 BF16 original differs from V67/V68")


def build_report(variants):
    if set(variants)!=set(MODES):
        raise RuntimeError("V70 partial modes")
    report={
        "SEMANTIC_VALIDATION_COMPLETE":0,
        "TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,
        "V70_CTRL_PASS":1,
        "V70_CTRL_BLIND_ACCESS":0,
        "V70_CTRL_VAL_LEXICAL":9170,
    }
    for mode in MODES:
        for field in FIELDS:
            report[f"V70_CTRL_{mode}_{field}"]=variants[mode][field]
    if not (
        len(report)==30
        and all(type(value) is int and 0<=value<=100_000_000
                for value in report.values())
    ):
        raise RuntimeError("V70 must publish 30 nonnegative numeric metrics")
    return report


def main():
    v69=import_frozen("v70_v69",V69_SOURCE)
    v64=import_frozen("v70_v64",V64_SOURCE)
    v67=import_frozen("v70_v67",V67_SOURCE)
    metrics=require_v69_record(v64)
    model,device,train,validation=v64.preflight()
    if sum(map(len,train.values()))!=345:
        raise RuntimeError("Frozen TRAIN segment count changed")
    modes=evaluate(model,device,validation,v67.stable_true_ranks,metrics)
    report=build_report(modes)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key,value in sorted(report.items()):
        print(f"{key}: {value}")


if __name__=="__main__":
    main()
