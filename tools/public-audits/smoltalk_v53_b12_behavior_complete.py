#!/usr/bin/env python3
"""V53 read-only audit for completed B12 TRAIN behavior.

Validates the previously published first B12 serialization, the explicit
B12-local 4+4 coverage decision, the expanded reviewed v0.3 batch, semantic
guards, and the resulting 53-record canonical TRAIN population.

The 4-per-group target is local to B12 and is not promoted to a global schema
rule. This audit does not authorize model training.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

PRIOR_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-B12-SERIALIZATION-001.json"
)
COVERAGE = REPO / "data/phase-03/manifests/b12-coverage-target-v0.1.json"
BATCH_PREVIOUS = REPO / "data/phase-03/train/train-batch-b12-v0.2.jsonl"
BATCH = REPO / "data/phase-03/train/train-batch-b12-v0.3.jsonl"
REVIEW = REPO / "data/phase-03/reports/train-batch-b12-v0.3-review.json"
MANIFEST = REPO / "data/phase-03/manifests/train-batch-b12-v0.3-manifest.json"
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"
GROUPS = REPO / "data/phase-03/schema/semantic-groups-v0.3.json"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.5.jsonl",
    REPO / "data/phase-03/train/train-batch-b12-v0.3.jsonl",
)

PRECEDENT_GROUPS = (
    "sg-b01-01", "sg-b01-02",
    "sg-b02-01", "sg-b02-02",
    "sg-b03-01", "sg-b03-02",
    "sg-b05-01", "sg-b05-02",
    "sg-b08-01", "sg-b08-02",
)

EXPECTED_IDS = {
    "p03-train-b12-000001",
    "p03-train-b12-000002",
    "p03-train-b12-000003",
    "p03-train-b12-000004",
    "p03-train-b12-000005",
    "p03-train-b12-000006",
    "p03-train-b12-000007",
    "p03-train-b12-000008",
}

METRIC_KEYS = {
    "V53_B12C_TOTAL_RECORDS",
    "V53_B12C_SG01_RECORDS",
    "V53_B12C_SG02_RECORDS",
    "V53_B12C_LOCAL_TARGET_VALID",
    "V53_B12C_EXTERNAL_RECORDS",
    "V53_B12C_DESIGNED_RECORDS",
    "V53_B12C_BEHAVIOR_COMPLETE",
    "V53_B12C_RESERVED_OVERLAP",
    "V53_B12C_CANONICAL_TRAIN_RECORDS",
    "V53_B12C_VALIDATION_TEXT_CREATED",
    "V53_B12C_MODEL_TRAINING_AUTHORIZED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B12 completion JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B12 completion JSONL")
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
        report.get("step_id") != "PHASE03-SMOLTALK-V53-B12-SERIALIZATION-001"
        or report.get("training_authorized") is not False
        or metrics.get("V53_B12_SERIALIZED_RECORDS") != 1
        or metrics.get("V53_B12_REVIEWED_RECORDS") != 1
        or metrics.get("V53_B12_CANONICAL_TRAIN_RECORDS") != 46
        or metrics.get("V53_B12_SG01_CURRENT") != 1
        or metrics.get("V53_B12_SG02_CURRENT") != 0
        or metrics.get("V53_B12_TRAIN_COMPLETE") != 0
        or metrics.get("V53_B12_MODEL_TRAINING_AUTHORIZED") != 0
    ):
        raise RuntimeError("Prior B12 serialization prerequisite changed")


def group_counts_from_files(paths):
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
        decision.get("decision_id") != "B12-COVERAGE-TARGET-001"
        or decision.get("status") != "LOCAL_BATCH_DESIGN_DECISION"
        or decision.get("applies_to_behavior") != "B12"
        or decision.get("global_schema_rule") is not False
        or decision.get("b12_target")
        != {"sg-b12-01": 4, "sg-b12-02": 4, "total": 8}
        or decision.get("current_before_completion")
        != {"sg-b12-01": 1, "sg-b12-02": 0, "total": 1}
        or decision.get("records_to_add") != 7
        or decision.get("validation_text_created") is not False
        or decision.get("blind_test_text_created") is not False
        or decision.get("model_training_authorized") is not False
    ):
        raise RuntimeError("B12 local coverage decision changed")

    actual = group_counts_from_files(TRAIN_FILES[:-1])
    precedent = decision.get("precedent", {})
    for gid in PRECEDENT_GROUPS:
        if precedent.get(gid) != 4 or actual.get(gid) != 4:
            raise RuntimeError("B12 4+4 precedent no longer matches canonical data")
    return True


def validate_semantic_scope():
    groups = load_json(GROUPS)
    if (
        groups.get("inventory_version") != "0.3"
        or groups.get("status") != "VALIDATED_SPLITS_ASSIGNED"
    ):
        raise RuntimeError("Semantic-group inventory state changed")

    by_id = {
        row.get("group_id"): row
        for row in groups.get("groups", [])
        if isinstance(row, dict)
    }
    for gid, scenario, difficulty in (
        ("sg-b12-01", "alternative_generation", 2),
        ("sg-b12-02", "conceptual_combination", 3),
    ):
        row = by_id.get(gid, {})
        if (
            row.get("split") != "train"
            or row.get("primary_behavior") != "B12"
            or row.get("behavior_priority") != "CRITICAL"
            or row.get("scenario_type") != scenario
            or row.get("knowledge_layers") != ["K3", "K4"]
            or row.get("knowledge_status") != ["LAB"]
            or row.get("difficulty") != difficulty
        ):
            raise RuntimeError("B12 TRAIN semantic scope changed")

    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B12", {})
    validation = {
        row.get("group_id"): row.get("scenario_type")
        for row in block.get("reserved_validation_groups", [])
    }
    blind = {
        row.get("group_id"): row.get("scenario_type")
        for row in block.get("reserved_blind_test_groups", [])
    }
    if validation.get("sg-b12-03") != "creative_hypothesis_epistemic_control":
        raise RuntimeError("B12 validation reservation changed")
    if blind.get("sg-b12-04") != "creative_under_constraints":
        raise RuntimeError("B12 blind reservation changed")


def validate_batch():
    previous = load_jsonl(BATCH_PREVIOUS)
    rows = load_jsonl(BATCH)
    if len(previous) != 1 or len(rows) != 8:
        raise RuntimeError("Unexpected B12 batch size")
    if rows[0] != previous[0]:
        raise RuntimeError("Inherited canonical B12 record changed in v0.3")

    ids = {row.get("id") for row in rows}
    if ids != EXPECTED_IDS:
        raise RuntimeError("Unexpected B12 v0.3 identifiers")

    groups = {"sg-b12-01": 0, "sg-b12-02": 0}
    external = 0
    designed = 0
    for row in rows:
        gid = row.get("group_id")
        if gid not in groups:
            raise RuntimeError("Unexpected B12 group")
        groups[gid] += 1
        expected_scenario = (
            "alternative_generation"
            if gid == "sg-b12-01"
            else "conceptual_combination"
        )
        expected_difficulty = 2 if gid == "sg-b12-01" else 3
        if (
            row.get("schema_version") != "0.1"
            or row.get("split") != "train"
            or row.get("language") != "en"
            or row.get("primary_behavior") != "B12"
            or row.get("knowledge_layers") != ["K3", "K4"]
            or row.get("knowledge_status") != ["LAB"]
            or row.get("difficulty") != expected_difficulty
            or row.get("scenario_type") != expected_scenario
        ):
            raise RuntimeError("B12 v0.3 record structure changed")

        messages = row.get("messages")
        if (
            not isinstance(messages, list)
            or len(messages) < 2
            or any(
                not isinstance(message, dict)
                or message.get("role") not in {"user", "assistant"}
                or not isinstance(message.get("content"), str)
                or not message.get("content").strip()
                for message in messages
            )
        ):
            raise RuntimeError("B12 record contains an invalid message")

        provenance = row.get("provenance", {})
        source = provenance.get("source")
        if source == "HuggingFaceTB/smol-smoltalk":
            external += 1
            if row.get("id") != "p03-train-b12-000001":
                raise RuntimeError("Unexpected external B12 record")
        elif source == "phase03-designed":
            designed += 1
            if (
                provenance.get("reviewed") is not True
                or provenance.get("review_decision") != "ACCEPT"
            ):
                raise RuntimeError("Designed B12 record must be reviewed")
        else:
            raise RuntimeError("Unexpected B12 provenance source")

    if groups != {"sg-b12-01": 4, "sg-b12-02": 4}:
        raise RuntimeError("B12 v0.3 group balance changed")
    if external != 1 or designed != 7:
        raise RuntimeError("B12 v0.3 provenance mix changed")
    return groups, external, designed


def canonical_count():
    identifiers = []
    for path in TRAIN_FILES:
        for row in load_jsonl(path):
            identifier = row.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            identifiers.append(identifier)
    if len(identifiers) != 53 or len(set(identifiers)) != 53:
        raise RuntimeError("Canonical TRAIN population is not 53 unique records")
    if not EXPECTED_IDS <= set(identifiers):
        raise RuntimeError("Completed B12 records missing from canonical TRAIN")
    return len(identifiers)


def audit_metrics():
    validate_prior()
    local_target_valid = validate_coverage_target()
    validate_semantic_scope()
    groups, external, designed = validate_batch()

    review = load_json(REVIEW)
    if (
        review.get("review_status") != "PASS"
        or review.get("record_count") != 8
        or review.get("inherited_reviewed_records") != 1
        or review.get("newly_authored_records") != 7
        or review.get("accepted_records") != 8
        or review.get("rejected") != 0
        or review.get("inherited_model_visible_text_changed") is not False
        or review.get("semantic_guard_review") != "PASS"
        or review.get("reserved_validation_overlap") is not False
        or review.get("reserved_blind_test_overlap") is not False
        or review.get("group_counts") != {"sg-b12-01": 4, "sg-b12-02": 4}
        or review.get("sg_b12_01_complete") is not True
        or review.get("sg_b12_02_complete") is not True
        or review.get("b12_train_complete") is not True
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B12 v0.3 review state changed")

    manifest = load_json(MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS"
        or manifest.get("record_count") != 8
        or manifest.get("group_counts") != {"sg-b12-01": 4, "sg-b12-02": 4}
        or manifest.get("provenance_counts")
        != {"HuggingFaceTB/smol-smoltalk": 1, "phase03-designed": 7}
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("semantic_leakage_remaining") is not False
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("sg_b12_01_current") != 4
        or manifest.get("sg_b12_01_target") != 4
        or manifest.get("sg_b12_01_complete") is not True
        or manifest.get("sg_b12_02_current") != 4
        or manifest.get("sg_b12_02_target") != 4
        or manifest.get("sg_b12_02_complete") is not True
        or manifest.get("b12_train_complete") is not True
        or manifest.get("canonical_train_record_count_after") != 53
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B12 v0.3 manifest state changed")

    metrics = {
        "V53_B12C_TOTAL_RECORDS": 8,
        "V53_B12C_SG01_RECORDS": groups["sg-b12-01"],
        "V53_B12C_SG02_RECORDS": groups["sg-b12-02"],
        "V53_B12C_LOCAL_TARGET_VALID": int(local_target_valid),
        "V53_B12C_EXTERNAL_RECORDS": external,
        "V53_B12C_DESIGNED_RECORDS": designed,
        "V53_B12C_BEHAVIOR_COMPLETE": 1,
        "V53_B12C_RESERVED_OVERLAP": 0,
        "V53_B12C_CANONICAL_TRAIN_RECORDS": canonical_count(),
        "V53_B12C_VALIDATION_TEXT_CREATED": 0,
        "V53_B12C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("B12 completion metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B12C_TOTAL_RECORDS": 8,
        "V53_B12C_SG01_RECORDS": 4,
        "V53_B12C_SG02_RECORDS": 4,
        "V53_B12C_LOCAL_TARGET_VALID": 1,
        "V53_B12C_EXTERNAL_RECORDS": 1,
        "V53_B12C_DESIGNED_RECORDS": 7,
        "V53_B12C_BEHAVIOR_COMPLETE": 1,
        "V53_B12C_RESERVED_OVERLAP": 0,
        "V53_B12C_CANONICAL_TRAIN_RECORDS": 53,
        "V53_B12C_VALIDATION_TEXT_CREATED": 0,
        "V53_B12C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("B12 completion state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
