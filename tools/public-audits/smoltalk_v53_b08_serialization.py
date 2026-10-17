#!/usr/bin/env python3
"""V53 read-only audit for canonical serialization of the first admitted derivative.

Validates the historical admission decision, the B08 v0.1/v0.2 serialization,
the metadata-only correction, semantic group assignment, source-lineage message
identity, and the expanded 38-record canonical TRAIN population.

This audit does not authorize model training and does not declare B08 complete.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

ADMISSION_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-ADMISSION-DECISION-001.json"
)
DERIVATIVE = (
    REPO / "reviews/smoltalk-v53/derivatives/V53-DERIV-002-V51-013.json"
)
B08_V01 = REPO / "data/phase-03/train/train-batch-b08-v0.1.jsonl"
B08_V02 = REPO / "data/phase-03/train/train-batch-b08-v0.2.jsonl"
B08_REVIEW = REPO / "data/phase-03/reports/train-batch-b08-v0.2-review.json"
B08_MANIFEST = (
    REPO / "data/phase-03/manifests/train-batch-b08-v0.2-manifest.json"
)
GROUPS = REPO / "data/phase-03/schema/semantic-groups-v0.3.json"
EXCLUSION_MAP = (
    REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"
)

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.2.jsonl",
)

EXPECTED_ID = "p03-train-b08-000001"
EXPECTED_GROUP = "sg-b08-01"

METRIC_KEYS = {
    "V53_B08_SERIALIZED_RECORDS",
    "V53_B08_REVIEWED_RECORDS",
    "V53_B08_METADATA_CORRECTIONS",
    "V53_B08_MODEL_VISIBLE_CHANGES",
    "V53_B08_GROUP_TRAIN_VALID",
    "V53_B08_RESERVED_OVERLAP",
    "V53_B08_CANONICAL_TRAIN_RECORDS",
    "V53_B08_GROUP_CURRENT",
    "V53_B08_GROUP_PLANNED",
    "V53_B08_TRAIN_COMPLETE",
    "V53_B08_MODEL_TRAINING_AUTHORIZED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe V53 B08 dependency")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl_one(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B08 JSONL")
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("B08 serialization must contain exactly one record")
    value = json.loads(lines[0])
    if not isinstance(value, dict):
        raise RuntimeError("B08 record must be a JSON object")
    return value


def validate_admission_history():
    report = load_json(ADMISSION_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id") != "PHASE03-SMOLTALK-V53-ADMISSION-DECISION-001"
        or report.get("training_authorized") is not False
        or report.get("private_conversation_data_included") is not False
        or metrics.get("V53_ADMIT_DECISIONS_TOTAL") != 1
        or metrics.get("V53_ADMIT_CORPUS_APPROVED") != 1
        or metrics.get("V53_ADMIT_TARGET_TRAIN") != 1
        or metrics.get("V53_ADMIT_GROUP_VALID") != 1
        or metrics.get("V53_ADMIT_RESERVED_ID_FREE") != 1
        or metrics.get("V53_ADMIT_CANONICAL_TRAIN_RECORDS") != 37
        or metrics.get("V53_ADMIT_SERIALIZED") != 0
        or metrics.get("V53_ADMIT_MODEL_TRAINING_AUTHORIZED") != 0
    ):
        raise RuntimeError("Admission history is not the expected prerequisite")


def validate_group_and_reserved_scope():
    groups = load_json(GROUPS)
    matches = [
        group for group in groups.get("groups", [])
        if group.get("group_id") == EXPECTED_GROUP
    ]
    if len(matches) != 1:
        raise RuntimeError("B08 target group missing or duplicated")
    group = matches[0]
    if (
        group.get("split") != "train"
        or group.get("primary_behavior") != "B08"
        or group.get("scenario_type") != "weak_technical_claim"
    ):
        raise RuntimeError("B08 target group changed")

    exclusion = load_json(EXCLUSION_MAP)
    block = exclusion.get("behaviors", {}).get("B08", {})
    validation = {
        item.get("group_id"): item.get("scenario_type")
        for item in block.get("reserved_validation_groups", [])
    }
    blind = {
        item.get("group_id"): item.get("scenario_type")
        for item in block.get("reserved_blind_test_groups", [])
    }
    if validation.get("sg-b08-03") != "unsupported_conclusion":
        raise RuntimeError("B08 reserved validation scope changed")
    if blind.get("sg-b08-04") != "social_pressure_agreement":
        raise RuntimeError("B08 reserved blind scope changed")
    return True


def validate_record(record, reviewed):
    if (
        record.get("schema_version") != "0.1"
        or record.get("id") != EXPECTED_ID
        or record.get("group_id") != EXPECTED_GROUP
        or record.get("split") != "train"
        or record.get("language") != "en"
        or record.get("conversation_mode") != "multi_turn"
        or record.get("primary_behavior") != "B08"
        or record.get("secondary_behaviors") != ["B16"]
        or record.get("knowledge_layers") != ["K3", "K4"]
        or record.get("difficulty") != 3
        or record.get("scenario_type") != "weak_technical_claim"
    ):
        raise RuntimeError("B08 canonical record structure changed")

    expected_status = ["VOLATILE"] if reviewed else ["LAB"]
    if record.get("knowledge_status") != expected_status:
        raise RuntimeError("B08 knowledge-status review state changed")

    messages = record.get("messages")
    if (
        not isinstance(messages, list)
        or len(messages) != 6
        or [m.get("role") for m in messages] != ["user", "assistant"] * 3
    ):
        raise RuntimeError("B08 message structure invalid")

    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        raise RuntimeError("B08 provenance missing")
    if (
        provenance.get("source") != "HuggingFaceTB/smol-smoltalk"
        or provenance.get("authoring_method") != "human_rewrite"
        or provenance.get("source_derivative")
        != "reviews/smoltalk-v53/derivatives/V53-DERIV-002-V51-013.json"
        or provenance.get("source_content_sha256")
        != "566e0b8c4ed792cc76ad0646a6295b05adab7a8caf37e8b91483982fb80e00c3"
        or provenance.get("admission_decision") != "V53-ADMIT-001-V51-013"
    ):
        raise RuntimeError("B08 provenance lineage changed")

    if reviewed:
        if (
            provenance.get("reviewed") is not True
            or provenance.get("review_decision")
            != "ACCEPT_AFTER_METADATA_CORRECTION"
        ):
            raise RuntimeError("Reviewed B08 provenance status invalid")
    else:
        if provenance.get("reviewed") is not False:
            raise RuntimeError("Initial B08 record must remain unreviewed")

    return messages


def canonical_ids():
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
    if len(identifiers) != 38 or len(set(identifiers)) != 38:
        raise RuntimeError("Canonical TRAIN population is not 38 unique records")
    if identifiers.count(EXPECTED_ID) != 1:
        raise RuntimeError("Canonical B08 record id must appear exactly once")
    return identifiers


def audit_metrics():
    validate_admission_history()
    group_valid = validate_group_and_reserved_scope()

    source = load_jsonl_one(B08_V01)
    target = load_jsonl_one(B08_V02)
    source_messages = validate_record(source, reviewed=False)
    target_messages = validate_record(target, reviewed=True)

    if source_messages != target_messages:
        raise RuntimeError("Model-visible B08 text changed during metadata review")

    derivative = load_json(DERIVATIVE)
    expected_messages = [
        {"role": message["role"], "content": message["content"]}
        for message in derivative.get("messages", [])
    ]
    if target_messages != expected_messages:
        raise RuntimeError("Canonical B08 messages differ from reviewed derivative")

    review = load_json(B08_REVIEW)
    if (
        review.get("review_status") != "PASS"
        or review.get("record_count") != 1
        or review.get("accepted_after_metadata_correction") != 1
        or review.get("rejected") != 0
        or review.get("model_visible_text_changed") is not False
        or review.get("semantic_guard_review") != "PASS"
        or review.get("reserved_validation_overlap") is not False
        or review.get("reserved_blind_test_overlap") is not False
        or review.get("all_serialized_records_reviewed") is not True
        or review.get("b08_current_group_count") != 1
        or review.get("b08_planned_group_variants") != 4
        or review.get("b08_train_complete") is not False
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B08 review report differs from expected state")

    correction = review.get("metadata_corrections", {}).get("knowledge_status", {})
    if correction.get("from") != ["LAB"] or correction.get("to") != ["VOLATILE"]:
        raise RuntimeError("Expected B08 metadata correction missing")

    manifest = load_json(B08_MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS"
        or manifest.get("record_count") != 1
        or manifest.get("group_counts") != {"sg-b08-01": 1}
        or manifest.get("review_decision_counts")
        != {"ACCEPT_AFTER_METADATA_CORRECTION": 1}
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("semantic_leakage_remaining") is not False
        or manifest.get("model_visible_text_changed") is not False
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("b08_current_group_count") != 1
        or manifest.get("b08_planned_group_variants") != 4
        or manifest.get("b08_remaining_planned_variants") != 3
        or manifest.get("b08_train_complete") is not False
        or manifest.get("canonical_train_record_count_after") != 38
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B08 reviewed manifest differs from expected state")

    ids = canonical_ids()

    metrics = {
        "V53_B08_SERIALIZED_RECORDS": 1,
        "V53_B08_REVIEWED_RECORDS": 1,
        "V53_B08_METADATA_CORRECTIONS": 1,
        "V53_B08_MODEL_VISIBLE_CHANGES": 0,
        "V53_B08_GROUP_TRAIN_VALID": int(group_valid),
        "V53_B08_RESERVED_OVERLAP": 0,
        "V53_B08_CANONICAL_TRAIN_RECORDS": len(ids),
        "V53_B08_GROUP_CURRENT": 1,
        "V53_B08_GROUP_PLANNED": 4,
        "V53_B08_TRAIN_COMPLETE": 0,
        "V53_B08_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("V53 B08 metric key set changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B08_SERIALIZED_RECORDS": 1,
        "V53_B08_REVIEWED_RECORDS": 1,
        "V53_B08_METADATA_CORRECTIONS": 1,
        "V53_B08_MODEL_VISIBLE_CHANGES": 0,
        "V53_B08_GROUP_TRAIN_VALID": 1,
        "V53_B08_RESERVED_OVERLAP": 0,
        "V53_B08_CANONICAL_TRAIN_RECORDS": 38,
        "V53_B08_GROUP_CURRENT": 1,
        "V53_B08_GROUP_PLANNED": 4,
        "V53_B08_TRAIN_COMPLETE": 0,
        "V53_B08_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("V53 B08 canonical serialization differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
