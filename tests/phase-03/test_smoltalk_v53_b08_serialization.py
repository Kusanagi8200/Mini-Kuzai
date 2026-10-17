"""Offline tests for V53 B08 canonical serialization audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_b08_serialization.py",
    "v53_b08_serialization_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_b08_serialization_gogit_test")


class V53B08SerializationTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_B08_SERIALIZED_RECORDS": 1,
            "V53_B08_REVIEWED_RECORDS": 1,
            "V53_B08_METADATA_CORRECTIONS": 1,
            "V53_B08_MODEL_VISIBLE_CHANGES": 0,
            "V53_B08_GROUP_TRAIN_VALID": 1,
            "V53_B08_RESERVED_OVERLAP": 0,
            "V53_B08_CANONICAL_TRAIN_RECORDS": 38,
            "V53_B08_GROUP_CURRENT": 1,
            "V53_B08_GROUP_PLANNED": 4,
            "V53_B08_TRAIN_COMPLETE": 0,
            "V53_B08_MODEL_TRAINING_AUTHORIZED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_reserved_identity_and_group(self):
        self.assertEqual(audit.EXPECTED_ID, "p03-train-b08-000001")
        self.assertEqual(audit.EXPECTED_GROUP, "sg-b08-01")
        self.assertEqual(len(audit.TRAIN_FILES), 7)

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
