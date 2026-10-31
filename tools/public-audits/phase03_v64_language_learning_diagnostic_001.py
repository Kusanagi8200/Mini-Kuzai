#!/usr/bin/env python3
"""V64 read-only language learning diagnostic on frozen V62 cycle-2.

Measures tokenizer fragmentation and CUDA/BF16 next-token likelihood by
token type on a fixed, deliberately nonrepresentative TRAIN sample versus
all frozen VALIDATION. Publishes only numeric aggregate GOGIT metrics.
No gradient, optimizer step, BLIND TEST, or model artifact mutation.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

REPO=Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
from mini_kuzai import phase03_v62_trainer as T

RUN=Path("/root/Mini-Kuzai/runs/v62-margin-001")
CHECKPOINT=RUN/"checkpoint-cycle-02.pt"
HISTORY=REPO/"reports"/"assistant-results"/"history"
PRIOR="PHASE03-SMOLTALK-V63-AUTOMATIC-LANGUAGE-SCREEN-001"
BATCH=4
PER_STREAM=3
BYTE_BASE_START=3
BYTE_BASE_END=259


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):
        raise RuntimeError(f"Invalid JSON at {path}")
    return obj


def preflight():
    summary=read_json(RUN/"RUN-SUMMARY.json")
    manifest=read_json(RUN/"RUN-MANIFEST.json")
    if (
        summary.get("schema_version")!="v62-margin-run-summary-1"
        or manifest.get("schema_version")!="v62-margin-run-1"
        or summary.get("status")!="STOPPED"
        or manifest.get("status")!="STOPPED"
        or summary.get("stop_reason")!="MILESTONE_REVIEW_REQUIRED"
        or summary.get("optimizer_steps")!=69
        or summary.get("exposure_tokens")!=597982
        or summary.get("blind_test_accessed") is not False
        or manifest.get("blind_test_during_training") is not False
        or manifest.get("resume") is not False
        or (RUN/".training.lock").exists()
    ):
        raise RuntimeError("V62 cycle-2 stop gate failed")
    if not CHECKPOINT.is_file() or CHECKPOINT.is_symlink():
        raise RuntimeError("Frozen checkpoint missing or unsafe")

    old=read_json(HISTORY/f"{PRIOR}.json")
    m=old.get("metrics",{})
    if (
        old.get("step_id")!=PRIOR
        or old.get("semantic_validation_complete") is not False
        or m.get("V63_AUTO_PASS")!=1
        or m.get("V63_AUTO_BLIND_ACCESS")!=0
        or m.get("V63_AUTO_HUMAN_RATINGS")!=0
    ):
        raise RuntimeError("Frozen V63 nonsemantic GOGIT baseline absent")
    runtime=T.verify_runtime(
        REPO/"mini_kuzai"/"phase03_v62_trainer.py",
        REPO/"tools"/"train_v62_margin.py",
    )
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError("V64 requires CUDA BF16")
    state=torch.load(CHECKPOINT,map_location="cpu",weights_only=False)
    if (
        state.get("schema_version")!="v62-margin-checkpoint-1"
        or state.get("step")!=69
        or state.get("exposure_tokens")!=597982
        or state.get("authorization_freeze_fingerprint")!=runtime["authorization"]["freeze_fingerprint"]
        or state.get("trainer_freeze_fingerprint")!=runtime["trainer_freeze"]["trainer_freeze_fingerprint"]
    ):
        raise RuntimeError("V62 checkpoint identity or freeze mismatch")
    device=torch.device("cuda")
    model=T.MODEL.MiniKuzaiPhase03V60(T.MODEL.Phase03Config()).to(device)
    model.load_state_dict(state["model"],strict=True)
    del state
    model.eval()
    return model,device


def sample_train(streams: dict) -> list:
    # Deterministic spaced indices per stream; never mutate corpus inventory.
    if tuple(streams.keys())!=T.STREAMS:
        raise RuntimeError("Frozen TRAIN stream keys/order changed")
    selected=[]
    for name,segments in streams.items():
        if len(segments)<PER_STREAM:
            raise RuntimeError(f"Not enough frozen segments in {name}")
        indices=[0,len(segments)//2,len(segments)-1]
        if len(set(indices))!=PER_STREAM:
            raise RuntimeError("Unexpected duplicate TRAIN sampled index")
        selected.extend(segments[index] for index in indices)
    if len(selected)!=PER_STREAM*len(T.STREAMS):
        raise RuntimeError("TRAIN sample inventory invalid")
    return selected


def tally_token_statistics(segments: list, tokenizer) -> dict:
    """Byte fragmentation is a *corpus tokenization* measurement, not model CE."""
    tokens=0
    bytes_count=0
    base=0
    merges=0
    for seg in segments:
        ids=seg.token_ids
        if len(ids)<2 or ids[0]!=T.BOS_ID or ids[-1]!=T.EOS_ID:
            raise RuntimeError("Invalid frozen segment BOS/EOS")
        normal=[value for value in ids if value not in (T.BOS_ID,T.EOS_ID,T.PAD_ID)]
        tokens+=len(normal)
        base+=sum(BYTE_BASE_START<=value<BYTE_BASE_END for value in normal)
        merges+=sum(BYTE_BASE_END<=value<T.VOCAB_SIZE for value in normal)
        decoded=tokenizer.decode(ids)
        bytes_count+=len(decoded.encode("utf-8"))
    if not tokens or base+merges!=tokens or not bytes_count:
        raise RuntimeError("Invalid tokenizer metrics")
    return {
        "BYTES_PER_TOKEN_X1000":round(bytes_count*1000/tokens),
        "BASE_SHARE_BP":round(base*10000/tokens),
        "SEGMENTS":len(segments),
    }


def score(model,device,segments: list) -> dict:
    model.eval()
    total=correct=base_targets=merge_targets=terminal_top1=0
    sum_loss=base_loss=merge_loss=0.0
    with torch.inference_mode():
        for start in range(0,len(segments),BATCH):
            group=segments[start:start+BATCH]
            x=torch.full(
                (len(group),max(len(seg.token_ids) for seg in group)),
                T.PAD_ID,device=device,dtype=torch.long
            )
            for row,seg in enumerate(group):
                x[row,:len(seg.token_ids)]=torch.tensor(
                    seg.token_ids,dtype=torch.long,device=device
                )
            with torch.autocast(device_type="cuda",dtype=torch.bfloat16):
                logits=model(x).float()
            targets=x[:,1:]
            valid=targets.ne(T.PAD_ID)
            lp=logits[:,:-1,:]
            losses=F.cross_entropy(
                lp.reshape(-1,T.VOCAB_SIZE),targets.reshape(-1),
                ignore_index=T.PAD_ID,reduction="none",
            ).reshape_as(targets)
            nll=losses[valid]
            target=targets[valid]
            predicted=lp.argmax(dim=-1)[valid]
            n=target.numel()
            total+=n
            correct+=int(predicted.eq(target).sum().item())
            sum_loss+=float(nll.sum().item())
            raw_base=(target>=BYTE_BASE_START)&(target<BYTE_BASE_END)
            merged=(target>=BYTE_BASE_END)&(target<T.VOCAB_SIZE)
            base_targets+=int(raw_base.sum().item())
            merge_targets+=int(merged.sum().item())
            base_loss+=float(nll[raw_base].sum().item())
            merge_loss+=float(nll[merged].sum().item())
            # Last target is EOS; select true sequence end rather than padding.
            for row,seg in enumerate(group):
                end=len(seg.token_ids)-2
                if targets[row,end].item()!=T.EOS_ID:
                    raise RuntimeError("End target is not EOS")
                terminal_top1+=int(
                    lp[row,end].argmax().item()==T.EOS_ID
                )
    if total<=0 or base_targets==0 or merge_targets==0:
        raise RuntimeError("Insufficient byte or merged validation targets")
    return {
        "TOKENS":total,
        "CE_X1000":round(sum_loss*1000/total),
        "TOP1_BP":round(correct*10000/total),
        "BASE_TARGET_BP":round(base_targets*10000/total),
        "BYTE_NLL_X1000":round(base_loss*1000/base_targets),
        "MERGE_NLL_X1000":round(merge_loss*1000/merge_targets),
        "EOS_TOP1":terminal_top1,
    }


def result_metrics(train_t,validation_t,train,val,peak) -> dict:
    if train_t["SEGMENTS"]!=12 or validation_t["SEGMENTS"]!=36:
        raise RuntimeError("Train/validation size deviates from frozen diagnostic")
    if val["TOKENS"]!=9206:
        raise RuntimeError("VALIDATION predicted token count changed")
    gap=val["CE_X1000"]-train["CE_X1000"]
    output={
        "SEMANTIC_VALIDATION_COMPLETE":0,
        "TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,
        "V64_LANG_PASS":1,
        "V64_LANG_BLIND_ACCESS":0,
        "V64_LANG_GPU_BF16":1,
        "V64_LANG_GPU_PEAK_MIB":peak,
        "V64_LANG_VOCAB":T.VOCAB_SIZE,
        "V64_LANG_BPE_MERGES":T.VOCAB_SIZE-BYTE_BASE_END,
        "V64_LANG_TRAIN_SEGMENTS":train_t["SEGMENTS"],
        "V64_LANG_VAL_SEGMENTS":validation_t["SEGMENTS"],
        "V64_LANG_TRAIN_BYTES_PER_TOKEN_X1000":train_t["BYTES_PER_TOKEN_X1000"],
        "V64_LANG_VAL_BYTES_PER_TOKEN_X1000":validation_t["BYTES_PER_TOKEN_X1000"],
        "V64_LANG_TRAIN_BASE_SHARE_BP":train_t["BASE_SHARE_BP"],
        "V64_LANG_VAL_BASE_SHARE_BP":validation_t["BASE_SHARE_BP"],
        "V64_LANG_TRAIN_TOKENS":train["TOKENS"],
        "V64_LANG_VAL_TOKENS":val["TOKENS"],
        "V64_LANG_TRAIN_CE_X1000":train["CE_X1000"],
        "V64_LANG_VAL_CE_X1000":val["CE_X1000"],
        "V64_LANG_VAL_CE_GE_TRAIN":int(gap>=0),
        "V64_LANG_ABS_CE_GAP_X1000":abs(gap),
        "V64_LANG_TRAIN_TOP1_BP":train["TOP1_BP"],
        "V64_LANG_VAL_TOP1_BP":val["TOP1_BP"],
        "V64_LANG_TRAIN_BASE_TARGET_BP":train["BASE_TARGET_BP"],
        "V64_LANG_VAL_BASE_TARGET_BP":val["BASE_TARGET_BP"],
        "V64_LANG_TRAIN_BYTE_NLL_X1000":train["BYTE_NLL_X1000"],
        "V64_LANG_TRAIN_MERGE_NLL_X1000":train["MERGE_NLL_X1000"],
        "V64_LANG_VAL_BYTE_NLL_X1000":val["BYTE_NLL_X1000"],
        "V64_LANG_VAL_MERGE_NLL_X1000":val["MERGE_NLL_X1000"],
        "V64_LANG_VAL_EOS_TOP1":val["EOS_TOP1"],
    }
    if len(output)!=30:
        raise RuntimeError("GOGIT diagnostic metric count differs")
    if any(type(v) is not int or not 0<=v<=100_000_000 for v in output.values()):
        raise RuntimeError("Invalid V64 numeric-only diagnostic output")
    return output


def main():
    model,device=preflight()
    tokenizer=T.load_tokenizer()
    streams,train_inventory=T.build_training_streams()
    if sum(row["segments"] for row in train_inventory.values())!=345:
        raise RuntimeError("Frozen TRAIN inventory changed")
    selected=sample_train(streams)
    validation,inventory=T.build_validation_segments()
    if inventory.get("records")!=36 or inventory.get("segments")!=36:
        raise RuntimeError("Frozen VALIDATION inventory changed")
    train_t=tally_token_statistics(selected,tokenizer)
    validation_t=tally_token_statistics(validation,tokenizer)
    torch.cuda.reset_peak_memory_stats(device)
    train=score(model,device,selected)
    val=score(model,device,validation)
    # Reference EOS result must match the corrected immutable V63 audit.
    previous=read_json(HISTORY/"PHASE03-SMOLTALK-V63-DIAGNOSTIC-PREFLIGHT-002.json")
    if (
        previous.get("metrics",{}).get("V63_DIAG_TF_TERMINAL_TOP1")!=14
        or previous.get("metrics",{}).get("V63_DIAG_BLIND_ACCESS")!=0
        or val["EOS_TOP1"]!=14
    ):
        raise RuntimeError("V64 EOS disagrees with immutable V63 reference")
    peak=math.ceil(torch.cuda.max_memory_allocated(device)/(1024**2))
    output=result_metrics(train_t,validation_t,train,val,peak)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key,value in sorted(output.items()):
        print(f"{key}: {value}")


if __name__=="__main__":
    main()
