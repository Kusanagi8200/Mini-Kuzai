#!/usr/bin/env python3
"""V53 read-only audit for the first repaired-derivative corpus admission.

Validates that exactly one eligibility-ready derivative is approved for future
canonical TRAIN serialization, that its target semantic group is a TRAIN group,
that the reserved record id is unused, and that canonical TRAIN files remain
unchanged at 37 records.

This audit does not serialize data and does not authorize model training.
"""

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

ELIGIBILITY_AUDIT = REPO / "tools/public-audits/smoltalk_v53_eligibility.py"
ELIGIBILITY_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-ELIGIBILITY-001.json"
)
ADMISSION = REPO / "reviews/smoltalk-v53/admissions/V53-ADMIT-001-V51-013.json"
GROUPS = REPO / "data/phase-03/schema/semantic-groups-v0.3.json"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
)

EXPECTED_ID = "p03-train-b08-000001"
EXPECTED_GROUP = "sg-b08-01"
EXPECTED_DERIVATIVE = "V53-DERIV-002-V51-013"
EXPECTED_ELIGIBILITY = "V53-ELIG-002-V51-013"

METRIC_KEYS = {
    "V53_ADMIT_DECISIONS_TOTAL",
    "V53_ADMIT_CORPUS_APPROVED",
    "V53_ADMIT_TARGET_TRAIN",
    "V53_ADMIT_GROUP_VALID",
    "V53_ADMIT_RESERVED_ID_FREE",
    "V53_ADMIT_CANONICAL_TRAIN_RECORDS",
    "V53_ADMIT_SERIALIZED",
    "V53_ADMIT_MODEL_TRAINING_AUTHORIZED",
}


def load_module(path, name):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe V53 admission dependency")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load V53 admission dependency")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe V53 admission JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V53 admission JSON must be an object")
    return value


def validate_eligibility_prerequisite():
    report = load_json(ELIGIBILITY_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id") != "PHASE03-SMOLTALK-V53-ELIGIBILITY-001"
        or report.get("training_authorized") is not False
        or report.get("private_conversation_data_included") is not False
        or metrics.get("V53_ELIG_ADMISSION_READY") != 1
        or metrics.get("V53_ELIG_SEMANTIC_PASS") != 1
        or metrics.get("V53_ELIG_SEMANTIC_BLOCKED") != 1
        or metrics.get("V53_ELIG_TRAIN_APPROVED") != 0
        or metrics.get("V53_ELIG_SPLIT_ASSIGNED") != 0
    ):
        raise RuntimeError("Eligibility history is not the expected prerequisite")

    eligibility = load_module(ELIGIBILITY_AUDIT, "v53_admit_eligibility")
    current = eligibility.audit_metrics()
    eligibility.require_expected_state(current)


def canonical_train_ids():
    identifiers = []
    for path in TRAIN_FILES:
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("Canonical TRAIN file missing or unsafe")
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            identifier = record.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            identifiers.append(identifier)
    if len(identifiers) != 37 or len(set(identifiers)) != 37:
        raise RuntimeError("Canonical TRAIN population is not 37 unique records")
    return identifiers


def validate_group():
    groups = load_json(GROUPS)
    if groups.get("inventory_version") != "0.3":
        raise RuntimeError("Unexpected semantic-group inventory version")
    matches = [
        group for group in groups.get("groups", [])
        if group.get("group_id") == EXPECTED_GROUP
    ]
    if len(matches) != 1:
        raise RuntimeError("Expected admission target group missing or duplicated")
    group = matches[0]
    if (
        group.get("split") != "train"
        or group.get("primary_behavior") != "B08"
        or group.get("scenario_type") != "weak_technical_claim"
    ):
        raise RuntimeError("Admission target group does not match expected TRAIN scope")
    return True


def audit_metrics():
    validate_eligibility_prerequisite()
    identifiers = canonical_train_ids()
    group_valid = validate_group()
    decision = load_json(ADMISSION)

    if (
        decision.get("schema_version") != "v53-admission-decision-0.1"
        or decision.get("decision_id") != "V53-ADMIT-001-V51-013"
        or decision.get("derivative_id") != EXPECTED_DERIVATIVE
        or decision.get("eligibility_id") != EXPECTED_ELIGIBILITY
        or decision.get("decision_status")
        != "APPROVED_FOR_TRAIN_CORPUS_SERIALIZATION"
        or decision.get("corpus_admission_approved") is not True
        or decision.get("target_split") != "train"
        or decision.get("target_group_id") != EXPECTED_GROUP
        or decision.get("target_primary_behavior") != "B08"
        or decision.get("target_scenario_type") != "weak_technical_claim"
        or decision.get("reserved_record_id") != EXPECTED_ID
        or decision.get("canonical_serialization_complete") is not False
        or decision.get("canonical_train_record_count_before") != 37
        or decision.get("canonical_train_record_count_after_decision") != 37
        or decision.get("model_training_authorized") is not False
        or decision.get("tokenizer_frozen") is not False
        or decision.get("architecture_selected") is not False
    ):
        raise RuntimeError("Admission decision state differs from expected")

    requirements = decision.get("serialization_requirements")
    if not isinstance(requirements, dict):
        raise RuntimeError("Admission serialization requirements missing")
    if (
        requirements.get("schema_version") != "0.1"
        or requirements.get("language") != "en"
        or requirements.get("conversation_mode") != "multi_turn"
        or requirements.get("primary_behavior") != "B08"
        or requirements.get("secondary_behaviors") != ["B16"]
        or requirements.get("knowledge_layers") != ["K3", "K4"]
        or requirements.get("knowledge_status") != ["LAB"]
        or requirements.get("difficulty") != 3
        or requirements.get("scenario_type") != "weak_technical_claim"
        or requirements.get("reviewed") is not True
    ):
        raise RuntimeError("Admission serialization requirements changed")

    id_free = EXPECTED_ID not in set(identifiers)
    if not id_free:
        raise RuntimeError("Reserved admission record id is already serialized")

    metrics = {
        "V53_ADMIT_DECISIONS_TOTAL": 1,
        "V53_ADMIT_CORPUS_APPROVED": 1,
        "V53_ADMIT_TARGET_TRAIN": 1,
        "V53_ADMIT_GROUP_VALID": int(group_valid),
        "V53_ADMIT_RESERVED_ID_FREE": int(id_free),
        "V53_ADMIT_CANONICAL_TRAIN_RECORDS": len(identifiers),
        "V53_ADMIT_SERIALIZED": int(decision["canonical_serialization_complete"]),
        "V53_ADMIT_MODEL_TRAINING_AUTHORIZED": int(
            decision["model_training_authorized"]
        ),
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("V53 admission metric key set changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_ADMIT_DECISIONS_TOTAL": 1,
        "V53_ADMIT_CORPUS_APPROVED": 1,
        "V53_ADMIT_TARGET_TRAIN": 1,
        "V53_ADMIT_GROUP_VALID": 1,
        "V53_ADMIT_RESERVED_ID_FREE": 1,
        "V53_ADMIT_CANONICAL_TRAIN_RECORDS": 37,
        "V53_ADMIT_SERIALIZED": 0,
        "V53_ADMIT_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("V53 admission decision differs from expected state")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
