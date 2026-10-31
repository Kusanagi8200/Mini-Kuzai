#!/usr/bin/env python3
"""V68 frozen output-head norm and logit-dominance audit (read-only).

Unmodified V62 cycle-2 checkpoint, full frozen VALIDATION, tied head probes,
no gradients, no BLIND and exactly 30 numeric metrics via GOGIT.
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

HELPER=REPO/"tools"/"public-audits"/"phase03_v64_language_learning_diagnostic_002.py"
HISTORY=REPO/"reports"/"assistant-results"/"history"
PRIOR="PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001"
BATCH=4


def frozen_helper():
    if not HELPER.is_file() or HELPER.is_symlink():
        raise RuntimeError("Frozen V64-002 helper missing")
    spec=importlib.util.spec_from_file_location("v68_helper",HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Frozen V64 helper import failed")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def summarize_head(model):
    head=model.lm_head
    embed=model.token_embedding
    if head.bias is not None or head.weight.data_ptr()!=embed.weight.data_ptr():
        raise RuntimeError("V60 tied output projection or no-bias rule violated")
    norms=head.weight.detach().float().norm(dim=-1)
    if norms.numel()!=T.VOCAB_SIZE or not torch.isfinite(norms).all():
        raise RuntimeError("Frozen output-head row norms invalid")
    # PAD is excluded as an input embedding gradient by padding_idx, but
    # output and input weights are tied: the output softmax can train this row.
    # Finite/nonnegative row norms are enforced above; zero is not required.
    return norms


def summarize_numeric(stats,norms,peak,prior):
    if not (
        stats["tokens"]==9206 and stats["lexical"]==9170
        and stats["eos"]==14 and len(stats["pred"])==4
    ):
        raise RuntimeError("V68 inventory/rank baseline mismatch")
    if not all(math.isfinite(x) and x>=0 for x in (
        *stats["gap"],*stats["gold_deficit"],*stats["byte_deficit"],
        *stats["merge_deficit"],*stats["pred_norm"],*stats["gold_norm"],
    )):
        raise RuntimeError("Nonfinite or negative V68 numeric measurement")
    m=prior.get("metrics",{})
    counts=stats["pred"]
    byte=sum(n for k,n in counts.items() if 3<=k<259)
    merged=sum(n for k,n in counts.items() if k>=259)
    special=sum(n for k,n in counts.items() if k<3)
    if (
        byte!=6692 or merged!=2428 or special!=50
        or m.get("V67_CONC_PRED_DISTINCT")!=4
        or m.get("V67_CONC_VAL_LEXICAL")!=9170
    ):
        raise RuntimeError("V68 argmax distribution differs from V66/V67")
    concentration=round(max(counts.values())*10000/9170)
    if concentration!=m.get("V67_CONC_TOP1_SHARE_BP"):
        raise RuntimeError("V68 concentration differs from V67")
    ce=round(stats["nll_sum"]*1000/stats["tokens"])
    if ce!=m.get("V67_CONC_VAL_CE_X1000") or ce!=4733:
        raise RuntimeError("V68 cross-entropy changed")
    q90=sorted(stats["gap"])[int(math.ceil(.90*len(stats["gap"])))-1]
    result={
        "SEMANTIC_VALIDATION_COMPLETE":0,
        "TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,
        "V68_HEAD_PASS":1,
        "V68_HEAD_BLIND_ACCESS":0,
        "V68_HEAD_GPU_BF16":1,
        "V68_HEAD_TIED_WEIGHTS":1,
        "V68_HEAD_HAS_BIAS":0,
        "V68_HEAD_VAL_TOKENS":stats["tokens"],
        "V68_HEAD_VAL_LEXICAL":stats["lexical"],
        "V68_HEAD_CE_X1000":ce,
        "V68_HEAD_EOS_TOP1":stats["eos"],
        "V68_HEAD_NORM_BYTE_MEAN_X1000":round(norms[3:259].mean().item()*1000),
        "V68_HEAD_NORM_MERGE_MEAN_X1000":round(norms[259:].mean().item()*1000),
        "V68_HEAD_NORM_PAD_X1000":round(norms[T.PAD_ID].item()*1000),
        "V68_HEAD_NORM_MAX_X1000":round(norms.max().item()*1000),
        "V68_HEAD_NORM_STD_X1000":round(norms.std(unbiased=False).item()*1000),
        "V68_HEAD_PRED_DISTINCT":len(counts),
        "V68_HEAD_PRED_BYTE_COUNT":byte,
        "V68_HEAD_PRED_MERGE_COUNT":merged,
        "V68_HEAD_PRED_SPECIAL_COUNT":special,
        "V68_HEAD_TOP1_SHARE_BP":concentration,
        "V68_HEAD_LOGIT_GAP_MEAN_X1000":round(sum(stats["gap"])*1000/9170),
        "V68_HEAD_LOGIT_GAP_P90_X1000":round(q90*1000),
        "V68_HEAD_GOLD_DEFICIT_MEAN_X1000":round(sum(stats["gold_deficit"])*1000/9170),
        "V68_HEAD_GOLD_BYTE_DEFICIT_X1000":round(sum(stats["byte_deficit"])*1000/4876),
        "V68_HEAD_GOLD_MERGE_DEFICIT_X1000":round(sum(stats["merge_deficit"])*1000/4294),
        "V68_HEAD_PRED_NORM_MEAN_X1000":round(sum(stats["pred_norm"])*1000/9170),
        "V68_HEAD_GOLD_NORM_MEAN_X1000":round(sum(stats["gold_norm"])*1000/9170),
        "V68_HEAD_GPU_PEAK_MIB":peak,
    }
    if len(result)!=30 or any(type(v) is not int or not 0<=v<=100_000_000 for v in result.values()):
        raise RuntimeError("V68 must publish exactly 30 bounded integer metrics")
    return result


def evaluate(model,device,validation,norms):
    if len(validation)!=36:
        raise RuntimeError("Expected 36 frozen VALIDATION segments")
    stats={
        "tokens":0,"lexical":0,"eos":0,"nll_sum":0.0,
        "pred":Counter(),"gap":[],"gold_deficit":[],
        "byte_deficit":[],"merge_deficit":[],
        "pred_norm":[],"gold_norm":[],
    }
    gpu_norms=norms.to(device=device)
    model.eval()
    with torch.inference_mode():
        for offset in range(0,len(validation),BATCH):
            segs=validation[offset:offset+BATCH]
            ids=torch.full((len(segs),max(len(s.token_ids) for s in segs)),
                           T.PAD_ID,dtype=torch.long,device=device)
            for row,seg in enumerate(segs):
                if seg.token_ids[0]!=T.BOS_ID or seg.token_ids[-1]!=T.EOS_ID:
                    raise RuntimeError("Frozen VALIDATION segment boundary changed")
                ids[row,:len(seg.token_ids)]=torch.as_tensor(seg.token_ids,dtype=torch.long,device=device)
            with torch.autocast(device_type="cuda",dtype=torch.bfloat16):
                logits=model(ids).float()[:,:-1,:]
            gold=ids[:,1:]
            valid=gold.ne(T.PAD_ID)
            losses=F.cross_entropy(logits.reshape(-1,T.VOCAB_SIZE),
                                   gold.reshape(-1),
                                   ignore_index=T.PAD_ID,reduction="none").reshape_as(gold)
            stats["tokens"]+=int(valid.sum().item())
            stats["nll_sum"]+=float(losses[valid].sum().item())
            top1=logits.argmax(-1)
            for row,seg in enumerate(segs):
                index=len(seg.token_ids)-2
                if int(gold[row,index].item())!=T.EOS_ID:
                    raise RuntimeError("Frozen EOS target mismatch")
                stats["eos"]+=int(int(top1[row,index].item())==T.EOS_ID)
            lexical=valid&gold.ge(3)&gold.lt(T.VOCAB_SIZE)
            if not lexical.any():
                continue
            true=gold[lexical]
            selected=logits[lexical]
            top=selected.topk(2,dim=-1)
            # V67 uses argmax first-ID tie breaking. torch.topk indices
            # are not required to use that same deterministic tie rule.
            pred=selected.argmax(dim=-1)
            gap=(top.values[:,0]-top.values[:,1]).clamp_min(0)
            gold_logit=selected.gather(1,true.unsqueeze(1)).squeeze(1)
            deficit=(top.values[:,0]-gold_logit).clamp_min(0)
            stats["lexical"]+=int(true.numel())
            stats["pred"].update(pred.cpu().tolist())
            stats["gap"].extend(gap.cpu().tolist())
            stats["gold_deficit"].extend(deficit.cpu().tolist())
            stats["byte_deficit"].extend(deficit[true.lt(259)].cpu().tolist())
            stats["merge_deficit"].extend(deficit[true.ge(259)].cpu().tolist())
            stats["pred_norm"].extend(gpu_norms[pred].cpu().tolist())
            stats["gold_norm"].extend(gpu_norms[true].cpu().tolist())
    if not (
        stats["tokens"]==9206 and stats["lexical"]==9170
        and len(stats["byte_deficit"])==4876
        and len(stats["merge_deficit"])==4294
    ):
        raise RuntimeError("V68 observed token inventory disagrees with V67")
    return stats


def main():
    helper=frozen_helper()
    prior=helper.read_json(HISTORY/f"{PRIOR}.json")
    metrics=prior.get("metrics",{})
    if not (
        prior.get("step_id")==PRIOR
        and prior.get("semantic_validation_complete") is False
        and prior.get("training_authorized") is False
        and metrics.get("V67_CONC_PASS")==1
        and metrics.get("V67_CONC_BLIND_ACCESS")==0
        and metrics.get("V67_CONC_PRED_DISTINCT")==4
        and metrics.get("V67_CONC_EOS_TOP1")==14
    ):
        raise RuntimeError("Frozen V67 prerequisite invalid")
    model,device,streams,validation=helper.preflight()
    if sum(map(len,streams.values()))!=345:
        raise RuntimeError("Frozen TRAIN inventory changed")
    norms=summarize_head(model)
    torch.cuda.reset_peak_memory_stats(device)
    stats=evaluate(model,device,validation,norms)
    peak=math.ceil(torch.cuda.max_memory_allocated(device)/(1024**2))
    result=summarize_numeric(stats,norms,peak,prior)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for k,v in sorted(result.items()):
        print(f"{k}: {v}")


if __name__=="__main__":
    main()
