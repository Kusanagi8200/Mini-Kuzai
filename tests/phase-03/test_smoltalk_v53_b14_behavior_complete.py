"""Offline tests for V53 B14 and full TRAIN completion audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_b14_behavior_complete.py",
    "v53_b14_behavior_complete_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_b14_behavior_gogit_test")


class V53B14BehaviorCompleteTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_B14C_TOTAL_RECORDS": 3,
            "V53_B14C_SG01_RECORDS": 3,
            "V53_B14C_POLICY_TARGET_VALID": 1,
            "V53_B14C_SINGLE_TURN_RECORDS": 3,
            "V53_B14C_REVIEWED_RECORDS": 3,
            "V53_B14C_CORRECTED_RECORDS": 1,
            "V53_B14C_MODEL_VISIBLE_CHANGES": 1,
            "V53_B14C_RESERVED_OVERLAP": 0,
            "V53_B14C_BEHAVIOR_COMPLETE": 1,
            "V53_B14C_CANONICAL_TRAIN_RECORDS": 107,
            "V53_B14C_COMPLETE_TRAIN_GROUPS": 29,
            "V53_B14C_ALL_TRAIN_GROUPS_COMPLETE": 1,
            "V53_B14C_VALIDATION_TEXT_CREATED": 0,
            "V53_B14C_MODEL_TRAINING_AUTHORIZED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_current_repository_state(self):
        metrics = audit.audit_metrics()
        audit.require_expected_state(metrics)

    def test_policy_rule_is_medium_three_and_planned_train_is_107(self):
        policy = audit.load_json(audit.POLICY)
        self.assertEqual(policy["variant_policy"]["train"]["MEDIUM"], 3)
        self.assertEqual(policy["variant_policy"]["planned_train_records"], 107)

    def test_single_reviewed_correction_is_preserved(self):
        review = audit.load_json(audit.REVIEW)
        self.assertEqual(review["corrected_record_ids"], ["p03-train-b14-000003"])
        self.assertTrue(review["model_visible_text_changed"])

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.METRIC_KEYS), 14)
        self.assertTrue(audit.METRIC_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.METRIC_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.METRIC_KEYS)


if __name__ == "__main__":
    unittest.main()
