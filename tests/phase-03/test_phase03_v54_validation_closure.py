"""Offline tests for Phase 03 V54 global VALIDATION closure."""
import importlib.util
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

audit=load(
    REPO/"tools/public-audits/phase03_v54_validation_closure.py",
    "v54_validation_closure_test",
)
gogit=load(REPO/"tools/gogit_public.py","v54_validation_closure_gogit_test")

class V54ValidationClosureTests(unittest.TestCase):
    def test_expected_global_state(self):
        metrics=audit.audit()
        audit.require_expected_state(metrics)

    def test_closure_metrics_are_publicly_allowlisted(self):
        expected={
            "TRAIN_FILES","TRAIN_RECORDS","TRAIN_GROUPS",
            "VALIDATION_RECORDS","VALIDATION_GROUPS",
            "VALIDATION_FREEZE_HISTORIES","VALIDATION_SIGNOFFS",
            "VALIDATION_SEMANTIC_PASSES","VALIDATION_EXACT_PROMPT_DUPLICATES",
            "CROSS_SPLIT_ID_COLLISIONS","CROSS_SPLIT_GROUP_COLLISIONS",
            "EXACT_USER_PROMPT_MATCHES",
            "BLIND_TEST_RECORDS","BLIND_TEST_GROUPS_RESERVED",
            "SEMANTIC_VALIDATION_COMPLETE","BLIND_AUTHORING_AUTHORIZED",
            "TRAINING_AUTHORIZED",
        }
        self.assertTrue(expected<=gogit.METRIC_KEYS)

    def test_only_closure_audit_can_complete_semantic_validation(self):
        passing={
            "SEMANTIC_VALIDATION_COMPLETE":1,
            "BLIND_AUTHORING_AUTHORIZED":1,
            "TRAINING_AUTHORIZED":0,
        }
        self.assertTrue(gogit.semantic_validation_complete_for_audit(
            "tools/public-audits/phase03_v54_validation_closure.py",passing
        ))
        self.assertFalse(gogit.semantic_validation_complete_for_audit(
            "tools/public-audits/phase03_v54_validation_freeze.py",passing
        ))
        self.assertFalse(gogit.semantic_validation_complete_for_audit(
            "tools/public-audits/phase03_v54_validation_closure.py",
            {**passing,"TRAINING_AUTHORIZED":1},
        ))

    def test_source_metadata(self):
        self.assertEqual(
            gogit.source_for_audit("tools/public-audits/phase03_v54_validation_closure.py"),
            "Mini-Kuzai Phase 03 designed validation corpus",
        )

if __name__=="__main__":
    unittest.main()
