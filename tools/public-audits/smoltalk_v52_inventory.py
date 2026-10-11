#!/usr/bin/env python3
"""V52 numeric-only inventory of unreviewed PUBLIC SmolTalk V44 candidates.

Uses verified V50/V44/public-source records and immutable V51 case checks.
No private files, prompts, identifiers, or raw dialogue are printed or
published. This audit does not select TRAIN, change splits, or train a model.
"""
import importlib.util
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PUBLISHER = REPO / "tools/publish_smoltalk_v51_github_reviews.py"
PROGRESS = REPO / "tools/public-audits/smoltalk_v51_github_progress.py"
V51_DIR = REPO / "reviews/smoltalk-v51/cases"
PRIORITIES = ("HIGH", "MEDIUM", "LOW")
SOURCES = {
    "SMOL": "smol-magpie-ultra-short",
    "HERMES": "openhermes-50k",
    "OSS": "self-oss-instruct",
    "REWRITE": "explore-instruct-rewrite",
}
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"


def load_module(path, name):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required audited public code is missing or unsafe")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load public audit module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validated_v51_sha(publisher, progress, available_after_v48):
    selected = publisher.select_batch(available_after_v48)
    expected_names = set()
    shas = set()
    for index, record in enumerate(selected, 1):
        sha = record["source_content_sha256"]
        filename = f"{index:03d}-{sha[:16]}.md"
        expected_names.add(filename)
        path = V51_DIR / filename
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("Expected public V51 review page is missing")
        fields, normalized = progress.extract_and_normalize(
            path.read_text(encoding="utf-8")
        )
        if normalized != publisher.case_page(index, record):
            raise RuntimeError("V51 immutable source or metadata mismatch")
        if progress.validate(fields) == "PENDING":
            raise RuntimeError("V51 case is not reviewed")
        if sha in shas:
            raise RuntimeError("Duplicate V51 source record")
        shas.add(sha)
    if not V51_DIR.is_dir() or V51_DIR.is_symlink():
        raise RuntimeError("Invalid V51 directory")
    if {p.name for p in V51_DIR.iterdir()} != expected_names:
        raise RuntimeError("Unexpected V51 file")
    if len(shas) != 24:
        raise RuntimeError("Unexpected V51 review size")
    return shas


def inventory_metrics(records, v48_excluded, v51_excluded, population=1139):
    if len(records) + v48_excluded + v51_excluded != population:
        raise RuntimeError("V52 inventory population mismatch")
    seen = set()
    counts = Counter()
    metrics = {
        "V52_QUEUE_TOTAL": population,
        "V52_V48_EXCLUDED": v48_excluded,
        "V52_V51_EXCLUDED": v51_excluded,
        "V52_AVAILABLE": len(records),
        "V52_MULTITURN": 0,
        "V52_TRAIN_APPROVED": 0,
    }
    for record in records:
        sha = record["source_content_sha256"]
        priority = record["priority_hint"]
        source = record["source_dataset"]
        messages = record["messages"]
        if sha in seen or priority not in PRIORITIES or source not in SOURCES.values():
            raise RuntimeError("Invalid or duplicate V52 candidate")
        if len(messages) not in (2, 4, 6):
            raise RuntimeError("Invalid V52 public dialogue length")
        seen.add(sha)
        counts[(priority, source, "TOTAL")] += 1
        if len(messages) > 2:
            counts[(priority, source, "MULTITURN")] += 1
            metrics["V52_MULTITURN"] += 1
    for priority in PRIORITIES:
        for alias, source in SOURCES.items():
            for kind in ("TOTAL", "MULTITURN"):
                metrics[f"V52_{priority}_{alias}_{kind}"] = counts[
                    (priority, source, kind)
                ]
    if len(metrics) != 30:
        raise RuntimeError("Unexpected numeric metric schema")
    return dict(sorted(metrics.items()))


def main():
    publisher = load_module(PUBLISHER, "v52_public_v51_publisher")
    progress = load_module(PROGRESS, "v52_public_v51_progress")
    # Full-source verification: 8,000 source records, 1,139 V44/V50
    # candidates, computed heuristic signals and all 68 V48 filenames.
    after_v48 = publisher.verified_candidates()
    excluded_v48 = 1139 - len(after_v48)
    if excluded_v48 != 68:
        raise RuntimeError("Expected V48 exclusions do not match V50 population")
    selected_v51 = validated_v51_sha(publisher, progress, after_v48)
    remaining = [
        row for row in after_v48
        if row["source_content_sha256"] not in selected_v51
    ]
    metrics = inventory_metrics(remaining, excluded_v48, len(selected_v51))
    print(MARKER)
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
