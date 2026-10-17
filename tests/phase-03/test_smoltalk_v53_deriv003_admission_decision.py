"""Offline tests for V53 derivative-003 B12 admission-decision audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_deriv003_admission_decision.py",
    "v53_deriv003_admission_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_deriv003_admission_gogit_test")


class V53Deriv003AdmissionTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_D3A_DECISIONS_TOTAL": 1,
            "V53_D3A_CORPUS_APPROVED": 1,
            "V53_D3A_TARGET_TRAIN": 1,
            "V53_D3A_GROUP_VALID": 1,
            "V53_D3A_RESERVED_ID_FREE": 1,
            "V53_D3A_CANONICAL_TRAIN_RECORDS": 45,
            "V53_D3A_SERIALIZED": 0,
            "V53_D3A_MODEL_TRAINING_AUTHORIZED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_current_repository_state(self):
        metrics = audit.audit_metrics()
        audit.require_expected_state(metrics)

    def test_reserved_identity_and_group(self):
        self.assertEqual(audit.EXPECTED_ID, "p03-train-b12-000001")
        self.assertEqual(audit.EXPECTED_GROUP, "sg-b12-01")
        self.assertEqual(audit.EXPECTED_DERIVATIVE, "V53-DERIV-003-V51-002")

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
