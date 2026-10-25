#!/usr/bin/env python3
"""Validate the two V59 public replacement candidates locally."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

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

REPORT = (
    REPO
    / "data/phase-03/reports"
    / "v59-replacement-validation.json"
)

CONTEXT = 2048


def load_module(name, path):
    import importlib.util
    import sys

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
    "phase03_v57_for_v59_replacements",
    V57_PATH,
)


def load_json(path):
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


def review_fields(path):
    text = path.read_text(
        encoding="utf-8"
    )

    def field(name):
        match = re.search(
            rf"^{re.escape(name)}: (.+)$",
            text,
            flags=re.MULTILINE,
        )

        if match is None:
            raise RuntimeError(
                f"Missing review field {name}: {path}"
            )

        return match.group(1)

    return {
        "grade":
            field("V51 grade"),
        "factual_risk":
            field("V51 factual risk"),
        "instruction_fit":
            field("V51 instruction fit"),
    }


def source_reused_in_train(sha):
    for path in sorted(
        (
            REPO
            / "data/phase-03/train"
        ).glob(
            "*.jsonl"
        )
    ):
        if sha in path.read_text(
            encoding="utf-8"
        ):
            return True

    return False


def validate():
    manifest = load_json(
        MANIFEST
    )

    if (
        manifest.get("status")
        != "PENDING_LOCAL_TOKEN_AUDIT"
        or manifest.get("context_length")
        != CONTEXT
        or manifest.get("training_authorized")
        is not False
    ):
        raise RuntimeError(
            "Unexpected V59 replacement manifest state"
        )

    replacements = manifest.get(
        "replacements"
    )

    if (
        not isinstance(replacements, list)
        or len(replacements) != 2
    ):
        raise RuntimeError(
            "Expected exactly two replacement candidates"
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

    results = []

    for candidate in replacements:
        sha = candidate[
            "source_content_sha256"
        ]

        if sha not in v44:
            raise RuntimeError(
                "Replacement candidate is not in V44"
            )

        if sha not in pool:
            raise RuntimeError(
                "Replacement candidate missing from public pool"
            )

        if (
            v44[sha]["messages"]
            != pool[sha]["messages"]
        ):
            raise RuntimeError(
                "V44/public source mismatch"
            )

        review_path = (
            REPO
            / candidate["review_path"]
        )

        fields = review_fields(
            review_path
        )

        if (
            fields["grade"]
            != candidate["required_grade"]
            or fields["factual_risk"]
            != candidate["required_factual_risk"]
            or fields["instruction_fit"]
            != candidate["required_instruction_fit"]
        ):
            raise RuntimeError(
                "Replacement review state changed"
            )

        if source_reused_in_train(
            sha
        ):
            raise RuntimeError(
                "Replacement source already appears in canonical TRAIN"
            )

        token_count = V57.serialized_length(
            pool[sha]["messages"],
            count_text,
        )

        if token_count > CONTEXT:
            raise RuntimeError(
                "Replacement exceeds V58 context"
            )

        results.append(
            {
                "review_case":
                    candidate["review_case"],
                "source_content_sha256":
                    sha,
                "token_count":
                    token_count,
                "within_context":
                    True,
                "v44_member":
                    True,
                "source_reused_in_train":
                    False,
            }
        )

    if len({
        value["source_content_sha256"]
        for value in results
    }) != 2:
        raise RuntimeError(
            "Replacement source collision"
        )

    report = {
        "schema_version":
            "v59-replacement-validation-1",
        "status":
            "REPLACEMENTS_VALIDATED",
        "context_length":
            CONTEXT,
        "replacement_count":
            2,
        "replacements":
            results,
        "all_within_context":
            True,
        "all_v44_members":
            True,
        "all_reviewed_a_low_risk_good_fit":
            True,
        "canonical_train_source_reuse":
            0,
        "validation_included":
            False,
        "blind_included":
            False,
        "private_data_included":
            False,
        "training_mix_finalized":
            False,
        "training_authorized":
            False,
    }

    return report


def main():
    report = validate()

    write_json(
        REPORT,
        report,
    )

    print(
        "V59 REPLACEMENT VALIDATION COMPLETE"
    )

    for value in report["replacements"]:
        print(
            value["review_case"],
            value["token_count"],
        )


if __name__ == "__main__":
    main()
