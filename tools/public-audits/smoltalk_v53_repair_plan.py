#!/usr/bin/env python3
"""V53 Gate 3 read-only repair-plan audit for public SmolTalk cases.

Confirms that the eight documented B repair-priority cases still reconstruct
from the verified public source, remain Gate 2 repair-priority cases, and match
the documented overlapping repair flags. Emits numeric-only aggregates.

No source case is edited and no derivative training record is created.
"""

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"

GATE2_AUDIT = REPO / "tools/public-audits/smoltalk_v53_behavior_shortlist.py"
GATE2_REPORT = REPO / (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V53-BEHAVIOR-SHORTLIST-001.json"
)

# Public source content SHA-256 -> overlapping repair flags.
REPAIR_CASES = {
    "ca3e77d780443438d12cc387bc0a447135e835df393349f781c04cd3a6630e64": {
        "segment", "fact",
    },
    "688b9094130c5df25612772ff107e3d3b1ef13e6fe5f6341dfcd5f3d5adf143b": {
        "calibrate",
    },
    "566e0b8c4ed792cc76ad0646a6295b05adab7a8caf37e8b91483982fb80e00c3": {
        "wording",
    },
    "2ab4c403ee2c94b1eb6dc9c91b33f97b4fca1a7d757dd4f772bd53b3d52f47dd": {
        "segment", "wording",
    },
    "926e7e38b7dc57447fbe49df5ae13ed4f1a04811c841a53dea61b01563039101": {
        "segment", "fact", "wording",
    },
    "6053fdebd4dd0f617020671ba725ecb2732b790589122f01019096d93e6fd569": {
        "fact", "calibrate",
    },
    "8d1fa4491e9b2ca5a69c03a336cf93c14a8f22144c548fa76f332b7d10b80329": {
        "calibrate",
    },
    "4bd411ceb95b9b3c9cafe265405a9522445712ae330fa4af1fc74d76a088cd04": {
        "fact",
    },
}

EXPECTED_KEYS = {
    "V53_G3_REPAIR_TOTAL",
    "V53_G3_SOURCE_MATCHED",
    "V53_G3_GATE2_PRIORITY_CONFIRMED",
    "V53_G3_SEGMENTATION_REQUIRED",
    "V53_G3_FACTUAL_NUMERIC_FIX",
    "V53_G3_UNCERTAINTY_LOGIC_CALIBRATION",
    "V53_G3_WORDING_CONSTRAINT_CLEANUP",
    "V53_G3_TRAIN_APPROVED",
}


def load(path, name):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe V53 Gate 3 dependency")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load V53 Gate 3 dependency")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_gate2_history():
    if not GATE2_REPORT.is_file() or GATE2_REPORT.is_symlink():
        raise RuntimeError("Completed V53 Gate 2 history missing")
    report = json.loads(GATE2_REPORT.read_text(encoding="utf-8"))
    metrics = report.get("metrics", {})
    if (
        report.get("step_id")
        != "PHASE03-SMOLTALK-V53-BEHAVIOR-SHORTLIST-001"
        or report.get("training_authorized") is not False
        or report.get("private_conversation_data_included") is not False
        or metrics.get("V53_G2_B_REPAIR_PRIORITY") != 8
        or metrics.get("V53_G2_TRAIN_APPROVED") != 0
    ):
        raise RuntimeError("V53 Gate 2 history does not match Gate 3 prerequisite")


def gate2_rows(gate2):
    v51 = gate2.load(gate2.V51_PUBLISHER, "v53_g3_v51_publisher")
    v51_progress = gate2.load(gate2.V51_PROGRESS, "v53_g3_v51_progress")
    v52 = gate2.load(gate2.V52_PUBLISHER, "v53_g3_v52_publisher")
    v52_progress = gate2.load(gate2.V52_PROGRESS, "v53_g3_v52_progress")
    inventory = gate2.load(gate2.V52_INVENTORY, "v53_g3_v52_inventory")

    rows = []
    for source_id, grade, fields in gate2.parse_v51(v51, v51_progress):
        rows.append(("V51", source_id, grade, fields))
    for source_id, grade, fields in gate2.parse_v52(
        v52, v52_progress, v51, v51_progress, inventory
    ):
        rows.append(("V52", source_id, grade, fields))
    return rows


def is_gate2_repair_priority(cycle, grade, fields):
    if grade != "B":
        return False
    risk = fields[cycle + " factual risk"]
    if risk == "HIGH":
        return False
    signal = sum(
        int(fields[cycle + " " + name])
        for name in (
            "cognition", "creativity", "continuity",
            "correction", "communication"
        )
    )
    return signal >= 8


def repair_metrics(rows):
    if len(rows) != 56 or len({row[1] for row in rows}) != 56:
        raise RuntimeError("Unexpected V51/V52 Gate 3 source population")

    by_id = {source_id: (cycle, grade, fields)
             for cycle, source_id, grade, fields in rows}
    if len(by_id) != 56:
        raise RuntimeError("Duplicate V53 Gate 3 source identifier")

    expected_ids = set(REPAIR_CASES)
    if not expected_ids <= set(by_id):
        raise RuntimeError("Documented V53 Gate 3 source case missing")

    priority = 0
    for source_id in expected_ids:
        cycle, grade, fields = by_id[source_id]
        if not is_gate2_repair_priority(cycle, grade, fields):
            raise RuntimeError("V53 Gate 3 case no longer matches Gate 2 priority")
        priority += 1

    metrics = {
        "V53_G3_REPAIR_TOTAL": len(expected_ids),
        "V53_G3_SOURCE_MATCHED": len(expected_ids),
        "V53_G3_GATE2_PRIORITY_CONFIRMED": priority,
        "V53_G3_SEGMENTATION_REQUIRED": sum(
            "segment" in flags for flags in REPAIR_CASES.values()
        ),
        "V53_G3_FACTUAL_NUMERIC_FIX": sum(
            "fact" in flags for flags in REPAIR_CASES.values()
        ),
        "V53_G3_UNCERTAINTY_LOGIC_CALIBRATION": sum(
            "calibrate" in flags for flags in REPAIR_CASES.values()
        ),
        "V53_G3_WORDING_CONSTRAINT_CLEANUP": sum(
            "wording" in flags for flags in REPAIR_CASES.values()
        ),
        "V53_G3_TRAIN_APPROVED": 0,
    }
    if set(metrics) != EXPECTED_KEYS:
        raise RuntimeError("V53 Gate 3 metric key set changed")
    return dict(sorted(metrics.items()))


def require_expected_state(metrics):
    expected = {
        "V53_G3_REPAIR_TOTAL": 8,
        "V53_G3_SOURCE_MATCHED": 8,
        "V53_G3_GATE2_PRIORITY_CONFIRMED": 8,
        "V53_G3_SEGMENTATION_REQUIRED": 3,
        "V53_G3_FACTUAL_NUMERIC_FIX": 4,
        "V53_G3_UNCERTAINTY_LOGIC_CALIBRATION": 3,
        "V53_G3_WORDING_CONSTRAINT_CLEANUP": 3,
        "V53_G3_TRAIN_APPROVED": 0,
    }
    if metrics != dict(sorted(expected.items())):
        raise RuntimeError("V53 Gate 3 repair flags differ from documented plan")


def main():
    validate_gate2_history()
    gate2 = load(GATE2_AUDIT, "v53_g3_gate2")
    rows = gate2_rows(gate2)
    metrics = repair_metrics(rows)
    require_expected_state(metrics)

    print(MARKER)
    for name, value in metrics.items():
        print("{}: {}".format(name, value))


if __name__ == "__main__":
    main()
