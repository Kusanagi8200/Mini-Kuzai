#!/usr/bin/env python3
"""Generic state/evidence engine for Phase 03 V55 BLIND TEST authoring."""
import hashlib
import json
import os
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/"reports/assistant-results/history"
MASTER=ROOT/"data/phase-03/manifests/blind-master-v55.json"
SPLITS=ROOT/"data/phase-03/schema/semantic-group-split-manifest-v0.1.json"
VALIDATION_CLOSURE_STEP="PHASE03-SMOLTALK-V54-VALIDATION-CLOSURE-001"
SOURCE_BLIND="Mini-Kuzai Phase 03 designed blind-test corpus"
SOURCE_VALIDATION="Mini-Kuzai Phase 03 designed validation corpus"

TRAIN_NAMES=[
    "train-pilot-v0.2.jsonl",
    *["train-batch-b{:02d}-{}.jsonl".format(
        n,{8:"v0.5",12:"v0.3"}.get(n,"v0.2")
    ) for n in range(1,19)]
]
VALIDATION_NAMES=[
    "validation-batch-b01-v0.2.jsonl",
    "validation-batch-b02-v0.3.jsonl",
    "validation-batch-b03-v0.1.jsonl",
    "validation-batch-b04-v0.1.jsonl",
    "validation-batch-b05-v0.1.jsonl",
    "validation-batch-b06-v0.1.jsonl",
    "validation-batch-b07-v0.2.jsonl",
    *["validation-batch-b{:02d}-v0.1.jsonl".format(n) for n in range(8,19)]
]

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

def load_master():
    master=load_json(MASTER)
    if (master.get("version")!="V55"
        or master.get("status")!="REVIEWED_READY_FOR_BLIND_FREEZE"
        or master.get("total_behaviors")!=18
        or master.get("target_records")!=36
        or master.get("training_authorized") is not False):
        raise RuntimeError("Unexpected BLIND master manifest state")
    behaviors=master.get("behaviors")
    if not isinstance(behaviors,list) or len(behaviors)!=18:
        raise RuntimeError("BLIND behavior inventory invalid")
    expected=["B{:02d}".format(i) for i in range(1,19)]
    if [item.get("behavior") for item in behaviors]!=expected:
        raise RuntimeError("BLIND behavior order invalid")
    return master

def behavior_config(behavior=None):
    behavior=(behavior or os.environ.get("MINI_KUZAI_BLIND_BEHAVIOR","")).upper()
    if not behavior.startswith("B") or len(behavior)!=3 or not behavior[1:].isdigit():
        raise RuntimeError("MINI_KUZAI_BLIND_BEHAVIOR must be B01..B18")
    master=load_master()
    for item in master["behaviors"]:
        if item["behavior"]==behavior:
            return master,item
    raise RuntimeError("Unknown BLIND behavior "+behavior)

def verify_validation_closure():
    path=HISTORY/(VALIDATION_CLOSURE_STEP+".json")
    report=load_json(path)
    if report.get("step_id")!=VALIDATION_CLOSURE_STEP:
        raise RuntimeError("VALIDATION closure STEP_ID mismatch")
    if report.get("source")!=SOURCE_VALIDATION:
        raise RuntimeError("VALIDATION closure source mismatch")
    if report.get("semantic_validation_complete") is not True:
        raise RuntimeError("VALIDATION semantic closure is not complete")
    if report.get("training_authorized") is not False:
        raise RuntimeError("VALIDATION closure unexpectedly authorizes training")
    metrics=report.get("metrics",{})
    expected={
        "SEMANTIC_VALIDATION_COMPLETE":1,
        "BLIND_AUTHORING_AUTHORIZED":1,
        "VALIDATION_RECORDS":36,
        "VALIDATION_GROUPS":18,
        "BLIND_TEST_RECORDS":0,
        "TRAINING_AUTHORIZED":0,
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
    }
    for key,value in expected.items():
        if metrics.get(key)!=value:
            raise RuntimeError("VALIDATION closure metric mismatch: "+key)

def history_report(step):
    path=HISTORY/(step+".json")
    if not path.is_file():
        return None
    return load_json(path)

def verify_previous_freeze(cfg):
    index=cfg["index"]
    if index==1:
        verify_validation_closure()
        return
    prev="B{:02d}".format(index-1)
    step="PHASE03-SMOLTALK-V55-{}-BLIND-FREEZE-001".format(prev)
    report=history_report(step)
    if report is None:
        raise RuntimeError("Previous BLIND freeze history missing for "+prev)
    if report.get("step_id")!=step or report.get("source")!=SOURCE_BLIND:
        raise RuntimeError("Previous BLIND freeze metadata mismatch for "+prev)
    if report.get("semantic_validation_complete") is not True:
        raise RuntimeError("VALIDATION completion flag regressed in "+prev)
    if report.get("training_authorized") is not False:
        raise RuntimeError("Previous BLIND freeze unexpectedly authorizes training")
    metrics=report.get("metrics",{})
    expected={
        "BLIND_BATCH_INDEX":index-1,
        "BLIND_BATCH_FROZEN":1,
        "BLIND_BATCH_SIGNOFF":1,
        "BLIND_BATCH_SEMANTIC_PASS":1,
        "BLIND_TEST_RECORDS_FROZEN":(index-1)*2,
        "BLIND_BEHAVIORS_FROZEN":index-1,
        "SEMANTIC_VALIDATION_COMPLETE":1,
        "BLIND_AUTHORING_AUTHORIZED":1,
        "TRAINING_AUTHORIZED":0,
    }
    for key,value in expected.items():
        if metrics.get(key)!=value:
            raise RuntimeError("Previous BLIND freeze metric mismatch: {} {}".format(prev,key))

def canonical_blind_rows(master):
    all_rows=[]
    ids=[]
    groups=set()
    user_prompts=[]
    canonical_paths=set()
    for cfg in master["behaviors"]:
        path=ROOT/cfg["batch_path"]
        canonical_paths.add(path.resolve())
        if git_blob_sha(path)!=cfg["batch_blob_sha"]:
            raise RuntimeError("BLIND batch blob changed for "+cfg["behavior"])
        rows=load_jsonl(path)
        if len(rows)!=2 or {r.get("id") for r in rows}!=set(cfg["expected_ids"]):
            raise RuntimeError("BLIND batch record set changed for "+cfg["behavior"])
        for row in rows:
            if row.get("split")!="blind_test":
                raise RuntimeError("BLIND split mismatch for "+cfg["behavior"])
            if row.get("group_id")!=cfg["group_id"]:
                raise RuntimeError("BLIND group mismatch for "+cfg["behavior"])
            if row.get("primary_behavior")!=cfg["behavior"]:
                raise RuntimeError("BLIND primary behavior mismatch for "+cfg["behavior"])
            if row.get("scenario_type")!=cfg["scenario_type"]:
                raise RuntimeError("BLIND scenario mismatch for "+cfg["behavior"])
            if row.get("provenance",{}).get("reviewed") is not False:
                raise RuntimeError("BLIND candidate provenance was rewritten for "+cfg["behavior"])
            messages=row.get("messages")
            if not isinstance(messages,list) or not messages:
                raise RuntimeError("BLIND messages missing for "+cfg["behavior"])
            for message in messages:
                if message.get("role") not in ("user","assistant"):
                    raise RuntimeError("Invalid BLIND role")
                if not isinstance(message.get("content"),str) or not message["content"].strip():
                    raise RuntimeError("Invalid BLIND content")
            ids.append(row["id"])
            groups.add(row["group_id"])
            user_prompts.extend(prompts(row))
            all_rows.append(row)

        review=load_json(ROOT/cfg["review_path"])
        if (review.get("review_id")!=cfg["review_id"]
            or review.get("target_blob_sha")!=cfg["batch_blob_sha"]
            or review.get("review_complete") is not True
            or review.get("status")!="PASS_TO_BLIND_FREEZE_AUDIT"
            or review.get("accepted")!=2
            or review.get("revise")!=0
            or review.get("semantic_isolation_pass") is not True
            or review.get("external_human_review_claimed") is not False
            or review.get("training_approved") is not False
            or review.get("blind_frozen") is not False):
            raise RuntimeError("BLIND review evidence invalid for "+cfg["behavior"])

    if len(all_rows)!=36 or len(set(ids))!=36 or len(groups)!=18:
        raise RuntimeError("Global canonical BLIND shape invalid")
    if len(user_prompts)!=len(set(user_prompts)):
        raise RuntimeError("Duplicate normalized user prompts inside canonical BLIND corpus")

    blind_dir=ROOT/"data/phase-03/blind-test"
    allowed_superseded={
        (blind_dir/"blind-batch-b02-v0.1.jsonl").resolve(),
        (blind_dir/"blind-batch-b03-v0.1.jsonl").resolve(),
    }
    actual={p.resolve() for p in blind_dir.glob("*.jsonl") if p.is_file() and not p.is_symlink()}
    unexpected=actual-canonical_paths-allowed_superseded
    if unexpected:
        raise RuntimeError("Unexpected BLIND JSONL files: "+", ".join(sorted(str(p.relative_to(ROOT)) for p in unexpected)))
    return all_rows

def reference_rows():
    train=[row for name in TRAIN_NAMES for row in load_jsonl(ROOT/"data/phase-03/train"/name)]
    validation=[row for name in VALIDATION_NAMES for row in load_jsonl(ROOT/"data/phase-03/validation"/name)]
    if len(train)!=107 or len({r["id"] for r in train})!=107 or len({r["group_id"] for r in train})!=29:
        raise RuntimeError("Canonical TRAIN state changed")
    if len(validation)!=36 or len({r["id"] for r in validation})!=36 or len({r["group_id"] for r in validation})!=18:
        raise RuntimeError("Canonical VALIDATION state changed")
    return train,validation

def validate_global_split(master,blind_rows):
    split=load_json(SPLITS)["splits"]
    reserved=set(split["blind_test"])
    groups={r["group_id"] for r in blind_rows}
    if len(reserved)!=18 or groups!=reserved:
        raise RuntimeError("Canonical BLIND group coverage differs from reservation")

    train,validation=reference_rows()
    refs=train+validation
    ref_ids={r["id"] for r in refs}
    ref_groups={r["group_id"] for r in refs}
    ref_prompts={p for r in refs for p in prompts(r)}

    cross_id=sum(r["id"] in ref_ids for r in blind_rows)
    cross_group=len(groups & ref_groups)
    cross_prompt=sum(p in ref_prompts for r in blind_rows for p in prompts(r))
    if cross_id or cross_group or cross_prompt:
        raise RuntimeError("TRAIN/VALIDATION/BLIND exact collision detected")
    return cross_id,cross_group,cross_prompt

def integrity_metrics(behavior=None):
    master,cfg=behavior_config(behavior)
    verify_validation_closure()
    verify_previous_freeze(cfg)
    blind=canonical_blind_rows(master)
    ci,cg,cp=validate_global_split(master,blind)
    return dict(sorted({
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_RECORDS":36,
        "VALIDATION_GROUPS":18,
        "SEMANTIC_VALIDATION_COMPLETE":1,
        "BLIND_AUTHORING_AUTHORIZED":1,
        "BLIND_BATCH_INDEX":cfg["index"],
        "BLIND_BATCH_CANDIDATES":2,
        "BLIND_BATCH_SIGNOFF":1,
        "BLIND_BATCH_SEMANTIC_PASS":1,
        "BLIND_BATCH_FROZEN":0,
        "BLIND_TEST_RECORDS_FROZEN":cfg["cumulative_before_records"],
        "BLIND_BEHAVIORS_FROZEN":cfg["cumulative_before_behaviors"],
        "CROSS_SPLIT_ID_COLLISIONS":ci,
        "CROSS_SPLIT_GROUP_COLLISIONS":cg,
        "EXACT_USER_PROMPT_MATCHES":cp,
        "TRAINING_AUTHORIZED":0,
    }.items()))

def require_integrity_expected(metrics,behavior=None):
    _,cfg=behavior_config(behavior)
    expected=dict(sorted({
        "TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_RECORDS":36,"VALIDATION_GROUPS":18,
        "SEMANTIC_VALIDATION_COMPLETE":1,"BLIND_AUTHORING_AUTHORIZED":1,
        "BLIND_BATCH_INDEX":cfg["index"],"BLIND_BATCH_CANDIDATES":2,
        "BLIND_BATCH_SIGNOFF":1,"BLIND_BATCH_SEMANTIC_PASS":1,
        "BLIND_BATCH_FROZEN":0,
        "BLIND_TEST_RECORDS_FROZEN":cfg["cumulative_before_records"],
        "BLIND_BEHAVIORS_FROZEN":cfg["cumulative_before_behaviors"],
        "CROSS_SPLIT_ID_COLLISIONS":0,"CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,"TRAINING_AUTHORIZED":0,
    }.items()))
    if metrics!=expected:
        raise RuntimeError("V55 BLIND integrity state differs from expected for "+cfg["behavior"])

def freeze_metrics(behavior=None):
    master,cfg=behavior_config(behavior)
    step=cfg["integrity_step_id"]
    history=history_report(step)
    if history is None:
        raise RuntimeError("BLIND integrity history missing for "+cfg["behavior"])
    if history.get("step_id")!=step or history.get("source")!=SOURCE_BLIND:
        raise RuntimeError("BLIND integrity history metadata mismatch for "+cfg["behavior"])
    if history.get("semantic_validation_complete") is not True:
        raise RuntimeError("VALIDATION completion flag missing from BLIND integrity history")
    if history.get("training_authorized") is not False:
        raise RuntimeError("BLIND integrity history unexpectedly authorizes training")
    expected_integrity=integrity_metrics(cfg["behavior"])
    for key,value in expected_integrity.items():
        if history.get("metrics",{}).get(key)!=value:
            raise RuntimeError("Published BLIND integrity mismatch for {}: {}".format(cfg["behavior"],key))

    blind=canonical_blind_rows(master)
    ci,cg,cp=validate_global_split(master,blind)
    return dict(sorted({
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_RECORDS":36,
        "VALIDATION_GROUPS":18,
        "SEMANTIC_VALIDATION_COMPLETE":1,
        "BLIND_AUTHORING_AUTHORIZED":1,
        "BLIND_BATCH_INDEX":cfg["index"],
        "BLIND_BATCH_CANDIDATES":2,
        "BLIND_BATCH_SIGNOFF":1,
        "BLIND_BATCH_SEMANTIC_PASS":1,
        "BLIND_BATCH_FROZEN":1,
        "BLIND_TEST_RECORDS_FROZEN":cfg["cumulative_after_records"],
        "BLIND_BEHAVIORS_FROZEN":cfg["cumulative_after_behaviors"],
        "CROSS_SPLIT_ID_COLLISIONS":ci,
        "CROSS_SPLIT_GROUP_COLLISIONS":cg,
        "EXACT_USER_PROMPT_MATCHES":cp,
        "TRAINING_AUTHORIZED":0,
    }.items()))

def require_freeze_expected(metrics,behavior=None):
    _,cfg=behavior_config(behavior)
    expected=dict(sorted({
        "TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_RECORDS":36,"VALIDATION_GROUPS":18,
        "SEMANTIC_VALIDATION_COMPLETE":1,"BLIND_AUTHORING_AUTHORIZED":1,
        "BLIND_BATCH_INDEX":cfg["index"],"BLIND_BATCH_CANDIDATES":2,
        "BLIND_BATCH_SIGNOFF":1,"BLIND_BATCH_SEMANTIC_PASS":1,
        "BLIND_BATCH_FROZEN":1,
        "BLIND_TEST_RECORDS_FROZEN":cfg["cumulative_after_records"],
        "BLIND_BEHAVIORS_FROZEN":cfg["cumulative_after_behaviors"],
        "CROSS_SPLIT_ID_COLLISIONS":0,"CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,"TRAINING_AUTHORIZED":0,
    }.items()))
    if metrics!=expected:
        raise RuntimeError("V55 BLIND freeze state differs from expected for "+cfg["behavior"])
