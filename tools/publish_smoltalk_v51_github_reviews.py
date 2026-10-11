#!/usr/bin/env python3
"""Publish 24 verified PUBLIC SmolTalk V51 cases, without private inputs.

A one-time deterministic balanced pilot: HIGH 12, MEDIUM 6, LOW 6.
All 1,139 V50 candidates are checked against the verified public reservoir.
Nothing is approved for TRAIN; no previously published cases are overwritten.
"""
import hashlib
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path("/root/Mini-Kuzai/data/external/smol-smoltalk")
POOL = ROOT / "candidates/external-candidate-pool-v0.4.jsonl"
V44 = ROOT / "review/stratified-candidates-v44.jsonl"
V50 = ROOT / "review/v50-cognitive-review-priority.jsonl"
SUMMARY = ROOT / "review/v50-cognitive-review-summary.json"
OLD = REPO / "reviews/smoltalk-v48/cases"
DEST = REPO / "reviews/smoltalk-v51"
MODULE = REPO / "tools/public-audits/smoltalk_v50_cognitive_screen.py"
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"
QUOTAS = {"HIGH": 12, "MEDIUM": 6, "LOW": 6}
EXPECTED_PRIORITY = {"HIGH": 200, "MEDIUM": 431, "LOW": 508}
SOURCE_COUNTS = {
    "smol-magpie-ultra-short": 5000, "openhermes-50k": 1500,
    "self-oss-instruct": 1000, "explore-instruct-rewrite": 500,
}
SHA = re.compile(r"[a-f0-9]{64}\Z")


def git(*args):
    process = subprocess.run(
        ["git", "-C", str(REPO), *args], text=True, capture_output=True,
        check=False
    )
    if process.returncode:
        raise RuntimeError("Git operation failed: " + process.stderr.strip())
    return process.stdout.strip()


def load_v50_module():
    spec = importlib.util.spec_from_file_location("v50_public_smoltalk", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load V50 public audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight():
    if git("rev-parse", "--show-toplevel") != str(REPO):
        raise RuntimeError("Not inside the expected Git repository")
    if git("branch", "--show-current") != "main" or git("status", "--porcelain"):
        raise RuntimeError("Clean main branch required")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local main differs from remote main")
    if DEST.exists() or DEST.is_symlink():
        raise RuntimeError("V51 export already exists; refusing overwrite")
    if ROOT.resolve().is_relative_to(REPO.resolve()):
        raise RuntimeError("Public SmolTalk source must remain outside Git")
    if not OLD.is_dir() or OLD.is_symlink():
        raise RuntimeError("V48 public review directory is missing")


def verified_candidates():
    v50 = load_v50_module()
    pool = {}
    counts = Counter()
    for rec in v50.read_jsonl(POOL):
        sha, source, messages = (
            rec.get("content_sha256"), rec.get("source"), rec.get("messages")
        )
        if (not isinstance(sha, str) or not SHA.fullmatch(sha)
            or sha in pool or source not in SOURCE_COUNTS
            or not v50.valid_messages(messages)):
            raise RuntimeError("Invalid public SmolTalk source record")
        pool[sha] = rec
        counts[source] += 1
    if len(pool) != 8000 or counts != SOURCE_COUNTS:
        raise RuntimeError("Unexpected public SmolTalk reservoir")

    original_v44 = {}
    for rec in v50.read_jsonl(V44):
        sha = rec.get("source_content_sha256")
        if (sha in original_v44 or sha not in pool
            or rec.get("source_dataset") != pool[sha]["source"]
            or rec.get("messages") != pool[sha]["messages"]
            or rec.get("heuristic_category") not in v50.CATEGORIES
            or rec.get("training_approved") is not False
            or rec.get("dataset_split_assigned") is not False
            or rec.get("semantic_validation_complete") is not False):
            raise RuntimeError("V44 selection integrity check failed")
        original_v44[sha] = rec
    if len(original_v44) != 1139:
        raise RuntimeError("Expected exactly 1139 V44 candidates")

    if not SUMMARY.is_file() or SUMMARY.is_symlink():
        raise RuntimeError("V50 public-source summary unavailable")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if (summary.get("candidate_count") != 1139
        or summary.get("training_approved") is not False
        or summary.get("reviewed") != 0):
        raise RuntimeError("Unexpected V50 screening summary")

    candidates = {}
    prior = Counter()
    for rec in v50.read_jsonl(V50):
        sha = rec.get("source_content_sha256")
        v44 = original_v44.get(sha)
        if (v44 is None or sha in candidates
            or rec.get("source") != "SmolTalk v0.4 - external public dataset"
            or rec.get("schema") != "mini-kuzai.v50.public-smoltalk-local-screen"
            or rec.get("source_dataset") != pool[sha]["source"]
            or rec.get("messages") != pool[sha]["messages"]
            or rec.get("v44_heuristic_category") != v44["heuristic_category"]
            or rec.get("review_state") != "UNREVIEWED"
            or rec.get("training_approved") is not False
            or rec.get("dataset_split_assigned") is not False
            or rec.get("semantic_validation_complete") is not False
            or rec.get("factual_validation_complete") is not False):
            raise RuntimeError("V50 public-source queue integrity mismatch")
        recomputed = v50.signals(pool[sha]["messages"], v44["heuristic_category"])
        if any(rec.get(k) != value for k, value in recomputed.items()):
            raise RuntimeError("V50 priority hints do not match recomputation")
        if rec["priority_hint"] not in QUOTAS:
            raise RuntimeError("Unexpected priority category")
        candidates[sha] = rec
        prior[rec["priority_hint"]] += 1
    if (set(candidates) != set(original_v44)
        or prior != EXPECTED_PRIORITY):
        raise RuntimeError("V50 population or priority totals differ")

    excluded = set()
    pages = list(OLD.iterdir())
    if len(pages) != 68:
        raise RuntimeError("Unexpected V48 diagnostic page count")
    for p in pages:
        m = re.fullmatch(r"\d{3}-([a-f0-9]{16})\.md", p.name)
        if not m or not p.is_file() or p.is_symlink():
            raise RuntimeError("Invalid V48 public review page")
        excluded.add(m.group(1))
    eligible = [
        rec for rec in candidates.values()
        if rec["source_content_sha256"][:16] not in excluded
    ]
    return eligible


def sample_key(rec):
    seed = "MINI-KUZAI-V51-PUBLIC-BATCH-001|" + rec["source_content_sha256"]
    return hashlib.sha256(seed.encode("ascii")).hexdigest()


def select_batch(candidates):
    selection = []
    for priority, quota in QUOTAS.items():
        rows = sorted(
            (r for r in candidates if r["priority_hint"] == priority),
            key=sample_key,
        )
        chosen, seen = [], set()

        def add_first(predicate):
            for row in rows:
                sha = row["source_content_sha256"]
                if sha not in seen and predicate(row):
                    chosen.append(row)
                    seen.add(sha)
                    return

        for source in SOURCE_COUNTS:
            if len(chosen) < quota:
                add_first(lambda r, src=source: r["source_dataset"] == src)
        for category in sorted({
            r["v44_heuristic_category"] for r in rows
        }):
            if len(chosen) < quota:
                add_first(lambda r, cat=category:
                          r["v44_heuristic_category"] == cat)
        for row in rows:
            if len(chosen) >= quota:
                break
            add_first(lambda r, target=row:
                      r["source_content_sha256"] == target["source_content_sha256"])
        if len(chosen) != quota:
            raise RuntimeError("Insufficient V51 source candidates")
        selection.extend(chosen)
    if len(selection) != 24 or len({
        r["source_content_sha256"] for r in selection
    }) != 24:
        raise RuntimeError("Invalid V51 batch selection")
    return selection


def escape_content(value):
    safe = html.escape(value, quote=True).replace("\r", "&#13;")
    return "\n".join(
        line.rstrip(" \t") +
        line[len(line.rstrip(" \t")):].replace(" ", "&#32;").replace("\t", "&#9;")
        for line in safe.split("\n")
    )


def case_page(index, row):
    parts = [
        "# V51 public SmolTalk semantic review {:02d}/24".format(index), "",
        "V51 grade: PENDING",
        "V51 rationale: NOT_REVIEWED",
        "V51 cognition: UNREVIEWED",
        "V51 creativity: UNREVIEWED",
        "V51 continuity: UNREVIEWED",
        "V51 correction: UNREVIEWED",
        "V51 communication: UNREVIEWED",
        "V51 factual risk: UNREVIEWED",
        "V51 instruction fit: UNREVIEWED", "",
        "V50 priority hint: " + row["priority_hint"],
        "V44 heuristic category: " + row["v44_heuristic_category"],
        "Public external subset: " + row["source_dataset"],
        "Public content SHA-256: " + row["source_content_sha256"], "",
        "## Public external source dialogue", "",
        "Source: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk", "",
    ]
    for n, message in enumerate(row["messages"], 1):
        parts.extend([
            "### Turn {} - {}".format(n, message["role"].upper()), "",
            "<pre>", escape_content(message["content"]), "</pre>", "",
        ])
    parts.extend([
        "## V51 rubric", "",
        "Edit only the nine V51 fields near the top.",
        "Grades: PENDING, A, B, C, HOLD.",
        "Scores cognition, creativity, continuity, correction, communication: 0, 1, 2, 3.",
        "Factual risk: LOW, REVIEW, HIGH. Instruction fit: GOOD, PARTIAL, BAD.",
        "A reviewed grade requires scores and a substantive specific rationale.",
        "B may signal useful fragments but is not a clean full-conversation target.",
        "V51 review never approves TRAIN and never establishes independent human validation.",
        "",
    ])
    return "\n".join(parts)


def main():
    preflight()
    cases = select_batch(verified_candidates())
    with tempfile.TemporaryDirectory(prefix="v51-public-", dir=ROOT / "review") as scratch:
        draft = Path(scratch) / "smoltalk-v51"
        folder = draft / "cases"
        folder.mkdir(parents=True)
        staged = set()
        index = [
            "# Mini-Kuzai V51 - public cognitive and creative review", "",
            "Pilot batch: 24 external-public SmolTalk conversations.",
            "HIGH: 12, MEDIUM: 6, LOW: 6. Previous V48 cases excluded.",
            "All initial states are PENDING; no TRAIN approval.", "",
            "This is heuristic sampling for semantic review, not final corpus selection.",
            "Never add private ChatGPT data or private-derived information.", "",
            "| Case | V50 hint | V44 category | Source | Page |",
            "| ---: | --- | --- | --- | --- |",
        ]
        for i, row in enumerate(cases, 1):
            filename = "{:03d}-{}.md".format(i, row["source_content_sha256"][:16])
            page = case_page(i, row)
            if len(page.encode("utf-8")) > 250000:
                raise RuntimeError("Public example exceeds review limit")
            (folder / filename).write_text(page, encoding="utf-8")
            staged.add("reviews/smoltalk-v51/cases/" + filename)
            index.append("| {} | {} | {} | {} | [Review {}](cases/{}) |".format(
                i, row["priority_hint"], row["v44_heuristic_category"],
                row["source_dataset"], i, filename))
        (draft / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
        staged.add("reviews/smoltalk-v51/README.md")
        if sum(f.stat().st_size for f in draft.rglob("*.md")) > 8000000:
            raise RuntimeError("Public review batch exceeds size cap")
        shutil.copytree(draft, DEST)

    committed = False
    try:
        git("add", "--", *sorted(staged))
        if set(git("diff", "--cached", "--name-only").splitlines()) != staged:
            raise RuntimeError("Unexpected staged files; commit blocked")
        git("diff", "--cached", "--check")
        git("commit", "-m", "Publish 24 verified public SmolTalk V51 semantic review cases")
        committed = True
    except Exception:
        if not committed:
            git("reset", "--quiet", "--", *sorted(staged))
            shutil.rmtree(DEST)
        raise
    pushed = subprocess.run(
        ["git", "-C", str(REPO), "push", "origin", "main"],
        capture_output=True, text=True, check=False
    )
    if pushed.returncode:
        raise RuntimeError("Commit exists but push failed; never force push")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Remote sync verification failed")
    print(MARKER)
    print("V51_PUBLIC_CASES: 24")
    print("V51_HIGH: 12")
    print("V51_MEDIUM: 6")
    print("V51_LOW: 6")
    print("V51_REVIEWED: 0")
    print("V51_TRAIN_APPROVED: 0")
    print("GIT_HEAD:", git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, KeyError, ValueError, TypeError) as exc:
        print(MARKER)
        print("V51_EXPORT: NOT_CONFIRMED")
        print("ERROR:", str(exc))
        sys.exit(1)
