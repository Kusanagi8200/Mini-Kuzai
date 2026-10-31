"""CPU-only V67 stable ranks and immutable numeric concentration report tests."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from collections import Counter
from pathlib import Path

import torch

REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
FILE=REPO/"tools"/"public-audits"/"phase03_v67_output_concentration_001.py"
spec=importlib.util.spec_from_file_location("v67_concentration_unit",FILE)
if spec is None or spec.loader is None:
    raise RuntimeError("V67 audit cannot be loaded")
A=importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


class V67ConcentrationTests(unittest.TestCase):
    def test_rank_stable_tie_breaker_matches_argmax(self):
        values=torch.zeros((3,1024),dtype=torch.float32)
        values[0,3]=5.0
        values[0,259]=5.0
        values[1,3]=3.0
        values[1,259]=4.0
        values[2,259]=4.0
        values[2,258]=4.0
        ranks=A.stable_true_ranks(values,torch.tensor([259,259,259]))
        self.assertEqual(ranks.tolist(),[2,1,2])
        self.assertEqual(values.argmax(1).tolist(),[3,259,258])

    def test_rank_topk_uses_entire_vocabulary(self):
        values=torch.zeros((1,1024),dtype=torch.float32)
        values[0,0]=10.0
        values[0,100]=9.0
        values[0,259]=8.0
        ranks=A.stable_true_ranks(values,torch.tensor([259]))
        self.assertEqual(ranks.tolist(),[3])

    def test_invalid_rank_inputs_fail_closed(self):
        with self.assertRaises(RuntimeError):
            A.stable_true_ranks(torch.zeros((2,1024)),torch.tensor([259]))
        with self.assertRaises(RuntimeError):
            A.stable_true_ranks(torch.zeros((1,1024)),torch.tensor([2]))
        with self.assertRaises(RuntimeError):
            A.stable_true_ranks(torch.zeros((1,512)),torch.tensor([259]))

    def fixture(self):
        stats=A.empty_stats()
        stats["val_tokens"]=9206
        stats["lexical"]=9170
        stats["eos_top1"]=14
        stats["val_loss_sum"]=4.733*9206
        stats["predictions"]=Counter({3:4000,259:3000,2:2170})
        stats["gold"]=Counter({3:4876,259:4294})
        stats["ranks"]={
            "B":[1]*2500+[2]*1000+[11]*700+[101]*676,
            "M":[1]*150+[5]*400+[10]*600+[51]*3144
        }
        stats["conf"]={
            ("B","B"):4438,("B","M"):399,("B","S"):39,
            ("M","B"):2254,("M","M"):2029,("M","S"):11,
        }
        refs={"A":{"V66_BIAS_VAL_CE_X1000":4733}}
        for (gold,pred),count in stats["conf"].items():
            refs["A"][f"V66_BIAS_CONF_{gold}_P{pred}"]=count
        return stats,refs

    def test_numeric_report_has_exactly_30_metrics(self):
        stats,refs=self.fixture()
        output=A.build_report(stats,refs,64)
        self.assertEqual(len(output),30)
        self.assertEqual(output["V67_CONC_PASS"],1)
        self.assertEqual(output["V67_CONC_BLIND_ACCESS"],0)
        self.assertEqual(output["TRAINING_STARTED"],0)
        self.assertEqual(output["V67_CONC_PRED_DISTINCT"],3)
        self.assertEqual(output["V67_CONC_GOLD_DISTINCT"],2)
        self.assertEqual(output["V67_CONC_PRED_BYTE_DISTINCT"],1)
        self.assertEqual(output["V67_CONC_PRED_MERGE_DISTINCT"],1)
        self.assertEqual(output["V67_CONC_VAL_LEXICAL"],9170)
        self.assertTrue(all(type(x) is int and x>=0 for x in output.values()))

    def test_monotonic_prediction_concentration(self):
        stats,refs=self.fixture()
        out=A.build_report(stats,refs,56)
        values=[out[f"V67_CONC_TOP{k}_SHARE_BP"] for k in (1,5,10,20)]
        self.assertTrue(all(a<=b for a,b in zip(values,values[1:])))
        self.assertEqual(values[-1],10000)
        self.assertEqual(out["V67_CONC_BYTE_GOLD_MEDIAN_RANK"],1)
        self.assertEqual(out["V67_CONC_MERGE_GOLD_MEDIAN_RANK"],51)

    def test_reject_confusion_mismatch(self):
        stats,refs=self.fixture()
        stats["conf"][("M","B")]-=1
        with self.assertRaises(RuntimeError):
            A.build_report(stats,refs,56)

    def test_reject_loss_mismatch(self):
        stats,refs=self.fixture()
        stats["val_loss_sum"]+=100
        with self.assertRaises(RuntimeError):
            A.build_report(stats,refs,56)

    def test_no_training_or_blind_paths(self):
        source=FILE.read_text(encoding="utf-8")
        self.assertNotIn("optimizer.step(",source)
        self.assertNotIn("torch.save(",source)
        self.assertNotIn("build_blind",source)
        self.assertIn("helper.preflight()",source)


if __name__=="__main__":
    unittest.main()
