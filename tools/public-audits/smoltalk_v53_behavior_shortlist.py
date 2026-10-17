#!/usr/bin/env python3
"""V53 Gate 2 read-only behavioral shortlist audit for public SmolTalk.

Reconstructs all V51 and V52 public review pages from their verified source,
validates their nine review fields, checks agreement with the completed V53
cross-cycle inventory, and emits numeric-only routing metrics.

The routing is a review-order aid, not semantic validation or TRAIN approval.
"""

import importlib.util
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

V51_PUBLISHER = REPO / "tools/publish_smoltalk_v51_github_reviews.py"
V51_PROGRESS = REPO / "tools/public-audits/smoltalk_v51_github_progress.py"
V52_PUBLISHER = REPO / "tools/publish_smoltalk_v52_github_reviews.py"
V52_PROGRESS = REPO / "tools/public-audits/smoltalk_v52_github_progress.py"
V52_INVENTORY = REPO / "tools/public-audits/smoltalk_v52_inventory.py"

V51_DIR = REPO / "reviews/smoltalk-v51/cases"
V52_DIR = REPO / "reviews/smoltalk-v52/cases"
GATE1 = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-CROSS-CYCLE-INVENTORY-001.json"
)

EXPECTED_KEYS = {
    "V53_G2_REVIEWED_TOTAL",
    "V53_G2_A_TOTAL",
    "V53_G2_A_LOW_RISK",
    "V53_G2_A_REVIEW_RISK",
    "V53_G2_A_STRONG_CONTINUITY",
    "V53_G2_A_STRONG_CREATIVITY",
    "V53_G2_A_STRONG_CORRECTION",
    "V53_G2_B_TOTAL",
    "V53_G2_B_REPAIR_PRIORITY",
    "V53_G2_B_SUPPORTING",
    "V53_G2_B_LOW_PERSONA",
    "V53_G2_B_HIGH_RISK",
    "V53_G2_C_ERROR_ANALYSIS",
    "V53_G2_UNRESOLVED",
    "V53_G2_TRAIN_APPROVED",
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


def axis(fields, prefix, name):
    value = fields[prefix + " " + name]
    if value not in ("0", "1", "2", "3"):
        raise RuntimeError("Invalid V53 Gate 2 behavior score")
    return int(value)


def parse_v51(publisher, progress):
    if not V51_DIR.is_dir() or V51_DIR.is_symlink():
        raise RuntimeError("V51 public review directory missing")
    cases = publisher.select_batch(publisher.verified_candidates())
    if len(cases) != 24:
        raise RuntimeError("Unexpected V51 batch size")
    rows = []
    expected = set()
    for index, record in enumerate(cases, 1):
        filename = "{:03d}-{}.md".format(
            index, record["source_content_sha256"][:16]
        )
        expected.add(filename)
        page = V51_DIR / filename
        if not page.is_file() or page.is_symlink():
            raise RuntimeError("Missing or unsafe V51 case")
        text = page.read_text(encoding="utf-8")
        fields, normalized = progress.extract_and_normalize(text)
        if normalized != publisher.case_page(index, record):
            raise RuntimeError("V51 public-source material modified")
        grade = progress.validate(fields)
        rows.append((record["source_content_sha256"], grade, fields))
    if {p.name for p in V51_DIR.iterdir()} != expected:
        raise RuntimeError("Unexpected V51 case file")
    return rows


def parse_v52(publisher, progress, v51, v51_progress, inventory):
    if not V52_DIR.is_dir() or V52_DIR.is_symlink():
        raise RuntimeError("V52 public review directory missing")
    selected = publisher.select_batch(
        publisher.verified_v52_pool(v51, v51_progress, inventory)
    )
    if len(selected) != 32:
        raise RuntimeError("Unexpected V52 batch size")
    rows = []
    expected = set()
    for index, record in enumerate(selected, 1):
        filename = publisher.page_name(index, record)
        expected.add(filename)
        page = V52_DIR / filename
        if not page.is_file() or page.is_symlink():
            raise RuntimeError("Missing or unsafe V52 case")
        text = page.read_text(encoding="utf-8")
        fields, normalized = progress.extract_and_normalize(
            text, publisher.RUBRIC_DEFAULTS
        )
        if normalized != publisher.case_page(index, record, v51):
            raise RuntimeError("V52 public-source material modified")
        grade = progress.grade_review(fields, v51_progress)
        rows.append((record["source_content_sha256"], grade, fields))
    if {p.name for p in V52_DIR.iterdir()} != expected:
        raise RuntimeError("Unexpected V52 case file")
    return rows


def route_metrics(v51_rows, v52_rows):
    rows = []
    for source_id, grade, fields in v51_rows:
        rows.append(("V51", source_id, grade, fields))
    for source_id, grade, fields in v52_rows:
        rows.append(("V52", source_id, grade, fields))

    if len(rows) != 56 or len({row[1] for row in rows}) != 56:
        raise RuntimeError("V53 Gate 2 source population mismatch")

    counts = Counter()
    b_routes = Counter()

    for cycle, _, grade, fields in rows:
        prefix = cycle
        if grade not in ("A", "B", "C", "HOLD", "PENDING"):
            raise RuntimeError("Unexpected V53 Gate 2 grade")
        counts[grade] += 1

        risk = fields[prefix + " factual risk"]
        fit = fields[prefix + " instruction fit"]
        if risk not in ("LOW", "REVIEW", "HIGH"):
            raise RuntimeError("Invalid V53 Gate 2 factual-risk field")
        if fit not in ("GOOD", "PARTIAL", "BAD"):
            raise RuntimeError("Invalid V53 Gate 2 instruction-fit field")

        scores = {
            name: axis(fields, prefix, name)
            for name in (
                "cognition", "creativity", "continuity",
                "correction", "communication"
            )
        }

        if grade == "A":
            if risk == "LOW":
                counts["A_LOW_RISK"] += 1
            elif risk == "REVIEW":
                counts["A_REVIEW_RISK"] += 1
            else:
                counts["A_HIGH_RISK"] += 1
            counts["A_STRONG_CONTINUITY"] += int(scores["continuity"] >= 2)
            counts["A_STRONG_CREATIVITY"] += int(scores["creativity"] >= 2)
            counts["A_STRONG_CORRECTION"] += int(scores["correction"] >= 2)

        elif grade == "B":
            signal = sum(scores.values())
            if risk == "HIGH":
                b_routes["HIGH_RISK"] += 1
            elif signal >= 8:
                b_routes["REPAIR_PRIORITY"] += 1
            elif signal >= 5:
                b_routes["SUPPORTING"] += 1
            else:
                b_routes["LOW_PERSONA"] += 1

    unresolved = counts["HOLD"] + counts["PENDING"]
    metrics = {
        "V53_G2_REVIEWED_TOTAL": len(rows) - unresolved,
        "V53_G2_A_TOTAL": counts["A"],
        "V53_G2_A_LOW_RISK": counts["A_LOW_RISK"],
        "V53_G2_A_REVIEW_RISK": counts["A_REVIEW_RISK"],
        "V53_G2_A_STRONG_CONTINUITY": counts["A_STRONG_CONTINUITY"],
        "V53_G2_A_STRONG_CREATIVITY": counts["A_STRONG_CREATIVITY"],
        "V53_G2_A_STRONG_CORRECTION": counts["A_STRONG_CORRECTION"],
        "V53_G2_B_TOTAL": counts["B"],
        "V53_G2_B_REPAIR_PRIORITY": b_routes["REPAIR_PRIORITY"],
        "V53_G2_B_SUPPORTING": b_routes["SUPPORTING"],
        "V53_G2_B_LOW_PERSONA": b_routes["LOW_PERSONA"],
        "V53_G2_B_HIGH_RISK": b_routes["HIGH_RISK"],
        "V53_G2_C_ERROR_ANALYSIS": counts["C"],
        "V53_G2_UNRESOLVED": unresolved,
        "V53_G2_TRAIN_APPROVED": 0,
    }
    if set(metrics) != EXPECTED_KEYS:
        raise RuntimeError("V53 Gate 2 metric key set changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_G2_REVIEWED_TOTAL": 56,
        "V53_G2_A_TOTAL": 17,
        "V53_G2_A_LOW_RISK": 12,
        "V53_G2_A_REVIEW_RISK": 5,
        "V53_G2_A_STRONG_CONTINUITY": 15,
        "V53_G2_A_STRONG_CREATIVITY": 7,
        "V53_G2_A_STRONG_CORRECTION": 9,
        "V53_G2_B_TOTAL": 20,
        "V53_G2_B_REPAIR_PRIORITY": 8,
        "V53_G2_B_SUPPORTING": 6,
        "V53_G2_B_LOW_PERSONA": 3,
        "V53_G2_B_HIGH_RISK": 3,
        "V53_G2_C_ERROR_ANALYSIS": 19,
        "V53_G2_UNRESOLVED": 0,
        "V53_G2_TRAIN_APPROVED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("V53 Gate 2 routing differs from reviewed shortlist")

    if not GATE1.is_file() or GATE1.is_symlink():
        raise RuntimeError("V53 Gate 1 history missing")
    gate1 = json.loads(GATE1.read_text(encoding="utf-8"))
    gm = gate1.get("metrics", {})
    if (
        gate1.get("step_id")
        != "PHASE03-SMOLTALK-V53-CROSS-CYCLE-INVENTORY-001"
        or gate1.get("training_authorized") is not False
        or gate1.get("private_conversation_data_included") is not False
        or gm.get("V53_V51V52_A") != metrics["V53_G2_A_TOTAL"]
        or gm.get("V53_V51V52_B") != metrics["V53_G2_B_TOTAL"]
        or gm.get("V53_V51V52_C") != metrics["V53_G2_C_ERROR_ANALYSIS"]
        or gm.get("V53_UNRESOLVED") != metrics["V53_G2_UNRESOLVED"]
    ):
        raise RuntimeError("V53 Gate 2 no longer agrees with Gate 1 history")


def main():
    v51 = load(V51_PUBLISHER, "v53_g2_v51_publisher")
    v51_progress = load(V51_PROGRESS, "v53_g2_v51_progress")
    v52 = load(V52_PUBLISHER, "v53_g2_v52_publisher")
    v52_progress = load(V52_PROGRESS, "v53_g2_v52_progress")
    inventory = load(V52_INVENTORY, "v53_g2_v52_inventory")

    v51_rows = parse_v51(v51, v51_progress)
    v52_rows = parse_v52(v52, v52_progress, v51, v51_progress, inventory)
    metrics = route_metrics(v51_rows, v52_rows)
    require_expected_state(metrics)

    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
