#!/usr/bin/env python3

from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "tools/public-audits/phase03_v81_v62_continuation_readiness_001.py"

spec = importlib.util.spec_from_file_location(
    "phase03_v81_v62_continuation_readiness_001",
    AUDIT,
)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class V81V62ContinuationReadinessTests(unittest.TestCase):

    def test_remaining_budget_is_exact(self):
        self.assertEqual(module.CURRENT_STEPS, 69)
        self.assertEqual(module.MAX_STEPS, 145)
        self.assertEqual(module.REMAINING_STEPS, 76)
        self.assertEqual(module.CURRENT_EXPOSURE, 597982)
        self.assertEqual(module.MAX_EXPOSURE, 1181664)
        self.assertEqual(module.REMAINING_EXPOSURE, 583682)

    def test_frozen_fingerprints_are_pinned(self):
        for value in (
            module.AUTH_FP,
            module.TRAINER_FP,
            module.OBJECTIVE_FP,
            module.CORPUS_FP,
        ):
            self.assertEqual(len(value), 64)
            int(value, 16)

    def test_audit_has_no_training_runtime_import(self):
        tree = ast.parse(AUDIT.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)

        self.assertNotIn("torch", imported)
        self.assertNotIn("subprocess", imported)

    def test_exact_30_metric_schema(self):
        tree = ast.parse(AUDIT.read_text(encoding="utf-8"))
        metric_keys = None

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name) or target.id != "metrics":
                continue
            if not isinstance(node.value, ast.Dict):
                continue

            keys = []
            for key in node.value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    keys.append(key.value)
            if keys:
                metric_keys = keys

        self.assertIsNotNone(metric_keys)
        self.assertEqual(len(metric_keys), 30)
        self.assertEqual(len(set(metric_keys)), 30)
        self.assertIn("TRAINING_AUTHORIZED", metric_keys)
        self.assertIn("TRAINING_STARTED", metric_keys)
        self.assertIn("V81_PREFLIGHT_CHECKPOINT_WRITE", metric_keys)
        self.assertIn("V81_GPU_EXECUTION", metric_keys)

    def test_readiness_gate_remains_non_authorizing(self):
        source = AUDIT.read_text(encoding="utf-8")
        self.assertIn('"TRAINING_AUTHORIZED": 0', source)
        self.assertIn('"TRAINING_STARTED": 0', source)
        self.assertIn('"V81_BLIND_ACCESS": 0', source)
        self.assertIn('"V81_PREFLIGHT_CHECKPOINT_WRITE": 0', source)
        self.assertIn('"V81_GPU_EXECUTION": 0', source)


if __name__ == "__main__":
    unittest.main()
