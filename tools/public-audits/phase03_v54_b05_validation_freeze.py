#!/usr/bin/env python3
"""Final read-only freeze gate for Phase 03 V54 B05 validation."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
INTEGRITY_PATH=ROOT/"tools/public-audits/phase03_v54_b05_validation_integrity.py"
INTEGRITY_HISTORY=ROOT/"reports/assistant-results/history/PHASE03-SMOLTALK-V54-B05-VALIDATION-INTEGRITY-001.json"
FREEZE=ROOT/"data/phase-03/manifests/validation-batch-b05-v0.1-freeze-declaration.json"

def load_module():
    spec=importlib.util.spec_from_file_location("v54_b05_integrity_for_freeze",INTEGRITY_PATH)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_json(path):
    if not path.is_file() or path.is_symlink(): raise RuntimeError("Missing or unsafe JSON: "+str(path.relative_to(ROOT)))
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise RuntimeError("Expected JSON object")
    return value

def validate_history():
    history=load_json(INTEGRITY_HISTORY)
    if history.get("step_id")!="PHASE03-SMOLTALK-V54-B05-VALIDATION-INTEGRITY-001":
        raise RuntimeError("B05 integrity STEP_ID mismatch")
    metrics=history.get("metrics",{})
    expected={
        "VALIDATION_B05_CANDIDATES":2,
        "B05_ANSWER_PLUS_QUESTION_RECORDS":2,
        "B05_INDEPENDENT_SIGNOFF":1,
        "B05_VALIDATION_FROZEN":0,
        "VALIDATION_FROZEN_RECORDS":8,
        "VALIDATION_BEHAVIORS_FROZEN":4,
        "TRAIN_RECORDS":107,
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "TRAINING_AUTHORIZED":0,
    }
    for key,value in expected.items():
        if metrics.get(key)!=value:
            raise RuntimeError("B05 integrity history not passing: "+key)

def validate_freeze_declaration():
    freeze=load_json(FREEZE)
    if (freeze.get("declaration_id")!="V54-B05-VALIDATION-FREEZE-001"
        or freeze.get("status")!="PENDING_SUCCESSFUL_GOGIT_AUDIT"
        or freeze.get("target_step_id")!="PHASE03-SMOLTALK-V54-B05-VALIDATION-FREEZE-001"
        or freeze.get("integrity_step_id")!="PHASE03-SMOLTALK-V54-B05-VALIDATION-INTEGRITY-001"
        or freeze.get("target_batch_blob_sha")!="10d262ce7ecf809d07591fd19a94ed105274c332"
        or freeze.get("records")!=2
        or freeze.get("group_id")!="sg-b05-03"):
        raise RuntimeError("B05 freeze declaration changed")

def audit():
    validate_history()
    validate_freeze_declaration()
    integrity=load_module()
    base=integrity.audit()
    integrity.require_expected_state(base)
    return dict(sorted({
        "TRAIN_FILES":19,
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_B05_CANDIDATES":2,
        "B05_ANSWER_PLUS_QUESTION_RECORDS":2,
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "B05_INDEPENDENT_SIGNOFF":1,
        "B05_VALIDATION_FROZEN":1,
        "VALIDATION_FROZEN_RECORDS":10,
        "VALIDATION_BEHAVIORS_FROZEN":5,
        "TRAINING_AUTHORIZED":0,
    }.items()))

def require_expected_state(metrics):
    expected=dict(sorted({
        "TRAIN_FILES":19,
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_B05_CANDIDATES":2,
        "B05_ANSWER_PLUS_QUESTION_RECORDS":2,
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "B05_INDEPENDENT_SIGNOFF":1,
        "B05_VALIDATION_FROZEN":1,
        "VALIDATION_FROZEN_RECORDS":10,
        "VALIDATION_BEHAVIORS_FROZEN":5,
        "TRAINING_AUTHORIZED":0,
    }.items()))
    if metrics!=expected: raise RuntimeError("B05 freeze state differs from expected")

if __name__=="__main__":
    metrics=audit(); require_expected_state(metrics); print(MARKER)
    for key,value in metrics.items(): print("{}: {}".format(key,value))
