#!/usr/bin/env python3
"""V53 read-only corpus eligibility audit for repaired SmolTalk derivatives.

This audit revalidates the completed independent derivative-review gate,
recomputes exact and normalized 5-token-shingle duplicate checks against the
current 37-record controlled TRAIN corpus, validates recorded public provenance
and license metadata, and checks manual semantic decisions against the frozen
semantic split exclusion map.

It does not approve TRAIN or assign a dataset split.
"""

import importlib.util
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

REVIEW_AUDIT = REPO / "tools/public-audits/smoltalk_v53_derivative_review.py"
REVIEW_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-DERIVATIVE-REVIEW-001.json"
)
EXCLUSION_MAP = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"
DERIVATIVE_DIR = REPO / "reviews/smoltalk-v53/derivatives"
ELIGIBILITY_DIR = REPO / "reviews/smoltalk-v53/eligibility"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
)

NEAR_DUP_THRESHOLD = 0.20

EXPECTED = {
    "V53-ELIG-001-V52-025": {
        "file": "V53-ELIG-001-V52-025.json",
        "derivative_file": "V53-DERIV-001-V52-025.json",
        "derivative_id": "V53-DERIV-001-V52-025",
        "behavior": "B07",
        "train_group": "sg-b07-01",
        "validation_group": "sg-b07-02",
        "blind_group": "sg-b07-03",
        "validation_collision": True,
        "blind_collision": False,
        "eligibility_status": "NOT_TRAIN_ELIGIBLE_RESERVED_VALIDATION_COLLISION",
    },
    "V53-ELIG-002-V51-013": {
        "file": "V53-ELIG-002-V51-013.json",
        "derivative_file": "V53-DERIV-002-V51-013.json",
        "derivative_id": "V53-DERIV-002-V51-013",
        "behavior": "B08",
        "train_group": "sg-b08-01",
        "validation_group": "sg-b08-03",
        "blind_group": "sg-b08-04",
        "validation_collision": False,
        "blind_collision": False,
        "eligibility_status": "ELIGIBLE_FOR_ADMISSION_DECISION",
    },
}

METRIC_KEYS = {
    "V53_ELIG_TOTAL",
    "V53_ELIG_PROVENANCE_PASS",
    "V53_ELIG_LICENSE_PASS",
    "V53_ELIG_CANONICAL_TRAIN_RECORDS",
    "V53_ELIG_EXACT_DUP_HITS",
    "V53_ELIG_NEAR_DUP_HITS",
    "V53_ELIG_RESERVED_VALIDATION_COLLISIONS",
    "V53_ELIG_SEMANTIC_PASS",
    "V53_ELIG_SEMANTIC_BLOCKED",
    "V53_ELIG_ADMISSION_READY",
    "V53_ELIG_TRAIN_APPROVED",
    "V53_ELIG_SPLIT_ASSIGNED",
}


def load_module(path, name):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe V53 eligibility dependency")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load V53 eligibility dependency")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe V53 eligibility JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V53 eligibility JSON must be an object")
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
        report.get("step_id") != "PHASE03-SMOLTALK-V53-DERIVATIVE-REVIEW-001"
        or report.get("training_authorized") is not False
        or report.get("private_conversation_data_included") is not False
        or metrics.get("V53_DERIV_REVIEW_TOTAL") != 2
        or metrics.get("V53_DERIV_REVIEW_ELIGIBILITY_READY") != 2
        or metrics.get("V53_DERIV_REVIEW_FURTHER_REPAIR") != 0
        or metrics.get("V53_DERIV_REVIEW_NEW_ERRORS") != 0
        or metrics.get("V53_DERIV_REVIEW_TRAIN_APPROVED") != 0
    ):
        raise RuntimeError("Independent derivative review is not the expected prerequisite")

    review = load_module(REVIEW_AUDIT, "v53_elig_review_dependency")
    review.validate_derivative_prerequisite()
    current = review.audit_metrics()
    review.require_expected_state(current)


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
            records.append(
                {
                    "id": identifier,
                    "normalized": normalize(text),
                    "shingles": shingles(text),
                }
            )
    if len(records) != 37 or len(identifiers) != 37:
        raise RuntimeError("Canonical TRAIN population is not the expected 37 records")
    return records


def group_entry(exclusion, behavior, bucket, group_id):
    block = exclusion.get("behaviors", {}).get(behavior)
    if not isinstance(block, dict):
        raise RuntimeError("Eligibility behavior missing from exclusion map")
    entries = block.get(bucket)
    if not isinstance(entries, list):
        raise RuntimeError("Eligibility exclusion-map bucket missing")
    for entry in entries:
        if entry.get("group_id") == group_id:
            return entry
    raise RuntimeError("Eligibility group not found in expected exclusion-map bucket")


def validate_semantic_record(data, definition, exclusion):
    semantic = data.get("semantic_control")
    if not isinstance(semantic, dict):
        raise RuntimeError("Eligibility semantic-control metadata missing")
    if semantic.get("manual_review_required") is not True:
        raise RuntimeError("Manual semantic review must remain required")
    if (
        semantic.get("primary_behavior_considered") != definition["behavior"]
        or semantic.get("train_group_considered") != definition["train_group"]
        or semantic.get("reserved_validation_group") != definition["validation_group"]
        or semantic.get("reserved_blind_group") != definition["blind_group"]
        or semantic.get("reserved_validation_collision")
        is not definition["validation_collision"]
        or semantic.get("reserved_blind_collision")
        is not definition["blind_collision"]
    ):
        raise RuntimeError("Recorded semantic eligibility decision changed")

    train = group_entry(
        exclusion, definition["behavior"], "train_groups", definition["train_group"]
    )
    validation = group_entry(
        exclusion,
        definition["behavior"],
        "reserved_validation_groups",
        definition["validation_group"],
    )
    blind = group_entry(
        exclusion,
        definition["behavior"],
        "reserved_blind_test_groups",
        definition["blind_group"],
    )

    if (
        train.get("scenario_type") != semantic.get("train_scenario")
        or validation.get("scenario_type") != semantic.get("reserved_validation_scenario")
        or blind.get("scenario_type") != semantic.get("reserved_blind_scenario")
    ):
        raise RuntimeError("Recorded semantic scenario names differ from exclusion map")


def validate_eligibility_record(data, eligibility_id, definition, train_records, exclusion):
    if (
        data.get("schema_version") != "v53-eligibility-review-0.1"
        or data.get("eligibility_id") != eligibility_id
        or data.get("derivative_id") != definition["derivative_id"]
        or data.get("review_status") != "COMPLETE"
        or data.get("eligibility_status") != definition["eligibility_status"]
        or data.get("training_approved") is not False
        or data.get("dataset_split_assigned") is not False
        or data.get("admission_decision_made") is not False
    ):
        raise RuntimeError("Eligibility status or safety fields invalid")

    provenance = data.get("provenance")
    if not isinstance(provenance, dict):
        raise RuntimeError("Eligibility provenance missing")
    if (
        provenance.get("status") != "PASS"
        or provenance.get("public_dataset") != "HuggingFaceTB/smol-smoltalk"
        or provenance.get("source_license") != "apache-2.0"
        or not isinstance(provenance.get("source_content_sha256"), str)
        or len(provenance["source_content_sha256"]) != 64
    ):
        raise RuntimeError("Eligibility provenance or license metadata invalid")

    derivative = load_json(DERIVATIVE_DIR / definition["derivative_file"])
    if derivative.get("derivative_id") != definition["derivative_id"]:
        raise RuntimeError("Eligibility derivative identifier mismatch")
    source = derivative.get("source", {})
    if source.get("public_content_sha256") != provenance["source_content_sha256"]:
        raise RuntimeError("Eligibility source lineage mismatch")

    text = conversation_text(derivative)
    normalized = normalize(text)
    shingle_set = shingles(text)

    exact = any(normalized == record["normalized"] for record in train_records)
    scores = [jaccard(shingle_set, record["shingles"]) for record in train_records]
    maximum = max(scores) if scores else 0.0
    near = maximum >= NEAR_DUP_THRESHOLD

    duplicate = data.get("duplicate_control")
    if not isinstance(duplicate, dict):
        raise RuntimeError("Eligibility duplicate-control metadata missing")
    if (
        duplicate.get("canonical_train_records_compared") != 37
        or duplicate.get("exact_duplicate") is not exact
        or duplicate.get("near_duplicate_method")
        != "normalized 5-token shingle Jaccard"
        or duplicate.get("near_duplicate_threshold") != NEAR_DUP_THRESHOLD
        or duplicate.get("near_duplicate_hit") is not near
        or duplicate.get("derivative_cross_duplicate") is not False
        or abs(duplicate.get("maximum_train_jaccard", -1.0) - maximum) > 1e-15
    ):
        raise RuntimeError("Eligibility duplicate-control result changed")

    validate_semantic_record(data, definition, exclusion)

    return {
        "provenance_pass": 1,
        "license_pass": int(provenance["source_license"] == "apache-2.0"),
        "exact_hit": int(exact),
        "near_hit": int(near),
        "validation_collision": int(definition["validation_collision"]),
        "semantic_pass": int(
            not definition["validation_collision"] and not definition["blind_collision"]
        ),
        "semantic_blocked": int(
            definition["validation_collision"] or definition["blind_collision"]
        ),
        "admission_ready": int(
            data["eligibility_status"] == "ELIGIBLE_FOR_ADMISSION_DECISION"
        ),
        "train_approved": int(data["training_approved"]),
        "split_assigned": int(data["dataset_split_assigned"]),
    }


def audit_metrics():
    validate_review_prerequisite()

    if not ELIGIBILITY_DIR.is_dir() or ELIGIBILITY_DIR.is_symlink():
        raise RuntimeError("V53 eligibility directory missing")
    actual = {path.name for path in ELIGIBILITY_DIR.glob("*.json")}
    expected = {definition["file"] for definition in EXPECTED.values()}
    if actual != expected:
        raise RuntimeError("Unexpected V53 eligibility JSON file set")

    exclusion = load_json(EXCLUSION_MAP)
    if (
        exclusion.get("map_version") != "0.1"
        or exclusion.get("status") != "VALIDATED"
        or exclusion.get("rules", {}).get("semantic_meaning_review_required")
        is not True
        or exclusion.get("rules", {}).get(
            "validation_and_blind_groups_are_reserved_semantic_scope"
        ) is not True
    ):
        raise RuntimeError("Semantic exclusion map is not the expected validated policy")

    train_records = load_train_records()

    results = []
    derivatives = []
    for eligibility_id, definition in EXPECTED.items():
        data = load_json(ELIGIBILITY_DIR / definition["file"])
        results.append(
            validate_eligibility_record(
                data, eligibility_id, definition, train_records, exclusion
            )
        )
        derivative = load_json(DERIVATIVE_DIR / definition["derivative_file"])
        derivatives.append(conversation_text(derivative))

    if normalize(derivatives[0]) == normalize(derivatives[1]):
        raise RuntimeError("Derivative candidates are exact duplicates")
    if jaccard(shingles(derivatives[0]), shingles(derivatives[1])) >= NEAR_DUP_THRESHOLD:
        raise RuntimeError("Derivative candidates are near duplicates")

    metrics = {
        "V53_ELIG_TOTAL": len(results),
        "V53_ELIG_PROVENANCE_PASS": sum(row["provenance_pass"] for row in results),
        "V53_ELIG_LICENSE_PASS": sum(row["license_pass"] for row in results),
        "V53_ELIG_CANONICAL_TRAIN_RECORDS": len(train_records),
        "V53_ELIG_EXACT_DUP_HITS": sum(row["exact_hit"] for row in results),
        "V53_ELIG_NEAR_DUP_HITS": sum(row["near_hit"] for row in results),
        "V53_ELIG_RESERVED_VALIDATION_COLLISIONS": sum(
            row["validation_collision"] for row in results
        ),
        "V53_ELIG_SEMANTIC_PASS": sum(row["semantic_pass"] for row in results),
        "V53_ELIG_SEMANTIC_BLOCKED": sum(row["semantic_blocked"] for row in results),
        "V53_ELIG_ADMISSION_READY": sum(row["admission_ready"] for row in results),
        "V53_ELIG_TRAIN_APPROVED": sum(row["train_approved"] for row in results),
        "V53_ELIG_SPLIT_ASSIGNED": sum(row["split_assigned"] for row in results),
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("V53 eligibility metric key set changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_ELIG_TOTAL": 2,
        "V53_ELIG_PROVENANCE_PASS": 2,
        "V53_ELIG_LICENSE_PASS": 2,
        "V53_ELIG_CANONICAL_TRAIN_RECORDS": 37,
        "V53_ELIG_EXACT_DUP_HITS": 0,
        "V53_ELIG_NEAR_DUP_HITS": 0,
        "V53_ELIG_RESERVED_VALIDATION_COLLISIONS": 1,
        "V53_ELIG_SEMANTIC_PASS": 1,
        "V53_ELIG_SEMANTIC_BLOCKED": 1,
        "V53_ELIG_ADMISSION_READY": 1,
        "V53_ELIG_TRAIN_APPROVED": 0,
        "V53_ELIG_SPLIT_ASSIGNED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("V53 corpus eligibility state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
