#!/usr/bin/env python3
"""Global closure audit for Phase 03 V54 VALIDATION.

This audit independently aggregates the frozen validation corpus and confirms
that VALIDATION is complete before BLIND TEST authoring is opened.
It never authorizes tokenizer finalization or model training.
"""
import json
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
HISTORY=ROOT/"reports/assistant-results/history"
SPLITS=ROOT/"data/phase-03/schema/semantic-group-split-manifest-v0.1.json"

TRAIN_NAMES=[
    "train-pilot-v0.2.jsonl",
    *["train-batch-b{:02d}-{}.jsonl".format(
        n,{8:"v0.5",12:"v0.3"}.get(n,"v0.2")
    ) for n in range(1,19)]
]

VALIDATION_SPECS=[
    ("B01","validation-batch-b01-v0.2.jsonl","validation-batch-b01-v0.2-manifest.json","sg-b01-03"),
    ("B02","validation-batch-b02-v0.3.jsonl","validation-batch-b02-v0.3-manifest.json","sg-b02-03"),
    ("B03","validation-batch-b03-v0.1.jsonl","validation-batch-b03-v0.1-manifest.json","sg-b03-03"),
    ("B04","validation-batch-b04-v0.1.jsonl","validation-batch-b04-v0.1-manifest.json","sg-b04-02"),
    ("B05","validation-batch-b05-v0.1.jsonl","validation-batch-b05-v0.1-manifest.json","sg-b05-03"),
    ("B06","validation-batch-b06-v0.1.jsonl","validation-batch-b06-v0.1-manifest.json","sg-b06-03"),
    ("B07","validation-batch-b07-v0.2.jsonl","validation-batch-b07-v0.2-manifest.json","sg-b07-02"),
    ("B08","validation-batch-b08-v0.1.jsonl","validation-batch-b08-v0.1-manifest.json","sg-b08-03"),
    ("B09","validation-batch-b09-v0.1.jsonl","validation-batch-b09-v0.1-manifest.json","sg-b09-02"),
    ("B10","validation-batch-b10-v0.1.jsonl","validation-batch-b10-v0.1-manifest.json","sg-b10-03"),
    ("B11","validation-batch-b11-v0.1.jsonl","validation-batch-b11-v0.1-manifest.json","sg-b11-03"),
    ("B12","validation-batch-b12-v0.1.jsonl","validation-batch-b12-v0.1-manifest.json","sg-b12-03"),
    ("B13","validation-batch-b13-v0.1.jsonl","validation-batch-b13-v0.1-manifest.json","sg-b13-02"),
    ("B14","validation-batch-b14-v0.1.jsonl","validation-batch-b14-v0.1-manifest.json","sg-b14-02"),
    ("B15","validation-batch-b15-v0.1.jsonl","validation-batch-b15-v0.1-manifest.json","sg-b15-02"),
    ("B16","validation-batch-b16-v0.1.jsonl","validation-batch-b16-v0.1-manifest.json","sg-b16-03"),
    ("B17","validation-batch-b17-v0.1.jsonl","validation-batch-b17-v0.1-manifest.json","sg-b17-02"),
    ("B18","validation-batch-b18-v0.1.jsonl","validation-batch-b18-v0.1-manifest.json","sg-b18-03"),
]

def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe JSON: "+str(path.relative_to(ROOT)))
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise RuntimeError("Expected JSON object: "+str(path.relative_to(ROOT)))
    return value

def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe JSONL: "+str(path.relative_to(ROOT)))
    rows=[json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not all(isinstance(row,dict) for row in rows):
        raise RuntimeError("Expected JSONL objects: "+str(path.relative_to(ROOT)))
    return rows

def norm(text):
    return " ".join(unicodedata.normalize("NFKC",text).casefold().split())

def user_prompts(row):
    return [norm(m["content"]) for m in row["messages"] if m["role"]=="user"]

def verify_freeze_history(behavior,index):
    step="PHASE03-SMOLTALK-V54-{}-VALIDATION-FREEZE-001".format(behavior)
    report=load_json(HISTORY/(step+".json"))
    if report.get("step_id")!=step:
        raise RuntimeError("Freeze STEP_ID mismatch for "+behavior)
    if report.get("source")!="Mini-Kuzai Phase 03 designed validation corpus":
        raise RuntimeError("Unexpected freeze source for "+behavior)
    if report.get("training_authorized") is not False:
        raise RuntimeError("Freeze history authorizes training for "+behavior)
    metrics=report.get("metrics",{})
    if metrics.get("TRAIN_RECORDS")!=107 or metrics.get("TRAIN_GROUPS")!=29:
        raise RuntimeError("TRAIN baseline mismatch in freeze history "+behavior)
    if metrics.get("TRAINING_AUTHORIZED")!=0:
        raise RuntimeError("Numeric training authorization is not zero for "+behavior)
    if index<=5:
        if metrics.get("{}_VALIDATION_FROZEN".format(behavior))!=1:
            raise RuntimeError("Behavior freeze not confirmed for "+behavior)
        signoff="{}_INDEPENDENT_SIGNOFF".format(behavior)
        if metrics.get(signoff)!=1:
            raise RuntimeError("Behavior signoff not confirmed for "+behavior)
    else:
        if metrics.get("VALIDATION_BATCH_INDEX")!=index:
            raise RuntimeError("Generic validation index mismatch for "+behavior)
        if metrics.get("VALIDATION_BATCH_FROZEN")!=1:
            raise RuntimeError("Generic freeze not confirmed for "+behavior)
        if metrics.get("VALIDATION_BATCH_SIGNOFF")!=1:
            raise RuntimeError("Generic signoff not confirmed for "+behavior)
        if metrics.get("VALIDATION_BATCH_SEMANTIC_PASS")!=1:
            raise RuntimeError("Generic semantic pass not confirmed for "+behavior)
    if index>=2:
        if metrics.get("VALIDATION_FROZEN_RECORDS")!=index*2:
            raise RuntimeError("Cumulative validation record mismatch for "+behavior)
        if metrics.get("VALIDATION_BEHAVIORS_FROZEN")!=index:
            raise RuntimeError("Cumulative validation behavior mismatch for "+behavior)

def audit():
    train=[row for name in TRAIN_NAMES for row in load_jsonl(ROOT/"data/phase-03/train"/name)]
    if len(train)!=107 or len({r["id"] for r in train})!=107:
        raise RuntimeError("Canonical TRAIN record state changed")
    train_groups={r["group_id"] for r in train}
    if len(train_groups)!=29:
        raise RuntimeError("Canonical TRAIN group state changed")

    split_manifest=load_json(SPLITS)["splits"]
    reserved_validation=set(split_manifest["validation"])
    reserved_blind=set(split_manifest["blind_test"])
    if len(reserved_validation)!=18 or len(reserved_blind)!=18:
        raise RuntimeError("Reserved split counts changed")

    validation=[]
    expected_groups=set()
    for index,(behavior,batch_name,manifest_name,group_id) in enumerate(VALIDATION_SPECS,1):
        verify_freeze_history(behavior,index)
        batch_path=ROOT/"data/phase-03/validation"/batch_name
        manifest_path=ROOT/"data/phase-03/manifests"/manifest_name
        rows=load_jsonl(batch_path)
        manifest=load_json(manifest_path)
        if len(rows)!=2:
            raise RuntimeError("Expected exactly 2 validation records for "+behavior)
        if manifest.get("behavior")!=behavior or manifest.get("record_count")!=2:
            raise RuntimeError("Validation manifest identity/count mismatch for "+behavior)
        if manifest.get("status")!="REVIEWED_PASS_PENDING_FREEZE_AUDIT":
            raise RuntimeError("Unexpected validation manifest status for "+behavior)
        if manifest.get("semantic_guard_review")!="PASS":
            raise RuntimeError("Semantic guard not passing for "+behavior)
        if manifest.get("all_records_accepted") is not True:
            raise RuntimeError("Not all validation records accepted for "+behavior)
        if manifest.get("training_authorized") is not False:
            raise RuntimeError("Validation manifest authorizes training for "+behavior)
        if manifest.get("blind_test_text_created") is not False:
            raise RuntimeError("Validation manifest claims BLIND text created for "+behavior)
        if set(manifest.get("group_counts",{}))!={group_id}:
            raise RuntimeError("Manifest validation group mismatch for "+behavior)
        for row in rows:
            if row.get("split")!="validation" or row.get("group_id")!=group_id:
                raise RuntimeError("Validation row split/group mismatch for "+behavior)
            if row.get("primary_behavior")!=behavior:
                raise RuntimeError("Validation primary behavior mismatch for "+behavior)
            messages=row.get("messages")
            if not isinstance(messages,list) or not messages:
                raise RuntimeError("Validation messages missing for "+behavior)
            for message in messages:
                if message.get("role") not in ("user","assistant"):
                    raise RuntimeError("Invalid validation role for "+behavior)
                if not isinstance(message.get("content"),str) or not message["content"].strip():
                    raise RuntimeError("Invalid validation content for "+behavior)
        validation.extend(rows)
        expected_groups.add(group_id)

    if len(validation)!=36:
        raise RuntimeError("Global validation record count is not 36")
    ids=[r["id"] for r in validation]
    if len(set(ids))!=36:
        raise RuntimeError("Duplicate validation IDs detected")
    groups={r["group_id"] for r in validation}
    if len(groups)!=18 or groups!=expected_groups or groups!=reserved_validation:
        raise RuntimeError("Global validation group coverage mismatch")

    train_ids={r["id"] for r in train}
    train_prompts={p for r in train for p in user_prompts(r)}
    cross_id=sum(r["id"] in train_ids for r in validation)
    cross_group=len(groups & train_groups)
    cross_prompt=sum(p in train_prompts for r in validation for p in user_prompts(r))
    if cross_id or cross_group or cross_prompt:
        raise RuntimeError("TRAIN/VALIDATION exact collision detected")

    validation_prompts=[p for r in validation for p in user_prompts(r)]
    validation_prompt_dupes=len(validation_prompts)-len(set(validation_prompts))
    if validation_prompt_dupes:
        raise RuntimeError("Duplicate normalized user prompts inside VALIDATION")

    blind_rows=0
    for path in (ROOT/"data/phase-03").rglob("*.jsonl"):
        if path.is_symlink():
            raise RuntimeError("Unsafe JSONL symlink: "+str(path.relative_to(ROOT)))
        if "/train/" in str(path).replace("\\","/") or "/validation/" in str(path).replace("\\","/"):
            continue
        for row in load_jsonl(path):
            if row.get("split")=="blind_test":
                blind_rows+=1
    if blind_rows:
        raise RuntimeError("BLIND TEST text already exists before closure authorization")

    return dict(sorted({
        "TRAIN_FILES":19,
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_RECORDS":36,
        "VALIDATION_GROUPS":18,
        "VALIDATION_FREEZE_HISTORIES":18,
        "VALIDATION_SIGNOFFS":18,
        "VALIDATION_SEMANTIC_PASSES":18,
        "VALIDATION_EXACT_PROMPT_DUPLICATES":0,
        "CROSS_SPLIT_ID_COLLISIONS":cross_id,
        "CROSS_SPLIT_GROUP_COLLISIONS":cross_group,
        "EXACT_USER_PROMPT_MATCHES":cross_prompt,
        "BLIND_TEST_RECORDS":blind_rows,
        "BLIND_TEST_GROUPS_RESERVED":18,
        "SEMANTIC_VALIDATION_COMPLETE":1,
        "BLIND_AUTHORING_AUTHORIZED":1,
        "TRAINING_AUTHORIZED":0,
    }.items()))

def require_expected_state(metrics):
    expected=dict(sorted({
        "TRAIN_FILES":19,
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_RECORDS":36,
        "VALIDATION_GROUPS":18,
        "VALIDATION_FREEZE_HISTORIES":18,
        "VALIDATION_SIGNOFFS":18,
        "VALIDATION_SEMANTIC_PASSES":18,
        "VALIDATION_EXACT_PROMPT_DUPLICATES":0,
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "BLIND_TEST_RECORDS":0,
        "BLIND_TEST_GROUPS_RESERVED":18,
        "SEMANTIC_VALIDATION_COMPLETE":1,
        "BLIND_AUTHORING_AUTHORIZED":1,
        "TRAINING_AUTHORIZED":0,
    }.items()))
    if metrics!=expected:
        raise RuntimeError("Global VALIDATION closure state differs from expected")

if __name__=="__main__":
    metrics=audit()
    require_expected_state(metrics)
    print(MARKER)
    for key,value in metrics.items():
        print("{}: {}".format(key,value))
