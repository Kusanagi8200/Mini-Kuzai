#!/usr/bin/env python3
"""V56 tokenizer candidate implementation audit."""

import importlib.util
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

TOKENIZER_PATH = (
    REPO
    / "mini_kuzai"
    / "tokenizer_v56.py"
)

TOKENIZER_SPEC = (
    importlib.util.spec_from_file_location(
        "mini_kuzai_tokenizer_v56_audit",
        TOKENIZER_PATH,
    )
)

if (
    TOKENIZER_SPEC is None
    or TOKENIZER_SPEC.loader is None
):
    raise RuntimeError(
        "Unable to load tokenizer_v56.py"
    )

TOKENIZER = importlib.util.module_from_spec(
    TOKENIZER_SPEC
)

sys.modules[TOKENIZER_SPEC.name] = TOKENIZER

TOKENIZER_SPEC.loader.exec_module(
    TOKENIZER
)

BASE_VOCAB_SIZE = TOKENIZER.BASE_VOCAB_SIZE
CANDIDATE_NAMES = TOKENIZER.CANDIDATE_NAMES
SPECIAL_TOKENS = TOKENIZER.SPECIAL_TOKENS
ByteBPETokenizer = TOKENIZER.ByteBPETokenizer
ByteTokenizer = TOKENIZER.ByteTokenizer
build_candidate = TOKENIZER.build_candidate


SCOPE_STEP = (
    "PHASE03-SMOLTALK-V56-TOKENIZER-SCOPE-002"
)

SCOPE_HISTORY = (
    REPO
    / "reports"
    / "assistant-results"
    / "history"
    / f"{SCOPE_STEP}.json"
)

MARKER = (
    "##### SECTION RESULTS FOR ASSISTANT ######"
)


FIXTURE = [
    "Mini-Kuzai is curious.",
    "Mini-Kuzai is curious!",
    "I do not know yet.",
    "I can form a tentative hypothesis.",
    "Better evidence should change my mind.",
    "hello world",
    "hello Mini-Kuzai",
    "café déjà vu",
    "Grenoble -> Linux -> CUDA",
    "print('hello')",
    "emoji: 🤖🧠",
    "line one\nline two",
] * 8


ROUNDTRIP_CASES = [
    "",
    "hello",
    "Mini-Kuzai",
    "spaces   remain",
    "line one\nline two",
    "café déjà vu",
    "naïve façade",
    "日本語",
    "🤖🧠",
    "x = (a+b) / 2;",
    "\tindent\nnext",
]


def load_scope_history():
    if (
        not SCOPE_HISTORY.is_file()
        or SCOPE_HISTORY.is_symlink()
    ):
        raise RuntimeError(
            "V56 tokenizer scope history missing "
            "or unsafe"
        )

    value = json.loads(
        SCOPE_HISTORY.read_text(
            encoding="utf-8"
        )
    )

    if (
        value.get("step_id") != SCOPE_STEP
        or value.get(
            "semantic_validation_complete"
        ) is not True
        or value.get(
            "training_authorized"
        ) is not False
        or value.get(
            "private_conversation_data_included"
        ) is not False
    ):
        raise RuntimeError(
            "V56 tokenizer scope history invalid"
        )

    metrics = value.get("metrics")

    if not isinstance(metrics, dict):
        raise RuntimeError(
            "V56 tokenizer scope metrics missing"
        )

    expected = {
        "TRAIN_FILES": 19,
        "TRAIN_RECORDS": 107,
        "TRAIN_GROUPS": 29,
        "V56_TOKENIZER_SCOPE_SMOLTALK_RECORDS":
            8000,
        "V56_TOKENIZER_SCOPE_SMOLTALK_SOURCES":
            4,
        "V56_TOKENIZER_SCOPE_VALIDATION_INCLUDED":
            0,
        "V56_TOKENIZER_SCOPE_BLIND_INCLUDED":
            0,
        "V56_TOKENIZER_SCOPE_PRIVATE_INCLUDED":
            0,
        "V56_TOKENIZER_FINALIZED": 0,
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
    }

    for key, expected_value in expected.items():
        if metrics.get(key) != expected_value:
            raise RuntimeError(
                f"Unexpected scope metric {key}"
            )

    return value


def check_lossless(tokenizer):
    for text in ROUNDTRIP_CASES:
        encoded = tokenizer.encode(text)
        decoded = tokenizer.decode(encoded)

        if decoded != text:
            return False

    return True


def check_serialization(tokenizer):
    if isinstance(
        tokenizer,
        ByteTokenizer,
    ):
        return (
            tokenizer.to_dict()["family"]
            == "byte_baseline"
        )

    restored = ByteBPETokenizer.from_dict(
        tokenizer.to_dict()
    )

    if (
        restored.to_dict()
        != tokenizer.to_dict()
    ):
        return False

    return check_lossless(restored)


def audit():
    load_scope_history()

    if len(CANDIDATE_NAMES) != 3:
        raise RuntimeError(
            "Unexpected V56 candidate count"
        )

    if BASE_VOCAB_SIZE != 259:
        raise RuntimeError(
            "Unexpected byte fallback vocabulary"
        )

    if len(SPECIAL_TOKENS) != 3:
        raise RuntimeError(
            "Unexpected special-token count"
        )

    baseline = build_candidate(
        "byte_baseline"
    )

    whitespace_first = build_candidate(
        "byte_bpe_whitespace",
        texts=FIXTURE,
        target_vocab_size=300,
        min_pair_frequency=2,
    )

    whitespace_second = build_candidate(
        "byte_bpe_whitespace",
        texts=FIXTURE,
        target_vocab_size=300,
        min_pair_frequency=2,
    )

    unicode_first = build_candidate(
        "byte_bpe_unicode",
        texts=FIXTURE,
        target_vocab_size=300,
        min_pair_frequency=2,
    )

    unicode_second = build_candidate(
        "byte_bpe_unicode",
        texts=FIXTURE,
        target_vocab_size=300,
        min_pair_frequency=2,
    )

    candidates = [
        baseline,
        whitespace_first,
        unicode_first,
    ]

    lossless = sum(
        int(check_lossless(tokenizer))
        for tokenizer in candidates
    )

    serializable = sum(
        int(check_serialization(tokenizer))
        for tokenizer in candidates
    )

    deterministic = 1

    deterministic += int(
        whitespace_first.to_dict()
        == whitespace_second.to_dict()
        and whitespace_first.fingerprint()
        == whitespace_second.fingerprint()
    )

    deterministic += int(
        unicode_first.to_dict()
        == unicode_second.to_dict()
        and unicode_first.fingerprint()
        == unicode_second.fingerprint()
    )

    byte_fallback = sum(
        int(tokenizer.byte_fallback)
        for tokenizer in candidates
    )

    external_dependencies = sum(
        tokenizer.external_dependencies
        for tokenizer in candidates
    )

    return dict(
        sorted(
            {
                "V56_TOKENIZER_CANDIDATES": 3,
                "V56_TOKENIZER_LOSSLESS_CANDIDATES":
                    lossless,
                "V56_TOKENIZER_SERIALIZABLE_CANDIDATES":
                    serializable,
                "V56_TOKENIZER_DETERMINISTIC_CANDIDATES":
                    deterministic,
                "V56_TOKENIZER_BYTE_FALLBACK_CANDIDATES":
                    byte_fallback,
                "V56_TOKENIZER_EXTERNAL_DEPENDENCIES":
                    external_dependencies,
                "V56_TOKENIZER_BASE_VOCAB":
                    BASE_VOCAB_SIZE,
                "V56_TOKENIZER_SPECIAL_TOKENS":
                    len(SPECIAL_TOKENS),
                "V56_TOKENIZER_FINALIZED": 0,
                "SEMANTIC_VALIDATION_COMPLETE": 1,
                "TRAINING_AUTHORIZED": 0,
            }.items()
        )
    )


def require_expected(metrics):
    expected = dict(
        sorted(
            {
                "V56_TOKENIZER_CANDIDATES": 3,
                "V56_TOKENIZER_LOSSLESS_CANDIDATES": 3,
                "V56_TOKENIZER_SERIALIZABLE_CANDIDATES": 3,
                "V56_TOKENIZER_DETERMINISTIC_CANDIDATES": 3,
                "V56_TOKENIZER_BYTE_FALLBACK_CANDIDATES": 3,
                "V56_TOKENIZER_EXTERNAL_DEPENDENCIES": 0,
                "V56_TOKENIZER_BASE_VOCAB": 259,
                "V56_TOKENIZER_SPECIAL_TOKENS": 3,
                "V56_TOKENIZER_FINALIZED": 0,
                "SEMANTIC_VALIDATION_COMPLETE": 1,
                "TRAINING_AUTHORIZED": 0,
            }.items()
        )
    )

    if metrics != expected:
        raise RuntimeError(
            "Unexpected V56 tokenizer candidate state"
        )


if __name__ == "__main__":
    result = audit()

    require_expected(result)

    print(MARKER)

    for key, value in result.items():
        print(f"{key}: {value}")
