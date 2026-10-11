#!/usr/bin/env python3
"""V47 read-only integrity gate for the LOCAL V46 public-SmolTalk review queue.

This is an inventory audit, not a qualitative review or TRAIN approval.
All source conversations remain on fhc2; only numeric counts go to gogit.
"""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path("/root/Mini-Kuzai/data/external/smol-smoltalk")
POOL = ROOT / "candidates/external-candidate-pool-v0.4.jsonl"
V44 = ROOT / "review/stratified-candidates-v44.jsonl"
V46_QUEUE = ROOT / "review/v46-manual-review-queue.jsonl"
V46_SUMMARY = ROOT / "review/v46-heuristic-summary.json"

EXPECTED_SOURCES = {
    "smol-magpie-ultra-short": 5000,
    "openhermes-50k": 1500,
    "self-oss-instruct": 1000,
    "explore-instruct-rewrite": 500,
}
CATEGORIES = {
    "FOLLOWUP", "WRITING", "CREATIVE", "FACTUAL_QA",
    "MATHEMATICS", "PROGRAMMING", "PRACTICAL_ADVICE", "GENERAL_OTHER",
}
REASONS = {"BASE": 32, "RELABEL": 12, "RESCUE": 24}
SHA = re.compile(r"[0-9a-f]{64}\Z")


def records(path):
    if not path.is_file():
        raise RuntimeError("Missing required local public-SmolTalk audit input")
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def validate_messages(messages):
    if not isinstance(messages, list) or len(messages) not in (2, 4, 6):
        raise RuntimeError("Invalid conversation structure")
    if [m.get("role") for m in messages] != ["user", "assistant"] * (len(messages) // 2):
        raise RuntimeError("Invalid dialogue roles")
    if any(not isinstance(m.get("content"), str) or not m["content"].strip()
           for m in messages):
        raise RuntimeError("Empty or invalid dialogue content")


def main():
    if not V46_SUMMARY.is_file():
        raise RuntimeError("Missing V46 summary")
    summary = json.loads(V46_SUMMARY.read_text(encoding="utf-8"))
    if (
        summary.get("step") != "PHASE03-SMOLTALK-V46"
        or summary.get("source_records") != 8000
        or summary.get("v44_selected") != 1139
        or summary.get("manual_review_queue_total") != 68
        or summary.get("manual_review_queue_by_reason") != REASONS
        or summary.get("review_complete") is not False
        or summary.get("training_approved") is not False
    ):
        raise RuntimeError("V46 audit summary mismatch")

    public_pool = {}
    by_source = Counter()
    for rec in records(POOL):
        sha = rec.get("content_sha256")
        source = rec.get("source")
        messages = rec.get("messages")
        if (not isinstance(sha, str) or not SHA.fullmatch(sha)
            or sha in public_pool or source not in EXPECTED_SOURCES):
            raise RuntimeError("Public reservoir identity check failed")
        validate_messages(messages)
        public_pool[sha] = (source, messages)
        by_source[source] += 1
    if len(public_pool) != 8000 or by_source != EXPECTED_SOURCES:
        raise RuntimeError("Unexpected public reservoir")

    v44 = {}
    for rec in records(V44):
        sha = rec.get("source_content_sha256")
        label = rec.get("heuristic_category")
        if (
            sha in v44 or sha not in public_pool or label not in CATEGORIES
            or rec.get("source_dataset") != public_pool[sha][0]
            or rec.get("messages") != public_pool[sha][1]
            or rec.get("training_approved") is not False
            or rec.get("semantic_validation_complete") is not False
            or rec.get("dataset_split_assigned") is not False
        ):
            raise RuntimeError("V44 provisional selection integrity failed")
        v44[sha] = label
    if len(v44) != 1139:
        raise RuntimeError("Unexpected V44 selection size")

    reasons = Counter()
    baseline_labels = Counter()
    seen = set()
    checked = 0
    for row in records(V46_QUEUE):
        sha = row.get("source_content_sha256")
        reason = row.get("review_queue_reason")
        v44_selected = row.get("v44_selected")
        v44_label = row.get("v44_category")
        flagged = row.get("broad_creative_signal")
        if (
            sha in seen or sha not in public_pool or reason not in REASONS
            or row.get("source_dataset") != public_pool[sha][0]
            or row.get("messages_original") != public_pool[sha][1]
            or type(v44_selected) is not bool or type(flagged) is not bool
            or row.get("review_decision") != "UNREVIEWED"
            or row.get("semantic_validation_complete") is not False
            or row.get("factual_validation_complete") is not False
            or row.get("training_approved") is not False
            or row.get("dataset_split_assigned") is not False
        ):
            raise RuntimeError("V46 review-queue integrity or status failed")
        if v44_selected is not (sha in v44):
            raise RuntimeError("V44 selection flag mismatch")
        if v44_label != v44.get(sha):
            raise RuntimeError("V44 category flag mismatch")
        if reason == "BASE":
            if not v44_selected or v44_label not in CATEGORIES:
                raise RuntimeError("Invalid baseline queue entry")
            baseline_labels[v44_label] += 1
        elif reason == "RELABEL":
            if not v44_selected or v44_label == "CREATIVE" or not flagged:
                raise RuntimeError("Invalid relabel queue entry")
        else:
            if v44_selected or v44_label is not None or not flagged:
                raise RuntimeError("Invalid recovery queue entry")
        seen.add(sha)
        reasons[reason] += 1
        checked += 1

    if (checked != 68 or reasons != REASONS
        or baseline_labels != {category: 4 for category in CATEGORIES}):
        raise RuntimeError("V46 queue distribution mismatch")

    # Every condition above passed. A status of UNREVIEWED is not a
    # pedagogical acceptance, and no TRAIN or dataset-split changes occur.
    metrics = {
        "TOTAL_SOURCE": len(public_pool),
        "TOTAL_CANDIDATS": len(v44),
        "V47_QUEUE_TOTAL": checked,
        "V47_BASELINE": reasons["BASE"],
        "V47_RECLASS": reasons["RELABEL"],
        "V47_RESCUE": reasons["RESCUE"],
        "V47_PRIORITY": reasons["RELABEL"] + reasons["RESCUE"],
        "V47_UNREVIEWED": checked,
        "V47_SOURCE_MATCHED": checked,
        "V47_TRAIN_APPROVED": 0,
    }
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
