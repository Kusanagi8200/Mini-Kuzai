#!/usr/bin/env python3
"""V56.3 + V56.4 tokenizer benchmark.

Uses only:

- canonical Phase 03 TRAIN model-visible messages;
- public SmolTalk v0.4 model-visible messages.

Does not read VALIDATION, BLIND TEST or private conversation material.

The optimized trainer implemented here is required to reproduce the exact
deterministic merge order of ByteBPETokenizer.train while avoiding repeated
full-corpus rescans for every merge.

The maximum BPE model is trained once per pretokenizer. Smaller vocabulary
candidates are exact merge-prefix derivatives.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

TOKENIZER_PATH = (
    REPO
    / "mini_kuzai"
    / "tokenizer_v56.py"
)

SPEC = importlib.util.spec_from_file_location(
    "mini_kuzai_tokenizer_v56_benchmark",
    TOKENIZER_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        "Unable to load tokenizer_v56.py"
    )

TOK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = TOK
SPEC.loader.exec_module(TOK)


ByteBPETokenizer = TOK.ByteBPETokenizer
ByteTokenizer = TOK.ByteTokenizer
MergeRule = TOK.MergeRule

BASE_VOCAB_SIZE = TOK.BASE_VOCAB_SIZE
PRETOKENIZER_WHITESPACE = (
    TOK.PRETOKENIZER_WHITESPACE
)
PRETOKENIZER_UNICODE = (
    TOK.PRETOKENIZER_UNICODE
)

TRAIN_DIR = (
    REPO / "data/phase-03/train"
)

SMOLTALK_POOL = Path(
    "/root/Mini-Kuzai/data/external/"
    "smol-smoltalk/candidates/"
    "external-candidate-pool-v0.4.jsonl"
)

REPORT_PATH = (
    REPO
    / "data/phase-03/reports/"
    "tokenizer-benchmark-v56.json"
)

MODEL_DIR = (
    REPO
    / "data/phase-03/tokenizers/"
    "v56-candidates"
)

TARGETS = (
    512,
    1024,
    2048,
)

TRAIN_NAMES = [
    "train-pilot-v0.2.jsonl",
    *[
        "train-batch-b{:02d}-{}.jsonl".format(
            number,
            {
                8: "v0.5",
                12: "v0.3",
            }.get(number, "v0.2"),
        )
        for number in range(1, 19)
    ],
]

EXPECTED_SMOLTALK_SOURCES = {
    "smol-magpie-ultra-short": 5000,
    "openhermes-50k": 1500,
    "self-oss-instruct": 1000,
    "explore-instruct-rewrite": 500,
}


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(
            f"Missing or unsafe JSONL: {path}"
        )

    rows = []

    with path.open(
        encoding="utf-8"
    ) as stream:
        for raw in stream:
            if raw.strip():
                value = json.loads(raw)

                if not isinstance(value, dict):
                    raise RuntimeError(
                        f"Invalid JSON object: {path}"
                    )

                rows.append(value)

    return rows


def valid_messages(messages):
    return (
        isinstance(messages, list)
        and bool(messages)
        and all(
            isinstance(message, dict)
            and message.get("role")
            in {"user", "assistant"}
            and isinstance(
                message.get("content"),
                str,
            )
            and message["content"].strip()
            for message in messages
        )
    )


def load_learning_corpus():
    train_rows = []

    for name in TRAIN_NAMES:
        train_rows.extend(
            load_jsonl(
                TRAIN_DIR / name
            )
        )

    if len(TRAIN_NAMES) != 19:
        raise RuntimeError(
            "Canonical TRAIN file set changed"
        )

    if len(train_rows) != 107:
        raise RuntimeError(
            "Canonical TRAIN record count changed"
        )

    if (
        len(
            {
                row.get("id")
                for row in train_rows
            }
        )
        != 107
    ):
        raise RuntimeError(
            "Canonical TRAIN IDs changed"
        )

    if (
        len(
            {
                row.get("group_id")
                for row in train_rows
            }
        )
        != 29
    ):
        raise RuntimeError(
            "Canonical TRAIN groups changed"
        )

    texts = []

    for row in train_rows:
        if row.get("split") != "train":
            raise RuntimeError(
                "Non-TRAIN row in learning corpus"
            )

        messages = row.get("messages")

        if not valid_messages(messages):
            raise RuntimeError(
                "Invalid canonical TRAIN messages"
            )

        texts.extend(
            message["content"]
            for message in messages
        )

    train_message_count = len(texts)

    if train_message_count != 248:
        raise RuntimeError(
            "Canonical TRAIN message count changed"
        )

    if (
        SMOLTALK_POOL.resolve()
        .is_relative_to(REPO.resolve())
    ):
        raise RuntimeError(
            "SmolTalk source must remain outside Git"
        )

    if (
        not SMOLTALK_POOL.is_file()
        or SMOLTALK_POOL.is_symlink()
    ):
        raise RuntimeError(
            "SmolTalk reservoir missing or unsafe"
        )

    source_counts = Counter()
    smoltalk_records = 0
    smoltalk_messages = 0
    fingerprints = set()

    with SMOLTALK_POOL.open(
        encoding="utf-8"
    ) as stream:
        for raw in stream:
            if not raw.strip():
                continue

            row = json.loads(raw)

            source = row.get("source")
            fingerprint = row.get(
                "content_sha256"
            )
            messages = row.get("messages")

            if (
                source
                not in EXPECTED_SMOLTALK_SOURCES
            ):
                raise RuntimeError(
                    "Unexpected SmolTalk source"
                )

            if (
                not isinstance(
                    fingerprint,
                    str,
                )
                or len(fingerprint) != 64
            ):
                raise RuntimeError(
                    "Invalid SmolTalk fingerprint"
                )

            if fingerprint in fingerprints:
                raise RuntimeError(
                    "Duplicate SmolTalk fingerprint"
                )

            if not valid_messages(messages):
                raise RuntimeError(
                    "Invalid SmolTalk messages"
                )

            fingerprints.add(fingerprint)

            source_counts[source] += 1
            smoltalk_records += 1

            for message in messages:
                texts.append(
                    message["content"]
                )
                smoltalk_messages += 1

    if smoltalk_records != 8000:
        raise RuntimeError(
            "Unexpected SmolTalk record count"
        )

    if smoltalk_messages != 36002:
        raise RuntimeError(
            "Unexpected SmolTalk message count"
        )

    if (
        dict(source_counts)
        != EXPECTED_SMOLTALK_SOURCES
    ):
        raise RuntimeError(
            "Unexpected SmolTalk source distribution"
        )

    if len(texts) != 36250:
        raise RuntimeError(
            "Unexpected tokenizer learning message count"
        )

    digest = hashlib.sha256()

    for text in texts:
        blob = text.encode("utf-8")

        digest.update(
            len(blob).to_bytes(
                8,
                "big",
            )
        )
        digest.update(blob)

    return {
        "texts": texts,
        "train_records": 107,
        "train_groups": 29,
        "train_messages": train_message_count,
        "smoltalk_records": smoltalk_records,
        "smoltalk_messages": smoltalk_messages,
        "smoltalk_sources": len(
            source_counts
        ),
        "total_messages": len(texts),
        "corpus_sha256": digest.hexdigest(),
    }


def local_pair_counts(sequence):
    return Counter(
        zip(
            sequence,
            sequence[1:],
        )
    )


def train_fast(
    texts,
    *,
    target_vocab_size,
    pretokenizer,
    min_pair_frequency=2,
):
    if target_vocab_size < BASE_VOCAB_SIZE:
        raise ValueError(
            "Target vocabulary is too small"
        )

    sequence_counter = Counter()

    for text in texts:
        for chunk in TOK._split_text(
            text,
            pretokenizer,
        ):
            sequence = (
                TOK._bytes_to_base_ids(
                    chunk.encode("utf-8")
                )
            )

            if sequence:
                sequence_counter[
                    sequence
                ] += 1

    if not sequence_counter:
        raise RuntimeError(
            "Empty tokenizer learning corpus"
        )

    sequences = list(
        sequence_counter.keys()
    )

    frequencies = [
        sequence_counter[sequence]
        for sequence in sequences
    ]

    pair_counts = Counter()
    pair_sequences = defaultdict(set)

    for index, sequence in enumerate(
        sequences
    ):
        local = local_pair_counts(
            sequence
        )

        frequency = frequencies[index]

        for pair, occurrences in (
            local.items()
        ):
            pair_counts[pair] += (
                occurrences * frequency
            )
            pair_sequences[pair].add(
                index
            )

    token_bytes = {
        TOK._base_id(value): bytes(
            [value]
        )
        for value in range(
            TOK.BYTE_COUNT
        )
    }

    heap = []

    def heap_entry(pair):
        return (
            -pair_counts[pair],
            token_bytes[pair[0]]
            + token_bytes[pair[1]],
            pair[0],
            pair[1],
        )

    for pair in pair_counts:
        heapq.heappush(
            heap,
            heap_entry(pair),
        )

    merges = []

    while (
        BASE_VOCAB_SIZE + len(merges)
        < target_vocab_size
    ):
        selected = None

        while heap:
            negative_count, _, left, right = (
                heapq.heappop(heap)
            )

            pair = (
                left,
                right,
            )

            current = pair_counts.get(
                pair,
                0,
            )

            if (
                current > 0
                and -negative_count
                == current
            ):
                selected = (
                    pair,
                    current,
                )
                break

        if selected is None:
            break

        pair, pair_frequency = selected

        if (
            pair_frequency
            < min_pair_frequency
        ):
            break

        new_id = (
            BASE_VOCAB_SIZE
            + len(merges)
        )

        rule = MergeRule(
            left_id=pair[0],
            right_id=pair[1],
            new_id=new_id,
        )

        token_bytes[new_id] = (
            token_bytes[pair[0]]
            + token_bytes[pair[1]]
        )

        affected = list(
            pair_sequences.get(
                pair,
                (),
            )
        )

        touched_pairs = set()

        for index in affected:
            old_sequence = (
                sequences[index]
            )

            old_local = (
                local_pair_counts(
                    old_sequence
                )
            )

            frequency = (
                frequencies[index]
            )

            for old_pair, occurrences in (
                old_local.items()
            ):
                pair_counts[
                    old_pair
                ] -= (
                    occurrences
                    * frequency
                )

                touched_pairs.add(
                    old_pair
                )

                members = pair_sequences.get(
                    old_pair
                )

                if members is not None:
                    members.discard(
                        index
                    )

                    if not members:
                        pair_sequences.pop(
                            old_pair,
                            None,
                        )

                if (
                    pair_counts[
                        old_pair
                    ]
                    <= 0
                ):
                    pair_counts.pop(
                        old_pair,
                        None,
                    )

            new_sequence = (
                TOK._merge_sequence(
                    old_sequence,
                    pair,
                    new_id,
                )
            )

            sequences[index] = (
                new_sequence
            )

            new_local = (
                local_pair_counts(
                    new_sequence
                )
            )

            for new_pair, occurrences in (
                new_local.items()
            ):
                pair_counts[
                    new_pair
                ] += (
                    occurrences
                    * frequency
                )

                pair_sequences[
                    new_pair
                ].add(
                    index
                )

                touched_pairs.add(
                    new_pair
                )

        merges.append(rule)

        for touched in touched_pairs:
            if pair_counts.get(
                touched,
                0,
            ) > 0:
                heapq.heappush(
                    heap,
                    heap_entry(
                        touched
                    ),
                )

        if (
            len(heap)
            > max(
                100000,
                20 * len(
                    pair_counts
                ),
            )
        ):
            heap = [
                heap_entry(pair)
                for pair in pair_counts
                if pair_counts[pair] > 0
            ]

            heapq.heapify(heap)

    return merges


def fast_encode_chunk(
    tokenizer,
    chunk,
):
    sequence = (
        TOK._bytes_to_base_ids(
            chunk.encode("utf-8")
        )
    )

    if len(sequence) < 2:
        return sequence

    ranks = {
        (
            merge.left_id,
            merge.right_id,
        ): (
            rank,
            merge.new_id,
        )
        for rank, merge
        in enumerate(
            tokenizer.merges
        )
    }

    while len(sequence) >= 2:
        selected_pair = None
        selected_rank = None
        selected_new_id = None

        for pair in zip(
            sequence,
            sequence[1:],
        ):
            value = ranks.get(pair)

            if value is None:
                continue

            rank, new_id = value

            if (
                selected_rank is None
                or rank
                < selected_rank
            ):
                selected_pair = pair
                selected_rank = rank
                selected_new_id = new_id

        if selected_pair is None:
            break

        sequence = TOK._merge_sequence(
            sequence,
            selected_pair,
            selected_new_id,
        )

    return sequence


def fast_encode_text(
    tokenizer,
    text,
):
    output = []

    for chunk in TOK._split_text(
        text,
        tokenizer.pretokenizer,
    ):
        output.extend(
            fast_encode_chunk(
                tokenizer,
                chunk,
            )
        )

    return output


def self_test():
    fixture = [
        "Mini-Kuzai is curious.",
        "Mini-Kuzai is curious!",
        "I do not know yet.",
        "hello hello world",
        "café déjà vu",
        "日本語 🤖",
        "a  b   c",
    ] * 5

    for mode in (
        PRETOKENIZER_WHITESPACE,
        PRETOKENIZER_UNICODE,
    ):
        reference = (
            ByteBPETokenizer.train(
                fixture,
                target_vocab_size=320,
                pretokenizer=mode,
                min_pair_frequency=2,
            )
        )

        optimized_merges = train_fast(
            fixture,
            target_vocab_size=320,
            pretokenizer=mode,
            min_pair_frequency=2,
        )

        optimized = ByteBPETokenizer(
            pretokenizer=mode,
            merges=optimized_merges,
        )

        if (
            reference.to_dict()
            != optimized.to_dict()
        ):
            raise RuntimeError(
                "Fast trainer differs from "
                "reference trainer"
            )

        for text in fixture:
            if (
                fast_encode_text(
                    optimized,
                    text,
                )
                != optimized.encode(text)
            ):
                raise RuntimeError(
                    "Fast encoder differs from "
                    "reference encoder"
                )

            if (
                optimized.decode(
                    fast_encode_text(
                        optimized,
                        text,
                    )
                )
                != text
            ):
                raise RuntimeError(
                    "Fast encoder round-trip failed"
                )


def percentile(
    values,
    fraction,
):
    if not values:
        raise ValueError(
            "Empty percentile input"
        )

    ordered = sorted(values)

    index = (
        math.ceil(
            len(ordered)
            * fraction
        )
        - 1
    )

    return ordered[
        max(
            0,
            min(
                index,
                len(ordered) - 1,
            ),
        )
    ]


def benchmark_baseline(texts):
    lengths = [
        len(
            text.encode("utf-8")
        )
        for text in texts
    ]

    total = sum(lengths)

    return {
        "name": "byte_baseline",
        "family": "byte_baseline",
        "target_vocab_size": 259,
        "vocab_size": 259,
        "merges": 0,
        "total_tokens": total,
        "compression_bp": 0,
        "avg_tokens_x100": round(
            total
            * 100
            / len(lengths)
        ),
        "p50_tokens": percentile(
            lengths,
            0.50,
        ),
        "p95_tokens": percentile(
            lengths,
            0.95,
        ),
        "p99_tokens": percentile(
            lengths,
            0.99,
        ),
        "max_tokens": max(lengths),
        "roundtrip_failures": 0,
        "tied_params_per_hidden_dim": 259,
        "untied_params_per_hidden_dim": 518,
        "fingerprint": ByteTokenizer()
        .fingerprint(),
    }


def benchmark_bpe(
    texts,
    *,
    tokenizer,
    name,
    target_vocab_size,
    baseline_tokens,
):
    chunk_cache = {}
    failed_chunks = set()
    lengths = []

    for text in texts:
        length = 0

        for chunk in TOK._split_text(
            text,
            tokenizer.pretokenizer,
        ):
            ids = chunk_cache.get(
                chunk
            )

            if ids is None:
                ids = fast_encode_chunk(
                    tokenizer,
                    chunk,
                )

                chunk_cache[chunk] = ids

                if (
                    tokenizer.decode(ids)
                    != chunk
                ):
                    failed_chunks.add(
                        chunk
                    )

            length += len(ids)

        lengths.append(length)

    total = sum(lengths)

    compression_bp = round(
        (
            1
            - total
            / baseline_tokens
        )
        * 10000
    )

    return {
        "name": name,
        "family": tokenizer.family,
        "target_vocab_size":
            target_vocab_size,
        "vocab_size":
            tokenizer.vocab_size,
        "merges":
            len(tokenizer.merges),
        "total_tokens":
            total,
        "compression_bp":
            compression_bp,
        "avg_tokens_x100": round(
            total
            * 100
            / len(lengths)
        ),
        "p50_tokens": percentile(
            lengths,
            0.50,
        ),
        "p95_tokens": percentile(
            lengths,
            0.95,
        ),
        "p99_tokens": percentile(
            lengths,
            0.99,
        ),
        "max_tokens": max(lengths),
        "roundtrip_failures":
            len(failed_chunks),
        "unique_chunks":
            len(chunk_cache),
        "tied_params_per_hidden_dim":
            tokenizer.vocab_size,
        "untied_params_per_hidden_dim":
            2 * tokenizer.vocab_size,
        "fingerprint":
            tokenizer.fingerprint(),
    }


def mark_pareto(configs):
    for current in configs:
        dominated = False

        for other in configs:
            if other is current:
                continue

            no_more_vocab = (
                other["vocab_size"]
                <= current["vocab_size"]
            )

            no_more_tokens = (
                other["total_tokens"]
                <= current["total_tokens"]
            )

            strictly_better = (
                other["vocab_size"]
                < current["vocab_size"]
                or other["total_tokens"]
                < current["total_tokens"]
            )

            if (
                no_more_vocab
                and no_more_tokens
                and strictly_better
            ):
                dominated = True
                break

        current["pareto"] = (
            not dominated
        )


def write_json(path, value):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(path)


def run_benchmark():
    self_test()

    corpus = load_learning_corpus()

    texts = corpus["texts"]

    baseline = benchmark_baseline(
        texts
    )

    configs = [
        baseline
    ]

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    modes = (
        (
            "whitespace",
            PRETOKENIZER_WHITESPACE,
        ),
        (
            "unicode",
            PRETOKENIZER_UNICODE,
        ),
    )

    max_target = max(TARGETS)

    model_fingerprints = {}

    for short_name, mode in modes:
        max_merges = train_fast(
            texts,
            target_vocab_size=max_target,
            pretokenizer=mode,
            min_pair_frequency=2,
        )

        required_merges = (
            max_target
            - BASE_VOCAB_SIZE
        )

        if (
            len(max_merges)
            < required_merges
        ):
            raise RuntimeError(
                f"{short_name} BPE stopped at "
                f"{BASE_VOCAB_SIZE + len(max_merges)} "
                f"tokens before target {max_target}"
            )

        max_tokenizer = (
            ByteBPETokenizer(
                pretokenizer=mode,
                merges=max_merges,
            )
        )

        model_path = (
            MODEL_DIR
            / (
                "byte-bpe-"
                f"{short_name}-2048.json"
            )
        )

        write_json(
            model_path,
            max_tokenizer.to_dict(),
        )

        model_fingerprints[
            short_name
        ] = (
            max_tokenizer.fingerprint()
        )

        for target in TARGETS:
            merge_count = (
                target
                - BASE_VOCAB_SIZE
            )

            tokenizer = (
                ByteBPETokenizer(
                    pretokenizer=mode,
                    merges=max_merges[
                        :merge_count
                    ],
                )
            )

            if (
                tokenizer.vocab_size
                != target
            ):
                raise RuntimeError(
                    "Derived vocabulary size "
                    "does not match target"
                )

            config = benchmark_bpe(
                texts,
                tokenizer=tokenizer,
                name=(
                    f"byte_bpe_"
                    f"{short_name}_"
                    f"{target}"
                ),
                target_vocab_size=target,
                baseline_tokens=baseline[
                    "total_tokens"
                ],
            )

            configs.append(config)

    if any(
        config["roundtrip_failures"]
        != 0
        for config in configs
    ):
        raise RuntimeError(
            "Tokenizer round-trip failure"
        )

    mark_pareto(configs)

    bpe_configs = configs[1:]

    best_compression = min(
        bpe_configs,
        key=lambda item: (
            item["total_tokens"],
            item["vocab_size"],
            item["name"],
        ),
    )

    best_p95 = min(
        bpe_configs,
        key=lambda item: (
            item["p95_tokens"],
            item["vocab_size"],
            item["total_tokens"],
            item["name"],
        ),
    )

    report = {
        "schema_version":
            "v56-tokenizer-benchmark-1",
        "status":
            "BENCHMARK_AND_COST_COMPARISON_COMPLETE",
        "scope": {
            "train_records":
                corpus["train_records"],
            "train_groups":
                corpus["train_groups"],
            "train_messages":
                corpus["train_messages"],
            "smoltalk_records":
                corpus["smoltalk_records"],
            "smoltalk_messages":
                corpus["smoltalk_messages"],
            "smoltalk_sources":
                corpus["smoltalk_sources"],
            "total_messages":
                corpus["total_messages"],
            "validation_included": False,
            "blind_included": False,
            "private_included": False,
            "learning_corpus_sha256":
                corpus["corpus_sha256"],
        },
        "targets": list(TARGETS),
        "method": {
            "base_vocab_size":
                BASE_VOCAB_SIZE,
            "min_pair_frequency": 2,
            "max_training_target":
                max_target,
            "smaller_candidates":
                "exact_prefix_of_maximum_merge_table",
            "roundtrip_check":
                "all_unique_pretokenized_chunks",
            "parameter_cost":
                "vocabulary parameters per hidden dimension",
        },
        "max_model_fingerprints":
            model_fingerprints,
        "configs": configs,
        "summary": {
            "config_count":
                len(configs),
            "pareto_config_count":
                sum(
                    int(
                        config["pareto"]
                    )
                    for config in configs
                ),
            "roundtrip_failures":
                sum(
                    config[
                        "roundtrip_failures"
                    ]
                    for config in configs
                ),
            "best_compression_config":
                best_compression["name"],
            "best_p95_config":
                best_p95["name"],
        },
        "tokenizer_finalized": False,
        "vocabulary_frozen": False,
        "architecture_selected": False,
        "training_authorized": False,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    return report


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--self-test",
        action="store_true",
    )

    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("V56 BENCHMARK SELF-TEST: OK")
        return

    report = run_benchmark()

    print(
        "V56 BENCHMARK COMPLETE"
    )

    print(
        "MESSAGES:",
        report["scope"][
            "total_messages"
        ],
    )

    print(
        "CONFIGS:",
        report["summary"][
            "config_count"
        ],
    )


if __name__ == "__main__":
    main()
