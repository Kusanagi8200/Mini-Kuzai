#!/usr/bin/env python3
"""V53 read-only audit for canonical B12 serialization of derivative-003.

Validates the published admission decision, frozen B12 semantic scope,
v0.1/v0.2 serialization lineage, exact model-visible equality with the
independently reviewed derivative, review/manifest state, and the resulting
46-record canonical TRAIN population.

This audit does not complete B12 and does not authorize model training.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

ADMISSION_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-DERIV003-ADMISSION-001.json"
)
ADMISSION = (
    REPO / "reviews/smoltalk-v53/admissions/V53-ADMIT-002-V51-002.json"
)
DERIVATIVE = (
    REPO / "reviews/smoltalk-v53/a-low-wave2/V53-DERIV-003-V51-002.json"
)
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"

BATCH_V01 = REPO / "data/phase-03/train/train-batch-b12-v0.1.jsonl"
BATCH_V02 = REPO / "data/phase-03/train/train-batch-b12-v0.2.jsonl"
MANIFEST_V01 = (
    REPO / "data/phase-03/manifests/train-batch-b12-v0.1-manifest.json"
)
REVIEW_V02 = REPO / "data/phase-03/reports/train-batch-b12-v0.2-review.json"
MANIFEST_V02 = (
    REPO / "data/phase-03/manifests/train-batch-b12-v0.2-manifest.json"
)

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.5.jsonl",
    REPO / "data/phase-03/train/train-batch-b12-v0.2.jsonl",
)

EXPECTED_ID = "p03-train-b12-000001"

METRIC_KEYS = {
    "V53_B12_SERIALIZED_RECORDS",
    "V53_B12_REVIEWED_RECORDS",
    "V53_B12_METADATA_CORRECTIONS",
    "V53_B12_MODEL_VISIBLE_CHANGES",
    "V53_B12_GROUP_TRAIN_VALID",
    "V53_B12_RESERVED_OVERLAP",
    "V53_B12_CANONICAL_TRAIN_RECORDS",
    "V53_B12_SG01_CURRENT",
    "V53_B12_SG02_CURRENT",
    "V53_B12_TRAIN_COMPLETE",
    "V53_B12_MODEL_TRAINING_AUTHORIZED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B12 serialization JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B12 serialization JSONL")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise RuntimeError("Expected JSONL object")
        rows.append(row)
    return rows


def validate_admission_prerequisite():
    report = load_json(ADMISSION_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id")
        != "PHASE03-SMOLTALK-V53-DERIV003-ADMISSION-001"
        or report.get("training_authorized") is not False
        or report.get("private_conversation_data_included") is not False
        or metrics.get("V53_D3A_DECISIONS_TOTAL") != 1
        or metrics.get("V53_D3A_CORPUS_APPROVED") != 1
        or metrics.get("V53_D3A_TARGET_TRAIN") != 1
        or metrics.get("V53_D3A_GROUP_VALID") != 1
        or metrics.get("V53_D3A_RESERVED_ID_FREE") != 1
        or metrics.get("V53_D3A_CANONICAL_TRAIN_RECORDS") != 45
        or metrics.get("V53_D3A_SERIALIZED") != 0
        or metrics.get("V53_D3A_MODEL_TRAINING_AUTHORIZED") != 0
    ):
        raise RuntimeError("Derivative-003 admission prerequisite changed")

    decision = load_json(ADMISSION)
    if (
        decision.get("decision_id") != "V53-ADMIT-002-V51-002"
        or decision.get("derivative_id") != "V53-DERIV-003-V51-002"
        or decision.get("eligibility_id") != "V53-ELIG-003-V51-002"
        or decision.get("corpus_admission_approved") is not True
        or decision.get("target_split") != "train"
        or decision.get("target_group_id") != "sg-b12-01"
        or decision.get("target_primary_behavior") != "B12"
        or decision.get("target_scenario_type") != "alternative_generation"
        or decision.get("reserved_record_id") != EXPECTED_ID
        or decision.get("canonical_serialization_complete") is not False
        or decision.get("canonical_train_record_count_before") != 45
        or decision.get("canonical_train_record_count_after_decision") != 45
        or decision.get("model_training_authorized") is not False
    ):
        raise RuntimeError("Derivative-003 admission decision changed")


def validate_semantic_scope():
    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B12", {})
    train = {
        row.get("group_id"): row
        for row in block.get("train_groups", [])
    }
    validation = {
        row.get("group_id"): row
        for row in block.get("reserved_validation_groups", [])
    }
    blind = {
        row.get("group_id"): row
        for row in block.get("reserved_blind_test_groups", [])
    }
    if train.get("sg-b12-01", {}).get("scenario_type") != "alternative_generation":
        raise RuntimeError("B12 sg-b12-01 scope changed")
    if train.get("sg-b12-02", {}).get("scenario_type") != "conceptual_combination":
        raise RuntimeError("B12 sg-b12-02 scope changed")
    if (
        validation.get("sg-b12-03", {}).get("scenario_type")
        != "creative_hypothesis_epistemic_control"
    ):
        raise RuntimeError("B12 reserved validation scope changed")
    if blind.get("sg-b12-04", {}).get("scenario_type") != "creative_under_constraints":
        raise RuntimeError("B12 reserved blind scope changed")


def expected_messages():
    derivative = load_json(DERIVATIVE)
    if (
        derivative.get("derivative_id") != "V53-DERIV-003-V51-002"
        or derivative.get("training_approved") is not False
        or derivative.get("dataset_split_assigned") is not False
    ):
        raise RuntimeError("Derivative-003 source state changed")
    messages = derivative.get("messages")
    if (
        not isinstance(messages, list)
        or len(messages) != 6
        or [row.get("role") for row in messages] != ["user", "assistant"] * 3
    ):
        raise RuntimeError("Derivative-003 messages changed")
    return [
        {"role": row["role"], "content": row["content"]}
        for row in messages
    ]


def validate_serialized_record(row, reviewed, decision):
    if (
        row.get("schema_version") != "0.1"
        or row.get("id") != EXPECTED_ID
        or row.get("group_id") != "sg-b12-01"
        or row.get("split") != "train"
        or row.get("language") != "en"
        or row.get("conversation_mode") != "multi_turn"
        or row.get("primary_behavior") != "B12"
        or row.get("secondary_behaviors") != ["B16"]
        or row.get("knowledge_layers") != ["K3", "K4"]
        or row.get("knowledge_status") != ["LAB"]
        or row.get("difficulty") != 2
        or row.get("scenario_type") != "alternative_generation"
        or row.get("messages") != expected_messages()
    ):
        raise RuntimeError("B12 serialized record differs from expected")

    provenance = row.get("provenance", {})
    if (
        provenance.get("source") != "HuggingFaceTB/smol-smoltalk"
        or provenance.get("authoring_method") != "human_rewrite"
        or provenance.get("reviewed") is not reviewed
        or provenance.get("review_decision") != decision
        or provenance.get("source_derivative")
        != "reviews/smoltalk-v53/a-low-wave2/V53-DERIV-003-V51-002.json"
        or provenance.get("source_content_sha256")
        != "383f5926f407ae183de348a6aae660e952a4e03887ba2ed275d259969e23fc9a"
        or provenance.get("admission_decision") != "V53-ADMIT-002-V51-002"
    ):
        raise RuntimeError("B12 provenance differs from expected")


def canonical_count():
    identifiers = []
    for path in TRAIN_FILES:
        for row in load_jsonl(path):
            identifier = row.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            identifiers.append(identifier)
    if len(identifiers) != 46 or len(set(identifiers)) != 46:
        raise RuntimeError("Canonical TRAIN population is not 46 unique records")
    if identifiers.count(EXPECTED_ID) != 1:
        raise RuntimeError("B12 serialized record must appear exactly once")
    return len(identifiers)


def audit_metrics():
    validate_admission_prerequisite()
    validate_semantic_scope()

    v01 = load_jsonl(BATCH_V01)
    v02 = load_jsonl(BATCH_V02)
    if len(v01) != 1 or len(v02) != 1:
        raise RuntimeError("B12 v0.1/v0.2 must each contain exactly one record")

    validate_serialized_record(v01[0], False, "PENDING_CANONICAL_REVIEW")
    validate_serialized_record(v02[0], True, "ACCEPT")

    if v01[0].get("messages") != v02[0].get("messages"):
        raise RuntimeError("B12 model-visible messages changed between v0.1 and v0.2")

    manifest01 = load_json(MANIFEST_V01)
    if (
        manifest01.get("status") != "STRUCTURALLY_VALID_UNREVIEWED"
        or manifest01.get("record_count") != 1
        or manifest01.get("group_counts") != {"sg-b12-01": 1}
        or manifest01.get("reserved_record_id") != EXPECTED_ID
        or manifest01.get("all_records_reviewed") is not False
        or manifest01.get("manual_review_required") is not True
        or manifest01.get("b12_train_complete") is not False
        or manifest01.get("training_authorized") is not False
    ):
        raise RuntimeError("B12 v0.1 manifest changed")

    review = load_json(REVIEW_V02)
    if (
        review.get("review_status") != "PASS"
        or review.get("record_count") != 1
        or review.get("accepted_without_change") != 1
        or review.get("accepted_after_metadata_correction") != 0
        or review.get("rejected") != 0
        or review.get("model_visible_text_changed") is not False
        or review.get("metadata_corrections") != {}
        or review.get("semantic_guard_review") != "PASS"
        or review.get("reserved_validation_overlap") is not False
        or review.get("reserved_blind_test_overlap") is not False
        or review.get("all_serialized_records_reviewed") is not True
        or review.get("b12_sg01_current") != 1
        or review.get("b12_sg02_current") != 0
        or review.get("b12_train_complete") is not False
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B12 v0.2 review changed")

    manifest02 = load_json(MANIFEST_V02)
    if (
        manifest02.get("status") != "REVIEWED_PASS"
        or manifest02.get("record_count") != 1
        or manifest02.get("group_counts") != {"sg-b12-01": 1}
        or manifest02.get("review_decision_counts") != {"ACCEPT": 1}
        or manifest02.get("semantic_guard_review") != "PASS"
        or manifest02.get("semantic_leakage_remaining") is not False
        or manifest02.get("model_visible_text_changed") is not False
        or manifest02.get("all_records_reviewed") is not True
        or manifest02.get("b12_sg01_current") != 1
        or manifest02.get("b12_sg02_current") != 0
        or manifest02.get("b12_train_complete") is not False
        or manifest02.get("canonical_train_record_count_after") != 46
        or manifest02.get("training_authorized") is not False
    ):
        raise RuntimeError("B12 v0.2 manifest changed")

    metrics = {
        "V53_B12_SERIALIZED_RECORDS": 1,
        "V53_B12_REVIEWED_RECORDS": 1,
        "V53_B12_METADATA_CORRECTIONS": 0,
        "V53_B12_MODEL_VISIBLE_CHANGES": 0,
        "V53_B12_GROUP_TRAIN_VALID": 1,
        "V53_B12_RESERVED_OVERLAP": 0,
        "V53_B12_CANONICAL_TRAIN_RECORDS": canonical_count(),
        "V53_B12_SG01_CURRENT": 1,
        "V53_B12_SG02_CURRENT": 0,
        "V53_B12_TRAIN_COMPLETE": 0,
        "V53_B12_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("B12 serialization metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B12_SERIALIZED_RECORDS": 1,
        "V53_B12_REVIEWED_RECORDS": 1,
        "V53_B12_METADATA_CORRECTIONS": 0,
        "V53_B12_MODEL_VISIBLE_CHANGES": 0,
        "V53_B12_GROUP_TRAIN_VALID": 1,
        "V53_B12_RESERVED_OVERLAP": 0,
        "V53_B12_CANONICAL_TRAIN_RECORDS": 46,
        "V53_B12_SG01_CURRENT": 1,
        "V53_B12_SG02_CURRENT": 0,
        "V53_B12_TRAIN_COMPLETE": 0,
        "V53_B12_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("B12 serialization state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
