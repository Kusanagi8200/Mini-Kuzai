#!/usr/bin/env python3
"""V53 read-only audit for completed B10 TRAIN behavior.

Requires the published B06 completion report, validates the authoring-policy
HIGH=3 variant rule, B10 semantic scope and reserved exclusions, reviewed
v0.1/v0.2 identity, and the resulting 89-record canonical TRAIN population.

This audit must run after PHASE03-SMOLTALK-V53-B06-BEHAVIOR-COMPLETE-001.
It does not create validation/blind text or authorize model training.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

PRIOR_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-B06-BEHAVIOR-COMPLETE-001.json"
)
POLICY = REPO / "data/phase-03/schema/conversation-authoring-policy-v0.2.json"
COVERAGE = REPO / "data/phase-03/manifests/b10-coverage-target-v0.1.json"
GROUPS = REPO / "data/phase-03/schema/semantic-groups-v0.3.json"
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"
BATCH_V01 = REPO / "data/phase-03/train/train-batch-b10-v0.1.jsonl"
BATCH_V02 = REPO / "data/phase-03/train/train-batch-b10-v0.2.jsonl"
REVIEW = REPO / "data/phase-03/reports/train-batch-b10-v0.2-review.json"
MANIFEST = REPO / "data/phase-03/manifests/train-batch-b10-v0.2-manifest.json"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b06-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.5.jsonl",
    REPO / "data/phase-03/train/train-batch-b10-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b11-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b12-v0.3.jsonl",
    REPO / "data/phase-03/train/train-batch-b16-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b18-v0.2.jsonl",
)

EXPECTED_IDS = {
    "p03-train-b10-000001",
    "p03-train-b10-000002",
    "p03-train-b10-000003",
    "p03-train-b10-000004",
    "p03-train-b10-000005",
    "p03-train-b10-000006",
}

METRIC_KEYS = {
    "V53_B10C_TOTAL_RECORDS",
    "V53_B10C_SG01_RECORDS",
    "V53_B10C_SG02_RECORDS",
    "V53_B10C_POLICY_TARGET_VALID",
    "V53_B10C_SINGLE_TURN_RECORDS",
    "V53_B10C_REVIEWED_RECORDS",
    "V53_B10C_MODEL_VISIBLE_CHANGES",
    "V53_B10C_RESERVED_OVERLAP",
    "V53_B10C_BEHAVIOR_COMPLETE",
    "V53_B10C_CANONICAL_TRAIN_RECORDS",
    "V53_B10C_VALIDATION_TEXT_CREATED",
    "V53_B10C_MODEL_TRAINING_AUTHORIZED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B10 JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B10 JSONL")
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
        != "PHASE03-SMOLTALK-V53-B06-BEHAVIOR-COMPLETE-001"
        or report.get("training_authorized") is not False
        or metrics.get("V53_B06C_BEHAVIOR_COMPLETE") != 1
        or metrics.get("V53_B06C_CANONICAL_TRAIN_RECORDS") != 83
        or metrics.get("V53_B06C_SG01_RECORDS") != 4
        or metrics.get("V53_B06C_SG02_RECORDS") != 4
        or metrics.get("V53_B06C_MODEL_TRAINING_AUTHORIZED") != 0
    ):
        raise RuntimeError("Published B06 prerequisite missing or changed")


def validate_policy_target():
    policy = load_json(POLICY)
    if (
        policy.get("policy_version") != "0.2"
        or policy.get("variant_policy", {}).get("train", {}).get("HIGH") != 3
        or policy.get("training_authorized") is not False
    ):
        raise RuntimeError("Authoring policy no longer defines HIGH=3")

    target = load_json(COVERAGE)
    if (
        target.get("decision_id") != "B10-COVERAGE-TARGET-001"
        or target.get("status") != "POLICY_DERIVED_BATCH_TARGET"
        or target.get("applies_to_behavior") != "B10"
        or target.get("behavior_priority") != "HIGH"
        or target.get("policy_train_variants_per_group") != 3
        or target.get("global_schema_rule") is not False
        or target.get("b10_target")
        != {"sg-b10-01": 3, "sg-b10-02": 3, "total": 6}
        or target.get("current_before_completion")
        != {"sg-b10-01": 0, "sg-b10-02": 0, "total": 0}
        or target.get("records_to_add") != 6
        or target.get("validation_text_created") is not False
        or target.get("blind_test_text_created") is not False
        or target.get("model_training_authorized") is not False
    ):
        raise RuntimeError("B10 policy-derived target changed")
    return True


def validate_semantic_scope():
    groups = load_json(GROUPS)
    by_id = {
        row.get("group_id"): row
        for row in groups.get("groups", [])
        if isinstance(row, dict)
    }
    expectations = (
        ("sg-b10-01", "weak_counterevidence_hold", ["K4", "K5"], ["UNKNOWN"], 3),
        ("sg-b10-02", "strong_counterevidence_revise", ["K4"], ["LAB"], 3),
    )
    for gid, scenario, layers, status, difficulty in expectations:
        row = by_id.get(gid, {})
        if (
            row.get("split") != "train"
            or row.get("primary_behavior") != "B10"
            or row.get("behavior_priority") != "HIGH"
            or row.get("scenario_type") != scenario
            or row.get("knowledge_layers") != layers
            or row.get("knowledge_status") != status
            or row.get("difficulty") != difficulty
        ):
            raise RuntimeError("B10 TRAIN semantic scope changed")

    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B10", {})
    validation = {
        row.get("group_id"): row.get("scenario_type")
        for row in block.get("reserved_validation_groups", [])
    }
    blind = {
        row.get("group_id"): row.get("scenario_type")
        for row in block.get("reserved_blind_test_groups", [])
    }
    if validation.get("sg-b10-03") != "partial_revision":
        raise RuntimeError("B10 validation reservation changed")
    if blind.get("sg-b10-04") != "multi_turn_opinion_revision":
        raise RuntimeError("B10 blind reservation changed")


def validate_batches():
    v01 = load_jsonl(BATCH_V01)
    v02 = load_jsonl(BATCH_V02)
    if len(v01) != 6 or len(v02) != 6:
        raise RuntimeError("B10 batch must contain six records")
    if v01 != v02:
        raise RuntimeError("B10 v0.1/v0.2 content changed")
    if {row.get("id") for row in v02} != EXPECTED_IDS:
        raise RuntimeError("Unexpected B10 identifiers")

    counts = {"sg-b10-01": 0, "sg-b10-02": 0}
    single_turn = 0
    for row in v02:
        gid = row.get("group_id")
        if gid not in counts:
            raise RuntimeError("Unexpected B10 group")
        counts[gid] += 1
        hold = gid == "sg-b10-01"
        expected_scenario = "weak_counterevidence_hold" if hold else "strong_counterevidence_revise"
        expected_layers = ["K4", "K5"] if hold else ["K4"]
        expected_status = ["UNKNOWN"] if hold else ["LAB"]
        if (
            row.get("schema_version") != "0.1"
            or row.get("split") != "train"
            or row.get("language") != "en"
            or row.get("conversation_mode") != "single_turn"
            or row.get("primary_behavior") != "B10"
            or row.get("secondary_behaviors") != ["B09"]
            or row.get("scenario_type") != expected_scenario
            or row.get("knowledge_layers") != expected_layers
            or row.get("knowledge_status") != expected_status
            or row.get("difficulty") != 3
        ):
            raise RuntimeError("B10 record structure changed")
        single_turn += 1
        messages = row.get("messages")
        if (
            not isinstance(messages, list)
            or len(messages) != 2
            or [message.get("role") for message in messages] != ["user", "assistant"]
            or any(not isinstance(message.get("content"), str) or not message.get("content").strip() for message in messages)
        ):
            raise RuntimeError("B10 message structure changed")
        provenance = row.get("provenance", {})
        if (
            provenance.get("source") != "phase03-designed"
            or provenance.get("authoring_method") != "manual"
            or provenance.get("reviewed") is not True
            or provenance.get("review_decision") != "ACCEPT"
        ):
            raise RuntimeError("B10 provenance changed")
    if counts != {"sg-b10-01": 3, "sg-b10-02": 3}:
        raise RuntimeError("B10 group balance changed")
    return counts, single_turn


def canonical_count():
    identifiers = []
    for path in TRAIN_FILES:
        for row in load_jsonl(path):
            identifier = row.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            identifiers.append(identifier)
    if len(identifiers) != 89 or len(set(identifiers)) != 89:
        raise RuntimeError("Canonical TRAIN population is not 89 unique records")
    if not EXPECTED_IDS <= set(identifiers):
        raise RuntimeError("B10 records missing from canonical TRAIN")
    return len(identifiers)


def audit_metrics():
    validate_prior()
    policy_valid = validate_policy_target()
    validate_semantic_scope()
    counts, single_turn = validate_batches()

    review = load_json(REVIEW)
    if (
        review.get("review_status") != "PASS"
        or review.get("record_count") != 6
        or review.get("accepted_without_change") != 6
        or review.get("accepted_after_correction") != 0
        or review.get("rejected") != 0
        or review.get("model_visible_text_changed") is not False
        or review.get("semantic_guard_review") != "PASS"
        or review.get("same_behavior_reserved_validation_overlap") is not False
        or review.get("same_behavior_reserved_blind_overlap") is not False
        or review.get("cross_behavior_reserved_overlap") is not False
        or review.get("conversation_modes") != {"single_turn": 6, "multi_turn": 0}
        or review.get("group_counts") != {"sg-b10-01": 3, "sg-b10-02": 3}
        or review.get("b10_train_complete") is not True
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B10 review state changed")
    if set(review.get("cross_behavior_checks", {})) != {"B08", "B09", "B16"}:
        raise RuntimeError("B10 cross-behavior review coverage changed")

    manifest = load_json(MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS"
        or manifest.get("record_count") != 6
        or manifest.get("group_counts") != {"sg-b10-01": 3, "sg-b10-02": 3}
        or manifest.get("provenance_counts") != {"phase03-designed": 6}
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("semantic_leakage_remaining") is not False
        or manifest.get("model_visible_text_changed") is not False
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("sg_b10_01_current") != 3
        or manifest.get("sg_b10_01_target") != 3
        or manifest.get("sg_b10_01_complete") is not True
        or manifest.get("sg_b10_02_current") != 3
        or manifest.get("sg_b10_02_target") != 3
        or manifest.get("sg_b10_02_complete") is not True
        or manifest.get("b10_train_complete") is not True
        or manifest.get("canonical_train_record_count_after") != 89
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B10 manifest state changed")

    metrics = {
        "V53_B10C_TOTAL_RECORDS": 6,
        "V53_B10C_SG01_RECORDS": counts["sg-b10-01"],
        "V53_B10C_SG02_RECORDS": counts["sg-b10-02"],
        "V53_B10C_POLICY_TARGET_VALID": int(policy_valid),
        "V53_B10C_SINGLE_TURN_RECORDS": single_turn,
        "V53_B10C_REVIEWED_RECORDS": 6,
        "V53_B10C_MODEL_VISIBLE_CHANGES": 0,
        "V53_B10C_RESERVED_OVERLAP": 0,
        "V53_B10C_BEHAVIOR_COMPLETE": 1,
        "V53_B10C_CANONICAL_TRAIN_RECORDS": canonical_count(),
        "V53_B10C_VALIDATION_TEXT_CREATED": 0,
        "V53_B10C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("B10 metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B10C_TOTAL_RECORDS": 6,
        "V53_B10C_SG01_RECORDS": 3,
        "V53_B10C_SG02_RECORDS": 3,
        "V53_B10C_POLICY_TARGET_VALID": 1,
        "V53_B10C_SINGLE_TURN_RECORDS": 6,
        "V53_B10C_REVIEWED_RECORDS": 6,
        "V53_B10C_MODEL_VISIBLE_CHANGES": 0,
        "V53_B10C_RESERVED_OVERLAP": 0,
        "V53_B10C_BEHAVIOR_COMPLETE": 1,
        "V53_B10C_CANONICAL_TRAIN_RECORDS": 89,
        "V53_B10C_VALIDATION_TEXT_CREATED": 0,
        "V53_B10C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("B10 state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
