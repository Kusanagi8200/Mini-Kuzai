"""Offline tests for V54 B01 validation structural integrity audit."""

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
    REPO / "tools/public-audits/phase03_v54_b01_validation_integrity.py",
    "v54_b01_validation_integrity_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v54_b01_validation_gogit_test")


class V54B01ValidationIntegrityTests(unittest.TestCase):
    def test_expected_state(self):
        self.assertEqual(
            audit.audit(),
            {
                "TRAIN_FILES": 19,
                "TRAIN_RECORDS": 107,
                "TRAIN_GROUPS": 29,
                "VALIDATION_B01_CANDIDATES": 2,
                "CROSS_SPLIT_ID_COLLISIONS": 0,
                "CROSS_SPLIT_GROUP_COLLISIONS": 0,
                "EXACT_USER_PROMPT_MATCHES": 0,
                "B01_INDEPENDENT_SIGNOFF": 0,
                "B01_VALIDATION_FROZEN": 0,
                "TRAINING_AUTHORIZED": 0,
            },
        )

    def test_public_numeric_allowlist(self):
        expected = {
            "TRAIN_FILES",
            "TRAIN_RECORDS",
            "TRAIN_GROUPS",
            "VALIDATION_B01_CANDIDATES",
            "CROSS_SPLIT_ID_COLLISIONS",
            "CROSS_SPLIT_GROUP_COLLISIONS",
            "EXACT_USER_PROMPT_MATCHES",
            "B01_INDEPENDENT_SIGNOFF",
            "B01_VALIDATION_FROZEN",
            "TRAINING_AUTHORIZED",
        }
        self.assertTrue(expected <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(expected)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), expected)


if __name__ == "__main__":
    unittest.main()
