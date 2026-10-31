"""CPU-only checks for GOGIT V68 failure taxonomy; no GPU model accessed."""
from __future__ import annotations

import importlib.util
import sys
import traceback
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
FILE=REPO/"tools"/"public-audits"/"phase03_v68_failure_probe_001.py"
spec=importlib.util.spec_from_file_location("v68_failure_probe_tests",FILE)
if spec is None or spec.loader is None:
    raise RuntimeError("Failure-probe source unavailable")
P=importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


class V68FailureProbeTests(unittest.TestCase):
    def test_known_pad_row_failure_code(self):
        error=RuntimeError("Frozen PAD embedding row nonzero")
        frames=[
            traceback.FrameSummary(str(P.SOURCE),200,"main"),
            traceback.FrameSummary(str(P.SOURCE),49,"summarize_head"),
        ]
        result=P.numeric_report(error,frames,19)
        self.assertEqual(len(result),13)
        self.assertEqual(result["V68_FAIL_ORIGINAL_FAILED"],1)
        self.assertEqual(result["V68_FAIL_CAUSE_ID"],5)
        self.assertEqual(result["V68_FAIL_SOURCE_FUNCTION_ID"],2)
        self.assertEqual(result["V68_FAIL_SOURCE_LINE"],49)
        self.assertEqual(result["V68_FAIL_LAST_FILE_FAMILY"],1)
        self.assertEqual(result["V68_FAIL_BLIND_ACCESS"],0)

    def test_unknown_error_does_not_publish_message(self):
        secret="private payload DO NOT DISCLOSE"
        result=P.numeric_report(ValueError(secret),[],0)
        self.assertEqual(result["V68_FAIL_CAUSE_ID"],0)
        self.assertEqual(result["V68_FAIL_EXCEPTION_CLASS_ID"],2)
        self.assertNotIn(secret,str(result))
        self.assertTrue(all(type(v) is int for v in result.values()))

    def test_success_code_is_not_misrepresented_as_failure(self):
        result=P.numeric_report(None,[],42)
        self.assertEqual(result["V68_FAIL_ORIGINAL_FAILED"],0)
        self.assertEqual(result["V68_FAIL_CAUSE_ID"],0)
        self.assertEqual(result["TRAINING_STARTED"],0)
        self.assertEqual(result["SEMANTIC_VALIDATION_COMPLETE"],0)

    def test_no_raw_output_captured(self):
        sink=P.DiscardOutput()
        self.assertEqual(sink.write("secret"),6)
        self.assertIsNone(sink.flush())
        self.assertFalse(hasattr(sink,"buffer"))

    def test_probe_has_no_training_or_blind(self):
        c=FILE.read_text(encoding="utf-8")
        self.assertNotIn("optimizer.step(",c)
        self.assertNotIn("torch.save(",c)
        self.assertNotIn("build_blind",c)
        self.assertIn("runpy.run_path",c)

if __name__=="__main__":
    unittest.main()
