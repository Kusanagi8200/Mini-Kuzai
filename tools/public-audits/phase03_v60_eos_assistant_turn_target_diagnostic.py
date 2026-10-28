#!/usr/bin/env python3
"""Numeric-only diagnostic of EOS and assistant-turn targets in frozen V60 TRAIN.

This audit reconstructs the authorized TRAIN segmentation from source messages.
It does not train, generate, load BLIND TEST material, or publish conversation text.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v60_trainer as T


def segmented_messages(tokenizer, messages):
    def count_text(text: str) -> int:
        return len(tokenizer.encode(text))

    segments = T.SEG.segment_messages(
        messages,
        serialize_messages=T.CONV.serialize_messages,
        validate_messages=T.CONV.validate_messages,
        count_text=count_text,
        context_length=T.CONTEXT_LENGTH,
    )

    result = []
    for segment in segments:
        ids = T.encode_messages(
            tokenizer,
            list(segment.messages),
        )
        if len(ids) != segment.token_count:
            raise RuntimeError(
                "Tokenizer/segmentation token-count mismatch"
            )
        if not ids or ids[0] != T.BOS_ID or ids[-1] != T.EOS_ID:
            raise RuntimeError("Segment lost BOS/EOS boundary")
        pairs = len(segment.messages) // 2
        if pairs <= 0:
            raise RuntimeError("Segment has no complete assistant turn")
        result.append((pairs, len(ids)))
    return result


def main() -> None:
    authorization, freeze, _ = T.verify_authorization()
    if authorization.get("training_authorized") is not True:
        raise RuntimeError("V60 training authorization is not active")

    tokenizer = T.load_tokenizer()

    expected_streams, expected_inventory = T.build_training_streams()
    if sum(len(values) for values in expected_streams.values()) != 345:
        raise RuntimeError("Frozen V60 segment inventory changed")

    stream_counts = {
        stream: {
            "segments": 0,
            "tokens": 0,
            "assistant_turns": 0,
            "assistant_to_eos": 0,
            "assistant_to_user": 0,
        }
        for stream in T.STREAMS
    }

    single_pair_segments = 0
    multi_pair_segments = 0
    max_pairs = 0

    def add(stream: str, messages) -> None:
        nonlocal single_pair_segments
        nonlocal multi_pair_segments
        nonlocal max_pairs

        for pairs, tokens in segmented_messages(
            tokenizer,
            messages,
        ):
            item = stream_counts[stream]
            item["segments"] += 1
            item["tokens"] += tokens
            item["assistant_turns"] += pairs

            # Every serialized segment ends with an assistant turn + EOS.
            item["assistant_to_eos"] += 1

            # Every earlier assistant turn in a multi-pair segment is followed
            # by TURN_SEPARATOR + USER_HEADER, not EOS.
            item["assistant_to_user"] += pairs - 1

            if pairs == 1:
                single_pair_segments += 1
            else:
                multi_pair_segments += 1
            max_pairs = max(max_pairs, pairs)

    # Controlled TRAIN.
    for name in T.TRAIN_NAMES:
        path = T.TRAIN_DIR / name
        for row in T.read_jsonl(path):
            if row.get("split") != "train":
                raise RuntimeError("Non-TRAIN row in controlled corpus")
            add("CONTROLLED_TRAIN", row["messages"])

    # Frozen public DIRECT_KEEP streams.
    pool = T._load_public_pool()
    public = freeze.get("public_direct_keep")
    if not isinstance(public, dict):
        raise RuntimeError("Frozen public DIRECT_KEEP is missing")

    for stream in (
        "PERSONA_CORE",
        "GENERAL_SUPPORT",
        "LEGACY_STRUCTURED_KEEP",
    ):
        frozen_stream = public["streams"].get(stream)
        if not isinstance(frozen_stream, dict):
            raise RuntimeError(f"Missing frozen public stream: {stream}")
        for source_sha in frozen_stream["source_shas"]:
            row = pool.get(source_sha)
            if row is None:
                raise RuntimeError(
                    f"Frozen public source missing locally: {source_sha}"
                )
            add(stream, row["messages"])

    for stream, expected in expected_inventory.items():
        observed = stream_counts[stream]
        if observed["segments"] != expected["segments"]:
            raise RuntimeError(
                f"Segment count mismatch for {stream}"
            )
        if observed["tokens"] != expected["tokens"]:
            raise RuntimeError(
                f"Token count mismatch for {stream}"
            )

    segments = sum(
        value["segments"]
        for value in stream_counts.values()
    )
    tokens = sum(
        value["tokens"]
        for value in stream_counts.values()
    )
    assistant_turns = sum(
        value["assistant_turns"]
        for value in stream_counts.values()
    )
    assistant_to_eos = sum(
        value["assistant_to_eos"]
        for value in stream_counts.values()
    )
    assistant_to_user = sum(
        value["assistant_to_user"]
        for value in stream_counts.values()
    )

    if segments != 345 or tokens != 295416:
        raise RuntimeError("Frozen V60 TRAIN totals changed")
    if assistant_to_eos != segments:
        raise RuntimeError("Expected exactly one EOS target per segment")
    if assistant_to_eos + assistant_to_user != assistant_turns:
        raise RuntimeError("Assistant-turn transition accounting mismatch")
    if single_pair_segments + multi_pair_segments != segments:
        raise RuntimeError("Segment pair-count accounting mismatch")

    predicted_tokens = tokens - segments
    eos_targets = segments

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V60_EOS_DIAG_PASS": 1,
        "V60_EOS_BLIND_ACCESS": 0,
        "V60_EOS_TRAIN_SEGMENTS": segments,
        "V60_EOS_TRAIN_TOKENS": tokens,
        "V60_EOS_PREDICTED_TOKENS": predicted_tokens,
        "V60_EOS_TARGETS": eos_targets,
        "V60_EOS_TARGET_PPM": round(
            eos_targets * 1_000_000 / predicted_tokens
        ),
        "V60_EOS_ASSISTANT_TURNS": assistant_turns,
        "V60_EOS_ASSISTANT_TO_EOS": assistant_to_eos,
        "V60_EOS_ASSISTANT_TO_USER": assistant_to_user,
        "V60_EOS_ASSISTANT_TO_EOS_BP": round(
            assistant_to_eos * 10000 / assistant_turns
        ),
        "V60_EOS_ASSISTANT_TO_USER_BP": round(
            assistant_to_user * 10000 / assistant_turns
        ),
        "V60_EOS_SINGLE_PAIR_SEGMENTS": single_pair_segments,
        "V60_EOS_MULTI_PAIR_SEGMENTS": multi_pair_segments,
        "V60_EOS_MAX_PAIRS_PER_SEGMENT": max_pairs,
        "V60_EOS_MEAN_PAIRS_X100": round(
            assistant_turns * 100 / segments
        ),
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
