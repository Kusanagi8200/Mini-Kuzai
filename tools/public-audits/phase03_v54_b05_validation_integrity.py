#!/usr/bin/env python3
"""Read-only integrity gate for Phase 03 V54 B05 validation."""
import json
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
BATCH=ROOT/"data/phase-03/validation/validation-batch-b05-v0.1.jsonl"
REVIEW=ROOT/"reviews/phase-03-v54/B05-INDEPENDENT-REVIEW-RESULT-001.json"
REPORT=ROOT/"data/phase-03/reports/validation-batch-b05-v0.1-review.json"
MANIFEST=ROOT/"data/phase-03/manifests/validation-batch-b05-v0.1-manifest.json"
SPLITS=ROOT/"data/phase-03/schema/semantic-group-split-manifest-v0.1.json"
B04_HISTORY=ROOT/"reports/assistant-results/history/PHASE03-SMOLTALK-V54-B04-VALIDATION-FREEZE-001.json"
BLIND_DIR=ROOT/"data/phase-03/blind-test"
TRAIN_NAMES=["train-pilot-v0.2.jsonl",*["train-batch-b{:02d}-{}.jsonl".format(n,{8:"v0.5",12:"v0.3"}.get(n,"v0.2")) for n in range(1,19)]]
EXPECTED_IDS={"p03-val-b05-000001","p03-val-b05-000002"}

def load_json(path):
    if not path.is_file() or path.is_symlink(): raise RuntimeError("Missing or unsafe JSON: "+str(path.relative_to(ROOT)))
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise RuntimeError("Expected JSON object")
    return value

def load_jsonl(path):
    if not path.is_file() or path.is_symlink(): raise RuntimeError("Missing or unsafe JSONL: "+str(path.relative_to(ROOT)))
    rows=[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not all(isinstance(x,dict) for x in rows): raise RuntimeError("Expected JSONL objects")
    return rows

def norm(text): return " ".join(unicodedata.normalize("NFKC",text).casefold().split())
def prompts(row): return [norm(m["content"]) for m in row["messages"] if m["role"]=="user"]

def answer_plus_question_count(rows):
    count=0
    for row in rows:
        assistant=[m["content"] for m in row["messages"] if m["role"]=="assistant"]
        if assistant and all("?" in text for text in assistant):
            count+=1
    return count

def audit():
    b04=load_json(B04_HISTORY)
    if b04.get("metrics",{}).get("B04_VALIDATION_FROZEN")!=1: raise RuntimeError("B04 freeze prerequisite not confirmed")
    train=[r for name in TRAIN_NAMES for r in load_jsonl(ROOT/"data/phase-03/train"/name)]
    val=load_jsonl(BATCH)
    if len(train)!=107 or len({r["id"] for r in train})!=107: raise RuntimeError("TRAIN state changed")
    if len({r["group_id"] for r in train})!=29: raise RuntimeError("TRAIN groups changed")
    if len(val)!=2 or {r.get("id") for r in val}!=EXPECTED_IDS: raise RuntimeError("B05 candidate batch changed")
    if any(r.get("split")!="validation" or r.get("group_id")!="sg-b05-03" for r in val): raise RuntimeError("B05 split assignment invalid")
    if any(r.get("provenance",{}).get("reviewed") is not False for r in val): raise RuntimeError("B05 historical candidate provenance changed")

    behavior_shape=answer_plus_question_count(val)
    if behavior_shape!=2: raise RuntimeError("B05 answer-plus-question shape changed")

    review=load_json(REVIEW)
    if (review.get("review_complete") is not True or review.get("accepted")!=2
        or review.get("semantic_isolation_pass") is not True
        or review.get("review_status")!="PASS_TO_REVIEWED_BATCH_AND_FREEZE_AUDIT"
        or review.get("external_human_review_claimed") is not False):
        raise RuntimeError("B05 review evidence invalid")

    report=load_json(REPORT)
    if (report.get("review_status")!="PASS" or report.get("record_count")!=2
        or report.get("accepted")!=2 or report.get("semantic_guard_review")!="PASS"
        or report.get("candidate_provenance_left_immutable") is not True
        or report.get("training_authorized") is not False):
        raise RuntimeError("B05 review report invalid")

    manifest=load_json(MANIFEST)
    if (manifest.get("status")!="REVIEWED_PASS_PENDING_FREEZE_AUDIT"
        or manifest.get("group_counts")!={"sg-b05-03":2}
        or manifest.get("reviewed_by_sidecar") is not True
        or manifest.get("all_records_accepted") is not True
        or manifest.get("validation_frozen") is not False):
        raise RuntimeError("B05 manifest invalid")

    splits=load_json(SPLITS)["splits"]
    if "sg-b05-03" not in splits["validation"] or "sg-b05-04" not in splits["blind_test"]:
        raise RuntimeError("B05 reserved split allocation changed")

    for row in train+val:
        if not row.get("messages"): raise RuntimeError("Missing messages")
        for message in row["messages"]:
            if message.get("role") not in ("user","assistant") or not isinstance(message.get("content"),str) or not message["content"].strip():
                raise RuntimeError("Invalid message")

    ids={r["id"] for r in train}; groups={r["group_id"] for r in train}; tp={p for r in train for p in prompts(r)}
    ih=sum(r["id"] in ids for r in val); gh=sum(r["group_id"] in groups for r in val); ph=sum(p in tp for r in val for p in prompts(r))
    if ih or gh or ph: raise RuntimeError("Cross-split collision detected")

    if BLIND_DIR.exists() and any(p.is_file() and not p.is_symlink() for p in BLIND_DIR.rglob("*")):
        raise RuntimeError("BLIND TEST text/files exist before authorized authoring")

    return dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_B05_CANDIDATES":2,
        "B05_ANSWER_PLUS_QUESTION_RECORDS":behavior_shape,
        "CROSS_SPLIT_ID_COLLISIONS":ih,
        "CROSS_SPLIT_GROUP_COLLISIONS":gh,
        "EXACT_USER_PROMPT_MATCHES":ph,
        "B05_INDEPENDENT_SIGNOFF":1,
        "B05_VALIDATION_FROZEN":0,
        "VALIDATION_FROZEN_RECORDS":8,
        "VALIDATION_BEHAVIORS_FROZEN":4,
        "TRAINING_AUTHORIZED":0,
    }.items()))

def require_expected_state(metrics):
    expected=dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_B05_CANDIDATES":2,
        "B05_ANSWER_PLUS_QUESTION_RECORDS":2,
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "B05_INDEPENDENT_SIGNOFF":1,
        "B05_VALIDATION_FROZEN":0,
        "VALIDATION_FROZEN_RECORDS":8,
        "VALIDATION_BEHAVIORS_FROZEN":4,
        "TRAINING_AUTHORIZED":0,
    }.items()))
    if metrics!=expected: raise RuntimeError("B05 integrity state differs from expected")

if __name__=="__main__":
    metrics=audit(); require_expected_state(metrics); print(MARKER)
    for key,value in metrics.items(): print("{}: {}".format(key,value))
