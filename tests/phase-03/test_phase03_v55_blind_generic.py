"""Generic tests for configured V55 BLIND integrity/freeze gates."""
import importlib.util
import os
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
BEHAVIOR=os.environ.get("MINI_KUZAI_BLIND_BEHAVIOR","").upper()
GATE=os.environ.get("MINI_KUZAI_BLIND_GATE","integrity").lower()

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

engine=load(REPO/"tools/phase03_v55_blind_engine.py","v55_blind_engine_test")
gogit=load(REPO/"tools/gogit_public.py","v55_blind_gogit_test")

class V55GenericBlindTests(unittest.TestCase):
    def setUp(self):
        if not BEHAVIOR:
            self.skipTest("V55 BLIND behavior not selected")

    def test_expected_state(self):
        if GATE=="freeze":
            metrics=engine.freeze_metrics(BEHAVIOR)
            engine.require_freeze_expected(metrics,BEHAVIOR)
        else:
            metrics=engine.integrity_metrics(BEHAVIOR)
            engine.require_integrity_expected(metrics,BEHAVIOR)

    def test_public_allowlist(self):
        expected={
            "TRAIN_RECORDS","TRAIN_GROUPS","VALIDATION_RECORDS","VALIDATION_GROUPS",
            "SEMANTIC_VALIDATION_COMPLETE","BLIND_AUTHORING_AUTHORIZED",
            "BLIND_BATCH_INDEX","BLIND_BATCH_CANDIDATES","BLIND_BATCH_SIGNOFF",
            "BLIND_BATCH_SEMANTIC_PASS","BLIND_BATCH_FROZEN",
            "BLIND_TEST_RECORDS_FROZEN","BLIND_BEHAVIORS_FROZEN",
            "CROSS_SPLIT_ID_COLLISIONS","CROSS_SPLIT_GROUP_COLLISIONS",
            "EXACT_USER_PROMPT_MATCHES","TRAINING_AUTHORIZED",
        }
        self.assertTrue(expected<=gogit.METRIC_KEYS)

    def test_source_metadata(self):
        tracked="tools/public-audits/phase03_v55_blind_{}.py".format(
            "freeze" if GATE=="freeze" else "integrity"
        )
        self.assertEqual(
            gogit.source_for_audit(tracked),
            "Mini-Kuzai Phase 03 designed blind-test corpus",
        )

    def test_validation_completion_persists(self):
        metrics={
            "SEMANTIC_VALIDATION_COMPLETE":1,
            "BLIND_AUTHORING_AUTHORIZED":1,
            "TRAINING_AUTHORIZED":0,
        }
        self.assertTrue(gogit.semantic_validation_complete_for_audit(
            "tools/public-audits/phase03_v55_blind_integrity.py",metrics
        ))

if __name__=="__main__":
    unittest.main()
