"""CPU-only AUTOPILOT V2 campaign verification."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools import mini_kuzai_autopilot as A

class V69AutopilotTests(unittest.TestCase):
    def test_campaign_schema_and_readonly_stages(self):
        p,h,path=A.load_campaign("phase03-autopilot-v2.json")
        self.assertEqual(p["campaign_id"],"phase03-norm-v2")
        self.assertEqual(len(p["steps"]),6)
        self.assertEqual(len(h),64)
        self.assertTrue(path.is_file())
        self.assertTrue(all(s["kind"] in ("verify","diagnostic") for s in p["steps"]))
        self.assertEqual(A.TRAIN_RUNNERS,{})

    def test_v69_runner_exactly_pinned(self):
        p,_,_=A.load_campaign("phase03-autopilot-v2.json")
        runners=[s for s in p["steps"] if s["kind"]=="diagnostic"]
        self.assertEqual(len(runners),1)
        self.assertEqual(runners[0]["runner"],"v69-norm")
        self.assertEqual(A.APPROVED_RUN_BLOB["v69-norm"],
                         "14eb37c5835a9c93c4a11da301bac25db94bbe0e")
        self.assertEqual(A.DIAGNOSTIC_RUNNERS["v69-norm"],
                         "tools/run_v69_output_norm_counterfactual_001_job.py")

    def test_only_integer_decision_conditions(self):
        p,_,_=A.load_campaign("phase03-autopilot-v2.json")
        for stage in p["steps"]:
            for rule in stage["when"]+stage["rules"]:
                A.validate_rule(rule)
                self.assertIs(type(rule["value"]),int)

    def test_training_stage_stays_disabled(self):
        p,_,_=A.load_campaign("phase03-autopilot-v2.json")
        modified=copy.deepcopy(p)
        modified["steps"][2]["kind"]="train_window"
        with self.assertRaises(A.Halt):
            A.validate_campaign(modified)

    def test_decision_branches_do_not_launch_jobs(self):
        p,_,_=A.load_campaign("phase03-autopilot-v2.json")
        branches=p["steps"][-3:]
        self.assertTrue(all(s["required"] is False for s in branches))
        self.assertTrue(all(s["kind"]=="verify" and s["runner"] is None for s in branches))

if __name__=="__main__":unittest.main()
