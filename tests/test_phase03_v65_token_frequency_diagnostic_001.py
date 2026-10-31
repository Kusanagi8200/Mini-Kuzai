"""CPU-only V65 frozen-frequency binning and numeric-only report tests."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
SOURCE=REPO/"tools"/"public-audits"/"phase03_v65_token_frequency_diagnostic_001.py"
spec=importlib.util.spec_from_file_location("v65_frequency_test_module",SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V65 frequency audit module unavailable")
A=importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


@dataclass
class FakeSegment:
    token_ids:tuple[int,...]


class V65FrequencyDiagnosticTests(unittest.TestCase):
    def test_predeclared_token_frequency_bins(self):
        self.assertEqual(A.frequency_bin(3,0),"B0")
        self.assertEqual(A.frequency_bin(258,1),"B1_9")
        self.assertEqual(A.frequency_bin(3,9),"B1_9")
        self.assertEqual(A.frequency_bin(258,10),"B10P")
        self.assertEqual(A.frequency_bin(259,0),"M0")
        self.assertEqual(A.frequency_bin(259,9),"M1_9")
        self.assertEqual(A.frequency_bin(1023,10),"M10P")

    def test_binning_rejects_special_or_invalid_tokens(self):
        for token,seen in ((0,0),(1,1),(2,0),(1024,1),(259,-1)):
            with self.subTest(token=token,seen=seen):
                with self.assertRaises(ValueError):
                    A.frequency_bin(token,seen)

    def test_all_frozen_train_segments_counted(self):
        lengths=(100,100,100,45)
        self.assertEqual(len(A.T.STREAMS),len(lengths))
        body=tuple(3+(i%500) for i in range(310))
        streams={
            name:[FakeSegment((A.T.BOS_ID,)+body+(A.T.EOS_ID,)) for _ in range(n)]
            for name,n in zip(A.T.STREAMS,lengths)
        }
        freq=A.count_training_tokens(streams)
        self.assertEqual(sum(freq.values()),345*310)
        self.assertEqual(len(freq),310)
        self.assertNotIn(A.T.EOS_ID,freq)

    def test_invalid_train_body_fails_closed(self):
        streams={stream:[] for stream in A.T.STREAMS}
        streams[A.T.STREAMS[0]]=[FakeSegment((1,0,2))]
        with self.assertRaises(RuntimeError):
            A.count_training_tokens(streams)

    def test_numeric_metrics_full_coverage(self):
        groups=A.empty_groups()
        groups["B10P"]={"count":2,"correct":1,"loss":4.0}
        groups["M1_9"]={"count":3,"correct":2,"loss":9.0}
        groups["M0"]={"count":1,"correct":0,"loss":5.0}
        metrics=A.numerical_report(Counter({3:100,259:5}),groups,6,4733,14,128)
        self.assertEqual(len(metrics),30)
        self.assertEqual(metrics["V65_FREQ_B10P_COUNT"],2)
        self.assertEqual(metrics["V65_FREQ_B10P_TOP1_BP"],5000)
        self.assertEqual(metrics["V65_FREQ_B10P_NLL_X1000"],2000)
        self.assertEqual(metrics["V65_FREQ_M0_COUNT"],1)
        self.assertEqual(metrics["V65_FREQ_M0_NLL_X1000"],5000)
        self.assertEqual(metrics["V65_FREQ_B0_COUNT"],0)
        self.assertEqual(metrics["V65_FREQ_B0_NLL_X1000"],0)
        self.assertEqual(metrics["V65_FREQ_VAL_LEXICAL"],6)
        self.assertEqual(metrics["TRAINING_AUTHORIZED"],0)
        self.assertEqual(metrics["TRAINING_STARTED"],0)
        self.assertEqual(metrics["SEMANTIC_VALIDATION_COMPLETE"],0)
        self.assertEqual(metrics["V65_FREQ_BLIND_ACCESS"],0)
        self.assertTrue(all(type(value) is int and value>=0 for value in metrics.values()))

    def test_bucket_counts_must_cover_every_lexical_target(self):
        with self.assertRaises(RuntimeError):
            A.numerical_report(Counter({3:100}),A.empty_groups(),2,4733,14,128)


if __name__=="__main__":
    unittest.main()
