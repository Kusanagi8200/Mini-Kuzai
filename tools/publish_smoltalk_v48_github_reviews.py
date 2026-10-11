#!/usr/bin/env python3
"""One-time export of 68 PUBLIC SmolTalk V48 cases to GitHub Markdown.

This command does not read private ChatGPT exports or the local human review
ledger. It verifies every case against the 8000-record external SmolTalk pool.
All newly published review decisions start as PENDING.
"""
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from collections import Counter

REPO = Path(__file__).resolve().parents[1]
ROOT = Path("/root/Mini-Kuzai/data/external/smol-smoltalk")
POOL = ROOT / "candidates/external-candidate-pool-v0.4.jsonl"
V44 = ROOT / "review/stratified-candidates-v44.jsonl"
V46 = ROOT / "review/v46-manual-review-queue.jsonl"
DEST = REPO / "reviews/smoltalk-v48"
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"
SOURCES = {
    "smol-magpie-ultra-short": 5000, "openhermes-50k": 1500,
    "self-oss-instruct": 1000, "explore-instruct-rewrite": 500,
}
REASONS = {"RELABEL": 12, "RESCUE": 24, "BASE": 32}
CATEGORIES = {
    "FOLLOWUP", "WRITING", "CREATIVE", "FACTUAL_QA", "MATHEMATICS",
    "PROGRAMMING", "PRACTICAL_ADVICE", "GENERAL_OTHER",
}
SHA = re.compile(r"[a-f0-9]{64}\Z")

def git(*args):
    cmd = subprocess.run(["git", "-C", str(REPO), *args],
                         capture_output=True, text=True, check=False)
    if cmd.returncode:
        raise RuntimeError("Git command failed: " + cmd.stderr.strip())
    return cmd.stdout.strip()

def rows(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing local public SmolTalk input")
    with path.open(encoding="utf-8") as file:
        for line in file:
            if line.strip():
                yield json.loads(line)

def dialogue(msg):
    return (
        isinstance(msg, list) and len(msg) in (2, 4, 6)
        and [r.get("role") for r in msg] == ["user", "assistant"] * (len(msg) // 2)
        and all(isinstance(r.get("content"), str) and r["content"].strip() for r in msg)
    )

def preflight_git():
    if git("rev-parse", "--show-toplevel") != str(REPO):
        raise RuntimeError("Incorrect Git checkout")
    if git("branch", "--show-current") != "main" or git("status", "--porcelain"):
        raise RuntimeError("Clean main branch required")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Pull origin/main --ff-only before publishing")
    if DEST.exists() or DEST.is_symlink():
        raise RuntimeError("Review export already exists; no overwrite permitted")
    if ROOT.resolve().is_relative_to(REPO.resolve()):
        raise RuntimeError("Private or in-repository source location rejected")

def verified_cases():
    pool = {}
    counter = Counter()
    for rec in rows(POOL):
        sha, src, messages = rec.get("content_sha256"), rec.get("source"), rec.get("messages")
        if (not isinstance(sha, str) or not SHA.fullmatch(sha)
            or sha in pool or src not in SOURCES or not dialogue(messages)):
            raise RuntimeError("SmolTalk source integrity mismatch")
        pool[sha] = rec
        counter[src] += 1
    if len(pool) != 8000 or counter != SOURCES:
        raise RuntimeError("Unexpected external reservoir composition")

    v44 = {}
    for rec in rows(V44):
        sha, cat = rec.get("source_content_sha256"), rec.get("heuristic_category")
        if (sha in v44 or sha not in pool or cat not in CATEGORIES
            or rec.get("source_dataset") != pool[sha]["source"]
            or rec.get("messages") != pool[sha]["messages"]
            or rec.get("training_approved") is not False
            or rec.get("dataset_split_assigned") is not False):
            raise RuntimeError("Provisional V44 selection changed")
        v44[sha] = cat
    if len(v44) != 1139:
        raise RuntimeError("Wrong V44 size")

    result, seen, counts, base = [], set(), Counter(), Counter()
    for rec in rows(V46):
        sha, why = rec.get("source_content_sha256"), rec.get("review_queue_reason")
        if (sha in seen or sha not in pool or why not in REASONS
            or rec.get("source_dataset") != pool[sha]["source"]
            or rec.get("messages_original") != pool[sha]["messages"]
            or rec.get("v44_selected") is not (sha in v44)
            or rec.get("v44_category") != v44.get(sha)
            or rec.get("review_decision") != "UNREVIEWED"
            or rec.get("training_approved") is not False
            or rec.get("dataset_split_assigned") is not False):
            raise RuntimeError("V46 queue diverges from public reservoir")
        if why == "BASE":
            base[rec["v44_category"]] += 1
        elif why == "RELABEL":
            if sha not in v44 or v44[sha] == "CREATIVE" or rec["broad_creative_signal"] is not True:
                raise RuntimeError("Invalid RELABEL entry")
        elif sha in v44 or rec["broad_creative_signal"] is not True:
            raise RuntimeError("Invalid RESCUE entry")
        seen.add(sha)
        counts[why] += 1
        result.append((rec, pool[sha]))
    if len(result) != 68 or counts != REASONS or base != {c: 4 for c in CATEGORIES}:
        raise RuntimeError("V46 queue must contain 68 verified cases")
    return sorted(result, key=lambda entry: (
        {"RELABEL":0,"RESCUE":1,"BASE":2}[entry[0]["review_queue_reason"]],
        entry[0]["source_content_sha256"],
    ))

def escaped(text):
    safe = html.escape(text, quote=True).replace("\r", "&#13;")
    return "\n".join(
        line.rstrip(" \t") + line[len(line.rstrip(" \t")):].replace(" ", "&#32;").replace("\t", "&#9;")
        for line in safe.split("\n")
    )

def page(i, row, original):
    out = [
        "# V48 public SmolTalk review {:02d}/68".format(i), "",
        "Review status: PENDING", "Review rationale: NOT_REVIEWED", "",
        "Reason: " + row["review_queue_reason"],
        "External subset: " + row["source_dataset"],
        "V44 category: " + (row["v44_category"] or "NOT_SELECTED"),
        "External content SHA-256: " + row["source_content_sha256"], "",
        "## Public-source dialogue", "",
        "Source: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk", "",
    ]
    for n, msg in enumerate(original["messages"], 1):
        out.extend(["### Turn {} - {}".format(n, msg["role"].upper()), "",
                    "<pre>", escaped(msg["content"]), "</pre>", ""])
    out.extend([
        "## Review procedure", "",
        "Edit the two Review fields at the top directly on GitHub.",
        "Valid statuses: PENDING, RETAIN, REJECT, HOLD.",
        "A completed decision requires a specific rationale.",
        "RETAIN is only a candidate-review decision and does not approve TRAIN.",
        "",
    ])
    return "\n".join(out)

def main():
    preflight_git()
    cases = verified_cases()
    tmp_root = ROOT / "backups"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="github-v48-", dir=tmp_root) as tmp:
        draft = Path(tmp) / "smoltalk-v48"
        folder = draft / "cases"
        folder.mkdir(parents=True)
        index = [
            "# Phase 03 - V48 public SmolTalk reviews", "",
            "68 public-source conversations, initially all PENDING.",
            "Only external SmolTalk material is included. Never publish private",
            "ChatGPT exports, private review ledgers or private-derived metrics.", "",
            "Source: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk",
            "Upstream dataset card identifies Apache-2.0 licensing; retain attribution.", "",
            "Edit each case on GitHub: Review status and Review rationale.",
            "RETAIN / REJECT / HOLD are quality triage, never authorization for TRAIN.", "",
            "| Number | Queue reason | External subset | Review |",
            "|---:|---|---|---|",
        ]
        staged = set()
        for i, (row, external) in enumerate(cases, 1):
            file = "{:03d}-{}.md".format(i, row["source_content_sha256"][:16])
            data = page(i, row, external)
            if len(data.encode("utf-8")) > 250000:
                raise RuntimeError("External example too large")
            (folder / file).write_text(data, encoding="utf-8")
            index.append("| {} | {} | {} | [Open case {}](cases/{}) |".format(
                i, row["review_queue_reason"], row["source_dataset"], i, file))
            staged.add("reviews/smoltalk-v48/cases/" + file)
        (draft / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
        staged.add("reviews/smoltalk-v48/README.md")
        total_bytes = sum(x.stat().st_size for x in draft.rglob("*.md"))
        if total_bytes > 10000000:
            raise RuntimeError("Excessive external text export")
        shutil.copytree(draft, DEST)
    committed = False
    try:
        git("add", "--", *sorted(staged))
        if set(git("diff", "--cached", "--name-only").splitlines()) != staged:
            raise RuntimeError("Unexpected staged paths")
        git("diff", "--cached", "--check")
        git("commit", "-m", "Publish 68 public SmolTalk V48 reviews for GitHub evaluation")
        committed = True
    except Exception:
        if not committed:
            git("reset", "--quiet", "--", *sorted(staged))
            shutil.rmtree(DEST)
        raise
    push = subprocess.run(["git", "-C", str(REPO), "push", "origin", "main"],
                          capture_output=True, text=True, check=False)
    if push.returncode != 0:
        raise RuntimeError("Commit exists but push failed; inspect, do not force push")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Remote verification failed")
    print(MARKER)
    print("GITHUB_REVIEWS: 68")
    print("REVIEW_STATUS: PENDING")
    print("TRAIN_APPROVED: 0")
    print("GIT_HEAD:", git("rev-parse", "--short", "HEAD"))
    print("GOGIT: REVIEWS_READY")

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, KeyError, ValueError, TypeError) as exc:
        print(MARKER)
        print("PUBLISH: NOT_CONFIRMED")
        print("ERROR:", str(exc))
        sys.exit(1)
