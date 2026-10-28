#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
OUT=REPO/"reviews"/"smoltalk-v59-final-mix-freeze-authorization"

FINAL_POLICY=REPO/"reviews"/"smoltalk-v59-final-mix-policy"/"REPORT-001.json"
DIRECT_KEEP=REPO/"reviews"/"smoltalk-v59-final-mix-policy"/"direct-keep-001.json"
EXPOSURE_REPORT=REPO/"reviews"/"smoltalk-v59-persona-exposure-policy"/"REPORT-001.json"
SAMPLER_POLICY=REPO/"reviews"/"smoltalk-v59-persona-exposure-policy"/"SAMPLER-POLICY-001.json"
PREFLIGHT_REPORT=REPO/"reviews"/"smoltalk-v59-training-protocol"/"REPORT-001.json"
PROTOCOL=REPO/"reviews"/"smoltalk-v59-training-protocol"/"PROTOCOL-001.json"

TOKENIZER_MANIFEST=REPO/"data"/"phase-03"/"manifests"/"tokenizer-v56-final.json"
TOKENIZER_FILE=REPO/"data"/"phase-03"/"tokenizers"/"tokenizer-v56-final.json"
ARCH_MANIFEST=REPO/"data"/"phase-03"/"manifests"/"architecture-v58-final.json"
ARCH_CONFIG=REPO/"data"/"phase-03"/"config"/"architecture-v58-final.json"
MODEL_SOURCE=REPO/"mini_kuzai"/"phase03_model.py"
SERIALIZER_SOURCE=REPO/"mini_kuzai"/"phase03_conversation.py"
SEGMENTATION_SOURCE=REPO/"mini_kuzai"/"phase03_segmentation.py"

VALIDATION_MASTER=REPO/"data"/"phase-03"/"manifests"/"validation-master-v54.json"
BLIND_MASTER=REPO/"data"/"phase-03"/"manifests"/"blind-master-v55.json"
SPLIT_MANIFEST=REPO/"data"/"phase-03"/"schema"/"semantic-group-split-manifest-v0.1.json"
TRAIN_DIR=REPO/"data"/"phase-03"/"train"

TRAIN_NAMES=[
    "train-pilot-v0.2.jsonl",
    *[
        "train-batch-b{:02d}-{}.jsonl".format(
            n,
            {8:"v0.5",12:"v0.3"}.get(n,"v0.2"),
        )
        for n in range(1,19)
    ],
]

EXPECTED_TARGET_BP={
    "CONTROLLED_TRAIN":3000,
    "PERSONA_CORE":4658,
    "GENERAL_SUPPORT":1500,
    "LEGACY_STRUCTURED_KEEP":842,
}

def sha256(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value

def canonical_sha(value):
    blob=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
    return hashlib.sha256(blob).hexdigest()

def read_train():
    files=[]
    ids=set()
    groups=set()
    records=0
    for name in TRAIN_NAMES:
        path=TRAIN_DIR/name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"Canonical TRAIN file missing: {name}")
        rows=[]
        for raw in path.read_text(encoding="utf-8").splitlines():
            if raw.strip():
                row=json.loads(raw)
                if not isinstance(row,dict) or row.get("split")!="train":
                    raise RuntimeError(f"Invalid TRAIN row in {name}")
                rows.append(row)
                rid=row.get("id"); gid=row.get("group_id")
                if not isinstance(rid,str) or rid in ids:
                    raise RuntimeError("TRAIN ID invariant failed")
                if not isinstance(gid,str):
                    raise RuntimeError("TRAIN group invariant failed")
                ids.add(rid); groups.add(gid)
        records+=len(rows)
        files.append({
            "path":str(path.relative_to(REPO)),
            "sha256":sha256(path),
            "records":len(rows),
        })
    if len(TRAIN_NAMES)!=19 or records!=107 or len(ids)!=107 or len(groups)!=29:
        raise RuntimeError("Canonical TRAIN inventory changed")
    return {
        "files":files,
        "records":records,
        "groups":len(groups),
        "record_ids_sha256":canonical_sha(sorted(ids)),
        "group_ids_sha256":canonical_sha(sorted(groups)),
    }

def build():
    final_policy=read_json(FINAL_POLICY)
    direct=read_json(DIRECT_KEEP)
    exposure=read_json(EXPOSURE_REPORT)
    sampler=read_json(SAMPLER_POLICY)
    preflight=read_json(PREFLIGHT_REPORT)
    protocol=read_json(PROTOCOL)
    tok=read_json(TOKENIZER_MANIFEST)
    arch=read_json(ARCH_MANIFEST)
    val=read_json(VALIDATION_MASTER)
    blind=read_json(BLIND_MASTER)
    split=read_json(SPLIT_MANIFEST)

    if final_policy.get("status")!="POLICY_DEFINED_NOT_FINALIZED":
        raise RuntimeError("Final policy state changed")
    if final_policy.get("candidate_population")!=1112:
        raise RuntimeError("V59 candidate population changed")
    if final_policy.get("ready_now_combined_tokens")!=295416:
        raise RuntimeError("Ready-now clean envelope changed")
    if final_policy.get("automatic_filtering_used") is not False:
        raise RuntimeError("Automatic filtering unexpectedly used")
    if final_policy.get("repair_admitted_unchanged") is not False or final_policy.get("unreviewed_admitted") is not False:
        raise RuntimeError("Unsafe V59 admission detected")

    if direct.get("bucket")!="DIRECT_KEEP" or direct.get("count")!=165:
        raise RuntimeError("DIRECT_KEEP manifest changed")
    items=direct.get("items")
    if not isinstance(items,list) or len(items)!=165:
        raise RuntimeError("DIRECT_KEEP item inventory changed")
    shas=[x.get("sha") for x in items]
    if any(not isinstance(x,str) or len(x)!=64 for x in shas) or len(set(shas))!=165:
        raise RuntimeError("DIRECT_KEEP SHA inventory invalid")

    streams={}
    for tier in ("PERSONA_CORE","GENERAL_SUPPORT","LEGACY_STRUCTURED_KEEP"):
        selected=[x for x in items if x.get("persona_tier")==tier]
        streams[tier]={
            "conversations":len(selected),
            "segments":sum(int(x["segments"]) for x in selected),
            "tokens":sum(int(x["tokens"]) for x in selected),
            "source_shas":sorted(x["sha"] for x in selected),
        }
    if (
        streams["PERSONA_CORE"]["conversations"]!=86
        or streams["GENERAL_SUPPORT"]["conversations"]!=68
        or streams["LEGACY_STRUCTURED_KEEP"]["conversations"]!=11
    ):
        raise RuntimeError("DIRECT_KEEP stream inventory changed")

    if exposure.get("status")!="EXPOSURE_POLICY_DEFINED_NOT_TRAINING_AUTHORIZED":
        raise RuntimeError("Exposure report state changed")
    if exposure.get("mix_weighting_finalized") is not True:
        raise RuntimeError("Exposure policy not finalized")
    if exposure.get("target_share_bp")!=EXPECTED_TARGET_BP:
        raise RuntimeError("Exposure target shares changed")
    if exposure.get("repair_queue_admitted") or exposure.get("exclude_admitted") or exposure.get("unreviewed_admitted"):
        raise RuntimeError("Unsafe exposure stream admitted")
    if sampler.get("target_share_bp")!=EXPECTED_TARGET_BP:
        raise RuntimeError("Sampler target shares changed")
    if sampler.get("physical_duplication") is not False or sampler.get("with_replacement") is not True:
        raise RuntimeError("Sampler policy changed")

    if preflight.get("status")!="PREFLIGHT_PASSED_AUTHORIZATION_REVIEW_REQUIRED":
        raise RuntimeError("Training preflight did not pass")
    if preflight.get("authorization_candidate") is not True:
        raise RuntimeError("Training preflight is not an authorization candidate")
    if preflight.get("training_authorized") is not False or preflight.get("training_started") is not False:
        raise RuntimeError("Unexpected training state before authorization")
    gates=preflight.get("authorization_gates")
    if not isinstance(gates,dict) or not gates or not all(gates.values()):
        raise RuntimeError("Preflight authorization gates incomplete")

    if protocol.get("authorization_candidate") is not True:
        raise RuntimeError("Protocol candidate state changed")
    if protocol.get("blind_test_reserved") is not True:
        raise RuntimeError("BLIND reservation changed")
    if protocol.get("evaluation",{}).get("blind_test_during_training") is not False:
        raise RuntimeError("BLIND access during training is forbidden")
    if protocol.get("exposure",{}).get("max_exposure_tokens")!=1181664:
        raise RuntimeError("Pilot token budget changed")
    if protocol.get("exposure",{}).get("max_optimizer_steps")!=145:
        raise RuntimeError("Pilot step budget changed")
    if protocol.get("pilot_only") is not True:
        raise RuntimeError("Authorization must remain pilot-only")

    if tok.get("status")!="FROZEN" or tok.get("tokenizer_finalized") is not True or tok.get("vocabulary_frozen") is not True:
        raise RuntimeError("Tokenizer is not frozen")
    if tok.get("fingerprint")!="62216744c1493d3bd5558120570e0178d6adb94c40311e0639dde245cfab4ee9":
        raise RuntimeError("Tokenizer fingerprint changed")
    if sha256(TOKENIZER_FILE)!=tok.get("tokenizer_sha256"):
        raise RuntimeError("Tokenizer artifact hash mismatch")

    if arch.get("status")!="FROZEN" or arch.get("architecture_frozen") is not True or arch.get("parameters")!=1184512:
        raise RuntimeError("Architecture is not frozen")
    if sha256(ARCH_CONFIG)!=arch.get("config_sha256"):
        raise RuntimeError("Architecture config hash mismatch")
    if sha256(MODEL_SOURCE)!=arch.get("model_source_sha256"):
        raise RuntimeError("Model source hash mismatch")

    if (
        val.get("status")!="CLOSED"
        or val.get("target_records")!=36
        or val.get("total_behaviors")!=18
        or val.get("semantic_validation_complete") is not True
        or val.get("global_validation_closure_complete") is not True
    ):
        raise RuntimeError("VALIDATION is not frozen/closed")
    if (
        blind.get("status")!="CLOSED"
        or blind.get("target_records")!=36
        or blind.get("total_behaviors")!=18
        or blind.get("global_blind_closure_complete") is not True
    ):
        raise RuntimeError("BLIND TEST is not frozen/closed")
    if split.get("status")!="VALIDATED" or split.get("split_counts")!={"train":29,"validation":18,"blind_test":18}:
        raise RuntimeError("Semantic split manifest changed")

    train=read_train()
    streams["CONTROLLED_TRAIN"]={
        "conversations":107,
        "segments":107,
        "tokens":24539,
        "record_ids_sha256":train["record_ids_sha256"],
        "group_ids_sha256":train["group_ids_sha256"],
    }

    fingerprints={
        "final_policy_report_sha256":sha256(FINAL_POLICY),
        "direct_keep_manifest_sha256":sha256(DIRECT_KEEP),
        "exposure_report_sha256":sha256(EXPOSURE_REPORT),
        "sampler_policy_sha256":sha256(SAMPLER_POLICY),
        "preflight_report_sha256":sha256(PREFLIGHT_REPORT),
        "training_protocol_sha256":sha256(PROTOCOL),
        "tokenizer_manifest_sha256":sha256(TOKENIZER_MANIFEST),
        "tokenizer_file_sha256":sha256(TOKENIZER_FILE),
        "architecture_manifest_sha256":sha256(ARCH_MANIFEST),
        "architecture_config_sha256":sha256(ARCH_CONFIG),
        "model_source_sha256":sha256(MODEL_SOURCE),
        "serializer_source_sha256":sha256(SERIALIZER_SOURCE),
        "segmentation_source_sha256":sha256(SEGMENTATION_SOURCE),
        "validation_master_sha256":sha256(VALIDATION_MASTER),
        "blind_master_sha256":sha256(BLIND_MASTER),
        "semantic_split_manifest_sha256":sha256(SPLIT_MANIFEST),
        "canonical_train_files_sha256":canonical_sha(train["files"]),
    }

    freeze_core={
        "schema_version":"v59-final-mix-freeze-1",
        "status":"FROZEN_FOR_BOUNDED_PILOT",
        "controlled_train":train,
        "public_direct_keep":{
            "conversations":165,
            "segments":238,
            "tokens":270877,
            "source_shas_sha256":canonical_sha(sorted(shas)),
            "streams":{
                key:value
                for key,value in streams.items()
                if key!="CONTROLLED_TRAIN"
            },
        },
        "training_streams":streams,
        "total_training_conversations":272,
        "total_unique_training_segments":345,
        "total_unique_training_tokens":295416,
        "excluded_from_training":{
            "repair_queue_conversations":108,
            "exclude_reviewed_conversations":47,
            "defer_unreviewed_conversations":792,
        },
        "target_share_bp":EXPECTED_TARGET_BP,
        "authorization_scope":{
            "pilot_only":True,
            "architecture":"V58_MICRO_FROZEN",
            "max_optimizer_steps":145,
            "max_exposure_tokens":1181664,
            "validation_allowed":True,
            "blind_test_during_training":False,
            "blind_test_reserved_for_post_training":True,
        },
        "fingerprints":fingerprints,
    }
    freeze_fingerprint=canonical_sha(freeze_core)

    report={
        "schema_version":"v59-final-mix-authorization-1",
        "status":"TRAINING_AUTHORIZED_FOR_BOUNDED_PILOT",
        "semantic_validation_complete":True,
        "mix_finalized":True,
        "freeze_fingerprint":freeze_fingerprint,
        "freeze":freeze_core,
        "authorization_gates":{
            "semantic_validation_closed":True,
            "blind_test_closed_and_reserved":True,
            "tokenizer_frozen":True,
            "serializer_fingerprinted":True,
            "segmentation_fingerprinted":True,
            "architecture_frozen":True,
            "public_mix_human_review_policy_closed":True,
            "unsafe_public_buckets_excluded":True,
            "persona_exposure_policy_finalized":True,
            "hardware_preflight_passed":True,
            "bounded_protocol_frozen":True,
        },
        "training_authorized":True,
        "training_started":False,
        "authorization_scope":"V59_BOUNDED_PILOT_ONLY",
    }
    if not all(report["authorization_gates"].values()):
        raise RuntimeError("Final authorization gate failed")
    return report

def write(report):
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("Final freeze output already exists")
    OUT.mkdir(parents=True)

    manifest={
        "schema_version":"v59-final-training-manifest-1",
        "status":"FROZEN",
        "freeze_fingerprint":report["freeze_fingerprint"],
        "training_authorized":True,
        "training_started":False,
        "authorization_scope":"V59_BOUNDED_PILOT_ONLY",
        "max_optimizer_steps":145,
        "max_exposure_tokens":1181664,
        "blind_test_during_training":False,
        "target_share_bp":EXPECTED_TARGET_BP,
        "total_training_conversations":report["freeze"]["total_training_conversations"],
        "total_unique_training_segments":report["freeze"]["total_unique_training_segments"],
        "total_unique_training_tokens":report["freeze"]["total_unique_training_tokens"],
        "fingerprints":report["freeze"]["fingerprints"],
    }

    (OUT/"FINAL-MIX-FREEZE-001.json").write_text(
        json.dumps(report["freeze"],indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (OUT/"TRAINING-AUTHORIZATION-001.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (OUT/"REPORT-001.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
      "# Mini-Kuzai V59 - final mix freeze + training authorization gate","",
      "Status --> **TRAINING AUTHORIZED FOR BOUNDED V59 PILOT ONLY**","",
      "## Frozen training mix","",
      "- controlled TRAIN conversations --> 107",
      "- clean public DIRECT_KEEP conversations --> 165",
      "- total training conversations --> **272**",
      "- total unique training segments --> **345**",
      "- total unique training tokens --> **295416**","",
      "Exposure targets -->",
      "- CONTROLLED_TRAIN --> 30.00%",
      "- PERSONA_CORE --> 46.58%",
      "- GENERAL_SUPPORT --> 15.00%",
      "- LEGACY_STRUCTURED_KEEP --> 8.42%","",
      "Explicit exclusions -->",
      "- REPAIR_QUEUE --> 108 conversations excluded",
      "- EXCLUDE_REVIEWED --> 47 conversations excluded",
      "- DEFER_UNREVIEWED --> 792 conversations excluded","",
      "## Authorization scope","",
      "- architecture --> V58 MICRO FROZEN",
      "- maximum optimizer steps --> **145**",
      "- maximum exposure tokens --> **1181664**",
      "- VALIDATION --> allowed during pilot",
      "- BLIND TEST --> forbidden during training",
      "- BLIND TEST --> reserved for post-training evaluation",
      "- authorization --> pilot only","",
      "Freeze fingerprint --> "+report["freeze_fingerprint"],"",
      "SEMANTIC_VALIDATION_COMPLETE --> **1**",
      "V59_MIX_FINALIZED --> **1**",
      "TRAINING_AUTHORIZED --> **1**",
      "TRAINING_STARTED --> **0**","",
      "This authorization does not start training. A separate trainer execution is required.","",
      "---","","##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**",""
    ]
    (OUT/"RESULTS-001.md").write_text("\n".join(lines),encoding="utf-8")

def metrics(r):
    f=r["freeze"]
    return {
      "SEMANTIC_VALIDATION_COMPLETE":1,
      "V59_MIX_FINALIZED":1,
      "V59_FINAL_TRAIN_CONVERSATIONS":f["total_training_conversations"],
      "V59_FINAL_TRAIN_SEGMENTS":f["total_unique_training_segments"],
      "V59_FINAL_UNIQUE_TOKENS":f["total_unique_training_tokens"],
      "V59_FINAL_CONTROLLED_CONVERSATIONS":107,
      "V59_FINAL_PUBLIC_KEEP_CONVERSATIONS":165,
      "V59_FINAL_REPAIR_EXCLUDED":108,
      "V59_FINAL_REVIEWED_EXCLUDED":47,
      "V59_FINAL_UNREVIEWED_EXCLUDED":792,
      "V59_FINAL_CONTROLLED_TARGET_BP":3000,
      "V59_FINAL_PERSONA_TARGET_BP":4658,
      "V59_FINAL_GENERAL_TARGET_BP":1500,
      "V59_FINAL_LEGACY_TARGET_BP":842,
      "V59_FINAL_MAX_STEPS":145,
      "V59_FINAL_MAX_EXPOSURE_TOKENS":1181664,
      "V59_FINAL_BLIND_DURING_TRAINING":0,
      "V59_FINAL_AUTH_SCOPE_BOUNDED_PILOT":1,
      "TRAINING_AUTHORIZED":1,
      "TRAINING_STARTED":0,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--write",action="store_true")
    ap.add_argument("--from-report",action="store_true")
    args=ap.parse_args()

    if args.from_report:
        report=read_json(OUT/"REPORT-001.json")
    else:
        report=build()
        if args.write:
            write(report)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for k,v in sorted(metrics(report).items()):
        print(f"{k}: {v}")

if __name__=="__main__":
    main()
