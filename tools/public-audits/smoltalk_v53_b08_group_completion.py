#!/usr/bin/env python3
"""V53 read-only audit for completion of TRAIN group sg-b08-01.

Validates the previously published first B08 serialization report, the expanded
v0.3 B08 batch containing four reviewed weak-technical-claim variants, semantic
guard metadata, and the resulting 41-record canonical TRAIN population.

The audit marks sg-b08-01 complete, not the entire B08 behavior, and does not
authorize model training.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

PRIOR_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-B08-SERIALIZATION-001.json"
)
BATCH = REPO / "data/phase-03/train/train-batch-b08-v0.3.jsonl"
REVIEW = REPO / "data/phase-03/reports/train-batch-b08-v0.3-review.json"
MANIFEST = REPO / "data/phase-03/manifests/train-batch-b08-v0.3-manifest.json"
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.3.jsonl",
)

EXPECTED_IDS = {
    "p03-train-b08-000001",
    "p03-train-b08-000002",
    "p03-train-b08-000003",
    "p03-train-b08-000004",
}

METRIC_KEYS = {
    "V53_B08C_GROUP_RECORDS",
    "V53_B08C_NEW_DESIGNED_RECORDS",
    "V53_B08C_EXTERNAL_RECORDS",
    "V53_B08C_REVIEWED_RECORDS",
    "V53_B08C_GROUP_COMPLETE",
    "V53_B08C_BEHAVIOR_COMPLETE",
    "V53_B08C_RESERVED_OVERLAP",
    "V53_B08C_CANONICAL_TRAIN_RECORDS",
    "V53_B08C_VALIDATION_TEXT_CREATED",
    "V53_B08C_MODEL_TRAINING_AUTHORIZED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B08 completion dependency")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B08 completion JSONL")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise RuntimeError("B08 row must be a JSON object")
        rows.append(row)
    return rows


def validate_prior_history():
    report = load_json(PRIOR_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id") != "PHASE03-SMOLTALK-V53-B08-SERIALIZATION-001"
        or report.get("training_authorized") is not False
        or metrics.get("V53_B08_CANONICAL_TRAIN_RECORDS") != 38
        or metrics.get("V53_B08_GROUP_CURRENT") != 1
        or metrics.get("V53_B08_GROUP_PLANNED") != 4
        or metrics.get("V53_B08_TRAIN_COMPLETE") != 0
        or metrics.get("V53_B08_MODEL_TRAINING_AUTHORIZED") != 0
    ):
        raise RuntimeError("Prior B08 serialization history is not the expected prerequisite")


def validate_reserved_scope():
    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B08", {})
    train = {row.get("group_id"): row for row in block.get("train_groups", [])}
    validation = {
        row.get("group_id"): row for row in block.get("reserved_validation_groups", [])
    }
    blind = {
        row.get("group_id"): row for row in block.get("reserved_blind_test_groups", [])
    }
    if train.get("sg-b08-01", {}).get("scenario_type") != "weak_technical_claim":
        raise RuntimeError("B08 TRAIN weak-claim scope changed")
    if validation.get("sg-b08-03", {}).get("scenario_type") != "unsupported_conclusion":
        raise RuntimeError("B08 reserved validation scope changed")
    if blind.get("sg-b08-04", {}).get("scenario_type") != "social_pressure_agreement":
        raise RuntimeError("B08 reserved blind scope changed")


def validate_batch():
    rows = load_jsonl(BATCH)
    if len(rows) != 4:
        raise RuntimeError("B08 v0.3 must contain four records")
    ids = {row.get("id") for row in rows}
    if ids != EXPECTED_IDS:
        raise RuntimeError("Unexpected B08 v0.3 record identifiers")

    external = 0
    designed = 0
    for row in rows:
        if (
            row.get("schema_version") != "0.1"
            or row.get("group_id") != "sg-b08-01"
            or row.get("split") != "train"
            or row.get("primary_behavior") != "B08"
            or row.get("scenario_type") != "weak_technical_claim"
        ):
            raise RuntimeError("B08 v0.3 record structure changed")
        messages = row.get("messages")
        if not isinstance(messages, list) or len(messages) < 2:
            raise RuntimeError("B08 record messages missing")
        provenance = row.get("provenance", {})
        source = provenance.get("source")
        if source == "HuggingFaceTB/smol-smoltalk":
            external += 1
            if row.get("id") != "p03-train-b08-000001":
                raise RuntimeError("Unexpected external B08 record")
        elif source == "phase03-designed":
            designed += 1
            if provenance.get("reviewed") is not True:
                raise RuntimeError("Designed B08 record must already be reviewed")
        else:
            raise RuntimeError("Unexpected B08 provenance source")
    if external != 1 or designed != 3:
        raise RuntimeError("B08 v0.3 provenance mix changed")
    return external, designed


def canonical_count():
    ids = []
    for path in TRAIN_FILES:
        for row in load_jsonl(path):
            identifier = row.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            ids.append(identifier)
    if len(ids) != 41 or len(set(ids)) != 41:
        raise RuntimeError("Canonical TRAIN population is not 41 unique records")
    if not EXPECTED_IDS <= set(ids):
        raise RuntimeError("Completed B08 weak-claim group missing from canonical TRAIN")
    return len(ids)


def audit_metrics():
    validate_prior_history()
    validate_reserved_scope()
    external, designed = validate_batch()

    review = load_json(REVIEW)
    if (
        review.get("review_status") != "PASS"
        or review.get("record_count") != 4
        or review.get("inherited_reviewed_records") != 1
        or review.get("newly_authored_records") != 3
        or review.get("accepted_records") != 4
        or review.get("rejected") != 0
        or review.get("semantic_guard_review") != "PASS"
        or review.get("reserved_validation_overlap") is not False
        or review.get("reserved_blind_test_overlap") is not False
        or review.get("group_counts") != {"sg-b08-01": 4}
        or review.get("sg_b08_01_complete") is not True
        or review.get("sg_b08_02_current") != 0
        or review.get("b08_train_complete") is not False
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B08 v0.3 review state changed")

    manifest = load_json(MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS"
        or manifest.get("record_count") != 4
        or manifest.get("group_counts") != {"sg-b08-01": 4}
        or manifest.get("provenance_counts")
        != {"HuggingFaceTB/smol-smoltalk": 1, "phase03-designed": 3}
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("semantic_leakage_remaining") is not False
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("sg_b08_01_current") != 4
        or manifest.get("sg_b08_01_planned") != 4
        or manifest.get("sg_b08_01_complete") is not True
        or manifest.get("sg_b08_02_current") != 0
        or manifest.get("sg_b08_02_planned") != 4
        or manifest.get("b08_train_complete") is not False
        or manifest.get("canonical_train_record_count_after") != 41
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B08 v0.3 manifest state changed")

    metrics = {
        "V53_B08C_GROUP_RECORDS": 4,
        "V53_B08C_NEW_DESIGNED_RECORDS": designed,
        "V53_B08C_EXTERNAL_RECORDS": external,
        "V53_B08C_REVIEWED_RECORDS": 4,
        "V53_B08C_GROUP_COMPLETE": 1,
        "V53_B08C_BEHAVIOR_COMPLETE": 0,
        "V53_B08C_RESERVED_OVERLAP": 0,
        "V53_B08C_CANONICAL_TRAIN_RECORDS": canonical_count(),
        "V53_B08C_VALIDATION_TEXT_CREATED": 0,
        "V53_B08C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("B08 completion metric key set changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B08C_GROUP_RECORDS": 4,
        "V53_B08C_NEW_DESIGNED_RECORDS": 3,
        "V53_B08C_EXTERNAL_RECORDS": 1,
        "V53_B08C_REVIEWED_RECORDS": 4,
        "V53_B08C_GROUP_COMPLETE": 1,
        "V53_B08C_BEHAVIOR_COMPLETE": 0,
        "V53_B08C_RESERVED_OVERLAP": 0,
        "V53_B08C_CANONICAL_TRAIN_RECORDS": 41,
        "V53_B08C_VALIDATION_TEXT_CREATED": 0,
        "V53_B08C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("B08 completion state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
