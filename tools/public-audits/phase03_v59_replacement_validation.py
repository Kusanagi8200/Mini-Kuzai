#!/usr/bin/env python3
"""Public numeric audit for V59 replacement candidates."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

VALIDATOR = (
    REPO
    / "tools"
    / "phase03_v59_replacement_validation.py"
)

MARKER = (
    "##### SECTION RESULTS FOR ASSISTANT ######"
)


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


VALIDATION = load_module(
    "phase03_v59_replacement_validation_public",
    VALIDATOR,
)


def main():
    value = VALIDATION.validate()

    if (
        value.get("status")
        != "REPLACEMENTS_VALIDATED"
        or value.get("replacement_count")
        != 2
        or value.get("all_pairs_within_context")
        is not True
        or value.get("all_segments_within_context")
        is not True
        or value.get("all_v44_members")
        is not True
        or value.get(
            "all_reviewed_a_low_risk_good_fit"
        ) is not True
        or value.get(
            "canonical_train_source_reuse"
        ) != 0
        or value.get(
            "training_mix_finalized"
        ) is not False
        or value.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "Unexpected V59 replacement validation state"
        )

    replacements = value[
        "replacements"
    ]

    if len(replacements) != 2:
        raise RuntimeError(
            "Expected exactly two replacements"
        )

    metrics = {
        "V59_REPLACEMENT_CANDIDATES":
            2,
        "V59_REPLACEMENTS_VALIDATED":
            2,
        "V59_REPLACEMENTS_WITHIN_CONTEXT":
            sum(
                int(row["within_context"])
                for row in replacements
            ),
        "V59_REPLACEMENTS_V44":
            sum(
                int(row["v44_member"])
                for row in replacements
            ),
        "V59_REPLACEMENTS_TRAIN_SOURCE_REUSE":
            value[
                "canonical_train_source_reuse"
            ],
        "V59_REPLACEMENT_TOTAL_SEGMENTS":
            sum(
                row["segment_count"]
                for row in replacements
            ),
        "V59_REPLACEMENT_MAX_PAIR_TOKENS":
            max(
                row["max_pair_tokens"]
                for row in replacements
            ),
        "V59_REPLACEMENT_MAX_SEGMENT_TOKENS":
            max(
                row["max_segment_tokens"]
                for row in replacements
            ),
        "V59_REPLACEMENT_MAX_SOURCE_TOKENS":
            max(
                row["source_token_count"]
                for row in replacements
            ),
        "V59_REPLACEMENT_MIN_SOURCE_TOKENS":
            min(
                row["source_token_count"]
                for row in replacements
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
