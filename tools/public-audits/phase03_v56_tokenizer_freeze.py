#!/usr/bin/env python3
"""Public aggregate audit for final V56 tokenizer freeze."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

TOKENIZER_MODULE = (
    REPO
    / "mini_kuzai"
    / "tokenizer_v56.py"
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

BENCHMARK_HISTORY = (
    REPO
    / "reports/assistant-results/history"
    / "PHASE03-SMOLTALK-V56-TOKENIZER-BENCHMARK-001.json"
)

MARKER = (
    "##### SECTION RESULTS FOR ASSISTANT ######"
)


SPEC = importlib.util.spec_from_file_location(
    "mini_kuzai_tokenizer_v56_freeze_audit",
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
            f"Expected object: {path}"
        )

    return value


def audit():
    history = load_json(
        BENCHMARK_HISTORY
    )

    if (
        history.get("step_id")
        != "PHASE03-SMOLTALK-V56-TOKENIZER-BENCHMARK-001"
        or history.get(
            "semantic_validation_complete"
        ) is not True
        or history.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "Benchmark GOGIT history invalid"
        )

    manifest = load_json(
        MANIFEST
    )

    selection = load_json(
        SELECTION_REPORT
    )

    tokenizer_value = load_json(
        FINAL_TOKENIZER
    )

    tokenizer = (
        TOK.ByteBPETokenizer.from_dict(
            tokenizer_value
        )
    )

    actual_sha = hashlib.sha256(
        FINAL_TOKENIZER.read_bytes()
    ).hexdigest()

    if (
        manifest.get("status")
        != "FROZEN"
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
            "Final tokenizer manifest invalid"
        )

    if (
        tokenizer.family
        != "byte_bpe_whitespace"
        or tokenizer.vocab_size
        != 1024
        or len(tokenizer.merges)
        != 765
        or tokenizer.fingerprint()
        != manifest.get(
            "fingerprint"
        )
        or actual_sha
        != manifest.get(
            "tokenizer_sha256"
        )
    ):
        raise RuntimeError(
            "Frozen tokenizer integrity failure"
        )

    if (
        manifest.get(
            "validation_included"
        ) is not False
        or manifest.get(
            "blind_included"
        ) is not False
        or manifest.get(
            "private_included"
        ) is not False
    ):
        raise RuntimeError(
            "Tokenizer scope violation"
        )

    evidence = selection.get(
        "benchmark_evidence"
    )

    if not isinstance(
        evidence,
        dict,
    ):
        raise RuntimeError(
            "Selection evidence missing"
        )

    expected = {
        "selected_compression_bp":
            4883,
        "selected_p95":
            887,
        "selected_p99":
            1003,
        "selected_total_tokens":
            11813524,
        "roundtrip_failures":
            0,
        "from_512_token_reduction_bp":
            1496,
        "extra_2048_token_reduction_bp":
            1160,
        "2048_vocab_multiplier_x100":
            200,
    }

    for key, value in expected.items():
        if evidence.get(key) != value:
            raise RuntimeError(
                f"Unexpected selection evidence: {key}"
            )

    return dict(
        sorted(
            {
                "V56_FINAL_VOCAB":
                    1024,
                "V56_FINAL_MERGES":
                    765,
                "V56_FINAL_COMP_BP":
                    4883,
                "V56_FINAL_P95":
                    887,
                "V56_FINAL_P99":
                    1003,
                "V56_FINAL_TOTAL_TOKENS":
                    11813524,
                "V56_FINAL_ROUNDTRIP_FAILURES":
                    0,
                "V56_FINAL_WHITESPACE":
                    1,
                "V56_FINAL_BYTE_FALLBACK":
                    1,
                "V56_FINAL_FROM512_TOKEN_REDUCTION_BP":
                    1496,
                "V56_FINAL_2048_EXTRA_TOKEN_REDUCTION_BP":
                    1160,
                "V56_FINAL_2048_VOCAB_MULTIPLIER_X100":
                    200,
                "V56_FINAL_VALIDATION_INCLUDED":
                    0,
                "V56_FINAL_BLIND_INCLUDED":
                    0,
                "V56_FINAL_PRIVATE_INCLUDED":
                    0,
                "V56_TOKENIZER_FINALIZED":
                    1,
                "V56_VOCABULARY_FROZEN":
                    1,
                "V56_ARCHITECTURE_SELECTED":
                    0,
                "SEMANTIC_VALIDATION_COMPLETE":
                    1,
                "TRAINING_AUTHORIZED":
                    0,
            }.items()
        )
    )


if __name__ == "__main__":
    result = audit()

    print(MARKER)

    for key, value in result.items():
        print(f"{key}: {value}")
