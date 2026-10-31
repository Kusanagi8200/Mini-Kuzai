"""V72 CPU tests for frozen hidden-state spectrum and GOGIT invariants."""
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
SOURCE = (ROOT / "tools/public-audits" /
          "phase03_v72_hidden_state_anisotropy_001.py")
spec = importlib.util.spec_from_file_location("v72_geometry", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("Frozen V72 audit source not found")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def fixture():
    geometry = {
        "mean_energy": 0.7, "raw": (0.82, 0.95, 1.4),
        "center": (0.48, 0.72, 3.1), "pair_cos": 0.54,
        "mean_norm": 6.0, "mean_h_norm": 7.1, "mean_pc1": 0.65,
    }
    center = {
        "switch": 700, "switch_byte": 400, "switch_merge": 300,
        "correct": 2800, "orig_correct": 2673, "distinct": 9,
        "top1_share": 6400, "byte_deficit": 4876.0,
        "merge_deficit": 8000.0,
    }
    original = {
        "CE_X1000": 4732, "PRED_DISTINCT": 5,
        "TOP1_SHARE_BP": 7255,
    }
    v71 = {
        "V71_ATTR_ORIG_CE_X1000": 4732,
        "V71_ATTR_ORIG_DISTINCT": 5,
        "V71_ATTR_ORIG_TOP1_SHARE_BP": 7255,
        "V71_ATTR_CORRECT_BOTH": 2626,
        "V71_ATTR_CORRECT_ORIG_ONLY": 47,
    }
    return geometry, center, original, v71


class V72AnisotropyTests(unittest.TestCase):
    def test_schema_exactly_30_numeric_only(self):
        report = V.build_report(*fixture())
        self.assertEqual(len(report), 30)
        self.assertEqual(
            {x for x in report if x.startswith("V72_GEOM_")},
            {"V72_GEOM_" + x for x in V.FIELDS})
        self.assertEqual(report["V72_GEOM_PASS"], 1)
        self.assertEqual(report["V72_GEOM_BLIND_ACCESS"], 0)
        self.assertEqual(report["TRAINING_STARTED"], 0)
        self.assertEqual(report["V72_GEOM_MEAN_ENERGY_BP"], 7000)
        self.assertEqual(report["V72_GEOM_CENTER_SWITCH"], 700)
        self.assertEqual(report["V72_GEOM_RAW_PARTICIPATION_X100"], 140)
        self.assertTrue(all(type(v) is int for v in report.values()))

    def test_original_v71_replay_is_mandatory(self):
        for name in ("CE_X1000", "PRED_DISTINCT", "TOP1_SHARE_BP"):
            data = list(fixture())
            data[2] = dict(data[2])
            data[2][name] += 1
            with self.subTest(metric=name), self.assertRaises(RuntimeError):
                V.build_report(*data)

    def test_correctness_and_switch_invariants(self):
        for field, replacement in (
            ("orig_correct", 2672),
            ("switch", 701),
            ("distinct", 0),
            ("top1_share", 10001),
        ):
            data = list(fixture())
            data[1] = dict(data[1])
            data[1][field] = replacement
            with self.subTest(field=field), self.assertRaises(RuntimeError):
                V.build_report(*data)

    def test_synthetic_spatial_spectrum(self):
        rows = torch.arange(9170, dtype=torch.float32)
        h = torch.zeros((9170, 128), dtype=torch.float32)
        h[:, 0] = 3.0
        h[:, 1] = (rows - rows.mean()) / 9170
        h[:, 2] = h[:, 1].square()
        g = V.spectral_summary(h)
        self.assertEqual(tuple(g["mean"].shape), (128,))
        self.assertGreater(g["mean_energy"], 0.7)
        self.assertGreater(g["raw"][0], g["center"][0])
        self.assertGreaterEqual(g["center"][1], g["center"][0])
        self.assertGreaterEqual(g["center"][2], 1)
        self.assertLessEqual(g["center"][2], 128)
        self.assertGreaterEqual(g["pair_cos"], -1)
        self.assertLessEqual(g["pair_cos"], 1)

    def test_reject_degenerate_covariance(self):
        h = torch.zeros((9170, 128), dtype=torch.float32)
        with self.assertRaises(RuntimeError):
            V.spectral_summary(h)
        h[:, 0] = 3.0
        with self.assertRaises(RuntimeError):
            V.spectral_summary(h)

    def test_mean_centered_argmax_accounting(self):
        hidden = torch.zeros((9170, 128), dtype=torch.float32)
        hidden[:, 0] = 1.0
        weights = torch.zeros((1024, 128), dtype=torch.float32)
        weights[3, 0] = 1.0
        targets = torch.full((9170,), 259, dtype=torch.long)
        targets[:4876] = 3
        orig = torch.full_like(targets, 3)
        mean = torch.zeros(128)
        mean[0] = 1.0
        observed = V.center_control(hidden, targets, orig, weights, mean)
        self.assertEqual(observed["switch"], 9170)
        self.assertEqual(observed["switch_byte"], 4876)
        self.assertEqual(observed["switch_merge"], 4294)
        self.assertEqual(observed["orig_correct"], 4876)
        self.assertEqual(observed["correct"], 0)
        self.assertEqual(observed["distinct"], 1)
        self.assertEqual(observed["top1_share"], 10000)

    def test_no_training_or_private_split(self):
        content = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("optimizer.step(", content)
        self.assertNotIn("torch.save(", content)
        self.assertNotIn("load_blind", content)
        self.assertNotIn("build_blind", content)
        self.assertIn("torch.inference_mode()", content)
        self.assertIn("handle.remove()", content)
        self.assertIn("torch.equal(weights, before)", content)

    def test_v71_source_identity_is_required(self):
        content = SOURCE.read_text(encoding="utf-8")
        self.assertIn("hashlib.sha256(V71.read_bytes()).hexdigest()", content)
        self.assertIn("V71_ATTR_ORIG_CE_X1000", content)


if __name__ == "__main__":
    unittest.main()
