#!/usr/bin/env python3

from __future__ import annotations

import ast
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "tools" / "phase03_v81_v62_continuation_authorization.py"
LAUNCHER = ROOT / "tools" / "train_v81_v62_continuation.py"
AUDIT = ROOT / "tools" / "public-audits" / "phase03_v81_v62_continuation_authorization_001.py"
GOGIT = ROOT / "tools" / "gogit_public.py"


class V81ContinuationAuthorizationTests(unittest.TestCase):

    def test_authorization_metrics_contract(self):
        spec = importlib.util.spec_from_file_location("v81_auth", AUTH)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        report = {
            "starting_optimizer_steps": 69,
            "starting_exposure_tokens": 597982,
            "max_total_optimizer_steps": 145,
            "max_total_exposure_tokens": 1181664,
            "max_remaining_optimizer_steps": 76,
            "max_remaining_exposure_tokens": 583682,
            "final_review_cycle": 4,
        }
        metrics = module.metrics(report)
        self.assertEqual(metrics["TRAINING_AUTHORIZED"], 1)
        self.assertEqual(metrics["TRAINING_STARTED"], 0)
        self.assertEqual(metrics["SEMANTIC_VALIDATION_COMPLETE"], 0)
        self.assertEqual(metrics["V81_AUTH_BLIND_ACCESS"], 0)
        self.assertEqual(metrics["V81_AUTH_MAX_REMAINING_STEPS"], 76)
        self.assertEqual(metrics["V81_AUTH_MAX_REMAINING_EXPOSURE"], 583682)

    def test_authorization_write_requires_explicit_flag(self):
        source = AUTH.read_text(encoding="utf-8")
        self.assertIn('if args.write and not args.authorize:', source)
        self.assertIn('fail("--write requires explicit --authorize")', source)

    def test_launcher_requires_double_live_gate(self):
        source = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--execute", action="store_true")', source)
        self.assertIn(
            'os.environ.get("MINI_KUZAI_V81_TRAINING_ENABLED") != "YES"',
            source,
        )
        self.assertIn('"--resume"', source)
        self.assertIn('"TRAINING_STARTED=0"', source)

    def test_launcher_progress_monitor_is_live_and_non_scientific(self):
        source = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("def _progress_bar(", source)
        self.assertIn("def _monitor_training(", source)
        self.assertIn("subprocess.Popen(", source)
        self.assertIn('RUN / "metrics.jsonl"', source)
        self.assertIn("V81 VERIFY_RUNTIME", source)
        self.assertIn("V81 TRAIN", source)
        self.assertNotIn("from tqdm", source)

    def test_progress_jsonl_reader_preserves_partial_line(self):
        spec = importlib.util.spec_from_file_location("v81_launcher", LAUNCHER)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "metrics.jsonl"
            path.write_bytes(
                b'{"type":"train_step","step":70,"exposure_tokens":600000'
            )

            rows, offset, carry = module._read_appended_jsonl(
                path,
                0,
                b"",
            )
            self.assertEqual(rows, [])
            self.assertTrue(carry)

            with path.open("ab") as handle:
                handle.write(b',"train_loss":4.1}\n')

            rows, offset, carry = module._read_appended_jsonl(
                path,
                offset,
                carry,
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["step"], 70)
            self.assertEqual(rows[0]["exposure_tokens"], 600000)
            self.assertEqual(carry, b"")

    def test_authorization_producer_never_starts_training(self):
        tree = ast.parse(AUTH.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertNotIn("subprocess", imported)
        self.assertNotIn("torch", imported)

    def test_public_audit_and_gogit_registration(self):
        self.assertTrue(AUDIT.is_file())

        spec = importlib.util.spec_from_file_location("gogit_v81_auth", GOGIT)
        gogit = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(gogit)

        expected = {
            "SEMANTIC_VALIDATION_COMPLETE",
            "TRAINING_AUTHORIZED",
            "TRAINING_STARTED",
            "V81_AUTH_PASS",
            "V81_AUTH_BLIND_ACCESS",
            "V81_AUTH_RESUME_REQUIRED",
            "V81_AUTH_START_STEPS",
            "V81_AUTH_START_EXPOSURE",
            "V81_AUTH_MAX_TOTAL_STEPS",
            "V81_AUTH_MAX_TOTAL_EXPOSURE",
            "V81_AUTH_MAX_REMAINING_STEPS",
            "V81_AUTH_MAX_REMAINING_EXPOSURE",
            "V81_AUTH_FINAL_REVIEW_CYCLE",
            "V81_AUTH_OBJECTIVE_CHANGES",
            "V81_AUTH_TOKENIZER_CHANGES",
            "V81_AUTH_ARCHITECTURE_CHANGES",
            "V81_AUTH_CORPUS_CHANGES",
            "V81_AUTH_STREAM_WEIGHT_CHANGES",
            "V81_AUTH_SCHEDULER_CHANGES",
            "V81_AUTH_EXTENSION_BEYOND_CYCLE4",
        }
        self.assertTrue(expected <= gogit.METRIC_KEYS)
        self.assertEqual(
            gogit.source_for_audit(
                "tools/public-audits/"
                "phase03_v81_v62_continuation_authorization_001.py"
            ),
            "Mini-Kuzai V81 bounded V62 continuation training authorization",
        )


if __name__ == "__main__":
    unittest.main()
