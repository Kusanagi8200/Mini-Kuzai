"""CPU-only V80 decision-boundary proximity protocol and safety regression."""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "v80_decision_boundary_proximity_control.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V80-DECISION-BOUNDARY-PROXIMITY-CONTROL-001.md"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
AUDIT = ROOT / "tools" / "public-audits" / (
    "phase03_v80_decision_boundary_proximity_control_001.py"
)

spec = importlib.util.spec_from_file_location("v80_test_source", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V80 source unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class V80DecisionBoundaryProximityTests(unittest.TestCase):
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
        self.assertEqual(V.PERTURBED_PREFIXES, 9062)
        self.assertEqual(V.UNCHANGED_PREFIXES, 108)

    def test_03_frozen_thresholds(self):
        self.assertEqual(V.THRESHOLDS, (1e-7, 1e-6, 1e-5, 1e-4, 1e-3))
        self.assertEqual(tuple(sorted(V.THRESHOLDS)), V.THRESHOLDS)
        self.assertEqual(V.NANO_SCALE, 1_000_000_000)
        self.assertEqual(V.ALPHA_NANO_LIMIT, 2_000_000_000)

    def test_04_dependency_pins(self):
        V.verify_dependency_blobs()

    def test_05_start_receipt(self):
        V.verify_start_receipt()

    def test_06_v79_exact_report_replay_gate(self):
        m = V.verify_v79_report()
        self.assertEqual(m["V79_PRED_CHANGED"], 5)
        self.assertEqual(m["V79_ALPHA_SIGN_CHANGED"], 5)
        self.assertEqual(m["V79_ORIGINAL_CORRECT"], 2594)
        self.assertEqual(m["V79_REVERSE_CORRECT"], 2594)

    def test_07_boundary_distance_definition(self):
        self.assertEqual(
            V.sign_classes(torch.tensor([-1.0, -0.0, 0.0, 2.0])).tolist(),
            [-1, 0, 0, 1],
        )
        x = torch.tensor([-2.0, -0.25, 0.0, 3.0], dtype=torch.float64)
        y = torch.tensor([-1.0, 0.5, 0.1, -4.0], dtype=torch.float64)
        boundary, crossing = V.boundary_distance(x, y)
        self.assertEqual(boundary.tolist(), [1.0, 0.25, 0.0, 3.0])
        self.assertEqual(crossing.tolist(), [2.0, 0.5, 0.1, 4.0])

    def test_08_nonfinite_boundary_fails_closed(self):
        with self.assertRaises(ValueError):
            V.boundary_distance(
                torch.tensor([1.0, float("nan")]),
                torch.tensor([1.0, 2.0]),
            )

    def test_09_thresholds_are_cumulative_and_inclusive(self):
        stats = V.empty_boundary_stats()
        x = torch.tensor([1e-7, 1e-6, 1e-5, 1e-4, 1e-3], dtype=torch.float64)
        y = x * 2.0
        po = torch.tensor([3, 3, 3, 3, 3])
        pr = torch.tensor([4, 4, 4, 4, 4])
        V.update_boundary_stats(stats, x, y, po, pr)
        final = V.finalize_boundary_stats(stats, 5)
        self.assertEqual(final["ALL_WITHIN_1E7"], 1)
        self.assertEqual(final["ALL_WITHIN_1E6"], 2)
        self.assertEqual(final["ALL_WITHIN_1E5"], 3)
        self.assertEqual(final["ALL_WITHIN_1E4"], 4)
        self.assertEqual(final["ALL_WITHIN_1E3"], 5)

    def test_10_changed_and_sign_counts_are_independent(self):
        stats = V.empty_boundary_stats()
        x = torch.tensor([-1e-8, -2e-8, 3e-8, 4e-8], dtype=torch.float64)
        y = torch.tensor([1e-8, -3e-8, -4e-8, -5e-8], dtype=torch.float64)
        po = torch.tensor([3, 4, 5, 6])
        pr = torch.tensor([7, 4, 8, 6])
        V.update_boundary_stats(stats, x, y, po, pr)
        self.assertEqual(stats["CHANGED_COUNT"], 2)
        self.assertEqual(stats["SIGN_CHANGED_COUNT"], 3)

    def test_11_empty_changed_set_fails_closed(self):
        stats = V.empty_boundary_stats()
        x = torch.tensor([-1.0, 1.0], dtype=torch.float64)
        po = torch.tensor([3, 4])
        V.update_boundary_stats(stats, x, x, po, po)
        with self.assertRaises(RuntimeError):
            V.finalize_boundary_stats(stats, 2)

    def test_12_nano_scaling_for_changed_positions(self):
        stats = V.empty_boundary_stats()
        x = torch.tensor([-2e-7, 5e-7], dtype=torch.float64)
        y = torch.tensor([3e-7, -9e-7], dtype=torch.float64)
        po = torch.tensor([3, 4])
        pr = torch.tensor([5, 6])
        V.update_boundary_stats(stats, x, y, po, pr)
        final = V.finalize_boundary_stats(stats, 2)
        self.assertEqual(final["BOUNDARY_MAX_NANO_CHANGED"], 500)
        self.assertEqual(final["BOUNDARY_MEAN_NANO_CHANGED"], 350)
        self.assertEqual(final["CROSSING_MAX_NANO_CHANGED"], 900)
        self.assertEqual(final["CROSSING_MEAN_NANO_CHANGED"], 600)

    def test_13_source_reuses_v79_same_path_scorer_for_both_modes(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("alpha_original = V79.score_prefix_batch(", source)
        self.assertIn("alpha_reverse = V79.score_prefix_batch(", source)
        self.assertIn("range(0, VAL_LEXICAL, SAME_PATH_BATCH)", source)
        self.assertNotIn("PATH_A_BATCH =", source)

    def test_14_source_replays_v79_before_metrics(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("verify_v79_report()", source)
        self.assertIn('replay["PRED_CHANGED"] == 5', source)
        self.assertIn('replay["SIGN_CHANGED"] == 5', source)
        self.assertIn('original["CORRECT"] == 2594', source)
        self.assertIn('reverse["CORRECT"] == 2594', source)

    def test_15_gogit_allowlist_source_mapping_and_overrides(self):
        tree = ast.parse(GOGIT.read_text(encoding="utf-8"))
        keys = None
        overrides = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names = {
                    target.id for target in node.targets
                    if isinstance(target, ast.Name)
                }
                if "METRIC_KEYS" in names:
                    keys = ast.literal_eval(node.value)
                if "METRIC_MAX_OVERRIDES" in names:
                    overrides = ast.literal_eval(node.value)
        self.assertIsInstance(keys, set)
        self.assertTrue(set(V.METRIC_FIELDS) <= keys)
        for key in (
            "V80_BOUNDARY_MAX_NANO_CHANGED",
            "V80_BOUNDARY_MEAN_NANO_CHANGED",
            "V80_CROSSING_MAX_NANO_CHANGED",
            "V80_CROSSING_MEAN_NANO_CHANGED",
        ):
            self.assertEqual(overrides[key], 2_000_000_000)

        spec = importlib.util.spec_from_file_location("v80_gogit_test", GOGIT)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(
            module.source_for_audit(
                "tools/public-audits/"
                "phase03_v80_decision_boundary_proximity_control_001.py"
            ),
            "Mini-Kuzai V80 decision-boundary proximity control",
        )

    def test_16_scientific_audit_pins_exact_core_blob(self):
        audit = AUDIT.read_text(encoding="utf-8")
        blob = subprocess.run(
            ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertIn(f'FROZEN_GIT_BLOB = "{blob}"', audit)

    def test_17_no_blind_training_generation_or_checkpoint_write_path(self):
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
        self.assertIn('"V80_BLIND_ACCESS": 0', source)

    def test_18_scientific_history_not_created_by_implementation(self):
        history = ROOT / "reports" / "assistant-results" / "history" / (
            "PHASE03-SMOLTALK-V80-DECISION-BOUNDARY-PROXIMITY-CONTROL-001.json"
        )
        self.assertFalse(history.exists())


if __name__ == "__main__":
    unittest.main()
