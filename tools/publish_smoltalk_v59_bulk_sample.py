#!/usr/bin/env python3
"""Publish deterministic V59 bulk-quality sample from public SmolTalk.

The sample is drawn only from the 1,080 currently unreviewed members of the
V59 final candidate population. No private, VALIDATION or BLIND data are read.
"""

from __future__ import annotations

import hashlib
import html
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SOURCE_MODULE = REPO / "tools" / "phase03_v59_final_candidate_mix.py"
DEST = REPO / "reviews" / "smoltalk-v59-bulk-sample-001"
PUBLIC_REVIEW_ROOT = Path(
    "/root/Mini-Kuzai/data/external/smol-smoltalk/review"
)
SAMPLE_SIZE = 72
PER_STRATUM = 3
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MIX = load_module("phase03_v59_candidate_mix_for_sample", SOURCE_MODULE)


def git(*args):
    process = subprocess.run(
        ["git", "-C", str(REPO), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode:
        raise RuntimeError(
            "Git operation failed: " + process.stderr.strip()
        )
    return process.stdout.strip()


def preflight():
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Expected main branch")
    if git("status", "--porcelain"):
        raise RuntimeError("Clean worktree required")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local main differs from origin/main")
    if DEST.exists() or DEST.is_symlink():
        raise RuntimeError("V59 bulk sample already exists")
    if not PUBLIC_REVIEW_ROOT.is_dir():
        raise RuntimeError("Public SmolTalk review workspace missing")


def stable_rank(sha):
    return hashlib.sha256(
        ("v59-bulk-sample-001:" + sha).encode("ascii")
    ).hexdigest()


def eligible_population():
    queue = list(MIX.read_jsonl(MIX.V50_QUEUE))
    if len(queue) != 1139:
        raise RuntimeError("V50 queue population changed")

    queue_by_sha = {
        row["source_content_sha256"]: row
        for row in queue
    }

    reviews = MIX.reviewed_exclusions()
    tokenizer = MIX.V57.load_tokenizer()
    count_text = MIX.V57.make_fast_counter(tokenizer)

    pool_by_sha = {
        row["content_sha256"]: row
        for row in MIX.V57.load_pool()
    }

    eligible = []

    for row in MIX.V57.load_v44():
        sha = row["source_content_sha256"]
        q = queue_by_sha[sha]

        pair_counts = MIX.SEG.pair_token_counts(
            row["messages"],
            serialize_messages=MIX.V57.CONV.serialize_messages,
            validate_messages=MIX.V57.CONV.validate_messages,
            count_text=count_text,
        )

        if max(pair_counts) > MIX.CONTEXT:
            continue
        if sha in MIX.CONTROLLED_SOURCE_SHAS:
            continue
        if sha in reviews["union"]:
            continue
        if sha in reviews["reviewed"]:
            continue

        base = pool_by_sha.get(sha)
        if base is None or base["messages"] != row["messages"]:
            raise RuntimeError("Public source mismatch")

        eligible.append({
            "sha": sha,
            "source_dataset": row["source_dataset"],
            "heuristic_category": row["heuristic_category"],
            "priority_hint": q["priority_hint"],
            "turn_bucket": (
                "MULTITURN"
                if len(row["messages"]) > 2
                else "SINGLE"
            ),
            "messages": row["messages"],
            "rank": stable_rank(sha),
        })

    if len(eligible) != 1080:
        raise RuntimeError(
            f"Expected 1080 unreviewed eligible cases, got {len(eligible)}"
        )

    return eligible


def category_round_robin(rows, limit):
    by_category = defaultdict(list)
    for row in rows:
        by_category[row["heuristic_category"]].append(row)

    for values in by_category.values():
        values.sort(key=lambda row: row["rank"])

    result = []
    categories = sorted(by_category)

    while len(result) < limit:
        progressed = False
        for category in categories:
            values = by_category[category]
            if values:
                result.append(values.pop(0))
                progressed = True
                if len(result) == limit:
                    break
        if not progressed:
            break

    return result


def draw_sample(population):
    strata = defaultdict(list)
    for row in population:
        key = (
            row["priority_hint"],
            row["source_dataset"],
            row["turn_bucket"],
        )
        strata[key].append(row)

    selected = []
    selected_sha = set()

    for key in sorted(strata):
        chosen = category_round_robin(
            strata[key],
            PER_STRATUM,
        )
        for row in chosen:
            selected.append(row)
            selected_sha.add(row["sha"])

    if len(selected) < SAMPLE_SIZE:
        remaining = sorted(
            (
                row
                for row in population
                if row["sha"] not in selected_sha
            ),
            key=lambda row: row["rank"],
        )
        for row in remaining[: SAMPLE_SIZE - len(selected)]:
            selected.append(row)
            selected_sha.add(row["sha"])

    if len(selected) != SAMPLE_SIZE or len(selected_sha) != SAMPLE_SIZE:
        raise RuntimeError("Unable to create deterministic 72-case sample")

    selected.sort(
        key=lambda row: (
            row["priority_hint"],
            row["source_dataset"],
            row["turn_bucket"],
            row["rank"],
        )
    )

    return selected, strata


def escape_content(value):
    safe = html.escape(value, quote=True).replace("\r", "&#13;")
    return "\n".join(
        line.rstrip(" \t")
        + line[len(line.rstrip(" \t")):]
        .replace(" ", "&#32;")
        .replace("\t", "&#9;")
        for line in safe.split("\n")
    )


def case_page(index, row):
    parts = [
        f"# V59 public bulk sample review {index:02d}/72",
        "",
        "V59 grade: PENDING",
        "V59 factual risk: PENDING",
        "V59 instruction fit: PENDING",
        "V59 persona value: PENDING",
        "V59 disposition: PENDING",
        "V59 rationale: NOT_REVIEWED",
        "",
        f"V50 priority hint: {row['priority_hint']}",
        f"V44 heuristic category: {row['heuristic_category']}",
        f"Turn bucket: {row['turn_bucket']}",
        f"Public external subset: {row['source_dataset']}",
        f"Public content SHA-256: {row['sha']}",
        "",
        "## Public external source dialogue",
        "",
        "Source: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk",
        "",
    ]

    for turn, message in enumerate(row["messages"], 1):
        parts.extend([
            f"### Turn {turn} - {message['role'].upper()}",
            "",
            "<pre>",
            escape_content(message["content"]),
            "</pre>",
            "",
        ])

    parts.extend([
        "## Review rubric",
        "",
        "- Grade A: coherent positive target.",
        "- Grade B: behaviorally useful but imperfect; keep only with caveat or repair.",
        "- Grade C: unsuitable unchanged as a positive target.",
        "- Factual risk: LOW / REVIEW / HIGH.",
        "- Instruction fit: GOOD / PARTIAL / BAD.",
        "- Persona value: HIGH / MEDIUM / LOW.",
        "- Disposition: KEEP / REPAIR / EXCLUDE.",
        "",
        "The priority hint is heuristic and must not determine the review.",
        "",
    ])

    return "\n".join(parts)


def main():
    preflight()
    population = eligible_population()
    selected, strata = draw_sample(population)

    with tempfile.TemporaryDirectory(
        prefix="v59-bulk-sample-",
        dir=PUBLIC_REVIEW_ROOT,
    ) as scratch:
        draft = Path(scratch) / "smoltalk-v59-bulk-sample-001"
        cases = draft / "cases"
        cases.mkdir(parents=True)

        staged = set()
        index_lines = [
            "# Mini-Kuzai V59 - bulk quality sample 001",
            "",
            "Status: 72-case deterministic public SmolTalk review sample.",
            "",
            "Population: 1,080 currently unreviewed members of the V59 final candidate mix.",
            "Sampling: priority x source x turn bucket, target 3 per stratum, with category round-robin and deterministic top-up.",
            "",
            "No private, VALIDATION or BLIND TEST material is included.",
            "All review fields start PENDING.",
            "",
            "| Case | Priority | Source | Turns | Category | Review |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]

        for index, row in enumerate(selected, 1):
            filename = f"{index:02d}-{row['sha'][:16]}.md"
            page = case_page(index, row)
            (cases / filename).write_text(page, encoding="utf-8")
            staged.add(
                "reviews/smoltalk-v59-bulk-sample-001/cases/" + filename
            )
            index_lines.append(
                "| {} | {} | {} | {} | {} | [Review](cases/{}) |".format(
                    index,
                    row["priority_hint"],
                    row["source_dataset"],
                    row["turn_bucket"],
                    row["heuristic_category"],
                    filename,
                )
            )

        index_lines.extend([
            "",
            "## Sampling coverage",
            "",
            f"Eligible unreviewed population: {len(population)}",
            f"Sample size: {len(selected)}",
            f"Observed strata: {len(strata)}",
            "",
            "This sample is a quality gate, not training authorization.",
            "",
        ])

        (draft / "README.md").write_text(
            "\n".join(index_lines),
            encoding="utf-8",
        )
        staged.add("reviews/smoltalk-v59-bulk-sample-001/README.md")

        shutil.copytree(draft, DEST)

    committed = False
    try:
        git("add", "--", *sorted(staged))
        actual = set(
            git("diff", "--cached", "--name-only").splitlines()
        )
        if actual != staged:
            raise RuntimeError("Unexpected staged files")
        git("diff", "--cached", "--check")
        git(
            "commit",
            "-m",
            "V59: publish deterministic bulk quality sample 001",
        )
        committed = True
    except Exception:
        if not committed:
            git("reset", "--quiet", "--", *sorted(staged))
            shutil.rmtree(DEST, ignore_errors=True)
        raise

    push = subprocess.run(
        ["git", "-C", str(REPO), "push", "origin", "main"],
        text=True,
        capture_output=True,
        check=False,
    )
    if push.returncode:
        raise RuntimeError("Commit exists but push failed; never force push")

    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Remote synchronization failed")

    print(MARKER)
    print("V59_BULK_SAMPLE_POPULATION: 1080")
    print("V59_BULK_SAMPLE_SIZE: 72")
    print("V59_BULK_SAMPLE_REVIEWED: 0")
    print("TRAINING_AUTHORIZED: 0")
    print("GIT_HEAD:", git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(MARKER)
        print("V59_BULK_SAMPLE_EXPORT: NOT_CONFIRMED")
        print("ERROR:", str(exc))
        raise
