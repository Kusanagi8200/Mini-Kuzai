#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "tools" / "public-audits" / "phase03_v75_final_preflight_001.py"
GOGIT = ROOT / "tools" / "gogit_public.py"

EXPECTED_KEYS = {
    "SEMANTIC_VALIDATION_COMPLETE",
    "TRAINING_AUTHORIZED",
    "TRAINING_STARTED",
    "V75_FINAL_PREFLIGHT_PASS",
    "V75_FINAL_PREFLIGHT_BLIND_ACCESS",
    "V75_FINAL_PREFLIGHT_REPORT_FIELDS",
    "V75_FINAL_PREFLIGHT_REPORT_VERIFIED",
    "V75_FINAL_PREFLIGHT_START_RECEIPT",
    "V75_FINAL_PREFLIGHT_DISCUSSION_PRESENT",
    "V75_FINAL_PREFLIGHT_CLOSURE_READY",
    "V75_FINAL_PREFLIGHT_PUBLICATION_DISABLED",
    "V75_FINAL_PREFLIGHT_REQUEST_PRESENT",
    "V75_FINAL_PREFLIGHT_RECEIPT_PRESENT",
    "V75_FINAL_PREFLIGHT_FINAL_AUTHORIZED",
    "V75_FINAL_PREFLIGHT_V75_PASS",
    "V75_FINAL_PREFLIGHT_COVERAGE_BP",
}


class V75FinalPreflightTests(unittest.TestCase):
    def test_audit_is_read_only_and_pinned_to_v75_scientific_report(self):
        source = AUDIT.read_text(encoding="utf-8")
        self.assertIn(
            "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json",
            source,
        )
        self.assertIn('"--action",\n            "close"', source)
        self.assertNotIn('"--publish",', source)
        self.assertIn('FINAL_REQUEST.exists() or FINAL_RECEIPT.exists()', source)
        for forbidden in (
            ".write_text(",
            ".write_bytes(",
            "unlink(",
            "git push",
            "create_discussion",
            "addDiscussionComment",
        ):
            self.assertNotIn(forbidden, source)

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
        self.assertTrue(EXPECTED_KEYS <= keys)

        spec = importlib.util.spec_from_file_location("v75_final_gogit_test", GOGIT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(
            module.source_for_audit(
                "tools/public-audits/phase03_v75_final_preflight_001.py"
            ),
            "Mini-Kuzai V75 FINAL DEV-FLOW read-only preflight",
        )


if __name__ == "__main__":
    unittest.main()
