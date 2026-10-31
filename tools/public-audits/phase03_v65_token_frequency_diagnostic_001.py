#!/usr/bin/env python3
"""V65 frozen-token-frequency diagnostic (numeric GOGIT only, no training).

TRAIN frequency counts use all 345 frozen stream segments; VALIDATION
prediction metrics use all 36 held-out, frozen segments. The existing V64-002
read-only preflight reconstructs the corpus exactly once and verifies
authorization, trainer freeze, schedule preview and checkpoint identity.
No optimizer step, modified tokenizer, checkpoint write or BLIND TEST access.
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
PRIOR="PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002"
SOURCE=REPO/"tools"/"public-audits"/"phase03_v64_language_learning_diagnostic_002.py"
BATCH=4
# Defined before measurement, without adapting thresholds to outcomes.
BINS=("B0","B1_9","B10P","M0","M1_9","M10P")
MIN_TOKEN=3
MERGED_START=259
MAX_TOKEN=1024


def read_v64_helper():
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("Frozen V64-002 preflight helper unavailable")
    spec=importlib.util.spec_from_file_location("v65_frozen_v64_helper",SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import frozen V64-002 diagnostic")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frequency_bin(token:int, observed:int)->str:
    if type(token) is not int or not MIN_TOKEN<=token<MAX_TOKEN:
        raise ValueError("Expected a normal non-special V56 token")
    if type(observed) is not int or observed<0:
        raise ValueError("Negative or invalid frozen TRAIN frequency")
    kind="B" if token<MERGED_START else "M"
    return kind+("0" if observed==0 else "1_9" if observed<10 else "10P")


def count_training_tokens(streams:dict)->Counter:
    if tuple(streams)!=T.STREAMS:
        raise RuntimeError("Unexpected frozen TRAIN stream order")
    counts=Counter()
    for stream,segments in streams.items():
        for seg in segments:
            ids=seg.token_ids
            if len(ids)<2 or ids[0]!=T.BOS_ID or ids[-1]!=T.EOS_ID:
                raise RuntimeError("Invalid frozen TRAIN sequence boundaries")
            for token in ids[1:-1]:
                if not MIN_TOKEN<=token<MAX_TOKEN:
                    raise RuntimeError("Special or invalid token inside TRAIN body")
                counts[int(token)]+=1
    if sum(len(v) for v in streams.values())!=345:
        raise RuntimeError("Frozen TRAIN segment count changed")
    if not 100000<sum(counts.values())<295416:
        raise RuntimeError("Frozen TRAIN lexical-token inventory abnormal")
    if len(counts)<100 or len(counts)>MAX_TOKEN-MIN_TOKEN:
        raise RuntimeError("Frozen TRAIN token-type coverage abnormal")
    return counts


def empty_groups():
    return {key:{"count":0,"correct":0,"loss":0.0} for key in BINS}


def score_validation(model,device,segments:list,frequency:Counter)->tuple[dict,int,int,int]:
    if len(segments)!=36:
        raise RuntimeError("Expected full frozen VALIDATION 36 segments")
    model.eval()
    groups=empty_groups()
    train_frequency=torch.zeros(T.VOCAB_SIZE,dtype=torch.long,device=device)
    for token,count in frequency.items():
        train_frequency[token]=count
    full_nll=0.0
    full_targets=0
    eos_top1=0
    lexical_targets=0
    with torch.inference_mode():
        for start in range(0,len(segments),BATCH):
            batch=segments[start:start+BATCH]
            ids=torch.full(
                (len(batch),max(len(x.token_ids) for x in batch)),
                T.PAD_ID,dtype=torch.long,device=device
            )
            for row,seg in enumerate(batch):
                if seg.token_ids[0]!=T.BOS_ID or seg.token_ids[-1]!=T.EOS_ID:
                    raise RuntimeError("Frozen VALIDATION BOS/EOS invariant failed")
                ids[row,:len(seg.token_ids)]=torch.as_tensor(
                    seg.token_ids,dtype=torch.long,device=device
                )
            with torch.autocast(device_type="cuda",dtype=torch.bfloat16):
                logits=model(ids).float()[:,:-1,:]
            targets=ids[:,1:]
            loss=F.cross_entropy(
                logits.reshape(-1,T.VOCAB_SIZE),
                targets.reshape(-1),
                ignore_index=T.PAD_ID,reduction="none",
            ).reshape_as(targets)
            valid=targets.ne(T.PAD_ID)
            full_targets+=int(valid.sum().item())
            full_nll+=float(loss[valid].sum().item())
            predicted=logits.argmax(dim=-1)
            for row,segment in enumerate(batch):
                end=len(segment.token_ids)-2
                if int(targets[row,end].item())!=T.EOS_ID:
                    raise RuntimeError("Missing end-of-segment EOS in VALIDATION")
                eos_top1+=int(int(predicted[row,end].item())==T.EOS_ID)
            lexical=valid & targets.ge(MIN_TOKEN) & targets.lt(MAX_TOKEN)
            selected=targets[lexical]
            if selected.numel()==0:
                continue
            lexical_targets+=int(selected.numel())
            nll=loss[lexical]
            hit=predicted[lexical].eq(selected)
            counts=train_frequency[selected]
            base=selected.lt(MERGED_START)
            for name in BINS:
                merged=name.startswith("M")
                freq_group=0 if name.endswith("0") else 1 if name.endswith("1_9") else 2
                in_group=(~base if merged else base)
                if freq_group==0:
                    in_group=in_group & counts.eq(0)
                elif freq_group==1:
                    in_group=in_group & counts.ge(1) & counts.le(9)
                else:
                    in_group=in_group & counts.ge(10)
                n=int(in_group.sum().item())
                if n:
                    g=groups[name]
                    g["count"]+=n
                    g["correct"]+=int(hit[in_group].sum().item())
                    g["loss"]+=float(nll[in_group].sum().item())
    if full_targets!=9206 or lexical_targets!=9170 or eos_top1!=14:
        raise RuntimeError("V64/V63 VALIDATION and EOS invariants changed")
    if sum(g["count"] for g in groups.values())!=lexical_targets:
        raise RuntimeError("Incomplete token-frequency bucket coverage")
    overall_ce=round(full_nll*1000/full_targets)
    if abs(overall_ce-4733)>2:
        raise RuntimeError("V65 VALIDATION loss disagrees with V64-002")
    return groups,lexical_targets,overall_ce,eos_top1


def numerical_report(frequency:Counter,groups:dict,lexical:int,val_ce:int,eos:int,peak:int):
    if set(groups)!=set(BINS):
        raise RuntimeError("Expected all predefined frequency bins")
    report={
        "SEMANTIC_VALIDATION_COMPLETE":0,
        "TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,
        "V65_FREQ_PASS":1,
        "V65_FREQ_BLIND_ACCESS":0,
        "V65_FREQ_GPU_BF16":1,
        "V65_FREQ_TRAIN_LEXICAL":sum(frequency.values()),
        "V65_FREQ_TRAIN_TYPES":len(frequency),
        "V65_FREQ_VAL_LEXICAL":lexical,
        "V65_FREQ_VAL_CE_X1000":val_ce,
        "V65_FREQ_VAL_EOS_TOP1":eos,
        "V65_FREQ_GPU_PEAK_MIB":peak,
    }
    for name in BINS:
        values=groups[name]
        n=values["count"]
        if type(n) is not int or n<0 or values["correct"]>n:
            raise RuntimeError("Invalid grouped validation counts")
        prefix=f"V65_FREQ_{name}_"
        report[prefix+"COUNT"]=n
        report[prefix+"TOP1_BP"]=round(values["correct"]*10000/n) if n else 0
        report[prefix+"NLL_X1000"]=round(values["loss"]*1000/n) if n else 0
    if len(report)!=30:
        raise RuntimeError("Unexpected V65 numeric metric count")
    if sum(report[f"V65_FREQ_{name}_COUNT"] for name in BINS)!=lexical:
        raise RuntimeError("Public bucket count does not equal lexical targets")
    if any(type(value) is not int or not 0<=value<=100_000_000 for value in report.values()):
        raise RuntimeError("Invalid numeric-only V65 GOGIT metric")
    return report


def main():
    helper=read_v64_helper()
    previous=helper.read_json(HISTORY/f"{PRIOR}.json")
    m=previous.get("metrics",{})
    if (
        previous.get("step_id")!=PRIOR
        or previous.get("semantic_validation_complete") is not False
        or m.get("V64_LANG_PASS")!=1
        or m.get("V64_LANG_BLIND_ACCESS")!=0
        or m.get("V64_LANG_VAL_EOS_TOP1")!=14
        or m.get("V64_LANG_VAL_TOKENS")!=9206
    ):
        raise RuntimeError("Required published V64-002 numeric evidence invalid")
    model,device,streams,validation=helper.preflight()
    train=count_training_tokens(streams)
    torch.cuda.reset_peak_memory_stats(device)
    groups,lexical,val_ce,eos=score_validation(model,device,validation,train)
    peak=math.ceil(torch.cuda.max_memory_allocated(device)/(1024*1024))
    report=numerical_report(train,groups,lexical,val_ce,eos,peak)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key,val in sorted(report.items()):
        print(f"{key}: {val}")


if __name__=="__main__":
    main()
