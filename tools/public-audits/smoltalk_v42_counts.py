#!/usr/bin/env python3
"""Recompute the public SmolTalk V42 continuity counts without publishing text."""

import json
from collections import Counter
from pathlib import Path

source = Path(
    "/root/Mini-Kuzai/data/external/smol-smoltalk/review/"
    "continuity-candidates-v42.jsonl"
)
counts = Counter()
with source.open(encoding="utf-8") as stream:
    for line in stream:
        if not line.strip():
            continue
        record = json.loads(line)
        assert record["source_record"]["source"] == "smol-magpie-ultra-short"
        assert record["training_approved"] is False
        assert len(record["source_record"]["messages"]) == 6
        counts[record["heuristic_category"]] += 1

expected = {
    "TWO_ANCHORED": 95,
    "PARTIAL_ANCHOR": 24,
    "LOW_LEXICAL_ANCHOR": 9,
}
assert dict(counts) == expected, f"Unexpected counts: {dict(counts)}"
print("##### SECTION RESULTS FOR ASSISTANT ######")
print("TOTAL_CANDIDATS:", sum(counts.values()))
for key in ("TWO_ANCHORED", "PARTIAL_ANCHOR", "LOW_LEXICAL_ANCHOR"):
    print(f"{key}: {counts[key]}")
