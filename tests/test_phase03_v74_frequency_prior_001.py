"""Offline CPU-only V74 frequency-prior schema and provenance regression."""
from __future__ import annotations

import ast
import importlib.util
import unittest
from collections import Counter
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "v74_frequency_prior.py"
spec = importlib.util.spec_from_file_location("v74_frequency_test_source", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V74 reviewed source unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def fake_aggregate():
    bins = {"F0": 3, "F1_9": 7, "F10_99": 300, "F100P": 8860}
    hit_counts = {
        "ORIG": (10, 20, 30, 40),
        "CENTER": (20, 30, 40, 50),
        "PC1": (30, 40, 50, 60),
        "UNIGRAM": (40, 50, 60, 70),
    }
    outcomes = {}
    for mode in V.MODES:
        strata = dict(zip(V.BINS, hit_counts[mode]))
        correct = sum(strata.values())
        outcomes[mode] = {
            "STRATA": strata,
            "CORRECT": correct,
            "BYTE_CORRECT": correct // 2,
            "MERGE_CORRECT": correct - correct // 2,
            "DISTINCT": 1 if mode == "UNIGRAM" else 4,
            "TOP1_SHARE_BP": 10000 if mode == "UNIGRAM" else 5000,
        }
    v72 = {
        f"V72_GEOM_ORIG_{key}": outcomes["ORIG"][key]
        for key in ("CORRECT", "DISTINCT", "TOP1_SHARE_BP")
    }
    v73 = {}
    for mode, prefix in (("CENTER", "V73_AXIS_CENTER"),
                         ("PC1", "V73_AXIS_PC1_ONLY")):
        v73.update({
            f"{prefix}_{key}": outcomes[mode][key]
            for key in ("CORRECT", "DISTINCT", "TOP1_SHARE_BP")
        })
    # Exactly 891 token types, 294726 training lexical occurrences.
    frequency = Counter({token: 331 for token in range(3, 894)})
    frequency[3] -= 195
    return outcomes, bins, frequency, v72, v73


class V74FrequencyTests(unittest.TestCase):
    def test_schema_has_two_exactly_thirty_field_reports(self):
        self.assertEqual(len(V.core_keys()), 30)
        self.assertEqual(len(V.strata_keys()), 30)
        self.assertEqual(V.core_keys() & V.strata_keys(), set(V.SAFE))
        self.assertEqual(len(V.core_keys() | V.strata_keys()), 57)

    def test_frequency_thresholds_fixed(self):
        mapping = {
            0: "F0", 1: "F1_9", 9: "F1_9", 10: "F10_99",
            99: "F10_99", 100: "F100P", 100000: "F100P",
        }
        for value, expected in mapping.items():
            with self.subTest(value=value):
                self.assertEqual(V.frequency_bin(value), expected)
        for value in (-1, 1.0, None, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                V.frequency_bin(value)

    def test_unigram_ties_resolve_by_lowest_train_id(self):
        freq = Counter({300: 11, 4: 11, 3: 10})
        self.assertEqual(V.most_frequent(freq), 4)
        self.assertEqual(V.most_frequent(Counter({3: 12, 4: 11})), 3)

    def test_unigram_rejects_invalid_train_inventory(self):
        for freq in (Counter(), Counter({0: 99}), Counter({1024: 99}),
                     Counter({3: 0}), Counter({4: -1})):
            with self.subTest(freq=freq), self.assertRaises(ValueError):
                V.most_frequent(freq)

    def test_report_aggregate_reconciliation(self):
        agg, bins, freq, v72, v73 = fake_aggregate()
        core, strata = V.build_reports(agg, bins, 120, 20, freq, v72, v73)
        self.assertEqual(set(core), V.core_keys())
        self.assertEqual(set(strata), V.strata_keys())
        self.assertEqual(len(core), len(strata))
        self.assertEqual(core["V74_CORE_VAL_LEXICAL"], 9170)
        self.assertEqual(strata["V74_STRATA_TRAIN_LEXICAL"], 294726)
        self.assertEqual(strata["V74_STRATA_TRAIN_TYPES"], 891)
        self.assertEqual(strata["V74_STRATA_PC1_UNIGRAM_AGREE"], 120)
        self.assertEqual(strata["V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT"], 20)
        self.assertEqual(core["TRAINING_STARTED"], 0)
        self.assertEqual(core["V74_CORE_BLIND_ACCESS"], 0)
        self.assertEqual(strata["V74_STRATA_BLIND_ACCESS"], 0)

    def test_fail_closed_for_mutated_original_reference(self):
        agg, bins, freq, v72, v73 = fake_aggregate()
        v72["V72_GEOM_ORIG_CORRECT"] += 1
        with self.assertRaises(RuntimeError):
            V.build_reports(agg, bins, 120, 20, freq, v72, v73)

    def test_fail_closed_for_invalid_overlap_and_train(self):
        agg, bins, freq, v72, v73 = fake_aggregate()
        with self.assertRaises(RuntimeError):
            V.build_reports(agg, bins, 100, 110, freq, v72, v73)
        with self.assertRaises(RuntimeError):
            V.build_reports(agg, bins, 120, 20, Counter({3: 5}), v72, v73)

    def test_fail_closed_for_train_binning_mismatch(self):
        agg, bins, freq, v72, v73 = fake_aggregate()
        bins["F0"] += 1
        with self.assertRaises(RuntimeError):
            V.build_reports(agg, bins, 120, 20, freq, v72, v73)

    def test_all_keys_registered_in_static_gogit_allowlist(self):
        tree = ast.parse((ROOT / "tools" / "gogit_public.py").read_text())
        keys = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "METRIC_KEYS"
                for target in node.targets
            ):
                keys = ast.literal_eval(node.value)
                break
        self.assertIsInstance(keys, set)
        self.assertTrue((V.core_keys() | V.strata_keys()) <= keys)

    def test_cpu_projection_diagnostics_no_mutation(self):
        h = torch.zeros((V.LEXICAL, 128), dtype=torch.float32)
        h[:, 0] = 1.0
        h[:, 1] = 2.0
        gold = torch.tensor([3] * V.BYTE + [259] * V.MERGED, dtype=torch.long)
        w = torch.zeros((V.T.VOCAB_SIZE, 128), dtype=torch.float32)
        w[3, 0] = 3.0
        w[259, 1] = 1.0
        original = (h.clone(), w.clone())
        basis = torch.zeros((128, 2), dtype=torch.float32)
        basis[1, 0] = 1.0
        basis[0, 1] = 1.0
        freq = Counter({3: 100, 259: 20})
        agg, bins, agree, shared = V.score(
            h, gold, w, basis, torch.zeros(128), freq
        )
        self.assertEqual(sum(bins.values()), 9170)
        self.assertEqual(bins["F0"], 0)
        self.assertEqual(bins["F10_99"], 4294)
        self.assertEqual(bins["F100P"], 4876)
        self.assertEqual(agg["UNIGRAM"]["DISTINCT"], 1)
        self.assertEqual(agg["UNIGRAM"]["CORRECT"], 4876)
        self.assertTrue(0 <= shared <= agree <= 9170)
        self.assertTrue(torch.equal(h, original[0]))
        self.assertTrue(torch.equal(w, original[1]))

    def test_never_train_or_read_blind(self):
        source = SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "optimizer.step(", "torch.save(", "load_blind(",
            "build_blind(", "torch.load(",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("torch.inference_mode()", source)
        self.assertIn("V74 full immutable V73 metric replay mismatch", source)


if __name__ == "__main__":
    unittest.main()
