#!/usr/bin/env python3
"""V53 read-only independent review audit for derivative V53-DERIV-003-V51-002.

Validates the prior A/LOW wave-2 routing report, the derivative candidate,
the separate semantic/factual review record, and the B12 route metadata.
No TRAIN admission or split assignment is performed.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

PRIOR_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-A-LOW-WAVE2-001.json"
)
DERIVATIVE = (
    REPO / "reviews/smoltalk-v53/a-low-wave2/V53-DERIV-003-V51-002.json"
)
REVIEW = (
    REPO / "reviews/smoltalk-v53/a-low-wave2/reviews/"
    "V53-DERIV-REVIEW-003-V51-002.json"
)
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"

METRIC_KEYS = {
    "V53_D3_REVIEW_TOTAL",
    "V53_D3_REVIEW_COMPLETE",
    "V53_D3_QUALITY_PASS",
    "V53_D3_FACTUAL_PASS",
    "V53_D3_COHERENCE_PASS",
    "V53_D3_CREATIVITY_PASS",
    "V53_D3_INSTRUCTION_PASS",
    "V53_D3_ELIGIBILITY_READY",
    "V53_D3_FURTHER_REPAIR",
    "V53_D3_NEW_ERRORS",
    "V53_D3_TRAIN_APPROVED",
    "V53_D3_SPLIT_ASSIGNED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe V53 derivative-003 dependency")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def validate_prior():
    report = load_json(PRIOR_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id") != "PHASE03-SMOLTALK-V53-A-LOW-WAVE2-001"
        or report.get("training_authorized") is not False
        or metrics.get("V53_AW2_INSPECTED") != 3
        or metrics.get("V53_AW2_DERIVATIVE_READY") != 1
        or metrics.get("V53_AW2_DERIVATIVE_CREATED") != 1
        or metrics.get("V53_AW2_B12_ROUTE_VALID") != 1
        or metrics.get("V53_AW2_TRAIN_APPROVED") != 0
    ):
        raise RuntimeError("A/LOW wave-2 prerequisite changed")


def validate_b12_scope():
    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B12", {})
    train = {x.get("group_id"): x.get("scenario_type") for x in block.get("train_groups", [])}
    validation = {x.get("group_id"): x.get("scenario_type") for x in block.get("reserved_validation_groups", [])}
    blind = {x.get("group_id"): x.get("scenario_type") for x in block.get("reserved_blind_test_groups", [])}
    if train.get("sg-b12-01") != "alternative_generation":
        raise RuntimeError("B12 TRAIN route changed")
    if validation.get("sg-b12-03") != "creative_hypothesis_epistemic_control":
        raise RuntimeError("B12 reserved validation route changed")
    if blind.get("sg-b12-04") != "creative_under_constraints":
        raise RuntimeError("B12 reserved blind route changed")


def audit_metrics():
    validate_prior()
    validate_b12_scope()

    derivative = load_json(DERIVATIVE)
    if (
        derivative.get("schema_version") != "v53-derivative-0.1"
        or derivative.get("derivative_id") != "V53-DERIV-003-V51-002"
        or derivative.get("status") != "CANDIDATE_REVIEW_REQUIRED"
        or derivative.get("training_approved") is not False
        or derivative.get("dataset_split_assigned") is not False
        or derivative.get("semantic_validation_complete") is not False
        or derivative.get("routing", {}).get("proposed_primary_behavior") != "B12"
        or derivative.get("routing", {}).get("proposed_train_group") != "sg-b12-01"
        or derivative.get("routing", {}).get("reserved_validation_checked") != "sg-b12-03"
        or derivative.get("routing", {}).get("reserved_blind_checked") != "sg-b12-04"
    ):
        raise RuntimeError("Derivative-003 state changed")

    messages = derivative.get("messages")
    if (
        not isinstance(messages, list)
        or len(messages) != 6
        or [x.get("role") for x in messages] != ["user", "assistant"] * 3
    ):
        raise RuntimeError("Derivative-003 message structure changed")

    review = load_json(REVIEW)
    if (
        review.get("schema_version") != "v53-derivative-review-0.1"
        or review.get("review_id") != "V53-DERIV-REVIEW-003-V51-002"
        or review.get("derivative_id") != "V53-DERIV-003-V51-002"
        or review.get("review_type") != "INDEPENDENT_SEMANTIC_FACTUAL"
        or review.get("review_status") != "PASS_TO_ELIGIBILITY_CONTROLS"
        or review.get("review_complete") is not True
        or review.get("quality_gate_passed") is not True
        or review.get("further_repair_required") is not False
        or review.get("training_approved") is not False
        or review.get("dataset_split_assigned") is not False
        or review.get("semantic_validation_complete") is not False
        or review.get("next_gate") != "PROVENANCE_DEDUP_SEMANTIC_SPLIT_ELIGIBILITY"
    ):
        raise RuntimeError("Derivative-003 independent review state changed")

    checks = review.get("checks", {})
    required = (
        "factual_accuracy",
        "multi_turn_coherence",
        "behavioral_value",
        "instruction_fit",
        "creativity",
        "uncertainty_calibration",
    )
    if any(checks.get(name) != "PASS" for name in required):
        raise RuntimeError("Derivative-003 independent review core check failed")
    if checks.get("new_error_introduced") is not False:
        raise RuntimeError("Derivative-003 review identifies a new error")

    gate = review.get("proposed_next_gate", {})
    if (
        gate.get("primary_behavior") != "B12"
        or gate.get("train_group") != "sg-b12-01"
        or gate.get("scenario_type") != "alternative_generation"
        or gate.get("reserved_validation_group") != "sg-b12-03"
        or gate.get("reserved_blind_group") != "sg-b12-04"
    ):
        raise RuntimeError("Derivative-003 next-gate route changed")

    metrics = {
        "V53_D3_REVIEW_TOTAL": 1,
        "V53_D3_REVIEW_COMPLETE": 1,
        "V53_D3_QUALITY_PASS": 1,
        "V53_D3_FACTUAL_PASS": 1,
        "V53_D3_COHERENCE_PASS": 1,
        "V53_D3_CREATIVITY_PASS": 1,
        "V53_D3_INSTRUCTION_PASS": 1,
        "V53_D3_ELIGIBILITY_READY": 1,
        "V53_D3_FURTHER_REPAIR": 0,
        "V53_D3_NEW_ERRORS": 0,
        "V53_D3_TRAIN_APPROVED": 0,
        "V53_D3_SPLIT_ASSIGNED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("Derivative-003 review metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_D3_REVIEW_TOTAL": 1,
        "V53_D3_REVIEW_COMPLETE": 1,
        "V53_D3_QUALITY_PASS": 1,
        "V53_D3_FACTUAL_PASS": 1,
        "V53_D3_COHERENCE_PASS": 1,
        "V53_D3_CREATIVITY_PASS": 1,
        "V53_D3_INSTRUCTION_PASS": 1,
        "V53_D3_ELIGIBILITY_READY": 1,
        "V53_D3_FURTHER_REPAIR": 0,
        "V53_D3_NEW_ERRORS": 0,
        "V53_D3_TRAIN_APPROVED": 0,
        "V53_D3_SPLIT_ASSIGNED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("Derivative-003 review differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
