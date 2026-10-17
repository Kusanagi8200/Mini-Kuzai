#!/usr/bin/env python3
"""Generic state/evidence engine for Phase 03 V54 validation batches B06+."""
import hashlib
import json
import os
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/"reports/assistant-results/history"
BLIND_DIR=ROOT/"data/phase-03/blind-test"
SPLITS=ROOT/"data/phase-03/schema/semantic-group-split-manifest-v0.1.json"
TRAIN_NAMES=["train-pilot-v0.2.jsonl",*["train-batch-b{:02d}-{}.jsonl".format(n,{8:"v0.5",12:"v0.3"}.get(n,"v0.2")) for n in range(1,19)]]
SOURCE="Mini-Kuzai Phase 03 designed validation corpus"

def load_json(path):
    path=Path(path)
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe JSON: "+str(path.relative_to(ROOT)))
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise RuntimeError("Expected JSON object: "+str(path.relative_to(ROOT)))
    return value

def load_jsonl(path):
    path=Path(path)
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe JSONL: "+str(path.relative_to(ROOT)))
    rows=[json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows or not all(isinstance(row,dict) for row in rows):
        raise RuntimeError("Expected non-empty JSONL objects: "+str(path.relative_to(ROOT)))
    return rows

def git_blob_sha(path):
    data=Path(path).read_bytes()
    raw=b"blob "+str(len(data)).encode("ascii")+b"\0"+data
    return hashlib.sha1(raw).hexdigest()

def norm(text):
    return " ".join(unicodedata.normalize("NFKC",text).casefold().split())

def prompts(row):
    return [norm(m["content"]) for m in row["messages"] if m["role"]=="user"]

def config_path(behavior):
    return ROOT/"data/phase-03/manifests"/("validation-{}-v54-config.json".format(behavior.lower()))

def load_config(behavior=None):
    behavior=(behavior or os.environ.get("MINI_KUZAI_VALIDATION_BEHAVIOR","")).upper()
    if not behavior.startswith("B") or len(behavior)!=3 or not behavior[1:].isdigit():
        raise RuntimeError("MINI_KUZAI_VALIDATION_BEHAVIOR must be B06..B18")
    cfg=load_json(config_path(behavior))
    if cfg.get("behavior")!=behavior or cfg.get("version")!="V54":
        raise RuntimeError("Validation config identity mismatch for "+behavior)
    index=int(behavior[1:])
    if cfg.get("index")!=index or index<6 or index>18:
        raise RuntimeError("Generic engine supports configured B06..B18 only")
    if cfg.get("training_authorized") is not False:
        raise RuntimeError("Validation config unexpectedly authorizes training")
    return cfg

def verify_history(step, *, expected_source=SOURCE):
    path=HISTORY/(step+".json")
    report=load_json(path)
    if report.get("step_id")!=step:
        raise RuntimeError("STEP_ID mismatch for "+step)
    if report.get("source")!=expected_source:
        raise RuntimeError("Unexpected history source for "+step)
    if report.get("training_authorized") is not False:
        raise RuntimeError("Training unexpectedly authorized in "+step)
    return report

def verify_prerequisite(cfg):
    index=cfg["index"]
    report=verify_history(cfg["prerequisite_freeze_step_id"])
    metrics=report.get("metrics",{})
    previous=index-1
    if previous<=5:
        key="B{:02d}_VALIDATION_FROZEN".format(previous)
        if metrics.get(key)!=1:
            raise RuntimeError("Previous freeze prerequisite not confirmed: "+key)
    else:
        if metrics.get("VALIDATION_BATCH_INDEX")!=previous or metrics.get("VALIDATION_BATCH_FROZEN")!=1:
            raise RuntimeError("Previous generic freeze prerequisite not confirmed")
    if previous>=2:
        if metrics.get("VALIDATION_FROZEN_RECORDS")!=previous*2:
            raise RuntimeError("Previous cumulative record count mismatch")
        if metrics.get("VALIDATION_BEHAVIORS_FROZEN")!=previous:
            raise RuntimeError("Previous cumulative behavior count mismatch")

def validate_evidence(cfg):
    batch_path=ROOT/cfg["batch_path"]
    review_path=ROOT/cfg["review_path"]
    report_path=ROOT/cfg["report_path"]
    manifest_path=ROOT/cfg["manifest_path"]
    freeze_path=ROOT/cfg["freeze_declaration_path"]

    if git_blob_sha(batch_path)!=cfg["batch_blob_sha"]:
        raise RuntimeError("Validation batch blob changed for "+cfg["behavior"])
    rows=load_jsonl(batch_path)
    if len(rows)!=cfg["expected_records"] or {r.get("id") for r in rows}!=set(cfg["expected_ids"]):
        raise RuntimeError("Validation batch record set changed for "+cfg["behavior"])
    for row in rows:
        if row.get("split")!="validation" or row.get("group_id")!=cfg["group_id"]:
            raise RuntimeError("Validation split/group mismatch for "+cfg["behavior"])
        if row.get("primary_behavior")!=cfg["behavior"] or row.get("scenario_type")!=cfg["scenario_type"]:
            raise RuntimeError("Behavior/scenario mismatch for "+cfg["behavior"])
        if row.get("provenance",{}).get("reviewed") is not False:
            raise RuntimeError("Historical candidate provenance changed for "+cfg["behavior"])
        messages=row.get("messages")
        if not isinstance(messages,list) or not messages:
            raise RuntimeError("Missing messages for "+row.get("id","?"))
        for message in messages:
            if message.get("role") not in ("user","assistant"):
                raise RuntimeError("Invalid message role")
            if not isinstance(message.get("content"),str) or not message["content"].strip():
                raise RuntimeError("Invalid message content")

    review=load_json(review_path)
    if review.get("review_id")!=cfg["review_id"]:
        raise RuntimeError("Review ID mismatch for "+cfg["behavior"])
    if (review.get("review_complete") is not True
        or review.get("review_status")!="PASS_TO_REVIEWED_BATCH_AND_FREEZE_AUDIT"
        or review.get("accepted")!=2
        or review.get("semantic_isolation_pass") is not True
        or review.get("external_human_review_claimed") is not False):
        raise RuntimeError("Review evidence not passing for "+cfg["behavior"])

    tech=load_json(report_path)
    if (tech.get("behavior")!=cfg["behavior"] or tech.get("review_status")!="PASS"
        or tech.get("record_count")!=2 or tech.get("accepted")!=2
        or tech.get("semantic_guard_review")!="PASS"
        or tech.get("candidate_provenance_left_immutable") is not True
        or tech.get("training_authorized") is not False):
        raise RuntimeError("Technical review report invalid for "+cfg["behavior"])

    manifest=load_json(manifest_path)
    if (manifest.get("behavior")!=cfg["behavior"]
        or manifest.get("status")!="REVIEWED_PASS_PENDING_FREEZE_AUDIT"
        or manifest.get("batch_blob_sha")!=cfg["batch_blob_sha"]
        or manifest.get("record_count")!=2
        or manifest.get("group_counts")!={cfg["group_id"]:2}
        or manifest.get("reviewed_by_sidecar") is not True
        or manifest.get("all_records_accepted") is not True
        or manifest.get("validation_frozen") is not False
        or manifest.get("training_authorized") is not False):
        raise RuntimeError("Validation manifest invalid for "+cfg["behavior"])

    freeze=load_json(freeze_path)
    if (freeze.get("declaration_id")!="V54-{}-VALIDATION-FREEZE-001".format(cfg["behavior"])
        or freeze.get("status")!="PENDING_SUCCESSFUL_GOGIT_AUDIT"
        or freeze.get("target_step_id")!=cfg["freeze_step_id"]
        or freeze.get("integrity_step_id")!=cfg["integrity_step_id"]
        or freeze.get("prerequisite_freeze_step_id")!=cfg["prerequisite_freeze_step_id"]
        or freeze.get("target_batch_blob_sha")!=cfg["batch_blob_sha"]
        or freeze.get("records")!=2
        or freeze.get("group_id")!=cfg["group_id"]
        or freeze.get("training_authorized") is not False):
        raise RuntimeError("Freeze declaration invalid for "+cfg["behavior"])

    split=load_json(SPLITS)["splits"]
    if cfg["group_id"] not in split["validation"] or cfg["blind_group_id"] not in split["blind_test"]:
        raise RuntimeError("Reserved split allocation changed for "+cfg["behavior"])

    if BLIND_DIR.exists() and any(p.is_file() and not p.is_symlink() for p in BLIND_DIR.rglob("*")):
        raise RuntimeError("BLIND TEST text/files exist before authorized authoring")

    return rows

def validate_train_and_collisions(rows):
    train=[r for name in TRAIN_NAMES for r in load_jsonl(ROOT/"data/phase-03/train"/name)]
    if len(train)!=107 or len({r["id"] for r in train})!=107 or len({r["group_id"] for r in train})!=29:
        raise RuntimeError("Canonical TRAIN state changed")
    ids={r["id"] for r in train}
    groups={r["group_id"] for r in train}
    user_prompts={p for r in train for p in prompts(r)}
    ih=sum(r["id"] in ids for r in rows)
    gh=sum(r["group_id"] in groups for r in rows)
    ph=sum(p in user_prompts for r in rows for p in prompts(r))
    if ih or gh or ph:
        raise RuntimeError("Cross-split collision detected")
    return ih,gh,ph

def integrity_metrics(behavior=None):
    cfg=load_config(behavior)
    verify_prerequisite(cfg)
    rows=validate_evidence(cfg)
    ih,gh,ph=validate_train_and_collisions(rows)
    return dict(sorted({
        "TRAIN_FILES":19,
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_BATCH_INDEX":cfg["index"],
        "VALIDATION_BATCH_CANDIDATES":2,
        "VALIDATION_BATCH_SIGNOFF":1,
        "VALIDATION_BATCH_SEMANTIC_PASS":1,
        "VALIDATION_BATCH_FROZEN":0,
        "CROSS_SPLIT_ID_COLLISIONS":ih,
        "CROSS_SPLIT_GROUP_COLLISIONS":gh,
        "EXACT_USER_PROMPT_MATCHES":ph,
        "VALIDATION_FROZEN_RECORDS":cfg["cumulative_before_records"],
        "VALIDATION_BEHAVIORS_FROZEN":cfg["cumulative_before_behaviors"],
        "TRAINING_AUTHORIZED":0,
    }.items()))

def require_integrity_expected(metrics,behavior=None):
    cfg=load_config(behavior)
    expected=dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_BATCH_INDEX":cfg["index"],"VALIDATION_BATCH_CANDIDATES":2,
        "VALIDATION_BATCH_SIGNOFF":1,"VALIDATION_BATCH_SEMANTIC_PASS":1,
        "VALIDATION_BATCH_FROZEN":0,
        "CROSS_SPLIT_ID_COLLISIONS":0,"CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "VALIDATION_FROZEN_RECORDS":cfg["cumulative_before_records"],
        "VALIDATION_BEHAVIORS_FROZEN":cfg["cumulative_before_behaviors"],
        "TRAINING_AUTHORIZED":0,
    }.items()))
    if metrics!=expected:
        raise RuntimeError("Generic integrity state differs from expected for "+cfg["behavior"])

def freeze_metrics(behavior=None):
    cfg=load_config(behavior)
    history=verify_history(cfg["integrity_step_id"])
    expected=integrity_metrics(cfg["behavior"])
    published=history.get("metrics",{})
    for key,value in expected.items():
        if published.get(key)!=value:
            raise RuntimeError("Published integrity metric mismatch for {}: {}".format(cfg["behavior"],key))
    rows=validate_evidence(cfg)
    ih,gh,ph=validate_train_and_collisions(rows)
    return dict(sorted({
        "TRAIN_FILES":19,
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_BATCH_INDEX":cfg["index"],
        "VALIDATION_BATCH_CANDIDATES":2,
        "VALIDATION_BATCH_SIGNOFF":1,
        "VALIDATION_BATCH_SEMANTIC_PASS":1,
        "VALIDATION_BATCH_FROZEN":1,
        "CROSS_SPLIT_ID_COLLISIONS":ih,
        "CROSS_SPLIT_GROUP_COLLISIONS":gh,
        "EXACT_USER_PROMPT_MATCHES":ph,
        "VALIDATION_FROZEN_RECORDS":cfg["cumulative_after_records"],
        "VALIDATION_BEHAVIORS_FROZEN":cfg["cumulative_after_behaviors"],
        "TRAINING_AUTHORIZED":0,
    }.items()))

def require_freeze_expected(metrics,behavior=None):
    cfg=load_config(behavior)
    expected=dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_BATCH_INDEX":cfg["index"],"VALIDATION_BATCH_CANDIDATES":2,
        "VALIDATION_BATCH_SIGNOFF":1,"VALIDATION_BATCH_SEMANTIC_PASS":1,
        "VALIDATION_BATCH_FROZEN":1,
        "CROSS_SPLIT_ID_COLLISIONS":0,"CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "VALIDATION_FROZEN_RECORDS":cfg["cumulative_after_records"],
        "VALIDATION_BEHAVIORS_FROZEN":cfg["cumulative_after_behaviors"],
        "TRAINING_AUTHORIZED":0,
    }.items()))
    if metrics!=expected:
        raise RuntimeError("Generic freeze state differs from expected for "+cfg["behavior"])
