#!/usr/bin/env python3
"""Final read-only freeze gate for Phase 03 V54 B03 validation."""
import json
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
BATCH=ROOT/"data/phase-03/validation/validation-batch-b03-v0.1.jsonl"
REVIEW=ROOT/"reviews/phase-03-v54/B03-INDEPENDENT-REVIEW-RESULT-001.json"
REPORT=ROOT/"data/phase-03/reports/validation-batch-b03-v0.1-review.json"
MANIFEST=ROOT/"data/phase-03/manifests/validation-batch-b03-v0.1-manifest.json"
FREEZE=ROOT/"data/phase-03/manifests/validation-batch-b03-v0.1-freeze-declaration.json"
SPLITS=ROOT/"data/phase-03/schema/semantic-group-split-manifest-v0.1.json"
B02_HISTORY=ROOT/"reports/assistant-results/history/PHASE03-SMOLTALK-V54-B02-VALIDATION-FREEZE-001.json"
INTEGRITY_HISTORY=ROOT/"reports/assistant-results/history/PHASE03-SMOLTALK-V54-B03-VALIDATION-INTEGRITY-001.json"
BLIND_DIR=ROOT/"data/phase-03/blind-test"
TRAIN_NAMES=["train-pilot-v0.2.jsonl",*["train-batch-b{:02d}-{}.jsonl".format(n,{8:"v0.5",12:"v0.3"}.get(n,"v0.2")) for n in range(1,19)]]
EXPECTED_IDS={"p03-val-b03-000001","p03-val-b03-000002"}

def load_json(path):
    if not path.is_file() or path.is_symlink(): raise RuntimeError("Missing or unsafe JSON: "+str(path.relative_to(ROOT)))
    v=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(v,dict): raise RuntimeError("Expected JSON object")
    return v

def load_jsonl(path):
    if not path.is_file() or path.is_symlink(): raise RuntimeError("Missing or unsafe JSONL: "+str(path.relative_to(ROOT)))
    rows=[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not all(isinstance(x,dict) for x in rows): raise RuntimeError("Expected JSONL objects")
    return rows

def norm(s): return " ".join(unicodedata.normalize("NFKC",s).casefold().split())
def prompts(r): return [norm(m["content"]) for m in r["messages"] if m["role"]=="user"]

def validate_history():
    b02=load_json(B02_HISTORY).get("metrics",{})
    if b02.get("B02_VALIDATION_FROZEN")!=1: raise RuntimeError("B02 freeze prerequisite lost")
    integ=load_json(INTEGRITY_HISTORY)
    if integ.get("step_id")!="PHASE03-SMOLTALK-V54-B03-VALIDATION-INTEGRITY-001": raise RuntimeError("B03 integrity STEP_ID mismatch")
    m=integ.get("metrics",{})
    if (m.get("B03_INDEPENDENT_SIGNOFF")!=1 or m.get("B03_VALIDATION_FROZEN")!=0 or m.get("VALIDATION_B03_CANDIDATES")!=2
        or m.get("TRAIN_RECORDS")!=107 or m.get("CROSS_SPLIT_ID_COLLISIONS")!=0
        or m.get("CROSS_SPLIT_GROUP_COLLISIONS")!=0 or m.get("EXACT_USER_PROMPT_MATCHES")!=0):
        raise RuntimeError("B03 integrity history not passing")

def validate_evidence():
    val=load_jsonl(BATCH)
    if len(val)!=2 or {r["id"] for r in val}!=EXPECTED_IDS: raise RuntimeError("B03 batch changed")
    if any(r.get("provenance",{}).get("reviewed") is not False for r in val): raise RuntimeError("B03 candidate provenance changed")
    review=load_json(REVIEW)
    if (review.get("review_status")!="PASS_TO_REVIEWED_BATCH_AND_FREEZE_AUDIT" or review.get("review_complete") is not True
        or review.get("accepted")!=2 or review.get("semantic_isolation_pass") is not True
        or review.get("external_human_review_claimed") is not False):
        raise RuntimeError("B03 review evidence changed")
    report=load_json(REPORT)
    if (report.get("review_status")!="PASS" or report.get("record_count")!=2 or report.get("accepted")!=2
        or report.get("model_visible_text_changed") is not False or report.get("candidate_provenance_left_immutable") is not True
        or report.get("semantic_guard_review")!="PASS" or report.get("training_authorized") is not False):
        raise RuntimeError("B03 review report changed")
    manifest=load_json(MANIFEST)
    if (manifest.get("status")!="REVIEWED_PASS_PENDING_FREEZE_AUDIT" or manifest.get("batch_blob_sha")!="8166c7f381e501515b1461fcb5d66b232702d1fe"
        or manifest.get("record_count")!=2 or manifest.get("group_counts")!={"sg-b03-03":2}
        or manifest.get("reviewed_by_sidecar") is not True or manifest.get("all_records_accepted") is not True
        or manifest.get("validation_frozen") is not False):
        raise RuntimeError("B03 manifest changed")
    freeze=load_json(FREEZE)
    if (freeze.get("declaration_id")!="V54-B03-VALIDATION-FREEZE-001" or freeze.get("status")!="PENDING_SUCCESSFUL_GOGIT_AUDIT"
        or freeze.get("target_step_id")!="PHASE03-SMOLTALK-V54-B03-VALIDATION-FREEZE-001"
        or freeze.get("integrity_step_id")!="PHASE03-SMOLTALK-V54-B03-VALIDATION-INTEGRITY-001"
        or freeze.get("target_batch_blob_sha")!="8166c7f381e501515b1461fcb5d66b232702d1fe"
        or freeze.get("records")!=2 or freeze.get("group_id")!="sg-b03-03"):
        raise RuntimeError("B03 freeze declaration changed")
    return val

def validate_cross_split(val):
    train=[r for n in TRAIN_NAMES for r in load_jsonl(ROOT/"data/phase-03/train"/n)]
    if len(train)!=107 or len({r["id"] for r in train})!=107 or len({r["group_id"] for r in train})!=29: raise RuntimeError("Canonical TRAIN state changed")
    splits=load_json(SPLITS)["splits"]
    if "sg-b03-03" not in splits["validation"] or "sg-b03-04" not in splits["blind_test"]: raise RuntimeError("B03 split reservation changed")
    ids={r["id"] for r in train}; groups={r["group_id"] for r in train}; tp={p for r in train for p in prompts(r)}
    ih=sum(r["id"] in ids for r in val); gh=sum(r["group_id"] in groups for r in val); ph=sum(p in tp for r in val for p in prompts(r))
    if ih or gh or ph: raise RuntimeError("Cross-split collision detected at freeze gate")
    if BLIND_DIR.exists() and any(p.is_file() and not p.is_symlink() for p in BLIND_DIR.rglob("*")): raise RuntimeError("BLIND TEST text/files exist before authorized authoring")
    return ih,gh,ph

def audit():
    validate_history(); val=validate_evidence(); ih,gh,ph=validate_cross_split(val)
    return dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,"VALIDATION_B03_CANDIDATES":2,
        "CROSS_SPLIT_ID_COLLISIONS":ih,"CROSS_SPLIT_GROUP_COLLISIONS":gh,"EXACT_USER_PROMPT_MATCHES":ph,
        "B03_INDEPENDENT_SIGNOFF":1,"B03_VALIDATION_FROZEN":1,
        "VALIDATION_FROZEN_RECORDS":6,"VALIDATION_BEHAVIORS_FROZEN":3,"TRAINING_AUTHORIZED":0,
    }.items()))

def require_expected_state(m):
    e=dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,"VALIDATION_B03_CANDIDATES":2,
        "CROSS_SPLIT_ID_COLLISIONS":0,"CROSS_SPLIT_GROUP_COLLISIONS":0,"EXACT_USER_PROMPT_MATCHES":0,
        "B03_INDEPENDENT_SIGNOFF":1,"B03_VALIDATION_FROZEN":1,
        "VALIDATION_FROZEN_RECORDS":6,"VALIDATION_BEHAVIORS_FROZEN":3,"TRAINING_AUTHORIZED":0,
    }.items()))
    if m!=e: raise RuntimeError("B03 freeze state differs from expected")

if __name__=="__main__":
    m=audit(); require_expected_state(m); print(MARKER)
    for k,v in m.items(): print("{}: {}".format(k,v))
