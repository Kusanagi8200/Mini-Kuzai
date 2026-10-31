"""CPU-only tests for V64 read-only language-learning aggregates.

The tests intentionally do not open private training data or GPU checkpoints.
"""
from __future__ import annotations

import importlib.util
import inspect
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO))
FILE=REPO/"tools"/"public-audits"/"phase03_v64_language_learning_diagnostic_002.py"
spec=importlib.util.spec_from_file_location("v64_language_diagnostic_002_test",FILE)
if spec is None or spec.loader is None:
    raise RuntimeError("V64 diagnostic import failed")
A=importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


@dataclass
class FakeSeg:
    token_ids:tuple[int,...]


class FakeTokenizer:
    def decode(self,ids):
        return "abc"


class V64DiagnosticV2Tests(unittest.TestCase):
    def test_tokenizer_base_merge_bytes(self):
        segs=[FakeSeg((1,3,300,2)),FakeSeg((1,200,259,2))]
        totals=A.tally_token_statistics(segs,FakeTokenizer())
        self.assertEqual(totals["SEGMENTS"],2)
        self.assertEqual(totals["BYTES_PER_TOKEN_X1000"],1500)
        self.assertEqual(totals["BASE_SHARE_BP"],5000)

    def test_invalid_token_sequence_rejected(self):
        with self.assertRaises(RuntimeError):
            A.tally_token_statistics([FakeSeg((3,300,2))],FakeTokenizer())

    def test_train_sampling_spaced(self):
        values={
            stream:[FakeSeg((1,3,index+259,2)) for index in range(9)]
            for stream in A.T.STREAMS
        }
        sampled=A.sample_train(values)
        self.assertEqual(len(sampled),12)
        self.assertEqual([x.token_ids[2] for x in sampled[:3]],[259,263,267])

    def test_train_sampling_requires_complete_streams(self):
        with self.assertRaises(RuntimeError):
            A.sample_train({"CONTROLLED_TRAIN":[FakeSeg((1,3,259,2))]})

    def test_aggregates_and_gap_are_nonnegative(self):
        train_t={"SEGMENTS":12,"BYTES_PER_TOKEN_X1000":1450,"BASE_SHARE_BP":3800}
        val_t={"SEGMENTS":36,"BYTES_PER_TOKEN_X1000":1120,"BASE_SHARE_BP":4900}
        tr={"TOKENS":9500,"CE_X1000":3900,"TOP1_BP":3300,
            "BASE_TARGET_BP":4000,"BYTE_NLL_X1000":4200,
            "MERGE_NLL_X1000":3700,"EOS_TOP1":4}
        va={"TOKENS":9206,"CE_X1000":4732,"TOP1_BP":2920,
            "BASE_TARGET_BP":5000,"BYTE_NLL_X1000":5200,
            "MERGE_NLL_X1000":4200,"EOS_TOP1":14}
        output=A.result_metrics(train_t,val_t,tr,va,56)
        self.assertEqual(len(output),30)
        self.assertEqual(output["V64_LANG_ABS_CE_GAP_X1000"],832)
        self.assertEqual(output["V64_LANG_VAL_CE_GE_TRAIN"],1)
        self.assertEqual(output["V64_LANG_TRAIN_SEGMENTS"],12)
        self.assertEqual(output["TRAINING_AUTHORIZED"],0)
        self.assertEqual(output["SEMANTIC_VALIDATION_COMPLETE"],0)
        self.assertEqual(output["V64_LANG_BLIND_ACCESS"],0)

    def test_no_duplicate_frozen_corpus_rebuild(self):
        source=inspect.getsource(A.main)
        self.assertEqual(source.count("preflight()"),1)
        self.assertEqual(source.count("build_training_streams("),0)
        self.assertEqual(source.count("build_validation_segments("),0)

    def test_expensive_training_boundary_index_is_not_needed(self):
        source=inspect.getsource(A.preflight)
        self.assertNotIn("verify_runtime(",source)
        self.assertNotIn("build_boundary_index(",source)
        self.assertEqual(source.count("T.build_training_streams()"),1)
        self.assertEqual(source.count("T.build_validation_segments()"),1)
        self.assertIn("T.verify_authorization()",source)
        self.assertIn("T.verify_trainer_freeze(",source)
        self.assertIn('trainer_freeze.get("training_inventory")',source)
        self.assertIn('trainer_freeze.get("validation_inventory")',source)

    def test_negative_gap_flag_does_not_publish_negative_value(self):
        tt={"SEGMENTS":12,"BYTES_PER_TOKEN_X1000":1500,"BASE_SHARE_BP":4000}
        vt={"SEGMENTS":36,"BYTES_PER_TOKEN_X1000":1500,"BASE_SHARE_BP":4000}
        tr={"TOKENS":100,"CE_X1000":6000,"TOP1_BP":0,"BASE_TARGET_BP":4000,
            "BYTE_NLL_X1000":0,"MERGE_NLL_X1000":0,"EOS_TOP1":0}
        va={**tr,"TOKENS":9206,"CE_X1000":4000,"EOS_TOP1":14}
        result=A.result_metrics(tt,vt,tr,va,1)
        self.assertEqual(result["V64_LANG_ABS_CE_GAP_X1000"],2000)
        self.assertEqual(result["V64_LANG_VAL_CE_GE_TRAIN"],0)


if __name__=="__main__":
    unittest.main()
