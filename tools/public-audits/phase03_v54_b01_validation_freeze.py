#!/usr/bin/env python3
"""Final read-only freeze audit for Phase 03 V54 B01 validation.

A successful GOGIT publication of this audit freezes exactly the reviewed
B01 validation v0.2 batch referenced by the freeze declaration.
The audit does not create BLIND TEST text and does not authorize training.
"""

import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

BATCH_V01 = ROOT / "data/phase-03/validation/validation-batch-b01-v0.1.jsonl"
BATCH_V02 = ROOT / "data/phase-03/validation/validation-batch-b01-v0.2.jsonl"
REVIEW_RESULT = ROOT / "reviews/phase-03-v54/B01-INDEPENDENT-REVIEW-RESULT-001.json"
REVIEW_REPORT = ROOT / "data/phase-03/reports/validation-batch-b01-v0.2-review.json"
MANIFEST = ROOT / "data/phase-03/manifests/validation-batch-b01-v0.2-manifest.json"
FREEZE = ROOT / "data/phase-03/manifests/validation-batch-b01-v0.2-freeze-declaration.json"
SPLITS = ROOT / "data/phase-03/schema/semantic-group-split-manifest-v0.1.json"
BLIND_DIR = ROOT / "data/phase-03/blind-test"

TRAIN_NAMES = [
    "train-pilot-v0.2.jsonl",
    *[
        "train-batch-b{:02d}-{}.jsonl".format(
            n, {8: "v0.5", 12: "v0.3"}.get(n, "v0.2")
        )
        for n in range(1, 19)
    ],
]

EXPECTED_IDS = {"p03-val-b01-000001", "p03-val-b01-000002"}


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe JSON: " + str(path.relative_to(ROOT)))
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe JSONL: " + str(path.relative_to(ROOT)))
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise RuntimeError("Expected JSONL object")
        rows.append(row)
    return rows


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def user_prompts(record):
    return [
        normalize(message["content"])
        for message in record["messages"]
        if message["role"] == "user"
    ]


def validate_review_transition():
    v01 = load_jsonl(BATCH_V01)
    v02 = load_jsonl(BATCH_V02)
    if len(v01) != 2 or len(v02) != 2:
        raise RuntimeError("B01 validation batch count changed")
    if {row.get("id") for row in v01} != EXPECTED_IDS:
        raise RuntimeError("Unexpected B01 v0.1 IDs")
    if {row.get("id") for row in v02} != EXPECTED_IDS:
        raise RuntimeError("Unexpected B01 v0.2 IDs")

    by01 = {row["id"]: row for row in v01}
    by02 = {row["id"]: row for row in v02}
    for identifier in sorted(EXPECTED_IDS):
        a = json.loads(json.dumps(by01[identifier]))
        b = json.loads(json.dumps(by02[identifier]))
        a_prov = a.pop("provenance")
        b_prov = b.pop("provenance")
        if a != b:
            raise RuntimeError("Model-visible or research metadata changed outside provenance")
        if a_prov.get("reviewed") is not False:
            raise RuntimeError("v0.1 must remain unreviewed historical candidate")
        if b_prov.get("reviewed") is not True:
            raise RuntimeError("v0.2 must be reviewed")
        if b_prov.get("review_decision") != "ACCEPT":
            raise RuntimeError("v0.2 review decision changed")
        if b_prov.get("independent_review_id") != "V54-B01-INDEPENDENT-REVIEW-001":
            raise RuntimeError("v0.2 independent review reference changed")

    return v02


def validate_review_evidence():
    review = load_json(REVIEW_RESULT)
    if (
        review.get("review_id") != "V54-B01-INDEPENDENT-REVIEW-001"
        or review.get("review_type") != "INDEPENDENT_SEMANTIC_SPLIT_REVIEW"
        or review.get("independence_scope") != "SEPARATE_EVIDENCE_PASS_PROJECT_CONVENTION"
        or review.get("external_human_review_claimed") is not False
        or review.get("review_complete") is not True
        or review.get("review_status") != "PASS_TO_REVIEWED_BATCH_AND_FREEZE_AUDIT"
        or review.get("candidates_total") != 2
        or review.get("accepted") != 2
        or review.get("revise") != 0
        or review.get("rejected") != 0
        or review.get("held") != 0
        or review.get("semantic_isolation_pass") is not True
        or review.get("training_approved") is not False
        or review.get("validation_frozen") is not False
        or review.get("blind_test_text_created") is not False
    ):
        raise RuntimeError("Independent review evidence changed")

    candidates = review.get("candidate_reviews", {})
    if set(candidates) != EXPECTED_IDS:
        raise RuntimeError("Independent review candidate set changed")
    for identifier in EXPECTED_IDS:
        item = candidates[identifier]
        if (
            item.get("decision") != "ACCEPT"
            or item.get("canonical_identity") != "PASS"
            or item.get("validation_scope") != "PASS"
            or item.get("behavioral_validity") != "PASS"
            or item.get("target_quality") != "PASS"
            or item.get("blind_reservation") != "PASS"
        ):
            raise RuntimeError("Independent review candidate decision changed")


def validate_reports_and_freeze():
    report = load_json(REVIEW_REPORT)
    if (
        report.get("review_status") != "PASS"
        or report.get("record_count") != 2
        or report.get("accepted_without_change") != 2
        or report.get("accepted_after_correction") != 0
        or report.get("rejected") != 0
        or report.get("model_visible_text_changed") is not False
        or report.get("semantic_guard_review") != "PASS"
        or report.get("train_semantic_overlap") is not False
        or report.get("blind_semantic_overlap") is not False
        or report.get("exact_id_collisions") != 0
        or report.get("exact_group_collisions") != 0
        or report.get("exact_user_prompt_matches") != 0
        or report.get("all_records_reviewed") is not True
        or report.get("independent_review_complete") is not True
        or report.get("b01_validation_ready_for_freeze_audit") is not True
        or report.get("validation_frozen") is not False
        or report.get("blind_test_text_created") is not False
        or report.get("training_authorized") is not False
    ):
        raise RuntimeError("B01 review report changed")

    manifest = load_json(MANIFEST)
    if (
        manifest.get("status") != "REVIEWED_PASS_PENDING_FREEZE_AUDIT"
        or manifest.get("split") != "validation"
        or manifest.get("record_count") != 2
        or manifest.get("group_counts") != {"sg-b01-03": 2}
        or manifest.get("provenance_counts") != {"phase03-designed": 2}
        or manifest.get("conversation_modes") != {"single_turn": 1, "multi_turn": 1}
        or manifest.get("all_records_reviewed") is not True
        or manifest.get("all_records_accepted") is not True
        or manifest.get("model_visible_text_changed_from_v0_1") is not False
        or manifest.get("semantic_guard_review") != "PASS"
        or manifest.get("train_semantic_overlap") is not False
        or manifest.get("blind_semantic_overlap") is not False
        or manifest.get("cross_split_exact_collisions") != 0
        or manifest.get("independent_review_complete") is not True
        or manifest.get("validation_frozen") is not False
        or manifest.get("blind_test_text_created") is not False
        or manifest.get("training_authorized") is not False
    ):
        raise RuntimeError("B01 reviewed manifest changed")

    freeze = load_json(FREEZE)
    if (
        freeze.get("declaration_id") != "V54-B01-VALIDATION-FREEZE-001"
        or freeze.get("status") != "PENDING_SUCCESSFUL_GOGIT_AUDIT"
        or freeze.get("target_step_id")
        != "PHASE03-SMOLTALK-V54-B01-VALIDATION-FREEZE-001"
        or freeze.get("target_batch")
        != "data/phase-03/validation/validation-batch-b01-v0.2.jsonl"
        or freeze.get("target_batch_blob_sha")
        != "f5aef6f21f53b0f723bf64c2f2c74a0b749b0681"
        or freeze.get("records") != 2
        or freeze.get("group_id") != "sg-b01-03"
        or freeze.get("independent_review_complete") is not True
        or freeze.get("semantic_guard_pass") is not True
        or freeze.get("structural_integrity_audit_passed") is not True
        or freeze.get("structural_integrity_step_id")
        != "PHASE03-SMOLTALK-V54-B01-VALIDATION-INTEGRITY-001"
        or freeze.get("blind_test_text_created") is not False
        or freeze.get("training_authorized") is not False
    ):
        raise RuntimeError("B01 freeze declaration changed")


def validate_cross_split(v02):
    train = [
        row
        for name in TRAIN_NAMES
        for row in load_jsonl(ROOT / "data/phase-03/train" / name)
    ]
    if len(train) != 107 or len({row.get("id") for row in train}) != 107:
        raise RuntimeError("Canonical TRAIN state changed")
    train_groups = {row.get("group_id") for row in train}
    if len(train_groups) != 29:
        raise RuntimeError("Canonical TRAIN group count changed")

    splits = load_json(SPLITS).get("splits", {})
    if "sg-b01-03" not in splits.get("validation", []):
        raise RuntimeError("B01 validation split reservation changed")
    if "sg-b01-04" not in splits.get("blind_test", []):
        raise RuntimeError("B01 blind split reservation changed")

    ids = {row["id"] for row in train}
    groups = {row["group_id"] for row in train}
    prompts = {
        prompt
        for row in train
        for prompt in user_prompts(row)
    }
    id_hits = sum(row["id"] in ids for row in v02)
    group_hits = sum(row["group_id"] in groups for row in v02)
    prompt_hits = sum(
        prompt in prompts
        for row in v02
        for prompt in user_prompts(row)
    )
    if id_hits or group_hits or prompt_hits:
        raise RuntimeError("Cross-split collision detected at freeze gate")

    blind_files = []
    if BLIND_DIR.exists():
        blind_files = [
            path for path in BLIND_DIR.rglob("*")
            if path.is_file() and not path.is_symlink()
        ]
    if blind_files:
        raise RuntimeError("BLIND TEST text/files exist before authorized authoring")

    return len(train), len(train_groups), id_hits, group_hits, prompt_hits


def audit():
    v02 = validate_review_transition()
    validate_review_evidence()
    validate_reports_and_freeze()
    train_records, train_groups, id_hits, group_hits, prompt_hits = validate_cross_split(v02)

    return dict(sorted({
        "TRAIN_FILES": len(TRAIN_NAMES),
        "TRAIN_RECORDS": train_records,
        "TRAIN_GROUPS": train_groups,
        "VALIDATION_B01_CANDIDATES": len(v02),
        "CROSS_SPLIT_ID_COLLISIONS": id_hits,
        "CROSS_SPLIT_GROUP_COLLISIONS": group_hits,
        "EXACT_USER_PROMPT_MATCHES": prompt_hits,
        "B01_INDEPENDENT_SIGNOFF": 1,
        "B01_VALIDATION_FROZEN": 1,
        "TRAINING_AUTHORIZED": 0,
    }.items()))


def require_expected_state(metrics):
    expected = dict(sorted({
        "TRAIN_FILES": 19,
        "TRAIN_RECORDS": 107,
        "TRAIN_GROUPS": 29,
        "VALIDATION_B01_CANDIDATES": 2,
        "CROSS_SPLIT_ID_COLLISIONS": 0,
        "CROSS_SPLIT_GROUP_COLLISIONS": 0,
        "EXACT_USER_PROMPT_MATCHES": 0,
        "B01_INDEPENDENT_SIGNOFF": 1,
        "B01_VALIDATION_FROZEN": 1,
        "TRAINING_AUTHORIZED": 0,
    }.items()))
    if metrics != expected:
        raise RuntimeError("B01 freeze state differs from expected")


if __name__ == "__main__":
    metrics = audit()
    require_expected_state(metrics)
    print(MARKER)
    for key, value in metrics.items():
        print("{}: {}".format(key, value))
