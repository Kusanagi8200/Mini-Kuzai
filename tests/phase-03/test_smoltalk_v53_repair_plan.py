"""Offline tests for V53 Gate 3 public repair-plan routing."""

import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load(
    REPO / "tools/public-audits/smoltalk_v53_repair_plan.py",
    "v53_gate3_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_gate3_gogit_test")


def fields(prefix, scores=(2, 1, 3, 0, 3), risk="REVIEW", fit="GOOD"):
    cognition, creativity, continuity, correction, communication = scores
    return {
        prefix + " cognition": str(cognition),
        prefix + " creativity": str(creativity),
        prefix + " continuity": str(continuity),
        prefix + " correction": str(correction),
        prefix + " communication": str(communication),
        prefix + " factual risk": risk,
        prefix + " instruction fit": fit,
    }


class V53Gate3Tests(unittest.TestCase):
    def rows(self):
        ids = list(audit.REPAIR_CASES)
        rows = []
        for i, source_id in enumerate(ids):
            cycle = "V51" if i < 4 else "V52"
            rows.append((cycle, source_id, "B", fields(cycle)))

        # Fill to the real 24 V51 / 32 V52 population with non-priority C cases.
        for i in range(20):
            rows.append((
                "V51", "v51-fill-{:03d}".format(i), "C",
                fields("V51", scores=(1, 0, 0, 0, 1), risk="LOW"),
            ))
        for i in range(28):
            rows.append((
                "V52", "v52-fill-{:03d}".format(i), "C",
                fields("V52", scores=(1, 0, 0, 0, 1), risk="LOW"),
            ))
        self.assertEqual(len(rows), 56)
        self.assertEqual(sum(row[0] == "V51" for row in rows), 24)
        self.assertEqual(sum(row[0] == "V52" for row in rows), 32)
        return rows

    def test_expected_gate3_metrics(self):
        metrics = audit.repair_metrics(self.rows())
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
        self.assertEqual(metrics, dict(sorted(expected.items())))

    def test_priority_change_fails_closed(self):
        rows = self.rows()
        cycle, source_id, _, case_fields = rows[0]
        rows[0] = (cycle, source_id, "C", case_fields)
        with self.assertRaises(RuntimeError):
            audit.repair_metrics(rows)

    def test_high_risk_priority_change_fails_closed(self):
        rows = self.rows()
        cycle, source_id, grade, case_fields = rows[0]
        changed = dict(case_fields)
        changed[cycle + " factual risk"] = "HIGH"
        rows[0] = (cycle, source_id, grade, changed)
        with self.assertRaises(RuntimeError):
            audit.repair_metrics(rows)

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.EXPECTED_KEYS), 8)
        self.assertTrue(audit.EXPECTED_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.EXPECTED_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.EXPECTED_KEYS)


if __name__ == "__main__":
    unittest.main()
