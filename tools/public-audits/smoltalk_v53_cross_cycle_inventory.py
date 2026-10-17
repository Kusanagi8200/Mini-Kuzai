#!/usr/bin/env python3
"""V53 read-only cross-cycle inventory for public SmolTalk review cases.

Revalidates the published V48/V49, V51 and V52 public case pages against
their deterministic public-source reconstruction, checks cross-cycle source
identifier distinctness, compares current dispositions with immutable GOGIT
history, and emits numeric-only aggregate metrics.

No private source is read and no case page is modified.
"""

import importlib.util
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

V48_PUBLISHER = REPO / "tools/publish_smoltalk_v48_github_reviews.py"
V48_PROGRESS = REPO / "tools/public-audits/smoltalk_v48_github_progress.py"
V51_PUBLISHER = REPO / "tools/publish_smoltalk_v51_github_reviews.py"
V51_PROGRESS = REPO / "tools/public-audits/smoltalk_v51_github_progress.py"
V52_PUBLISHER = REPO / "tools/publish_smoltalk_v52_github_reviews.py"
V52_PROGRESS = REPO / "tools/public-audits/smoltalk_v52_github_progress.py"
V52_INVENTORY = REPO / "tools/public-audits/smoltalk_v52_inventory.py"

V48_DIR = REPO / "reviews/smoltalk-v48"
V51_DIR = REPO / "reviews/smoltalk-v51"
V52_DIR = REPO / "reviews/smoltalk-v52"

V49_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V49-HOLD-RESOLVED-001.json"
)
V51_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V51-PILOT-REVIEW-001.json"
)
V52_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V52-REVIEW-FINAL-001.json"
)

EXPECTED_KEYS = {
    "V53_PUBLIC_TOTAL",
    "V53_SOURCE_MATCHED",
    "V53_DISTINCT_SOURCE_IDS",
    "V53_DUPLICATE_SOURCE_IDS",
    "V53_V44_REVIEWED",
    "V53_OUTSIDE_V44_REVIEWED",
    "V53_V48_TOTAL",
    "V53_V48_RETAINED",
    "V53_V48_REJECTED",
    "V53_V48_HELD",
    "V53_V51_TOTAL",
    "V53_V51_A",
    "V53_V51_B",
    "V53_V51_C",
    "V53_V51_HELD",
    "V53_V52_TOTAL",
    "V53_V52_A",
    "V53_V52_B",
    "V53_V52_C",
    "V53_V52_HELD",
    "V53_V51V52_A",
    "V53_V51V52_B",
    "V53_V51V52_C",
    "V53_UNRESOLVED",
    "V53_TRAIN_APPROVED",
}


def load(path, name):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe public review module")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load public review module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_history(path, step_id, producer):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required immutable GOGIT history is missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    if (
        data.get("step_id") != step_id
        or data.get("producer") != producer
        or data.get("training_authorized") is not False
        or data.get("private_conversation_data_included") is not False
        or not isinstance(data.get("metrics"), dict)
    ):
        raise RuntimeError("Historical GOGIT report integrity check failed")
    return data["metrics"]


def require_case_index(root, filenames):
    index_path = root / "README.md"
    if not index_path.is_file() or index_path.is_symlink():
        raise RuntimeError("Public review index missing")
    index = index_path.read_text(encoding="utf-8")
    for filename in filenames:
        if index.count("(cases/" + filename + ")") != 1:
            raise RuntimeError("Public review index mismatch")


def validate_v48(publisher, progress):
    folder = V48_DIR / "cases"
    if not folder.is_dir() or folder.is_symlink():
        raise RuntimeError("V48 public review directory missing")
    cases = publisher.verified_cases()
    if len(cases) != 68:
        raise RuntimeError("Unexpected V48 public case count")

    expected = set()
    ids = []
    statuses = Counter()
    in_v44 = 0

    for index, (record, original) in enumerate(cases, 1):
        filename = "{:03d}-{}.md".format(
            index, record["source_content_sha256"][:16]
        )
        expected.add(filename)
        page = folder / filename
        if not page.is_file() or page.is_symlink():
            raise RuntimeError("Missing or unsafe V48 public review page")
        text = page.read_text(encoding="utf-8")
        states = progress.STATUS_RE.findall(text)
        rationales = progress.RATIONALE_RE.findall(text)
        if len(states) != 1 or len(rationales) != 1:
            raise RuntimeError("V48 page review fields are malformed")
        status = states[0]
        rationale = rationales[0].strip()
        if status == "PENDING":
            if rationale != "NOT_REVIEWED":
                raise RuntimeError("Pending V48 case has a rationale")
        elif rationale == "NOT_REVIEWED" or not 12 <= len(rationale) <= 2000:
            raise RuntimeError("Reviewed V48 case lacks a valid rationale")

        normalized = progress.STATUS_RE.sub(
            "Review status: PENDING", text, count=1
        )
        normalized = progress.RATIONALE_RE.sub(
            "Review rationale: NOT_REVIEWED", normalized, count=1
        )
        if normalized != publisher.page(index, record, original):
            raise RuntimeError("V48 public-source page was modified")

        source_id = record["source_content_sha256"]
        ids.append(source_id)
        statuses[status] += 1
        in_v44 += int(record.get("v44_selected") is True)

    if {p.name for p in folder.iterdir()} != expected:
        raise RuntimeError("Unexpected file in V48 public case directory")
    require_case_index(V48_DIR, expected)
    return {
        "ids": ids,
        "statuses": statuses,
        "in_v44": in_v44,
        "matched": len(ids),
    }


def validate_v51(publisher, progress):
    folder = V51_DIR / "cases"
    if not folder.is_dir() or folder.is_symlink():
        raise RuntimeError("V51 public review directory missing")
    cases = publisher.select_batch(publisher.verified_candidates())
    if len(cases) != 24:
        raise RuntimeError("Unexpected V51 public case count")

    expected = set()
    ids = []
    grades = Counter()

    for index, record in enumerate(cases, 1):
        filename = "{:03d}-{}.md".format(
            index, record["source_content_sha256"][:16]
        )
        expected.add(filename)
        page = folder / filename
        if not page.is_file() or page.is_symlink():
            raise RuntimeError("Missing or unsafe V51 public review page")
        text = page.read_text(encoding="utf-8")
        fields, normalized = progress.extract_and_normalize(text)
        if normalized != publisher.case_page(index, record):
            raise RuntimeError("V51 public-source page was modified")
        grade = progress.validate(fields)
        ids.append(record["source_content_sha256"])
        grades[grade] += 1

    if {p.name for p in folder.iterdir()} != expected:
        raise RuntimeError("Unexpected file in V51 public case directory")
    require_case_index(V51_DIR, expected)
    return {
        "ids": ids,
        "grades": grades,
        "in_v44": len(ids),
        "matched": len(ids),
    }


def validate_v52(publisher, progress, v51, v51_progress, inventory):
    folder = V52_DIR / "cases"
    if not folder.is_dir() or folder.is_symlink():
        raise RuntimeError("V52 public review directory missing")
    selected = publisher.select_batch(
        publisher.verified_v52_pool(v51, v51_progress, inventory)
    )
    if len(selected) != publisher.TOTAL:
        raise RuntimeError("Unexpected V52 public case count")

    expected = set()
    ids = []
    grades = Counter()

    for index, record in enumerate(selected, 1):
        filename = publisher.page_name(index, record)
        expected.add(filename)
        page = folder / filename
        if not page.is_file() or page.is_symlink():
            raise RuntimeError("Missing or unsafe V52 public review page")
        text = page.read_text(encoding="utf-8")
        fields, normalized = progress.extract_and_normalize(
            text, publisher.RUBRIC_DEFAULTS
        )
        if normalized != publisher.case_page(index, record, v51):
            raise RuntimeError("V52 public-source page was modified")
        grade = progress.grade_review(fields, v51_progress)
        ids.append(record["source_content_sha256"])
        grades[grade] += 1

    if {p.name for p in folder.iterdir()} != expected:
        raise RuntimeError("Unexpected file in V52 public case directory")
    require_case_index(V52_DIR, expected)
    return {
        "ids": ids,
        "grades": grades,
        "in_v44": len(ids),
        "matched": len(ids),
    }


def consolidation_metrics(v48, v51, v52):
    all_ids = v48["ids"] + v51["ids"] + v52["ids"]
    distinct = len(set(all_ids))
    total = len(all_ids)

    v48_status = v48["statuses"]
    v51_grade = v51["grades"]
    v52_grade = v52["grades"]

    unresolved = (
        v48_status["PENDING"]
        + v48_status["HOLD"]
        + v51_grade["PENDING"]
        + v51_grade["HOLD"]
        + v52_grade["PENDING"]
        + v52_grade["HOLD"]
    )

    metrics = {
        "V53_PUBLIC_TOTAL": total,
        "V53_SOURCE_MATCHED": (
            v48["matched"] + v51["matched"] + v52["matched"]
        ),
        "V53_DISTINCT_SOURCE_IDS": distinct,
        "V53_DUPLICATE_SOURCE_IDS": total - distinct,
        "V53_V44_REVIEWED": v48["in_v44"] + v51["in_v44"] + v52["in_v44"],
        "V53_OUTSIDE_V44_REVIEWED": total - (
            v48["in_v44"] + v51["in_v44"] + v52["in_v44"]
        ),
        "V53_V48_TOTAL": len(v48["ids"]),
        "V53_V48_RETAINED": v48_status["RETAIN"],
        "V53_V48_REJECTED": v48_status["REJECT"],
        "V53_V48_HELD": v48_status["HOLD"],
        "V53_V51_TOTAL": len(v51["ids"]),
        "V53_V51_A": v51_grade["A"],
        "V53_V51_B": v51_grade["B"],
        "V53_V51_C": v51_grade["C"],
        "V53_V51_HELD": v51_grade["HOLD"],
        "V53_V52_TOTAL": len(v52["ids"]),
        "V53_V52_A": v52_grade["A"],
        "V53_V52_B": v52_grade["B"],
        "V53_V52_C": v52_grade["C"],
        "V53_V52_HELD": v52_grade["HOLD"],
        "V53_V51V52_A": v51_grade["A"] + v52_grade["A"],
        "V53_V51V52_B": v51_grade["B"] + v52_grade["B"],
        "V53_V51V52_C": v51_grade["C"] + v52_grade["C"],
        "V53_UNRESOLVED": unresolved,
        "V53_TRAIN_APPROVED": 0,
    }
    if set(metrics) != EXPECTED_KEYS:
        raise RuntimeError("V53 metric key set changed unexpectedly")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics, v49_history, v51_history, v52_history):
    expected = {
        "V53_PUBLIC_TOTAL": 124,
        "V53_SOURCE_MATCHED": 124,
        "V53_DISTINCT_SOURCE_IDS": 124,
        "V53_DUPLICATE_SOURCE_IDS": 0,
        "V53_V44_REVIEWED": 100,
        "V53_OUTSIDE_V44_REVIEWED": 24,
        "V53_V48_TOTAL": 68,
        "V53_V48_RETAINED": 24,
        "V53_V48_REJECTED": 44,
        "V53_V48_HELD": 0,
        "V53_V51_TOTAL": 24,
        "V53_V51_A": 9,
        "V53_V51_B": 8,
        "V53_V51_C": 7,
        "V53_V51_HELD": 0,
        "V53_V52_TOTAL": 32,
        "V53_V52_A": 8,
        "V53_V52_B": 12,
        "V53_V52_C": 12,
        "V53_V52_HELD": 0,
        "V53_V51V52_A": 17,
        "V53_V51V52_B": 20,
        "V53_V51V52_C": 19,
        "V53_UNRESOLVED": 0,
        "V53_TRAIN_APPROVED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("V53 cross-cycle inventory differs from expected state")

    if (
        v49_history.get("V48_REVIEWED") != metrics["V53_V48_TOTAL"]
        or v49_history.get("V48_RETAINED") != metrics["V53_V48_RETAINED"]
        or v49_history.get("V48_REJECTED") != metrics["V53_V48_REJECTED"]
        or v49_history.get("V48_HELD") != metrics["V53_V48_HELD"]
        or v49_history.get("V48_TRAIN_APPROVED") != 0
    ):
        raise RuntimeError("V48/V49 current state differs from immutable history")

    if (
        v51_history.get("V51_REVIEWED") != metrics["V53_V51_TOTAL"]
        or v51_history.get("V51_A") != metrics["V53_V51_A"]
        or v51_history.get("V51_B") != metrics["V53_V51_B"]
        or v51_history.get("V51_C") != metrics["V53_V51_C"]
        or v51_history.get("V51_HELD") != metrics["V53_V51_HELD"]
        or v51_history.get("V51_TRAIN_APPROVED") != 0
    ):
        raise RuntimeError("V51 current state differs from immutable history")

    if (
        v52_history.get("V52_PUBLIC_REVIEWED") != metrics["V53_V52_TOTAL"]
        or v52_history.get("V52_PUBLIC_A") != metrics["V53_V52_A"]
        or v52_history.get("V52_PUBLIC_B") != metrics["V53_V52_B"]
        or v52_history.get("V52_PUBLIC_C") != metrics["V53_V52_C"]
        or v52_history.get("V52_PUBLIC_HELD") != metrics["V53_V52_HELD"]
        or v52_history.get("V52_PUBLIC_TRAIN_APPROVED") != 0
    ):
        raise RuntimeError("V52 current state differs from immutable history")


def main():
    v48_publisher = load(V48_PUBLISHER, "v53_v48_publisher")
    v48_progress = load(V48_PROGRESS, "v53_v48_progress")
    v51_publisher = load(V51_PUBLISHER, "v53_v51_publisher")
    v51_progress = load(V51_PROGRESS, "v53_v51_progress")
    v52_publisher = load(V52_PUBLISHER, "v53_v52_publisher")
    v52_progress = load(V52_PROGRESS, "v53_v52_progress")
    inventory = load(V52_INVENTORY, "v53_v52_inventory")

    v48 = validate_v48(v48_publisher, v48_progress)
    v51 = validate_v51(v51_publisher, v51_progress)
    v52 = validate_v52(
        v52_publisher, v52_progress, v51_publisher, v51_progress, inventory
    )
    metrics = consolidation_metrics(v48, v51, v52)

    v49_history = load_history(
        V49_REPORT,
        "PHASE03-SMOLTALK-V49-HOLD-RESOLVED-001",
        "tools/public-audits/smoltalk_v48_github_progress.py",
    )
    v51_history = load_history(
        V51_REPORT,
        "PHASE03-SMOLTALK-V51-PILOT-REVIEW-001",
        "tools/public-audits/smoltalk_v51_github_progress.py",
    )
    v52_history = load_history(
        V52_REPORT,
        "PHASE03-SMOLTALK-V52-REVIEW-FINAL-001",
        "tools/public-audits/smoltalk_v52_github_progress.py",
    )
    require_expected_state(metrics, v49_history, v51_history, v52_history)

    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
