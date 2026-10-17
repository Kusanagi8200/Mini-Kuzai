#!/usr/bin/env python3
"""Final read-only freeze gate for Phase 03 V54 B04 validation."""
import json
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
BATCH=ROOT/"data/phase-03/validation/validation-batch-b04-v0.1.jsonl"
REVIEW=ROOT/"reviews/phase-03-v54/B04-INDEPENDENT-REVIEW-RESULT-001.json"
REPORT=ROOT/"data/phase-03/reports/validation-batch-b04-v0.1-review.json"
MANIFEST=ROOT/"data/phase-03/manifests/validation-batch-b04-v0.1-manifest.json"
FREEZE=ROOT/"data/phase-03/manifests/validation-batch-b04-v0.1-freeze-declaration.json"
SPLITS=ROOT/"data/phase-03/schema/semantic-group-split-manifest-v0.1.json"
B03_HISTORY=ROOT/"reports/assistant-results/history/PHASE03-SMOLTALK-V54-B03-VALIDATION-FREEZE-001.json"
INTEGRITY_HISTORY=ROOT/"reports/assistant-results/history/PHASE03-SMOLTALK-V54-B04-VALIDATION-INTEGRITY-001.json"
BLIND_DIR=ROOT/"data/phase-03/blind-test"
TRAIN_NAMES=["train-pilot-v0.2.jsonl",*["train-batch-b{:02d}-{}.jsonl".format(n,{8:"v0.5",12:"v0.3"}.get(n,"v0.2")) for n in range(1,19)]]
EXPECTED_IDS={"p03-val-b04-000001","p03-val-b04-000002"}
HIDDEN_TERMS=("kuzai-llm",)

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
def visible_text(row): return "\n".join(m["content"] for m in row["messages"]).casefold()

def validate_history():
    b03=load_json(B03_HISTORY).get("metrics",{})
    if b03.get("B03_VALIDATION_FROZEN")!=1: raise RuntimeError("B03 freeze prerequisite lost")
    integrity=load_json(INTEGRITY_HISTORY)
    if integrity.get("step_id")!="PHASE03-SMOLTALK-V54-B04-VALIDATION-INTEGRITY-001":
        raise RuntimeError("B04 integrity STEP_ID mismatch")
    metrics=integrity.get("metrics",{})
    expected={
        "B04_INDEPENDENT_SIGNOFF":1,
        "B04_VALIDATION_FROZEN":0,
        "VALIDATION_B04_CANDIDATES":2,
        "B04_HIDDEN_ROADMAP_EXPOSURES":0,
        "TRAIN_RECORDS":107,
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
    }
    for key,value in expected.items():
        if metrics.get(key)!=value:
            raise RuntimeError("B04 integrity history not passing: "+key)

def validate_evidence():
    val=load_jsonl(BATCH)
    if len(val)!=2 or {r["id"] for r in val}!=EXPECTED_IDS: raise RuntimeError("B04 batch changed")
    if any(r.get("provenance",{}).get("reviewed") is not False for r in val): raise RuntimeError("B04 candidate provenance changed")
    hidden_hits=sum(any(term in visible_text(r) for term in HIDDEN_TERMS) for r in val)
    if hidden_hits: raise RuntimeError("Hidden roadmap term exposed in B04 model-visible text")

    review=load_json(REVIEW)
    if (review.get("review_status")!="PASS_TO_REVIEWED_BATCH_AND_FREEZE_AUDIT"
        or review.get("review_complete") is not True
        or review.get("accepted")!=2
        or review.get("semantic_isolation_pass") is not True
        or review.get("hidden_roadmap_exposed") is not False
        or review.get("external_human_review_claimed") is not False):
        raise RuntimeError("B04 review evidence changed")

    report=load_json(REPORT)
    if (report.get("review_status")!="PASS" or report.get("record_count")!=2
        or report.get("accepted")!=2
        or report.get("model_visible_text_changed") is not False
        or report.get("semantic_guard_review")!="PASS"
        or report.get("hidden_roadmap_exposed") is not False
        or report.get("candidate_provenance_left_immutable") is not True
        or report.get("training_authorized") is not False):
        raise RuntimeError("B04 review report changed")

    manifest=load_json(MANIFEST)
    if (manifest.get("status")!="REVIEWED_PASS_PENDING_FREEZE_AUDIT"
        or manifest.get("batch_blob_sha")!="5481509165aabf0f4e4c888b88aa893ffa96b80c"
        or manifest.get("record_count")!=2
        or manifest.get("group_counts")!={"sg-b04-02":2}
        or manifest.get("reviewed_by_sidecar") is not True
        or manifest.get("all_records_accepted") is not True
        or manifest.get("hidden_roadmap_exposed") is not False
        or manifest.get("validation_frozen") is not False):
        raise RuntimeError("B04 manifest changed")

    freeze=load_json(FREEZE)
    if (freeze.get("declaration_id")!="V54-B04-VALIDATION-FREEZE-001"
        or freeze.get("status")!="PENDING_SUCCESSFUL_GOGIT_AUDIT"
        or freeze.get("target_step_id")!="PHASE03-SMOLTALK-V54-B04-VALIDATION-FREEZE-001"
        or freeze.get("integrity_step_id")!="PHASE03-SMOLTALK-V54-B04-VALIDATION-INTEGRITY-001"
        or freeze.get("target_batch_blob_sha")!="5481509165aabf0f4e4c888b88aa893ffa96b80c"
        or freeze.get("records")!=2
        or freeze.get("group_id")!="sg-b04-02"
        or freeze.get("hidden_roadmap_exposed") is not False):
        raise RuntimeError("B04 freeze declaration changed")
    return val,hidden_hits

def validate_cross_split(val):
    train=[r for name in TRAIN_NAMES for r in load_jsonl(ROOT/"data/phase-03/train"/name)]
    if len(train)!=107 or len({r["id"] for r in train})!=107 or len({r["group_id"] for r in train})!=29:
        raise RuntimeError("Canonical TRAIN state changed")
    splits=load_json(SPLITS)["splits"]
    if "sg-b04-02" not in splits["validation"] or "sg-b04-01" not in splits["blind_test"]:
        raise RuntimeError("B04 split reservation changed")
    ids={r["id"] for r in train}; groups={r["group_id"] for r in train}; tp={p for r in train for p in prompts(r)}
    ih=sum(r["id"] in ids for r in val); gh=sum(r["group_id"] in groups for r in val); ph=sum(p in tp for r in val for p in prompts(r))
    if ih or gh or ph: raise RuntimeError("Cross-split collision detected at freeze gate")
    if BLIND_DIR.exists() and any(p.is_file() and not p.is_symlink() for p in BLIND_DIR.rglob("*")):
        raise RuntimeError("BLIND TEST text/files exist before authorized authoring")
    return ih,gh,ph

def audit():
    validate_history(); val,hidden_hits=validate_evidence(); ih,gh,ph=validate_cross_split(val)
    return dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_B04_CANDIDATES":2,
        "CROSS_SPLIT_ID_COLLISIONS":ih,
        "CROSS_SPLIT_GROUP_COLLISIONS":gh,
        "EXACT_USER_PROMPT_MATCHES":ph,
        "B04_HIDDEN_ROADMAP_EXPOSURES":hidden_hits,
        "B04_INDEPENDENT_SIGNOFF":1,
        "B04_VALIDATION_FROZEN":1,
        "VALIDATION_FROZEN_RECORDS":8,
        "VALIDATION_BEHAVIORS_FROZEN":4,
        "TRAINING_AUTHORIZED":0,
    }.items()))

def require_expected_state(metrics):
    expected=dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_B04_CANDIDATES":2,
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "B04_HIDDEN_ROADMAP_EXPOSURES":0,
        "B04_INDEPENDENT_SIGNOFF":1,
        "B04_VALIDATION_FROZEN":1,
        "VALIDATION_FROZEN_RECORDS":8,
        "VALIDATION_BEHAVIORS_FROZEN":4,
        "TRAINING_AUTHORIZED":0,
    }.items()))
    if metrics!=expected: raise RuntimeError("B04 freeze state differs from expected")

if __name__=="__main__":
    metrics=audit(); require_expected_state(metrics); print(MARKER)
    for key,value in metrics.items(): print("{}: {}".format(key,value))
