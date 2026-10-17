#!/usr/bin/env python3
"""V53 read-only audit for the second LOW-risk A-candidate inspection wave.

Validates three reviewed public SmolTalk A/LOW source cases, their explicit
routing decisions, the B12 semantic-map route for V51-002, and the newly
authored derivative candidate. No TRAIN admission is performed.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

INSPECTION = REPO / "reviews/smoltalk-v53/a-low-wave2/INSPECTION-001.json"
DERIVATIVE = (
    REPO / "reviews/smoltalk-v53/a-low-wave2/V53-DERIV-003-V51-002.json"
)
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"

EXPECTED_SOURCES = {
    "V51-002": (
        REPO / "reviews/smoltalk-v51/cases/002-383f5926f407ae18.md",
        "383f5926f407ae183de348a6aae660e952a4e03887ba2ed275d259969e23fc9a",
    ),
    "V51-007": (
        REPO / "reviews/smoltalk-v51/cases/007-920cde53de1a1873.md",
        "920cde53de1a1873064ab2d16c18bc8789ff1bee4e9f741bc1eaf512b15da899",
    ),
    "V52-008": (
        REPO / "reviews/smoltalk-v52/cases/008-30c78210173e3a4f.md",
        "30c78210173e3a4f51f5aa81b2a0925b98005da687e069238628f5ef228c8f2b",
    ),
}

METRIC_KEYS = {
    "V53_AW2_INSPECTED",
    "V53_AW2_SOURCE_MATCHED",
    "V53_AW2_LOW_RISK_A",
    "V53_AW2_DERIVATIVE_READY",
    "V53_AW2_DEFER_NO_GROUP",
    "V53_AW2_DEFER_RESERVED",
    "V53_AW2_DERIVATIVE_CREATED",
    "V53_AW2_B12_ROUTE_VALID",
    "V53_AW2_TRAIN_APPROVED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe A-wave2 JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def validate_source(case_id, path, source_sha):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("A-wave2 source case missing")
    text = path.read_text(encoding="utf-8")
    cycle = case_id.split("-")[0]
    if (
        source_sha not in text
        or (cycle + " grade: A") not in text
        or (cycle + " factual risk: LOW") not in text
        or (cycle + " instruction fit: GOOD") not in text
    ):
        raise RuntimeError("A-wave2 source review no longer matches expected state")


def validate_b12_route():
    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B12", {})
    train = {row.get("group_id"): row for row in block.get("train_groups", [])}
    validation = {
        row.get("group_id"): row for row in block.get("reserved_validation_groups", [])
    }
    blind = {
        row.get("group_id"): row for row in block.get("reserved_blind_test_groups", [])
    }
    if train.get("sg-b12-01", {}).get("scenario_type") != "alternative_generation":
        raise RuntimeError("B12 TRAIN route changed")
    if (
        validation.get("sg-b12-03", {}).get("scenario_type")
        != "creative_hypothesis_epistemic_control"
    ):
        raise RuntimeError("B12 validation reservation changed")
    if blind.get("sg-b12-04", {}).get("scenario_type") != "creative_under_constraints":
        raise RuntimeError("B12 blind reservation changed")
    return True


def audit_metrics():
    inspection = load_json(INSPECTION)
    if (
        inspection.get("schema_version") != "v53-a-low-inspection-0.1"
        or inspection.get("inspection_id") != "V53-A-LOW-WAVE2-001"
        or inspection.get("inspected") != 3
        or inspection.get("derivative_ready") != 1
        or inspection.get("deferred") != 2
        or inspection.get("train_approved") != 0
    ):
        raise RuntimeError("A-wave2 inspection aggregate state changed")

    rows = inspection.get("population")
    if not isinstance(rows, list) or len(rows) != 3:
        raise RuntimeError("A-wave2 population must contain three cases")

    decisions = {}
    matched = 0
    for row in rows:
        case_id = row.get("case_id")
        if case_id not in EXPECTED_SOURCES:
            raise RuntimeError("Unexpected A-wave2 source case")
        path, source_sha = EXPECTED_SOURCES[case_id]
        if (
            row.get("case_path") != str(path.relative_to(REPO))
            or row.get("source_sha256") != source_sha
            or row.get("grade") != "A"
            or row.get("factual_risk") != "LOW"
        ):
            raise RuntimeError("A-wave2 source metadata changed")
        validate_source(case_id, path, source_sha)
        matched += 1
        decisions[case_id] = row.get("decision")

    if decisions != {
        "V51-002": "DERIVATIVE_READY",
        "V51-007": "DEFER_NO_CLEAN_PRIMARY_TRAIN_GROUP",
        "V52-008": "DEFER_RESERVED_VALIDATION_RISK",
    }:
        raise RuntimeError("A-wave2 routing decisions changed")

    derivative = load_json(DERIVATIVE)
    if (
        derivative.get("schema_version") != "v53-derivative-0.1"
        or derivative.get("derivative_id") != "V53-DERIV-003-V51-002"
        or derivative.get("status") != "CANDIDATE_REVIEW_REQUIRED"
        or derivative.get("training_approved") is not False
        or derivative.get("dataset_split_assigned") is not False
        or derivative.get("semantic_validation_complete") is not False
        or derivative.get("source", {}).get("public_content_sha256")
        != EXPECTED_SOURCES["V51-002"][1]
        or derivative.get("routing", {}).get("proposed_primary_behavior") != "B12"
        or derivative.get("routing", {}).get("proposed_train_group") != "sg-b12-01"
    ):
        raise RuntimeError("A-wave2 derivative state changed")

    messages = derivative.get("messages")
    if (
        not isinstance(messages, list)
        or len(messages) != 6
        or [row.get("role") for row in messages] != ["user", "assistant"] * 3
    ):
        raise RuntimeError("A-wave2 derivative messages invalid")
    if any(
        row.get("origin")
        != ("SOURCE_TEXT_NORMALIZED" if index % 2 == 0 else "DERIVATIVE_REWRITE")
        for index, row in enumerate(messages)
    ):
        raise RuntimeError("A-wave2 derivative message origins invalid")

    metrics = {
        "V53_AW2_INSPECTED": 3,
        "V53_AW2_SOURCE_MATCHED": matched,
        "V53_AW2_LOW_RISK_A": 3,
        "V53_AW2_DERIVATIVE_READY": 1,
        "V53_AW2_DEFER_NO_GROUP": 1,
        "V53_AW2_DEFER_RESERVED": 1,
        "V53_AW2_DERIVATIVE_CREATED": 1,
        "V53_AW2_B12_ROUTE_VALID": int(validate_b12_route()),
        "V53_AW2_TRAIN_APPROVED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("A-wave2 metric key set changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_AW2_INSPECTED": 3,
        "V53_AW2_SOURCE_MATCHED": 3,
        "V53_AW2_LOW_RISK_A": 3,
        "V53_AW2_DERIVATIVE_READY": 1,
        "V53_AW2_DEFER_NO_GROUP": 1,
        "V53_AW2_DEFER_RESERVED": 1,
        "V53_AW2_DERIVATIVE_CREATED": 1,
        "V53_AW2_B12_ROUTE_VALID": 1,
        "V53_AW2_TRAIN_APPROVED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("A-wave2 state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
