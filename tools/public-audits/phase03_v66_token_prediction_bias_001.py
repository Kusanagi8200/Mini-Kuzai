#!/usr/bin/env python3
"""V66 read-only Byte-BPE prediction-bias audit on frozen V62 checkpoint.

Numerical GOGIT only. Reuses verified, once-only V64 frozen preflight and
V65 full-TRAIN frequency estimator. VALIDATION only, never the BLIND TEST.
Class confusion includes SPECIAL argmax for lexical gold targets. Probability
mass uses all 1024 logits, not only the best token.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from collections import Counter
from pathlib import Path

import torch
import torch.nn.functional as F

REPO=Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
from mini_kuzai import phase03_v62_trainer as T

HISTORY=REPO/"reports"/"assistant-results"/"history"
V65_STEP="PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001"
V64_SRC=REPO/"tools"/"public-audits"/"phase03_v64_language_learning_diagnostic_002.py"
V65_SRC=REPO/"tools"/"public-audits"/"phase03_v65_token_frequency_diagnostic_001.py"
BIN_NAMES=(
    "B0","B1_9","B10_99","B100_999","B1000P",
    "M0","M1_9","M10_99","M100_999","M1000P",
)
GOLD=("B","M")
PRED=("B","M","S")
BATCH=4


def load_committed(name:str,path:Path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required frozen audit dependency unavailable")
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import frozen audit dependency")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frequency_bucket(token:int,frequency:int)->str:
    if type(token) is not int or not 3<=token<T.VOCAB_SIZE:
        raise ValueError("Only non-special V56 target tokens are classified")
    if type(frequency) is not int or frequency<0:
        raise ValueError("TRAIN frequency must be a nonnegative integer")
    label="B" if token<259 else "M"
    if frequency==0:
        return label+"0"
    if frequency<=9:
        return label+"1_9"
    if frequency<=99:
        return label+"10_99"
    if frequency<=999:
        return label+"100_999"
    return label+"1000P"


def predicted_kind(token:int)->str:
    if type(token) is not int or not 0<=token<T.VOCAB_SIZE:
        raise ValueError("Invalid top-1 prediction token")
    return "S" if token<3 else "B" if token<259 else "M"


def blank_result()->dict:
    return {
        "bins":{name:{"count":0,"correct":0,"nll":0.0} for name in BIN_NAMES},
        "conf":{(gold,pred):0 for gold in GOLD for pred in PRED},
        "prob":{(gold,pred):0.0 for gold in GOLD for pred in PRED},
        "gold":{"B":0,"M":0},
        "total_targets":0,
        "lexical":0,
        "full_nll":0.0,
        "eos":0,
    }


def consume_predictions(stats:dict,gold:torch.Tensor,pred:torch.Tensor,nll:torch.Tensor,
                        probs:torch.Tensor,frequency:Counter)->None:
    """Accumulate only counts and sums, never token IDs or text in output."""
    if gold.ndim!=1 or pred.shape!=gold.shape or nll.shape!=gold.shape:
        raise RuntimeError("Token prediction tensors are not aligned")
    if probs.shape!=(gold.numel(),T.VOCAB_SIZE):
        raise RuntimeError("Full-vocabulary probability tensor required")
    if (gold<3).any() or (gold>=T.VOCAB_SIZE).any():
        raise RuntimeError("SPECIAL target passed to lexical accumulator")
    if not torch.isfinite(nll).all() or not torch.isfinite(probs).all():
        raise RuntimeError("Nonfinite prediction probability or loss")

    gold_cpu=gold.detach().cpu().tolist()
    pred_cpu=pred.detach().cpu().tolist()
    nll_cpu=nll.detach().cpu().tolist()
    byteraw=probs[:,:3].sum(dim=1).detach().cpu().tolist()
    byte=probs[:,3:259].sum(dim=1).detach().cpu().tolist()
    merged=probs[:,259:].sum(dim=1).detach().cpu().tolist()
    for true_id,best_id,loss,ps,pb,pm in zip(
        gold_cpu,pred_cpu,nll_cpu,byteraw,byte,merged
    ):
        observed=frequency.get(int(true_id),0)
        bucket=frequency_bucket(int(true_id),int(observed))
        target_family="B" if true_id<259 else "M"
        predicted_family=predicted_kind(int(best_id))
        if not abs(float(ps)+float(pb)+float(pm)-1.0)<1e-4:
            raise RuntimeError("Unnormalized full-vocabulary probability mass")
        entry=stats["bins"][bucket]
        entry["count"]+=1
        entry["correct"]+=int(true_id==best_id)
        entry["nll"]+=float(loss)
        stats["conf"][(target_family,predicted_family)]+=1
        stats["gold"][target_family]+=1
        stats["prob"][(target_family,"S")]+=float(ps)
        stats["prob"][(target_family,"B")]+=float(pb)
        stats["prob"][(target_family,"M")]+=float(pm)
        stats["lexical"]+=1


def evaluate(model,device,validation:list,frequency:Counter)->dict:
    if len(validation)!=36:
        raise RuntimeError("Expected full VALIDATION 36 segments")
    result=blank_result()
    model.eval()
    with torch.inference_mode():
        for offset in range(0,len(validation),BATCH):
            selected=validation[offset:offset+BATCH]
            ids=torch.full(
                (len(selected),max(len(s.token_ids) for s in selected)),
                T.PAD_ID,dtype=torch.long,device=device
            )
            for row,seg in enumerate(selected):
                if seg.token_ids[0]!=T.BOS_ID or seg.token_ids[-1]!=T.EOS_ID:
                    raise RuntimeError("Frozen VALIDATION boundary mismatch")
                ids[row,:len(seg.token_ids)]=torch.as_tensor(
                    seg.token_ids,dtype=torch.long,device=device
                )
            with torch.autocast(device_type="cuda",dtype=torch.bfloat16):
                logits=model(ids).float()[:,:-1,:]
            targets=ids[:,1:]
            valid=targets.ne(T.PAD_ID)
            loss=F.cross_entropy(
                logits.reshape(-1,T.VOCAB_SIZE),
                targets.reshape(-1),
                reduction="none",ignore_index=T.PAD_ID
            ).reshape_as(targets)
            result["total_targets"]+=int(valid.sum().item())
            result["full_nll"]+=float(loss[valid].sum().item())
            predictions=logits.argmax(dim=-1)
            for row,seg in enumerate(selected):
                idx=len(seg.token_ids)-2
                if int(targets[row,idx].item())!=T.EOS_ID:
                    raise RuntimeError("Frozen VALIDATION EOS missing")
                result["eos"]+=int(int(predictions[row,idx].item())==T.EOS_ID)

            lexical=valid & targets.ge(3) & targets.lt(T.VOCAB_SIZE)
            if int(lexical.sum().item()):
                values=logits[lexical]
                mass=F.softmax(values,dim=-1)
                consume_predictions(
                    result,targets[lexical],predictions[lexical],
                    loss[lexical],mass,frequency
                )
    if result["total_targets"]!=9206 or result["lexical"]!=9170:
        raise RuntimeError("VALIDATION token inventory differs from frozen V64")
    if result["eos"]!=14:
        raise RuntimeError("EOS result does not match V63/V64/V65")
    if sum(result["gold"].values())!=9170:
        raise RuntimeError("Missing lexical gold type")
    if result["gold"]["B"]!=4876 or result["gold"]["M"]!=4294:
        raise RuntimeError("V65 type proportions not reproduced")
    if sum(result["conf"].values())!=9170:
        raise RuntimeError("Confusion matrix does not cover lexical targets")
    ce=round(result["full_nll"]*1000/result["total_targets"])
    if abs(ce-4733)>2:
        raise RuntimeError("CE differs from V64/V65 reference")
    result["ce_x1000"]=ce
    return result


def build_report(stats:dict,train:Counter,peak:int,prior:dict)->dict:
    if set(stats["bins"])!=set(BIN_NAMES):
        raise RuntimeError("Missing predefined V66 frequency strata")
    if stats["total_targets"]!=9206 or stats["lexical"]!=9170 or stats["eos"]!=14:
        raise RuntimeError("Incomplete validation prediction inventory")
    if sum(stats["gold"].values())!=stats["lexical"]:
        raise RuntimeError("Target type coverage mismatch")
    if sum(stats["conf"].values())!=stats["lexical"]:
        raise RuntimeError("Confusion count mismatch")
    old=prior.get("metrics",{})
    if not (
        sum(train.values())==old.get("V65_FREQ_TRAIN_LEXICAL")==294726
        and len(train)==old.get("V65_FREQ_TRAIN_TYPES")==891
        and stats["ce_x1000"]==old.get("V65_FREQ_VAL_CE_X1000")==4733
    ):
        raise RuntimeError("V65 frequency inventory or CE changed")
    output={
        "SEMANTIC_VALIDATION_COMPLETE":0,
        "TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,
        "V66_BIAS_PASS":1,
        "V66_BIAS_BLIND_ACCESS":0,
        "V66_BIAS_GPU_BF16":1,
        "V66_BIAS_GPU_PEAK_MIB":peak,
        "V66_BIAS_TRAIN_LEXICAL":sum(train.values()),
        "V66_BIAS_TRAIN_TYPES":len(train),
        "V66_BIAS_VAL_TOKENS":stats["total_targets"],
        "V66_BIAS_VAL_LEXICAL":stats["lexical"],
        "V66_BIAS_VAL_CE_X1000":stats["ce_x1000"],
        "V66_BIAS_EOS_TOP1":stats["eos"],
        "V66_BIAS_BYTE_TARGETS":stats["gold"]["B"],
        "V66_BIAS_MERGE_TARGETS":stats["gold"]["M"],
    }
    for gold in GOLD:
        n=stats["gold"][gold]
        if n<=0:
            raise RuntimeError("No target tokens for probability mass audit")
        mass_sum=0
        for predicted in PRED:
            confusion=stats["conf"][(gold,predicted)]
            mass=int(round(stats["prob"][(gold,predicted)]*10000/n))
            output[f"V66_BIAS_CONF_{gold}_P{predicted}"]=confusion
            output[f"V66_BIAS_MASS_{gold}_{predicted}_BP"]=mass
            mass_sum+=mass
        if abs(mass_sum-10000)>2:
            raise RuntimeError("Per-target-class probability mass not normalized")
        if sum(stats["conf"][(gold,x)] for x in PRED)!=n:
            raise RuntimeError("Per-target-class confusion row not complete")
    for bucket in BIN_NAMES:
        item=stats["bins"][bucket]
        n=item["count"]
        if not 0<=item["correct"]<=n:
            raise RuntimeError("Invalid V66 bucket prediction counters")
        output[f"V66_BIAS_{bucket}_COUNT"]=n
        output[f"V66_BIAS_{bucket}_TOP1_BP"]=round(10000*item["correct"]/n) if n else 0
        output[f"V66_BIAS_{bucket}_NLL_X1000"]=round(1000*item["nll"]/n) if n else 0
    if sum(stats["bins"][b]["count"] for b in BIN_NAMES)!=9170:
        raise RuntimeError("V66 detailed strata do not cover VALIDATION")
    # Collapse fine-grained bins back to the immutable V65 three-tier groups.
    for family in GOLD:
        expected={
            "0":stats["bins"][family+"0"]["count"],
            "1_9":stats["bins"][family+"1_9"]["count"],
            "10P":sum(stats["bins"][family+s]["count"] for s in ("10_99","100_999","1000P")),
        }
        for suffix,count in expected.items():
            if count!=old.get(f"V65_FREQ_{family}{suffix}_COUNT"):
                raise RuntimeError("V66 frequency-bin totals contradict published V65")
    if len(output)!=57 or any(
        type(v) is not int or v<0 or v>100_000_000
        for v in output.values()
    ):
        raise RuntimeError("Unexpected or nonnumeric V66 GOGIT report")
    return output


def main():
    v65=load_committed("v66_v65_frequency_helper",V65_SRC)
    helper=load_committed("v66_v64_frozen_helper",V64_SRC)
    prior=helper.read_json(HISTORY/f"{V65_STEP}.json")
    metrics=prior.get("metrics",{})
    if (
        prior.get("step_id")!=V65_STEP
        or prior.get("semantic_validation_complete") is not False
        or prior.get("training_authorized") is not False
        or metrics.get("V65_FREQ_PASS")!=1
        or metrics.get("V65_FREQ_BLIND_ACCESS")!=0
        or metrics.get("V65_FREQ_VAL_LEXICAL")!=9170
        or metrics.get("V65_FREQ_VAL_EOS_TOP1")!=14
    ):
        raise RuntimeError("V65 frozen prerequisite missing or invalid")
    model,device,streams,validation=helper.preflight()
    train=v65.count_training_tokens(streams)
    torch.cuda.reset_peak_memory_stats(device)
    scored=evaluate(model,device,validation,train)
    peak=int(math.ceil(torch.cuda.max_memory_allocated(device)/(1024*1024)))
    report=build_report(scored,train,peak,prior)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for name,value in sorted(report.items()):
        print(f"{name}: {value}")


if __name__=="__main__":
    main()
