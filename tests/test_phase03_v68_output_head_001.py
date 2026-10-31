"""V68 CPU-only output-head audit sanity tests."""
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
SOURCE=REPO/"tools"/"public-audits"/"phase03_v68_output_head_001.py"
spec=importlib.util.spec_from_file_location("v68_head_audit",SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot import V68 audit")
A=importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


class V68OutputHeadTests(unittest.TestCase):
    def fixture(self):
        norms=torch.ones(1024,dtype=torch.float32)
        norms[0]=0
        stats={
            "tokens":9206,"lexical":9170,"eos":14,
            "nll_sum":4733*9206/1000,
            "pred":Counter({3:6656,4:36,259:2428,2:50}),
            "gap":[1.0]*9170,
            "gold_deficit":[3.0]*9170,
            "byte_deficit":[2.0]*4876,
            "merge_deficit":[4.0]*4294,
            "pred_norm":[1.0]*9170,
            "gold_norm":[1.0]*9170,
        }
        prior={"metrics":{
            "V67_CONC_PRED_DISTINCT":4,
            "V67_CONC_VAL_LEXICAL":9170,
            "V67_CONC_TOP1_SHARE_BP":round(6656*10000/9170),
            "V67_CONC_VAL_CE_X1000":4733,
        }}
        return stats,norms,prior

    def test_exactly_30_integer_metrics(self):
        stats,norms,prior=self.fixture()
        out=A.summarize_numeric(stats,norms,61,prior)
        self.assertEqual(len(out),30)
        self.assertTrue(all(type(x) is int and x>=0 for x in out.values()))
        self.assertEqual(out["V68_HEAD_TIED_WEIGHTS"],1)
        self.assertEqual(out["V68_HEAD_HAS_BIAS"],0)
        self.assertEqual(out["V68_HEAD_NORM_PAD_X1000"],0)
        self.assertNotIn("V68_HEAD_NORM_SPECIAL_MEAN_X1000",out)
        self.assertEqual(out["V68_HEAD_PRED_BYTE_COUNT"],6692)
        self.assertEqual(out["V68_HEAD_PRED_MERGE_COUNT"],2428)
        self.assertEqual(out["V68_HEAD_PRED_SPECIAL_COUNT"],50)
        self.assertEqual(out["V68_HEAD_GOLD_MERGE_DEFICIT_X1000"],4000)
        self.assertEqual(out["TRAINING_STARTED"],0)

    def test_reject_incorrect_argmax_distribution(self):
        stats,norms,prior=self.fixture()
        stats["pred"][3]-=1
        stats["pred"][259]+=1
        with self.assertRaises(RuntimeError):
            A.summarize_numeric(stats,norms,61,prior)

    def test_reject_nonfinite_logit_margins(self):
        stats,norms,prior=self.fixture()
        stats["gap"][0]=float("nan")
        with self.assertRaises(RuntimeError):
            A.summarize_numeric(stats,norms,61,prior)

    def test_reject_ce_regression(self):
        stats,norms,prior=self.fixture()
        stats["nll_sum"]+=100
        with self.assertRaises(RuntimeError):
            A.summarize_numeric(stats,norms,61,prior)

    def test_detect_tied_and_unbiased_output_head(self):
        class M(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.token_embedding=torch.nn.Embedding(1024,8)
                self.lm_head=torch.nn.Linear(8,1024,bias=False)
                self.lm_head.weight=self.token_embedding.weight
                with torch.no_grad():
                    self.token_embedding.weight[0].zero_()
        m=M()
        norms=A.summarize_head(m)
        self.assertEqual(norms.numel(),1024)
        self.assertEqual(norms[0].item(),0)
        m.lm_head.weight=torch.nn.Parameter(m.lm_head.weight.clone())
        with self.assertRaises(RuntimeError):
            A.summarize_head(m)

    def test_nonzero_pad_row_is_accepted_for_weight_tying(self):
        class M(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.token_embedding=torch.nn.Embedding(1024,8,padding_idx=0)
                self.lm_head=torch.nn.Linear(8,1024,bias=False)
                self.lm_head.weight=self.token_embedding.weight
                # Simulate an update through the shared output projection.
                with torch.no_grad():
                    self.token_embedding.weight[0].fill_(0.5)

        norms=A.summarize_head(M())
        self.assertGreater(norms[0].item(),0)
        stats,_,prior=self.fixture()
        result=A.summarize_numeric(stats,norms,61,prior)
        self.assertEqual(result["V68_HEAD_NORM_PAD_X1000"],round(norms[0].item()*1000))
        self.assertEqual(len(result),30)

    def test_head_with_nonfinite_pad_row_is_rejected(self):
        class M(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.token_embedding=torch.nn.Embedding(1024,8,padding_idx=0)
                self.lm_head=torch.nn.Linear(8,1024,bias=False)
                self.lm_head.weight=self.token_embedding.weight
                with torch.no_grad():
                    self.token_embedding.weight[0].fill_(float("nan"))

        with self.assertRaisesRegex(RuntimeError,"row norms invalid"):
            A.summarize_head(M())

    def test_head_with_bias_is_rejected(self):
        class M(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.token_embedding=torch.nn.Embedding(1024,8)
                self.lm_head=torch.nn.Linear(8,1024,bias=True)
                self.lm_head.weight=self.token_embedding.weight
        with self.assertRaises(RuntimeError):
            A.summarize_head(M())

    def test_reject_incomplete_eos(self):
        stats,norms,prior=self.fixture()
        stats["eos"]=13
        with self.assertRaises(RuntimeError):
            A.summarize_numeric(stats,norms,61,prior)

    def test_static_no_optimizer_or_blind(self):
        c=SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("optimizer.step(",c)
        self.assertNotIn("torch.save(",c)
        self.assertNotIn("build_blind",c)
        self.assertIn("helper.preflight()",c)


if __name__=="__main__":
    unittest.main()
