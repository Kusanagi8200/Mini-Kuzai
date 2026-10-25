#!/usr/bin/env python3
"""Publish the V59 oversized-pair PUBLIC SmolTalk review packet.

Only public SmolTalk source data are read. No private corpus, VALIDATION or
BLIND TEST data are accessed. The publisher is one-time and refuses overwrite.
"""

from __future__ import annotations

import html
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

V57_PATH = (
    REPO
    / "tools"
    / "phase03_v57_architecture_prep.py"
)

SEGMENTATION_PATH = (
    REPO
    / "mini_kuzai"
    / "phase03_segmentation.py"
)

DEST = (
    REPO
    / "reviews"
    / "smoltalk-v59-blocked"
)

PUBLIC_REVIEW_ROOT = Path(
    "/root/Mini-Kuzai/data/external/"
    "smol-smoltalk/review"
)

CONTEXT = 2048

MARKER = (
    "##### SECTION RESULTS FOR ASSISTANT ######"
)


def git(*args):
    process = subprocess.run(
        [
            "git",
            "-C",
            str(REPO),
            *args,
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    if process.returncode:
        raise RuntimeError(
            "Git operation failed: "
            + process.stderr.strip()
        )

    return process.stdout.strip()


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


V57 = load_module(
    "phase03_v57_for_v59_blocked",
    V57_PATH,
)

SEG = load_module(
    "phase03_segmentation_v59_blocked",
    SEGMENTATION_PATH,
)


def preflight():
    if (
        git(
            "rev-parse",
            "--show-toplevel",
        )
        != str(REPO)
    ):
        raise RuntimeError(
            "Unexpected repository root"
        )

    if (
        git(
            "branch",
            "--show-current",
        )
        != "main"
        or git(
            "status",
            "--porcelain",
        )
    ):
        raise RuntimeError(
            "Clean main branch required"
        )

    git(
        "fetch",
        "--quiet",
        "origin",
        "main",
    )

    if (
        git(
            "rev-parse",
            "HEAD",
        )
        != git(
            "rev-parse",
            "origin/main",
        )
    ):
        raise RuntimeError(
            "Local main differs from remote main"
        )

    if (
        DEST.exists()
        or DEST.is_symlink()
    ):
        raise RuntimeError(
            "V59 blocked review packet already exists"
        )

    if not PUBLIC_REVIEW_ROOT.is_dir():
        raise RuntimeError(
            "Public SmolTalk review workspace missing"
        )


def blocked_rows():
    tokenizer = V57.load_tokenizer()

    count_text = V57.make_fast_counter(
        tokenizer
    )

    pool = V57.load_pool()
    v44 = V57.load_v44()

    v44_sha = {
        row["source_content_sha256"]
        for row in v44
    }

    selected = []

    for row in pool:
        sha = row["content_sha256"]

        counts = SEG.pair_token_counts(
            row["messages"],
            serialize_messages=V57.CONV.serialize_messages,
            validate_messages=V57.CONV.validate_messages,
            count_text=count_text,
        )

        oversized = [
            (
                index,
                value,
            )
            for index, value
            in enumerate(
                counts,
                1,
            )
            if value > CONTEXT
        ]

        if not oversized:
            continue

        selected.append(
            {
                "sha":
                    sha,
                "source_dataset":
                    row["source"],
                "messages":
                    row["messages"],
                "pair_counts":
                    counts,
                "oversized":
                    oversized,
                "in_v44":
                    sha in v44_sha,
            }
        )

    selected.sort(
        key=lambda row: row["sha"]
    )

    if len(selected) != 10:
        raise RuntimeError(
            "Expected exactly 10 blocked public conversations"
        )

    if (
        sum(
            row["in_v44"]
            for row in selected
        )
        != 3
    ):
        raise RuntimeError(
            "Expected exactly 3 blocked V44 conversations"
        )

    if (
        sum(
            len(row["oversized"])
            for row in selected
        )
        != 10
    ):
        raise RuntimeError(
            "Expected exactly 10 oversized pairs"
        )

    return selected


def escape_content(value):
    safe = html.escape(
        value,
        quote=True,
    ).replace(
        "\r",
        "&#13;",
    )

    return "\n".join(
        line.rstrip(" \t")
        + line[
            len(
                line.rstrip(" \t")
            ):
        ].replace(
            " ",
            "&#32;",
        ).replace(
            "\t",
            "&#9;",
        )
        for line in safe.split(
            "\n"
        )
    )


def case_page(
    index,
    row,
):
    oversized_pairs = ", ".join(
        str(pair_index)
        for pair_index, _
        in row["oversized"]
    )

    oversized_tokens = ", ".join(
        str(token_count)
        for _, token_count
        in row["oversized"]
    )

    parts = [
        "# V59 public SmolTalk oversized-pair review {:02d}/10".format(index),
        "",
        "V59 disposition: PENDING",
        "V59 rationale: NOT_REVIEWED",
        "",
        "Context limit: 2048",
        "V44 provisional member: "
        + (
            "YES"
            if row["in_v44"]
            else "NO"
        ),
        "Blocked pair index: "
        + oversized_pairs,
        "Blocked pair tokens: "
        + oversized_tokens,
        "Maximum pair tokens: "
        + str(
            max(
                row["pair_counts"]
            )
        ),
        "Public external subset: "
        + row["source_dataset"],
        "Public content SHA-256: "
        + row["sha"],
        "",
        "## Pair token counts",
        "",
        " | ".join(
            "{}:{}".format(
                pair_index,
                token_count,
            )
            for pair_index, token_count
            in enumerate(
                row["pair_counts"],
                1,
            )
        ),
        "",
        "## Public external source dialogue",
        "",
        "Source: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk",
        "",
    ]

    for turn, message in enumerate(
        row["messages"],
        1,
    ):
        parts.extend(
            [
                "### Turn {} - {}".format(
                    turn,
                    message["role"].upper(),
                ),
                "",
                "<pre>",
                escape_content(
                    message["content"]
                ),
                "</pre>",
                "",
            ]
        )

    parts.extend(
        [
            "## V59 decision rule",
            "",
            "Edit only V59 disposition and V59 rationale.",
            "",
            "Allowed dispositions:",
            "",
            "- EXCLUDE - do not use this conversation in the public training mix.",
            "- REPLACE - exclude this conversation and replace its intended coverage with another public candidate.",
            "- SPECIAL_POLICY - retain only after a separately specified and reviewed non-truncating policy exists.",
            "- HOLD - insufficient evidence for a decision.",
            "",
            "Do not use arbitrary intra-message or intra-pair token slicing.",
            "A disposition is a data-preparation decision, not training authorization.",
            "",
        ]
    )

    return "\n".join(
        parts
    )


def main():
    preflight()

    rows = blocked_rows()

    with tempfile.TemporaryDirectory(
        prefix="v59-blocked-public-",
        dir=PUBLIC_REVIEW_ROOT,
    ) as scratch:
        draft = (
            Path(scratch)
            / "smoltalk-v59-blocked"
        )

        cases = (
            draft
            / "cases"
        )

        cases.mkdir(
            parents=True
        )

        staged = set()

        index = [
            "# Mini-Kuzai V59 - public oversized-pair review",
            "",
            "This packet contains the 10 public SmolTalk conversations whose",
            "single USER / MINI-KUZAI pair exceeds the frozen 2048-token context.",
            "",
            "Exactly 3 are members of the provisional V44 population.",
            "No private, VALIDATION or BLIND TEST material is included.",
            "",
            "All dispositions start at PENDING.",
            "",
            "| Case | V44 | Max pair tokens | Source | Review |",
            "| ---: | --- | ---: | --- | --- |",
        ]

        for index_number, row in enumerate(
            rows,
            1,
        ):
            filename = (
                "{:02d}-{}.md".format(
                    index_number,
                    row["sha"][:16],
                )
            )

            page = case_page(
                index_number,
                row,
            )

            if (
                len(
                    page.encode(
                        "utf-8"
                    )
                )
                > 400000
            ):
                raise RuntimeError(
                    "Public review case exceeds size cap"
                )

            (
                cases
                / filename
            ).write_text(
                page,
                encoding="utf-8",
            )

            staged.add(
                "reviews/smoltalk-v59-blocked/cases/"
                + filename
            )

            index.append(
                "| {} | {} | {} | {} | [Review](cases/{}) |".format(
                    index_number,
                    (
                        "YES"
                        if row["in_v44"]
                        else "NO"
                    ),
                    max(
                        row["pair_counts"]
                    ),
                    row["source_dataset"],
                    filename,
                )
            )

        (
            draft
            / "README.md"
        ).write_text(
            "\n".join(
                index
            )
            + "\n",
            encoding="utf-8",
        )

        staged.add(
            "reviews/smoltalk-v59-blocked/README.md"
        )

        shutil.copytree(
            draft,
            DEST,
        )

    committed = False

    try:
        git(
            "add",
            "--",
            *sorted(
                staged
            ),
        )

        actual = set(
            git(
                "diff",
                "--cached",
                "--name-only",
            ).splitlines()
        )

        if actual != staged:
            raise RuntimeError(
                "Unexpected staged files; commit blocked"
            )

        git(
            "diff",
            "--cached",
            "--check",
        )

        git(
            "commit",
            "-m",
            "V59: publish public oversized-pair review packet",
        )

        committed = True

    except Exception:
        if not committed:
            git(
                "reset",
                "--quiet",
                "--",
                *sorted(
                    staged
                ),
            )

            shutil.rmtree(
                DEST,
                ignore_errors=True,
            )

        raise

    push = subprocess.run(
        [
            "git",
            "-C",
            str(REPO),
            "push",
            "origin",
            "main",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    if push.returncode:
        raise RuntimeError(
            "Commit exists but push failed; never force push"
        )

    git(
        "fetch",
        "--quiet",
        "origin",
        "main",
    )

    if (
        git(
            "rev-parse",
            "HEAD",
        )
        != git(
            "rev-parse",
            "origin/main",
        )
    ):
        raise RuntimeError(
            "Remote sync verification failed"
        )

    print(MARKER)
    print("V59_BLOCKED_PUBLIC_CASES: 10")
    print("V59_BLOCKED_V44_CASES: 3")
    print("V59_BLOCKED_POOL_ONLY_CASES: 7")
    print("V59_REVIEWED: 0")
    print("V59_TRAINING_AUTHORIZED: 0")
    print(
        "GIT_HEAD:",
        git(
            "rev-parse",
            "--short",
            "HEAD",
        ),
    )


if __name__ == "__main__":
    try:
        main()
    except (
        RuntimeError,
        OSError,
        KeyError,
        ValueError,
        TypeError,
    ) as exc:
        print(MARKER)
        print("V59_EXPORT: NOT_CONFIRMED")
        print(
            "ERROR:",
            str(exc),
        )
        sys.exit(1)
