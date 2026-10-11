#!/usr/bin/env python3
"""Reconstruct public V52 review cases and emit numeric-only GOGIT metrics.

No dialogue, hashes, filenames, private inputs or qualitative rationales
are printed. The nine editable fields are the ONLY differences allowed
from immutable source-derived review pages.
"""
import importlib.util
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PUBLISHER = REPO / "tools/publish_smoltalk_v52_github_reviews.py"
V51_PUBLISHER = REPO / "tools/publish_smoltalk_v51_github_reviews.py"
V51_PROGRESS = REPO / "tools/public-audits/smoltalk_v51_github_progress.py"
V52_INVENTORY = REPO / "tools/public-audits/smoltalk_v52_inventory.py"
DEST = REPO / "reviews/smoltalk-v52"
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"


def load(path, name):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe public review module")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load public review module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_and_normalize(body, defaults):
    fields = {}
    for name, default in defaults.items():
        pattern = re.compile(r"(?m)^" + re.escape(name) + r": ([^\r\n]*)$")
        matches = pattern.findall(body)
        if len(matches) != 1:
            raise RuntimeError("V52 case requires exactly nine review fields")
        fields[name] = matches[0]
        body = pattern.sub(lambda _: name + ": " + default, body, count=1)
    return fields, body


def grade_review(fields, v51_progress):
    former = {
        name.replace("V52 ", "V51 ", 1): value
        for name, value in fields.items()
    }
    return v51_progress.validate(former)


def audit_metrics(selected, publisher, v51, v51_progress):
    folder = DEST / "cases"
    if (not folder.is_dir() or folder.is_symlink()
        or not (DEST / "README.md").is_file()):
        raise RuntimeError("V52 public review is not yet published")
    counts = Counter()
    expected = set()
    total_multiturn = 0
    index = (DEST / "README.md").read_text(encoding="utf-8")
    for number, row in enumerate(selected, 1):
        filename = publisher.page_name(number, row)
        expected.add(filename)
        file = folder / filename
        if not file.is_file() or file.is_symlink():
            raise RuntimeError("Missing V52 public review case")
        content = file.read_text(encoding="utf-8")
        fields, normalized = extract_and_normalize(
            content, publisher.RUBRIC_DEFAULTS
        )
        if normalized != publisher.case_page(number, row, v51):
            raise RuntimeError("V52 immutable public-source material modified")
        grade = grade_review(fields, v51_progress)
        counts[grade] += 1
        counts[("priority", row["priority_hint"])] += 1
        counts[("source", row["source_dataset"])] += 1
        total_multiturn += int(len(row["messages"]) > 2)
        if index.count("(cases/" + filename + ")") != 1:
            raise RuntimeError("V52 public case index mismatch")
    if {path.name for path in folder.iterdir()} != expected:
        raise RuntimeError("Unexpected V52 review file")
    if len(expected) != publisher.TOTAL:
        raise RuntimeError("V52 public batch size mismatch")
    graded = sum(counts[key] for key in ("A", "B", "C", "HOLD"))
    if graded + counts["PENDING"] != publisher.TOTAL:
        raise RuntimeError("Invalid V52 graded count")
    metrics = {
        "V52_PUBLIC_QUEUE_TOTAL": publisher.TOTAL,
        "V52_PUBLIC_PENDING": counts["PENDING"],
        "V52_PUBLIC_REVIEWED": graded,
        "V52_PUBLIC_A": counts["A"],
        "V52_PUBLIC_B": counts["B"],
        "V52_PUBLIC_C": counts["C"],
        "V52_PUBLIC_HELD": counts["HOLD"],
        "V52_PUBLIC_HIGH": counts[("priority", "HIGH")],
        "V52_PUBLIC_MEDIUM": counts[("priority", "MEDIUM")],
        "V52_PUBLIC_LOW": counts[("priority", "LOW")],
        "V52_PUBLIC_SMOL": counts[("source", "smol-magpie-ultra-short")],
        "V52_PUBLIC_HERMES": counts[("source", "openhermes-50k")],
        "V52_PUBLIC_OSS": counts[("source", "self-oss-instruct")],
        "V52_PUBLIC_REWRITE": counts[("source", "explore-instruct-rewrite")],
        "V52_PUBLIC_MULTITURN": total_multiturn,
        "V52_PUBLIC_TRAIN_APPROVED": 0,
    }
    if (
        len(metrics) != 16
        or sum(metrics["V52_PUBLIC_" + key]
               for key in ("HIGH", "MEDIUM", "LOW")) != publisher.TOTAL
        or sum(metrics["V52_PUBLIC_" + key]
               for key in ("SMOL", "HERMES", "OSS", "REWRITE")) != publisher.TOTAL
    ):
        raise RuntimeError("V52 numeric progress metrics inconsistent")
    return dict(sorted(metrics.items()))


def main():
    publisher = load(PUBLISHER, "v52_progress_publisher")
    v51 = load(V51_PUBLISHER, "v52_progress_v51_publisher")
    v51_progress = load(V51_PROGRESS, "v52_progress_v51_progress")
    inventory = load(V52_INVENTORY, "v52_progress_inventory")
    selected = publisher.select_batch(
        publisher.verified_v52_pool(v51, v51_progress, inventory)
    )
    metrics = audit_metrics(selected, publisher, v51, v51_progress)
    print(MARKER)
    for name, value in metrics.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
