#!/usr/bin/env python3
"""V53 eligibility audit for derivative V53-DERIV-003-V51-002.

Revalidates the completed independent review, recomputes duplicate checks
against the current 45-record canonical TRAIN corpus, validates recorded
public provenance/license metadata, and checks the B12 semantic decision
against the frozen exclusion map.

This audit does not approve TRAIN and does not assign a dataset split.
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

REVIEW_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-DERIV003-REVIEW-001.json"
)
DERIVATIVE = REPO / (
    "reviews/smoltalk-v53/a-low-wave2/V53-DERIV-003-V51-002.json"
)
ELIGIBILITY = REPO / (
    "reviews/smoltalk-v53/a-low-wave2/eligibility/"
    "V53-ELIG-003-V51-002.json"
)
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

NEAR_DUP_THRESHOLD = 0.20

METRIC_KEYS = {
    "V53_D3E_TOTAL",
    "V53_D3E_PROVENANCE_PASS",
    "V53_D3E_LICENSE_PASS",
    "V53_D3E_CANONICAL_TRAIN_RECORDS",
    "V53_D3E_EXACT_DUP_HITS",
    "V53_D3E_NEAR_DUP_HITS",
    "V53_D3E_RESERVED_VALIDATION_COLLISION",
    "V53_D3E_RESERVED_BLIND_COLLISION",
    "V53_D3E_SEMANTIC_PASS",
    "V53_D3E_ADMISSION_READY",
    "V53_D3E_TRAIN_APPROVED",
    "V53_D3E_SPLIT_ASSIGNED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe derivative-003 eligibility dependency")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def normalize(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def shingles(text, size=5):
    tokens = normalize(text).split()
    return {
        " ".join(tokens[index:index + size])
        for index in range(max(0, len(tokens) - size + 1))
    }


def jaccard(left, right):
    if not left and not right:
        return 1.0
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def conversation_text(record):
    messages = record.get("messages")
    if not isinstance(messages, list) or not messages:
        raise RuntimeError("Conversation messages missing")
    parts = []
    for message in messages:
        if not isinstance(message, dict):
            raise RuntimeError("Conversation message malformed")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Conversation content missing")
        parts.append(content)
    return "\n".join(parts)


def validate_review_prerequisite():
    report = load_json(REVIEW_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id") != "PHASE03-SMOLTALK-V53-DERIV003-REVIEW-001"
        or report.get("training_authorized") is not False
        or report.get("private_conversation_data_included") is not False
        or metrics.get("V53_D3_REVIEW_TOTAL") != 1
        or metrics.get("V53_D3_REVIEW_COMPLETE") != 1
        or metrics.get("V53_D3_QUALITY_PASS") != 1
        or metrics.get("V53_D3_ELIGIBILITY_READY") != 1
        or metrics.get("V53_D3_FURTHER_REPAIR") != 0
        or metrics.get("V53_D3_NEW_ERRORS") != 0
        or metrics.get("V53_D3_TRAIN_APPROVED") != 0
        or metrics.get("V53_D3_SPLIT_ASSIGNED") != 0
    ):
        raise RuntimeError("Derivative-003 review prerequisite changed")


def load_train_records():
    records = []
    identifiers = set()
    for path in TRAIN_FILES:
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("Canonical TRAIN file missing or unsafe")
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            identifier = record.get("id")
            if not isinstance(identifier, str) or identifier in identifiers:
                raise RuntimeError("Canonical TRAIN identifier invalid or duplicated")
            identifiers.add(identifier)
            text = conversation_text(record)
            records.append({
                "id": identifier,
                "normalized": normalize(text),
                "shingles": shingles(text),
            })
    if len(records) != 45 or len(identifiers) != 45:
        raise RuntimeError("Canonical TRAIN population is not 45 unique records")
    return records


def group_entry(exclusion, bucket, group_id):
    block = exclusion.get("behaviors", {}).get("B12")
    if not isinstance(block, dict):
        raise RuntimeError("B12 missing from exclusion map")
    entries = block.get(bucket)
    if not isinstance(entries, list):
        raise RuntimeError("B12 exclusion-map bucket missing")
    for entry in entries:
        if entry.get("group_id") == group_id:
            return entry
    raise RuntimeError("Expected B12 group missing")


def audit_metrics():
    validate_review_prerequisite()

    derivative = load_json(DERIVATIVE)
    if (
        derivative.get("derivative_id") != "V53-DERIV-003-V51-002"
        or derivative.get("training_approved") is not False
        or derivative.get("dataset_split_assigned") is not False
        or derivative.get("semantic_validation_complete") is not False
    ):
        raise RuntimeError("Derivative-003 state changed")

    eligibility = load_json(ELIGIBILITY)
    if (
        eligibility.get("schema_version") != "v53-eligibility-review-0.1"
        or eligibility.get("eligibility_id") != "V53-ELIG-003-V51-002"
        or eligibility.get("derivative_id") != "V53-DERIV-003-V51-002"
        or eligibility.get("review_status") != "COMPLETE"
        or eligibility.get("eligibility_status") != "ELIGIBLE_FOR_ADMISSION_DECISION"
        or eligibility.get("training_approved") is not False
        or eligibility.get("dataset_split_assigned") is not False
        or eligibility.get("admission_decision_made") is not False
        or eligibility.get("proposed_train_group_if_admitted") != "sg-b12-01"
        or eligibility.get("next_action") != "ADMISSION_DECISION_REQUIRED"
    ):
        raise RuntimeError("Derivative-003 eligibility state changed")

    provenance = eligibility.get("provenance", {})
    source = derivative.get("source", {})
    if (
        provenance.get("status") != "PASS"
        or provenance.get("public_dataset") != "HuggingFaceTB/smol-smoltalk"
        or provenance.get("source_license") != "apache-2.0"
        or provenance.get("source_content_sha256")
        != "383f5926f407ae183de348a6aae660e952a4e03887ba2ed275d259969e23fc9a"
        or source.get("public_content_sha256") != provenance.get("source_content_sha256")
    ):
        raise RuntimeError("Derivative-003 provenance/license state changed")

    train_records = load_train_records()
    text = conversation_text(derivative)
    normalized = normalize(text)
    shingle_set = shingles(text)
    exact = any(normalized == record["normalized"] for record in train_records)
    scores = [jaccard(shingle_set, record["shingles"]) for record in train_records]
    maximum = max(scores) if scores else 0.0
    near = maximum >= NEAR_DUP_THRESHOLD

    duplicate = eligibility.get("duplicate_control", {})
    if (
        duplicate.get("canonical_train_records_compared") != 45
        or duplicate.get("exact_duplicate") is not exact
        or duplicate.get("near_duplicate_method")
        != "normalized 5-token shingle Jaccard"
        or duplicate.get("near_duplicate_threshold") != NEAR_DUP_THRESHOLD
        or duplicate.get("near_duplicate_hit") is not near
        or abs(duplicate.get("maximum_train_jaccard", -1.0) - maximum) > 1e-15
    ):
        raise RuntimeError("Derivative-003 duplicate-control state changed")

    exclusion = load_json(EXCLUSION)
    if (
        exclusion.get("map_version") != "0.1"
        or exclusion.get("status") != "VALIDATED"
        or exclusion.get("rules", {}).get("semantic_meaning_review_required")
        is not True
    ):
        raise RuntimeError("Semantic exclusion map changed")

    semantic = eligibility.get("semantic_control", {})
    train = group_entry(exclusion, "train_groups", "sg-b12-01")
    validation = group_entry(
        exclusion, "reserved_validation_groups", "sg-b12-03"
    )
    blind = group_entry(
        exclusion, "reserved_blind_test_groups", "sg-b12-04"
    )
    if (
        semantic.get("manual_review_required") is not True
        or semantic.get("primary_behavior_considered") != "B12"
        or semantic.get("train_group_considered") != "sg-b12-01"
        or semantic.get("train_scenario") != train.get("scenario_type")
        or semantic.get("reserved_validation_group") != "sg-b12-03"
        or semantic.get("reserved_validation_scenario")
        != validation.get("scenario_type")
        or semantic.get("reserved_blind_group") != "sg-b12-04"
        or semantic.get("reserved_blind_scenario") != blind.get("scenario_type")
        or semantic.get("reserved_validation_collision") is not False
        or semantic.get("reserved_blind_collision") is not False
    ):
        raise RuntimeError("Derivative-003 semantic eligibility state changed")

    metrics = {
        "V53_D3E_TOTAL": 1,
        "V53_D3E_PROVENANCE_PASS": 1,
        "V53_D3E_LICENSE_PASS": 1,
        "V53_D3E_CANONICAL_TRAIN_RECORDS": len(train_records),
        "V53_D3E_EXACT_DUP_HITS": int(exact),
        "V53_D3E_NEAR_DUP_HITS": int(near),
        "V53_D3E_RESERVED_VALIDATION_COLLISION": 0,
        "V53_D3E_RESERVED_BLIND_COLLISION": 0,
        "V53_D3E_SEMANTIC_PASS": 1,
        "V53_D3E_ADMISSION_READY": 1,
        "V53_D3E_TRAIN_APPROVED": 0,
        "V53_D3E_SPLIT_ASSIGNED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("Derivative-003 eligibility metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_D3E_TOTAL": 1,
        "V53_D3E_PROVENANCE_PASS": 1,
        "V53_D3E_LICENSE_PASS": 1,
        "V53_D3E_CANONICAL_TRAIN_RECORDS": 45,
        "V53_D3E_EXACT_DUP_HITS": 0,
        "V53_D3E_NEAR_DUP_HITS": 0,
        "V53_D3E_RESERVED_VALIDATION_COLLISION": 0,
        "V53_D3E_RESERVED_BLIND_COLLISION": 0,
        "V53_D3E_SEMANTIC_PASS": 1,
        "V53_D3E_ADMISSION_READY": 1,
        "V53_D3E_TRAIN_APPROVED": 0,
        "V53_D3E_SPLIT_ASSIGNED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("Derivative-003 eligibility differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
