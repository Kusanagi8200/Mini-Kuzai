"""Offline tests for first V53 repaired derivative candidates."""

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
    REPO / "tools/public-audits/smoltalk_v53_derivative_candidates.py",
    "v53_derivative_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_derivative_gogit_test")


class V53DerivativeTests(unittest.TestCase):
    def test_expected_metrics_shape(self):
        expected = {
            "V53_DERIVATIVE_TOTAL": 2,
            "V53_DERIVATIVE_SOURCE_MATCHED": 2,
            "V53_DERIVATIVE_USER_SOURCE_TURNS": 6,
            "V53_DERIVATIVE_ASSISTANT_REWRITES": 6,
            "V53_DERIVATIVE_REVIEW_PENDING": 2,
            "V53_DERIVATIVE_TRAIN_APPROVED": 0,
            "V53_DERIVATIVE_SPLIT_ASSIGNED": 0,
            "V53_DERIVATIVE_SEMANTIC_VALIDATED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_known_source_population(self):
        self.assertEqual(len(audit.EXPECTED), 2)
        self.assertEqual(
            {row["cycle"] for row in audit.EXPECTED.values()},
            {"V51", "V52"},
        )
        self.assertEqual(
            len({row["source_sha"] for row in audit.EXPECTED.values()}), 2
        )

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.METRIC_KEYS), 8)
        self.assertTrue(audit.METRIC_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.METRIC_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.METRIC_KEYS)


if __name__ == "__main__":
    unittest.main()
