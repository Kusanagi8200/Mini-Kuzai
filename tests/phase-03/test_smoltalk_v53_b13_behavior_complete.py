"""Offline tests for V53 completed B13 TRAIN behavior audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_b13_behavior_complete.py",
    "v53_b13_behavior_complete_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_b13_behavior_gogit_test")


class V53B13BehaviorCompleteTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_B13C_TOTAL_RECORDS": 3,
            "V53_B13C_SG01_RECORDS": 3,
            "V53_B13C_POLICY_TARGET_VALID": 1,
            "V53_B13C_SINGLE_TURN_RECORDS": 3,
            "V53_B13C_REVIEWED_RECORDS": 3,
            "V53_B13C_MODEL_VISIBLE_CHANGES": 0,
            "V53_B13C_RESERVED_OVERLAP": 0,
            "V53_B13C_BEHAVIOR_COMPLETE": 1,
            "V53_B13C_CANONICAL_TRAIN_RECORDS": 104,
            "V53_B13C_VALIDATION_TEXT_CREATED": 0,
            "V53_B13C_MODEL_TRAINING_AUTHORIZED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_current_repository_state(self):
        metrics = audit.audit_metrics()
        audit.require_expected_state(metrics)

    def test_policy_rule_is_medium_three(self):
        policy = audit.load_json(audit.POLICY)
        self.assertEqual(policy["variant_policy"]["train"]["MEDIUM"], 3)

    def test_behavior_name_is_humor_sarcasm_teasing(self):
        groups = audit.load_json(audit.GROUPS)
        row = next(x for x in groups["groups"] if x["group_id"] == "sg-b13-01")
        self.assertEqual(row["behavior_name"], "HUMOR / SARCASM / TEASING")

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
