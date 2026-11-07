"""CPU-only V75 frozen protocol, streaming geometry and safety regression."""
from __future__ import annotations

import importlib.util
import unittest
from collections import Counter
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "v75_train_fitted_geometry_transfer.py"
PROTOCOL = ROOT / "phases" / "MINI-KUZAI-PHASE-03-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.md"

spec = importlib.util.spec_from_file_location("v75_train_geometry_test_source", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V75 reviewed source unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def fake_outcomes():
    return {
        "ORIG": {"CORRECT": 2673, "DISTINCT": 5, "TOP1_SHARE_BP": 7255},
        "TRAIN_CENTER": {"CORRECT": 2500, "DISTINCT": 20, "TOP1_SHARE_BP": 5000},
        "TRAIN_PC1": {"CORRECT": 2300, "DISTINCT": 4, "TOP1_SHARE_BP": 6500},
        "TRAIN_MINUS_PC1": {"CORRECT": 1200, "DISTINCT": 500, "TOP1_SHARE_BP": 2100},
        "VAL_PC1": {"CORRECT": 2455, "DISTINCT": 2, "TOP1_SHARE_BP": 7034},
    }


class V75GeometryTransferTests(unittest.TestCase):
    def test_exact_thirty_field_schema_and_protocol_registration(self):
        self.assertEqual(len(V.METRIC_FIELDS), 30)
        self.assertEqual(len(set(V.METRIC_FIELDS)), 30)
        protocol = PROTOCOL.read_text(encoding="utf-8")
        for key in V.METRIC_FIELDS:
            self.assertIn(f"`{key}`", protocol)

    def test_fixed_execution_constants(self):
        self.assertEqual(V.TRAIN_BATCH, 2)
        self.assertEqual(V.VAL_BATCH, 4)
        self.assertEqual(V.SCORE_CHUNK, 512)
        self.assertEqual(V.GPU_PEAK_LIMIT_MIB, 6144)
        self.assertEqual(V.TRAIN_LEXICAL, 294726)
        self.assertEqual(V.TRAIN_TYPES, 891)
        self.assertEqual(V.VAL_LEXICAL, 9170)
        self.assertEqual(V.MODEL_DIM, 128)

    def test_unigram_tie_break_uses_lowest_train_token_id(self):
        self.assertEqual(V.most_frequent(Counter({300: 10, 4: 10, 3: 9})), 4)
        with self.assertRaises(ValueError):
            V.most_frequent(Counter())
        with self.assertRaises(ValueError):
            V.most_frequent(Counter({2: 99}))

    def test_streaming_covariance_matches_direct_population_covariance(self):
        x = torch.zeros((9, V.MODEL_DIM), dtype=torch.float64)
        x[:, 0] = torch.tensor([-5, -4, -3, -2, 0, 2, 3, 4, 5], dtype=torch.float64)
        x[:, 1] = torch.tensor([0, 1, 0, -1, 0, 1, 0, -1, 0], dtype=torch.float64)
        count, mean, m2 = V.empty_stats()
        for chunk in (x[:2], x[2:6], x[6:]):
            count, mean, m2 = V.update_stats(count, mean, m2, chunk)
        direct_mean = x.mean(0)
        centered = x - direct_mean
        direct_m2 = centered.T @ centered
        self.assertEqual(count, len(x))
        self.assertTrue(torch.allclose(mean, direct_mean, rtol=1e-12, atol=1e-12))
        self.assertTrue(torch.allclose(m2, direct_m2, rtol=1e-12, atol=1e-12))
        final_mean, pc1, share = V.finalize_geometry(
            count, mean, m2, expected_count=len(x)
        )
        self.assertTrue(torch.allclose(final_mean, direct_mean))
        self.assertGreater(abs(float(pc1[0])), 0.99)
        self.assertGreater(share, 9000)

    def test_streaming_fixed_chunking_is_deterministic(self):
        x = torch.arange(12 * V.MODEL_DIM, dtype=torch.float64).reshape(12, V.MODEL_DIM)
        x[:, 0] *= 10.0

        def run_once():
            state = V.empty_stats()
            for start in range(0, len(x), 3):
                state = V.update_stats(*state, x[start:start + 3])
            return state

        a = run_once()
        b = run_once()
        self.assertEqual(a[0], b[0])
        self.assertTrue(torch.equal(a[1], b[1]))
        self.assertTrue(torch.equal(a[2], b[2]))

    def test_projection_is_invariant_to_pc1_sign(self):
        h = torch.zeros((4, V.MODEL_DIM), dtype=torch.float32)
        h[:, 0] = torch.tensor([1.0, 2.0, -1.0, -2.0])
        h[:, 1] = 3.0
        mean = torch.zeros(V.MODEL_DIM)
        axis = torch.zeros(V.MODEL_DIM)
        axis[0] = 1.0
        pos = V.project_modes(h, mean, axis)
        neg = V.project_modes(h, mean, -axis)
        for mode in ("TRAIN_CENTER", "TRAIN_PC1", "TRAIN_MINUS_PC1"):
            self.assertTrue(torch.equal(pos[mode], neg[mode]))

    def test_absolute_alignment_is_sign_invariant(self):
        a = torch.zeros(V.MODEL_DIM)
        b = torch.zeros(V.MODEL_DIM)
        a[0] = 1.0
        b[0] = 0.6
        b[1] = 0.8
        self.assertEqual(V.abs_cos_bp(a, b), 6000)
        self.assertEqual(V.abs_cos_bp(a, -b), 6000)

    def test_strict_metric_builder(self):
        metrics = V.build_metrics(
            fake_outcomes(),
            agree=6000,
            shared=2200,
            train_share_bp=8000,
            val_share_bp=8288,
            alignment_bp=7500,
            unigram_correct=2535,
        )
        self.assertEqual(tuple(metrics), V.METRIC_FIELDS)
        self.assertEqual(len(metrics), 30)
        self.assertEqual(metrics["TRAINING_AUTHORIZED"], 0)
        self.assertEqual(metrics["TRAINING_STARTED"], 0)
        self.assertEqual(metrics["V75_BLIND_ACCESS"], 0)
        self.assertEqual(metrics["V75_COVERAGE_BP"], 10000)

    def test_metric_builder_fails_closed_on_reference_drift(self):
        bad = fake_outcomes()
        bad["ORIG"]["CORRECT"] += 1
        with self.assertRaises(RuntimeError):
            V.build_metrics(bad, 6000, 2200, 8000, 8288, 7500, 2535)
        bad = fake_outcomes()
        bad["VAL_PC1"]["TOP1_SHARE_BP"] += 1
        with self.assertRaises(RuntimeError):
            V.build_metrics(bad, 6000, 2200, 8000, 8288, 7500, 2535)

    def test_nonfinite_and_degenerate_geometry_fail_closed(self):
        state = V.empty_stats()
        bad = torch.zeros((2, V.MODEL_DIM), dtype=torch.float64)
        bad[0, 0] = float("nan")
        with self.assertRaises(RuntimeError):
            V.update_stats(*state, bad)

        count, mean, m2 = V.empty_stats()
        flat = torch.zeros((4, V.MODEL_DIM), dtype=torch.float64)
        count, mean, m2 = V.update_stats(count, mean, m2, flat)
        with self.assertRaises(RuntimeError):
            V.finalize_geometry(count, mean, m2, expected_count=4)

    def test_start_receipt_and_frozen_prerequisite_reports(self):
        V.verify_start_receipt()
        refs = V.prerequisites()
        self.assertEqual(refs["V65"]["V65_FREQ_TRAIN_LEXICAL"], 294726)
        self.assertEqual(refs["V73"]["V73_AXIS_PC1_ONLY_CORRECT"], 2455)
        self.assertEqual(refs["V74_CORE"]["V74_CORE_UNIGRAM_CORRECT"], 2535)
        self.assertEqual(
            refs["V74_STRATA"]["V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT"], 2449
        )

    def test_source_has_no_training_checkpoint_write_or_full_hidden_retention(self):
        source = SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "optimizer.step(",
            "torch.save(",
            "load_blind(",
            "build_blind(",
            "memory.append(",
            "gold_tokens.append(",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("torch.inference_mode()", source)
        self.assertIn("Parallel-Welford", source)
        self.assertIn("GPU_PEAK_LIMIT_MIB = 6144", source)


if __name__ == "__main__":
    unittest.main()
