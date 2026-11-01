import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import dev_flow_worker as D


class DevFlowRequestTests(unittest.TestCase):
    def test_start_request(self):
        payload = {
            "schema_version": 1,
            "command": "START-DEV-FLOW",
            "step": "V74",
        }
        parsed = D.validate_request_payload(payload, "V74-start.json")
        self.assertEqual(parsed["action"], "start")
        self.assertIsNone(parsed["report"])

    def test_final_request(self):
        payload = {
            "schema_version": 1,
            "command": "FINAL-DEV-FLOW",
            "step": "V74",
            "report": (
                "reports/assistant-results/history/"
                "PHASE03-SMOLTALK-V74-TEST-001.json"
            ),
        }
        parsed = D.validate_request_payload(payload, "V74-final.json")
        self.assertEqual(parsed["action"], "close")

    def test_wrong_command_is_rejected(self):
        with self.assertRaises(D.DevFlowError):
            D.validate_request_payload(
                {
                    "schema_version": 1,
                    "command": "START",
                    "step": "V74",
                },
                "V74-start.json",
            )

    def test_unsafe_report_is_rejected(self):
        with self.assertRaises(D.DevFlowError):
            D.validate_request_payload(
                {
                    "schema_version": 1,
                    "command": "FINAL-DEV-FLOW",
                    "step": "V74",
                    "report": "../../secret.json",
                },
                "V74-final.json",
            )

    def test_filename_must_match_step(self):
        with self.assertRaises(D.DevFlowError):
            D.validate_request_payload(
                {
                    "schema_version": 1,
                    "command": "START-DEV-FLOW",
                    "step": "V75",
                },
                "V74-start.json",
            )


if __name__ == "__main__":
    unittest.main()
