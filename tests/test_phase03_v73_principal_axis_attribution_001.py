"""CPU regression tests for the V73 read-only principal-axis diagnostic."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SOURCE = (ROOT / "tools/public-audits" /
          "phase03_v73_principal_axis_attribution_001.py")
spec = importlib.util.spec_from_file_location("v73_axis_audit", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V73 audit unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def fixture():
    spectrum = {"PC1_BP": 8288, "PC2_BP": 900, "PC5_BP": 9738}
    measures = {
        "CENTER": {"DISTINCT": 15, "TOP1_SHARE_BP": 5788,
                   "CORRECT": 2832, "MARGIN_X1000": 620},
        "MINUS_PC1": {"DISTINCT": 21, "TOP1_SHARE_BP": 5500,
                      "CORRECT": 2900, "MARGIN_X1000": 500},
        "MINUS_PC12": {"DISTINCT": 31, "TOP1_SHARE_BP": 4100,
                       "CORRECT": 3000, "MARGIN_X1000": 440},
        "PC1_ONLY": {"DISTINCT": 4, "TOP1_SHARE_BP": 8000,
                     "CORRECT": 1050, "MARGIN_X1000": 980},
    }
    changes = {"MINUS_PC1": 900, "MINUS_PC12": 1700, "PC1_ONLY": 5000}
    alignment = {"WIN": 750, "GOLD": 240}
    original = {"CE_X1000": 4732, "PRED_DISTINCT": 5, "TOP1_SHARE_BP": 7255}
    v72 = {
        "V72_GEOM_ORIG_CE_X1000": 4732,
        "V72_GEOM_ORIG_DISTINCT": 5,
        "V72_GEOM_ORIG_TOP1_SHARE_BP": 7255,
        "V72_GEOM_CENTER_DISTINCT": 15,
        "V72_GEOM_CENTER_TOP1_SHARE_BP": 5788,
        "V72_GEOM_CENTER_CORRECT": 2832,
        "V72_GEOM_CENTER_PC1_SHARE_BP": 8288,
        "V72_GEOM_CENTER_PC5_SHARE_BP": 9738,
    }
    return spectrum, measures, changes, 400, 500, alignment, original, v72


class V73PrincipalAxisTests(unittest.TestCase):
    def test_exact_30_numeric_fields(self):
        report = V.build_report(*fixture())
        self.assertEqual(len(report), 30)
        self.assertEqual(
            {key for key in report if key.startswith("V73_AXIS_")},
            {"V73_AXIS_" + key for key in V.FIELDS})
        self.assertTrue(all(type(v) is int and v >= 0 for v in report.values()))
        self.assertEqual(report["V73_AXIS_PASS"], 1)
        self.assertEqual(report["V73_AXIS_CENTER_DISTINCT"], 15)
        self.assertEqual(report["V73_AXIS_CENTER_PC1_BP"], 8288)
        self.assertEqual(report["V73_AXIS_MINUS_PC1_SWITCH"], 900)
        self.assertEqual(report["TRAINING_STARTED"], 0)
        self.assertEqual(report["V73_AXIS_BLIND_ACCESS"], 0)

    def test_strict_v72_baseline(self):
        for field in ("CE_X1000", "PRED_DISTINCT", "TOP1_SHARE_BP"):
            args = list(fixture())
            args[6] = dict(args[6])
            args[6][field] += 1
            with self.subTest(field=field), self.assertRaises(RuntimeError):
                V.build_report(*args)
        for field in ("DISTINCT", "TOP1_SHARE_BP", "CORRECT"):
            args = list(fixture())
            args[1] = dict(args[1])
            args[1]["CENTER"] = dict(args[1]["CENTER"])
            args[1]["CENTER"][field] += 1
            with self.subTest(field=field), self.assertRaises(RuntimeError):
                V.build_report(*args)

    def test_switch_reconciliation_and_spectrum(self):
        for index, name, value in (
            (2, "MINUS_PC1", 901),
            (3, None, 401),
            (4, None, 501),
        ):
            args = list(fixture())
            if name is None:
                args[index] = value
            else:
                args[index] = dict(args[index])
                args[index][name] = value
            with self.subTest(index=index), self.assertRaises(RuntimeError):
                V.build_report(*args)
        args = list(fixture())
        args[0] = dict(args[0], PC1_BP=7000)
        with self.assertRaises(RuntimeError):
            V.build_report(*args)

    def test_sign_invariant_orthogonal_projection(self):
        basis = torch.zeros((128, 2), dtype=torch.float32)
        basis[1, 0] = 1.0  # PC2
        basis[0, 1] = 1.0  # PC1
        data = torch.zeros((3, 128), dtype=torch.float32)
        data[:, 0] = torch.tensor([1.0, 2.0, 3.0])
        data[:, 1] = torch.tensor([4.0, 5.0, 6.0])
        data[:, 2] = torch.tensor([7.0, 8.0, 9.0])
        projected = V.project_modes(data, basis)
        self.assertTrue(torch.allclose(projected["CENTER"], data))
        self.assertTrue(torch.equal(projected["MINUS_PC1"][:, 0],
                                    torch.zeros(3)))
        self.assertTrue(torch.equal(projected["MINUS_PC12"][:, :2],
                                    torch.zeros((3, 2))))
        self.assertTrue(torch.equal(projected["PC1_ONLY"][:, 0], data[:, 0]))
        self.assertTrue(torch.equal(projected["PC1_ONLY"][:, 1:],
                                    torch.zeros((3, 127))))
        flipped = V.project_modes(data, -basis)
        for name in V.MODES:
            self.assertTrue(torch.allclose(projected[name], flipped[name]))

    def test_frozen_covariance_axes(self):
        h = torch.zeros((9170, 128), dtype=torch.float32)
        h[:, 0] = torch.linspace(-2, 2, 9170)
        h[:, 1] = torch.sin(torch.linspace(0, 100, 9170)) * 0.12
        h[:, 2] = 0.4
        basis, spectrum = V.principal_axes(h)
        self.assertEqual(tuple(basis.shape), (128, 2))
        self.assertGreater(spectrum["PC1_BP"], 9000)
        self.assertGreater(spectrum["PC2_BP"], 0)
        self.assertGreaterEqual(spectrum["PC5_BP"], spectrum["PC1_BP"])
        self.assertTrue(torch.allclose(basis.T @ basis, torch.eye(2),
                                      atol=2e-5))

    def test_degenerate_hidden_covariance_rejected(self):
        h = torch.ones((9170, 128), dtype=torch.float32)
        with self.assertRaises(RuntimeError):
            V.principal_axes(h)

    def test_no_training_or_blind_in_audit(self):
        code = SOURCE.read_text(encoding="utf-8")
        for forbidden in ("optimizer.step(", "torch.save(",
                          "load_blind", "build_blind"):
            self.assertNotIn(forbidden, code)
        self.assertIn("torch.inference_mode()", code)
        self.assertIn("handle.remove()", code)
        self.assertIn("torch.equal(weights, before)", code)
        self.assertIn("hashlib.sha256(V72.read_bytes()).hexdigest()", code)


if __name__ == "__main__":
    unittest.main()
