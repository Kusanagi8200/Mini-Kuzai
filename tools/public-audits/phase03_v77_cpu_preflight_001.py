#!/usr/bin/env python3
"""V77 CPU-only implementation and safety preflight for GOGIT.

Runs only the frozen V77 CPU regression suite and immutable provenance checks.
No CUDA model execution, training, BLIND access or scientific V77 GOGIT run.
"""
from __future__ import annotations

import ast
import io
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "tests"
TEST_PATTERN = "test_phase03_v77_residual_context_order_sensitivity_001.py"
CORE = ROOT / "tools" / "v77_residual_context_order_sensitivity.py"
SCIENTIFIC_AUDIT = (
    ROOT
    / "tools"
    / "public-audits"
    / "phase03_v77_residual_context_order_sensitivity_001.py"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.md"
)
RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V77-start.json"
SCIENTIFIC_HISTORY = (
    ROOT
    / "reports"
    / "assistant-results"
    / "history"
    / "PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.json"
)


def load_core():
    spec = importlib.util.spec_from_file_location("v77_preflight_core", CORE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V77 core import unavailable")
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
                raise RuntimeError("V77 GOGIT metric allowlist malformed")
            return value
    raise RuntimeError("V77 GOGIT metric allowlist missing")


def main():
    for path in (CORE, SCIENTIFIC_AUDIT, GOGIT, PROTOCOL, RECEIPT):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("V77 preflight source missing or unsafe")
    if SCIENTIFIC_HISTORY.exists():
        raise RuntimeError(
            "V77 scientific GOGIT already exists; CPU preflight sequence changed"
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
        raise RuntimeError("V77 CPU regression failed")

    core = load_core()
    core.verify_start_receipt()
    v76 = core.verify_v76_report()
    keys = gogit_metric_keys()

    if not (
        total == 18
        and len(core.METRIC_FIELDS) == 30
        and set(core.METRIC_FIELDS) <= keys
        and v76["V76_FREQ_RESIDUAL_CORRECT"] == 2594
        and v76["V76_FREQ_RESIDUAL_DISTINCT"] == 2
        and v76["V76_FREQ_RESIDUAL_TOP1_SHARE_BP"] == 7043
        and v76["V76_RESIDUAL_UNIGRAM_AGREE"] == 6458
        and v76["V76_RESIDUAL_UNIGRAM_SHARED_CORRECT"] == 2451
        and v76["V76_AXIS_FREQ_R2_BP"] == 775
        and v76["V76_RESIDUAL_ENERGY_SHARE_BP"] == 9225
        and core.GPU_PEAK_LIMIT_MIB == 6144
        and core.VAL_BATCH == 4
        and core.COUNTERFACTUAL_BATCH == 32
        and core.SCORE_CHUNK == 512
        and core.ALPHA_DELTA_THRESHOLD == 1e-7
    ):
        raise RuntimeError("V77 frozen CPU preflight invariant failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V77_PREFLIGHT_PASS": 1,
        "V77_PREFLIGHT_CPU_ONLY": 1,
        "V77_PREFLIGHT_TESTS_TOTAL": total,
        "V77_PREFLIGHT_TESTS_FAILED": len(result.failures),
        "V77_PREFLIGHT_TESTS_ERRORS": len(result.errors),
        "V77_PREFLIGHT_TESTS_SKIPPED": len(result.skipped),
        "V77_PREFLIGHT_START_RECEIPT": 1,
        "V77_PREFLIGHT_SCHEMA_FIELDS": len(core.METRIC_FIELDS),
        "V77_PREFLIGHT_ALLOWLIST_OK": 1,
        "V77_PREFLIGHT_PINS_OK": 1,
        "V77_PREFLIGHT_DEPENDENCIES_OK": 1,
        "V77_PREFLIGHT_GPU_EXECUTION": 0,
        "V77_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V77_PREFLIGHT_BLIND_ACCESS": 0,
        "V77_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V77_PREFLIGHT_GPU_LIMIT_MIB": core.GPU_PEAK_LIMIT_MIB,
        "V77_PREFLIGHT_VAL_BATCH": core.VAL_BATCH,
        "V77_PREFLIGHT_COUNTERFACTUAL_BATCH": core.COUNTERFACTUAL_BATCH,
        "V77_PREFLIGHT_SCORE_CHUNK": core.SCORE_CHUNK,
    }
    if not (
        len(metrics) <= 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
        and set(metrics) <= keys
    ):
        raise RuntimeError("V77 preflight metric schema invalid")

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
