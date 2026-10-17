"""Offline tests for V54 B02 validation integrity gate."""
import importlib.util
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

audit=load(REPO/"tools/public-audits/phase03_v54_b02_validation_integrity.py","v54_b02_integrity_test")
gogit=load(REPO/"tools/gogit_public.py","v54_b02_integrity_gogit_test")

class V54B02IntegrityTests(unittest.TestCase):
    def test_expected_state(self):
        m=audit.audit(); audit.require_expected_state(m)

    def test_public_allowlist(self):
        expected={
            "TRAIN_FILES","TRAIN_RECORDS","TRAIN_GROUPS","VALIDATION_B02_CANDIDATES",
            "CROSS_SPLIT_ID_COLLISIONS","CROSS_SPLIT_GROUP_COLLISIONS",
            "EXACT_USER_PROMPT_MATCHES","B02_INDEPENDENT_SIGNOFF",
            "B02_VALIDATION_FROZEN","VALIDATION_FROZEN_RECORDS",
            "VALIDATION_BEHAVIORS_FROZEN","TRAINING_AUTHORIZED",
        }
        self.assertTrue(expected<=gogit.METRIC_KEYS)
        raw=audit.MARKER+"\n"+"".join("{}: 0\n".format(k) for k in sorted(expected))
        self.assertEqual(set(gogit.numeric_metrics(raw)),expected)

    def test_v54_source_metadata(self):
        self.assertEqual(
            gogit.source_for_audit("tools/public-audits/phase03_v54_b02_validation_integrity.py"),
            "Mini-Kuzai Phase 03 designed validation corpus",
        )

if __name__=="__main__": unittest.main()
