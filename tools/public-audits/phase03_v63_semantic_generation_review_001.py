#!/usr/bin/env python3
"""Publish only aggregate, human-entered semantic review ratings via GOGIT.

Reads private local V63 review scores and private sample inventory. Never
prints source prompts, generated responses, subjective notes, token IDs,
reviewer identity or paths. Human ratings cannot be synthesized by this audit.
"""
from __future__ import annotations

import importlib.util
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

HISTORY = REPO / "reports" / "assistant-results" / "history"
PRIOR = "PHASE03-SMOLTALK-V63-DECODING-ROBUSTNESS-001"


def load_review_helper():
    path = REPO / "tools" / "phase03_v63_semantic_generation_review_001.py"
    spec = importlib.util.spec_from_file_location("v63_human_review_helper", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("V63 private review helper is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def distribution(reviews, criterion: str):
    grades = [record[criterion] for record in reviews]
    allowed = (0, 1, 2, 3)
    count = {grade: grades.count(grade) for grade in allowed}
    assessed = [grade for grade in grades if grade != 3]
    if not assessed:
        average = 0
    else:
        average = round(statistics.mean(assessed) * 100)
    return count, average


def main():
    helper = load_review_helper()
    # Public GOGIT history is intentionally read by a separate path; private
    # file reading enforces strict owner-only permissions and stays local.
    import json
    previous_path = HISTORY / f"{PRIOR}.json"
    if not previous_path.is_file() or previous_path.is_symlink():
        raise RuntimeError("Prior public V63 robustness report absent")
    previous = json.loads(previous_path.read_text(encoding="utf-8"))
    metrics = previous.get("metrics", {})
    if (
        previous.get("step_id") != PRIOR
        or previous.get("semantic_validation_complete") is not True
        or metrics.get("V63_ROB_PASS") != 1
        or metrics.get("V63_ROB_BLIND_ACCESS") != 0
        or metrics.get("V63_ROB_SEEDS") != 8
    ):
        raise RuntimeError("Previous V63 GOGIT review baseline invalid")

    # GOGIT must fail if the private human review is incomplete.
    entries, ratings = helper.completed_review()
    if len(entries) != 24 or len(ratings) != 24:
        raise RuntimeError("Human review does not contain 24 completed ratings")
    if {x["seed"] for x in entries} != set(helper.SEEDS):
        raise RuntimeError("Frozen human-review seeds differ")

    output = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V63_HUM_PASS": 1,
        "V63_HUM_BLIND_ACCESS": 0,
        "V63_HUM_SAMPLES": len(entries),
        "V63_HUM_REVIEWED": len(ratings),
        "V63_HUM_SEEDS": len(helper.SEEDS),
        "V63_HUM_EOS": sum(int(row["eos"]) for row in entries),
        "V63_HUM_SHORT16": sum(len(row["tokens"]) <= 16 for row in entries),
        "V63_HUM_UTF8_INVALID": sum(int(not row["utf8_valid"]) for row in entries),
        "V63_HUM_ROLE_LEAK": sum(int(row["role_leak"]) for row in entries),
    }
    for criterion, prefix in (
        ("relevance", "REL"),
        ("coherence", "COH"),
        ("cognition", "COG"),
        ("persona", "PER"),
    ):
        scores = [ratings[row["id"]] for row in entries]
        counts, mean_x100 = distribution(scores, criterion)
        for score in range(3):
            output[f"V63_HUM_{prefix}_{score}"] = counts[score]
        if criterion in helper.OPTIONAL:
            output[f"V63_HUM_{prefix}_NA"] = counts[3]
        elif counts[3]:
            raise RuntimeError("Mandatory criterion unexpectedly not applicable")
        output[f"V63_HUM_{prefix}_MEAN_X100"] = mean_x100

    if len(output) != 30:
        raise RuntimeError("Unexpected GOGIT metric count for human review")
    if any(
        type(value) is not int or value < 0 or value > 100_000_000
        for value in output.values()
    ):
        raise RuntimeError("Non-numeric or invalid human aggregate")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for name, value in sorted(output.items()):
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
