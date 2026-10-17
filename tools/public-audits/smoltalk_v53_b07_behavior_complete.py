#!/usr/bin/env python3
"""V53 read-only audit for completed B07 TRAIN behavior.

Requires the published B09 completion report, validates the authoring-policy
HIGH=3 rule, B07 semantic scope and reserved exclusions, reviewed v0.1/v0.2
identity, and the resulting 95-record canonical TRAIN population.

This audit does not create validation/blind text or authorize model training.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

PRIOR_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-B09-BEHAVIOR-COMPLETE-001.json"
)
POLICY = REPO / "data/phase-03/schema/conversation-authoring-policy-v0.2.json"
COVERAGE = REPO / "data/phase-03/manifests/b07-coverage-target-v0.1.json"
GROUPS = REPO / "data/phase-03/schema/semantic-groups-v0.3.json"
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"
BATCH_V01 = REPO / "data/phase-03/train/train-batch-b07-v0.1.jsonl"
BATCH_V02 = REPO / "data/phase-03/train/train-batch-b07-v0.2.jsonl"
REVIEW = REPO / "data/phase-03/reports/train-batch-b07-v0.2-review.json"
MANIFEST = REPO / "data/phase-03/manifests/train-batch-b07-v0.2-manifest.json"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b06-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b07-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.5.jsonl",
    REPO / "data/phase-03/train/train-batch-b09-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b10-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b11-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b12-v0.3.jsonl",
    REPO / "data/phase-03/train/train-batch-b16-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b18-v0.2.jsonl",
)

EXPECTED_IDS = {
    "p03-train-b07-000001",
    "p03-train-b07-000002",
    "p03-train-b07-000003",
}

METRIC_KEYS = {
    "V53_B07C_TOTAL_RECORDS",
    "V53_B07C_SG01_RECORDS",
    "V53_B07C_POLICY_TARGET_VALID",
    "V53_B07C_SINGLE_TURN_RECORDS",
    "V53_B07C_REVIEWED_RECORDS",
    "V53_B07C_MODEL_VISIBLE_CHANGES",
    "V53_B07C_RESERVED_OVERLAP",
    "V53_B07C_BEHAVIOR_COMPLETE",
    "V53_B07C_CANONICAL_TRAIN_RECORDS",
    "V53_B07C_VALIDATION_TEXT_CREATED",
    "V53_B07C_MODEL_TRAINING_AUTHORIZED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B07 JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B07 JSONL")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise RuntimeError("Expected JSONL object")
        rows.append(row)
    return rows


def validate_prior():
    report = load_json(PRIOR_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id")
        != "PHASE03-SMOLTALK-V53-B09-BEHAVIOR-COMPLETE-001"
        or report.get("training_authorized") is not False
        or metrics.get("V53_B09C_BEHAVIOR_COMPLETE") != 1
        or metrics.get("V53_B09C_CANONICAL_TRAIN_RECORDS") != 92
        or metrics.get("V53_B09C_SG01_RECORDS") != 3
        or metrics.get("V53_B09C_MODEL_TRAINING_AUTHORIZED") != 0
    ):
        raise RuntimeError("Published B09 prerequisite missing or changed")


def validate_policy_target():
    policy = load_json(POLICY)
    if (
        policy.get("policy_version") != "0.2"
        or policy.get("status") != "VALIDATED_POLICY_ONLY"
        or policy.get("variant_policy", {}).get("train", {}).get("HIGH") != 3
        or policy.get("training_authorized") is not False
    ):
        raise RuntimeError("Authoring policy no longer defines HIGH=3")

    target = load_json(COVERAGE)
    if (
        target.get("decision_id") != "B07-COVERAGE-TARGET-001"
        or target.get("status") != "POLICY_DERIVED_BATCH_TARGET"
        or target.get("applies_to_behavior") != "B07"
        or target.get("behavior_priority") != "HIGH"
        or target.get("policy_train_variants_per_group") != 3
        or target.get("global_schema_rule") is not False
        or target.get("b07_target") != {"sg-b07-01": 3, "total": 3}
        or target.get("current_before_completion") != {"sg-b07-01": 0, "total": 0}
        or target.get("records_to_add") != 3
        or target.get("validation_text_created") is not False
        or target.get("blind_test_text_created") is not False
        or target.get("model_training_authorized") is not False
    ):
        raise RuntimeError("B07 policy-derived target changed")
    return True


def validate_semantic_scope():
    groups = load_json(GROUPS)
    by_id = {
        row.get("group_id"): row
        for row in groups.get("groups", [])
        if isinstance(row, dict)
    }
    row = by_id.get("sg-b07-01", {})
    if (
        row.get("split") != "train"
        or row.get("primary_behavior") != "B07"
        or row.get("behavior_priority") != "HIGH"
        or row.get("scenario_type") != "incomplete_evidence_hypothesis"
        or row.get("knowledge_layers") != ["K3", "K5"]
        or row.get("knowledge_status") != ["UNKNOWN"]
        or row.get("difficulty") != 2
    ):
        raise RuntimeError("B07 TRAIN semantic scope changed")

    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B07", {})
    validation = {
        item.get("group_id"): item.get("scenario_type")
        for item in block.get("reserved_validation_groups", [])
    }
    blind = {
        item.get("group_id"): item.get("scenario_type")
        for item in block.get("reserved_blind_test_groups", [])
    }
    if validation.get("sg-b07-02") != "hypothesis_plus_test":
        raise RuntimeError("B07 validation reservation changed")
    if blind.get("sg-b07-03") != "speculation_boundary":
        raise RuntimeError("B07 blind reservation changed")


def validate_batches():
    v01 = load_jsonl(BATCH_V01)
    v02 = load_jsonl(BATCH_V02)
    if len(v01) != 3 or len(v02) != 3:
        raise RuntimeError("B07 batch must contain three records")
    if v01 != v02:
        raise RuntimeError("B07 v0.1/v0.2 content changed")
    if {row.get("id") for row in v02} != EXPECTED_IDS:
        raise RuntimeError("Unexpected B07 identifiers")

    for row in v02:
        if (
            row.get("schema_version") != "0.1"
            or row.get("group_id") != "sg-b07-01"
            or row.get("split") != "train"
            or row.get("language") != "en"
            or row.get("conversation_mode") != "single_turn"
            or row.get("primary_behavior") != "B07"
            or row.get("secondary_behaviors") != ["B06"]
            or row.get("scenario_type") != "incomplete_evidence_hypothesis"
            or row.get("knowledge_layers") != ["K3", "K5"]
            or row.get("knowledge_status") != ["UNKNOWN"]
            or row.get("difficulty") != 2
        ):
            raise RuntimeError("B07 record structure changed")
        messages = row.get("messages")
        if (
            not isinstance(messages, list)
            or len(messages) != 2
            or [message.get("role") for message in messages] != ["user", "assistant"]
            or any(
                not isinstance(message.get("content"), str)
                or not message.get("content").strip()
                for message in messages
            )
        ):
            raise RuntimeError("B07 message structure changed")
        provenance = row.get("provenance", {})
        if (
            provenance.get("source") != "phase03-designed"
            or provenance.get("authoring_method") != "manual"
            or provenance.get("reviewed") is not True
            or provenance.get("review_decision") != "ACCEPT"
        ):
            raise RuntimeError("B07 provenance changed")
    return len(v02)


def canonical_count():
    identifiers = []
    for path in TRAIN_FILES:
        for row in load_jsonl(path):
            identifier = row.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            identifiers.append(identifier)
    if len(identifiers) != 95 or len(set(identifiers)) != 95:
        raise RuntimeError("Canonical TRAIN population is not 95 unique records")
    if not EXPECTED_IDS <= set(identifiers):
        raise RuntimeError("B07 records missing from canonical TRAIN")
    return len(identifiers)


def audit_metrics():
    validate_prior()
    policy_valid = validate_policy_target()
    validate_semantic_scope()
    record_count = validate_batches()

    review = load_json(REVIEW)
    if (
        review.get("review_status") != "PASS"
        or review.get("record_count") != 3
        or review.get("accepted_without_change") != 3
        or review.get("accepted_after_correction") != 0
        or review.get("rejected") != 0
        or review.get("model_visible_text_changed") is not False
        or review.get("semantic_guard_review") != "PASS"
        or review.get("same_behavior_reserved_validation_overlap") is not False
        or review.get("same_behavior_reserved_blind_overlap") is not False
        or review.get("cross_behavior_reserved_overlap") is not False
        or review.get("conversation_modes") != {"single_turn": 3, "multi_turn": 0}
        or review.get("group_counts") != {"sg-b07-01": 3}
        or review.get("sg_b07_01_complete") is not True
        or review.get("b07_train_complete") is not True
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B07 review state changed")
    if set(review.get("cross_behavior_checks", {})) != {"B06", "B08", "B11"}:
        raise RuntimeError("B07 cross-behavior review coverage changed")

    manifest = load_json(MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS"
        or manifest.get("record_count") != 3
        or manifest.get("group_counts") != {"sg-b07-01": 3}
        or manifest.get("provenance_counts") != {"phase03-designed": 3}
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("semantic_leakage_remaining") is not False
        or manifest.get("model_visible_text_changed") is not False
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("sg_b07_01_current") != 3
        or manifest.get("sg_b07_01_target") != 3
        or manifest.get("sg_b07_01_complete") is not True
        or manifest.get("b07_train_complete") is not True
        or manifest.get("canonical_train_record_count_after") != 95
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B07 manifest state changed")

    metrics = {
        "V53_B07C_TOTAL_RECORDS": record_count,
        "V53_B07C_SG01_RECORDS": record_count,
        "V53_B07C_POLICY_TARGET_VALID": int(policy_valid),
        "V53_B07C_SINGLE_TURN_RECORDS": record_count,
        "V53_B07C_REVIEWED_RECORDS": 3,
        "V53_B07C_MODEL_VISIBLE_CHANGES": 0,
        "V53_B07C_RESERVED_OVERLAP": 0,
        "V53_B07C_BEHAVIOR_COMPLETE": 1,
        "V53_B07C_CANONICAL_TRAIN_RECORDS": canonical_count(),
        "V53_B07C_VALIDATION_TEXT_CREATED": 0,
        "V53_B07C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("B07 metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B07C_TOTAL_RECORDS": 3,
        "V53_B07C_SG01_RECORDS": 3,
        "V53_B07C_POLICY_TARGET_VALID": 1,
        "V53_B07C_SINGLE_TURN_RECORDS": 3,
        "V53_B07C_REVIEWED_RECORDS": 3,
        "V53_B07C_MODEL_VISIBLE_CHANGES": 0,
        "V53_B07C_RESERVED_OVERLAP": 0,
        "V53_B07C_BEHAVIOR_COMPLETE": 1,
        "V53_B07C_CANONICAL_TRAIN_RECORDS": 95,
        "V53_B07C_VALIDATION_TEXT_CREATED": 0,
        "V53_B07C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("B07 state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
