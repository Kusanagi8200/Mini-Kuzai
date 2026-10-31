"""V70 AUTOPILOT V3 six-stage read-only campaign structural tests."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools import mini_kuzai_autopilot as A


class V70CampaignTests(unittest.TestCase):
    def test_six_stage_frozen_campaign(self):
        plan,digest,source=A.load_campaign("phase03-autopilot-v3.json")
        self.assertEqual(plan["campaign_id"],"phase03-precision-v3")
        self.assertEqual(len(plan["steps"]),6)
        self.assertEqual(len(digest),64)
        self.assertTrue(source.is_file())
        self.assertEqual(plan["max_wall_seconds"],7200)

    def test_one_pinned_gpu_runner(self):
        plan,_,_=A.load_campaign("phase03-autopilot-v3.json")
        jobs=[s for s in plan["steps"] if s["kind"]=="diagnostic"]
        self.assertEqual(len(jobs),1)
        self.assertEqual(jobs[0]["runner"],"v70-precision")
        self.assertEqual(A.APPROVED_RUN_BLOB["v70-precision"],
                         "91b4dfaae7aa1c5294f20c9edbc4692e63c77dac")
        self.assertEqual(A.DIAGNOSTIC_RUNNERS["v70-precision"],
                         "tools/run_v70_precision_control_001_job.py")

    def test_no_training_or_arbitrary_command(self):
        plan,_,_=A.load_campaign("phase03-autopilot-v3.json")
        self.assertEqual(A.TRAIN_RUNNERS,{})
        self.assertTrue(all(stage["kind"] in ("verify","diagnostic") for stage in plan["steps"]))
        altered=copy.deepcopy(plan)
        altered["steps"][2]["kind"]="train_window"
        with self.assertRaises(A.Halt):
            A.validate_campaign(altered)

    def test_numeric_decision_logic_only(self):
        plan,_,_=A.load_campaign("phase03-autopilot-v3.json")
        for stage in plan["steps"]:
            for condition in (*stage["when"],*stage["rules"]):
                A.validate_rule(condition)
        self.assertTrue(all(s["kind"]=="verify" and s["runner"] is None
                            and not s["required"] for s in plan["steps"][3:]))

    def test_v70_gogit_producer_registered(self):
        self.assertEqual(
            A.REPORT_PRODUCERS["PHASE03-SMOLTALK-V70-PRECISION-CONTROL-001"],
            "tools/public-audits/phase03_v70_precision_control_001.py",
        )


if __name__=="__main__":
    unittest.main()
