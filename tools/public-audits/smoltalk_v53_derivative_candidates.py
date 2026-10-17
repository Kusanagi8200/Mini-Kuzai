#!/usr/bin/env python3
"""V53 read-only audit for the first repaired derivative candidates.

Validates two public-source derivative records created after Gate 3. The audit
checks source lineage, safety locks, message origins, role alternation and the
specific documented corrections. It emits numeric-only aggregate metrics.

No derivative is admitted to TRAIN by this audit.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

DERIVATIVE_DIR = REPO / "reviews/smoltalk-v53/derivatives"
GATE3_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-REPAIR-PLAN-001.json"
)

EXPECTED = {
    "V53-DERIV-001-V52-025": {
        "file": "V53-DERIV-001-V52-025.json",
        "cycle": "V52",
        "source_case": "reviews/smoltalk-v52/cases/025-4bd411ceb95b9b3c.md",
        "source_sha": "4bd411ceb95b9b3c9cafe265405a9522445712ae330fa4af1fc74d76a088cd04",
        "repairs": {"FACTUAL_NUMERIC_FIX", "UNCERTAINTY_CALIBRATION"},
    },
    "V53-DERIV-002-V51-013": {
        "file": "V53-DERIV-002-V51-013.json",
        "cycle": "V51",
        "source_case": "reviews/smoltalk-v51/cases/013-566e0b8c4ed792cc.md",
        "source_sha": "566e0b8c4ed792cc76ad0646a6295b05adab7a8caf37e8b91483982fb80e00c3",
        "repairs": {"WORDING_CONSTRAINT_CLEANUP"},
    },
}

METRIC_KEYS = {
    "V53_DERIVATIVE_TOTAL",
    "V53_DERIVATIVE_SOURCE_MATCHED",
    "V53_DERIVATIVE_USER_SOURCE_TURNS",
    "V53_DERIVATIVE_ASSISTANT_REWRITES",
    "V53_DERIVATIVE_REVIEW_PENDING",
    "V53_DERIVATIVE_TRAIN_APPROVED",
    "V53_DERIVATIVE_SPLIT_ASSIGNED",
    "V53_DERIVATIVE_SEMANTIC_VALIDATED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe V53 derivative file")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("V53 derivative must be a JSON object")
    return data


def validate_gate3_history():
    report = load_json(GATE3_REPORT)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id") != "PHASE03-SMOLTALK-V53-REPAIR-PLAN-001"
        or report.get("training_authorized") is not False
        or report.get("private_conversation_data_included") is not False
        or metrics.get("V53_G3_REPAIR_TOTAL") != 8
        or metrics.get("V53_G3_GATE2_PRIORITY_CONFIRMED") != 8
        or metrics.get("V53_G3_TRAIN_APPROVED") != 0
    ):
        raise RuntimeError("V53 Gate 3 history does not satisfy derivative prerequisite")


def validate_source(data, expected):
    source = data.get("source")
    if not isinstance(source, dict):
        raise RuntimeError("Derivative source metadata missing")
    if (
        source.get("review_cycle") != expected["cycle"]
        or source.get("case_path") != expected["source_case"]
        or source.get("public_dataset") != "SmolTalk v0.4"
        or source.get("public_subset") != "smol-magpie-ultra-short"
        or source.get("public_content_sha256") != expected["source_sha"]
    ):
        raise RuntimeError("Derivative source lineage mismatch")

    source_path = REPO / expected["source_case"]
    if not source_path.is_file() or source_path.is_symlink():
        raise RuntimeError("Derivative source case missing")
    source_text = source_path.read_text(encoding="utf-8")
    if expected["source_sha"] not in source_text:
        raise RuntimeError("Derivative source SHA not present in source case")
    if expected["cycle"] + " grade: B" not in source_text:
        raise RuntimeError("Derivative source is no longer the reviewed B case")


def validate_common(data, expected_id, expected):
    if (
        data.get("schema_version") != "v53-derivative-0.1"
        or data.get("derivative_id") != expected_id
        or data.get("status") != "CANDIDATE_REVIEW_REQUIRED"
        or data.get("training_approved") is not False
        or data.get("dataset_split_assigned") is not False
        or data.get("semantic_validation_complete") is not False
        or data.get("public_external_only") is not True
    ):
        raise RuntimeError("Derivative safety or status fields invalid")

    repair = data.get("repair")
    if not isinstance(repair, dict):
        raise RuntimeError("Derivative repair metadata missing")
    if set(repair.get("types", [])) != expected["repairs"]:
        raise RuntimeError("Derivative repair type mismatch")
    if repair.get("plan_path") != "reviews/smoltalk-v53/REPAIR-PLAN-001.md":
        raise RuntimeError("Derivative repair plan lineage mismatch")
    if repair.get("user_text_origin") != "SOURCE_TEXT_NORMALIZED":
        raise RuntimeError("Derivative user text origin invalid")
    if repair.get("assistant_text_origin") != "DERIVATIVE_REWRITE":
        raise RuntimeError("Derivative assistant text origin invalid")

    validate_source(data, expected)

    messages = data.get("messages")
    if not isinstance(messages, list) or len(messages) != 6:
        raise RuntimeError("Derivative must contain exactly six messages")
    if [m.get("role") for m in messages] != ["user", "assistant"] * 3:
        raise RuntimeError("Derivative role alternation invalid")

    for index, message in enumerate(messages):
        if not isinstance(message.get("content"), str) or not message["content"].strip():
            raise RuntimeError("Derivative message content missing")
        expected_origin = (
            "SOURCE_TEXT_NORMALIZED" if index % 2 == 0
            else "DERIVATIVE_REWRITE"
        )
        if message.get("origin") != expected_origin:
            raise RuntimeError("Derivative message origin mismatch")

    return messages


def validate_specific(expected_id, messages):
    assistant = "\n".join(messages[i]["content"] for i in (1, 3, 5))

    if expected_id == "V53-DERIV-001-V52-025":
        required = (
            "mean is exactly 68.0 F",
            "r = 0.939",
            "1.469 F per day",
            "reasonable first model to test",
        )
        forbidden = ("approximately 69",)
    elif expected_id == "V53-DERIV-002-V51-013":
        required = (
            "legally and practically accommodate all five travelers",
            "break-even point is 5 people",
            "room occupancy limits matter",
            "option 2 is cheaper by $240",
        )
        forbidden = ("option 2's competitor",)
    else:
        raise RuntimeError("Unexpected derivative identifier")

    if any(fragment not in assistant for fragment in required):
        raise RuntimeError("Expected derivative repair text missing")
    if any(fragment in assistant for fragment in forbidden):
        raise RuntimeError("Known defective source wording retained")


def audit_metrics():
    if not DERIVATIVE_DIR.is_dir() or DERIVATIVE_DIR.is_symlink():
        raise RuntimeError("V53 derivative directory missing")

    actual_json = {p.name for p in DERIVATIVE_DIR.glob("*.json")}
    expected_json = {row["file"] for row in EXPECTED.values()}
    if actual_json != expected_json:
        raise RuntimeError("Unexpected V53 derivative JSON file set")

    source_matched = 0
    user_turns = 0
    assistant_turns = 0

    for derivative_id, expected in EXPECTED.items():
        data = load_json(DERIVATIVE_DIR / expected["file"])
        messages = validate_common(data, derivative_id, expected)
        validate_specific(derivative_id, messages)
        source_matched += 1
        user_turns += sum(m["origin"] == "SOURCE_TEXT_NORMALIZED" for m in messages)
        assistant_turns += sum(m["origin"] == "DERIVATIVE_REWRITE" for m in messages)

    metrics = {
        "V53_DERIVATIVE_TOTAL": len(EXPECTED),
        "V53_DERIVATIVE_SOURCE_MATCHED": source_matched,
        "V53_DERIVATIVE_USER_SOURCE_TURNS": user_turns,
        "V53_DERIVATIVE_ASSISTANT_REWRITES": assistant_turns,
        "V53_DERIVATIVE_REVIEW_PENDING": len(EXPECTED),
        "V53_DERIVATIVE_TRAIN_APPROVED": 0,
        "V53_DERIVATIVE_SPLIT_ASSIGNED": 0,
        "V53_DERIVATIVE_SEMANTIC_VALIDATED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("V53 derivative metric key set changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_DERIVATIVE_TOTAL": 2,
        "V53_DERIVATIVE_SOURCE_MATCHED": 2,
        "V53_DERIVATIVE_USER_SOURCE_TURNS": 6,
        "V53_DERIVATIVE_ASSISTANT_REWRITES": 6,
        "V53_DERIVATIVE_REVIEW_PENDING": 2,
        "V53_DERIVATIVE_TRAIN_APPROVED": 0,
        "V53_DERIVATIVE_SPLIT_ASSIGNED": 0,
        "V53_DERIVATIVE_SEMANTIC_VALIDATED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("V53 derivative population differs from expected state")


def main():
    validate_gate3_history()
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
