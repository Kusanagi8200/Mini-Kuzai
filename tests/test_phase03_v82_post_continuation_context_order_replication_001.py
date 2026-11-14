"""CPU-only V82 post-continuation context-order replication regressions."""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "v82_post_continuation_context_order_replication.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001.md"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
AUDIT = ROOT / "tools" / "public-audits" / (
    "phase03_v82_post_continuation_context_order_replication_001.py"
)
START = ROOT / "automation" / "dev-flow" / "receipts" / "V82-start.json"
V81_FINAL = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V81-FINAL-CLOSURE-001.json"
)

spec = importlib.util.spec_from_file_location("v82_test_source", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V82 source unavailable")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class V82PostContinuationReplicationTests(unittest.TestCase):
    def test_01_exact_thirty_field_schema(self):
        self.assertEqual(len(V.METRIC_FIELDS), 30)
        self.assertEqual(len(set(V.METRIC_FIELDS)), 30)
        self.assertEqual(V.METRIC_FIELDS[:5], (
            "SEMANTIC_VALIDATION_COMPLETE",
            "TRAINING_AUTHORIZED",
            "TRAINING_STARTED",
            "V82_PASS",
            "V82_BLIND_ACCESS",
        ))

    def test_02_fixed_runtime_constants(self):
        self.assertEqual(V.VAL_LEXICAL, 9170)
        self.assertEqual(V.SAME_PATH_BATCH, 32)
        self.assertEqual(V.GPU_PEAK_LIMIT_MIB, 6144)
        self.assertEqual(V.FINAL_STEPS, 136)
        self.assertEqual(V.FINAL_EXPOSURE, 1181302)
        self.assertEqual(V.V80_PERTURBED, 9062)
        self.assertEqual(V.V80_UNCHANGED, 108)

    def test_03_start_receipt_is_v82_discussion_14(self):
        receipt = V.verify_start_receipt()
        self.assertEqual(receipt["step"], "V82")
        self.assertEqual(
            receipt["github_url"],
            "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/14",
        )

    def test_04_v81_closure_gate(self):
        metrics = V.verify_v81_closure()
        self.assertEqual(metrics["V81_FINAL_PASS"], 1)
        self.assertEqual(metrics["V81_FINAL_STEPS"], 136)
        self.assertEqual(metrics["V81_FINAL_EXPOSURE"], 1181302)
        self.assertEqual(metrics["V81_FINAL_BLIND_ACCESS"], 0)
        self.assertEqual(metrics["V81_FINAL_FURTHER_TRAINING_AUTHORIZED"], 0)

    def test_05_protocol_freezes_cycle2_coordinate_and_last_checkpoint(self):
        protocol = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("checkpoint-cycle-02.pt", protocol)
        self.assertIn("checkpoint-last.pt", protocol)
        self.assertIn("does **not** refit", protocol)
        self.assertIn("START-DEV-FLOW V82 is required", protocol)

    def test_06_zero_changed_boundary_is_valid(self):
        class DummyV80:
            pass

        stats = {
            "COUNT": 2,
            "CHANGED_COUNT": 0,
            "SIGN_CHANGED_COUNT": 0,
            "BOUNDARY_SUM_CHANGED": 0.0,
            "BOUNDARY_MAX_CHANGED": 0.0,
            "CROSSING_SUM_CHANGED": 0.0,
            "CROSSING_MAX_CHANGED": 0.0,
        }
        for label in ("1E7", "1E6", "1E5", "1E4", "1E3"):
            stats[f"ALL_WITHIN_{label}"] = 0
            stats[f"CHANGED_WITHIN_{label}"] = 0
            stats[f"SIGN_WITHIN_{label}"] = 0

        result = V.finalize_boundary_stats_allow_zero(DummyV80, stats, 2)
        self.assertEqual(result["BOUNDARY_MAX_NANO_CHANGED"], 0)
        self.assertEqual(result["BOUNDARY_MEAN_NANO_CHANGED"], 0)
        self.assertEqual(result["CROSSING_MAX_NANO_CHANGED"], 0)
        self.assertEqual(result["CROSSING_MEAN_NANO_CHANGED"], 0)

    def test_07_source_requires_exact_v80_baseline_replay(self):
        source = SOURCE.read_text(encoding="utf-8")
        for expected in (
            'baseline["V80_V79_PRED_CHANGED_REPLAY"] == 5',
            'baseline["V80_V79_SIGN_CHANGED_REPLAY"] == 5',
            'baseline["V80_CHANGED_WITHIN_1E3"] == 0',
            'baseline["V80_BOUNDARY_MEAN_NANO_CHANGED"] == 30173315',
            'baseline["V80_BOUNDARY_MAX_NANO_CHANGED"] == 59604287',
            'baseline["V80_CROSSING_MEAN_NANO_CHANGED"] == 150983569',
            'baseline["V80_CROSSING_MAX_NANO_CHANGED"] == 249839202',
        ):
            self.assertIn(expected, source)

    def test_08_source_loads_final_after_baseline_coordinate(self):
        source = SOURCE.read_text(encoding="utf-8")
        coordinate = source.index("prepare_frozen_coordinate(V80)")
        baseline = source.index("baseline_outcomes")
        final_load = source.index("final_state = verify_checkpoint_state(")
        final_score = source.index("outcomes, pairs, boundary = score_validation(")
        self.assertLess(coordinate, baseline)
        self.assertLess(baseline, final_load)
        self.assertLess(final_load, final_score)

    def test_09_no_training_blind_generation_or_checkpoint_write(self):
        source = SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "optimizer.step(",
            "scheduler.step(",
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
        self.assertIn('"TRAINING_AUTHORIZED": 0', source)
        self.assertIn('"V82_BLIND_ACCESS": 0', source)

    def test_10_gogit_allowlist_mapping_and_overrides(self):
        tree = ast.parse(GOGIT.read_text(encoding="utf-8"))
        keys = None
        overrides = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names = {
                    target.id
                    for target in node.targets
                    if isinstance(target, ast.Name)
                }
                if "METRIC_KEYS" in names:
                    keys = ast.literal_eval(node.value)
                if "METRIC_MAX_OVERRIDES" in names:
                    overrides = ast.literal_eval(node.value)
        self.assertIsInstance(keys, set)
        self.assertTrue(set(V.METRIC_FIELDS) <= keys)
        for key in (
            "V82_FINAL_BOUNDARY_MAX_NANO_CHANGED",
            "V82_FINAL_BOUNDARY_MEAN_NANO_CHANGED",
            "V82_FINAL_CROSSING_MAX_NANO_CHANGED",
            "V82_FINAL_CROSSING_MEAN_NANO_CHANGED",
        ):
            self.assertEqual(overrides[key], 2_000_000_000)

        spec = importlib.util.spec_from_file_location("v82_gogit_test", GOGIT)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(
            module.source_for_audit(
                "tools/public-audits/"
                "phase03_v82_post_continuation_context_order_replication_001.py"
            ),
            "Mini-Kuzai V82 post-continuation context-order replication control",
        )

    def test_11_scientific_audit_pins_exact_core_blob(self):
        audit = AUDIT.read_text(encoding="utf-8")
        blob = subprocess.run(
            ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertIn(f'FROZEN_GIT_BLOB = "{blob}"', audit)

    def test_12_required_evidence_files_exist(self):
        for path in (START, V81_FINAL, PROTOCOL, AUDIT):
            self.assertTrue(path.is_file())
            self.assertFalse(path.is_symlink())


if __name__ == "__main__":
    unittest.main()
