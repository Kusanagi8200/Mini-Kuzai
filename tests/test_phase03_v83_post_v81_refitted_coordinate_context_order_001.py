"""CPU-only V83 post-V81 refitted-coordinate regressions."""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/v83_post_v81_refitted_coordinate_context_order.py"
PROTOCOL = ROOT / "phases/MINI-KUZAI-PHASE-03-V83-POST-V81-REFITTED-COORDINATE-CONTEXT-ORDER-CONTROL-001.md"
GOGIT = ROOT / "tools/gogit_public.py"
AUDIT = ROOT / "tools/public-audits/phase03_v83_post_v81_refitted_coordinate_context_order_001.py"
START = ROOT / "automation/dev-flow/receipts/V83-start.json"
V82_REPORT = ROOT / "reports/assistant-results/history/PHASE03-SMOLTALK-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001.json"
V82_SOURCE = ROOT / "tools/v82_post_continuation_context_order_replication.py"

spec = importlib.util.spec_from_file_location("v83_test_source", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V83 source unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class V83RefittedCoordinateTests(unittest.TestCase):
    def test_01_exact_thirty_field_schema(self):
        self.assertEqual(len(V.METRIC_FIELDS), 30)
        self.assertEqual(len(set(V.METRIC_FIELDS)), 30)
        self.assertEqual(V.METRIC_FIELDS[:5], (
            "SEMANTIC_VALIDATION_COMPLETE",
            "TRAINING_AUTHORIZED",
            "TRAINING_STARTED",
            "V83_PASS",
            "V83_BLIND_ACCESS",
        ))

    def test_02_fixed_runtime_constants(self):
        self.assertEqual(V.VAL_LEXICAL, 9170)
        self.assertEqual(V.TRAIN_LEXICAL, 294726)
        self.assertEqual(V.SAME_PATH_BATCH, 32)
        self.assertEqual(V.FINAL_STEPS, 136)
        self.assertEqual(V.FINAL_EXPOSURE, 1181302)
        self.assertEqual(V.GPU_PEAK_LIMIT_MIB, 6144)

    def test_03_start_receipt_is_v83_discussion_15(self):
        receipt = V.verify_start_receipt()
        self.assertEqual(receipt["step"], "V83")
        self.assertEqual(
            receipt["github_url"],
            "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/15",
        )

    def test_04_v82_report_gate(self):
        metrics = V.verify_v82_report()
        self.assertEqual(metrics["V82_PASS"], 1)
        self.assertEqual(metrics["V82_FINAL_PRED_CHANGED"], 38)
        self.assertEqual(metrics["V82_FINAL_SIGN_CHANGED"], 38)
        self.assertEqual(metrics["V82_BLIND_ACCESS"], 0)
        self.assertEqual(metrics["TRAINING_STARTED"], 0)

    def test_05_protocol_freezes_refit_boundary(self):
        protocol = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("Refit the coordinate on final model TRAIN only", protocol)
        self.assertIn("change **only** the diagnostic coordinate", protocol)
        self.assertIn("no optimizer", protocol.lower())
        self.assertIn("no BLIND", protocol)

    def test_06_source_requires_exact_old_coordinate_replay(self):
        source = SOURCE.read_text(encoding="utf-8")
        for expected in (
            'pairs["PRED_CHANGED"] == 38',
            'pairs["SIGN_CHANGED"] == 38',
            'pairs["ALPHA_CORR_ABS_BP"] == 9999',
            'boundary["BOUNDARY_MEAN_NANO_CHANGED"] == 54510100',
            'boundary["CROSSING_MEAN_NANO_CHANGED"] == 154062261',
        ):
            self.assertIn(expected, source)

    def test_07_refit_uses_final_model_before_train_geometry(self):
        source = SOURCE.read_text(encoding="utf-8")
        final_load = source.index('model.load_state_dict(final_state["model"], strict=True)')
        old_replay = source.index("exact_old_replay_gate(")
        collect = source.index("v75.collect_geometry(")
        refit_score = source.rindex("V82.score_validation(")
        self.assertLess(final_load, old_replay)
        self.assertLess(old_replay, collect)
        self.assertLess(collect, refit_score)

    def test_08_refit_is_train_only_by_construction(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("T.build_training_streams()", source)
        self.assertIn("v75._segments_in_order(streams)", source)
        self.assertIn("TRAIN_LEXICAL", source)
        self.assertNotIn("build_blind", source)
        self.assertNotIn("load_blind", source)

    def test_09_no_training_generation_or_checkpoint_write(self):
        source = SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "optimizer.step(",
            "scheduler.step(",
            "torch.save(",
            ".generate(",
            "decode(",
            "token_text",
            "per_position",
            "hidden_vectors",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("torch.set_grad_enabled(False)", source)
        self.assertIn('"TRAINING_AUTHORIZED": 0', source)
        self.assertIn('"V83_BLIND_ACCESS": 0', source)

    def test_10_checkpoint_integrity_before_and_after(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn('before = {', source)
        self.assertIn('after = {', source)
        self.assertIn('if after != before:', source)
        self.assertIn("checkpoint changed during read-only evaluation", source)

    def test_11_deterministic_refit_control_present(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("repeat_mean, repeat_pc1, repeat_share", source)
        self.assertIn("torch.equal(repeat_mean, refit_mean)", source)
        self.assertIn("abs_cos_bp(repeat_pc1, refit_pc1) == 10000", source)

    def test_12_gogit_allowlist_mapping_and_overrides(self):
        tree = ast.parse(GOGIT.read_text(encoding="utf-8"))
        keys = overrides = None
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
            "V83_REFIT_BOUNDARY_MAX_NANO_CHANGED",
            "V83_REFIT_BOUNDARY_MEAN_NANO_CHANGED",
            "V83_REFIT_CROSSING_MAX_NANO_CHANGED",
            "V83_REFIT_CROSSING_MEAN_NANO_CHANGED",
        ):
            self.assertEqual(overrides[key], 2_000_000_000)

        gs = GOGIT.read_text(encoding="utf-8")
        self.assertIn(
            '"tools/public-audits/phase03_v83_post_v81_refitted_coordinate_context_order_001.py": 900',
            gs,
        )
        self.assertIn("return SOURCE_PHASE03_V83", gs)

    def test_13_scientific_audit_pins_exact_core_blob(self):
        audit = AUDIT.read_text(encoding="utf-8")
        blob = subprocess.run(
            ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertIn(f'FROZEN_GIT_BLOB = "{blob}"', audit)

    def test_14_required_evidence_files_exist(self):
        for path in (START, V82_REPORT, V82_SOURCE, PROTOCOL, AUDIT):
            self.assertTrue(path.is_file())
            self.assertFalse(path.is_symlink())


if __name__ == "__main__":
    unittest.main()
