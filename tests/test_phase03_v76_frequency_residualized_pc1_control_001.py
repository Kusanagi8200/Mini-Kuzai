"""CPU-only V76 frozen protocol, OLS decomposition and safety regression."""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import unittest
from collections import Counter
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "v76_frequency_residualized_pc1_control.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.md"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
V65 = ROOT / "tools" / "public-audits" / "phase03_v65_token_frequency_diagnostic_001.py"
AUDIT = ROOT / "tools" / "public-audits" / (
    "phase03_v76_frequency_residualized_pc1_control_001.py"
)

spec = importlib.util.spec_from_file_location("v76_test_source", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V76 source unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def synthetic_frequency() -> Counter:
    return Counter({3: 1, 4: 3, 9: 7, 100: 2, 1023: 5})


def synthetic_axis() -> torch.Tensor:
    axis = torch.zeros(V.MODEL_DIM, dtype=torch.float64)
    axis[0] = 1.0
    return axis


def synthetic_weights() -> torch.Tensor:
    base = torch.arange(
        V.VOCAB * V.MODEL_DIM,
        dtype=torch.float64,
    ).reshape(V.VOCAB, V.MODEL_DIM)
    return (base.remainder(97) - 48.0) / 97.0


class V76FrequencyResidualizedTests(unittest.TestCase):
    def test_exact_thirty_field_schema_and_protocol_registration(self):
        self.assertEqual(len(V.METRIC_FIELDS), 30)
        self.assertEqual(len(set(V.METRIC_FIELDS)), 30)
        protocol = PROTOCOL.read_text(encoding="utf-8")
        for key in V.METRIC_FIELDS:
            self.assertIn(f"`{key}`", protocol)

    def test_fixed_runtime_and_dependency_blob_pins(self):
        self.assertEqual(V.TRAIN_BATCH, 2)
        self.assertEqual(V.VAL_BATCH, 4)
        self.assertEqual(V.SCORE_CHUNK, 512)
        self.assertEqual(V.GPU_PEAK_LIMIT_MIB, 6144)
        self.assertEqual(V.TRAIN_LEXICAL, 294726)
        self.assertEqual(V.TRAIN_TYPES, 891)
        self.assertEqual(V.VAL_LEXICAL, 9170)
        self.assertEqual(V.MODEL_DIM, 128)
        self.assertEqual(V.VOCAB, 1024)
        self.assertEqual(
            V.DEPENDENCY_BLOBS,
            {
                "tools/v75_train_fitted_geometry_transfer.py":
                    "8705d8ca9aebe7281779c704119d26eb82517da2",
                "tools/public-audits/phase03_v65_token_frequency_diagnostic_001.py":
                    "d88e05933686b369d5236c3bcd465729e2df3407",
                "reports/assistant-results/history/"
                "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json":
                    "51606f42f60c5e53c437cac0be9bc6459fadbd05",
                "reports/assistant-results/history/"
                "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001.json":
                    "8cf575c440d7625bd03d6ce1d77c3951c678f84a",
                "reports/assistant-results/history/"
                "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001.json":
                    "5096c81e32b6140f926930a09e0b6253fa557c01",
            },
        )
        V.verify_dependency_blobs()

    def test_v65_lexical_definition_and_zero_filled_count_vector(self):
        source = V65.read_text(encoding="utf-8")
        self.assertIn("for token in ids[1:-1]:", source)
        self.assertIn("MIN_TOKEN=3", source)
        self.assertIn("MAX_TOKEN=1024", source)

        counts = V.frequency_count_vector(synthetic_frequency())
        self.assertEqual(tuple(counts.shape), (1024,))
        self.assertEqual(float(counts[0]), 0.0)
        self.assertEqual(float(counts[1]), 0.0)
        self.assertEqual(float(counts[2]), 0.0)
        self.assertEqual(float(counts[5]), 0.0)
        self.assertEqual(float(counts[1023]), 5.0)
        self.assertEqual(int(counts.gt(0).sum()), 5)

    def test_synthetic_centered_ols_recovery(self):
        _f, g = V.centered_log_frequency(synthetic_frequency())
        q = 2.5 * g
        fit = V.centered_ols(q, g)
        self.assertAlmostEqual(fit["BETA"], 2.5, places=12)
        self.assertLessEqual(fit["DECOMPOSITION_ERROR"], V.DECOMP_ATOL)
        self.assertAlmostEqual(fit["CORR_ABS"], 1.0, places=12)
        self.assertAlmostEqual(fit["R2"], 1.0, places=12)
        self.assertAlmostEqual(fit["RESIDUAL_ENERGY"], 0.0, places=12)

    def test_constant_logit_offset_invariance(self):
        q = torch.linspace(-2.0, 3.0, V.VOCAB, dtype=torch.float64)
        raw = q + 17.25
        alpha = torch.tensor([-4.0, -0.5, 0.0, 0.25, 3.0], dtype=torch.float64)
        self.assertTrue(V.constant_offset_argmax_equal(alpha, raw, q))

    def test_pc1_sign_invariance_of_scored_profiles(self):
        weights = synthetic_weights()
        axis = synthetic_axis()
        frequency = synthetic_frequency()
        pos = V.decompose_output_profile(weights, axis, frequency)
        neg = V.decompose_output_profile(weights, -axis, frequency)

        self.assertTrue(torch.allclose(neg["Q"], -pos["Q"], rtol=0, atol=1e-12))
        self.assertTrue(
            torch.allclose(
                neg["COMPONENT"],
                -pos["COMPONENT"],
                rtol=0,
                atol=1e-12,
            )
        )
        self.assertTrue(
            torch.allclose(
                neg["RESIDUAL"],
                -pos["RESIDUAL"],
                rtol=0,
                atol=1e-12,
            )
        )

        alpha = torch.tensor([-2.0, -0.5, 0.5, 3.0], dtype=torch.float64)
        for key in ("Q", "COMPONENT", "RESIDUAL"):
            logits_pos = alpha[:, None] * pos[key][None, :]
            logits_neg = (-alpha)[:, None] * neg[key][None, :]
            self.assertTrue(torch.equal(logits_pos, logits_neg))

    def test_exact_q_component_residual_decomposition(self):
        fit = V.decompose_output_profile(
            synthetic_weights(),
            synthetic_axis(),
            synthetic_frequency(),
        )
        self.assertLessEqual(
            float(torch.max(torch.abs(
                fit["Q"] - fit["COMPONENT"] - fit["RESIDUAL"]
            ))),
            V.DECOMP_ATOL,
        )

    def test_residual_orthogonality(self):
        fit = V.decompose_output_profile(
            synthetic_weights(),
            synthetic_axis(),
            synthetic_frequency(),
        )
        dot = abs(float(torch.dot(fit["G"], fit["RESIDUAL"])))
        scale = float(
            torch.linalg.vector_norm(fit["G"])
            * torch.linalg.vector_norm(fit["RESIDUAL"])
        )
        if scale == 0.0:
            self.assertLessEqual(dot, V.DECOMP_ATOL)
        else:
            self.assertLessEqual(dot / scale, V.ORTHO_RTOL)

    def test_pearson_r2_identity(self):
        fit = V.decompose_output_profile(
            synthetic_weights(),
            synthetic_axis(),
            synthetic_frequency(),
        )
        self.assertLessEqual(
            abs(fit["R2"] - fit["CORR_ABS"] ** 2),
            V.IDENTITY_TOL,
        )
        self.assertLessEqual(
            abs(fit["R2"] + fit["RESIDUAL_ENERGY"] - 1.0),
            V.IDENTITY_TOL,
        )

    def test_histogram_accounting_helpers(self):
        out = V.empty_outcome()
        pred = torch.tensor([3, 3, 7, 9, 9, 9], dtype=torch.long)
        gold = torch.tensor([3, 4, 7, 8, 9, 10], dtype=torch.long)
        V.update_outcome(out, pred, gold)
        final = V.finalize_outcome(out, 6)
        self.assertEqual(final["CORRECT"], 3)
        self.assertEqual(final["DISTINCT"], 3)
        self.assertEqual(final["TOP1_SHARE_BP"], 5000)

    def test_nonfinite_and_degenerate_inputs_fail_closed(self):
        with self.assertRaises(RuntimeError):
            V.centered_ols(
                torch.full((V.VOCAB,), float("nan")),
                torch.ones(V.VOCAB),
            )
        with self.assertRaises(RuntimeError):
            V.centered_ols(
                torch.ones(V.VOCAB),
                torch.zeros(V.VOCAB),
            )
        with self.assertRaises(ValueError):
            V.frequency_count_vector(Counter({2: 10}))
        bad_weights = synthetic_weights()
        bad_weights[0, 0] = float("inf")
        with self.assertRaises(RuntimeError):
            V.decompose_output_profile(
                bad_weights,
                synthetic_axis(),
                synthetic_frequency(),
            )

    def test_start_receipt_and_frozen_reports(self):
        V.verify_start_receipt()
        refs = V.verify_frozen_reports()
        self.assertEqual(refs["V75"]["V75_TRAIN_PC1_CORRECT"], 2457)
        self.assertEqual(refs["V75"]["V75_TRAIN_PC1_VAR_SHARE_BP"], 9019)
        self.assertEqual(refs["V75"]["V75_TRAIN_VAL_PC1_COS_ABS_BP"], 9995)
        self.assertEqual(refs["V74_CORE"]["V74_CORE_UNIGRAM_CORRECT"], 2535)

    def test_gogit_allowlist_and_source_mapping(self):
        tree = ast.parse(GOGIT.read_text(encoding="utf-8"))
        keys = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "METRIC_KEYS"
                for target in node.targets
            ):
                keys = ast.literal_eval(node.value)
                break
        self.assertIsInstance(keys, set)
        self.assertTrue(set(V.METRIC_FIELDS) <= keys)

        gogit_spec = importlib.util.spec_from_file_location("v76_gogit_test", GOGIT)
        self.assertIsNotNone(gogit_spec)
        self.assertIsNotNone(gogit_spec.loader)
        gogit = importlib.util.module_from_spec(gogit_spec)
        gogit_spec.loader.exec_module(gogit)
        self.assertEqual(
            gogit.source_for_audit(
                "tools/public-audits/"
                "phase03_v76_frequency_residualized_pc1_control_001.py"
            ),
            "Mini-Kuzai V76 frozen frequency-residualized TRAIN-PC1 output control",
        )

    def test_scientific_wrapper_pins_current_core_blob(self):
        audit = AUDIT.read_text(encoding="utf-8")
        blob = subprocess.run(
            ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertIn(f'FROZEN_GIT_BLOB = "{blob}"', audit)

    def test_source_has_no_blind_training_checkpoint_or_private_output_path(self):
        source = SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "optimizer.step(",
            "torch.save(",
            "load_blind(",
            "build_blind(",
            "decode(",
            "token_text",
            "per_position",
            "hidden_vectors",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("torch.set_grad_enabled(False)", source)
        self.assertIn("torch.inference_mode()", source)
        self.assertIn("V76_BLIND_ACCESS", source)
        self.assertIn("GPU_PEAK_LIMIT_MIB = 6144", source)


if __name__ == "__main__":
    unittest.main()
