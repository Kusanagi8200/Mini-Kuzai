#!/usr/bin/env python3
"""Numeric-only V51 GitHub review progress; PUBLIC external SmolTalk only.

Reconstructs every published case from the verified V50/V44/public pool,
rejects changes outside the nine V51 review fields, and prints only
allowlisted non-identifying aggregate counts. No private inputs.
"""
import importlib.util
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools/publish_smoltalk_v51_github_reviews.py"
DIR = REPO / "reviews/smoltalk-v51/cases"
if not SCRIPT.is_file() or SCRIPT.is_symlink():
    raise RuntimeError("V51 exporter not found")
spec = importlib.util.spec_from_file_location("public_v51_publisher", SCRIPT)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)

FIELDS = {
    "V51 grade": "PENDING",
    "V51 rationale": "NOT_REVIEWED",
    "V51 cognition": "UNREVIEWED",
    "V51 creativity": "UNREVIEWED",
    "V51 continuity": "UNREVIEWED",
    "V51 correction": "UNREVIEWED",
    "V51 communication": "UNREVIEWED",
    "V51 factual risk": "UNREVIEWED",
    "V51 instruction fit": "UNREVIEWED",
}


def extract_and_normalize(text):
    found = {}
    for name, initial in FIELDS.items():
        pattern = re.compile(r"(?m)^" + re.escape(name) + r": ([^\r\n]*)$")
        values = pattern.findall(text)
        if len(values) != 1:
            raise RuntimeError("Every V51 field must appear exactly once")
        found[name] = values[0]
        text = pattern.sub(name + ": " + initial, text, count=1)
    return found, text


def validate(fields):
    grade = fields["V51 grade"]
    if grade not in ("PENDING", "A", "B", "C", "HOLD"):
        raise RuntimeError("Invalid V51 grade")
    if grade == "PENDING":
        if any(fields[name] != default for name, default in FIELDS.items()):
            raise RuntimeError("Pending V51 case has partial assessment")
        return grade
    reason = fields["V51 rationale"].strip()
    if reason == "NOT_REVIEWED" or not 12 <= len(reason) <= 2000:
        raise RuntimeError("V51 review requires a substantive rationale")
    for field in (
        "V51 cognition", "V51 creativity", "V51 continuity",
        "V51 correction", "V51 communication"
    ):
        if fields[field] not in ("0", "1", "2", "3"):
            raise RuntimeError("V51 review must score each behavior axis")
    if fields["V51 factual risk"] not in ("LOW", "REVIEW", "HIGH"):
        raise RuntimeError("V51 factual-risk assessment missing")
    if fields["V51 instruction fit"] not in ("GOOD", "PARTIAL", "BAD"):
        raise RuntimeError("V51 instruction-fit assessment missing")
    return grade


def main():
    if not DIR.is_dir() or DIR.is_symlink():
        raise RuntimeError("V51 GitHub review pages not published yet")
    cases = publisher.select_batch(publisher.verified_candidates())
    if len(cases) != 24:
        raise RuntimeError("Unexpected public V51 batch size")
    expected, counts = set(), Counter()
    by_priority = Counter()
    for i, row in enumerate(cases, 1):
        filename = "{:03d}-{}.md".format(i, row["source_content_sha256"][:16])
        expected.add(filename)
        path = DIR / filename
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("Missing or unsafe V51 review page")
        actual = path.read_text(encoding="utf-8")
        fields, normalized = extract_and_normalize(actual)
        if normalized != publisher.case_page(i, row):
            raise RuntimeError("Original public dialogue or metadata modified")
        grade = validate(fields)
        counts[grade] += 1
        if grade != "PENDING":
            by_priority[row["priority_hint"]] += 1
    if set(p.name for p in DIR.iterdir()) != expected:
        raise RuntimeError("Unexpected file in public V51 case directory")
    n = 24 - counts["PENDING"]
    if n != sum(counts[x] for x in ("A", "B", "C", "HOLD")):
        raise RuntimeError("Invalid V51 totals")
    metrics = {
        "V51_QUEUE_TOTAL": 24,
        "V51_REVIEWED": n,
        "V51_UNREVIEWED": counts["PENDING"],
        "V51_HIGH_REVIEWED": by_priority["HIGH"],
        "V51_MEDIUM_REVIEWED": by_priority["MEDIUM"],
        "V51_LOW_REVIEWED": by_priority["LOW"],
        "V51_A": counts["A"],
        "V51_B": counts["B"],
        "V51_C": counts["C"],
        "V51_HELD": counts["HOLD"],
        "V51_TRAIN_APPROVED": 0,
    }
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print("{}: {}".format(key, value))


if __name__ == "__main__":
    main()
