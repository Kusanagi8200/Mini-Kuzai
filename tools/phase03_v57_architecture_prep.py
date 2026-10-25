#!/usr/bin/env python3
"""V57 architecture preparation.

This step performs only deterministic preparation:

- freeze conversation serialization v1;
- measure serialized token lengths with the frozen V56 tokenizer;
- measure context coverage;
- define a small decoder-only architecture candidate grid;
- calculate exact planned parameter counts.

No architecture is selected and no model training is authorized.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

TOKENIZER_MODULE = (
    REPO
    / "mini_kuzai"
    / "tokenizer_v56.py"
)

CONVERSATION_MODULE = (
    REPO
    / "mini_kuzai"
    / "phase03_conversation.py"
)

TOKENIZER_FILE = (
    REPO
    / "data/phase-03/tokenizers"
    / "tokenizer-v56-final.json"
)

TOKENIZER_MANIFEST = (
    REPO
    / "data/phase-03/manifests"
    / "tokenizer-v56-final.json"
)

TRAIN_DIR = (
    REPO
    / "data/phase-03/train"
)

V44_FILE = Path(
    "/root/Mini-Kuzai/data/external/"
    "smol-smoltalk/review/"
    "stratified-candidates-v44.jsonl"
)

POOL_FILE = Path(
    "/root/Mini-Kuzai/data/external/"
    "smol-smoltalk/candidates/"
    "external-candidate-pool-v0.4.jsonl"
)

REPORT = (
    REPO
    / "data/phase-03/reports"
    / "architecture-prep-v57.json"
)

CONTEXTS = (
    1024,
    2048,
    4096,
)

TRAIN_NAMES = [
    "train-pilot-v0.2.jsonl",
    *[
        "train-batch-b{:02d}-{}.jsonl".format(
            number,
            {
                8: "v0.5",
                12: "v0.3",
            }.get(
                number,
                "v0.2",
            ),
        )
        for number in range(
            1,
            19,
        )
    ],
]

ARCHITECTURES = (
    {
        "name": "micro",
        "d_model": 128,
        "heads": 4,
        "layers": 4,
        "ff_dim": 512,
    },
    {
        "name": "small",
        "d_model": 192,
        "heads": 6,
        "layers": 6,
        "ff_dim": 768,
    },
    {
        "name": "medium",
        "d_model": 256,
        "heads": 8,
        "layers": 8,
        "ff_dim": 1024,
    },
    {
        "name": "large",
        "d_model": 320,
        "heads": 10,
        "layers": 10,
        "ff_dim": 1280,
    },
)


def load_module(
    name,
    path,
):
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

    spec.loader.exec_module(
        module
    )

    return module


TOK = load_module(
    "phase03_v57_tokenizer",
    TOKENIZER_MODULE,
)

CONV = load_module(
    "phase03_v57_conversation",
    CONVERSATION_MODULE,
)


def load_json(path):
    if (
        not path.is_file()
        or path.is_symlink()
    ):
        raise RuntimeError(
            f"Missing or unsafe JSON: {path}"
        )

    value = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(value, dict):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def read_jsonl(path):
    if (
        not path.is_file()
        or path.is_symlink()
    ):
        raise RuntimeError(
            f"Missing or unsafe JSONL: {path}"
        )

    with path.open(
        encoding="utf-8"
    ) as stream:
        for raw in stream:
            if raw.strip():
                value = json.loads(
                    raw
                )

                if not isinstance(
                    value,
                    dict,
                ):
                    raise RuntimeError(
                        f"Invalid JSONL row: {path}"
                    )

                yield value


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

    temporary.replace(
        path
    )


def percentile(
    values,
    fraction,
):
    if not values:
        raise RuntimeError(
            "Empty percentile population"
        )

    ordered = sorted(
        values
    )

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


def coverage_bp(
    lengths,
    context,
):
    covered = sum(
        length <= context
        for length in lengths
    )

    return round(
        covered
        * 10000
        / len(lengths)
    )


def load_tokenizer():
    manifest = load_json(
        TOKENIZER_MANIFEST
    )

    if (
        manifest.get("status")
        != "FROZEN"
        or manifest.get(
            "vocab_size"
        ) != 1024
        or manifest.get(
            "tokenizer_finalized"
        ) is not True
        or manifest.get(
            "vocabulary_frozen"
        ) is not True
        or manifest.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "V56 frozen tokenizer manifest invalid"
        )

    value = load_json(
        TOKENIZER_FILE
    )

    tokenizer = (
        TOK.ByteBPETokenizer.from_dict(
            value
        )
    )

    if (
        tokenizer.family
        != "byte_bpe_whitespace"
        or tokenizer.vocab_size
        != 1024
        or tokenizer.fingerprint()
        != manifest.get(
            "fingerprint"
        )
    ):
        raise RuntimeError(
            "Frozen tokenizer identity mismatch"
        )

    return tokenizer


def make_fast_counter(
    tokenizer,
):
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

    cache = {}

    def count_chunk(chunk):
        cached = cache.get(
            chunk
        )

        if cached is not None:
            return cached

        sequence = (
            TOK._bytes_to_base_ids(
                chunk.encode(
                    "utf-8"
                )
            )
        )

        while len(sequence) >= 2:
            selected_pair = None
            selected_rank = None
            selected_new_id = None

            for pair in zip(
                sequence,
                sequence[1:],
            ):
                value = ranks.get(
                    pair
                )

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

            sequence = (
                TOK._merge_sequence(
                    sequence,
                    selected_pair,
                    selected_new_id,
                )
            )

        result = len(
            sequence
        )

        cache[chunk] = result

        return result

    def count_text(text):
        total = 0

        for chunk in TOK._split_text(
            text,
            tokenizer.pretokenizer,
        ):
            total += count_chunk(
                chunk
            )

        return total

    return count_text


def serialized_length(
    messages,
    count_text,
):
    text = CONV.serialize_messages(
        messages
    )

    return (
        count_text(text)
        + 2
    )


def load_train():
    rows = []

    for name in TRAIN_NAMES:
        rows.extend(
            read_jsonl(
                TRAIN_DIR / name
            )
        )

    if (
        len(TRAIN_NAMES) != 19
        or len(rows) != 107
        or len(
            {
                row.get("id")
                for row in rows
            }
        )
        != 107
        or len(
            {
                row.get("group_id")
                for row in rows
            }
        )
        != 29
    ):
        raise RuntimeError(
            "Canonical TRAIN inventory changed"
        )

    for row in rows:
        if row.get("split") != "train":
            raise RuntimeError(
                "Non-TRAIN row in canonical TRAIN"
            )

        CONV.validate_messages(
            row.get("messages")
        )

    return rows


def load_v44():
    rows = list(
        read_jsonl(
            V44_FILE
        )
    )

    if len(rows) != 1139:
        raise RuntimeError(
            "V44 provisional population changed"
        )

    seen = set()

    for row in rows:
        fingerprint = row.get(
            "source_content_sha256"
        )

        if (
            not isinstance(
                fingerprint,
                str,
            )
            or len(fingerprint) != 64
            or fingerprint in seen
            or row.get(
                "training_approved"
            ) is not False
        ):
            raise RuntimeError(
                "Invalid V44 provisional row"
            )

        seen.add(
            fingerprint
        )

        CONV.validate_messages(
            row.get("messages")
        )

    return rows


def load_pool():
    rows = list(
        read_jsonl(
            POOL_FILE
        )
    )

    if len(rows) != 8000:
        raise RuntimeError(
            "SmolTalk reservoir changed"
        )

    seen = set()

    for row in rows:
        fingerprint = row.get(
            "content_sha256"
        )

        if (
            not isinstance(
                fingerprint,
                str,
            )
            or len(fingerprint) != 64
            or fingerprint in seen
        ):
            raise RuntimeError(
                "Invalid SmolTalk reservoir row"
            )

        seen.add(
            fingerprint
        )

        CONV.validate_messages(
            row.get("messages")
        )

    return rows


def summarize(
    rows,
    count_text,
):
    lengths = [
        serialized_length(
            row["messages"],
            count_text,
        )
        for row in rows
    ]

    return {
        "conversations":
            len(lengths),
        "tokens":
            sum(lengths),
        "p50":
            percentile(
                lengths,
                0.50,
            ),
        "p95":
            percentile(
                lengths,
                0.95,
            ),
        "p99":
            percentile(
                lengths,
                0.99,
            ),
        "max":
            max(lengths),
        "coverage_bp": {
            str(context):
                coverage_bp(
                    lengths,
                    context,
                )
            for context in CONTEXTS
        },
    }


def parameter_count(
    config,
    context_length,
):
    d_model = config[
        "d_model"
    ]

    ff_dim = config[
        "ff_dim"
    ]

    layers = config[
        "layers"
    ]

    vocab_size = 1024

    if (
        d_model
        % config["heads"]
        != 0
    ):
        raise RuntimeError(
            "Invalid head geometry"
        )

    attention = (
        4
        * d_model
        * d_model
    )

    mlp = (
        2
        * d_model
        * ff_dim
        + ff_dim
        + d_model
    )

    two_layer_norms = (
        4
        * d_model
    )

    per_layer = (
        attention
        + mlp
        + two_layer_norms
    )

    token_embedding = (
        vocab_size
        * d_model
    )

    position_embedding = (
        context_length
        * d_model
    )

    final_norm = (
        2
        * d_model
    )

    total = (
        token_embedding
        + position_embedding
        + final_norm
        + layers
        * per_layer
    )

    return total


def main():
    tokenizer = load_tokenizer()

    count_text = make_fast_counter(
        tokenizer
    )

    train = summarize(
        load_train(),
        count_text,
    )

    v44 = summarize(
        load_v44(),
        count_text,
    )

    pool = summarize(
        load_pool(),
        count_text,
    )

    recommended_context = 0

    for context in CONTEXTS:
        if (
            train["coverage_bp"][
                str(context)
            ]
            >= 9500
            and v44["coverage_bp"][
                str(context)
            ]
            >= 9500
        ):
            recommended_context = (
                context
            )
            break

    parameter_context = (
        recommended_context
        if recommended_context
        else max(CONTEXTS)
    )

    architectures = []

    for config in ARCHITECTURES:
        value = dict(
            config
        )

        value["context_length"] = (
            parameter_context
        )

        value["head_dim"] = (
            config["d_model"]
            // config["heads"]
        )

        value["parameters"] = (
            parameter_count(
                config,
                parameter_context,
            )
        )

        value[
            "adamw_static_bytes_estimate"
        ] = (
            value["parameters"]
            * 16
        )

        architectures.append(
            value
        )

    serializer_source = (
        CONVERSATION_MODULE
        .read_bytes()
    )

    report = {
        "schema_version":
            "v57-architecture-prep-1",
        "status":
            "ARCHITECTURE_PREPARATION_COMPLETE",
        "serializer": {
            "version": 1,
            "user_header":
                CONV.USER_HEADER,
            "assistant_header":
                CONV.ASSISTANT_HEADER,
            "turn_separator":
                CONV.TURN_SEPARATOR,
            "bos":
                True,
            "eos":
                True,
            "sha256":
                hashlib.sha256(
                    serializer_source
                ).hexdigest(),
            "frozen":
                True,
        },
        "tokenizer": {
            "family":
                tokenizer.family,
            "vocab_size":
                tokenizer.vocab_size,
            "fingerprint":
                tokenizer.fingerprint(),
            "frozen":
                True,
        },
        "populations": {
            "controlled_train":
                train,
            "v44_provisional":
                v44,
            "public_pool_upper_bound":
                pool,
        },
        "context": {
            "candidates":
                list(CONTEXTS),
            "coverage_rule_bp":
                9500,
            "recommended":
                recommended_context,
            "selected":
                False,
        },
        "architecture_family": {
            "type":
                "decoder_only_transformer",
            "pre_norm":
                True,
            "causal_attention":
                True,
            "multi_head_attention":
                True,
            "mlp_activation":
                "gelu",
            "ff_ratio":
                4,
            "learned_position_embedding":
                True,
            "tied_token_embedding_lm_head":
                True,
            "attention_projection_bias":
                False,
            "mlp_bias":
                True,
            "candidate_context":
                parameter_context,
        },
        "architecture_candidates":
            architectures,
        "architecture_selected":
            False,
        "training_mix_finalized":
            False,
        "training_authorized":
            False,
        "notes": {
            "v44_training_approved":
                False,
            "public_pool_training_approved":
                False,
            "private_data_included":
                False,
            "validation_included":
                False,
            "blind_included":
                False,
        },
    }

    write_json(
        REPORT,
        report,
    )

    print(
        "V57 ARCHITECTURE PREPARATION COMPLETE"
    )
    print(
        "RECOMMENDED_CONTEXT:",
        recommended_context,
    )


if __name__ == "__main__":
    main()
