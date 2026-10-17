"""Offline tests for V53 completed B08 TRAIN behavior audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_b08_behavior_complete.py",
    "v53_b08_behavior_complete_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_b08_behavior_gogit_test")


class V53B08BehaviorCompleteTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_B08D_TOTAL_RECORDS": 8,
            "V53_B08D_SG01_RECORDS": 4,
            "V53_B08D_SG02_RECORDS": 4,
            "V53_B08D_SG01_COMPLETE": 1,
            "V53_B08D_SG02_COMPLETE": 1,
            "V53_B08D_BEHAVIOR_COMPLETE": 1,
            "V53_B08D_RESERVED_OVERLAP": 0,
            "V53_B08D_B11_TEST_OVERLAP": 0,
            "V53_B08D_CANONICAL_TRAIN_RECORDS": 45,
            "V53_B08D_VALIDATION_TEXT_CREATED": 0,
            "V53_B08D_MODEL_TRAINING_AUTHORIZED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_expected_sg02_ids(self):
        self.assertEqual(len(audit.EXPECTED_SG02_IDS), 4)
        self.assertIn("p03-train-b08-000005", audit.EXPECTED_SG02_IDS)
        self.assertIn("p03-train-b08-000008", audit.EXPECTED_SG02_IDS)

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.METRIC_KEYS), 11)
        self.assertTrue(audit.METRIC_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.METRIC_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.METRIC_KEYS)


if __name__ == "__main__":
    unittest.main()
