"""Generic tests for configured V54 validation integrity/freeze gates."""
import importlib.util
import os
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
BEHAVIOR=os.environ.get("MINI_KUZAI_VALIDATION_BEHAVIOR","").upper()
GATE=os.environ.get("MINI_KUZAI_VALIDATION_GATE","integrity").lower()

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

engine=load(REPO/"tools/phase03_v54_validation_engine.py","v54_validation_engine_test")
gogit=load(REPO/"tools/gogit_public.py","v54_validation_gogit_test")

class V54GenericValidationTests(unittest.TestCase):
    def setUp(self):
        if not BEHAVIOR:
            self.skipTest("Generic validation behavior not selected")

    def test_expected_state(self):
        if GATE=="freeze":
            metrics=engine.freeze_metrics(BEHAVIOR)
            engine.require_freeze_expected(metrics,BEHAVIOR)
        else:
            metrics=engine.integrity_metrics(BEHAVIOR)
            engine.require_integrity_expected(metrics,BEHAVIOR)

    def test_public_allowlist(self):
        expected={
            "TRAIN_FILES","TRAIN_RECORDS","TRAIN_GROUPS",
            "VALIDATION_BATCH_INDEX","VALIDATION_BATCH_CANDIDATES",
            "VALIDATION_BATCH_SIGNOFF","VALIDATION_BATCH_SEMANTIC_PASS",
            "VALIDATION_BATCH_FROZEN","CROSS_SPLIT_ID_COLLISIONS",
            "CROSS_SPLIT_GROUP_COLLISIONS","EXACT_USER_PROMPT_MATCHES",
            "VALIDATION_FROZEN_RECORDS","VALIDATION_BEHAVIORS_FROZEN",
            "TRAINING_AUTHORIZED",
        }
        if not expected<=gogit.METRIC_KEYS and os.environ.get("MINI_KUZAI_REQUIRE_GENERIC_GOGIT_KEYS")!="1":
            self.skipTest("Generic V54 GOGIT keys are installed by the master runner")
        self.assertTrue(expected<=gogit.METRIC_KEYS)

    def test_v54_source_metadata(self):
        tracked="tools/public-audits/phase03_v54_validation_{}.py".format("freeze" if GATE=="freeze" else "integrity")
        self.assertEqual(gogit.source_for_audit(tracked),"Mini-Kuzai Phase 03 designed validation corpus")

if __name__=="__main__":
    unittest.main()
