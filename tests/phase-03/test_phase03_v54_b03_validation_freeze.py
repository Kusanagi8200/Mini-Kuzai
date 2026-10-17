"""Offline tests for V54 B03 validation freeze gate."""
import importlib.util
import os
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
HISTORY=REPO/"reports/assistant-results/history/PHASE03-SMOLTALK-V54-B03-VALIDATION-INTEGRITY-001.json"

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

audit=load(REPO/"tools/public-audits/phase03_v54_b03_validation_freeze.py","v54_b03_freeze_test")
gogit=load(REPO/"tools/gogit_public.py","v54_b03_freeze_gogit_test")

class V54B03FreezeTests(unittest.TestCase):
    def setUp(self):
        if not HISTORY.is_file() and os.environ.get("MINI_KUZAI_REQUIRE_B03_FREEZE_TEST")!="1":
            self.skipTest("B03 integrity history is not published yet")

    def test_expected_state(self):
        m=audit.audit(); audit.require_expected_state(m)

    def test_public_allowlist(self):
        expected={
            "TRAIN_FILES","TRAIN_RECORDS","TRAIN_GROUPS","VALIDATION_B03_CANDIDATES",
            "CROSS_SPLIT_ID_COLLISIONS","CROSS_SPLIT_GROUP_COLLISIONS",
            "EXACT_USER_PROMPT_MATCHES","B03_INDEPENDENT_SIGNOFF",
            "B03_VALIDATION_FROZEN","VALIDATION_FROZEN_RECORDS",
            "VALIDATION_BEHAVIORS_FROZEN","TRAINING_AUTHORIZED",
        }
        self.assertTrue(expected<=gogit.METRIC_KEYS)

    def test_v54_source_metadata(self):
        self.assertEqual(
            gogit.source_for_audit("tools/public-audits/phase03_v54_b03_validation_freeze.py"),
            "Mini-Kuzai Phase 03 designed validation corpus",
        )

if __name__=="__main__": unittest.main()
