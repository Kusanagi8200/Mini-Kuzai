#!/usr/bin/env python3
"""V76 CPU-only implementation and safety preflight for GOGIT.

Runs the frozen V76 CPU regression suite and immutable provenance checks.
No CUDA model execution, training, BLIND access or scientific V76 GOGIT runs.
"""
from __future__ import annotations

import ast
import io
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "tests"
TEST_PATTERN = "test_phase03_v76_frequency_residualized_pc1_control_001.py"
CORE = ROOT / "tools" / "v76_frequency_residualized_pc1_control.py"
SCIENTIFIC_AUDIT = (
    ROOT
    / "tools"
    / "public-audits"
    / "phase03_v76_frequency_residualized_pc1_control_001.py"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.md"
)
RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V76-start.json"
SCIENTIFIC_HISTORY = (
    ROOT
    / "reports"
    / "assistant-results"
    / "history"
    / "PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.json"
)


def load_core():
    spec = importlib.util.spec_from_file_location("v76_preflight_core", CORE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V76 core import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gogit_metric_keys() -> set[str]:
    tree = ast.parse(GOGIT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "METRIC_KEYS"
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            if not isinstance(value, set):
                raise RuntimeError("V76 GOGIT metric allowlist malformed")
            return value
    raise RuntimeError("V76 GOGIT metric allowlist missing")


def main():
    for path in (CORE, SCIENTIFIC_AUDIT, GOGIT, PROTOCOL, RECEIPT):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("V76 preflight source missing or unsafe")
    if SCIENTIFIC_HISTORY.exists():
        raise RuntimeError(
            "V76 scientific GOGIT already exists; CPU preflight sequence changed"
        )

    suite = unittest.defaultTestLoader.discover(
        str(TEST_DIR),
        pattern=TEST_PATTERN,
    )
    total = suite.countTestCases()
    buffer = io.StringIO()
    result = unittest.TextTestRunner(
        stream=buffer,
        verbosity=0,
    ).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("V76 CPU regression failed")

    core = load_core()
    core.verify_start_receipt()
    refs = core.verify_frozen_reports()
    keys = gogit_metric_keys()

    if not (
        total == 15
        and len(core.METRIC_FIELDS) == 30
        and set(core.METRIC_FIELDS) <= keys
        and refs["V75"]["V75_TRAIN_PC1_CORRECT"] == 2457
        and refs["V75"]["V75_TRAIN_PC1_VAR_SHARE_BP"] == 9019
        and refs["V75"]["V75_TRAIN_VAL_PC1_COS_ABS_BP"] == 9995
        and refs["V74_CORE"]["V74_CORE_UNIGRAM_CORRECT"] == 2535
        and core.GPU_PEAK_LIMIT_MIB == 6144
        and core.TRAIN_BATCH == 2
        and core.VAL_BATCH == 4
        and core.SCORE_CHUNK == 512
    ):
        raise RuntimeError("V76 frozen CPU preflight invariant failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V76_PREFLIGHT_PASS": 1,
        "V76_PREFLIGHT_CPU_ONLY": 1,
        "V76_PREFLIGHT_TESTS_TOTAL": total,
        "V76_PREFLIGHT_TESTS_FAILED": len(result.failures),
        "V76_PREFLIGHT_TESTS_ERRORS": len(result.errors),
        "V76_PREFLIGHT_TESTS_SKIPPED": len(result.skipped),
        "V76_PREFLIGHT_START_RECEIPT": 1,
        "V76_PREFLIGHT_SCHEMA_FIELDS": len(core.METRIC_FIELDS),
        "V76_PREFLIGHT_ALLOWLIST_OK": 1,
        "V76_PREFLIGHT_PINS_OK": 1,
        "V76_PREFLIGHT_DEPENDENCIES_OK": 1,
        "V76_PREFLIGHT_GPU_EXECUTION": 0,
        "V76_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V76_PREFLIGHT_BLIND_ACCESS": 0,
        "V76_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V76_PREFLIGHT_GPU_LIMIT_MIB": core.GPU_PEAK_LIMIT_MIB,
        "V76_PREFLIGHT_TRAIN_BATCH": core.TRAIN_BATCH,
        "V76_PREFLIGHT_VAL_BATCH": core.VAL_BATCH,
        "V76_PREFLIGHT_SCORE_CHUNK": core.SCORE_CHUNK,
    }
    if not (
        len(metrics) <= 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
        and set(metrics) <= keys
    ):
        raise RuntimeError("V76 preflight metric schema invalid")

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
