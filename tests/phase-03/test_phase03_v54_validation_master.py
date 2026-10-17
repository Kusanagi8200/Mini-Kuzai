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
        self.assertFalse(config["training_authorized"])

    def test_current_freeze_prefix_is_contiguous(self):
        config=master.load_config()
        frozen,next_item=master.current_state(config["behaviors"])
        self.assertGreaterEqual(len(frozen),5)
        self.assertEqual(frozen,[f"B{i:02d}" for i in range(1,len(frozen)+1)])
        if next_item is not None:
            self.assertEqual(next_item["behavior"],f"B{len(frozen)+1:02d}")

    def test_generic_configs_b06_to_b10_exist(self):
        for i in range(6,11):
            behavior=f"B{i:02d}"
            cfg=master.load_generic_config(behavior)
            self.assertIsNotNone(cfg)
            self.assertEqual(cfg["behavior"],behavior)
            self.assertEqual(cfg["index"],i)

    def test_first_unconfigured_behavior_is_b11(self):
        self.assertIsNone(master.load_generic_config("B11"))

if __name__=="__main__":
    unittest.main()
