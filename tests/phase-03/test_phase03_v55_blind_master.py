"""State tests for the V55 BLIND master runner."""
import importlib.util
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location(
    "v55_blind_master",REPO/"tools/run_phase03_v55_blind.py"
)
master=importlib.util.module_from_spec(spec)
spec.loader.exec_module(master)

class V55BlindMasterTests(unittest.TestCase):
    def test_manifest_shape(self):
        data=master.load_master()
        self.assertEqual(data["total_behaviors"],18)
        self.assertEqual(data["target_records"],36)
        self.assertFalse(data["training_authorized"])

    def test_behavior_sequence_and_counts(self):
        data=master.load_master()
        for i,cfg in enumerate(data["behaviors"],1):
            self.assertEqual(cfg["behavior"],f"B{i:02d}")
            self.assertEqual(cfg["index"],i)
            self.assertEqual(cfg["cumulative_before_records"],(i-1)*2)
            self.assertEqual(cfg["cumulative_after_records"],i*2)
            self.assertEqual(cfg["cumulative_before_behaviors"],i-1)
            self.assertEqual(cfg["cumulative_after_behaviors"],i)

    def test_current_freeze_prefix_is_contiguous(self):
        data=master.load_master()
        frozen,next_cfg=master.current_state(data)
        self.assertEqual(frozen,[f"B{i:02d}" for i in range(1,len(frozen)+1)])
        if next_cfg is not None:
            self.assertEqual(next_cfg["behavior"],f"B{len(frozen)+1:02d}")

    def test_v55_global_blind_closure_is_complete(self):
        data=master.load_master()
        frozen,next_cfg=master.current_state(data)
        self.assertEqual(data["status"],"CLOSED")
        self.assertTrue(data["freeze_complete"])
        self.assertEqual(
            data["freeze_complete_step_id"],
            "PHASE03-SMOLTALK-V55-B18-BLIND-FREEZE-001",
        )
        self.assertEqual(
            data["global_blind_closure_step_id"],
            "PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001",
        )
        self.assertTrue(data["global_blind_closure_complete"])
        self.assertEqual(len(frozen),18)
        self.assertIsNone(next_cfg)
        self.assertFalse(data["training_authorized"])

if __name__=="__main__":
    unittest.main()
