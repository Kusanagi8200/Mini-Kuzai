"""CPU-only V78 identical-context rebatching protocol and safety regression."""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "v78_identical_context_rebatching_numerical_control.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.md"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
AUDIT = ROOT / "tools" / "public-audits" / (
    "phase03_v78_identical_context_rebatching_numerical_control_001.py"
)

spec = importlib.util.spec_from_file_location("v78_test_source", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V78 source unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class V78IdenticalContextRebatchingTests(unittest.TestCase):
    def test_01_exact_thirty_field_schema_and_protocol_registration(self):
        self.assertEqual(len(V.METRIC_FIELDS), 30)
        self.assertEqual(len(set(V.METRIC_FIELDS)), 30)
        protocol = PROTOCOL.read_text(encoding="utf-8")
        for key in V.METRIC_FIELDS:
            self.assertIn(f"`{key}`", protocol)

    def test_02_fixed_runtime_constants(self):
        self.assertEqual(V.PATH_A_BATCH, 4)
        self.assertEqual(V.PATH_B_BATCH, 32)
        self.assertEqual(V.SCORE_CHUNK, 512)
        self.assertEqual(V.GPU_PEAK_LIMIT_MIB, 6144)
        self.assertEqual(V.VAL_LEXICAL, 9170)
        self.assertEqual(V.MODEL_DIM, 128)
        self.assertEqual(V.VOCAB, 1024)

    def test_03_frozen_delta_thresholds(self):
        self.assertEqual(V.DELTA_1E7, 1e-7)
        self.assertEqual(V.DELTA_1E6, 1e-6)
        self.assertEqual(V.DELTA_1E5, 1e-5)
        self.assertLess(V.DELTA_1E7, V.DELTA_1E6)
        self.assertLess(V.DELTA_1E6, V.DELTA_1E5)
        self.assertEqual(V.NANO_SCALE, 1_000_000_000)

    def test_04_dependency_pins(self):
        V.verify_dependency_blobs()

    def test_05_identity_prefix_is_exact_and_deterministic(self):
        b = V.T.BOS_ID
        prefix = (b, 3, 4, 5, 6)
        self.assertEqual(V.identical_prefix(prefix), prefix)
        self.assertEqual(V.identical_prefix(prefix), V.identical_prefix(prefix))

    def test_06_identity_prefix_preserves_length_order_and_last(self):
        b = V.T.BOS_ID
        prefix = (b, 7, 7, 9, 11)
        out = V.identical_prefix(prefix)
        self.assertEqual(len(out), len(prefix))
        self.assertEqual(out, prefix)
        self.assertEqual(out[0], b)
        self.assertEqual(out[-1], 11)

    def test_07_invalid_prefixes_fail_closed(self):
        b = V.T.BOS_ID
        with self.assertRaises(ValueError):
            V.identical_prefix(())
        with self.assertRaises(ValueError):
            V.identical_prefix((3, 4, 5))
        with self.assertRaises(ValueError):
            V.identical_prefix((b, V.T.PAD_ID, 5))
        with self.assertRaises(ValueError):
            V.identical_prefix((b, 4, V.VOCAB))

    def test_08_sign_classes_include_exact_zero(self):
        values = torch.tensor([-2.0, -0.0, 0.0, 3.0], dtype=torch.float64)
        self.assertEqual(V.sign_classes(values).tolist(), [-1, 0, 0, 1])

    def test_09_three_delta_thresholds_are_strict(self):
        stats = V.empty_pair_stats()
        x = torch.zeros(4, dtype=torch.float64)
        y = torch.tensor(
            [
                V.DELTA_1E7,
                V.DELTA_1E7 * 1.01,
                V.DELTA_1E6 * 1.01,
                V.DELTA_1E5 * 1.01,
            ],
            dtype=torch.float64,
        )
        pred = torch.tensor([3, 4, 5, 6])
        gold = pred.clone()
        V.update_pair_stats(stats, x, y, pred, pred, gold, 4, 4)
        self.assertEqual(stats["DELTA_GT_1E7"], 3)
        self.assertEqual(stats["DELTA_GT_1E6"], 2)
        self.assertEqual(stats["DELTA_GT_1E5"], 1)

    def test_10_prediction_sign_and_correctness_partitions(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-1.0, 0.5, 2.0, -0.25], dtype=torch.float64)
        y = torch.tensor([-2.0, -0.5, 1.0, 0.25], dtype=torch.float64)
        pa = torch.tensor([3, 4, 5, 6])
        pb = torch.tensor([3, 7, 5, 8])
        gold = torch.tensor([3, 4, 9, 8])
        V.update_pair_stats(stats, x, y, pa, pb, gold, 4, 4)
        self.assertEqual(stats["PRED_AGREE"] + stats["PRED_CHANGED"], 4)
        self.assertEqual(stats["SIGN_AGREE"] + stats["SIGN_CHANGED"], 4)
        self.assertEqual(stats["SHARED_CORRECT"], 1)
        self.assertEqual(stats["A_ONLY_CORRECT"], 1)
        self.assertEqual(stats["B_ONLY_CORRECT"], 1)

    def test_11_centered_pearson_perfect_relation(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-2.0, -1.0, 1.0, 2.0], dtype=torch.float64)
        y = 3.0 * x + 5.0
        pred = torch.tensor([3, 4, 5, 6])
        gold = pred.clone()
        V.update_pair_stats(stats, x, y, pred, pred, gold, 4, 4)
        final = V.finalize_pair_stats(stats, 4)
        self.assertEqual(final["ALPHA_CORR_ABS_BP"], 10000)

    def test_12_nano_scaling_is_deterministic(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-2.0, -1.0, 1.0, 2.0], dtype=torch.float64)
        y = x + torch.tensor([1e-7, 2e-7, 3e-7, 4e-7], dtype=torch.float64)
        pred = torch.tensor([3, 4, 5, 6])
        gold = pred.clone()
        V.update_pair_stats(stats, x, y, pred, pred, gold, 4, 4)
        final = V.finalize_pair_stats(stats, 4)
        self.assertEqual(final["ALPHA_MAX_ABS_NANO"], 400)
        self.assertEqual(final["ALPHA_MEAN_ABS_NANO"], 250)

    def test_13_identical_input_counts_must_cover_all_pairs(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-2.0, -1.0, 1.0, 2.0], dtype=torch.float64)
        pred = torch.tensor([3, 4, 5, 6])
        V.update_pair_stats(stats, x, x, pred, pred, pred, 3, 4)
        with self.assertRaises(RuntimeError):
            V.finalize_pair_stats(stats, 4)

    def test_14_nonfinite_and_degenerate_stats_fail_closed(self):
        with self.assertRaises(ValueError):
            V.sign_classes(torch.tensor([1.0, float("nan")]))
        stats = V.empty_pair_stats()
        x = torch.ones(4, dtype=torch.float64)
        pred = torch.tensor([3, 3, 3, 3])
        gold = torch.tensor([3, 4, 5, 6])
        V.update_pair_stats(stats, x, x, pred, pred, gold, 4, 4)
        with self.assertRaises(RuntimeError):
            V.finalize_pair_stats(stats, 4)

    def test_15_start_receipt_and_v77_report_replay(self):
        V.verify_start_receipt()
        metrics = V.verify_v77_report()
        self.assertEqual(metrics["V77_PRED_CHANGED"], 5)
        self.assertEqual(metrics["V77_ALPHA_DELTA_NONZERO"], 9123)
        self.assertEqual(metrics["V77_PERTURBED_PREFIXES"], 9062)
        self.assertEqual(metrics["V77_FULL_CORRECT"], 2594)

    def test_16_source_uses_same_prefix_without_transform(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("copied = [identical_prefix(prefix) for prefix in original]", source)
        self.assertNotIn("reverse_history_keep_last(", source)
        self.assertIn("PATH_A_BATCH = 4", source)
        self.assertIn("PATH_B_BATCH = 32", source)

    def test_17_source_keeps_target_separate(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("jobs_gold.append(target)", source)
        self.assertIn("prefix = tokens[:target_index]", source)
        self.assertNotIn("identical_prefix(target", source)

    def test_18_gogit_allowlist_and_source_mapping(self):
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

        spec = importlib.util.spec_from_file_location("v78_gogit_test", GOGIT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(
            module.source_for_audit(
                "tools/public-audits/"
                "phase03_v78_identical_context_rebatching_numerical_control_001.py"
            ),
            "Mini-Kuzai V78 identical-context rebatching numerical control",
        )

    def test_19_scientific_audit_pins_exact_core_blob(self):
        audit = AUDIT.read_text(encoding="utf-8")
        blob = subprocess.run(
            ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertIn(f'FROZEN_GIT_BLOB = "{blob}"', audit)

    def test_20_no_blind_training_generation_or_private_output_path(self):
        source = SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "optimizer.step(",
            "torch.save(",
            "load_blind(",
            "build_blind(",
            ".generate(",
            "decode(",
            "token_text",
            "per_position",
            "hidden_vectors",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("torch.set_grad_enabled(False)", source)
        self.assertIn("torch.inference_mode()", source)
        self.assertIn('"V78_BLIND_ACCESS": 0', source)
        self.assertIn("GPU_PEAK_LIMIT_MIB = 6144", source)


if __name__ == "__main__":
    unittest.main()
