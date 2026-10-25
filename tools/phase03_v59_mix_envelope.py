#!/usr/bin/env python3
"""V59 public training-mix envelope audit.

This is a quantitative decision aid only. It does not approve training.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

V57_PATH = REPO / "tools" / "phase03_v57_architecture_prep.py"
SEG_PATH = REPO / "mini_kuzai" / "phase03_segmentation.py"

V50_QUEUE = Path(
    "/root/Mini-Kuzai/data/external/smol-smoltalk/review/"
    "v50-cognitive-review-priority.jsonl"
)

CONTEXT = 2048
PARAMETERS = 1184512

CONTROLLED_SOURCE_SHAS = {
    "566e0b8c4ed792cc76ad0646a6295b05adab7a8caf37e8b91483982fb80e00c3",
    "383f5926f407ae183de348a6aae660e952a4e03887ba2ed275d259969e23fc9a",
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


V57 = load_module("phase03_v57_for_v59_mix", V57_PATH)
SEG = load_module("phase03_seg_for_v59_mix", SEG_PATH)


def read_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe input: {path}")
    with path.open(encoding="utf-8") as stream:
        for raw in stream:
            if raw.strip():
                yield json.loads(raw)


def main():
    queue = list(read_jsonl(V50_QUEUE))
    if len(queue) != 1139:
        raise RuntimeError("V50 queue population changed")

    queue_by_sha = {
        row["source_content_sha256"]: row
        for row in queue
    }
    if len(queue_by_sha) != 1139:
        raise RuntimeError("Duplicate V50 queue SHA")

    tokenizer = V57.load_tokenizer()
    count_text = V57.make_fast_counter(tokenizer)

    controlled = V57.load_train()
    controlled_tokens = sum(
        V57.serialized_length(row["messages"], count_text)
        for row in controlled
    )
    if controlled_tokens != 24539:
        raise RuntimeError("Controlled TRAIN token count changed")

    populations = {
        "HIGH": [],
        "HIGH_MEDIUM": [],
        "BROAD": [],
    }

    excluded_oversized = 0
    excluded_train_source = 0

    for row in V57.load_v44():
        sha = row["source_content_sha256"]
        q = queue_by_sha.get(sha)
        if q is None:
            raise RuntimeError("V44 candidate absent from V50 queue")

        if sha in CONTROLLED_SOURCE_SHAS:
            excluded_train_source += 1
            continue

        pair_counts = SEG.pair_token_counts(
            row["messages"],
            serialize_messages=V57.CONV.serialize_messages,
            validate_messages=V57.CONV.validate_messages,
            count_text=count_text,
        )

        if max(pair_counts) > CONTEXT:
            excluded_oversized += 1
            continue

        segments = SEG.segment_messages(
            row["messages"],
            serialize_messages=V57.CONV.serialize_messages,
            validate_messages=V57.CONV.validate_messages,
            count_text=count_text,
            context_length=CONTEXT,
        )

        item = {
            "priority": q["priority_hint"],
            "segments": len(segments),
            "tokens": sum(segment.token_count for segment in segments),
        }

        populations["BROAD"].append(item)

        if q["priority_hint"] in ("HIGH", "MEDIUM"):
            populations["HIGH_MEDIUM"].append(item)

        if q["priority_hint"] == "HIGH":
            populations["HIGH"].append(item)

    if excluded_oversized != 3:
        raise RuntimeError("Expected exactly three V44 oversized exclusions")

    if excluded_train_source != 2:
        raise RuntimeError("Expected exactly two controlled-source exclusions")

    def stats(items):
        tokens = sum(row["tokens"] for row in items)
        segments = sum(row["segments"] for row in items)
        return {
            "conversations": len(items),
            "segments": segments,
            "tokens": tokens,
            "tokens_per_param_x1000": (tokens * 1000) // PARAMETERS,
            "combined_tokens": tokens + controlled_tokens,
            "combined_tokens_per_param_x1000":
                ((tokens + controlled_tokens) * 1000) // PARAMETERS,
        }

    high = stats(populations["HIGH"])
    hm = stats(populations["HIGH_MEDIUM"])
    broad = stats(populations["BROAD"])

    broad_priority = {
        key: sum(
            1 for row in populations["BROAD"]
            if row["priority"] == key
        )
        for key in ("HIGH", "MEDIUM", "LOW")
    }

    metrics = {
        "V59_MIX_RAW_V44": 1139,
        "V59_MIX_EXCLUDE_OVERSIZED": excluded_oversized,
        "V59_MIX_EXCLUDE_TRAIN_SOURCE": excluded_train_source,
        "V59_MIX_HIGH_CONVERSATIONS": high["conversations"],
        "V59_MIX_HIGH_SEGMENTS": high["segments"],
        "V59_MIX_HIGH_TOKENS": high["tokens"],
        "V59_MIX_HIGH_TPP_X1000": high["tokens_per_param_x1000"],
        "V59_MIX_HM_CONVERSATIONS": hm["conversations"],
        "V59_MIX_HM_SEGMENTS": hm["segments"],
        "V59_MIX_HM_TOKENS": hm["tokens"],
        "V59_MIX_HM_TPP_X1000": hm["tokens_per_param_x1000"],
        "V59_MIX_BROAD_CONVERSATIONS": broad["conversations"],
        "V59_MIX_BROAD_SEGMENTS": broad["segments"],
        "V59_MIX_BROAD_TOKENS": broad["tokens"],
        "V59_MIX_BROAD_TPP_X1000": broad["tokens_per_param_x1000"],
        "V59_MIX_BROAD_HIGH": broad_priority["HIGH"],
        "V59_MIX_BROAD_MEDIUM": broad_priority["MEDIUM"],
        "V59_MIX_BROAD_LOW": broad_priority["LOW"],
        "V59_MIX_BROAD_PLUS_CONTROLLED_TOKENS": broad["combined_tokens"],
        "V59_MIX_BROAD_PLUS_CONTROLLED_TPP_X1000":
            broad["combined_tokens_per_param_x1000"],
        "V59_MIX_FINALIZED": 0,
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key in sorted(metrics):
        print(f"{key}: {metrics[key]}")


if __name__ == "__main__":
    main()
