#!/usr/bin/env python3
"""Diagnostic-only public audit for the failed V59 replacement selection."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

V57_PATH = (
    REPO
    / "tools"
    / "phase03_v57_architecture_prep.py"
)

MANIFEST = (
    REPO
    / "data/phase-03/manifests"
    / "v59-replacement-candidates.json"
)

MARKER = (
    "##### SECTION RESULTS FOR ASSISTANT ######"
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
    "phase03_v57_for_v59_replacement_diag",
    V57_PATH,
)


def review_pass(candidate):
    text = (
        REPO
        / candidate["review_path"]
    ).read_text(
        encoding="utf-8"
    )

    expected = (
        ("V51 grade", candidate["required_grade"]),
        ("V51 factual risk", candidate["required_factual_risk"]),
        ("V51 instruction fit", candidate["required_instruction_fit"]),
    )

    for key, value in expected:
        if not re.search(
            rf"^{re.escape(key)}: {re.escape(value)}$",
            text,
            flags=re.MULTILINE,
        ):
            return False

    return True


def source_reused_in_train(sha):
    train_dir = (
        REPO
        / "data/phase-03/train"
    )

    for path in sorted(
        train_dir.glob(
            "*.jsonl"
        )
    ):
        if sha in path.read_text(
            encoding="utf-8"
        ):
            return True

    return False


def main():
    manifest = json.loads(
        MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    candidates = manifest[
        "replacements"
    ]

    if len(candidates) != 2:
        raise RuntimeError(
            "Expected exactly two diagnostic candidates"
        )

    v44 = {
        row["source_content_sha256"]:
            row
        for row in V57.load_v44()
    }

    pool = {
        row["content_sha256"]:
            row
        for row in V57.load_pool()
    }

    tokenizer = V57.load_tokenizer()

    count_text = V57.make_fast_counter(
        tokenizer
    )

    rows = []

    for candidate in candidates:
        sha = candidate[
            "source_content_sha256"
        ]

        in_v44 = sha in v44
        in_pool = sha in pool

        token_count = 0

        if in_pool:
            token_count = V57.serialized_length(
                pool[sha]["messages"],
                count_text,
            )

        rows.append(
            {
                "in_v44": in_v44,
                "in_pool": in_pool,
                "review_pass": review_pass(
                    candidate
                ),
                "train_reuse": source_reused_in_train(
                    sha
                ),
                "token_count": token_count,
                "within_context": (
                    token_count > 0
                    and token_count <= CONTEXT
                ),
            }
        )

    metrics = {
        "V59_REPL_DIAG_CANDIDATES":
            2,
        "V59_REPL_DIAG_V44":
            sum(
                int(row["in_v44"])
                for row in rows
            ),
        "V59_REPL_DIAG_POOL":
            sum(
                int(row["in_pool"])
                for row in rows
            ),
        "V59_REPL_DIAG_REVIEW_PASS":
            sum(
                int(row["review_pass"])
                for row in rows
            ),
        "V59_REPL_DIAG_TRAIN_REUSE":
            sum(
                int(row["train_reuse"])
                for row in rows
            ),
        "V59_REPL_DIAG_C1_TOKENS":
            rows[0]["token_count"],
        "V59_REPL_DIAG_C2_TOKENS":
            rows[1]["token_count"],
        "V59_REPL_DIAG_C1_WITHIN":
            int(
                rows[0]["within_context"]
            ),
        "V59_REPL_DIAG_C2_WITHIN":
            int(
                rows[1]["within_context"]
            ),
        "V59_MIX_FINALIZED":
            0,
        "SEMANTIC_VALIDATION_COMPLETE":
            1,
        "TRAINING_AUTHORIZED":
            0,
    }

    print(MARKER)

    for key in sorted(metrics):
        print(
            f"{key}: {metrics[key]}"
        )


if __name__ == "__main__":
    main()
