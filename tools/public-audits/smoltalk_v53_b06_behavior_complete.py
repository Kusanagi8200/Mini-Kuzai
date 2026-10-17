#!/usr/bin/env python3
"""V53 read-only audit for completed B06 TRAIN behavior.

Validates the published B18 prerequisite, the authoring-policy CRITICAL=4
variant rule, B06 semantic scope and reserved exclusions, reviewed v0.1/v0.2
identity, and the resulting 83-record canonical TRAIN population.

This audit does not create validation/blind text and does not authorize model
training.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

PRIOR_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-B18-BEHAVIOR-COMPLETE-001.json"
)
POLICY = REPO / "data/phase-03/schema/conversation-authoring-policy-v0.2.json"
COVERAGE = REPO / "data/phase-03/manifests/b06-coverage-target-v0.1.json"
GROUPS = REPO / "data/phase-03/schema/semantic-groups-v0.3.json"
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"
BATCH_V01 = REPO / "data/phase-03/train/train-batch-b06-v0.1.jsonl"
BATCH_V02 = REPO / "data/phase-03/train/train-batch-b06-v0.2.jsonl"
REVIEW = REPO / "data/phase-03/reports/train-batch-b06-v0.2-review.json"
MANIFEST = REPO / "data/phase-03/manifests/train-batch-b06-v0.2-manifest.json"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.5.jsonl",
    REPO / "data/phase-03/train/train-batch-b11-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b12-v0.3.jsonl",
    REPO / "data/phase-03/train/train-batch-b16-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b18-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b06-v0.2.jsonl",
)

EXPECTED_IDS = {
    "p03-train-b06-000001",
    "p03-train-b06-000002",
    "p03-train-b06-000003",
    "p03-train-b06-000004",
    "p03-train-b06-000005",
    "p03-train-b06-000006",
    "p03-train-b06-000007",
    "p03-train-b06-000008",
}

METRIC_KEYS = {
    "V53_B06C_TOTAL_RECORDS",
    "V53_B06C_SG01_RECORDS",
    "V53_B06C_SG02_RECORDS",
    "V53_B06C_POLICY_TARGET_VALID",
    "V53_B06C_REVIEWED_RECORDS",
    "V53_B06C_MODEL_VISIBLE_CHANGES",
    "V53_B06C_RESERVED_OVERLAP",
    "V53_B06C_BEHAVIOR_COMPLETE",
    "V53_B06C_CANONICAL_TRAIN_RECORDS",
    "V53_B06C_VALIDATION_TEXT_CREATED",
    "V53_B06C_MODEL_TRAINING_AUTHORIZED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B06 JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B06 JSONL")
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
        != "PHASE03-SMOLTALK-V53-B18-BEHAVIOR-COMPLETE-001"
        or report.get("training_authorized") is not False
        or metrics.get("V53_B18C_BEHAVIOR_COMPLETE") != 1
        or metrics.get("V53_B18C_CANONICAL_TRAIN_RECORDS") != 75
        or metrics.get("V53_B18C_SG01_RECORDS") != 4
        or metrics.get("V53_B18C_SG02_RECORDS") != 4
        or metrics.get("V53_B18C_MODEL_TRAINING_AUTHORIZED") != 0
    ):
        raise RuntimeError("Prior B18 prerequisite changed")


def validate_policy_target():
    policy = load_json(POLICY)
    if (
        policy.get("policy_version") != "0.2"
        or policy.get("status") != "VALIDATED_POLICY_ONLY"
        or policy.get("variant_policy", {}).get("train", {}).get("CRITICAL") != 4
        or policy.get("training_authorized") is not False
    ):
        raise RuntimeError("Authoring policy no longer defines CRITICAL=4")

    target = load_json(COVERAGE)
    if (
        target.get("decision_id") != "B06-COVERAGE-TARGET-001"
        or target.get("status") != "POLICY_DERIVED_BATCH_TARGET"
        or target.get("applies_to_behavior") != "B06"
        or target.get("behavior_priority") != "CRITICAL"
        or target.get("policy_train_variants_per_group") != 4
        or target.get("global_schema_rule") is not False
        or target.get("b06_target")
        != {"sg-b06-01": 4, "sg-b06-02": 4, "total": 8}
        or target.get("current_before_completion")
        != {"sg-b06-01": 0, "sg-b06-02": 0, "total": 0}
        or target.get("records_to_add") != 8
        or target.get("validation_text_created") is not False
        or target.get("blind_test_text_created") is not False
        or target.get("model_training_authorized") is not False
    ):
        raise RuntimeError("B06 policy-derived coverage target changed")
    return True


def validate_semantic_scope():
    groups = load_json(GROUPS)
    by_id = {
        row.get("group_id"): row
        for row in groups.get("groups", [])
        if isinstance(row, dict)
    }
    for gid, scenario, difficulty in (
        ("sg-b06-01", "explicit_unknown", 1),
        ("sg-b06-02", "ambiguous_information", 2),
    ):
        row = by_id.get(gid, {})
        if (
            row.get("split") != "train"
            or row.get("primary_behavior") != "B06"
            or row.get("behavior_priority") != "CRITICAL"
            or row.get("scenario_type") != scenario
            or row.get("knowledge_layers") != ["K5"]
            or row.get("knowledge_status") != ["UNKNOWN"]
            or row.get("difficulty") != difficulty
        ):
            raise RuntimeError("B06 TRAIN semantic scope changed")

    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B06", {})
    validation = {
        row.get("group_id"): row.get("scenario_type")
        for row in block.get("reserved_validation_groups", [])
    }
    blind = {
        row.get("group_id"): row.get("scenario_type")
        for row in block.get("reserved_blind_test_groups", [])
    }
    if validation.get("sg-b06-03") != "tentative_hypothesis_unknown":
        raise RuntimeError("B06 validation reservation changed")
    if blind.get("sg-b06-04") != "no_false_certainty":
        raise RuntimeError("B06 blind reservation changed")


def validate_batches():
    v01 = load_jsonl(BATCH_V01)
    v02 = load_jsonl(BATCH_V02)
    if len(v01) != 8 or len(v02) != 8:
        raise RuntimeError("B06 batch must contain eight records")
    if v01 != v02:
        raise RuntimeError("B06 v0.1/v0.2 model-visible content changed")
    if {row.get("id") for row in v02} != EXPECTED_IDS:
        raise RuntimeError("Unexpected B06 identifiers")

    counts = {"sg-b06-01": 0, "sg-b06-02": 0}
    for row in v02:
        gid = row.get("group_id")
        if gid not in counts:
            raise RuntimeError("Unexpected B06 group")
        counts[gid] += 1
        expected_scenario = "explicit_unknown" if gid == "sg-b06-01" else "ambiguous_information"
        expected_difficulty = 1 if gid == "sg-b06-01" else 2
        if (
            row.get("schema_version") != "0.1"
            or row.get("split") != "train"
            or row.get("language") != "en"
            or row.get("conversation_mode") != "single_turn"
            or row.get("primary_behavior") != "B06"
            or row.get("scenario_type") != expected_scenario
            or row.get("knowledge_layers") != ["K5"]
            or row.get("knowledge_status") != ["UNKNOWN"]
            or row.get("difficulty") != expected_difficulty
        ):
            raise RuntimeError("B06 record structure changed")
        messages = row.get("messages")
        if (
            not isinstance(messages, list)
            or len(messages) != 2
            or [message.get("role") for message in messages] != ["user", "assistant"]
            or any(not isinstance(message.get("content"), str) or not message.get("content").strip() for message in messages)
        ):
            raise RuntimeError("B06 message structure changed")
        provenance = row.get("provenance", {})
        if (
            provenance.get("source") != "phase03-designed"
            or provenance.get("authoring_method") != "manual"
            or provenance.get("reviewed") is not True
            or provenance.get("review_decision") != "ACCEPT"
        ):
            raise RuntimeError("B06 provenance changed")
    if counts != {"sg-b06-01": 4, "sg-b06-02": 4}:
        raise RuntimeError("B06 group balance changed")
    return counts


def canonical_count():
    identifiers = []
    for path in TRAIN_FILES:
        for row in load_jsonl(path):
            identifier = row.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            identifiers.append(identifier)
    if len(identifiers) != 83 or len(set(identifiers)) != 83:
        raise RuntimeError("Canonical TRAIN population is not 83 unique records")
    if not EXPECTED_IDS <= set(identifiers):
        raise RuntimeError("B06 records missing from canonical TRAIN")
    return len(identifiers)


def audit_metrics():
    validate_prior()
    policy_valid = validate_policy_target()
    validate_semantic_scope()
    counts = validate_batches()

    review = load_json(REVIEW)
    if (
        review.get("review_status") != "PASS"
        or review.get("record_count") != 8
        or review.get("accepted_without_change") != 8
        or review.get("accepted_after_correction") != 0
        or review.get("rejected") != 0
        or review.get("model_visible_text_changed") is not False
        or review.get("semantic_guard_review") != "PASS"
        or review.get("same_behavior_reserved_validation_overlap") is not False
        or review.get("same_behavior_reserved_blind_overlap") is not False
        or review.get("cross_behavior_reserved_overlap") is not False
        or review.get("group_counts") != {"sg-b06-01": 4, "sg-b06-02": 4}
        or review.get("b06_train_complete") is not True
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B06 review state changed")
    if set(review.get("cross_behavior_checks", {})) != {"B05", "B07", "B11"}:
        raise RuntimeError("B06 cross-behavior review coverage changed")

    manifest = load_json(MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS"
        or manifest.get("record_count") != 8
        or manifest.get("group_counts") != {"sg-b06-01": 4, "sg-b06-02": 4}
        or manifest.get("provenance_counts") != {"phase03-designed": 8}
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("semantic_leakage_remaining") is not False
        or manifest.get("model_visible_text_changed") is not False
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("sg_b06_01_current") != 4
        or manifest.get("sg_b06_01_target") != 4
        or manifest.get("sg_b06_01_complete") is not True
        or manifest.get("sg_b06_02_current") != 4
        or manifest.get("sg_b06_02_target") != 4
        or manifest.get("sg_b06_02_complete") is not True
        or manifest.get("b06_train_complete") is not True
        or manifest.get("canonical_train_record_count_after") != 83
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B06 manifest state changed")

    metrics = {
        "V53_B06C_TOTAL_RECORDS": 8,
        "V53_B06C_SG01_RECORDS": counts["sg-b06-01"],
        "V53_B06C_SG02_RECORDS": counts["sg-b06-02"],
        "V53_B06C_POLICY_TARGET_VALID": int(policy_valid),
        "V53_B06C_REVIEWED_RECORDS": 8,
        "V53_B06C_MODEL_VISIBLE_CHANGES": 0,
        "V53_B06C_RESERVED_OVERLAP": 0,
        "V53_B06C_BEHAVIOR_COMPLETE": 1,
        "V53_B06C_CANONICAL_TRAIN_RECORDS": canonical_count(),
        "V53_B06C_VALIDATION_TEXT_CREATED": 0,
        "V53_B06C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("B06 metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B06C_TOTAL_RECORDS": 8,
        "V53_B06C_SG01_RECORDS": 4,
        "V53_B06C_SG02_RECORDS": 4,
        "V53_B06C_POLICY_TARGET_VALID": 1,
        "V53_B06C_REVIEWED_RECORDS": 8,
        "V53_B06C_MODEL_VISIBLE_CHANGES": 0,
        "V53_B06C_RESERVED_OVERLAP": 0,
        "V53_B06C_BEHAVIOR_COMPLETE": 1,
        "V53_B06C_CANONICAL_TRAIN_RECORDS": 83,
        "V53_B06C_VALIDATION_TEXT_CREATED": 0,
        "V53_B06C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("B06 state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
