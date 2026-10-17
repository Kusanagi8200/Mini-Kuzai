"""Offline tests for V53 B12 canonical serialization audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_b12_serialization.py",
    "v53_b12_serialization_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_b12_serialization_gogit_test")


class V53B12SerializationTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_B12_SERIALIZED_RECORDS": 1,
            "V53_B12_REVIEWED_RECORDS": 1,
            "V53_B12_METADATA_CORRECTIONS": 0,
            "V53_B12_MODEL_VISIBLE_CHANGES": 0,
            "V53_B12_GROUP_TRAIN_VALID": 1,
            "V53_B12_RESERVED_OVERLAP": 0,
            "V53_B12_CANONICAL_TRAIN_RECORDS": 46,
            "V53_B12_SG01_CURRENT": 1,
            "V53_B12_SG02_CURRENT": 0,
            "V53_B12_TRAIN_COMPLETE": 0,
            "V53_B12_MODEL_TRAINING_AUTHORIZED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_current_repository_state(self):
        metrics = audit.audit_metrics()
        audit.require_expected_state(metrics)

    def test_expected_identity(self):
        self.assertEqual(audit.EXPECTED_ID, "p03-train-b12-000001")
        self.assertEqual(len(audit.TRAIN_FILES), 8)

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
