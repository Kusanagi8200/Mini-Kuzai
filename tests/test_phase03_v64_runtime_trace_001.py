"""CPU-only unit tests of numeric V64 runtime trace parsing."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
FILE=REPO/"tools"/"public-audits"/"phase03_v64_runtime_trace_001.py"
spec=importlib.util.spec_from_file_location("v64_runtime_trace_test",FILE)
if spec is None or spec.loader is None:
    raise RuntimeError("V64 runtime trace not importable")
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class V64RuntimeTraceTests(unittest.TestCase):
    def test_parse_completed_nested_spans(self):
        stream=(
            "BEGIN:PREFLIGHT\nBEGIN:VERIFY_RUNTIME\n"
            "BEGIN:BUILD_TRAIN\nEND:BUILD_TRAIN:200\n"
            "END:VERIFY_RUNTIME:500\nEND:PREFLIGHT:600\n"
        )
        timings,active,last_started,finished,invalid=M.parse(stream)
        self.assertEqual(timings["BUILD_TRAIN"],200)
        self.assertEqual(timings["VERIFY_RUNTIME"],500)
        self.assertEqual(timings["PREFLIGHT"],600)
        self.assertEqual(active,[])
        self.assertEqual(last_started,M.CODES["BUILD_TRAIN"])
        self.assertEqual(finished,3)
        self.assertEqual(invalid,0)

    def test_parse_interrupted_active_stage(self):
        data="BEGIN:PREFLIGHT\nBEGIN:VERIFY_RUNTIME\nBEGIN:LOAD_POOL\n"
        durations,active,last_started,finished,invalid=M.parse(data)
        self.assertEqual(active[-1],"LOAD_POOL")
        self.assertEqual(M.CODES[active[-1]],M.CODES["LOAD_POOL"])
        self.assertEqual(finished,0)
        self.assertEqual(invalid,0)

    def test_parse_rejects_invalid_stage_order(self):
        data="BEGIN:PREFLIGHT\nEND:LOAD_POOL:42\n"
        self.assertEqual(M.parse(data)[-1],1)

    def test_parse_rejects_negative_timing(self):
        data="BEGIN:LOAD_POOL\nEND:LOAD_POOL:-2\n"
        self.assertEqual(M.parse(data)[-1],1)

    def test_stage_keys_unique(self):
        self.assertEqual(len(M.CODES),len(M.STAGES))
        self.assertEqual(len(M.CODES),13)
        self.assertEqual(M.TIMEOUT,155)


if __name__=="__main__":
    unittest.main()
