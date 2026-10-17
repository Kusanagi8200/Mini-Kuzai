"""Offline tests for V53 derivative-003 independent review audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_deriv003_review.py",
    "v53_deriv003_review_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_deriv003_review_gogit_test")


class V53Deriv003ReviewTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_D3_REVIEW_TOTAL": 1,
            "V53_D3_REVIEW_COMPLETE": 1,
            "V53_D3_QUALITY_PASS": 1,
            "V53_D3_FACTUAL_PASS": 1,
            "V53_D3_COHERENCE_PASS": 1,
            "V53_D3_CREATIVITY_PASS": 1,
            "V53_D3_INSTRUCTION_PASS": 1,
            "V53_D3_ELIGIBILITY_READY": 1,
            "V53_D3_FURTHER_REPAIR": 0,
            "V53_D3_NEW_ERRORS": 0,
            "V53_D3_TRAIN_APPROVED": 0,
            "V53_D3_SPLIT_ASSIGNED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

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
