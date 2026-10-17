"""Offline tests for the V53 public cross-cycle SmolTalk inventory."""

import importlib.util
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load(
    REPO / "tools/public-audits/smoltalk_v53_cross_cycle_inventory.py",
    "v53_cross_cycle_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_gogit_test")


def snapshot(ids, statuses=None, grades=None, in_v44=0):
    result = {
        "ids": list(ids),
        "in_v44": in_v44,
        "matched": len(ids),
    }
    if statuses is not None:
        result["statuses"] = Counter(statuses)
    if grades is not None:
        result["grades"] = Counter(grades)
    return result


class V53CrossCycleTests(unittest.TestCase):
    def expected_snapshots(self):
        v48_ids = ["v48-{:03d}".format(i) for i in range(68)]
        v51_ids = ["v51-{:03d}".format(i) for i in range(24)]
        v52_ids = ["v52-{:03d}".format(i) for i in range(32)]
        v48 = snapshot(
            v48_ids,
            statuses={"RETAIN": 24, "REJECT": 44, "HOLD": 0, "PENDING": 0},
            in_v44=44,
        )
        v51 = snapshot(
            v51_ids,
            grades={"A": 9, "B": 8, "C": 7, "HOLD": 0, "PENDING": 0},
            in_v44=24,
        )
        v52 = snapshot(
            v52_ids,
            grades={"A": 8, "B": 12, "C": 12, "HOLD": 0, "PENDING": 0},
            in_v44=32,
        )
        return v48, v51, v52

    def test_expected_cross_cycle_metrics(self):
        metrics = audit.consolidation_metrics(*self.expected_snapshots())
        self.assertEqual(metrics["V53_PUBLIC_TOTAL"], 124)
        self.assertEqual(metrics["V53_SOURCE_MATCHED"], 124)
        self.assertEqual(metrics["V53_DISTINCT_SOURCE_IDS"], 124)
        self.assertEqual(metrics["V53_DUPLICATE_SOURCE_IDS"], 0)
        self.assertEqual(metrics["V53_V44_REVIEWED"], 100)
        self.assertEqual(metrics["V53_OUTSIDE_V44_REVIEWED"], 24)
        self.assertEqual(metrics["V53_V51V52_A"], 17)
        self.assertEqual(metrics["V53_V51V52_B"], 20)
        self.assertEqual(metrics["V53_V51V52_C"], 19)
        self.assertEqual(metrics["V53_UNRESOLVED"], 0)
        self.assertEqual(metrics["V53_TRAIN_APPROVED"], 0)

    def test_duplicate_source_identifier_is_detected(self):
        v48, v51, v52 = self.expected_snapshots()
        v52["ids"][0] = v51["ids"][0]
        metrics = audit.consolidation_metrics(v48, v51, v52)
        self.assertEqual(metrics["V53_DISTINCT_SOURCE_IDS"], 123)
        self.assertEqual(metrics["V53_DUPLICATE_SOURCE_IDS"], 1)
        with self.assertRaises(RuntimeError):
            audit.require_expected_state(
                metrics,
                {
                    "V48_REVIEWED": 68,
                    "V48_RETAINED": 24,
                    "V48_REJECTED": 44,
                    "V48_HELD": 0,
                    "V48_TRAIN_APPROVED": 0,
                },
                {
                    "V51_REVIEWED": 24,
                    "V51_A": 9,
                    "V51_B": 8,
                    "V51_C": 7,
                    "V51_HELD": 0,
                    "V51_TRAIN_APPROVED": 0,
                },
                {
                    "V52_PUBLIC_REVIEWED": 32,
                    "V52_PUBLIC_A": 8,
                    "V52_PUBLIC_B": 12,
                    "V52_PUBLIC_C": 12,
                    "V52_PUBLIC_HELD": 0,
                    "V52_PUBLIC_TRAIN_APPROVED": 0,
                },
            )

    def test_history_agreement_accepts_expected_state(self):
        metrics = audit.consolidation_metrics(*self.expected_snapshots())
        audit.require_expected_state(
            metrics,
            {
                "V48_REVIEWED": 68,
                "V48_RETAINED": 24,
                "V48_REJECTED": 44,
                "V48_HELD": 0,
                "V48_TRAIN_APPROVED": 0,
            },
            {
                "V51_REVIEWED": 24,
                "V51_A": 9,
                "V51_B": 8,
                "V51_C": 7,
                "V51_HELD": 0,
                "V51_TRAIN_APPROVED": 0,
            },
            {
                "V52_PUBLIC_REVIEWED": 32,
                "V52_PUBLIC_A": 8,
                "V52_PUBLIC_B": 12,
                "V52_PUBLIC_C": 12,
                "V52_PUBLIC_HELD": 0,
                "V52_PUBLIC_TRAIN_APPROVED": 0,
            },
        )

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.EXPECTED_KEYS), 25)
        self.assertTrue(audit.EXPECTED_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.EXPECTED_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.EXPECTED_KEYS)
        self.assertEqual(len(parsed), 25)


if __name__ == "__main__":
    unittest.main()
