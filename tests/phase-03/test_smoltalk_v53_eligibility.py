"""Offline tests for V53 corpus eligibility controls."""

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
    REPO / "tools/public-audits/smoltalk_v53_eligibility.py",
    "v53_eligibility_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_eligibility_gogit_test")


class V53EligibilityTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_ELIG_TOTAL": 2,
            "V53_ELIG_PROVENANCE_PASS": 2,
            "V53_ELIG_LICENSE_PASS": 2,
            "V53_ELIG_CANONICAL_TRAIN_RECORDS": 37,
            "V53_ELIG_EXACT_DUP_HITS": 0,
            "V53_ELIG_NEAR_DUP_HITS": 0,
            "V53_ELIG_RESERVED_VALIDATION_COLLISIONS": 1,
            "V53_ELIG_SEMANTIC_PASS": 1,
            "V53_ELIG_SEMANTIC_BLOCKED": 1,
            "V53_ELIG_ADMISSION_READY": 1,
            "V53_ELIG_TRAIN_APPROVED": 0,
            "V53_ELIG_SPLIT_ASSIGNED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_semantic_decision_population(self):
        self.assertEqual(len(audit.EXPECTED), 2)
        blocked = [
            row for row in audit.EXPECTED.values()
            if row["validation_collision"] or row["blind_collision"]
        ]
        ready = [
            row for row in audit.EXPECTED.values()
            if not row["validation_collision"] and not row["blind_collision"]
        ]
        self.assertEqual(len(blocked), 1)
        self.assertEqual(len(ready), 1)
        self.assertEqual(blocked[0]["validation_group"], "sg-b07-02")
        self.assertEqual(ready[0]["train_group"], "sg-b08-01")

    def test_near_duplicate_threshold(self):
        self.assertEqual(audit.NEAR_DUP_THRESHOLD, 0.20)
        self.assertLess(audit.jaccard({"a"}, {"b"}), audit.NEAR_DUP_THRESHOLD)
        self.assertGreaterEqual(
            audit.jaccard({"a", "b"}, {"a", "b"}),
            audit.NEAR_DUP_THRESHOLD,
        )

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.METRIC_KEYS), 12)
        self.assertTrue(audit.METRIC_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.METRIC_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.METRIC_KEYS)


if __name__ == "__main__":
    unittest.main()
