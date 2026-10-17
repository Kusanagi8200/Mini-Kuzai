#!/usr/bin/env python3
"""V53 read-only audit for completed B08 TRAIN behavior.

Validates the published completion of sg-b08-01, the new sg-b08-02
contradiction-detection variants, semantic guards, and the resulting
45-record canonical TRAIN population.

This audit completes B08 TRAIN coverage only. It does not authorize model
training and does not create validation or blind-test text.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

PRIOR_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-B08-GROUP-COMPLETE-001.json"
)
BATCH = REPO / "data/phase-03/train/train-batch-b08-v0.5.jsonl"
REVIEW = REPO / "data/phase-03/reports/train-batch-b08-v0.5-review.json"
MANIFEST = REPO / "data/phase-03/manifests/train-batch-b08-v0.5-manifest.json"
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.5.jsonl",
)

EXPECTED_SG02_IDS = {
    "p03-train-b08-000005",
    "p03-train-b08-000006",
    "p03-train-b08-000007",
    "p03-train-b08-000008",
}

METRIC_KEYS = {
    "V53_B08D_TOTAL_RECORDS",
    "V53_B08D_SG01_RECORDS",
    "V53_B08D_SG02_RECORDS",
    "V53_B08D_SG01_COMPLETE",
    "V53_B08D_SG02_COMPLETE",
    "V53_B08D_BEHAVIOR_COMPLETE",
    "V53_B08D_RESERVED_OVERLAP",
    "V53_B08D_B11_TEST_OVERLAP",
    "V53_B08D_CANONICAL_TRAIN_RECORDS",
    "V53_B08D_VALIDATION_TEXT_CREATED",
    "V53_B08D_MODEL_TRAINING_AUTHORIZED",
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
        raise RuntimeError("Missing or unsafe TRAIN JSONL")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise RuntimeError("TRAIN row must be an object")
            rows.append(row)
    return rows


def validate_prior():
    report = load_json(PRIOR_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id") != "PHASE03-SMOLTALK-V53-B08-GROUP-COMPLETE-001"
        or report.get("training_authorized") is not False
        or metrics.get("V53_B08C_GROUP_RECORDS") != 4
        or metrics.get("V53_B08C_GROUP_COMPLETE") != 1
        or metrics.get("V53_B08C_BEHAVIOR_COMPLETE") != 0
        or metrics.get("V53_B08C_CANONICAL_TRAIN_RECORDS") != 41
    ):
        raise RuntimeError("Prior sg-b08-01 completion history changed")


def validate_semantic_scope():
    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B08", {})
    train = {x.get("group_id"): x.get("scenario_type") for x in block.get("train_groups", [])}
    validation = {x.get("group_id"): x.get("scenario_type") for x in block.get("reserved_validation_groups", [])}
    blind = {x.get("group_id"): x.get("scenario_type") for x in block.get("reserved_blind_test_groups", [])}
    if train.get("sg-b08-01") != "weak_technical_claim":
        raise RuntimeError("sg-b08-01 semantic scope changed")
    if train.get("sg-b08-02") != "contradiction_detection":
        raise RuntimeError("sg-b08-02 semantic scope changed")
    if validation.get("sg-b08-03") != "unsupported_conclusion":
        raise RuntimeError("B08 validation reservation changed")
    if blind.get("sg-b08-04") != "social_pressure_agreement":
        raise RuntimeError("B08 blind reservation changed")


def validate_batch():
    rows = load_jsonl(BATCH)
    if len(rows) != 8:
        raise RuntimeError("B08 v0.5 must contain eight records")
    groups = {"sg-b08-01": 0, "sg-b08-02": 0}
    sg02_ids = set()
    for row in rows:
        gid = row.get("group_id")
        if gid not in groups:
            raise RuntimeError("Unexpected B08 group in v0.5")
        groups[gid] += 1
        if (
            row.get("split") != "train"
            or row.get("primary_behavior") != "B08"
            or row.get("scenario_type")
            != ("weak_technical_claim" if gid == "sg-b08-01" else "contradiction_detection")
        ):
            raise RuntimeError("B08 record structure changed")
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
            raise RuntimeError("B08 record contains an invalid or empty message")
        if gid == "sg-b08-02":
            sg02_ids.add(row.get("id"))
            if row.get("difficulty") != 3:
                raise RuntimeError("sg-b08-02 difficulty changed")
            provenance = row.get("provenance", {})
            expected_decision = (
                "ACCEPT"
                if row.get("id") == "p03-train-b08-000005"
                else "ACCEPT_AFTER_SERIALIZATION_CORRECTION"
            )
            if (
                provenance.get("source") != "phase03-designed"
                or provenance.get("reviewed") is not True
                or provenance.get("review_decision") != expected_decision
            ):
                raise RuntimeError("sg-b08-02 provenance state invalid")
    if groups != {"sg-b08-01": 4, "sg-b08-02": 4}:
        raise RuntimeError("B08 group balance changed")
    if sg02_ids != EXPECTED_SG02_IDS:
        raise RuntimeError("Unexpected sg-b08-02 ids")
    return groups


def canonical_count():
    ids = []
    for path in TRAIN_FILES:
        for row in load_jsonl(path):
            identifier = row.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            ids.append(identifier)
    if len(ids) != 45 or len(set(ids)) != 45:
        raise RuntimeError("Canonical TRAIN population is not 45 unique records")
    if not EXPECTED_SG02_IDS <= set(ids):
        raise RuntimeError("sg-b08-02 records missing from canonical TRAIN")
    return len(ids)


def audit_metrics():
    validate_prior()
    validate_semantic_scope()
    groups = validate_batch()

    review = load_json(REVIEW)
    if (
        review.get("review_status") != "PASS"
        or review.get("record_count") != 8
        or review.get("inherited_reviewed_records") != 5
        or review.get("corrected_serialization_records") != 3
        or review.get("corrected_record_ids") != [
            "p03-train-b08-000006",
            "p03-train-b08-000007",
            "p03-train-b08-000008",
        ]
        or review.get("serialization_defect_caught_by_prepublication_audit") is not True
        or review.get("semantic_content_changed_from_intended_authoring") is not False
        or review.get("accepted_records") != 8
        or review.get("rejected") != 0
        or review.get("semantic_guard_review") != "PASS"
        or review.get("reserved_validation_overlap") is not False
        or review.get("reserved_blind_test_overlap") is not False
        or review.get("b11_unresolved_contradiction_test_overlap") is not False
        or review.get("sg_b08_01_complete") is not True
        or review.get("sg_b08_02_complete") is not True
        or review.get("b08_train_complete") is not True
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B08 v0.5 review state changed")

    manifest = load_json(MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS"
        or manifest.get("record_count") != 8
        or manifest.get("group_counts") != {"sg-b08-01": 4, "sg-b08-02": 4}
        or manifest.get("serialization_corrections") != 3
        or manifest.get("corrected_record_ids") != [
            "p03-train-b08-000006",
            "p03-train-b08-000007",
            "p03-train-b08-000008",
        ]
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("semantic_leakage_remaining") is not False
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("sg_b08_01_complete") is not True
        or manifest.get("sg_b08_02_complete") is not True
        or manifest.get("b08_train_complete") is not True
        or manifest.get("canonical_train_record_count_after") != 45
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B08 v0.5 manifest state changed")

    metrics = {
        "V53_B08D_TOTAL_RECORDS": 8,
        "V53_B08D_SG01_RECORDS": groups["sg-b08-01"],
        "V53_B08D_SG02_RECORDS": groups["sg-b08-02"],
        "V53_B08D_SG01_COMPLETE": 1,
        "V53_B08D_SG02_COMPLETE": 1,
        "V53_B08D_BEHAVIOR_COMPLETE": 1,
        "V53_B08D_RESERVED_OVERLAP": 0,
        "V53_B08D_B11_TEST_OVERLAP": 0,
        "V53_B08D_CANONICAL_TRAIN_RECORDS": canonical_count(),
        "V53_B08D_VALIDATION_TEXT_CREATED": 0,
        "V53_B08D_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("B08 behavior-complete metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B08D_TOTAL_RECORDS": 8,
        "V53_B08D_SG01_RECORDS": 4,
        "V53_B08D_SG02_RECORDS": 4,
        "V53_B08D_SG01_COMPLETE": 1,
        "V53_B08D_SG02_COMPLETE": 1,
        "V53_B08D_BEHAVIOR_COMPLETE": 1,
        "V53_B08D_RESERVED_OVERLAP": 0,
        "V53_B08D_B11_TEST_OVERLAP": 0,
        "V53_B08D_CANONICAL_TRAIN_RECORDS": 45,
        "V53_B08D_VALIDATION_TEXT_CREATED": 0,
        "V53_B08D_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("B08 behavior-complete state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
