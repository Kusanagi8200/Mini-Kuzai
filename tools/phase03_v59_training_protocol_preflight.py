#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

REPO=Path(__file__).resolve().parents[1]
EXPOSURE=REPO/"reviews"/"smoltalk-v59-persona-exposure-policy"/"REPORT-001.json"
ARCH=REPO/"data"/"phase-03"/"config"/"architecture-v58-final.json"
MODEL_PATH=REPO/"mini_kuzai"/"phase03_model.py"
OUT=REPO/"reviews"/"smoltalk-v59-training-protocol"

PARAMETERS=1184512
REFERENCE_CYCLES=4
TOKENS_PER_OPTIMIZER_STEP=8192
MICROBATCH_SEQUENCES=8
BASE_LR=3e-4
MIN_LR=3e-5
WEIGHT_DECAY=0.10
BETA1=0.9
BETA2=0.95
EPS=1e-8
GRAD_CLIP=1.0
SEED=42
MEMORY_GATE_BP=6000

def load_module(name,path):
    import importlib.util
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load model module")
    m=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=m
    spec.loader.exec_module(m)
    return m

MODEL=load_module("phase03_model_v59_training_protocol",MODEL_PATH)

def read_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe input: {path}")
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value

def protocol():
    exposure=read_json(EXPOSURE)
    arch=read_json(ARCH)
    if exposure.get("status")!="EXPOSURE_POLICY_DEFINED_NOT_TRAINING_AUTHORIZED":
        raise RuntimeError("Exposure policy state changed")
    if exposure.get("mix_weighting_finalized") is not True:
        raise RuntimeError("Exposure policy is not finalized")
    if exposure.get("training_authorized") is not False:
        raise RuntimeError("Unexpected exposure training authorization")
    if exposure.get("repair_queue_admitted") or exposure.get("unreviewed_admitted") or exposure.get("exclude_admitted"):
        raise RuntimeError("Unsafe exposure policy")
    if arch.get("status")!="FROZEN" or arch.get("parameters")!=PARAMETERS:
        raise RuntimeError("V58 architecture baseline changed")
    if arch.get("context_length")!=2048 or arch.get("vocab_size")!=1024:
        raise RuntimeError("V58 architecture dimensions changed")

    reference_tokens=int(exposure["reference_cycle_tokens"])
    if reference_tokens!=295416:
        raise RuntimeError("Reference exposure cycle changed")

    total_tokens=reference_tokens*REFERENCE_CYCLES
    max_steps=math.ceil(total_tokens/TOKENS_PER_OPTIMIZER_STEP)
    warmup_steps=max(5,math.ceil(max_steps*0.10))
    eval_every_tokens=math.ceil(reference_tokens/2)
    checkpoint_every_tokens=eval_every_tokens

    return {
      "schema_version":"v59-training-protocol-pilot-1",
      "status":"PROTOCOL_DEFINED_PREFLIGHT_REQUIRED",
      "architecture":"V58_MICRO_FROZEN",
      "parameters":PARAMETERS,
      "context_length":2048,
      "dtype":"BF16",
      "seed":SEED,
      "optimizer":{
        "name":"AdamW",
        "learning_rate":BASE_LR,
        "betas":[BETA1,BETA2],
        "eps":EPS,
        "weight_decay":WEIGHT_DECAY},
      "scheduler":{
        "name":"linear_warmup_cosine_decay",
        "warmup_steps":warmup_steps,
        "max_steps":max_steps,
        "min_learning_rate":MIN_LR},
      "batching":{
        "microbatch_sequences":MICROBATCH_SEQUENCES,
        "optimizer_step_target_nonpad_tokens":TOKENS_PER_OPTIMIZER_STEP,
        "gradient_accumulation":"DYNAMIC_UNTIL_TOKEN_TARGET",
        "right_padding":True,
        "pad_token_id":0,
        "loss_ignore_pad":True,
        "next_token_shift":True},
      "gradient_clip_norm":GRAD_CLIP,
      "exposure":{
        "reference_cycles":REFERENCE_CYCLES,
        "reference_cycle_tokens":reference_tokens,
        "max_exposure_tokens":total_tokens,
        "max_optimizer_steps":max_steps,
        "effective_exposure_tokens_per_parameter":total_tokens/PARAMETERS,
        "unique_clean_tokens":int(exposure["unique_ready_tokens"]),
        "unique_tokens_per_parameter":int(exposure["unique_ready_tokens"])/PARAMETERS,
        "target_share_bp":exposure["target_share_bp"],
        "stream_quota_mode":"TOKEN_QUOTA_WITH_REPLACEMENT",
        "quota_overshoot_rule":"LAST_SEGMENT_MAY_OVERSHOOT_STREAM_QUOTA",
        "stream_share_tolerance_bp":100},
      "evaluation":{
        "validation_split":"FROZEN_VALIDATION_36",
        "validation_every_exposure_tokens":eval_every_tokens,
        "blind_test_during_training":False,
        "teacher_forced_validation_loss":True,
        "generation_probe":"FIXED_VALIDATION_PROMPTS",
        "early_stop":{
          "nonfinite_loss":True,
          "nonfinite_gradient_norm":True,
          "relative_validation_loss_degradation_bp":500,
          "consecutive_degraded_evals":2,
          "minimum_completed_evals":3}},
      "checkpointing":{
        "every_exposure_tokens":checkpoint_every_tokens,
        "save_best_validation":True,
        "save_last":True,
        "include_optimizer":True,
        "include_scheduler":True,
        "include_rng_state":True,
        "include_sampler_state":True},
      "hardware_preflight":{
        "full_context_microbatch_sequences":MICROBATCH_SEQUENCES,
        "memory_gate_bp":MEMORY_GATE_BP,
        "require_cuda":True,
        "require_bf16":True},
      "torch_compile":False,
      "blind_test_reserved":True,
      "pilot_only":True,
      "authorization_candidate":False,
      "training_authorized":False,
      "training_started":False}

def hardware_preflight(p):
    if not torch.cuda.is_available():
        return {"passed":False,"reason":"CUDA_UNAVAILABLE"}

    if not torch.cuda.is_bf16_supported():
        return {"passed":False,"reason":"BF16_UNAVAILABLE"}

    device=torch.device("cuda")
    config=MODEL.Phase03Config()
    model=MODEL.MiniKuzaiPhase03(config).to(device)
    if MODEL.count_parameters(model)!=PARAMETERS:
        raise RuntimeError("Model parameter count changed")

    optimizer=torch.optim.AdamW(
        model.parameters(),
        lr=BASE_LR,
        betas=(BETA1,BETA2),
        eps=EPS,
        weight_decay=WEIGHT_DECAY)

    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    token_ids=torch.randint(
        3,1024,(MICROBATCH_SEQUENCES,2048),device=device,dtype=torch.long)

    optimizer.zero_grad(set_to_none=True)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    with torch.autocast(device_type="cuda",dtype=torch.bfloat16):
        logits=model(token_ids)
        targets=token_ids[:,1:]
        loss=F.cross_entropy(
            logits[:,:-1,:].reshape(-1,1024),
            targets.reshape(-1))

    finite_loss=bool(torch.isfinite(loss).item())
    if finite_loss:
        loss.backward()
        grad_norm=torch.nn.utils.clip_grad_norm_(model.parameters(),GRAD_CLIP)
        finite_grad=bool(torch.isfinite(torch.as_tensor(grad_norm)).item())
        if finite_grad:
            optimizer.step()
    else:
        grad_norm=torch.tensor(float("nan"),device=device)
        finite_grad=False

    torch.cuda.synchronize()
    allocated=int(torch.cuda.max_memory_allocated())
    reserved=int(torch.cuda.max_memory_reserved())
    total=int(torch.cuda.get_device_properties(0).total_memory)
    reserved_bp=round(reserved*10000/total) if total else 10000
    passed=finite_loss and finite_grad and reserved_bp<=MEMORY_GATE_BP

    return {
      "passed":passed,
      "device_name":torch.cuda.get_device_name(0),
      "bf16":True,
      "microbatch_sequences":MICROBATCH_SEQUENCES,
      "context_length":2048,
      "loss_finite":finite_loss,
      "gradient_norm_finite":finite_grad,
      "preclip_gradient_norm":float(grad_norm.detach().cpu()) if finite_grad else None,
      "peak_allocated_mib":allocated//(1024*1024),
      "peak_reserved_mib":reserved//(1024*1024),
      "total_memory_mib":total//(1024*1024),
      "peak_reserved_bp":reserved_bp,
      "memory_gate_bp":MEMORY_GATE_BP}

def write(protocol_value,preflight):
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("training protocol output already exists")
    OUT.mkdir(parents=True)

    static_gates={
      "architecture_frozen":True,
      "exposure_policy_finalized":True,
      "unsafe_public_buckets_excluded":True,
      "validation_frozen":True,
      "blind_reserved":True,
      "protocol_bounded":True,
      "hardware_preflight_passed":bool(preflight.get("passed"))}
    candidate=all(static_gates.values())

    protocol_value["authorization_candidate"]=candidate
    report={
      "schema_version":"v59-training-protocol-preflight-1",
      "status":"PREFLIGHT_PASSED_AUTHORIZATION_REVIEW_REQUIRED" if candidate else "PREFLIGHT_FAILED",
      "protocol":protocol_value,
      "hardware_preflight":preflight,
      "authorization_gates":static_gates,
      "authorization_candidate":candidate,
      "training_authorized":False,
      "training_started":False}

    (OUT/"PROTOCOL-001.json").write_text(
        json.dumps(protocol_value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (OUT/"REPORT-001.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=["# Mini-Kuzai V59 - training hyperparameters / step budget / authorization gate","",
      f"Status --> **{report['status']}**","",
      "## Pilot protocol","",
      f"- architecture --> V58 MICRO / {PARAMETERS} parameters",
      "- dtype --> BF16",
      "- optimizer --> AdamW",
      f"- learning rate --> {BASE_LR}",
      f"- minimum learning rate --> {MIN_LR}",
      f"- betas --> {BETA1} / {BETA2}",
      f"- weight decay --> {WEIGHT_DECAY}",
      f"- gradient clip --> {GRAD_CLIP}",
      f"- microbatch --> {MICROBATCH_SEQUENCES} sequences",
      f"- optimizer-step target --> {TOKENS_PER_OPTIMIZER_STEP} non-pad tokens",
      "- accumulation --> dynamic until token target",
      f"- pilot exposure cycles --> {REFERENCE_CYCLES}",
      f"- max exposure tokens --> {protocol_value['exposure']['max_exposure_tokens']}",
      f"- max optimizer steps --> {protocol_value['exposure']['max_optimizer_steps']}",
      f"- exposure tokens / parameter --> {protocol_value['exposure']['effective_exposure_tokens_per_parameter']:.3f}",
      f"- unique tokens / parameter --> {protocol_value['exposure']['unique_tokens_per_parameter']:.3f}","",
      "## Evaluation / stopping","",
      "- frozen VALIDATION --> used during pilot",
      "- frozen BLIND TEST --> not accessed during pilot",
      "- validation --> every half reference exposure cycle",
      "- checkpoint --> every half reference exposure cycle",
      "- stop on non-finite loss or gradient norm",
      "- stop after two consecutive validation-loss degradations >=5% after at least three evaluations","",
      "## Hardware preflight","",
      f"- passed --> {'YES' if preflight.get('passed') else 'NO'}",
      f"- device --> {preflight.get('device_name','N/A')}",
      f"- peak reserved MiB --> {preflight.get('peak_reserved_mib','N/A')}",
      f"- total GPU MiB --> {preflight.get('total_memory_mib','N/A')}",
      f"- reserved share --> {preflight.get('peak_reserved_bp',0)/100:.2f}%",
      f"- memory gate --> {MEMORY_GATE_BP/100:.2f}%","",
      f"Authorization candidate --> **{'YES' if candidate else 'NO'}**",
      "Training authorized --> **NO**",
      "Training started --> **NO**","",
      "A separate explicit authorization step is required before any persistent model training.","",
      "---","","##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**",""]
    (OUT/"RESULTS-001.md").write_text("\n".join(lines),encoding="utf-8")
    return report

def metrics(r):
    p=r["protocol"]; h=r["hardware_preflight"]
    return {
      "V59_TRAIN_PROTOCOL_PILOT_CYCLES":p["exposure"]["reference_cycles"],
      "V59_TRAIN_PROTOCOL_MAX_TOKENS":p["exposure"]["max_exposure_tokens"],
      "V59_TRAIN_PROTOCOL_MAX_STEPS":p["exposure"]["max_optimizer_steps"],
      "V59_TRAIN_PROTOCOL_STEP_TOKENS":p["batching"]["optimizer_step_target_nonpad_tokens"],
      "V59_TRAIN_PROTOCOL_MICROBATCH":p["batching"]["microbatch_sequences"],
      "V59_TRAIN_PROTOCOL_LR_X1E9":int(round(p["optimizer"]["learning_rate"]*1e9)),
      "V59_TRAIN_PROTOCOL_MIN_LR_X1E9":int(round(p["scheduler"]["min_learning_rate"]*1e9)),
      "V59_TRAIN_PROTOCOL_WARMUP_STEPS":p["scheduler"]["warmup_steps"],
      "V59_TRAIN_PROTOCOL_EXPOSURE_TPP_X1000":int(round(p["exposure"]["effective_exposure_tokens_per_parameter"]*1000)),
      "V59_TRAIN_PREFLIGHT_PASS":int(bool(h.get("passed"))),
      "V59_TRAIN_PREFLIGHT_PEAK_RESERVED_MIB":int(h.get("peak_reserved_mib",0) or 0),
      "V59_TRAIN_PREFLIGHT_RESERVED_BP":int(h.get("peak_reserved_bp",0) or 0),
      "V59_TRAIN_AUTHORIZATION_CANDIDATE":int(bool(r["authorization_candidate"])),
      "V59_MIX_FINALIZED":0,
      "TRAINING_AUTHORIZED":0}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--write",action="store_true")
    ap.add_argument("--from-report",action="store_true")
    args=ap.parse_args()

    if args.from_report:
        r=read_json(OUT/"REPORT-001.json")
    else:
        p=protocol()
        h=hardware_preflight(p)
        r={"protocol":p,"hardware_preflight":h,"authorization_candidate":False}
        if args.write:
            r=write(p,h)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for k,v in sorted(metrics(r).items()):
        print(f"{k}: {v}")

if __name__=="__main__":
    main()
