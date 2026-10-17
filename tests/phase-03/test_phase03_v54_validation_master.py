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

    def test_current_published_boundary(self):
        config=master.load_config()
        frozen,next_item=master.current_state(config["behaviors"])
        self.assertEqual(frozen,["B01","B02","B03","B04","B05"])
        self.assertEqual(next_item["behavior"],"B06")
        self.assertEqual(next_item["group_id"],"sg-b06-03")
        self.assertEqual(next_item["scenario_type"],"tentative_hypothesis_unknown")

    def test_b06_runner_is_not_silently_assumed(self):
        self.assertFalse(master.runner_path("B06").is_file())

if __name__=="__main__":
    unittest.main()
