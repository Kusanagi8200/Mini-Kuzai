"""Offline tests for V53 B08 sg-b08-01 completion audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_b08_group_completion.py",
    "v53_b08_completion_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_b08_completion_gogit_test")


class V53B08CompletionTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_B08C_GROUP_RECORDS": 4,
            "V53_B08C_NEW_DESIGNED_RECORDS": 3,
            "V53_B08C_EXTERNAL_RECORDS": 1,
            "V53_B08C_REVIEWED_RECORDS": 4,
            "V53_B08C_GROUP_COMPLETE": 1,
            "V53_B08C_BEHAVIOR_COMPLETE": 0,
            "V53_B08C_RESERVED_OVERLAP": 0,
            "V53_B08C_CANONICAL_TRAIN_RECORDS": 41,
            "V53_B08C_VALIDATION_TEXT_CREATED": 0,
            "V53_B08C_MODEL_TRAINING_AUTHORIZED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_expected_ids(self):
        self.assertEqual(len(audit.EXPECTED_IDS), 4)
        self.assertIn("p03-train-b08-000001", audit.EXPECTED_IDS)
        self.assertIn("p03-train-b08-000004", audit.EXPECTED_IDS)

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.METRIC_KEYS), 10)
        self.assertTrue(audit.METRIC_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.METRIC_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.METRIC_KEYS)


if __name__ == "__main__":
    unittest.main()
