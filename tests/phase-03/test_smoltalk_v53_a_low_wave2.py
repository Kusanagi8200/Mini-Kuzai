"""Offline tests for V53 A-low wave2 public candidate audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_a_low_wave2.py",
    "v53_a_wave2_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_a_wave2_gogit_test")


class V53ALowWave2Tests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_AW2_INSPECTED": 3,
            "V53_AW2_SOURCE_MATCHED": 3,
            "V53_AW2_LOW_RISK_A": 3,
            "V53_AW2_DERIVATIVE_READY": 1,
            "V53_AW2_DEFER_NO_GROUP": 1,
            "V53_AW2_DEFER_RESERVED": 1,
            "V53_AW2_DERIVATIVE_CREATED": 1,
            "V53_AW2_B12_ROUTE_VALID": 1,
            "V53_AW2_TRAIN_APPROVED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_expected_source_population(self):
        self.assertEqual(set(audit.EXPECTED_SOURCES), {"V51-002", "V51-007", "V52-008"})

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.METRIC_KEYS), 9)
        self.assertTrue(audit.METRIC_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.METRIC_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.METRIC_KEYS)


if __name__ == "__main__":
    unittest.main()
