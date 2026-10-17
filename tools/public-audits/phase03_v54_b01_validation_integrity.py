#!/usr/bin/env python3
"""Read-only structural audit for Phase 03 V54 B01 validation candidates.

Does not assess independent semantic quality or authorize a freeze/training.
Prints aggregate counts only; it never prints dialogue text.
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAIN = [
    "train-pilot-v0.2.jsonl",
    *[
        "train-batch-b{:02d}-{}.jsonl".format(
            n, {8: "v0.5", 12: "v0.3"}.get(n, "v0.2")
        ) for n in range(1, 19)
    ],
]
VALIDATION = ROOT / "data/phase-03/validation/validation-batch-b01-v0.1.jsonl"
MANIFEST = ROOT / "data/phase-03/schema/semantic-group-split-manifest-v0.1.json"
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe input: " + str(path.relative_to(ROOT)))
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not all(isinstance(row, dict) for row in rows):
        raise RuntimeError("JSONL row is not an object")
    return rows

def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())

def user_prompts(record):
    return [normalize(m["content"]) for m in record["messages"] if m["role"] == "user"]

def audit():
    train = [row for name in TRAIN for row in load_jsonl(ROOT / "data/phase-03/train" / name)]
    val = load_jsonl(VALIDATION)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["splits"]
    if len(train) != 107 or len({r["id"] for r in train}) != 107:
        raise RuntimeError("Canonical TRAIN count or ID uniqueness changed")
    if len(val) != 2 or {r["id"] for r in val} != {
        "p03-val-b01-000001", "p03-val-b01-000002"
    }:
        raise RuntimeError("B01 validation candidate inventory changed")
    if len({r["group_id"] for r in train}) != 29:
        raise RuntimeError("Canonical TRAIN group count changed")
    if any(r.get("split") != "train" or r.get("group_id") not in manifest["train"] for r in train):
        raise RuntimeError("TRAIN split assignment invalid")
    if any(r.get("split") != "validation" or r.get("group_id") != "sg-b01-03" for r in val):
        raise RuntimeError("VALIDATION split assignment invalid")
    if "sg-b01-03" not in manifest["validation"] or "sg-b01-04" not in manifest["blind_test"]:
        raise RuntimeError("B01 reserved split allocation changed")
    if any(r.get("provenance", {}).get("reviewed") is not False for r in val):
        raise RuntimeError("Unexpected independent review claim")
    for r in train + val:
        if not isinstance(r.get("messages"), list) or not r["messages"]:
            raise RuntimeError("Missing messages")
        for m in r["messages"]:
            if m.get("role") not in ("user", "assistant") or not isinstance(m.get("content"), str) or not m["content"].strip():
                raise RuntimeError("Invalid message")
    ids = {r["id"] for r in train}
    groups = {r["group_id"] for r in train}
    id_hits = sum(r["id"] in ids for r in val)
    group_hits = sum(r["group_id"] in groups for r in val)
    prompts = {s for r in train for s in user_prompts(r)}
    exact_hits = sum(s in prompts for r in val for s in user_prompts(r))
    if id_hits or group_hits or exact_hits:
        raise RuntimeError("Cross-split collision detected")
    return {
        "TRAIN_FILES": len(TRAIN),
        "TRAIN_RECORDS": len(train),
        "TRAIN_GROUPS": len(groups),
        "VALIDATION_B01_CANDIDATES": len(val),
        "CROSS_SPLIT_ID_COLLISIONS": id_hits,
        "CROSS_SPLIT_GROUP_COLLISIONS": group_hits,
        "EXACT_USER_PROMPT_MATCHES": exact_hits,
        "B01_INDEPENDENT_SIGNOFF": 0,
        "B01_VALIDATION_FROZEN": 0,
        "TRAINING_AUTHORIZED": 0,
    }

if __name__ == "__main__":
    metrics = audit()
    print(MARKER)
    for key, value in sorted(metrics.items()):
        print("{}: {}".format(key, value))
