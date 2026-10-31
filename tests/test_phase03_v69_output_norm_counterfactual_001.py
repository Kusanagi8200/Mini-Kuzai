"""V69 CPU-only causal intervention tests, frozen reference gates and 30-field cap."""
from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path

import torch

REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
SOURCE=REPO/"tools"/"public-audits"/"phase03_v69_output_norm_counterfactual_001.py"
spec=importlib.util.spec_from_file_location("v69_counterfactual_test",SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot load V69 reviewed audit")
V=importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def example_stats():
    return {
        "CE_X1000":4733,"PRED_DISTINCT":4,"TOP1_SHARE_BP":7258,
        "BYTE_SHARE_BP":round(6692*10000/9170),
        "MERGE_SHARE_BP":round(2428*10000/9170),
        "MERGE_TOP1_BP":326,"MERGE_TOP5_BP":685,
        "EOS_TOP1":14,"LEX_TOP1_BP":2895,
    }


def example_reference():
    return (
        {"V68_HEAD_CE_X1000":4733,"V68_HEAD_PRED_DISTINCT":4,
         "V68_HEAD_TOP1_SHARE_BP":7258,"V68_HEAD_EOS_TOP1":14},
        {"V67_CONC_MERGE_GOLD_TOP1_BP":326,"V67_CONC_MERGE_GOLD_TOP5_BP":685},
    )


class V69CounterfactualTests(unittest.TestCase):
    def test_frozen_original_alpha_zero_preserves_original_weights(self):
        w=torch.randn(1024,8)
        w[0].fill_(0.1)
        before=w.clone()
        x=V.equalize_rows(w,0.0)
        self.assertTrue(torch.allclose(x,before,rtol=1e-6,atol=1e-6))
        self.assertTrue(torch.equal(w,before))

    def test_full_equalization_has_constant_nonzero_norm(self):
        w=torch.ones((1024,8))
        w[3:,:]*=3.0
        w[0].zero_()
        original=w.clone()
        full=V.equalize_rows(w,1.0)
        half=V.equalize_rows(w,0.5)
        norms=torch.linalg.vector_norm(full[1:],dim=-1)
        self.assertLess((norms.max()-norms.min()).item(),1e-5)
        self.assertTrue(torch.equal(full[0],torch.zeros_like(full[0])))
        self.assertTrue(torch.equal(w,original))
        self.assertGreater(torch.linalg.vector_norm(half[3]).item(),
                           torch.linalg.vector_norm(half[1]).item())
        self.assertLess(torch.linalg.vector_norm(half[3]).item(),
                        torch.linalg.vector_norm(w[3]).item())

    def test_only_predeclared_norm_strengths_accepted(self):
        w=torch.rand(1024,4)
        for alpha in (-1,0.2,0.25,2,"1"):
            with self.subTest(alpha=alpha):
                with self.assertRaises(RuntimeError):
                    V.equalize_rows(w,alpha)

    def test_nonfinite_weights_rejected(self):
        w=torch.rand(1024,8)
        w[0,0]=float("nan")
        with self.assertRaises(RuntimeError):
            V.equalize_rows(w,1.0)

    def test_numeric_report_exactly_30_numeric_metrics(self):
        a=example_stats()
        variants={"BASE":a,"HALF":{**a,"PRED_DISTINCT":7},
                  "FULL":{**a,"PRED_DISTINCT":20}}
        report=V.numeric_report(variants,example_reference())
        self.assertEqual(len(report),30)
        self.assertEqual(report["V69_NORM_PASS"],1)
        self.assertEqual(report["V69_NORM_BLIND_ACCESS"],0)
        self.assertEqual(report["TRAINING_STARTED"],0)
        self.assertEqual(report["V69_NORM_BASE_MERGE_TOP5_BP"],685)
        self.assertEqual(report["V69_NORM_HALF_PRED_DISTINCT"],7)
        self.assertEqual(report["V69_NORM_FULL_PRED_DISTINCT"],20)
        self.assertEqual(sum(k.startswith("V69_NORM_") for k in report),27)
        self.assertTrue(all(type(v) is int for v in report.values()))

    def test_changed_baseline_ce_rejected(self):
        a=example_stats()
        a["CE_X1000"]=5000
        with self.assertRaises(RuntimeError):
            V.numeric_report({"BASE":a,"HALF":example_stats(),"FULL":example_stats()},
                             example_reference())

    def test_changed_v67_bpe_top5_rejected(self):
        a=example_stats()
        a["MERGE_TOP5_BP"]=999
        with self.assertRaises(RuntimeError):
            V.numeric_report({"BASE":a,"HALF":example_stats(),"FULL":example_stats()},
                             example_reference())

    def test_refuse_missing_counterfactual(self):
        a=example_stats()
        with self.assertRaises(RuntimeError):
            V.numeric_report({"BASE":a,"HALF":a},example_reference())

    def test_update_stats_uses_full_vocabulary_and_stable_rank(self):
        logits=torch.full((1,3,1024),-5.0)
        logits[0,0,3]=6.0
        logits[0,1,259]=6.0
        logits[0,2,2]=6.0
        true=torch.tensor([[3,259,2]])
        mask=torch.ones_like(true,dtype=torch.bool)
        stats=V.empty()
        # CPU ranker with the same lower-ID wins equal-logit rule.
        def ranker(z,t):
            gold=z.gather(1,t[:,None])
            ids=torch.arange(z.shape[1])[None,:]
            return 1+(z>gold).sum(1)+((z==gold)&(ids<t[:,None])).sum(1)
        V.update_stats(stats,logits,true,mask,[(0,2)],ranker)
        self.assertEqual(stats["tokens"],3)
        self.assertEqual(stats["lexical"],2)
        self.assertEqual(stats["eos"],1)
        self.assertEqual(stats["merge_top1"],1)
        self.assertEqual(stats["merge_top5"],1)

    def test_audit_has_no_training_or_checkpoint_write(self):
        source=SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("optimizer.step(",source)
        self.assertNotIn("torch.save(",source)
        self.assertNotIn("build_blind",source)
        self.assertNotIn("load_blind",source)
        self.assertIn("model.lm_head.register_forward_pre_hook(tap)",source)
        self.assertIn("torch.equal(model.lm_head.weight.detach().float(),weights_before)",source)


if __name__=="__main__":
    unittest.main()
