#!/usr/bin/env python3
"""Public numeric audit for validated V59 replacement candidates."""

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

REPORT = (
    REPO
    / "data/phase-03/reports"
    / "v59-replacement-validation.json"
)

MARKER = (
    "##### SECTION RESULTS FOR ASSISTANT ######"
)


def main():
    value = json.loads(
        REPORT.read_text(
            encoding="utf-8"
        )
    )

    if (
        value.get("status")
        != "REPLACEMENTS_VALIDATED"
        or value.get("replacement_count")
        != 2
        or value.get("all_within_context")
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
        "V59_REPLACEMENT_MAX_TOKENS":
            max(
                row["token_count"]
                for row in replacements
            ),
        "V59_REPLACEMENT_MIN_TOKENS":
            min(
                row["token_count"]
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
