"""Offline tests for V54 B01 validation freeze audit."""

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
    REPO / "tools/public-audits/phase03_v54_b01_validation_freeze.py",
    "v54_b01_validation_freeze_test",
)
gogit = load(
    REPO / "tools/gogit_public.py",
    "v54_b01_validation_freeze_gogit_test",
)


class V54B01ValidationFreezeTests(unittest.TestCase):
    def test_expected_state(self):
        metrics = audit.audit()
        audit.require_expected_state(metrics)

    def test_reviewed_batch_is_metadata_only_transition(self):
        v01 = audit.load_jsonl(audit.BATCH_V01)
        v02 = audit.load_jsonl(audit.BATCH_V02)
        self.assertEqual(len(v01), 2)
        self.assertEqual(len(v02), 2)
        for left, right in zip(v01, v02):
            self.assertEqual(left["id"], right["id"])
            self.assertEqual(left["messages"], right["messages"])
            self.assertFalse(left["provenance"]["reviewed"])
            self.assertTrue(right["provenance"]["reviewed"])
            self.assertEqual(right["provenance"]["review_decision"], "ACCEPT")

    def test_independent_review_evidence(self):
        review = audit.load_json(audit.REVIEW_RESULT)
        self.assertTrue(review["review_complete"])
        self.assertEqual(review["accepted"], 2)
        self.assertTrue(review["semantic_isolation_pass"])
        self.assertFalse(review["external_human_review_claimed"])

    def test_v54_source_metadata(self):
        self.assertEqual(
            gogit.source_for_audit("tools/public-audits/phase03_v54_b01_validation_freeze.py"),
            "Mini-Kuzai Phase 03 designed validation corpus",
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
