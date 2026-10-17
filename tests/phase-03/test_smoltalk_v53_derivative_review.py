"""Offline tests for V53 independent derivative review audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_derivative_review.py",
    "v53_derivative_review_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_derivative_review_gogit_test")


class V53DerivativeReviewTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_DERIV_REVIEW_TOTAL": 2,
            "V53_DERIV_REVIEW_COMPLETE": 2,
            "V53_DERIV_REVIEW_QUALITY_PASS": 2,
            "V53_DERIV_REVIEW_FACTUAL_PASS": 2,
            "V53_DERIV_REVIEW_COHERENCE_PASS": 2,
            "V53_DERIV_REVIEW_BEHAVIOR_PASS": 2,
            "V53_DERIV_REVIEW_INSTRUCTION_PASS": 2,
            "V53_DERIV_REVIEW_ELIGIBILITY_READY": 2,
            "V53_DERIV_REVIEW_FURTHER_REPAIR": 0,
            "V53_DERIV_REVIEW_NEW_ERRORS": 0,
            "V53_DERIV_REVIEW_TRAIN_APPROVED": 0,
            "V53_DERIV_REVIEW_SPLIT_ASSIGNED": 0,
            "V53_DERIV_REVIEW_SEMANTIC_VALIDATED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_expected_review_population(self):
        self.assertEqual(len(audit.EXPECTED), 2)
        self.assertEqual(
            {row["derivative_id"] for row in audit.EXPECTED.values()},
            {"V53-DERIV-001-V52-025", "V53-DERIV-002-V51-013"},
        )

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.METRIC_KEYS), 13)
        self.assertTrue(audit.METRIC_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.METRIC_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.METRIC_KEYS)


if __name__ == "__main__":
    unittest.main()
