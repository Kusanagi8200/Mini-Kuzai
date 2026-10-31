#!/usr/bin/env python3
"""V69 causal probe: re-score frozen V62 logits with in-memory head-norm controls.

Three modes share exactly the same frozen VALIDATION contexts and hidden states:
BASE original BF16 tied head; HALF alpha=0.5 and FULL alpha=1.0 row-norm
equalization, with no modification to the checkpoint, module or tokenization.
Counterfactual F.linear is intentionally FP32; note precision non-equivalence.
Numerical GOGIT: exactly 30 metrics, no tokens, prompts or individual logits.
"""
from __future__ import annotations

import hashlib
import importlib.util
import math
import sys
from collections import Counter
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from mini_kuzai import phase03_v62_trainer as T

HISTORY=ROOT/"reports"/"assistant-results"/"history"
V68_STEP="PHASE03-SMOLTALK-V68-OUTPUT-HEAD-001"
V67_STEP="PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001"
V64_SOURCE=ROOT/"tools"/"public-audits"/"phase03_v64_language_learning_diagnostic_002.py"
V67_SOURCE=ROOT/"tools"/"public-audits"/"phase03_v67_output_concentration_001.py"
MODE_KEYS=("BASE","HALF","FULL")
BATCH=4
MODE_METRICS=("CE_X1000","PRED_DISTINCT","TOP1_SHARE_BP","BYTE_SHARE_BP",
              "MERGE_SHARE_BP","MERGE_TOP1_BP","MERGE_TOP5_BP","EOS_TOP1",
              "LEX_TOP1_BP")


def import_reviewed(name:str,source:Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("Frozen reviewed audit dependency unavailable")
    spec=importlib.util.spec_from_file_location(name,source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Frozen audit import failed")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def prerequisites(helper):
    v68=helper.read_json(HISTORY/f"{V68_STEP}.json")
    v67=helper.read_json(HISTORY/f"{V67_STEP}.json")
    a=v68.get("metrics",{})
    b=v67.get("metrics",{})
    if not (
        v68.get("step_id")==V68_STEP and v67.get("step_id")==V67_STEP
        and v68.get("semantic_validation_complete") is False
        and v67.get("semantic_validation_complete") is False
        and v68.get("training_authorized") is False
        and v67.get("training_authorized") is False
        and a.get("V68_HEAD_PASS")==1
        and a.get("V68_HEAD_BLIND_ACCESS")==0
        and a.get("V68_HEAD_TIED_WEIGHTS")==1
        and a.get("V68_HEAD_HAS_BIAS")==0
        and a.get("V68_HEAD_VAL_TOKENS")==9206
        and a.get("V68_HEAD_VAL_LEXICAL")==9170
        and a.get("V68_HEAD_CE_X1000")==4733
        and a.get("V68_HEAD_PRED_DISTINCT")==4
        and a.get("V68_HEAD_TOP1_SHARE_BP")==7258
        and a.get("V68_HEAD_EOS_TOP1")==14
        and b.get("V67_CONC_MERGE_GOLD_TOP1_BP")==326
        and b.get("V67_CONC_MERGE_GOLD_TOP5_BP")==685
        and b.get("V67_CONC_VAL_LEXICAL")==9170
        and all(x.get("metrics",{}).get("TRAINING_STARTED")==0 for x in (v67,v68))
    ):
        raise RuntimeError("Frozen V67/V68 verified GOGIT prerequisites invalid")
    return a,b


def equalize_rows(weights:torch.Tensor,alpha:float)->torch.Tensor:
    """Geometric interpolation to mean row norm; no in-place mutations.

    Zero-norm rows are left zero, avoiding NaNs and invented directions.
    The entire 1024-ID output vocabulary (including specials) is treated
    uniformly. This is not a change to the stored checkpoint.
    """
    if alpha not in (0.0,0.5,1.0) or weights.ndim!=2:
        raise RuntimeError("Only predetermined norm intervention allowed")
    w=weights.detach().float()
    if w.shape[0]!=T.VOCAB_SIZE or not torch.isfinite(w).all():
        raise RuntimeError("Invalid frozen tied-head projection")
    norms=torch.linalg.vector_norm(w,dim=1,keepdim=True)
    nonzero=norms>1e-9
    if not nonzero.any():
        raise RuntimeError("All frozen output-head rows are zero")
    mean=norms[nonzero].mean()
    ratio=torch.where(nonzero,mean/norms.clamp_min(1e-9),torch.ones_like(norms))
    adjusted=w*ratio.pow(alpha)
    if not torch.isfinite(adjusted).all():
        raise RuntimeError("Nonfinite normalized output weights")
    return adjusted


def empty():
    return {"tokens":0,"lexical":0,"nll":0.0,"eos":0,
            "pred":Counter(),"correct":0,"merge_targets":0,
            "merge_top1":0,"merge_top5":0}


def update_stats(stats:dict,logits:torch.Tensor,gold:torch.Tensor,valid:torch.Tensor,
                 eos_idx:list[tuple[int,int]],ranker)->None:
    if logits.ndim!=3 or logits.shape[:2]!=gold.shape or logits.shape[-1]!=T.VOCAB_SIZE:
        raise RuntimeError("Prediction shape changed")
    if not torch.isfinite(logits).all():
        raise RuntimeError("Nonfinite next-token logits")
    nll=F.cross_entropy(logits.reshape(-1,T.VOCAB_SIZE),
                        gold.reshape(-1),ignore_index=T.PAD_ID,
                        reduction="none").reshape_as(gold)
    stats["tokens"]+=int(valid.sum().item())
    stats["nll"]+=float(nll[valid].sum().item())
    best=logits.argmax(-1)
    for row,index in eos_idx:
        if int(gold[row,index].item())!=T.EOS_ID:
            raise RuntimeError("Frozen terminal EOS boundary changed")
        stats["eos"]+=int(best[row,index].item()==T.EOS_ID)
    mask=valid & gold.ge(3) & gold.lt(T.VOCAB_SIZE)
    true=gold[mask]
    pred=best[mask]
    if not true.numel():
        return
    ranks=ranker(logits[mask],true)
    if not torch.equal(ranks.eq(1),pred.eq(true)):
        raise RuntimeError("Stable true-token ranking inconsistent with argmax")
    stats["lexical"]+=int(true.numel())
    stats["pred"].update(pred.detach().cpu().tolist())
    stats["correct"]+=int(ranks.eq(1).sum().item())
    merged=true.ge(259)
    stats["merge_targets"]+=int(merged.sum().item())
    stats["merge_top1"]+=int(ranks[merged].le(1).sum().item())
    stats["merge_top5"]+=int(ranks[merged].le(5).sum().item())


def finalize(stats:dict):
    if (
        stats["tokens"]!=9206 or stats["lexical"]!=9170
        or stats["merge_targets"]!=4294
        or sum(stats["pred"].values())!=9170
        or not 0<=stats["eos"]<=36
    ):
        raise RuntimeError("Frozen VALIDATION coverage drifted")
    counts=stats["pred"]
    top_share=round(max(counts.values())*10000/9170)
    raw=sum(count for token,count in counts.items() if 3<=token<259)
    merged=sum(count for token,count in counts.items() if token>=259)
    return {
        "CE_X1000":round(stats["nll"]*1000/9206),
        "PRED_DISTINCT":len(counts),
        "TOP1_SHARE_BP":top_share,
        "BYTE_SHARE_BP":round(raw*10000/9170),
        "MERGE_SHARE_BP":round(merged*10000/9170),
        "MERGE_TOP1_BP":round(stats["merge_top1"]*10000/4294),
        "MERGE_TOP5_BP":round(stats["merge_top5"]*10000/4294),
        "EOS_TOP1":stats["eos"],
        "LEX_TOP1_BP":round(stats["correct"]*10000/9170),
    }


def evaluate(model,device,validation,ranker):
    if len(validation)!=36 or model.lm_head.bias is not None or (
        model.lm_head.weight.data_ptr()!=model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("Frozen VALIDATION or tied-head model identity invalid")
    weights=model.lm_head.weight.detach().float()
    weights_before=weights.clone()
    # Compute counterfactual matrices once; do not replace lm_head.weight.
    controls={
        "HALF":equalize_rows(weights,0.5).to(device=device),
        "FULL":equalize_rows(weights,1.0).to(device=device),
    }
    scores={key:empty() for key in MODE_KEYS}
    hidden=[]
    def tap(_module,inputs):
        if len(inputs)!=1 or inputs[0].ndim!=3:
            raise RuntimeError("Frozen LM-head input shape invalid")
        hidden.append(inputs[0].detach())
    handle=model.lm_head.register_forward_pre_hook(tap)
    try:
        model.eval()
        with torch.inference_mode():
            for offset in range(0,len(validation),BATCH):
                chunk=validation[offset:offset+BATCH]
                ids=torch.full(
                    (len(chunk),max(len(s.token_ids) for s in chunk)),
                    T.PAD_ID,dtype=torch.long,device=device,
                )
                eos_positions=[]
                for row,seg in enumerate(chunk):
                    if seg.token_ids[0]!=T.BOS_ID or seg.token_ids[-1]!=T.EOS_ID:
                        raise RuntimeError("Frozen VALIDATION boundary changed")
                    ids[row,:len(seg.token_ids)]=torch.as_tensor(
                        seg.token_ids,dtype=torch.long,device=device
                    )
                    eos_positions.append((row,len(seg.token_ids)-2))
                with torch.autocast(device_type="cuda",dtype=torch.bfloat16):
                    base=model(ids).float()[:,:-1,:]
                if len(hidden)!=1 or hidden[0].shape[:2]!=ids.shape:
                    raise RuntimeError("LM-head output tap failed")
                captured=hidden.pop().float()[:,:-1,:]
                gold=ids[:,1:]
                valid=gold.ne(T.PAD_ID)
                update_stats(scores["BASE"],base,gold,valid,eos_positions,ranker)
                with torch.autocast(device_type="cuda",enabled=False):
                    for mode in ("HALF","FULL"):
                        test_logits=F.linear(captured,controls[mode])
                        update_stats(scores[mode],test_logits,gold,valid,eos_positions,ranker)
                del base,captured
    finally:
        handle.remove()
        hidden.clear()
    if not torch.equal(model.lm_head.weight.detach().float(),weights_before):
        raise RuntimeError("Frozen checkpoint weights were modified during inference")
    return {key:finalize(stats) for key,stats in scores.items()}


def numeric_report(variants,reference):
    if set(variants)!=set(MODE_KEYS):
        raise RuntimeError("Incomplete original and counterfactual evaluation")
    base=variants["BASE"]
    a,b=reference
    if not (
        base["CE_X1000"]==a["V68_HEAD_CE_X1000"]==4733
        and base["PRED_DISTINCT"]==a["V68_HEAD_PRED_DISTINCT"]==4
        and base["TOP1_SHARE_BP"]==a["V68_HEAD_TOP1_SHARE_BP"]==7258
        and base["MERGE_TOP1_BP"]==b["V67_CONC_MERGE_GOLD_TOP1_BP"]==326
        and base["MERGE_TOP5_BP"]==b["V67_CONC_MERGE_GOLD_TOP5_BP"]==685
        and base["EOS_TOP1"]==a["V68_HEAD_EOS_TOP1"]==14
        and base["BYTE_SHARE_BP"]==round(6692*10000/9170)
        and base["MERGE_SHARE_BP"]==round(2428*10000/9170)
    ):
        raise RuntimeError("V69 original logits did not reproduce V67/V68")
    report={
        "SEMANTIC_VALIDATION_COMPLETE":0,"TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,"V69_NORM_PASS":1,
        "V69_NORM_BLIND_ACCESS":0,"V69_NORM_GPU_BF16":1,
        "V69_NORM_VAL_LEXICAL":9170,
        "V69_NORM_BASE_CE_X1000":base["CE_X1000"],
        "V69_NORM_BASE_PRED_DISTINCT":base["PRED_DISTINCT"],
        "V69_NORM_BASE_TOP1_SHARE_BP":base["TOP1_SHARE_BP"],
        "V69_NORM_BASE_MERGE_TOP1_BP":base["MERGE_TOP1_BP"],
        "V69_NORM_BASE_MERGE_TOP5_BP":base["MERGE_TOP5_BP"],
    }
    for mode in ("HALF","FULL"):
        for key in MODE_METRICS:
            report[f"V69_NORM_{mode}_{key}"]=variants[mode][key]
    if not (len(report)==30 and all(type(v) is int and 0<=v<=100_000_000 for v in report.values())):
        raise RuntimeError("V69 must use exactly 30 numeric allowlisted GOGIT fields")
    return report


def main():
    helper=import_reviewed("v69_v64_verified",V64_SOURCE)
    ranks=import_reviewed("v69_v67_stable_rank",V67_SOURCE)
    ref=prerequisites(helper)
    model,device,train,validation=helper.preflight()
    if sum(map(len,train.values()))!=345:
        raise RuntimeError("Frozen TRAIN inventory changed")
    torch.cuda.reset_peak_memory_stats(device)
    variants=evaluate(model,device,validation,ranks.stable_true_ranks)
    report=numeric_report(variants,ref)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key,value in sorted(report.items()):
        print(f"{key}: {value}")


if __name__=="__main__":
    main()
