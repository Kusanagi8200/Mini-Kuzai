"""CPU-only V77 context-order protocol, accounting and safety regression."""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import unittest
from collections import Counter
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "v77_residual_context_order_sensitivity.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.md"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
AUDIT = ROOT / "tools" / "public-audits" / (
    "phase03_v77_residual_context_order_sensitivity_001.py"
)

spec = importlib.util.spec_from_file_location("v77_test_source", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V77 source unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class V77ResidualContextOrderTests(unittest.TestCase):
    def test_01_exact_thirty_field_schema_and_protocol_registration(self):
        self.assertEqual(len(V.METRIC_FIELDS), 30)
        self.assertEqual(len(set(V.METRIC_FIELDS)), 30)
        protocol = PROTOCOL.read_text(encoding="utf-8")
        for key in V.METRIC_FIELDS:
            self.assertIn(f"`{key}`", protocol)

    def test_02_fixed_runtime_and_dependency_pins(self):
        self.assertEqual(V.VAL_BATCH, 4)
        self.assertEqual(V.COUNTERFACTUAL_BATCH, 32)
        self.assertEqual(V.SCORE_CHUNK, 512)
        self.assertEqual(V.GPU_PEAK_LIMIT_MIB, 6144)
        self.assertEqual(V.ALPHA_DELTA_THRESHOLD, 1e-7)
        self.assertEqual(V.VAL_LEXICAL, 9170)
        self.assertEqual(V.MODEL_DIM, 128)
        self.assertEqual(V.VOCAB, 1024)
        V.verify_dependency_blobs()

    def test_03_reverse_history_is_deterministic(self):
        b = V.T.BOS_ID
        prefix = (b, 3, 4, 5, 6)
        self.assertEqual(
            V.reverse_history_keep_last(prefix),
            (b, 5, 4, 3, 6),
        )
        self.assertEqual(
            V.reverse_history_keep_last(prefix),
            V.reverse_history_keep_last(prefix),
        )

    def test_04_prefix_length_and_multiset_preserved(self):
        b = V.T.BOS_ID
        prefix = (b, 3, 7, 7, 9, 11)
        out = V.reverse_history_keep_last(prefix)
        self.assertEqual(len(out), len(prefix))
        self.assertEqual(Counter(out), Counter(prefix))

    def test_05_bos_and_immediate_predecessor_preserved(self):
        b = V.T.BOS_ID
        prefix = (b, 13, 17, 19, 23)
        out = V.reverse_history_keep_last(prefix)
        self.assertEqual(out[0], b)
        self.assertEqual(out[-1], 23)

    def test_06_short_prefixes_unchanged(self):
        b = V.T.BOS_ID
        self.assertEqual(V.reverse_history_keep_last((b,)), (b,))
        self.assertEqual(V.reverse_history_keep_last((b, 8)), (b, 8))
        self.assertEqual(
            V.reverse_history_keep_last((b, 8, 9)),
            (b, 8, 9),
        )

    def test_07_invalid_prefixes_fail_closed(self):
        b = V.T.BOS_ID
        with self.assertRaises(ValueError):
            V.reverse_history_keep_last(())
        with self.assertRaises(ValueError):
            V.reverse_history_keep_last((3, 4, 5))
        with self.assertRaises(ValueError):
            V.reverse_history_keep_last((b, V.T.PAD_ID, 5))
        with self.assertRaises(ValueError):
            V.reverse_history_keep_last((b, 4, V.VOCAB))

    def test_08_target_is_separate_and_not_transformed(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("jobs_gold.append(target)", source)
        self.assertIn("prefix = tokens[:target_index]", source)
        self.assertIn("gold_all = torch.as_tensor(", source)
        self.assertNotIn("reverse_history_keep_last(target", source)

    def test_09_sign_classes_include_exact_zero(self):
        values = torch.tensor([-2.0, -0.0, 0.0, 3.0], dtype=torch.float64)
        self.assertEqual(
            V.sign_classes(values).tolist(),
            [-1, 0, 0, 1],
        )

    def test_10_alpha_delta_threshold_is_strict(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([0.0, 0.0, 0.0], dtype=torch.float64)
        y = torch.tensor(
            [V.ALPHA_DELTA_THRESHOLD,
             V.ALPHA_DELTA_THRESHOLD * 1.01,
             -V.ALPHA_DELTA_THRESHOLD * 1.01],
            dtype=torch.float64,
        )
        pred = torch.tensor([3, 4, 5])
        gold = torch.tensor([3, 4, 5])
        changed = torch.tensor([False, True, True])
        V.update_pair_stats(stats, x, y, pred, pred, gold, changed)
        self.assertEqual(stats["ALPHA_DELTA_NONZERO"], 2)

    def test_11_pair_prediction_and_sign_partitions(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-1.0, 0.5, 2.0, -0.25], dtype=torch.float64)
        y = torch.tensor([-2.0, -0.5, 1.0, 0.25], dtype=torch.float64)
        pf = torch.tensor([3, 4, 5, 6])
        pr = torch.tensor([3, 7, 5, 8])
        gold = torch.tensor([3, 4, 9, 8])
        changed = torch.tensor([False, True, True, True])
        V.update_pair_stats(stats, x, y, pf, pr, gold, changed)
        self.assertEqual(stats["PRED_AGREE"] + stats["PRED_CHANGED"], 4)
        self.assertEqual(stats["SIGN_AGREE"] + stats["SIGN_CHANGED"], 4)
        self.assertEqual(
            stats["PERTURBED_PREFIXES"] + stats["UNCHANGED_PREFIXES"],
            4,
        )

    def test_12_centered_pearson_perfect_linear_relation(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-2.0, -1.0, 1.0, 2.0], dtype=torch.float64)
        y = 3.0 * x + 5.0
        pred = torch.tensor([3, 4, 5, 6])
        gold = torch.tensor([3, 4, 5, 6])
        changed = torch.tensor([True, True, True, True])
        V.update_pair_stats(stats, x, y, pred, pred, gold, changed)
        final = V.finalize_pair_stats(stats, 4)
        self.assertEqual(final["ALPHA_CORR_ABS_BP"], 10000)

    def test_13_outcome_histogram_and_unigram_accounting(self):
        out = V.empty_outcome()
        pred = torch.tensor([3, 3, 7, 9, 9, 9], dtype=torch.long)
        gold = torch.tensor([3, 4, 7, 8, 9, 10], dtype=torch.long)
        V.update_outcome(out, pred, gold, unigram=9)
        final = V.finalize_outcome(out, 6)
        self.assertEqual(final["CORRECT"], 3)
        self.assertEqual(final["DISTINCT"], 3)
        self.assertEqual(final["TOP1_SHARE_BP"], 5000)
        self.assertEqual(final["UNIGRAM_AGREE"], 3)
        self.assertEqual(final["UNIGRAM_SHARED_CORRECT"], 1)

    def test_14_paired_correctness_partition(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-2.0, -1.0, 1.0, 2.0], dtype=torch.float64)
        y = torch.tensor([-1.0, 1.0, 2.0, -2.0], dtype=torch.float64)
        pf = torch.tensor([3, 4, 5, 6])
        pr = torch.tensor([3, 8, 9, 6])
        gold = torch.tensor([3, 4, 9, 7])
        changed = torch.tensor([True, True, True, True])
        V.update_pair_stats(stats, x, y, pf, pr, gold, changed)
        self.assertEqual(stats["SHARED_CORRECT"], 1)
        self.assertEqual(stats["FULL_ONLY_CORRECT"], 1)
        self.assertEqual(stats["REVERSE_ONLY_CORRECT"], 1)

    def test_15_nonfinite_and_degenerate_pair_stats_fail_closed(self):
        with self.assertRaises(ValueError):
            V.sign_classes(torch.tensor([1.0, float("nan")]))
        stats = V.empty_pair_stats()
        x = torch.ones(4, dtype=torch.float64)
        pred = torch.tensor([3, 3, 3, 3])
        gold = torch.tensor([3, 4, 5, 6])
        changed = torch.tensor([True, True, True, True])
        V.update_pair_stats(stats, x, x, pred, pred, gold, changed)
        with self.assertRaises(RuntimeError):
            V.finalize_pair_stats(stats, 4)

    def test_16_start_receipt_and_v76_report_replay(self):
        V.verify_start_receipt()
        metrics = V.verify_v76_report()
        self.assertEqual(metrics["V76_FREQ_RESIDUAL_CORRECT"], 2594)
        self.assertEqual(metrics["V76_RESIDUAL_ENERGY_SHARE_BP"], 9225)
        self.assertEqual(metrics["V76_AXIS_FREQ_R2_BP"], 775)

    def test_17_gogit_allowlist_source_mapping_and_wrapper_pin(self):
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

        spec = importlib.util.spec_from_file_location("v77_gogit_test", GOGIT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(
            module.source_for_audit(
                "tools/public-audits/"
                "phase03_v77_residual_context_order_sensitivity_001.py"
            ),
            "Mini-Kuzai V77 frozen residual context-order sensitivity control",
        )

        audit = AUDIT.read_text(encoding="utf-8")
        blob = subprocess.run(
            ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertIn(f'FROZEN_GIT_BLOB = "{blob}"', audit)

    def test_18_source_has_no_blind_training_generation_or_private_output_path(self):
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
        self.assertIn("V77_BLIND_ACCESS", source)
        self.assertIn("GPU_PEAK_LIMIT_MIB = 6144", source)


if __name__ == "__main__":
    unittest.main()
