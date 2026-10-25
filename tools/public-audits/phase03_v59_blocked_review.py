#!/usr/bin/env python3
"""Public numeric audit for V59 oversized-pair review dispositions."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

PUBLISHER = (
    REPO
    / "tools"
    / "publish_smoltalk_v59_blocked_reviews.py"
)

REVIEWS = (
    REPO
    / "reviews"
    / "smoltalk-v59-blocked"
    / "cases"
)

MARKER = (
    "##### SECTION RESULTS FOR ASSISTANT ######"
)

DISPOSITION_RE = re.compile(
    r"^V59 disposition: (PENDING|EXCLUDE|REPLACE|SPECIAL_POLICY|HOLD)$",
    re.MULTILINE,
)

RATIONALE_RE = re.compile(
    r"^V59 rationale: (.+)$",
    re.MULTILINE,
)


def load_module(
    name,
    path,
):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if (
        spec is None
        or spec.loader is None
    ):
        raise RuntimeError(
            f"Unable to load {path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


PUB = load_module(
    "phase03_v59_blocked_review_audit",
    PUBLISHER,
)


def normalized_page(text):
    text = DISPOSITION_RE.sub(
        "V59 disposition: PENDING",
        text,
        count=1,
    )

    text = RATIONALE_RE.sub(
        "V59 rationale: NOT_REVIEWED",
        text,
        count=1,
    )

    return text


def audit():
    rows = PUB.blocked_rows()

    pages = sorted(
        path
        for path in REVIEWS.iterdir()
        if (
            path.is_file()
            and not path.is_symlink()
            and path.suffix == ".md"
        )
    )

    if len(rows) != 10 or len(pages) != 10:
        raise RuntimeError(
            "Expected exactly 10 V59 blocked review cases"
        )

    counts = {
        "EXCLUDE": 0,
        "REPLACE": 0,
        "SPECIAL_POLICY": 0,
        "HOLD": 0,
        "PENDING": 0,
    }

    v44_counts = {
        "EXCLUDE": 0,
        "REPLACE": 0,
        "SPECIAL_POLICY": 0,
        "HOLD": 0,
        "PENDING": 0,
    }

    for index, row in enumerate(
        rows,
        1,
    ):
        filename = (
            "{:02d}-{}.md".format(
                index,
                row["sha"][:16],
            )
        )

        path = (
            REVIEWS
            / filename
        )

        if (
            not path.is_file()
            or path.is_symlink()
        ):
            raise RuntimeError(
                f"Missing V59 review case: {filename}"
            )

        actual = path.read_text(
            encoding="utf-8"
        )

        expected = PUB.case_page(
            index,
            row,
        )

        if normalized_page(actual) != expected:
            raise RuntimeError(
                f"Immutable V59 case content changed: {filename}"
            )

        disposition_match = (
            DISPOSITION_RE.search(
                actual
            )
        )

        rationale_match = (
            RATIONALE_RE.search(
                actual
            )
        )

        if (
            disposition_match is None
            or rationale_match is None
        ):
            raise RuntimeError(
                f"Missing V59 review fields: {filename}"
            )

        disposition = (
            disposition_match.group(1)
        )

        rationale = (
            rationale_match.group(1)
        )

        if (
            disposition != "PENDING"
            and (
                rationale == "NOT_REVIEWED"
                or len(rationale) < 24
            )
        ):
            raise RuntimeError(
                f"Reviewed V59 case lacks rationale: {filename}"
            )

        counts[
            disposition
        ] += 1

        if row["in_v44"]:
            v44_counts[
                disposition
            ] += 1

    reviewed = (
        10
        - counts["PENDING"]
    )

    if (
        reviewed != 10
        or counts["EXCLUDE"] != 8
        or counts["REPLACE"] != 2
        or counts["SPECIAL_POLICY"] != 0
        or counts["HOLD"] != 0
        or v44_counts["EXCLUDE"] != 2
        or v44_counts["REPLACE"] != 1
        or v44_counts["PENDING"] != 0
    ):
        raise RuntimeError(
            "Unexpected V59 review disposition totals"
        )

    return {
        "V59_BLOCKED_REVIEW_TOTAL":
            10,
        "V59_BLOCKED_REVIEWED":
            reviewed,
        "V59_BLOCKED_EXCLUDE":
            counts["EXCLUDE"],
        "V59_BLOCKED_REPLACE":
            counts["REPLACE"],
        "V59_BLOCKED_SPECIAL_POLICY":
            counts["SPECIAL_POLICY"],
        "V59_BLOCKED_HOLD":
            counts["HOLD"],
        "V59_BLOCKED_PENDING":
            counts["PENDING"],
        "V59_BLOCKED_V44_TOTAL":
            3,
        "V59_BLOCKED_V44_EXCLUDE":
            v44_counts["EXCLUDE"],
        "V59_BLOCKED_V44_REPLACE":
            v44_counts["REPLACE"],
        "V59_BLOCKED_V44_PENDING":
            v44_counts["PENDING"],
        "V59_BLOCKED_POOL_ONLY_TOTAL":
            7,
        "V59_CONTEXT_EXCEPTION_POLICY":
            0,
        "V59_MIX_FINALIZED":
            0,
        "SEMANTIC_VALIDATION_COMPLETE":
            1,
        "TRAINING_AUTHORIZED":
            0,
    }


if __name__ == "__main__":
    metrics = audit()

    print(MARKER)

    for key in sorted(metrics):
        print(
            f"{key}: {metrics[key]}"
        )
