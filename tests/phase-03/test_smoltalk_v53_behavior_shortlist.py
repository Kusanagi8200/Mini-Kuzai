"""Offline tests for V53 Gate 2 public behavioral shortlist routing."""

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
    REPO / "tools/public-audits/smoltalk_v53_behavior_shortlist.py",
    "v53_gate2_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_gate2_gogit_test")


def fields(prefix, scores, risk="LOW", fit="GOOD"):
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


def row(prefix, index, grade, scores, risk="LOW", fit="GOOD"):
    return (
        "{}-{:03d}".format(prefix, index),
        grade,
        fields(prefix, scores, risk=risk, fit=fit),
    )


class V53Gate2Tests(unittest.TestCase):
    def reviewed_rows(self):
        v51 = []
        v52 = []

        # 17 A total: 12 LOW risk, 5 REVIEW; 15 continuity>=2,
        # 7 creativity>=2 and 9 correction>=2.
        for i in range(17):
            risk = "LOW" if i < 12 else "REVIEW"
            scores = (
                2,
                2 if i < 7 else 0,
                2 if i < 15 else 1,
                2 if i < 9 else 0,
                3,
            )
            target = v51 if i < 9 else v52
            target.append(row("V51" if i < 9 else "V52", i, "A", scores, risk))

        # Eight repair-priority B rows, sum >= 8, non-HIGH risk.
        for i in range(8):
            target = v51 if i < 4 else v52
            target.append(row(
                "V51" if i < 4 else "V52", 100 + i, "B",
                (2, 1, 3, 0, 3), "REVIEW", "PARTIAL"
            ))

        # Six supporting B rows, sum 5-7.
        for i in range(6):
            target = v51 if i < 3 else v52
            target.append(row(
                "V51" if i < 3 else "V52", 200 + i, "B",
                (1, 1, 2, 0, 2), "LOW", "PARTIAL"
            ))

        # Three low-persona B rows, sum below 5.
        for i in range(3):
            v52.append(row(
                "V52", 300 + i, "B", (1, 0, 0, 0, 2), "LOW", "GOOD"
            ))

        # Three HIGH-risk B rows; high risk overrides signal strength.
        for i in range(3):
            v52.append(row(
                "V52", 400 + i, "B", (3, 3, 3, 3, 3), "HIGH", "PARTIAL"
            ))

        # 19 C rows for error analysis.
        for i in range(19):
            target = v51 if i < 7 else v52
            target.append(row(
                "V51" if i < 7 else "V52", 500 + i, "C",
                (1, 0, 0, 0, 1), "LOW", "GOOD"
            ))

        self.assertEqual(len(v51), 24)
        self.assertEqual(len(v52), 32)
        return v51, v52

    def test_expected_gate2_metrics(self):
        metrics = audit.route_metrics(*self.reviewed_rows())
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
        self.assertEqual(metrics, dict(sorted(expected.items())))

    def test_high_risk_b_never_enters_repair_priority(self):
        v51 = []
        v52 = [row("V52", 1, "B", (3, 3, 3, 3, 3), "HIGH", "GOOD")]
        # Fill remaining 55 as C to satisfy the fixed population guard.
        for i in range(24):
            v51.append(row("V51", i, "C", (1, 0, 0, 0, 1)))
        for i in range(31):
            v52.append(row("V52", 100 + i, "C", (1, 0, 0, 0, 1)))
        metrics = audit.route_metrics(v51, v52)
        self.assertEqual(metrics["V53_G2_B_HIGH_RISK"], 1)
        self.assertEqual(metrics["V53_G2_B_REPAIR_PRIORITY"], 0)

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.EXPECTED_KEYS), 15)
        self.assertTrue(audit.EXPECTED_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.EXPECTED_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.EXPECTED_KEYS)


if __name__ == "__main__":
    unittest.main()
