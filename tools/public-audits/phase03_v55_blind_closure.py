#!/usr/bin/env python3
"""Global closure audit for Phase 03 V55 BLIND TEST.

The audit revalidates the frozen controlled corpus and all 18 V55 BLIND freeze
histories. It closes the evaluation-data preparation boundary only; tokenizer,
architecture, training-mixture and model-training authorization remain false.
"""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
ENGINE_PATH=ROOT/"tools/phase03_v55_blind_engine.py"
SOURCE_BLIND="Mini-Kuzai Phase 03 designed blind-test corpus"

spec=importlib.util.spec_from_file_location("phase03_v55_blind_engine_closure",ENGINE_PATH)
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

def verify_all_freezes(master):
    for cfg in master["behaviors"]:
        step=cfg["freeze_step_id"]
        report=engine.history_report(step)
        if report is None:
            raise RuntimeError("Missing BLIND freeze history for "+cfg["behavior"])
        if report.get("step_id")!=step or report.get("source")!=SOURCE_BLIND:
            raise RuntimeError("BLIND freeze metadata mismatch for "+cfg["behavior"])
        if report.get("semantic_validation_complete") is not True:
            raise RuntimeError("VALIDATION completion flag missing in "+cfg["behavior"])
        if report.get("training_authorized") is not False:
            raise RuntimeError("BLIND freeze authorizes training for "+cfg["behavior"])
        expected={
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
            "CROSS_SPLIT_ID_COLLISIONS":0,
            "CROSS_SPLIT_GROUP_COLLISIONS":0,
            "EXACT_USER_PROMPT_MATCHES":0,
            "TRAINING_AUTHORIZED":0,
        }
        metrics=report.get("metrics",{})
        for key,value in expected.items():
            if metrics.get(key)!=value:
                raise RuntimeError(
                    "{} freeze metric mismatch: {} expected {} got {}".format(
                        cfg["behavior"],key,value,metrics.get(key)
                    )
                )

def audit():
    master=engine.load_master()
    if (master.get("status")!="FROZEN_PENDING_GLOBAL_CLOSURE"
        or master.get("freeze_complete") is not True
        or master.get("freeze_complete_step_id")!="PHASE03-SMOLTALK-V55-B18-BLIND-FREEZE-001"
        or master.get("global_blind_closure_complete") is not False
        or master.get("training_authorized") is not False):
        raise RuntimeError("Unexpected V55 master state before global BLIND closure")

    engine.verify_validation_closure()
    verify_all_freezes(master)

    blind=engine.canonical_blind_rows(master)
    cross_id,cross_group,cross_prompt=engine.validate_global_split(master,blind)
    train,validation=engine.reference_rows()

    split=engine.load_json(engine.SPLITS)["splits"]
    train_groups={row["group_id"] for row in train}
    validation_groups={row["group_id"] for row in validation}
    blind_groups={row["group_id"] for row in blind}
    if train_groups!=set(split["train"]):
        raise RuntimeError("TRAIN semantic-group coverage changed")
    if validation_groups!=set(split["validation"]):
        raise RuntimeError("VALIDATION semantic-group coverage changed")
    if blind_groups!=set(split["blind_test"]):
        raise RuntimeError("BLIND semantic-group coverage changed")

    validation_prompts=[p for row in validation for p in engine.prompts(row)]
    if len(validation_prompts)!=len(set(validation_prompts)):
        raise RuntimeError("Duplicate normalized user prompts inside VALIDATION")

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
        "BLIND_TEST_RECORDS":len(blind),
        "BLIND_TEST_GROUPS_RESERVED":len(blind_groups),
        "BLIND_TEST_RECORDS_FROZEN":36,
        "BLIND_BEHAVIORS_FROZEN":18,
        "CROSS_SPLIT_ID_COLLISIONS":cross_id,
        "CROSS_SPLIT_GROUP_COLLISIONS":cross_group,
        "EXACT_USER_PROMPT_MATCHES":cross_prompt,
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
        "BLIND_TEST_RECORDS":36,
        "BLIND_TEST_GROUPS_RESERVED":18,
        "BLIND_TEST_RECORDS_FROZEN":36,
        "BLIND_BEHAVIORS_FROZEN":18,
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "SEMANTIC_VALIDATION_COMPLETE":1,
        "BLIND_AUTHORING_AUTHORIZED":1,
        "TRAINING_AUTHORIZED":0,
    }.items()))
    if metrics!=expected:
        raise RuntimeError("Global BLIND closure state differs from expected")

if __name__=="__main__":
    metrics=audit()
    require_expected_state(metrics)
    print(MARKER)
    for key,value in metrics.items():
        print("{}: {}".format(key,value))
