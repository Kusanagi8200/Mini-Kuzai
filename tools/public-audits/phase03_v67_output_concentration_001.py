#!/usr/bin/env python3
"""V67 read-only output-token concentration and true-token rank diagnostic.

Full frozen VALIDATION (36 segments), frozen V62 cycle-2 checkpoint, no
gradient, no training, no BLIND. Read-only V64-002 preflight verifies
authorization, trainer freeze, TRAIN/VALIDATION inventory and checkpoint.

The published output is exactly 30 numeric values including 3 safety flags.
Gold-token rank uses descending logits and token-ID-ascending stable tie break
to agree exactly with argmax (no optimistic rank-one ties).
"""
from __future__ import annotations

import importlib.util
import math
import statistics
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
V64_PATH=REPO/"tools"/"public-audits"/"phase03_v64_language_learning_diagnostic_002.py"
V66_A="PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-A-001"
V66_B="PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-B-001"
BATCH=4
CUTS=(1,5,10,20)
GOLD_TOP_K=(1,5,10,50)


def dependency_v64():
    if not V64_PATH.is_file() or V64_PATH.is_symlink():
        raise RuntimeError("Frozen V64-002 helper is missing or unsafe")
    spec=importlib.util.spec_from_file_location("v67_v64_preflight",V64_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import frozen V64-002 helper")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_prerequisites(helper):
    references={}
    for part,step in (("A",V66_A),("B",V66_B)):
        report=helper.read_json(HISTORY/f"{step}.json")
        metrics=report.get("metrics",{})
        if not (
            report.get("step_id")==step
            and report.get("semantic_validation_complete") is False
            and report.get("training_authorized") is False
            and report.get("private_conversation_data_included") is False
            and len(metrics)==30
            and metrics.get("SEMANTIC_VALIDATION_COMPLETE")==0
            and metrics.get("TRAINING_AUTHORIZED")==0
            and metrics.get("TRAINING_STARTED")==0
        ):
            raise RuntimeError("V66 Part "+part+" immutable GOGIT prerequisite invalid")
        references[part]=metrics
    a,b=references["A"],references["B"]
    if not (
        a.get("V66_BIAS_PASS")==1
        and a.get("V66_BIAS_BLIND_ACCESS")==0
        and a.get("V66_BIAS_GPU_BF16")==1
        and a.get("V66_BIAS_VAL_TOKENS")==9206
        and a.get("V66_BIAS_VAL_LEXICAL")==9170
        and a.get("V66_BIAS_BYTE_TARGETS")==4876
        and a.get("V66_BIAS_MERGE_TARGETS")==4294
        and a.get("V66_BIAS_EOS_TOP1")==14
        and a.get("V66_BIAS_VAL_CE_X1000")==4733
        and sum(a.get(f"V66_BIAS_CONF_{g}_P{p}",0)
                for g in ("B","M") for p in ("B","M","S"))==9170
        and sum(b.get(f"V66_BIAS_{g}{tier}_COUNT",0)
                for g in ("B","M") for tier in ("1_9","10_99","100_999","1000P"))
           +a.get("V66_BIAS_B0_COUNT",0)+b.get("V66_BIAS_M0_COUNT",0)==9170
    ):
        raise RuntimeError("V66 published baseline is inconsistent")
    return references


def stable_true_ranks(logits:torch.Tensor,targets:torch.Tensor)->torch.Tensor:
    """1-based true-token rank, ties broken by the smallest token ID."""
    if (
        logits.ndim!=2 or logits.shape[-1]!=T.VOCAB_SIZE
        or targets.ndim!=1 or logits.shape[0]!=targets.numel()
    ):
        raise RuntimeError("Rank inputs have incompatible shapes")
    if targets.numel()==0:
        return torch.empty(0,dtype=torch.long,device=logits.device)
    if (targets<3).any() or (targets>=T.VOCAB_SIZE).any():
        raise RuntimeError("True-rank target must be nonspecial lexical token")
    correct_logit=logits.gather(1,targets.unsqueeze(1))
    ids=torch.arange(T.VOCAB_SIZE,device=logits.device).unsqueeze(0)
    ranks=(logits>correct_logit).sum(1)
    ranks+=((logits==correct_logit)&(ids<targets.unsqueeze(1))).sum(1)
    ranks+=1
    if not torch.equal(ranks.eq(1),logits.argmax(1).eq(targets)):
        raise RuntimeError("Stable top-1 rank disagrees with argmax")
    return ranks


def empty_stats():
    return {
        "val_tokens":0,"lexical":0,"eos_top1":0,
        "val_loss_sum":0.0,
        "predictions":Counter(),"gold":Counter(),
        "ranks":{"B":[],"M":[]},
        "conf":{(g,p):0 for g in ("B","M") for p in ("B","M","S")},
    }


def evaluate(model,device,segments):
    if len(segments)!=36:
        raise RuntimeError("V67 requires every frozen VALIDATION segment")
    stats=empty_stats()
    model.eval()
    with torch.inference_mode():
        for offset in range(0,len(segments),BATCH):
            chunk=segments[offset:offset+BATCH]
            ids=torch.full(
                (len(chunk),max(len(s.token_ids) for s in chunk)),
                T.PAD_ID,dtype=torch.long,device=device,
            )
            for row,seg in enumerate(chunk):
                if seg.token_ids[0]!=T.BOS_ID or seg.token_ids[-1]!=T.EOS_ID:
                    raise RuntimeError("Frozen VALIDATION sequence boundary changed")
                ids[row,:len(seg.token_ids)]=torch.as_tensor(
                    seg.token_ids,dtype=torch.long,device=device
                )
            with torch.autocast(device_type="cuda",dtype=torch.bfloat16):
                logits=model(ids).float()[:,:-1,:]
            gold=ids[:,1:]
            valid=gold.ne(T.PAD_ID)
            nll=F.cross_entropy(
                logits.reshape(-1,T.VOCAB_SIZE),gold.reshape(-1),
                reduction="none",ignore_index=T.PAD_ID,
            ).reshape_as(gold)
            stats["val_tokens"]+=int(valid.sum().item())
            stats["val_loss_sum"]+=float(nll[valid].sum().item())
            top1=logits.argmax(-1)
            for row,seg in enumerate(chunk):
                end=len(seg.token_ids)-2
                if int(gold[row,end].item())!=T.EOS_ID:
                    raise RuntimeError("VALIDATION terminal EOS target changed")
                stats["eos_top1"]+=int(int(top1[row,end].item())==T.EOS_ID)
            lexical=valid&gold.ge(3)&gold.lt(T.VOCAB_SIZE)
            target=gold[lexical]
            if not target.numel():
                continue
            values=logits[lexical]
            predicted=top1[lexical]
            rank=stable_true_ranks(values,target)
            target_ids=target.cpu().tolist()
            predicted_ids=predicted.cpu().tolist()
            target_ranks=rank.cpu().tolist()
            stats["lexical"]+=len(target_ids)
            stats["gold"].update(target_ids)
            stats["predictions"].update(predicted_ids)
            for true_id,pred_id,true_rank in zip(
                target_ids,predicted_ids,target_ranks
            ):
                true_class="B" if true_id<259 else "M"
                pred_class="S" if pred_id<3 else "B" if pred_id<259 else "M"
                stats["conf"][(true_class,pred_class)]+=1
                stats["ranks"][true_class].append(true_rank)

    if (
        stats["val_tokens"]!=9206
        or stats["lexical"]!=9170
        or stats["eos_top1"]!=14
        or sum(stats["predictions"].values())!=9170
        or sum(stats["gold"].values())!=9170
        or len(stats["ranks"]["B"])!=4876
        or len(stats["ranks"]["M"])!=4294
    ):
        raise RuntimeError("V67 VALIDATION inventory/EOS violates frozen reference")
    return stats


def build_report(stats,references,peak):
    if (
        stats["val_tokens"]!=9206 or stats["lexical"]!=9170
        or stats["eos_top1"]!=14
        or len(stats["ranks"]["B"])!=4876
        or len(stats["ranks"]["M"])!=4294
        or sum(stats["predictions"].values())!=9170
        or sum(stats["gold"].values())!=9170
    ):
        raise RuntimeError("Incomplete V67 numeric evaluation")
    a=references["A"]
    if any(stats["conf"][(gold,pred)]!=a.get(f"V66_BIAS_CONF_{gold}_P{pred}")
           for gold in ("B","M") for pred in ("B","M","S")):
        raise RuntimeError("V67 class confusion changed from immutable V66")
    ce=round(stats["val_loss_sum"]*1000/stats["val_tokens"])
    if ce!=a.get("V66_BIAS_VAL_CE_X1000",0):
        raise RuntimeError("V67 teacher-forced CE differs from V66")
    hist=stats["predictions"]
    gold=stats["gold"]
    counts=sorted(hist.values(),reverse=True)
    total=stats["lexical"]
    top_share={k:round(10000*sum(counts[:k])/total) for k in CUTS}
    if not (0<top_share[1]<=top_share[5]<=top_share[10]<=top_share[20]<=10000):
        raise RuntimeError("Invalid monotone prediction concentration")
    entropy=-sum((n/total)*math.log(n/total) for n in counts)
    if not math.isfinite(entropy):
        raise RuntimeError("Nonfinite empirical prediction entropy")
    result={
        "SEMANTIC_VALIDATION_COMPLETE":0,
        "TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,
        "V67_CONC_PASS":1,
        "V67_CONC_BLIND_ACCESS":0,
        "V67_CONC_GPU_BF16":1,
        "V67_CONC_GPU_PEAK_MIB":peak,
        "V67_CONC_VAL_TOKENS":stats["val_tokens"],
        "V67_CONC_VAL_LEXICAL":total,
        "V67_CONC_VAL_CE_X1000":ce,
        "V67_CONC_EOS_TOP1":stats["eos_top1"],
        "V67_CONC_PRED_DISTINCT":len(hist),
        "V67_CONC_GOLD_DISTINCT":len(gold),
        "V67_CONC_PRED_BYTE_DISTINCT":sum(3<=x<259 for x in hist),
        "V67_CONC_PRED_MERGE_DISTINCT":sum(259<=x<1024 for x in hist),
        "V67_CONC_TOP1_SHARE_BP":top_share[1],
        "V67_CONC_TOP5_SHARE_BP":top_share[5],
        "V67_CONC_TOP10_SHARE_BP":top_share[10],
        "V67_CONC_TOP20_SHARE_BP":top_share[20],
        "V67_CONC_PRED_ENTROPY_X1000":round(1000*entropy),
    }
    for family,tag in (("B","BYTE"),("M","MERGE")):
        ranks=stats["ranks"][family]
        if not all(type(x) is int and 1<=x<=T.VOCAB_SIZE for x in ranks):
            raise RuntimeError("Invalid stable true-token ranks")
        n=len(ranks)
        for k in GOLD_TOP_K:
            result[f"V67_CONC_{tag}_GOLD_TOP{k}_BP"]=round(
                10000*sum(x<=k for x in ranks)/n
            )
        result[f"V67_CONC_{tag}_GOLD_MEDIAN_RANK"]=int(statistics.median_low(ranks))
    # Guard against reporting optimistic tied-logit top-1 results.
    correct=sum(
        sum(x==1 for x in stats["ranks"][kind])
        for kind in ("B","M")
    )
    if not 0<correct<total or result["V67_CONC_TOP20_SHARE_BP"]<result["V67_CONC_TOP10_SHARE_BP"]:
        raise RuntimeError("V67 top-1 or prediction concentration inconsistent")
    if len(result)!=30 or any(type(v) is not int or v<0 or v>100_000_000
                              for v in result.values()):
        raise RuntimeError("V67 violates the immutable 30-numeric-metric GOGIT cap")
    return result


def main():
    helper=dependency_v64()
    references=validate_prerequisites(helper)
    model,device,streams,validation=helper.preflight()
    if sum(map(len,streams.values()))!=345:
        raise RuntimeError("Frozen TRAIN stream inventory changed")
    torch.cuda.reset_peak_memory_stats(device)
    stats=evaluate(model,device,validation)
    peak=math.ceil(torch.cuda.max_memory_allocated(device)/(1024**2))
    report=build_report(stats,references,peak)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for name,value in sorted(report.items()):
        print(f"{name}: {value}")


if __name__=="__main__":
    main()
