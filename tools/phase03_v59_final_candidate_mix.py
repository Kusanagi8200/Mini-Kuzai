#!/usr/bin/env python3
"""V59 final public candidate-mix audit.

This step removes only explicit known-negative public cases from the cleaned
V44 envelope. It does not promote the remaining population to TRAIN.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

V57_PATH = REPO / "tools" / "phase03_v57_architecture_prep.py"
SEG_PATH = REPO / "mini_kuzai" / "phase03_segmentation.py"

V50_QUEUE = Path(
    "/root/Mini-Kuzai/data/external/smol-smoltalk/review/"
    "v50-cognitive-review-priority.jsonl"
)

REVIEW_DIRS = (
    ("V51", REPO / "reviews/smoltalk-v51/cases"),
    ("V52", REPO / "reviews/smoltalk-v52/cases"),
)

CONTEXT = 2048
PARAMETERS = 1184512

CONTROLLED_SOURCE_SHAS = {
    "566e0b8c4ed792cc76ad0646a6295b05adab7a8caf37e8b91483982fb80e00c3",
    "383f5926f407ae183de348a6aae660e952a4e03887ba2ed275d259969e23fc9a",
}

SHA_RE = re.compile(
    r"^Public content SHA-256: ([0-9a-f]{64})$",
    re.MULTILINE,
)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


V57 = load_module("phase03_v57_for_v59_candidate_mix", V57_PATH)
SEG = load_module("phase03_seg_for_v59_candidate_mix", SEG_PATH)


def read_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe input: {path}")
    with path.open(encoding="utf-8") as stream:
        for raw in stream:
            if raw.strip():
                yield json.loads(raw)


def field(text, key):
    match = re.search(
        rf"^{re.escape(key)}: (.+)$",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError(f"Missing review field: {key}")
    return match.group(1).strip()


def reviewed_exclusions():
    reviewed = {}
    grade_c = set()
    factual_high = set()
    instruction_bad = set()

    expected_counts = {
        "V51": 24,
        "V52": 32,
    }

    for cycle, directory in REVIEW_DIRS:
        pages = sorted(directory.glob("*.md"))

        if len(pages) != expected_counts[cycle]:
            raise RuntimeError(
                f"{cycle} review population changed"
            )

        for path in pages:
            if path.is_symlink():
                raise RuntimeError(
                    f"Unsafe review symlink: {path}"
                )

            text = path.read_text(
                encoding="utf-8"
            )

            sha_match = SHA_RE.search(text)
            if sha_match is None:
                raise RuntimeError(
                    f"Missing public SHA: {path}"
                )

            sha = sha_match.group(1)

            if sha in reviewed:
                raise RuntimeError(
                    "Duplicate V51/V52 reviewed source"
                )

            grade = field(
                text,
                f"{cycle} grade",
            )
            risk = field(
                text,
                f"{cycle} factual risk",
            )
            fit = field(
                text,
                f"{cycle} instruction fit",
            )

            if grade not in {
                "A",
                "B",
                "C",
                "HOLD",
                "PENDING",
            }:
                raise RuntimeError(
                    f"Invalid grade in {path}"
                )

            if risk not in {
                "LOW",
                "REVIEW",
                "HIGH",
            }:
                raise RuntimeError(
                    f"Invalid factual risk in {path}"
                )

            if fit not in {
                "GOOD",
                "PARTIAL",
                "BAD",
            }:
                raise RuntimeError(
                    f"Invalid instruction fit in {path}"
                )

            if grade in {"HOLD", "PENDING"}:
                raise RuntimeError(
                    "Structured review population is not closed"
                )

            reviewed[sha] = {
                "grade": grade,
                "risk": risk,
                "fit": fit,
            }

            if grade == "C":
                grade_c.add(sha)

            if risk == "HIGH":
                factual_high.add(sha)

            if fit == "BAD":
                instruction_bad.add(sha)

    if len(reviewed) != 56:
        raise RuntimeError(
            "Expected 56 structured reviewed sources"
        )

    exclusion_union = (
        grade_c
        | factual_high
        | instruction_bad
    )

    return {
        "reviewed": reviewed,
        "grade_c": grade_c,
        "factual_high": factual_high,
        "instruction_bad": instruction_bad,
        "union": exclusion_union,
    }


def main():
    queue = list(
        read_jsonl(
            V50_QUEUE
        )
    )

    if len(queue) != 1139:
        raise RuntimeError(
            "V50 queue population changed"
        )

    queue_by_sha = {
        row["source_content_sha256"]:
            row
        for row in queue
    }

    if len(queue_by_sha) != 1139:
        raise RuntimeError(
            "Duplicate V50 queue SHA"
        )

    reviews = reviewed_exclusions()

    tokenizer = V57.load_tokenizer()
    count_text = V57.make_fast_counter(
        tokenizer
    )

    selected = []
    excluded_oversized = set()
    excluded_train_source = set()
    excluded_known_negative = set()

    for row in V57.load_v44():
        sha = row[
            "source_content_sha256"
        ]

        q = queue_by_sha.get(sha)

        if q is None:
            raise RuntimeError(
                "V44 candidate absent from V50 queue"
            )

        pair_counts = SEG.pair_token_counts(
            row["messages"],
            serialize_messages=V57.CONV.serialize_messages,
            validate_messages=V57.CONV.validate_messages,
            count_text=count_text,
        )

        if max(pair_counts) > CONTEXT:
            excluded_oversized.add(
                sha
            )
            continue

        if sha in CONTROLLED_SOURCE_SHAS:
            excluded_train_source.add(
                sha
            )
            continue

        if sha in reviews["union"]:
            excluded_known_negative.add(
                sha
            )
            continue

        segments = SEG.segment_messages(
            row["messages"],
            serialize_messages=V57.CONV.serialize_messages,
            validate_messages=V57.CONV.validate_messages,
            count_text=count_text,
            context_length=CONTEXT,
        )

        selected.append(
            {
                "sha": sha,
                "priority":
                    q["priority_hint"],
                "segments":
                    len(segments),
                "tokens":
                    sum(
                        segment.token_count
                        for segment in segments
                    ),
                "reviewed":
                    sha in reviews["reviewed"],
            }
        )

    if len(excluded_oversized) != 3:
        raise RuntimeError(
            "Expected exactly three oversized V44 exclusions"
        )

    if len(excluded_train_source) != 2:
        raise RuntimeError(
            "Expected exactly two controlled-source exclusions"
        )

    if (
        excluded_oversized
        & excluded_train_source
        or excluded_oversized
        & excluded_known_negative
        or excluded_train_source
        & excluded_known_negative
    ):
        raise RuntimeError(
            "Exclusion classes unexpectedly overlap"
        )

    selected_shas = {
        row["sha"]
        for row in selected
    }

    if len(selected_shas) != len(selected):
        raise RuntimeError(
            "Duplicate selected public source"
        )

    tokens = sum(
        row["tokens"]
        for row in selected
    )

    segments = sum(
        row["segments"]
        for row in selected
    )

    priorities = Counter(
        row["priority"]
        for row in selected
    )

    reviewed_retained = sum(
        int(row["reviewed"])
        for row in selected
    )

    controlled_tokens = sum(
        V57.serialized_length(
            row["messages"],
            count_text,
        )
        for row in V57.load_train()
    )

    if controlled_tokens != 24539:
        raise RuntimeError(
            "Controlled TRAIN token count changed"
        )

    combined_tokens = (
        tokens
        + controlled_tokens
    )

    metrics = {
        "V59_FINAL_CANDIDATE_RAW_V44":
            1139,
        "V59_FINAL_CANDIDATE_EXCL_OVERSIZED":
            len(excluded_oversized),
        "V59_FINAL_CANDIDATE_EXCL_TRAIN_SOURCE":
            len(excluded_train_source),
        "V59_FINAL_CANDIDATE_REVIEWED_TOTAL":
            len(reviews["reviewed"]),
        "V59_FINAL_CANDIDATE_GRADE_C_TOTAL":
            len(reviews["grade_c"]),
        "V59_FINAL_CANDIDATE_FACT_HIGH_TOTAL":
            len(reviews["factual_high"]),
        "V59_FINAL_CANDIDATE_INSTR_BAD_TOTAL":
            len(reviews["instruction_bad"]),
        "V59_FINAL_CANDIDATE_KNOWN_NEG_UNION":
            len(reviews["union"]),
        "V59_FINAL_CANDIDATE_EXCL_KNOWN_NEG":
            len(excluded_known_negative),
        "V59_FINAL_CANDIDATE_CONVERSATIONS":
            len(selected),
        "V59_FINAL_CANDIDATE_SEGMENTS":
            segments,
        "V59_FINAL_CANDIDATE_TOKENS":
            tokens,
        "V59_FINAL_CANDIDATE_TPP_X1000":
            (tokens * 1000) // PARAMETERS,
        "V59_FINAL_CANDIDATE_HIGH":
            priorities["HIGH"],
        "V59_FINAL_CANDIDATE_MEDIUM":
            priorities["MEDIUM"],
        "V59_FINAL_CANDIDATE_LOW":
            priorities["LOW"],
        "V59_FINAL_CANDIDATE_REVIEWED_RETAINED":
            reviewed_retained,
        "V59_FINAL_COMBINED_TOKENS":
            combined_tokens,
        "V59_FINAL_COMBINED_TPP_X1000":
            (combined_tokens * 1000) // PARAMETERS,
        "V59_MIX_FINALIZED":
            0,
        "SEMANTIC_VALIDATION_COMPLETE":
            1,
        "TRAINING_AUTHORIZED":
            0,
    }

    if (
        len(selected)
        + len(excluded_oversized)
        + len(excluded_train_source)
        + len(excluded_known_negative)
        != 1139
    ):
        raise RuntimeError(
            "V59 candidate accounting does not close"
        )

    print(
        "##### SECTION RESULTS FOR ASSISTANT ######"
    )

    for key in sorted(metrics):
        print(
            f"{key}: {metrics[key]}"
        )


if __name__ == "__main__":
    main()
