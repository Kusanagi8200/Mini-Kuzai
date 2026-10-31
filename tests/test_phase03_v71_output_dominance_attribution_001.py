"""V71 frozen attribution: exact schema, V70 replay and synthetic CPU tests."""
from __future__ import annotations

import importlib.util
import math
import sys
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SOURCE = ROOT / "tools" / "public-audits" / (
    "phase03_v71_output_dominance_attribution_001.py")
spec = importlib.util.spec_from_file_location("v71_attribution", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V71 source not importable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def reference():
    stats = V.new_attribution()
    stats.update({
        "lexical": 9170, "byte": 4876, "merge": 4294,
        "switch": 800, "switch_byte": 400, "switch_merge": 400,
        "both": 900, "orig_only": 100, "full_only": 101, "neither": 8069,
        "orig_margin": 9500.0, "full_margin": 8100.0,
        "orig_byte_def": 5000.0, "orig_merge_def": 13000.0,
        "full_byte_def": 4000.0, "full_merge_def": 18000.0,
        "winner_norm": 3300.0, "gold_norm": 2600.0,
        "cos_win": 1200.0, "cos_gold": 300.0,
    })
    original = {
        "CE_X1000": 4732, "PRED_DISTINCT": 5, "TOP1_SHARE_BP": 7255,
        "MERGE_TOP1_BP": 326, "MERGE_TOP5_BP": 685, "EOS_TOP1": 14,
    }
    full = {
        "CE_X1000": 5048, "PRED_DISTINCT": 7, "TOP1_SHARE_BP": 6957,
        "MERGE_TOP1_BP": 335, "MERGE_TOP5_BP": 771, "EOS_TOP1": 24,
    }
    prior = {
        "V70_CTRL_" + mode + "_" + field: val
        for mode, datum in (("FP32", original), ("FULL", full))
        for field, val in datum.items()
    }
    return stats, original, full, prior


class V71AttributionTests(unittest.TestCase):
    def test_frozen_thirty_field_schema(self):
        result = V.build_report(*reference())
        self.assertEqual(len(result), 30)
        self.assertEqual(
            {key for key in result if key.startswith("V71_ATTR_")},
            {"V71_ATTR_" + name for name in V.FIELDS})
        self.assertEqual(result["V71_ATTR_PASS"], 1)
        self.assertEqual(result["V71_ATTR_BLIND_ACCESS"], 0)
        self.assertEqual(result["V71_ATTR_SWITCH_TOTAL"], 800)
        self.assertEqual(result["V71_ATTR_CORRECT_NEITHER"], 8069)
        self.assertEqual(result["V71_ATTR_ORIG_CE_X1000"], 4732)
        self.assertEqual(result["V71_ATTR_FULL_CE_X1000"], 5048)
        self.assertTrue(all(type(v) is int and v >= 0 for v in result.values()))

    def test_v70_baselines_are_exact(self):
        stats, original, full, prior = reference()
        for name, change in (("CE_X1000", 1), ("PRED_DISTINCT", 1),
                             ("EOS_TOP1", -1), ("MERGE_TOP5_BP", 1)):
            updated = dict(original)
            updated[name] += change
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                V.build_report(stats, updated, full, prior)

    def test_gold_inventory_and_switch_invariants(self):
        for field, amount in (
            ("byte", -1), ("switch_byte", 1), ("neither", -1),
            ("switch", -700), ("gold_norm", -2600.0),
        ):
            stats, original, full, prior = reference()
            stats[field] += amount
            with self.subTest(field=field), self.assertRaises(RuntimeError):
                V.build_report(stats, original, full, prior)

    def test_nonfinite_rejected(self):
        stats, original, full, prior = reference()
        stats["cos_gold"] = math.nan
        with self.assertRaises(RuntimeError):
            V.build_report(stats, original, full, prior)

    def test_synthetic_position_attribution(self):
        stats = V.new_attribution()
        weights = torch.zeros((1024, 3), dtype=torch.float32)
        weights[3] = torch.tensor([2.0, 0.0, 0.0])
        weights[4] = torch.tensor([0.0, 2.0, 0.0])
        weights[259] = torch.tensor([1.0, 1.0, 0.0])
        h = torch.tensor([[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]])
        gold = torch.tensor([[3, 259]])
        lexical = torch.ones_like(gold, dtype=torch.bool)
        original = torch.zeros((1, 2, 1024), dtype=torch.float32)
        full = torch.zeros_like(original)
        original[0, 0, 3], original[0, 0, 4] = 2.0, 1.0
        full[0, 0, 3], full[0, 0, 4] = 1.0, 2.0
        original[0, 1, 4], original[0, 1, 259] = 2.0, 1.0
        full[0, 1, 259], full[0, 1, 4] = 3.0, 2.0
        V.attribute_batch(stats, h, original, full, gold, lexical, weights)
        self.assertEqual(stats["lexical"], 2)
        self.assertEqual(stats["byte"], 1)
        self.assertEqual(stats["merge"], 1)
        self.assertEqual(stats["switch"], 2)
        self.assertEqual(stats["switch_byte"], 1)
        self.assertEqual(stats["switch_merge"], 1)
        self.assertEqual(stats["orig_only"], 1)
        self.assertEqual(stats["full_only"], 1)
        self.assertEqual(stats["both"], 0)
        self.assertEqual(stats["neither"], 0)

    def test_read_only_private_split_guards(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("optimizer.step(", source)
        self.assertNotIn("torch.save(", source)
        self.assertNotIn("load_blind", source)
        self.assertNotIn("build_blind", source)
        self.assertIn("torch.inference_mode()", source)
        self.assertIn("handle.remove()", source)
        self.assertIn("torch.equal(weights, before)", source)

    def test_no_gpu_during_import(self):
        self.assertTrue(callable(V.attribute_batch))
        self.assertTrue(callable(V.evaluate))


if __name__ == "__main__":
    unittest.main()
