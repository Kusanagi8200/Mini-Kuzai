#!/usr/bin/env python3
"""V53 read-only audit for independent reviews of repaired derivatives.

Revalidates the two derivative candidates, verifies the completed derivative
integrity GOGIT history, validates the separate semantic/factual review records,
and emits numeric-only aggregate review metrics.

Passing this audit advances candidates only to eligibility controls. It does
not approve TRAIN, assign a split or complete corpus semantic validation.
"""

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

DERIVATIVE_AUDIT = (
    REPO / "tools/public-audits/smoltalk_v53_derivative_candidates.py"
)
DERIVATIVE_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-DERIVATIVE-CANDIDATES-001.json"
)
REVIEW_DIR = REPO / "reviews/smoltalk-v53/derivative-reviews"

EXPECTED = {
    "V53-DERIV-REVIEW-001-V52-025": {
        "file": "V53-DERIV-REVIEW-001-V52-025.json",
        "derivative_id": "V53-DERIV-001-V52-025",
    },
    "V53-DERIV-REVIEW-002-V51-013": {
        "file": "V53-DERIV-REVIEW-002-V51-013.json",
        "derivative_id": "V53-DERIV-002-V51-013",
    },
}

METRIC_KEYS = {
    "V53_DERIV_REVIEW_TOTAL",
    "V53_DERIV_REVIEW_COMPLETE",
    "V53_DERIV_REVIEW_QUALITY_PASS",
    "V53_DERIV_REVIEW_FACTUAL_PASS",
    "V53_DERIV_REVIEW_COHERENCE_PASS",
    "V53_DERIV_REVIEW_BEHAVIOR_PASS",
    "V53_DERIV_REVIEW_INSTRUCTION_PASS",
    "V53_DERIV_REVIEW_ELIGIBILITY_READY",
    "V53_DERIV_REVIEW_FURTHER_REPAIR",
    "V53_DERIV_REVIEW_NEW_ERRORS",
    "V53_DERIV_REVIEW_TRAIN_APPROVED",
    "V53_DERIV_REVIEW_SPLIT_ASSIGNED",
    "V53_DERIV_REVIEW_SEMANTIC_VALIDATED",
}


def load_module(path, name):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe derivative audit dependency")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load derivative audit dependency")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe derivative review file")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Derivative review must be a JSON object")
    return value


def validate_derivative_prerequisite():
    report = load_json(DERIVATIVE_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id")
        != "PHASE03-SMOLTALK-V53-DERIVATIVE-CANDIDATES-001"
        or report.get("training_authorized") is not False
        or report.get("private_conversation_data_included") is not False
        or metrics.get("V53_DERIVATIVE_TOTAL") != 2
        or metrics.get("V53_DERIVATIVE_SOURCE_MATCHED") != 2
        or metrics.get("V53_DERIVATIVE_REVIEW_PENDING") != 2
        or metrics.get("V53_DERIVATIVE_TRAIN_APPROVED") != 0
        or metrics.get("V53_DERIVATIVE_SPLIT_ASSIGNED") != 0
        or metrics.get("V53_DERIVATIVE_SEMANTIC_VALIDATED") != 0
    ):
        raise RuntimeError("Derivative integrity history is not the expected prerequisite")

    derivative = load_module(DERIVATIVE_AUDIT, "v53_derivative_review_source")
    current = derivative.audit_metrics()
    derivative.require_expected_state(current)


def validate_review(review_id, expected):
    data = load_json(REVIEW_DIR / expected["file"])
    if (
        data.get("schema_version") != "v53-derivative-review-0.1"
        or data.get("review_id") != review_id
        or data.get("derivative_id") != expected["derivative_id"]
        or data.get("review_type") != "INDEPENDENT_SEMANTIC_FACTUAL"
        or data.get("review_status") != "PASS_TO_ELIGIBILITY_CONTROLS"
        or data.get("review_complete") is not True
        or data.get("quality_gate_passed") is not True
        or data.get("further_repair_required") is not False
        or data.get("training_approved") is not False
        or data.get("dataset_split_assigned") is not False
        or data.get("semantic_validation_complete") is not False
        or data.get("next_gate")
        != "PROVENANCE_DEDUP_SEMANTIC_SPLIT_ELIGIBILITY"
    ):
        raise RuntimeError("Derivative review status or safety fields invalid")

    checks = data.get("checks")
    if not isinstance(checks, dict):
        raise RuntimeError("Derivative review checks missing")
    for name in (
        "factual_accuracy",
        "multi_turn_coherence",
        "behavioral_value",
        "instruction_fit",
    ):
        if checks.get(name) != "PASS":
            raise RuntimeError("Derivative review core check did not pass")
    if checks.get("new_error_introduced") is not False:
        raise RuntimeError("Derivative review identifies a newly introduced error")

    evidence = data.get("evidence")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("notes"), list):
        raise RuntimeError("Derivative review evidence missing")

    if expected["derivative_id"] == "V53-DERIV-001-V52-025":
        if (
            evidence.get("verified_mean_f") != 68.0
            or abs(evidence.get("verified_pearson_r", 0) - 0.9386793281621157)
            > 1e-12
            or abs(
                evidence.get("verified_slope_f_per_day", 0)
                - 1.4685314685314685
            ) > 1e-12
            or abs(
                evidence.get("verified_intercept_f", 0)
                - 58.45454545454545
            ) > 1e-12
            or checks.get("uncertainty_calibration") != "PASS"
        ):
            raise RuntimeError("V52-025 derivative review evidence mismatch")
    elif expected["derivative_id"] == "V53-DERIV-002-V51-013":
        if (
            evidence.get("verified_break_even_people") != 5
            or evidence.get("verified_six_people_option1_per_person_usd") != 50
            or evidence.get("verified_solo_option2_savings_usd") != 240
            or checks.get("constraint_handling") != "PASS"
        ):
            raise RuntimeError("V51-013 derivative review evidence mismatch")
    else:
        raise RuntimeError("Unexpected reviewed derivative")

    return data


def audit_metrics():
    if not REVIEW_DIR.is_dir() or REVIEW_DIR.is_symlink():
        raise RuntimeError("Derivative review directory missing")
    actual = {p.name for p in REVIEW_DIR.glob("*.json")}
    expected = {row["file"] for row in EXPECTED.values()}
    if actual != expected:
        raise RuntimeError("Unexpected derivative review JSON file set")

    complete = quality = factual = coherence = behavior = instruction = 0
    eligible = repair = errors = train = split = semantic = 0

    for review_id, definition in EXPECTED.items():
        data = validate_review(review_id, definition)
        checks = data["checks"]
        complete += int(data["review_complete"])
        quality += int(data["quality_gate_passed"])
        factual += int(checks["factual_accuracy"] == "PASS")
        coherence += int(checks["multi_turn_coherence"] == "PASS")
        behavior += int(checks["behavioral_value"] == "PASS")
        instruction += int(checks["instruction_fit"] == "PASS")
        eligible += int(data["review_status"] == "PASS_TO_ELIGIBILITY_CONTROLS")
        repair += int(data["further_repair_required"])
        errors += int(checks["new_error_introduced"])
        train += int(data["training_approved"])
        split += int(data["dataset_split_assigned"])
        semantic += int(data["semantic_validation_complete"])

    metrics = {
        "V53_DERIV_REVIEW_TOTAL": len(EXPECTED),
        "V53_DERIV_REVIEW_COMPLETE": complete,
        "V53_DERIV_REVIEW_QUALITY_PASS": quality,
        "V53_DERIV_REVIEW_FACTUAL_PASS": factual,
        "V53_DERIV_REVIEW_COHERENCE_PASS": coherence,
        "V53_DERIV_REVIEW_BEHAVIOR_PASS": behavior,
        "V53_DERIV_REVIEW_INSTRUCTION_PASS": instruction,
        "V53_DERIV_REVIEW_ELIGIBILITY_READY": eligible,
        "V53_DERIV_REVIEW_FURTHER_REPAIR": repair,
        "V53_DERIV_REVIEW_NEW_ERRORS": errors,
        "V53_DERIV_REVIEW_TRAIN_APPROVED": train,
        "V53_DERIV_REVIEW_SPLIT_ASSIGNED": split,
        "V53_DERIV_REVIEW_SEMANTIC_VALIDATED": semantic,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("Derivative review metric key set changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_DERIV_REVIEW_TOTAL": 2,
        "V53_DERIV_REVIEW_COMPLETE": 2,
        "V53_DERIV_REVIEW_QUALITY_PASS": 2,
        "V53_DERIV_REVIEW_FACTUAL_PASS": 2,
        "V53_DERIV_REVIEW_COHERENCE_PASS": 2,
        "V53_DERIV_REVIEW_BEHAVIOR_PASS": 2,
        "V53_DERIV_REVIEW_INSTRUCTION_PASS": 2,
        "V53_DERIV_REVIEW_ELIGIBILITY_READY": 2,
        "V53_DERIV_REVIEW_FURTHER_REPAIR": 0,
        "V53_DERIV_REVIEW_NEW_ERRORS": 0,
        "V53_DERIV_REVIEW_TRAIN_APPROVED": 0,
        "V53_DERIV_REVIEW_SPLIT_ASSIGNED": 0,
        "V53_DERIV_REVIEW_SEMANTIC_VALIDATED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("Derivative independent-review state differs from expected")


def main():
    validate_derivative_prerequisite()
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
