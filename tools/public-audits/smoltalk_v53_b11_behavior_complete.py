#!/usr/bin/env python3
"""V53 read-only audit for completed B11 TRAIN behavior.

Validates the B11-local 4+4 coverage decision, reviewed initiative batch,
semantic guards, unchanged v0.1/v0.2 model-visible content, and the resulting
69-record canonical TRAIN population.

The 4-per-group target is local to B11 and is not a global schema rule.
This audit does not authorize model training.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

PRIOR_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-B16-BEHAVIOR-COMPLETE-001.json"
)
COVERAGE = REPO / "data/phase-03/manifests/b11-coverage-target-v0.1.json"
BATCH_V01 = REPO / "data/phase-03/train/train-batch-b11-v0.1.jsonl"
BATCH_V02 = REPO / "data/phase-03/train/train-batch-b11-v0.2.jsonl"
REVIEW = REPO / "data/phase-03/reports/train-batch-b11-v0.2-review.json"
MANIFEST = REPO / "data/phase-03/manifests/train-batch-b11-v0.2-manifest.json"
GROUPS = REPO / "data/phase-03/schema/semantic-groups-v0.3.json"
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.5.jsonl",
    REPO / "data/phase-03/train/train-batch-b12-v0.3.jsonl",
    REPO / "data/phase-03/train/train-batch-b16-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b11-v0.2.jsonl",
)

PRECEDENT_GROUPS = (
    "sg-b01-01", "sg-b01-02",
    "sg-b02-01", "sg-b02-02",
    "sg-b03-01", "sg-b03-02",
    "sg-b05-01", "sg-b05-02",
    "sg-b08-01", "sg-b08-02",
    "sg-b12-01", "sg-b12-02",
    "sg-b16-01", "sg-b16-02",
)

EXPECTED_IDS = {
    "p03-train-b11-000001",
    "p03-train-b11-000002",
    "p03-train-b11-000003",
    "p03-train-b11-000004",
    "p03-train-b11-000005",
    "p03-train-b11-000006",
    "p03-train-b11-000007",
    "p03-train-b11-000008",
}

METRIC_KEYS = {
    "V53_B11C_TOTAL_RECORDS",
    "V53_B11C_SG01_RECORDS",
    "V53_B11C_SG02_RECORDS",
    "V53_B11C_LOCAL_TARGET_VALID",
    "V53_B11C_REVIEWED_RECORDS",
    "V53_B11C_MODEL_VISIBLE_CHANGES",
    "V53_B11C_RESERVED_OVERLAP",
    "V53_B11C_BEHAVIOR_COMPLETE",
    "V53_B11C_CANONICAL_TRAIN_RECORDS",
    "V53_B11C_VALIDATION_TEXT_CREATED",
    "V53_B11C_MODEL_TRAINING_AUTHORIZED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B11 completion JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B11 completion JSONL")
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
        != "PHASE03-SMOLTALK-V53-B16-BEHAVIOR-COMPLETE-001"
        or report.get("training_authorized") is not False
        or metrics.get("V53_B16C_BEHAVIOR_COMPLETE") != 1
        or metrics.get("V53_B16C_CANONICAL_TRAIN_RECORDS") != 61
        or metrics.get("V53_B16C_SG01_RECORDS") != 4
        or metrics.get("V53_B16C_SG02_RECORDS") != 4
        or metrics.get("V53_B16C_MODEL_TRAINING_AUTHORIZED") != 0
    ):
        raise RuntimeError("Prior B16 completion prerequisite changed")


def group_counts(paths):
    counts = {}
    for path in paths:
        for row in load_jsonl(path):
            gid = row.get("group_id")
            if isinstance(gid, str):
                counts[gid] = counts.get(gid, 0) + 1
    return counts


def validate_coverage_target():
    decision = load_json(COVERAGE)
    if (
        decision.get("decision_id") != "B11-COVERAGE-TARGET-001"
        or decision.get("status") != "LOCAL_BATCH_DESIGN_DECISION"
        or decision.get("applies_to_behavior") != "B11"
        or decision.get("global_schema_rule") is not False
        or decision.get("b11_target")
        != {"sg-b11-01": 4, "sg-b11-02": 4, "total": 8}
        or decision.get("current_before_completion")
        != {"sg-b11-01": 0, "sg-b11-02": 0, "total": 0}
        or decision.get("records_to_add") != 8
        or decision.get("validation_text_created") is not False
        or decision.get("blind_test_text_created") is not False
        or decision.get("model_training_authorized") is not False
    ):
        raise RuntimeError("B11 local coverage decision changed")

    actual = group_counts(TRAIN_FILES[:-1])
    precedent = decision.get("precedent", {})
    for gid in PRECEDENT_GROUPS:
        if precedent.get(gid) != 4 or actual.get(gid) != 4:
            raise RuntimeError("B11 4+4 precedent no longer matches canonical data")
    return True


def validate_semantic_scope():
    groups = load_json(GROUPS)
    if (
        groups.get("inventory_version") != "0.3"
        or groups.get("status") != "VALIDATED_SPLITS_ASSIGNED"
    ):
        raise RuntimeError("Semantic-group inventory changed")

    by_id = {
        row.get("group_id"): row
        for row in groups.get("groups", [])
        if isinstance(row, dict)
    }
    expectations = (
        ("sg-b11-01", "underspecified_goal", ["K3"], ["LAB"], 2),
        ("sg-b11-02", "propose_next_experiment", ["K2", "K3"], ["LAB"], 3),
    )
    for gid, scenario, layers, status, difficulty in expectations:
        row = by_id.get(gid, {})
        if (
            row.get("split") != "train"
            or row.get("primary_behavior") != "B11"
            or row.get("behavior_priority") != "CRITICAL"
            or row.get("scenario_type") != scenario
            or row.get("knowledge_layers") != layers
            or row.get("knowledge_status") != status
            or row.get("difficulty") != difficulty
        ):
            raise RuntimeError("B11 TRAIN semantic scope changed")

    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B11", {})
    validation = {
        row.get("group_id"): row.get("scenario_type")
        for row in block.get("reserved_validation_groups", [])
    }
    blind = {
        row.get("group_id"): row.get("scenario_type")
        for row in block.get("reserved_blind_test_groups", [])
    }
    if validation.get("sg-b11-03") != "unresolved_contradiction_test":
        raise RuntimeError("B11 validation reservation changed")
    if blind.get("sg-b11-04") != "initiative_restraint":
        raise RuntimeError("B11 blind reservation changed")


def validate_batches():
    v01 = load_jsonl(BATCH_V01)
    v02 = load_jsonl(BATCH_V02)
    if len(v01) != 8 or len(v02) != 8:
        raise RuntimeError("B11 batch must contain eight records")
    if v01 != v02:
        raise RuntimeError("B11 v0.1/v0.2 content changed")

    ids = {row.get("id") for row in v02}
    if ids != EXPECTED_IDS:
        raise RuntimeError("Unexpected B11 identifiers")

    counts = {"sg-b11-01": 0, "sg-b11-02": 0}
    for row in v02:
        gid = row.get("group_id")
        if gid not in counts:
            raise RuntimeError("Unexpected B11 group")
        counts[gid] += 1
        expected_scenario = (
            "underspecified_goal"
            if gid == "sg-b11-01"
            else "propose_next_experiment"
        )
        expected_layers = ["K3"] if gid == "sg-b11-01" else ["K2", "K3"]
        expected_difficulty = 2 if gid == "sg-b11-01" else 3

        if (
            row.get("schema_version") != "0.1"
            or row.get("split") != "train"
            or row.get("language") != "en"
            or row.get("conversation_mode") != "single_turn"
            or row.get("primary_behavior") != "B11"
            or row.get("scenario_type") != expected_scenario
            or row.get("knowledge_layers") != expected_layers
            or row.get("knowledge_status") != ["LAB"]
            or row.get("difficulty") != expected_difficulty
        ):
            raise RuntimeError("B11 record structure changed")

        messages = row.get("messages")
        if (
            not isinstance(messages, list)
            or len(messages) != 2
            or [message.get("role") for message in messages]
            != ["user", "assistant"]
            or any(
                not isinstance(message.get("content"), str)
                or not message.get("content").strip()
                for message in messages
            )
        ):
            raise RuntimeError("B11 message structure changed")

        provenance = row.get("provenance", {})
        if (
            provenance.get("source") != "phase03-designed"
            or provenance.get("authoring_method") != "manual"
            or provenance.get("reviewed") is not True
            or provenance.get("review_decision") != "ACCEPT"
        ):
            raise RuntimeError("B11 provenance state changed")

    if counts != {"sg-b11-01": 4, "sg-b11-02": 4}:
        raise RuntimeError("B11 group balance changed")
    return counts


def canonical_count():
    identifiers = []
    for path in TRAIN_FILES:
        for row in load_jsonl(path):
            identifier = row.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            identifiers.append(identifier)
    if len(identifiers) != 69 or len(set(identifiers)) != 69:
        raise RuntimeError("Canonical TRAIN population is not 69 unique records")
    if not EXPECTED_IDS <= set(identifiers):
        raise RuntimeError("B11 records missing from canonical TRAIN")
    return len(identifiers)


def audit_metrics():
    validate_prior()
    target_valid = validate_coverage_target()
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
        or review.get("group_counts") != {"sg-b11-01": 4, "sg-b11-02": 4}
        or review.get("sg_b11_01_complete") is not True
        or review.get("sg_b11_02_complete") is not True
        or review.get("b11_train_complete") is not True
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B11 v0.2 review state changed")

    checks = review.get("cross_behavior_checks", {})
    if set(checks) != {"B06", "B07", "B08"}:
        raise RuntimeError("B11 cross-behavior review coverage changed")

    manifest = load_json(MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS"
        or manifest.get("record_count") != 8
        or manifest.get("group_counts") != {"sg-b11-01": 4, "sg-b11-02": 4}
        or manifest.get("provenance_counts") != {"phase03-designed": 8}
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("semantic_leakage_remaining") is not False
        or manifest.get("model_visible_text_changed") is not False
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("sg_b11_01_current") != 4
        or manifest.get("sg_b11_01_target") != 4
        or manifest.get("sg_b11_01_complete") is not True
        or manifest.get("sg_b11_02_current") != 4
        or manifest.get("sg_b11_02_target") != 4
        or manifest.get("sg_b11_02_complete") is not True
        or manifest.get("b11_train_complete") is not True
        or manifest.get("canonical_train_record_count_after") != 69
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B11 v0.2 manifest state changed")

    metrics = {
        "V53_B11C_TOTAL_RECORDS": 8,
        "V53_B11C_SG01_RECORDS": counts["sg-b11-01"],
        "V53_B11C_SG02_RECORDS": counts["sg-b11-02"],
        "V53_B11C_LOCAL_TARGET_VALID": int(target_valid),
        "V53_B11C_REVIEWED_RECORDS": 8,
        "V53_B11C_MODEL_VISIBLE_CHANGES": 0,
        "V53_B11C_RESERVED_OVERLAP": 0,
        "V53_B11C_BEHAVIOR_COMPLETE": 1,
        "V53_B11C_CANONICAL_TRAIN_RECORDS": canonical_count(),
        "V53_B11C_VALIDATION_TEXT_CREATED": 0,
        "V53_B11C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("B11 completion metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B11C_TOTAL_RECORDS": 8,
        "V53_B11C_SG01_RECORDS": 4,
        "V53_B11C_SG02_RECORDS": 4,
        "V53_B11C_LOCAL_TARGET_VALID": 1,
        "V53_B11C_REVIEWED_RECORDS": 8,
        "V53_B11C_MODEL_VISIBLE_CHANGES": 0,
        "V53_B11C_RESERVED_OVERLAP": 0,
        "V53_B11C_BEHAVIOR_COMPLETE": 1,
        "V53_B11C_CANONICAL_TRAIN_RECORDS": 69,
        "V53_B11C_VALIDATION_TEXT_CREATED": 0,
        "V53_B11C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("B11 completion state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
