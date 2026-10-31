"""AUTOPILOT V1 numeric-only V68 fault handoff; CPU-only with mocks."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools import mini_kuzai_autopilot as A


class NumericV68FailureHandoffTests(unittest.TestCase):
    def fixture(self):
        return {
            "SEMANTIC_VALIDATION_COMPLETE":0,
            "TRAINING_AUTHORIZED":0,
            "TRAINING_STARTED":0,
            "V68_FAIL_DIAG_PASS":1,
            "V68_FAIL_BLIND_ACCESS":0,
            "V68_FAIL_ORIGINAL_FAILED":1,
            "V68_FAIL_EXCEPTION_CLASS_ID":1,
        }

    def test_handoff_uses_existing_verified_probe_report(self):
        with patch.object(A,"report_path",return_value=Path("/existing/probe.json")), \
             patch.object(Path,"exists",return_value=True), \
             patch.object(A,"read_report",return_value=self.fixture()) as get, \
             patch.object(A,"git_sync") as sync:
            A.publish_v68_failure_probe()
            get.assert_called_once_with(A.FAILURE_PROBE_STEP)
            sync.assert_not_called()

    def test_report_rejected_when_blind_access_or_pass_is_invalid(self):
        for bad_field,bad_value in (
            ("V68_FAIL_BLIND_ACCESS",1),
            ("V68_FAIL_DIAG_PASS",0),
            ("V68_FAIL_EXCEPTION_CLASS_ID","ERROR"),
        ):
            metrics=self.fixture()
            metrics[bad_field]=bad_value
            with self.subTest(field=bad_field), \
                 patch.object(A,"report_path",return_value=Path("/existing/probe.json")), \
                 patch.object(Path,"exists",return_value=True), \
                 patch.object(A,"read_report",return_value=metrics):
                with self.assertRaises(A.Halt):
                    A.publish_v68_failure_probe()

    def test_failed_v68_runner_publishes_probe_then_halts(self):
        process=Mock()
        process.wait.return_value=1
        with patch.object(A,"git",return_value=A.APPROVED_RUN_BLOB["v68-head"]), \
             patch.object(A.subprocess,"Popen",return_value=process), \
             patch.object(A,"publish_v68_failure_probe") as probe:
            with self.assertRaisesRegex(A.Halt,"numeric failure report published"):
                A.checked_runner("v68-head","PHASE03-SMOLTALK-V68-OUTPUT-HEAD-001",400)
            probe.assert_called_once()

    def test_probe_publication_failure_is_not_swallowed(self):
        process=Mock()
        process.wait.return_value=1
        with patch.object(A,"git",return_value=A.APPROVED_RUN_BLOB["v68-head"]), \
             patch.object(A.subprocess,"Popen",return_value=process), \
             patch.object(A,"publish_v68_failure_probe",side_effect=A.Halt("failed")):
            with self.assertRaisesRegex(A.Halt,"probe also failed"):
                A.checked_runner("v68-head","PHASE03-SMOLTALK-V68-OUTPUT-HEAD-001",400)

    def test_unrelated_runner_failure_never_publishes_v68_probe(self):
        process=Mock()
        process.wait.return_value=2
        with patch.object(A,"git",return_value=A.APPROVED_RUN_BLOB["v67-readonly"]), \
             patch.object(A.subprocess,"Popen",return_value=process), \
             patch.object(A,"publish_v68_failure_probe") as probe:
            with self.assertRaisesRegex(A.Halt,"Diagnostic runner failed"):
                A.checked_runner("v67-readonly","PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001",400)
            probe.assert_not_called()

    def test_no_training_registered(self):
        self.assertEqual(A.TRAIN_RUNNERS,{})
        self.assertIn("V68-FAILURE-PROBE-001",A.FAILURE_PROBE_STEP)


if __name__=="__main__":
    unittest.main()
