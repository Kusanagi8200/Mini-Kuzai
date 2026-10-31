"""V66 CPU-only safeguards, matrix accounting, probability mass and strata."""
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
FILE=REPO/"tools"/"public-audits"/"phase03_v66_token_prediction_bias_001.py"
spec=importlib.util.spec_from_file_location("v66_bias_unit_module",FILE)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot import V66 audit")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


class V66BiasTests(unittest.TestCase):
    def test_frequency_strata_all_boundaries(self):
        for token,expected in (
            (3,"B"),(258,"B"),(259,"M"),(1023,"M")
        ):
            with self.subTest(token=token):
                self.assertEqual(D.frequency_bucket(token,0),expected+"0")
                self.assertEqual(D.frequency_bucket(token,1),expected+"1_9")
                self.assertEqual(D.frequency_bucket(token,9),expected+"1_9")
                self.assertEqual(D.frequency_bucket(token,10),expected+"10_99")
                self.assertEqual(D.frequency_bucket(token,99),expected+"10_99")
                self.assertEqual(D.frequency_bucket(token,100),expected+"100_999")
                self.assertEqual(D.frequency_bucket(token,999),expected+"100_999")
                self.assertEqual(D.frequency_bucket(token,1000),expected+"1000P")

    def test_bad_ids_and_frequencies_fail_closed(self):
        for token,count in ((-1,0),(0,1),(1,1),(2,1),(1024,1),(3,-1)):
            with self.subTest(token=token,count=count):
                with self.assertRaises(ValueError):
                    D.frequency_bucket(token,count)
        for token in (-1,1024):
            with self.assertRaises(ValueError):
                D.predicted_kind(token)

    def test_argmax_categories_include_special(self):
        self.assertEqual(D.predicted_kind(0),"S")
        self.assertEqual(D.predicted_kind(2),"S")
        self.assertEqual(D.predicted_kind(3),"B")
        self.assertEqual(D.predicted_kind(258),"B")
        self.assertEqual(D.predicted_kind(259),"M")
        self.assertEqual(D.predicted_kind(1023),"M")

    def test_cpu_probability_accounting_and_confusion(self):
        stats=D.blank_result()
        gold=torch.tensor([3,259],dtype=torch.long)
        pred=torch.tensor([259,2],dtype=torch.long)
        nll=torch.tensor([2.0,3.0],dtype=torch.float32)
        probs=torch.zeros((2,1024),dtype=torch.float32)
        probs[0,2]=0.1
        probs[0,3]=0.2
        probs[0,259]=0.7
        probs[1,2]=0.6
        probs[1,3]=0.1
        probs[1,259]=0.3
        D.consume_predictions(stats,gold,pred,nll,probs,Counter({3:500,259:20}))
        self.assertEqual(stats["lexical"],2)
        self.assertEqual(stats["conf"][("B","M")],1)
        self.assertEqual(stats["conf"][("M","S")],1)
        self.assertEqual(stats["bins"]["B100_999"]["count"],1)
        self.assertEqual(stats["bins"]["M10_99"]["count"],1)
        self.assertAlmostEqual(stats["prob"][("B","B")],0.2,places=5)
        self.assertAlmostEqual(stats["prob"][("M","S")],0.6,places=5)

    def test_reject_unnormalized_mass(self):
        stats=D.blank_result()
        bad=torch.zeros((1,1024),dtype=torch.float32)
        with self.assertRaises(RuntimeError):
            D.consume_predictions(
                stats,torch.tensor([3]),torch.tensor([3]),
                torch.tensor([1.0]),bad,Counter({3:1000})
            )

    def fixture(self):
        stats=D.blank_result()
        values={
            "B0":3,"B1_9":0,"B10_99":800,
            "B100_999":2200,"B1000P":1873,
            "M0":0,"M1_9":7,"M10_99":200,
            "M100_999":2000,"M1000P":2087,
        }
        for key,n in values.items():
            stats["bins"][key]={"count":n,"correct":n//3,"nll":n*4.0}
        stats["total_targets"]=9206
        stats["lexical"]=9170
        stats["eos"]=14
        stats["ce_x1000"]=4733
        stats["gold"]={"B":4876,"M":4294}
        stats["conf"]={
            ("B","B"):3000,("B","M"):1800,("B","S"):76,
            ("M","B"):2200,("M","M"):1000,("M","S"):1094
        }
        # Each gold class's integrated output mass must sum to its count.
        stats["prob"]={
            ("B","B"):2000.0,("B","M"):2000.0,("B","S"):876.0,
            ("M","B"):1000.0,("M","M"):2000.0,("M","S"):1294.0
        }
        train=Counter({i:1 for i in range(3,894)})
        train[3]+=294726-891
        prior={"metrics":{
            "V65_FREQ_TRAIN_LEXICAL":294726,
            "V65_FREQ_TRAIN_TYPES":891,
            "V65_FREQ_VAL_CE_X1000":4733,
            "V65_FREQ_B0_COUNT":3,"V65_FREQ_B1_9_COUNT":0,
            "V65_FREQ_B10P_COUNT":4873,
            "V65_FREQ_M0_COUNT":0,"V65_FREQ_M1_9_COUNT":7,
            "V65_FREQ_M10P_COUNT":4287,
        }}
        return stats,train,prior

    def test_report_numerical_complete_and_normalized(self):
        stats,train,prior=self.fixture()
        report=D.build_report(stats,train,56,prior)
        self.assertEqual(len(report),57)
        self.assertEqual(report["V66_BIAS_BYTE_TARGETS"],4876)
        self.assertEqual(report["V66_BIAS_MERGE_TARGETS"],4294)
        self.assertEqual(report["V66_BIAS_CONF_B_PM"],1800)
        self.assertEqual(report["V66_BIAS_CONF_M_PS"],1094)
        self.assertEqual(report["V66_BIAS_MASS_B_B_BP"],round(2000*10000/4876))
        self.assertEqual(report["V66_BIAS_B0_COUNT"],3)
        self.assertEqual(report["V66_BIAS_M1000P_COUNT"],2087)
        self.assertEqual(report["V66_BIAS_M0_TOP1_BP"],0)
        self.assertEqual(report["TRAINING_STARTED"],0)
        self.assertEqual(report["SEMANTIC_VALIDATION_COMPLETE"],0)
        self.assertTrue(all(type(x) is int and x>=0 for x in report.values()))

    def test_report_rejects_bad_matrix(self):
        stats,train,prior=self.fixture()
        stats["conf"][("M","B")]-=1
        with self.assertRaises(RuntimeError):
            D.build_report(stats,train,56,prior)

    def test_report_rejects_v65_frequency_mismatch(self):
        stats,train,prior=self.fixture()
        stats["bins"]["B10_99"]["count"]-=1
        with self.assertRaises(RuntimeError):
            D.build_report(stats,train,56,prior)


if __name__=="__main__":
    unittest.main()
