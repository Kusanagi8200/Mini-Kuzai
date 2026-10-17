#!/usr/bin/env python3
"""V53 read-only audit for completed B14 and full TRAIN corpus.

Requires the published B13 completion report, validates the authoring-policy
MEDIUM=3 rule, B14 semantic scope and reserved exclusions, the single reviewed
model-visible correction between v0.1 and v0.2, and the resulting 107-record
canonical TRAIN corpus with all 29 TRAIN semantic groups complete.

This audit does not create VALIDATION/BLIND text and does not authorize model
training.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

PRIOR_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-B13-BEHAVIOR-COMPLETE-001.json"
)
POLICY = REPO / "data/phase-03/schema/conversation-authoring-policy-v0.2.json"
COVERAGE = REPO / "data/phase-03/manifests/b14-coverage-target-v0.1.json"
GROUPS = REPO / "data/phase-03/schema/semantic-groups-v0.3.json"
EXCLUSION = REPO / "data/phase-03/schema/semantic-split-exclusion-map-v0.1.json"
BATCH_V01 = REPO / "data/phase-03/train/train-batch-b14-v0.1.jsonl"
BATCH_V02 = REPO / "data/phase-03/train/train-batch-b14-v0.2.jsonl"
REVIEW = REPO / "data/phase-03/reports/train-batch-b14-v0.2-review.json"
MANIFEST = REPO / "data/phase-03/manifests/train-batch-b14-v0.2-manifest.json"

TRAIN_FILES = (
    REPO / "data/phase-03/train/train-pilot-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b01-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b02-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b03-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b04-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b05-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b06-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b07-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b08-v0.5.jsonl",
    REPO / "data/phase-03/train/train-batch-b09-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b10-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b11-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b12-v0.3.jsonl",
    REPO / "data/phase-03/train/train-batch-b13-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b14-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b15-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b16-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b17-v0.2.jsonl",
    REPO / "data/phase-03/train/train-batch-b18-v0.2.jsonl",
)

EXPECTED_IDS = {
    "p03-train-b14-000001",
    "p03-train-b14-000002",
    "p03-train-b14-000003",
}
CORRECTED_ID = "p03-train-b14-000003"

METRIC_KEYS = {
    "V53_B14C_TOTAL_RECORDS",
    "V53_B14C_SG01_RECORDS",
    "V53_B14C_POLICY_TARGET_VALID",
    "V53_B14C_SINGLE_TURN_RECORDS",
    "V53_B14C_REVIEWED_RECORDS",
    "V53_B14C_CORRECTED_RECORDS",
    "V53_B14C_MODEL_VISIBLE_CHANGES",
    "V53_B14C_RESERVED_OVERLAP",
    "V53_B14C_BEHAVIOR_COMPLETE",
    "V53_B14C_CANONICAL_TRAIN_RECORDS",
    "V53_B14C_COMPLETE_TRAIN_GROUPS",
    "V53_B14C_ALL_TRAIN_GROUPS_COMPLETE",
    "V53_B14C_VALIDATION_TEXT_CREATED",
    "V53_B14C_MODEL_TRAINING_AUTHORIZED",
}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B14 JSON")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe B14 JSONL")
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
        != "PHASE03-SMOLTALK-V53-B13-BEHAVIOR-COMPLETE-001"
        or report.get("training_authorized") is not False
        or metrics.get("V53_B13C_BEHAVIOR_COMPLETE") != 1
        or metrics.get("V53_B13C_CANONICAL_TRAIN_RECORDS") != 104
        or metrics.get("V53_B13C_SG01_RECORDS") != 3
        or metrics.get("V53_B13C_MODEL_TRAINING_AUTHORIZED") != 0
    ):
        raise RuntimeError("Published B13 prerequisite missing or changed")


def validate_policy_target():
    policy = load_json(POLICY)
    if (
        policy.get("policy_version") != "0.2"
        or policy.get("status") != "VALIDATED_POLICY_ONLY"
        or policy.get("variant_policy", {}).get("train", {}).get("MEDIUM") != 3
        or policy.get("variant_policy", {}).get("planned_train_records") != 107
        or policy.get("training_authorized") is not False
    ):
        raise RuntimeError("Authoring policy no longer defines MEDIUM=3 / 107 TRAIN")

    target = load_json(COVERAGE)
    if (
        target.get("decision_id") != "B14-COVERAGE-TARGET-001"
        or target.get("status") != "POLICY_DERIVED_BATCH_TARGET"
        or target.get("applies_to_behavior") != "B14"
        or target.get("behavior_name") != "EMOTIONAL EXPRESSION"
        or target.get("behavior_priority") != "MEDIUM"
        or target.get("policy_train_variants_per_group") != 3
        or target.get("global_schema_rule") is not False
        or target.get("b14_target") != {"sg-b14-01": 3, "total": 3}
        or target.get("current_before_completion") != {"sg-b14-01": 0, "total": 0}
        or target.get("records_to_add") != 3
        or target.get("validation_text_created") is not False
        or target.get("blind_test_text_created") is not False
        or target.get("model_training_authorized") is not False
    ):
        raise RuntimeError("B14 policy-derived target changed")
    return True


def validate_semantic_scope():
    groups = load_json(GROUPS)
    by_id = {
        row.get("group_id"): row
        for row in groups.get("groups", [])
        if isinstance(row, dict)
    }
    row = by_id.get("sg-b14-01", {})
    if (
        row.get("split") != "train"
        or row.get("primary_behavior") != "B14"
        or row.get("behavior_name") != "EMOTIONAL EXPRESSION"
        or row.get("behavior_priority") != "MEDIUM"
        or row.get("scenario_type") != "discovery_affect"
        or row.get("knowledge_layers") != ["K4"]
        or row.get("knowledge_status") != ["LAB"]
        or row.get("difficulty") != 2
    ):
        raise RuntimeError("B14 TRAIN semantic scope changed")

    exclusion = load_json(EXCLUSION)
    block = exclusion.get("behaviors", {}).get("B14", {})
    validation = {
        item.get("group_id"): item.get("scenario_type")
        for item in block.get("reserved_validation_groups", [])
    }
    blind = {
        item.get("group_id"): item.get("scenario_type")
        for item in block.get("reserved_blind_test_groups", [])
    }
    if validation.get("sg-b14-02") != "frustration_preference":
        raise RuntimeError("B14 validation reservation changed")
    if blind.get("sg-b14-03") != "emotional_restraint_precision":
        raise RuntimeError("B14 blind reservation changed")


def validate_batches():
    v01 = load_jsonl(BATCH_V01)
    v02 = load_jsonl(BATCH_V02)
    if len(v01) != 3 or len(v02) != 3:
        raise RuntimeError("B14 batches must contain three records")
    if {row.get("id") for row in v01} != EXPECTED_IDS:
        raise RuntimeError("Unexpected B14 v0.1 identifiers")
    if {row.get("id") for row in v02} != EXPECTED_IDS:
        raise RuntimeError("Unexpected B14 v0.2 identifiers")

    by1 = {row["id"]: row for row in v01}
    by2 = {row["id"]: row for row in v02}
    changed = []
    for identifier in sorted(EXPECTED_IDS):
        a = json.loads(json.dumps(by1[identifier]))
        b = json.loads(json.dumps(by2[identifier]))
        a_messages = a.pop("messages")
        b_messages = b.pop("messages")
        if a != b:
            raise RuntimeError("B14 correction changed metadata, not only model-visible text")
        if a_messages != b_messages:
            changed.append(identifier)
            if (
                [m.get("role") for m in a_messages] != ["user", "assistant"]
                or [m.get("role") for m in b_messages] != ["user", "assistant"]
                or a_messages[0] != b_messages[0]
            ):
                raise RuntimeError("B14 correction changed prompt or role structure")
    if changed != [CORRECTED_ID]:
        raise RuntimeError("B14 reviewed correction set changed")

    forbidden_fragment = "I love the contrast"
    corrected_fragment = "the contrast with how regular the signal can be is striking"
    if forbidden_fragment not in by1[CORRECTED_ID]["messages"][1]["content"]:
        raise RuntimeError("Expected B14 draft preference wording missing")
    if forbidden_fragment in by2[CORRECTED_ID]["messages"][1]["content"]:
        raise RuntimeError("Preference-like wording remains in reviewed B14")
    if corrected_fragment not in by2[CORRECTED_ID]["messages"][1]["content"]:
        raise RuntimeError("Expected B14 reviewed correction missing")

    for row in v02:
        if (
            row.get("schema_version") != "0.1"
            or row.get("group_id") != "sg-b14-01"
            or row.get("split") != "train"
            or row.get("language") != "en"
            or row.get("conversation_mode") != "single_turn"
            or row.get("primary_behavior") != "B14"
            or row.get("secondary_behaviors") != []
            or row.get("scenario_type") != "discovery_affect"
            or row.get("knowledge_layers") != ["K4"]
            or row.get("knowledge_status") != ["LAB"]
            or row.get("difficulty") != 2
        ):
            raise RuntimeError("B14 record structure changed")
        messages = row.get("messages")
        if (
            not isinstance(messages, list)
            or len(messages) != 2
            or [message.get("role") for message in messages] != ["user", "assistant"]
            or any(
                not isinstance(message.get("content"), str)
                or not message.get("content").strip()
                for message in messages
            )
        ):
            raise RuntimeError("B14 message structure changed")
        provenance = row.get("provenance", {})
        if (
            provenance.get("source") != "phase03-designed"
            or provenance.get("authoring_method") != "manual"
            or provenance.get("reviewed") is not True
            or provenance.get("review_decision") != "ACCEPT"
        ):
            raise RuntimeError("B14 provenance changed")
    return len(v02), len(changed)


def canonical_state():
    policy = load_json(POLICY)
    inventory = load_json(GROUPS)
    train_groups = {
        row["group_id"]: row
        for row in inventory.get("groups", [])
        if isinstance(row, dict) and row.get("split") == "train"
    }
    if len(train_groups) != 29:
        raise RuntimeError("TRAIN semantic group count changed")

    identifiers = []
    counts = {}
    provenance = {}
    for path in TRAIN_FILES:
        for row in load_jsonl(path):
            identifier = row.get("id")
            group_id = row.get("group_id")
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("Canonical TRAIN id invalid")
            if group_id not in train_groups:
                raise RuntimeError("Canonical TRAIN row points outside TRAIN inventory")
            identifiers.append(identifier)
            counts[group_id] = counts.get(group_id, 0) + 1
            source = row.get("provenance", {}).get("source")
            provenance[source] = provenance.get(source, 0) + 1

    if len(identifiers) != 107 or len(set(identifiers)) != 107:
        raise RuntimeError("Canonical TRAIN population is not 107 unique records")
    if not EXPECTED_IDS <= set(identifiers):
        raise RuntimeError("B14 records missing from canonical TRAIN")
    if provenance != {"phase03-designed": 105, "HuggingFaceTB/smol-smoltalk": 2}:
        raise RuntimeError("Canonical TRAIN provenance counts changed")

    targets = policy.get("variant_policy", {}).get("train", {})
    complete = 0
    for group_id, meta in train_groups.items():
        target = targets.get(meta.get("behavior_priority"))
        if target not in (3, 4):
            raise RuntimeError("Unexpected TRAIN target")
        if counts.get(group_id, 0) != target:
            raise RuntimeError("TRAIN group is not exactly at policy target: " + group_id)
        complete += 1

    return len(identifiers), complete


def audit_metrics():
    validate_prior()
    policy_valid = validate_policy_target()
    validate_semantic_scope()
    record_count, corrected_count = validate_batches()

    review = load_json(REVIEW)
    if (
        review.get("review_status") != "PASS"
        or review.get("record_count") != 3
        or review.get("accepted_without_change") != 2
        or review.get("accepted_after_correction") != 1
        or review.get("rejected") != 0
        or review.get("corrected_record_ids") != [CORRECTED_ID]
        or review.get("model_visible_text_changed") is not True
        or review.get("semantic_guard_review") != "PASS"
        or review.get("same_behavior_reserved_validation_overlap") is not False
        or review.get("same_behavior_reserved_blind_overlap") is not False
        or review.get("cross_behavior_reserved_overlap") is not False
        or review.get("conversation_modes") != {"single_turn": 3, "multi_turn": 0}
        or review.get("group_counts") != {"sg-b14-01": 3}
        or review.get("sg_b14_01_complete") is not True
        or review.get("b14_train_complete") is not True
        or review.get("training_authorized") is not False
    ):
        raise RuntimeError("B14 review state changed")
    if set(review.get("cross_behavior_checks", {})) != {"B05", "B13", "B15"}:
        raise RuntimeError("B14 cross-behavior review coverage changed")

    manifest = load_json(MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS"
        or manifest.get("record_count") != 3
        or manifest.get("group_counts") != {"sg-b14-01": 3}
        or manifest.get("provenance_counts") != {"phase03-designed": 3}
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("semantic_leakage_remaining") is not False
        or manifest.get("model_visible_text_changed") is not True
        or manifest.get("corrected_records") != 1
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("sg_b14_01_current") != 3
        or manifest.get("sg_b14_01_target") != 3
        or manifest.get("sg_b14_01_complete") is not True
        or manifest.get("b14_train_complete") is not True
        or manifest.get("canonical_train_record_count_after") != 107
        or manifest.get("complete_train_groups_after") != 29
        or manifest.get("all_train_groups_complete_after") is not True
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B14 manifest state changed")

    canonical_records, complete_groups = canonical_state()
    metrics = {
        "V53_B14C_TOTAL_RECORDS": record_count,
        "V53_B14C_SG01_RECORDS": record_count,
        "V53_B14C_POLICY_TARGET_VALID": int(policy_valid),
        "V53_B14C_SINGLE_TURN_RECORDS": record_count,
        "V53_B14C_REVIEWED_RECORDS": 3,
        "V53_B14C_CORRECTED_RECORDS": corrected_count,
        "V53_B14C_MODEL_VISIBLE_CHANGES": 1,
        "V53_B14C_RESERVED_OVERLAP": 0,
        "V53_B14C_BEHAVIOR_COMPLETE": 1,
        "V53_B14C_CANONICAL_TRAIN_RECORDS": canonical_records,
        "V53_B14C_COMPLETE_TRAIN_GROUPS": complete_groups,
        "V53_B14C_ALL_TRAIN_GROUPS_COMPLETE": int(complete_groups == 29),
        "V53_B14C_VALIDATION_TEXT_CREATED": 0,
        "V53_B14C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if set(metrics) != METRIC_KEYS:
        raise RuntimeError("B14 metric keys changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_B14C_TOTAL_RECORDS": 3,
        "V53_B14C_SG01_RECORDS": 3,
        "V53_B14C_POLICY_TARGET_VALID": 1,
        "V53_B14C_SINGLE_TURN_RECORDS": 3,
        "V53_B14C_REVIEWED_RECORDS": 3,
        "V53_B14C_CORRECTED_RECORDS": 1,
        "V53_B14C_MODEL_VISIBLE_CHANGES": 1,
        "V53_B14C_RESERVED_OVERLAP": 0,
        "V53_B14C_BEHAVIOR_COMPLETE": 1,
        "V53_B14C_CANONICAL_TRAIN_RECORDS": 107,
        "V53_B14C_COMPLETE_TRAIN_GROUPS": 29,
        "V53_B14C_ALL_TRAIN_GROUPS_COMPLETE": 1,
        "V53_B14C_VALIDATION_TEXT_CREATED": 0,
        "V53_B14C_MODEL_TRAINING_AUTHORIZED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("B14 state differs from expected")


def main():
    metrics = audit_metrics()
    require_expected_state(metrics)
    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
