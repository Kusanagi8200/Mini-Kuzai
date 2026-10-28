#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
BASE=REPO/"reviews"/"smoltalk-v59-final-mix-policy"
BASE_REPORT=BASE/"REPORT-001.json"
DIRECT=BASE/"direct-keep-001.json"
OUT=REPO/"reviews"/"smoltalk-v59-persona-exposure-policy"

STREAMS=("CONTROLLED_TRAIN","PERSONA_CORE","GENERAL_SUPPORT","LEGACY_STRUCTURED_KEEP")
PARAMETERS=1184512

def bp_from_share(value):
    return int(round(value*10000))

def load_inputs():
    report=json.loads(BASE_REPORT.read_text(encoding="utf-8"))
    direct=json.loads(DIRECT.read_text(encoding="utf-8"))
    if report.get("status")!="POLICY_DEFINED_NOT_FINALIZED":
        raise RuntimeError("final-mix policy state changed")
    if report.get("training_authorized") is not False:
        raise RuntimeError("unexpected training authorization")
    if direct.get("bucket")!="DIRECT_KEEP" or direct.get("count")!=165:
        raise RuntimeError("DIRECT_KEEP manifest changed")
    items=direct.get("items")
    if not isinstance(items,list) or len(items)!=165:
        raise RuntimeError("DIRECT_KEEP items changed")
    return report,items

def derive():
    report,items=load_inputs()
    by=defaultdict(lambda:{"conversations":0,"segments":0,"tokens":0})
    by["CONTROLLED_TRAIN"]={"conversations":107,"segments":107,"tokens":int(report["controlled_train_tokens"])}

    tier_map={
      "PERSONA_CORE":"PERSONA_CORE",
      "GENERAL_SUPPORT":"GENERAL_SUPPORT",
      "LEGACY_STRUCTURED_KEEP":"LEGACY_STRUCTURED_KEEP"}
    seen=set()
    for item in items:
        sha=item["sha"]
        if sha in seen: raise RuntimeError("duplicate DIRECT_KEEP source")
        seen.add(sha)
        tier=item["persona_tier"]
        if tier not in tier_map: raise RuntimeError("unexpected DIRECT_KEEP persona tier")
        stream=tier_map[tier]
        by[stream]["conversations"]+=1
        by[stream]["segments"]+=int(item["segments"])
        by[stream]["tokens"]+=int(item["tokens"])

    if by["PERSONA_CORE"]["conversations"]!=86: raise RuntimeError("PERSONA_CORE count changed")
    if by["GENERAL_SUPPORT"]["conversations"]!=68: raise RuntimeError("GENERAL_SUPPORT count changed")
    if by["LEGACY_STRUCTURED_KEEP"]["conversations"]!=11: raise RuntimeError("LEGACY count changed")

    unique_total=sum(by[s]["tokens"] for s in STREAMS)
    if unique_total!=int(report["ready_now_combined_tokens"]) or unique_total!=295416:
        raise RuntimeError("ready-now token accounting changed")

    raw_bp={s:bp_from_share(by[s]["tokens"]/unique_total) for s in STREAMS}

    # Persona-first constraints:
    # CONTROLLED >= 30%
    # GENERAL_SUPPORT <= 15%
    # LEGACY <= 10%
    # CONTROLLED + PERSONA_CORE >= 75%
    controlled_bp=max(raw_bp["CONTROLLED_TRAIN"],3000)
    general_bp=min(raw_bp["GENERAL_SUPPORT"],1500)
    legacy_bp=min(raw_bp["LEGACY_STRUCTURED_KEEP"],1000)
    persona_bp=10000-controlled_bp-general_bp-legacy_bp

    if persona_bp<=0:
        raise RuntimeError("invalid derived persona share")
    target_bp={
      "CONTROLLED_TRAIN":controlled_bp,
      "PERSONA_CORE":persona_bp,
      "GENERAL_SUPPORT":general_bp,
      "LEGACY_STRUCTURED_KEEP":legacy_bp}

    if target_bp["CONTROLLED_TRAIN"]<3000: raise RuntimeError("controlled floor failed")
    if target_bp["GENERAL_SUPPORT"]>1500: raise RuntimeError("general cap failed")
    if target_bp["LEGACY_STRUCTURED_KEEP"]>1000: raise RuntimeError("legacy cap failed")
    if target_bp["CONTROLLED_TRAIN"]+target_bp["PERSONA_CORE"]<7500:
        raise RuntimeError("persona-oriented floor failed")
    if sum(target_bp.values())!=10000: raise RuntimeError("target-share closure failed")

    # Target tokens in a reference exposure cycle equal in size to the complete
    # ready-now unique corpus. Rounding is closed deterministically on PERSONA_CORE.
    target_tokens={}
    allocated=0
    for stream in ("CONTROLLED_TRAIN","GENERAL_SUPPORT","LEGACY_STRUCTURED_KEEP"):
        t=(unique_total*target_bp[stream])//10000
        target_tokens[stream]=t; allocated+=t
    target_tokens["PERSONA_CORE"]=unique_total-allocated

    streams={}
    for s in STREAMS:
        raw=by[s]["tokens"]
        target=target_tokens[s]
        streams[s]={
          **by[s],
          "raw_share_bp":bp_from_share(raw/unique_total),
          "target_share_bp":target_bp[s],
          "target_cycle_tokens":target,
          "equivalent_passes_x1000":int(round((target/raw)*1000)),
          "sampling_weight_x1000":int(round((target_bp[s]/max(1,raw_bp[s]))*1000))}

    persona_oriented_bp=target_bp["CONTROLLED_TRAIN"]+target_bp["PERSONA_CORE"]
    public_target_bp=10000-target_bp["CONTROLLED_TRAIN"]

    report_out={
      "schema_version":"v59-persona-exposure-policy-1",
      "status":"EXPOSURE_POLICY_DEFINED_NOT_TRAINING_AUTHORIZED",
      "source_final_mix_policy":"PHASE03-SMOLTALK-V59-FINAL-MIX-POLICY-001",
      "streams":streams,
      "unique_ready_tokens":unique_total,
      "reference_cycle_tokens":unique_total,
      "target_share_bp":target_bp,
      "persona_oriented_share_bp":persona_oriented_bp,
      "public_share_bp":public_target_bp,
      "constraints":{
        "controlled_min_bp":3000,
        "persona_oriented_min_bp":7500,
        "general_support_max_bp":1500,
        "legacy_max_bp":1000},
      "sampler_policy":{
        "physical_duplication":False,
        "sampling_unit":"SEGMENT_STREAM",
        "with_replacement":True,
        "shuffle_within_stream":True,
        "target_basis":"TOKEN_EXPOSURE_SHARE",
        "epoch_semantics":"REFERENCE_EXPOSURE_CYCLE_NOT_UNIQUE_DATA_EPOCH"},
      "repair_queue_admitted":False,
      "exclude_admitted":False,
      "unreviewed_admitted":False,
      "mix_weighting_finalized":True,
      "training_authorized":False,
      "training_started":False}
    return report_out

def write(r):
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("persona exposure policy output already exists")
    OUT.mkdir(parents=True)
    (OUT/"REPORT-001.json").write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    policy={
      "schema_version":"v59-persona-exposure-sampler-1",
      "sampling_unit":"SEGMENT_STREAM",
      "target_share_bp":r["target_share_bp"],
      "with_replacement":True,
      "shuffle_within_stream":True,
      "physical_duplication":False,
      "reference_cycle_tokens":r["reference_cycle_tokens"],
      "training_authorized":False}
    (OUT/"SAMPLER-POLICY-001.json").write_text(json.dumps(policy,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=["# Mini-Kuzai V59 - persona-first mix weighting / exposure policy","",
      "Status --> **POLICY DEFINED / TRAINING NOT AUTHORIZED**","",
      "The policy uses weighted stream sampling. No training record is physically duplicated.","",
      "## Unique clean data","",
      "| Stream | Conversations | Segments | Unique tokens | Raw share |",
      "| --- | ---: | ---: | ---: | ---: |"]
    for s in STREAMS:
        x=r["streams"][s]
        lines.append(f"| {s} | {x['conversations']} | {x['segments']} | {x['tokens']} | {x['raw_share_bp']/100:.2f}% |")
    lines+=["","## Persona-first exposure target","",
      "| Stream | Target share | Reference-cycle tokens | Equivalent passes |",
      "| --- | ---: | ---: | ---: |"]
    for s in STREAMS:
        x=r["streams"][s]
        lines.append(f"| {s} | {x['target_share_bp']/100:.2f}% | {x['target_cycle_tokens']} | {x['equivalent_passes_x1000']/1000:.3f}x |")
    lines+=["",
      f"Persona-oriented exposure (CONTROLLED + PERSONA_CORE) --> **{r['persona_oriented_share_bp']/100:.2f}%**",
      f"Reference exposure cycle --> **{r['reference_cycle_tokens']} tokens**","",
      "Constraints -->",
      "- CONTROLLED_TRAIN >= 30%",
      "- CONTROLLED_TRAIN + PERSONA_CORE >= 75%",
      "- GENERAL_SUPPORT <= 15%",
      "- LEGACY_STRUCTURED_KEEP <= 10%","",
      "Guardrails -->",
      "- REPAIR_QUEUE admitted --> NO",
      "- EXCLUDE_REVIEWED admitted --> NO",
      "- DEFER_UNREVIEWED admitted --> NO",
      "- physical duplication --> NO",
      "- training authorized --> NO",
      "- training started --> NO","",
      "This policy defines relative exposure only. Optimizer, learning-rate, batch, step count and training authorization remain separate decisions.","",
      "---","","##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**",""]
    (OUT/"RESULTS-001.md").write_text("\n".join(lines),encoding="utf-8")

def metrics(r):
    st=r["streams"]
    return {
      "V59_EXPOSURE_UNIQUE_TOKENS":r["unique_ready_tokens"],
      "V59_EXPOSURE_REFERENCE_CYCLE_TOKENS":r["reference_cycle_tokens"],
      "V59_EXPOSURE_CONTROLLED_RAW_BP":st["CONTROLLED_TRAIN"]["raw_share_bp"],
      "V59_EXPOSURE_CONTROLLED_TARGET_BP":st["CONTROLLED_TRAIN"]["target_share_bp"],
      "V59_EXPOSURE_CONTROLLED_PASS_X1000":st["CONTROLLED_TRAIN"]["equivalent_passes_x1000"],
      "V59_EXPOSURE_PERSONA_RAW_BP":st["PERSONA_CORE"]["raw_share_bp"],
      "V59_EXPOSURE_PERSONA_TARGET_BP":st["PERSONA_CORE"]["target_share_bp"],
      "V59_EXPOSURE_PERSONA_PASS_X1000":st["PERSONA_CORE"]["equivalent_passes_x1000"],
      "V59_EXPOSURE_GENERAL_RAW_BP":st["GENERAL_SUPPORT"]["raw_share_bp"],
      "V59_EXPOSURE_GENERAL_TARGET_BP":st["GENERAL_SUPPORT"]["target_share_bp"],
      "V59_EXPOSURE_GENERAL_PASS_X1000":st["GENERAL_SUPPORT"]["equivalent_passes_x1000"],
      "V59_EXPOSURE_LEGACY_RAW_BP":st["LEGACY_STRUCTURED_KEEP"]["raw_share_bp"],
      "V59_EXPOSURE_LEGACY_TARGET_BP":st["LEGACY_STRUCTURED_KEEP"]["target_share_bp"],
      "V59_EXPOSURE_LEGACY_PASS_X1000":st["LEGACY_STRUCTURED_KEEP"]["equivalent_passes_x1000"],
      "V59_EXPOSURE_PERSONA_ORIENTED_BP":r["persona_oriented_share_bp"],
      "V59_EXPOSURE_PHYSICAL_DUPLICATION":0,
      "V59_EXPOSURE_REPAIR_ADMITTED":0,
      "V59_EXPOSURE_UNREVIEWED_ADMITTED":0,
      "V59_EXPOSURE_POLICY_FINALIZED":int(r["mix_weighting_finalized"]),
      "V59_MIX_FINALIZED":0,
      "SEMANTIC_VALIDATION_COMPLETE":1,
      "TRAINING_AUTHORIZED":0}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--write",action="store_true"); ap.add_argument("--from-report",action="store_true"); a=ap.parse_args()
    r=json.loads((OUT/"REPORT-001.json").read_text(encoding="utf-8")) if a.from_report else derive()
    if a.write: write(r)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for k,v in sorted(metrics(r).items()): print(f"{k}: {v}")

if __name__=="__main__": main()
