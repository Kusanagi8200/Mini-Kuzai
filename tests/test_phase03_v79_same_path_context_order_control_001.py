"""CPU-only V79 same-path context-order protocol and safety regression."""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import unittest
from collections import Counter
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "v79_same_path_context_order_control.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.md"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
AUDIT = ROOT / "tools" / "public-audits" / (
    "phase03_v79_same_path_context_order_control_001.py"
)

spec = importlib.util.spec_from_file_location("v79_test_source", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V79 source unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class V79SamePathContextOrderTests(unittest.TestCase):
    def test_01_exact_thirty_field_schema_and_protocol_registration(self):
        self.assertEqual(len(V.METRIC_FIELDS), 30)
        self.assertEqual(len(set(V.METRIC_FIELDS)), 30)
        protocol = PROTOCOL.read_text(encoding="utf-8")
        for key in V.METRIC_FIELDS:
            self.assertIn(f"`{key}`", protocol)

    def test_02_fixed_runtime_constants(self):
        self.assertEqual(V.SAME_PATH_BATCH, 32)
        self.assertEqual(V.SCORE_CHUNK, 512)
        self.assertEqual(V.GPU_PEAK_LIMIT_MIB, 6144)
        self.assertEqual(V.VAL_LEXICAL, 9170)
        self.assertEqual(V.MODEL_DIM, 128)
        self.assertEqual(V.VOCAB, 1024)
        self.assertEqual(V.PERTURBED_PREFIXES, 9062)
        self.assertEqual(V.UNCHANGED_PREFIXES, 108)

    def test_03_frozen_delta_thresholds(self):
        self.assertEqual(V.DELTA_1E7, 1e-7)
        self.assertEqual(V.DELTA_1E6, 1e-6)
        self.assertEqual(V.DELTA_1E5, 1e-5)
        self.assertLess(V.DELTA_1E7, V.DELTA_1E6)
        self.assertLess(V.DELTA_1E6, V.DELTA_1E5)
        self.assertEqual(V.NANO_SCALE, 1_000_000_000)

    def test_04_dependency_pins(self):
        V.verify_dependency_blobs()

    def test_05_start_receipt(self):
        V.verify_start_receipt()

    def test_06_v77_replay(self):
        metrics = V.verify_v77_report()
        self.assertEqual(metrics["V77_PRED_CHANGED"], 5)
        self.assertEqual(metrics["V77_ALPHA_SIGN_CHANGED"], 5)
        self.assertEqual(metrics["V77_PERTURBED_PREFIXES"], 9062)
        self.assertEqual(metrics["V77_UNCHANGED_PREFIXES"], 108)

    def test_07_v78_path_b_replay(self):
        metrics = V.verify_v78_report()
        self.assertEqual(metrics["V78_PATH_B_BATCH"], 32)
        self.assertEqual(metrics["V78_PATH_B_CORRECT"], 2594)
        self.assertEqual(metrics["V78_PATH_B_DISTINCT"], 2)
        self.assertEqual(metrics["V78_PATH_B_TOP1_SHARE_BP"], 7043)
        self.assertEqual(metrics["V78_PRED_CHANGED"], 0)

    def test_08_reverse_transform_is_deterministic(self):
        b = V.T.BOS_ID
        prefix = (b, 3, 4, 5, 6)
        expected = (b, 5, 4, 3, 6)
        self.assertEqual(V.reverse_history_keep_last(prefix), expected)
        self.assertEqual(
            V.reverse_history_keep_last(prefix),
            V.reverse_history_keep_last(prefix),
        )

    def test_09_reverse_preserves_length_multiset_bos_and_last(self):
        b = V.T.BOS_ID
        prefix = (b, 7, 8, 7, 11)
        out = V.reverse_history_keep_last(prefix)
        self.assertEqual(len(out), len(prefix))
        self.assertEqual(Counter(out), Counter(prefix))
        self.assertEqual(out[0], b)
        self.assertEqual(out[-1], 11)

    def test_10_short_prefixes_remain_unchanged(self):
        b = V.T.BOS_ID
        self.assertEqual(V.reverse_history_keep_last((b,)), (b,))
        self.assertEqual(V.reverse_history_keep_last((b, 9)), (b, 9))

    def test_11_invalid_prefixes_fail_closed(self):
        b = V.T.BOS_ID
        with self.assertRaises(ValueError):
            V.reverse_history_keep_last(())
        with self.assertRaises(ValueError):
            V.reverse_history_keep_last((3, 4, 5))
        with self.assertRaises(ValueError):
            V.reverse_history_keep_last((b, V.T.PAD_ID, 5))
        with self.assertRaises(ValueError):
            V.reverse_history_keep_last((b, 4, V.VOCAB))

    def test_12_pair_invariant_count(self):
        b = V.T.BOS_ID
        original = [(b, 3, 4, 5), (b, 8)]
        reverse = [
            V.reverse_history_keep_last(original[0]),
            V.reverse_history_keep_last(original[1]),
        ]
        self.assertEqual(V.pair_invariant_count(original, reverse), 2)

    def test_13_sign_classes_include_exact_zero(self):
        values = torch.tensor([-2.0, -0.0, 0.0, 3.0], dtype=torch.float64)
        self.assertEqual(V.sign_classes(values).tolist(), [-1, 0, 0, 1])

    def test_14_three_delta_thresholds_are_strict(self):
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
        changed = torch.tensor([False, True, True, True])
        V.update_pair_stats(stats, x, y, pred, pred, gold, changed, 4)
        self.assertEqual(stats["DELTA_GT_1E7"], 3)
        self.assertEqual(stats["DELTA_GT_1E6"], 2)
        self.assertEqual(stats["DELTA_GT_1E5"], 1)

    def test_15_prediction_sign_and_correctness_partitions(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-1.0, 0.5, 2.0, -0.25], dtype=torch.float64)
        y = torch.tensor([-2.0, -0.5, 1.0, 0.25], dtype=torch.float64)
        po = torch.tensor([3, 4, 5, 6])
        pr = torch.tensor([3, 7, 5, 8])
        gold = torch.tensor([3, 4, 9, 8])
        changed = torch.tensor([False, True, True, False])
        V.update_pair_stats(stats, x, y, po, pr, gold, changed, 4)
        self.assertEqual(stats["PRED_AGREE"] + stats["PRED_CHANGED"], 4)
        self.assertEqual(stats["SIGN_AGREE"] + stats["SIGN_CHANGED"], 4)
        self.assertEqual(stats["SHARED_CORRECT"], 1)
        self.assertEqual(stats["ORIGINAL_ONLY_CORRECT"], 1)
        self.assertEqual(stats["REVERSE_ONLY_CORRECT"], 1)

    def test_16_centered_pearson_perfect_relation(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-2.0, -1.0, 1.0, 2.0], dtype=torch.float64)
        y = x + 5e-5
        pred = torch.tensor([3, 4, 5, 6])
        gold = pred.clone()
        changed = torch.tensor([False, True, True, False])
        V.update_pair_stats(stats, x, y, pred, pred, gold, changed, 4)
        final = V.finalize_pair_stats(stats, 4)
        self.assertEqual(final["ALPHA_CORR_ABS_BP"], 10000)

    def test_17_nano_scaling_is_deterministic(self):
        stats = V.empty_pair_stats()
        x = torch.tensor([-2.0, -1.0, 1.0, 2.0], dtype=torch.float64)
        y = x + torch.tensor([1e-7, 2e-7, 3e-7, 4e-7], dtype=torch.float64)
        pred = torch.tensor([3, 4, 5, 6])
        changed = torch.tensor([False, True, True, False])
        V.update_pair_stats(stats, x, y, pred, pred, pred, changed, 4)
        final = V.finalize_pair_stats(stats, 4)
        self.assertEqual(final["ALPHA_MAX_ABS_NANO"], 400)
        self.assertEqual(final["ALPHA_MEAN_ABS_NANO"], 250)
        self.assertEqual(V.PUBLIC_METRIC_MAX, 100_000_000)
        self.assertEqual(V.ALPHA_MAX_ABS_NANO_LIMIT, 2_000_000_000)

    def test_18_nonfinite_and_degenerate_stats_fail_closed(self):
        with self.assertRaises(ValueError):
            V.sign_classes(torch.tensor([1.0, float("nan")]))
        stats = V.empty_pair_stats()
        x = torch.ones(4, dtype=torch.float64)
        pred = torch.tensor([3, 3, 3, 3])
        changed = torch.tensor([False, True, True, False])
        V.update_pair_stats(stats, x, x, pred, pred, pred, changed, 4)
        with self.assertRaises(RuntimeError):
            V.finalize_pair_stats(stats, 4)

    def test_19_source_uses_same_scoring_helper_for_both_modes(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn(
            "alpha_original = score_prefix_batch(\n"
            "                    V77, model, device, original, mean_t, pc1_t, taps",
            source,
        )
        self.assertIn(
            "alpha_reverse = score_prefix_batch(\n"
            "                    V77, model, device, transformed, mean_t, pc1_t, taps",
            source,
        )

    def test_20_source_has_no_paired_batch4_path(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SAME_PATH_BATCH = 32", source)
        self.assertNotIn("PATH_A_BATCH =", source)
        self.assertNotIn("SAME_PATH_BATCH = 4", source)
        self.assertIn("range(0, VAL_LEXICAL, SAME_PATH_BATCH)", source)

    def test_21_source_keeps_target_separate_and_freezes_v77_transform(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("prefix = tokens[:target_index]", source)
        self.assertIn("gold_values.append(target)", source)
        self.assertIn("V77.reverse_history_keep_last(prefix)", source)
        self.assertNotIn("reverse_history_keep_last(target", source)

    def test_22_gogit_allowlist_and_source_mapping(self):
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

        spec = importlib.util.spec_from_file_location("v79_gogit_test", GOGIT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(
            module.source_for_audit(
                "tools/public-audits/"
                "phase03_v79_same_path_context_order_control_001.py"
            ),
            "Mini-Kuzai V79 same-path context-order control",
        )
        self.assertEqual(
            module.METRIC_MAX_OVERRIDES,
            {"V79_ALPHA_MAX_ABS_NANO": 2_000_000_000},
        )

    def test_23_scientific_audit_pins_exact_core_blob(self):
        audit = AUDIT.read_text(encoding="utf-8")
        blob = subprocess.run(
            ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertIn(f'FROZEN_GIT_BLOB = "{blob}"', audit)

    def test_24_no_blind_training_generation_or_private_output_path(self):
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
        self.assertIn('"V79_BLIND_ACCESS": 0', source)
        self.assertIn("GPU_PEAK_LIMIT_MIB = 6144", source)


if __name__ == "__main__":
    unittest.main()
