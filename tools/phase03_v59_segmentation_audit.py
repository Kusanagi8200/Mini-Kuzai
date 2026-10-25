#!/usr/bin/env python3
"""Measure V59 turn-aware segmentation against local public populations."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

V57_PATH = (
    REPO
    / "tools"
    / "phase03_v57_architecture_prep.py"
)

SEGMENTATION_PATH = (
    REPO
    / "mini_kuzai"
    / "phase03_segmentation.py"
)

CONTEXT = 2048


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load {path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


V57 = load_module(
    "phase03_v57_for_v59",
    V57_PATH,
)

SEG = load_module(
    "phase03_segmentation_v59",
    SEGMENTATION_PATH,
)


def summarize(
    rows,
    *,
    count_text,
):
    conversations = 0
    segmented_conversations = 0
    segments = 0
    blocked_conversations = 0
    blocked_pairs = 0
    max_pair_tokens = 0
    source_tokens_segmentable = 0
    segment_tokens = 0

    for row in rows:
        conversations += 1

        messages = row["messages"]

        pair_counts = SEG.pair_token_counts(
            messages,
            serialize_messages=V57.CONV.serialize_messages,
            validate_messages=V57.CONV.validate_messages,
            count_text=count_text,
        )

        max_pair_tokens = max(
            max_pair_tokens,
            max(pair_counts),
        )

        oversized = [
            value
            for value in pair_counts
            if value > CONTEXT
        ]

        if oversized:
            blocked_conversations += 1
            blocked_pairs += len(oversized)
            continue

        source_tokens_segmentable += (
            V57.serialized_length(
                messages,
                count_text,
            )
        )

        parts = SEG.segment_messages(
            messages,
            serialize_messages=V57.CONV.serialize_messages,
            validate_messages=V57.CONV.validate_messages,
            count_text=count_text,
            context_length=CONTEXT,
        )

        segments += len(parts)

        if len(parts) > 1:
            segmented_conversations += 1

        segment_tokens += sum(
            part.token_count
            for part in parts
        )

    overhead = (
        segment_tokens
        - source_tokens_segmentable
    )

    if overhead < 0:
        raise RuntimeError(
            "Unexpected negative segmentation overhead"
        )

    return {
        "conversations":
            conversations,
        "segments":
            segments,
        "segmented_conversations":
            segmented_conversations,
        "blocked_conversations":
            blocked_conversations,
        "blocked_pairs":
            blocked_pairs,
        "max_pair_tokens":
            max_pair_tokens,
        "segment_tokens":
            segment_tokens,
        "overhead_tokens":
            overhead,
    }


def collect_metrics():
    tokenizer = V57.load_tokenizer()

    count_text = V57.make_fast_counter(
        tokenizer
    )

    train = summarize(
        V57.load_train(),
        count_text=count_text,
    )

    v44 = summarize(
        V57.load_v44(),
        count_text=count_text,
    )

    pool = summarize(
        V57.load_pool(),
        count_text=count_text,
    )

    if (
        train["conversations"] != 107
        or train["blocked_conversations"] != 0
        or train["segments"] != 107
    ):
        raise RuntimeError(
            "Controlled TRAIN segmentation invariant failed"
        )

    return {
        "V59_CONTEXT":
            CONTEXT,
        "V59_TRAIN_CONVERSATIONS":
            train["conversations"],
        "V59_TRAIN_SEGMENTS":
            train["segments"],
        "V59_TRAIN_BLOCKED_CONVERSATIONS":
            train["blocked_conversations"],
        "V59_TRAIN_MAX_PAIR_TOKENS":
            train["max_pair_tokens"],
        "V59_V44_CONVERSATIONS":
            v44["conversations"],
        "V59_V44_SEGMENTS":
            v44["segments"],
        "V59_V44_SEGMENTED_CONVERSATIONS":
            v44["segmented_conversations"],
        "V59_V44_BLOCKED_CONVERSATIONS":
            v44["blocked_conversations"],
        "V59_V44_BLOCKED_PAIRS":
            v44["blocked_pairs"],
        "V59_V44_MAX_PAIR_TOKENS":
            v44["max_pair_tokens"],
        "V59_V44_SEGMENT_TOKENS":
            v44["segment_tokens"],
        "V59_V44_OVERHEAD_TOKENS":
            v44["overhead_tokens"],
        "V59_POOL_CONVERSATIONS":
            pool["conversations"],
        "V59_POOL_SEGMENTS":
            pool["segments"],
        "V59_POOL_SEGMENTED_CONVERSATIONS":
            pool["segmented_conversations"],
        "V59_POOL_BLOCKED_CONVERSATIONS":
            pool["blocked_conversations"],
        "V59_POOL_BLOCKED_PAIRS":
            pool["blocked_pairs"],
        "V59_POOL_MAX_PAIR_TOKENS":
            pool["max_pair_tokens"],
        "V59_POOL_SEGMENT_TOKENS":
            pool["segment_tokens"],
        "V59_POOL_OVERHEAD_TOKENS":
            pool["overhead_tokens"],
        "V59_MIX_FINALIZED":
            0,
        "SEMANTIC_VALIDATION_COMPLETE":
            1,
        "TRAINING_AUTHORIZED":
            0,
    }


def main():
    metrics = collect_metrics()

    for key in sorted(metrics):
        print(
            f"{key}: {metrics[key]}"
        )


if __name__ == "__main__":
    main()
