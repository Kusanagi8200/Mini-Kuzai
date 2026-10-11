#!/usr/bin/env python3
"""Numeric-only progress report from GitHub-editable public SmolTalk V48 pages.

The canonical source is the verified external public SmolTalk reservoir.
This audit does not inspect any private ChatGPT corpus or local human ledger.
"""

import importlib.util
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXPORTER = REPO / "tools/publish_smoltalk_v48_github_reviews.py"
if not EXPORTER.is_file():
    raise RuntimeError("Missing reviewed public-source exporter")
spec = importlib.util.spec_from_file_location("smoltalk_v48_github_exporter", EXPORTER)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
DIRECTORY = REPO / "reviews/smoltalk-v48/cases"
STATUS_RE = re.compile(r"(?m)^Review status: (PENDING|RETAIN|REJECT|HOLD)$")
RATIONALE_RE = re.compile(r"(?m)^Review rationale: ([^\r\n]*)$")


def main():
    if not DIRECTORY.is_dir():
        raise RuntimeError("Public V48 review pages have not been exported")
    cases = publisher.verified_cases()
    if len(cases) != 68:
        raise RuntimeError("Unexpected public source case count")
    expected_files = set()
    decisions = Counter()
    reasons = Counter()
    for index, (record, original) in enumerate(cases, 1):
        filename = "{:03d}-{}.md".format(index, record["source_content_sha256"][:16])
        expected_files.add(filename)
        file = DIRECTORY / filename
        if not file.is_file() or file.is_symlink():
            raise RuntimeError("Missing or unsafe GitHub review page")
        text = file.read_text(encoding="utf-8")
        states = STATUS_RE.findall(text)
        motivations = RATIONALE_RE.findall(text)
        if len(states) != 1 or len(motivations) != 1:
            raise RuntimeError("Review must contain exactly one status and rationale")
        status = states[0]
        reason = motivations[0].strip()
        if status == "PENDING":
            if reason != "NOT_REVIEWED":
                raise RuntimeError("Pending status must have no decision justification")
        elif not (12 <= len(reason) <= 2000) or reason == "NOT_REVIEWED":
            raise RuntimeError("Reviewed status requires a meaningful justification")
        # Detect unexpected changes to original public SmolTalk conversation text.
        normalized = STATUS_RE.sub("Review status: PENDING", text, count=1)
        normalized = RATIONALE_RE.sub("Review rationale: NOT_REVIEWED", normalized, count=1)
        canonical = publisher.page(index, record, original)
        if normalized != canonical:
            raise RuntimeError("Published review page was changed outside status/rationale")
        decisions[status] += 1
        if status != "PENDING":
            reasons[record["review_queue_reason"]] += 1
    if {p.name for p in DIRECTORY.iterdir()} != expected_files:
        raise RuntimeError("Unexpected file in public review directory")

    reviewed = 68 - decisions["PENDING"]
    metrics = {
        "TOTAL_CANDIDATS": 68,
        "V48_QUEUE_TOTAL": 68,
        "V48_REVIEWED": reviewed,
        "V48_UNREVIEWED": decisions["PENDING"],
        "V48_PRIORITY_REVIEWED": reasons["RELABEL"] + reasons["RESCUE"],
        "V48_BASELINE_REVIEWED": reasons["BASE"],
        "V48_RETAINED": decisions["RETAIN"],
        "V48_REJECTED": decisions["REJECT"],
        "V48_HELD": decisions["HOLD"],
        "V48_TRAIN_APPROVED": 0,
    }
    if (reviewed != metrics["V48_RETAINED"] + metrics["V48_REJECTED"]
        + metrics["V48_HELD"]):
        raise RuntimeError("Invalid public review status counts")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, val in sorted(metrics.items()):
        print("{}: {}".format(key, val))


if __name__ == "__main__":
    main()
