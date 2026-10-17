"""State tests for the V54 master validation runner."""
import importlib.util
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]

spec=importlib.util.spec_from_file_location(
    "v54_validation_master",
    REPO/"tools/run_phase03_v54_validation.py",
)
master=importlib.util.module_from_spec(spec)
spec.loader.exec_module(master)

class V54ValidationMasterTests(unittest.TestCase):
    def test_manifest_shape(self):
        config=master.load_config()
        self.assertEqual(config["total_behaviors"],18)
        self.assertEqual(config["target_records"],36)
        self.assertEqual(config["status"],"CLOSED")
        self.assertTrue(config["freeze_complete"])
        self.assertTrue(config["global_validation_closure_complete"])
        self.assertTrue(config["semantic_validation_complete"])
        self.assertTrue(config["blind_authoring_authorized"])
        self.assertFalse(config["training_authorized"])

    def test_current_freeze_prefix_is_contiguous(self):
        config=master.load_config()
        frozen,next_item=master.current_state(config["behaviors"])
        self.assertGreaterEqual(len(frozen),10)
        self.assertEqual(frozen,[f"B{i:02d}" for i in range(1,len(frozen)+1)])
        if next_item is not None:
            self.assertEqual(next_item["behavior"],f"B{len(frozen)+1:02d}")

    def test_generic_configs_b06_to_b18_exist(self):
        for i in range(6,19):
            behavior=f"B{i:02d}"
            cfg=master.load_generic_config(behavior)
            self.assertIsNotNone(cfg)
            self.assertEqual(cfg["behavior"],behavior)
            self.assertEqual(cfg["index"],i)
            self.assertEqual(cfg["cumulative_after_records"],i*2)
            self.assertEqual(cfg["cumulative_after_behaviors"],i)
            self.assertFalse(cfg["training_authorized"])

    def test_final_target_is_b18(self):
        cfg=master.load_generic_config("B18")
        self.assertEqual(cfg["freeze_step_id"],"PHASE03-SMOLTALK-V54-B18-VALIDATION-FREEZE-001")
        self.assertEqual(cfg["cumulative_after_records"],36)
        self.assertEqual(cfg["cumulative_after_behaviors"],18)

if __name__=="__main__":
    unittest.main()
