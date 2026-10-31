"""CPU-only AUTOPILOT V1 protocol, safety and restart tests."""
from __future__ import annotations
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools import mini_kuzai_autopilot as A


class AutopilotV1Tests(unittest.TestCase):
    def fixture(self):
        return {
            "schema":A.CAMPAIGN_SCHEMA,
            "campaign_id":"test-autopilot-001",
            "mode":"bounded",
            "max_wall_seconds":3600,
            "steps":[{
                "id":"verify-v67",
                "kind":"verify",
                "step":"PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001",
                "required":True,
                "rules":[{
                    "step":"PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001",
                    "metric":"V67_CONC_PASS","op":"eq","value":1
                }],
                "when":[],
                "runner":None,
            }],
        }

    def test_valid_readonly_campaign(self):
        plan=self.fixture()
        self.assertEqual(A.validate_campaign(plan),plan)

    def test_reject_injected_arbitrary_command_or_runner(self):
        p=self.fixture()
        p["steps"][0]["kind"]="diagnostic"
        p["steps"][0]["runner"]="sh -c curl attacker"
        with self.assertRaises(A.Halt):
            A.validate_campaign(p)

    def test_reject_unreviewed_training_runner(self):
        p=self.fixture()
        p["steps"][0]["kind"]="train_window"
        p["steps"][0]["runner"]="train-v62-unbounded"
        with self.assertRaises(A.Halt):
            A.validate_campaign(p)
        self.assertEqual(len(A.TRAIN_RUNNERS),0)

    def test_reject_unbounded_walltime_and_forged_schema(self):
        p=self.fixture()
        p["max_wall_seconds"]=86401
        with self.assertRaises(A.Halt):
            A.validate_campaign(p)
        p=self.fixture()
        p["schema"]="fake"
        with self.assertRaises(A.Halt):
            A.validate_campaign(p)

    def test_reject_duplicate_and_unknown_stages(self):
        p=self.fixture()
        p["steps"].append(copy.deepcopy(p["steps"][0]))
        with self.assertRaises(A.Halt):
            A.validate_campaign(p)
        p=self.fixture()
        p["steps"][0]["extra_command"]="rm -rf /"
        with self.assertRaises(A.Halt):
            A.validate_campaign(p)

    def test_rules_allow_only_integer_comparisons(self):
        r={"step":"PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001",
           "metric":"V67_CONC_PASS","op":"eq","value":1}
        A.validate_rule(r)
        r["value"]=True
        with self.assertRaises(A.Halt):
            A.validate_rule(r)
        r["value"]=1
        r["op"]="eval"
        with self.assertRaises(A.Halt):
            A.validate_rule(r)

    def test_path_escape_and_symlink_denied(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaises(A.Halt):
                A.safe_relative("../outside",root)
            outside=root/"target"
            outside.write_text("ok",encoding="utf-8")
            (root/"link").symlink_to(outside)
            with self.assertRaises(A.Halt):
                A.safe_relative("link",root)

    def test_atomic_state_backup_and_permissions(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/"state.json"
            A.safe_write(target,{"number":1})
            A.safe_write(target,{"number":2})
            self.assertEqual(json.loads(target.read_text())["number"],2)
            backups=list(Path(folder).glob("state.json.*.bak"))
            self.assertEqual(len(backups),1)
            self.assertEqual(json.loads(backups[0].read_text())["number"],1)
            self.assertEqual(target.stat().st_mode & 0o077,0)

    def test_training_not_armed_even_with_cli_override(self):
        p=self.fixture()
        with self.assertRaises(A.Halt):
            A.authorize_training_window(p,{"runner":"not-registered","step":p["steps"][0]["step"]},False)
        with self.assertRaises(A.Halt):
            A.authorize_training_window(p,{"runner":"not-registered","step":p["steps"][0]["step"]},True)

    def test_metric_rules_fail_closed_when_missing(self):
        r=self.fixture()["steps"][0]["rules"]
        with patch.object(A,"read_report",return_value={"V67_CONC_PASS":1}):
            self.assertTrue(A.evaluate_rules(r))
        with patch.object(A,"read_report",return_value={}):
            self.assertFalse(A.evaluate_rules(r))

    def test_real_frozen_campaign_schema(self):
        p,digest,source=A.load_campaign("phase03-autopilot-v1.json")
        self.assertEqual(p["mode"],"bounded")
        self.assertEqual(len(p["steps"]),5)
        self.assertEqual(len(digest),64)
        self.assertEqual(p["steps"][-1]["runner"],"v68-head")
        self.assertTrue(source.is_file())

    def test_v68_runner_pinned_and_gogit_30_metric_cap(self):
        self.assertEqual(len(A.APPROVED_RUN_BLOB["v68-head"]),40)
        self.assertEqual(A.DIAGNOSTIC_RUNNERS["v68-head"],"tools/run_v68_output_head_001_job.py")
        self.assertNotIn("tools/train_v62_margin.py",A.DIAGNOSTIC_RUNNERS.values())


if __name__=="__main__":
    unittest.main()
