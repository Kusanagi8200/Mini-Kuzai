#!/usr/bin/env python3
"""Final read-only freeze gate for Phase 03 V54 B02 validation."""
import json
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
V01=ROOT/"data/phase-03/validation/validation-batch-b02-v0.1.jsonl"
V02=ROOT/"data/phase-03/validation/validation-batch-b02-v0.2.jsonl"
V03=ROOT/"data/phase-03/validation/validation-batch-b02-v0.3.jsonl"
REVIEW1=ROOT/"reviews/phase-03-v54/B02-INDEPENDENT-REVIEW-RESULT-001.json"
REVIEW2=ROOT/"reviews/phase-03-v54/B02-INDEPENDENT-REVIEW-RESULT-002.json"
REPORT=ROOT/"data/phase-03/reports/validation-batch-b02-v0.3-review.json"
MANIFEST=ROOT/"data/phase-03/manifests/validation-batch-b02-v0.3-manifest.json"
FREEZE=ROOT/"data/phase-03/manifests/validation-batch-b02-v0.3-freeze-declaration.json"
SPLITS=ROOT/"data/phase-03/schema/semantic-group-split-manifest-v0.1.json"
B01_HISTORY=ROOT/"reports/assistant-results/history/PHASE03-SMOLTALK-V54-B01-VALIDATION-FREEZE-001.json"
INTEGRITY_HISTORY=ROOT/"reports/assistant-results/history/PHASE03-SMOLTALK-V54-B02-VALIDATION-INTEGRITY-001.json"
BLIND_DIR=ROOT/"data/phase-03/blind-test"
TRAIN_NAMES=["train-pilot-v0.2.jsonl",*["train-batch-b{:02d}-{}.jsonl".format(n,{8:"v0.5",12:"v0.3"}.get(n,"v0.2")) for n in range(1,19)]]
IDS={"p03-val-b02-000001","p03-val-b02-000002"}

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
    b01=load_json(B01_HISTORY).get("metrics",{})
    if b01.get("B01_VALIDATION_FROZEN")!=1: raise RuntimeError("B01 freeze prerequisite lost")
    integ=load_json(INTEGRITY_HISTORY)
    if integ.get("step_id")!="PHASE03-SMOLTALK-V54-B02-VALIDATION-INTEGRITY-001":
        raise RuntimeError("B02 integrity STEP_ID mismatch")
    m=integ.get("metrics",{})
    if (m.get("B02_INDEPENDENT_SIGNOFF")!=1 or m.get("B02_VALIDATION_FROZEN")!=0
        or m.get("VALIDATION_B02_CANDIDATES")!=2 or m.get("TRAIN_RECORDS")!=107
        or m.get("CROSS_SPLIT_ID_COLLISIONS")!=0 or m.get("CROSS_SPLIT_GROUP_COLLISIONS")!=0
        or m.get("EXACT_USER_PROMPT_MATCHES")!=0):
        raise RuntimeError("B02 integrity history not passing")

def validate_transitions():
    a={r["id"]:r for r in load_jsonl(V01)}
    b={r["id"]:r for r in load_jsonl(V02)}
    c={r["id"]:r for r in load_jsonl(V03)}
    if set(a)!=IDS or set(b)!=IDS or set(c)!=IDS: raise RuntimeError("B02 IDs changed")
    changed=[]
    for identifier in sorted(IDS):
        if a[identifier]["messages"]!=b[identifier]["messages"]: changed.append(identifier)
        bb=json.loads(json.dumps(b[identifier])); cc=json.loads(json.dumps(c[identifier]))
        bp=bb.pop("provenance"); cp=cc.pop("provenance")
        if bb!=cc: raise RuntimeError("v0.2 -> v0.3 changed outside provenance")
        if cp.get("reviewed") is not True or cp.get("review_decision")!="ACCEPT":
            raise RuntimeError("v0.3 reviewed provenance invalid")
        if cp.get("independent_review_id")!="V54-B02-INDEPENDENT-REVIEW-002":
            raise RuntimeError("v0.3 review reference changed")
        if bp.get("reviewed") is not False: raise RuntimeError("v0.2 must remain pending historical candidate")
    if changed!=["p03-val-b02-000002"]: raise RuntimeError("Unexpected corrected record set")
    return list(c.values())

def validate_evidence():
    r1=load_json(REVIEW1)
    if (r1.get("review_status")!="REVISE_AND_REREVIEW" or r1.get("accepted")!=1
        or r1.get("revise")!=1 or r1.get("semantic_isolation_pass") is not False):
        raise RuntimeError("Initial B02 review evidence changed")
    r2=load_json(REVIEW2)
    if (r2.get("review_status")!="PASS_TO_REVIEWED_BATCH_AND_FREEZE_AUDIT"
        or r2.get("review_complete") is not True or r2.get("accepted")!=2
        or r2.get("revise")!=0 or r2.get("semantic_isolation_pass") is not True
        or r2.get("external_human_review_claimed") is not False):
        raise RuntimeError("Final B02 review evidence changed")
    report=load_json(REPORT)
    if (report.get("review_status")!="PASS" or report.get("accepted_without_change")!=1
        or report.get("accepted_after_correction")!=1
        or report.get("corrected_record_ids")!=["p03-val-b02-000002"]
        or report.get("final_transition_v0_2_to_v0_3_model_visible_changed") is not False
        or report.get("semantic_guard_review")!="PASS"
        or report.get("training_authorized") is not False):
        raise RuntimeError("B02 review report changed")
    manifest=load_json(MANIFEST)
    if (manifest.get("status")!="REVIEWED_PASS_PENDING_FREEZE_AUDIT"
        or manifest.get("record_count")!=2 or manifest.get("group_counts")!={"sg-b02-03":2}
        or manifest.get("corrected_from_v0_1")!=1
        or manifest.get("all_records_accepted") is not True
        or manifest.get("validation_frozen") is not False):
        raise RuntimeError("B02 manifest changed")
    freeze=load_json(FREEZE)
    if (freeze.get("declaration_id")!="V54-B02-VALIDATION-FREEZE-001"
        or freeze.get("status")!="PENDING_SUCCESSFUL_GOGIT_AUDIT"
        or freeze.get("target_step_id")!="PHASE03-SMOLTALK-V54-B02-VALIDATION-FREEZE-001"
        or freeze.get("integrity_step_id")!="PHASE03-SMOLTALK-V54-B02-VALIDATION-INTEGRITY-001"
        or freeze.get("target_batch_blob_sha")!="b7875fd2b3adb138d59a7c442b4d2b38e7324b47"
        or freeze.get("records")!=2 or freeze.get("group_id")!="sg-b02-03"):
        raise RuntimeError("B02 freeze declaration changed")

def validate_cross_split(val):
    train=[r for n in TRAIN_NAMES for r in load_jsonl(ROOT/"data/phase-03/train"/n)]
    if len(train)!=107 or len({r["id"] for r in train})!=107 or len({r["group_id"] for r in train})!=29:
        raise RuntimeError("Canonical TRAIN state changed")
    splits=load_json(SPLITS)["splits"]
    if "sg-b02-03" not in splits["validation"] or "sg-b02-04" not in splits["blind_test"]:
        raise RuntimeError("B02 split reservation changed")
    ids={r["id"] for r in train}; groups={r["group_id"] for r in train}; tp={p for r in train for p in prompts(r)}
    ih=sum(r["id"] in ids for r in val); gh=sum(r["group_id"] in groups for r in val); ph=sum(p in tp for r in val for p in prompts(r))
    if ih or gh or ph: raise RuntimeError("Cross-split collision detected at freeze gate")
    if BLIND_DIR.exists() and any(p.is_file() and not p.is_symlink() for p in BLIND_DIR.rglob("*")):
        raise RuntimeError("BLIND TEST text/files exist before authorized authoring")
    return ih,gh,ph

def audit():
    validate_history(); val=validate_transitions(); validate_evidence(); ih,gh,ph=validate_cross_split(val)
    return dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_B02_CANDIDATES":2,
        "CROSS_SPLIT_ID_COLLISIONS":ih,"CROSS_SPLIT_GROUP_COLLISIONS":gh,
        "EXACT_USER_PROMPT_MATCHES":ph,
        "B02_INDEPENDENT_SIGNOFF":1,"B02_VALIDATION_FROZEN":1,
        "VALIDATION_FROZEN_RECORDS":4,"VALIDATION_BEHAVIORS_FROZEN":2,
        "TRAINING_AUTHORIZED":0,
    }.items()))

def require_expected_state(m):
    e=dict(sorted({
        "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
        "VALIDATION_B02_CANDIDATES":2,"CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,"EXACT_USER_PROMPT_MATCHES":0,
        "B02_INDEPENDENT_SIGNOFF":1,"B02_VALIDATION_FROZEN":1,
        "VALIDATION_FROZEN_RECORDS":4,"VALIDATION_BEHAVIORS_FROZEN":2,
        "TRAINING_AUTHORIZED":0,
    }.items()))
    if m!=e: raise RuntimeError("B02 freeze state differs from expected")

if __name__=="__main__":
    m=audit(); require_expected_state(m); print(MARKER)
    for k,v in m.items(): print("{}: {}".format(k,v))
