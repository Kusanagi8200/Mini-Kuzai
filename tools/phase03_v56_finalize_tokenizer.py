#!/usr/bin/env python3
"""Select and freeze the final Phase 03 V56 tokenizer.

Selection:
    byte_bpe_whitespace
    vocabulary size: 1024

The final tokenizer is an exact deterministic prefix of the previously
benchmarked 2048-token whitespace BPE merge table.

This script does not authorize model training.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

TOKENIZER_MODULE = (
    REPO
    / "mini_kuzai"
    / "tokenizer_v56.py"
)

BENCHMARK = (
    REPO
    / "data/phase-03/reports"
    / "tokenizer-benchmark-v56.json"
)

SOURCE_MODEL = (
    REPO
    / "data/phase-03/tokenizers/v56-candidates"
    / "byte-bpe-whitespace-2048.json"
)

FINAL_TOKENIZER = (
    REPO
    / "data/phase-03/tokenizers"
    / "tokenizer-v56-final.json"
)

SELECTION_REPORT = (
    REPO
    / "data/phase-03/reports"
    / "tokenizer-selection-v56.json"
)

MANIFEST = (
    REPO
    / "data/phase-03/manifests"
    / "tokenizer-v56-final.json"
)

BENCHMARK_STEP = (
    "PHASE03-SMOLTALK-V56-TOKENIZER-BENCHMARK-001"
)

FREEZE_STEP = (
    "PHASE03-SMOLTALK-V56-TOKENIZER-FREEZE-001"
)

SELECTED_NAME = "byte_bpe_whitespace_1024"
SELECTED_VOCAB = 1024


SPEC = importlib.util.spec_from_file_location(
    "mini_kuzai_tokenizer_v56_finalize",
    TOKENIZER_MODULE,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        "Unable to load tokenizer_v56.py"
    )

TOK = importlib.util.module_from_spec(SPEC)

sys.modules[SPEC.name] = TOK

SPEC.loader.exec_module(TOK)


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


def sha256_file(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def reduction_bp(old_value, new_value):
    return round(
        (
            1
            - new_value / old_value
        )
        * 10000
    )


def main():
    benchmark = load_json(
        BENCHMARK
    )

    if (
        benchmark.get("status")
        != "BENCHMARK_AND_COST_COMPARISON_COMPLETE"
        or benchmark.get(
            "tokenizer_finalized"
        ) is not False
        or benchmark.get(
            "vocabulary_frozen"
        ) is not False
        or benchmark.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "Benchmark state is not eligible "
            "for tokenizer finalization"
        )

    scope = benchmark["scope"]

    if (
        scope.get(
            "validation_included"
        ) is not False
        or scope.get(
            "blind_included"
        ) is not False
        or scope.get(
            "private_included"
        ) is not False
    ):
        raise RuntimeError(
            "Tokenizer learning scope violation"
        )

    configs = {
        item["name"]: item
        for item in benchmark["configs"]
    }

    required = {
        "byte_bpe_whitespace_512",
        "byte_bpe_whitespace_1024",
        "byte_bpe_whitespace_2048",
        "byte_bpe_unicode_512",
        "byte_bpe_unicode_1024",
        "byte_bpe_unicode_2048",
    }

    if not required <= set(configs):
        raise RuntimeError(
            "Benchmark configuration set incomplete"
        )

    for target in (
        512,
        1024,
        2048,
    ):
        whitespace = configs[
            f"byte_bpe_whitespace_{target}"
        ]

        unicode = configs[
            f"byte_bpe_unicode_{target}"
        ]

        if not (
            whitespace["total_tokens"]
            < unicode["total_tokens"]
            and whitespace["p95_tokens"]
            < unicode["p95_tokens"]
        ):
            raise RuntimeError(
                "Whitespace BPE does not dominate "
                f"Unicode BPE at {target}"
            )

    selected = configs[
        SELECTED_NAME
    ]

    smaller = configs[
        "byte_bpe_whitespace_512"
    ]

    larger = configs[
        "byte_bpe_whitespace_2048"
    ]

    if (
        selected["vocab_size"]
        != SELECTED_VOCAB
        or selected[
            "roundtrip_failures"
        ]
        != 0
    ):
        raise RuntimeError(
            "Selected benchmark candidate invalid"
        )

    source_value = load_json(
        SOURCE_MODEL
    )

    source_tokenizer = (
        TOK.ByteBPETokenizer.from_dict(
            source_value
        )
    )

    if (
        source_tokenizer.family
        != "byte_bpe_whitespace"
        or source_tokenizer.vocab_size
        != 2048
    ):
        raise RuntimeError(
            "Unexpected source tokenizer"
        )

    merge_count = (
        SELECTED_VOCAB
        - TOK.BASE_VOCAB_SIZE
    )

    final_tokenizer = (
        TOK.ByteBPETokenizer(
            pretokenizer=(
                TOK.PRETOKENIZER_WHITESPACE
            ),
            merges=(
                source_tokenizer.merges[
                    :merge_count
                ]
            ),
        )
    )

    if (
        final_tokenizer.vocab_size
        != SELECTED_VOCAB
    ):
        raise RuntimeError(
            "Final vocabulary size mismatch"
        )

    if (
        len(final_tokenizer.merges)
        != 765
    ):
        raise RuntimeError(
            "Final merge count mismatch"
        )

    fingerprint = (
        final_tokenizer.fingerprint()
    )

    if (
        fingerprint
        != selected["fingerprint"]
    ):
        raise RuntimeError(
            "Final tokenizer fingerprint "
            "does not match benchmark candidate"
        )

    final_value = (
        final_tokenizer.to_dict()
    )

    write_json(
        FINAL_TOKENIZER,
        final_value,
    )

    restored = (
        TOK.ByteBPETokenizer.from_dict(
            load_json(
                FINAL_TOKENIZER
            )
        )
    )

    if (
        restored.fingerprint()
        != fingerprint
    ):
        raise RuntimeError(
            "Frozen tokenizer reload mismatch"
        )

    roundtrip_cases = [
        "",
        "Mini-Kuzai",
        "I do not know yet.",
        "spaces   remain",
        "line one\nline two",
        "café déjà vu",
        "日本語",
        "🤖🧠",
        "x = (a+b) / 2;",
    ]

    for text in roundtrip_cases:
        if (
            restored.decode(
                restored.encode(text)
            )
            != text
        ):
            raise RuntimeError(
                "Frozen tokenizer round-trip failure"
            )

    from_512_token_reduction_bp = (
        reduction_bp(
            smaller["total_tokens"],
            selected["total_tokens"],
        )
    )

    extra_2048_token_reduction_bp = (
        reduction_bp(
            selected["total_tokens"],
            larger["total_tokens"],
        )
    )

    from_512_p95_reduction_bp = (
        reduction_bp(
            smaller["p95_tokens"],
            selected["p95_tokens"],
        )
    )

    extra_2048_p95_reduction_bp = (
        reduction_bp(
            selected["p95_tokens"],
            larger["p95_tokens"],
        )
    )

    selection_report = {
        "schema_version":
            "v56-tokenizer-selection-1",
        "status":
            "SELECTED_AND_FROZEN",
        "selection": {
            "config":
                SELECTED_NAME,
            "family":
                "byte_bpe_whitespace",
            "pretokenizer":
                "whitespace",
            "vocab_size":
                SELECTED_VOCAB,
            "merge_count":
                len(
                    final_tokenizer.merges
                ),
            "byte_fallback":
                True,
            "fingerprint":
                fingerprint,
        },
        "benchmark_evidence": {
            "benchmark_step":
                BENCHMARK_STEP,
            "baseline_tokens":
                configs[
                    "byte_baseline"
                ]["total_tokens"],
            "selected_total_tokens":
                selected["total_tokens"],
            "selected_compression_bp":
                selected["compression_bp"],
            "selected_p50":
                selected["p50_tokens"],
            "selected_p95":
                selected["p95_tokens"],
            "selected_p99":
                selected["p99_tokens"],
            "selected_max":
                selected["max_tokens"],
            "roundtrip_failures":
                selected[
                    "roundtrip_failures"
                ],
            "from_512_token_reduction_bp":
                from_512_token_reduction_bp,
            "from_512_p95_reduction_bp":
                from_512_p95_reduction_bp,
            "extra_2048_token_reduction_bp":
                extra_2048_token_reduction_bp,
            "extra_2048_p95_reduction_bp":
                extra_2048_p95_reduction_bp,
            "2048_vocab_multiplier_x100":
                round(
                    larger["vocab_size"]
                    * 100
                    / selected["vocab_size"]
                ),
        },
        "decision": {
            "whitespace_dominates_unicode":
                True,
            "reason":
                (
                    "1024 preserves most of the "
                    "measured compression benefit "
                    "without doubling vocabulary "
                    "parameters to 2048"
                ),
        },
        "scope": {
            "learning_corpus_sha256":
                scope[
                    "learning_corpus_sha256"
                ],
            "validation_included":
                False,
            "blind_included":
                False,
            "private_included":
                False,
        },
        "tokenizer_finalized":
            True,
        "vocabulary_frozen":
            True,
        "architecture_selected":
            False,
        "training_authorized":
            False,
    }

    write_json(
        SELECTION_REPORT,
        selection_report,
    )

    tokenizer_sha256 = (
        sha256_file(
            FINAL_TOKENIZER
        )
    )

    benchmark_sha256 = (
        sha256_file(
            BENCHMARK
        )
    )

    source_sha256 = (
        sha256_file(
            SOURCE_MODEL
        )
    )

    manifest = {
        "schema_version":
            "v56-tokenizer-manifest-1",
        "status":
            "FROZEN",
        "freeze_step_id":
            FREEZE_STEP,
        "benchmark_step_id":
            BENCHMARK_STEP,
        "tokenizer_path":
            str(
                FINAL_TOKENIZER
                .relative_to(REPO)
            ),
        "selection_report_path":
            str(
                SELECTION_REPORT
                .relative_to(REPO)
            ),
        "family":
            "byte_bpe_whitespace",
        "pretokenizer":
            "whitespace",
        "vocab_size":
            SELECTED_VOCAB,
        "merge_count":
            765,
        "base_vocab_size":
            TOK.BASE_VOCAB_SIZE,
        "special_tokens":
            dict(
                TOK.SPECIAL_TOKENS
            ),
        "byte_fallback":
            True,
        "fingerprint":
            fingerprint,
        "tokenizer_sha256":
            tokenizer_sha256,
        "benchmark_sha256":
            benchmark_sha256,
        "source_2048_sha256":
            source_sha256,
        "learning_corpus_sha256":
            scope[
                "learning_corpus_sha256"
            ],
        "validation_included":
            False,
        "blind_included":
            False,
        "private_included":
            False,
        "tokenizer_finalized":
            True,
        "vocabulary_frozen":
            True,
        "architecture_selected":
            False,
        "training_authorized":
            False,
    }

    write_json(
        MANIFEST,
        manifest,
    )

    print(
        "V56 TOKENIZER FINALIZED"
    )
    print(
        "CONFIG:",
        SELECTED_NAME,
    )
    print(
        "VOCAB:",
        SELECTED_VOCAB,
    )
    print(
        "FINGERPRINT:",
        fingerprint,
    )


if __name__ == "__main__":
    main()
