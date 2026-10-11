#!/usr/bin/env python3
"""Publish a deterministic 32-case PUBLIC SmolTalk V52 review batch.

The 1,139 V44/V50 candidates and V48/V51 source excerpts are checked
against the local public SmolTalk reservoir. Private sources are never read.
The original V48, V51, V44, TRAIN and evaluation files are not changed.
"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path("/root/Mini-Kuzai/data/external/smol-smoltalk")
V51_MODULE = REPO / "tools/publish_smoltalk_v51_github_reviews.py"
V51_PROGRESS = REPO / "tools/public-audits/smoltalk_v51_github_progress.py"
V52_INVENTORY = REPO / "tools/public-audits/smoltalk_v52_inventory.py"
V52_INVENTORY_REPORT = (
    REPO / "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V52-INVENTORY-001.json"
)
DEST = REPO / "reviews/smoltalk-v52"
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

# Source and multi-turn coverage, with deliberate MEDIUM/LOW false-negative controls.
QUOTAS = {
    ("HIGH", "smol-magpie-ultra-short"): 8,
    ("MEDIUM", "smol-magpie-ultra-short"): 6,
    ("MEDIUM", "openhermes-50k"): 3,
    ("MEDIUM", "self-oss-instruct"): 1,
    ("MEDIUM", "explore-instruct-rewrite"): 2,
    ("LOW", "smol-magpie-ultra-short"): 6,
    ("LOW", "openhermes-50k"): 3,
    ("LOW", "self-oss-instruct"): 2,
    ("LOW", "explore-instruct-rewrite"): 1,
}
TOTAL = 32
PRIORITIES = ("HIGH", "MEDIUM", "LOW")
SOURCES = {
    "SMOL": "smol-magpie-ultra-short",
    "HERMES": "openhermes-50k",
    "OSS": "self-oss-instruct",
    "REWRITE": "explore-instruct-rewrite",
}
RUBRIC_DEFAULTS = {
    "V52 grade": "PENDING",
    "V52 rationale": "NOT_REVIEWED",
    "V52 cognition": "UNREVIEWED",
    "V52 creativity": "UNREVIEWED",
    "V52 continuity": "UNREVIEWED",
    "V52 correction": "UNREVIEWED",
    "V52 communication": "UNREVIEWED",
    "V52 factual risk": "UNREVIEWED",
    "V52 instruction fit": "UNREVIEWED",
}


def load(path, name):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe committed public audit module")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to import public audit module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight(v51):
    if v51.git("rev-parse", "--show-toplevel") != str(REPO):
        raise RuntimeError("Unexpected repository root")
    if v51.git("branch", "--show-current") != "main":
        raise RuntimeError("Expected main branch")
    if v51.git("status", "--porcelain"):
        raise RuntimeError("Expected clean worktree and index")
    v51.git("fetch", "--quiet", "origin", "main")
    if v51.git("rev-parse", "HEAD") != v51.git("rev-parse", "origin/main"):
        raise RuntimeError("Main and origin/main differ")
    if DEST.exists() or DEST.is_symlink():
        raise RuntimeError("V52 public case destination already exists")
    if ROOT.resolve().is_relative_to(REPO.resolve()):
        raise RuntimeError("Public source is inside Git; refusing publication")
    if not V52_INVENTORY_REPORT.is_file() or V52_INVENTORY_REPORT.is_symlink():
        raise RuntimeError("Verified V52 inventory report missing")


def verified_v52_pool(v51, v51_progress, v52_inventory):
    after_v48 = v51.verified_candidates()
    if len(after_v48) != 1139 - 44:
        raise RuntimeError("Unexpected 44 in-V44 V48 exclusions")
    excluded = v52_inventory.validated_v51_sha(
        v51, v51_progress, after_v48
    )
    remaining = [
        row for row in after_v48
        if row["source_content_sha256"] not in excluded
    ]
    summary = v52_inventory.inventory_metrics(remaining, 44, 24)
    report = json.loads(V52_INVENTORY_REPORT.read_text(encoding="utf-8"))
    if (
        report.get("step_id") != "PHASE03-SMOLTALK-V52-INVENTORY-001"
        or report.get("producer") !=
            "tools/public-audits/smoltalk_v52_inventory.py"
        or report.get("training_authorized") is not False
        or report.get("private_conversation_data_included") is not False
        or report.get("metrics") != summary
    ):
        raise RuntimeError("V52 source inventory differs from published audit")
    if len(remaining) != 1071:
        raise RuntimeError("Unexpected V52 remaining candidate count")
    return remaining


def sample_key(record):
    seed = "MINI-KUZAI-V52-PUBLIC-SEMANTIC-001|"
    return hashlib.sha256(
        (seed + record["source_content_sha256"]).encode("ascii")
    ).hexdigest()


def select_batch(records):
    """Deterministic, source-stratified and category-diverse sample."""
    if sum(QUOTAS.values()) != TOTAL:
        raise RuntimeError("Incorrect V52 batch configuration")
    chosen = []
    seen = set()
    for (priority, source), quota in QUOTAS.items():
        group = sorted(
            (rec for rec in records
             if rec["priority_hint"] == priority
             and rec["source_dataset"] == source),
            key=sample_key,
        )
        if len(group) < quota:
            raise RuntimeError("Insufficient verified public candidates")
        selected = []
        categories = set()
        # Give distinct V44 categories a chance before filling the quota.
        for rec in group:
            category = rec["v44_heuristic_category"]
            if category not in categories and len(selected) < quota:
                selected.append(rec)
                categories.add(category)
        selected_shas = {rec["source_content_sha256"] for rec in selected}
        for rec in group:
            if len(selected) == quota:
                break
            if rec["source_content_sha256"] not in selected_shas:
                selected.append(rec)
                selected_shas.add(rec["source_content_sha256"])
        if len(selected) != quota:
            raise RuntimeError("V52 source quota unfulfilled")
        for rec in selected:
            sha = rec["source_content_sha256"]
            if sha in seen:
                raise RuntimeError("Duplicate V52 public candidate")
            seen.add(sha)
            chosen.append(rec)
    if len(chosen) != TOTAL:
        raise RuntimeError("Invalid V52 batch size")
    return chosen


def page_name(index, record):
    return "{:03d}-{}.md".format(index, record["source_content_sha256"][:16])


def case_page(index, record, v51):
    lines = [
        "# V52 public SmolTalk semantic review {:02d}/32".format(index), "",
    ]
    lines.extend(
        name + ": " + value for name, value in RUBRIC_DEFAULTS.items()
    )
    lines.extend([
        "",
        "V50 priority hint: " + record["priority_hint"],
        "V44 heuristic category: " + record["v44_heuristic_category"],
        "Public external subset: " + record["source_dataset"],
        "Public content SHA-256: " + record["source_content_sha256"], "",
        "## Public external source dialogue", "",
        "Source: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk",
        "",
    ])
    for number, message in enumerate(record["messages"], 1):
        lines.extend([
            "### Turn {} - {}".format(number, message["role"].upper()),
            "",
            "<pre>", v51.escape_content(message["content"]), "</pre>", "",
        ])
    lines.extend([
        "## V52 rubric", "",
        "Edit only the nine V52 fields near the top.",
        "A = coherent and promising, with later source and split checks.",
        "B = valuable fragment, explicit segmentation or repair required.",
        "C = unsuitable as an unchanged positive persona training target.",
        "HOLD = unresolved review issue; PENDING = not yet evaluated.",
        "Score cognition, creativity, continuity, correction and",
        "communication from 0 to 3 independently.",
        "Factual risk: LOW, REVIEW, HIGH. Instruction fit: GOOD, PARTIAL, BAD.",
        "Factual errors cannot become positive answers merely because",
        "their conversation is behaviorally interesting.",
        "A/B/C/HOLD are AI-assisted research labels, not TRAIN approval.",
        "No independent human validation or tokenizer freeze is implied.",
        "",
    ])
    return "\n".join(lines)


def main():
    v51 = load(V51_MODULE, "v52_public_v51_publisher")
    progress = load(V51_PROGRESS, "v52_public_v51_progress")
    inventory = load(V52_INVENTORY, "v52_public_inventory")
    preflight(v51)
    selected = select_batch(verified_v52_pool(v51, progress, inventory))
    batch_counts = Counter((r["priority_hint"], r["source_dataset"])
                           for r in selected)
    if batch_counts != QUOTAS:
        raise RuntimeError("Unexpected V52 priority or source coverage")
    review_root = ROOT / "review"
    if not review_root.is_dir() or review_root.is_symlink():
        raise RuntimeError("Public-only review workspace unavailable")
    with tempfile.TemporaryDirectory(prefix="v52-public-", dir=review_root) as scratch:
        draft = Path(scratch) / "smoltalk-v52"
        case_dir = draft / "cases"
        case_dir.mkdir(parents=True)
        allowed = set()
        index = [
            "# Mini-Kuzai V52 - public persona-first semantic review", "",
            "32 distinct public-external SmolTalk cases, not previously published",
            "in V48/V49 or V51. All nine V52 fields begin PENDING.",
            "Heuristic HIGH/MEDIUM/LOW are NOT quality judgments.",
            "No private ChatGPT conversation or private-derived content.",
            "No TRAIN, tokenizer or evaluation split approval.", "",
            "| Case | V50 hint | V44 category | Public source | Review |",
            "| ---: | --- | --- | --- | --- |",
        ]
        total_bytes = 0
        for index_number, row in enumerate(selected, 1):
            filename = page_name(index_number, row)
            body = case_page(index_number, row, v51)
            page_bytes = body.encode("utf-8")
            if len(page_bytes) > 250000:
                raise RuntimeError("V52 single public review page exceeds cap")
            total_bytes += len(page_bytes)
            (case_dir / filename).write_bytes(page_bytes)
            allowed.add("reviews/smoltalk-v52/cases/" + filename)
            index.append("| {} | {} | {} | {} | [Case {}](cases/{}) |".format(
                index_number, row["priority_hint"],
                row["v44_heuristic_category"], row["source_dataset"],
                index_number, filename))
        if total_bytes > 8000000:
            raise RuntimeError("V52 public review batch exceeds size cap")
        (draft / "README.md").write_text(
            "\n".join(index) + "\n", encoding="utf-8"
        )
        allowed.add("reviews/smoltalk-v52/README.md")
        shutil.copytree(draft, DEST)
    committed = False
    try:
        v51.git("add", "--", *sorted(allowed))
        actual = set(v51.git("diff", "--cached", "--name-only").splitlines())
        if actual != allowed:
            raise RuntimeError("Unexpected staged file; publication blocked")
        v51.git("diff", "--cached", "--check")
        v51.git("commit", "-m",
                "Publish 32 verified public SmolTalk V52 persona review cases")
        committed = True
    except Exception:
        if not committed:
            v51.git("reset", "--quiet", "--", *sorted(allowed))
            shutil.rmtree(DEST)
        raise
    push = subprocess.run(
        ["git", "-C", str(REPO), "push", "origin", "main"],
        text=True, capture_output=True, check=False,
    )
    if push.returncode:
        raise RuntimeError("Commit exists but push failed; never force-push")
    v51.git("fetch", "--quiet", "origin", "main")
    if v51.git("rev-parse", "HEAD") != v51.git("rev-parse", "origin/main"):
        raise RuntimeError("Public V52 case push could not be verified")
    print(MARKER)
    print("V52_PUBLIC_CASES: 32")
    print("V52_PUBLIC_PENDING: 32")
    print("V52_TRAIN_APPROVED: 0")
    print("GIT_HEAD:", v51.git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, KeyError, ValueError, TypeError) as exc:
        print(MARKER)
        print("PUSH: NOT_CONFIRMED")
        print("ERROR:", str(exc))
        sys.exit(1)
