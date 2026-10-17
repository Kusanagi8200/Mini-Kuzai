"""Offline tests for V53 derivative-003 eligibility audit."""

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
    REPO / "tools/public-audits/smoltalk_v53_deriv003_eligibility.py",
    "v53_deriv003_eligibility_test",
)
gogit = load(REPO / "tools/gogit_public.py", "v53_deriv003_eligibility_gogit_test")


class V53Deriv003EligibilityTests(unittest.TestCase):
    def test_expected_metric_shape(self):
        expected = {
            "V53_D3E_TOTAL": 1,
            "V53_D3E_PROVENANCE_PASS": 1,
            "V53_D3E_LICENSE_PASS": 1,
            "V53_D3E_CANONICAL_TRAIN_RECORDS": 45,
            "V53_D3E_EXACT_DUP_HITS": 0,
            "V53_D3E_NEAR_DUP_HITS": 0,
            "V53_D3E_RESERVED_VALIDATION_COLLISION": 0,
            "V53_D3E_RESERVED_BLIND_COLLISION": 0,
            "V53_D3E_SEMANTIC_PASS": 1,
            "V53_D3E_ADMISSION_READY": 1,
            "V53_D3E_TRAIN_APPROVED": 0,
            "V53_D3E_SPLIT_ASSIGNED": 0,
        }
        audit.require_expected_state(dict(sorted(expected.items())))

    def test_current_repository_state(self):
        metrics = audit.audit_metrics()
        audit.require_expected_state(metrics)

    def test_public_numeric_allowlist_exact(self):
        self.assertEqual(len(audit.METRIC_KEYS), 12)
        self.assertTrue(audit.METRIC_KEYS <= gogit.METRIC_KEYS)
        raw = audit.MARKER + "\n" + "".join(
            "{}: 0\n".format(name) for name in sorted(audit.METRIC_KEYS)
        )
        parsed = gogit.numeric_metrics(raw)
        self.assertEqual(set(parsed), audit.METRIC_KEYS)


if __name__ == "__main__":
    unittest.main()
