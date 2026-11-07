#!/usr/bin/env python3
"""V78 CPU-only implementation and safety preflight for GOGIT.

Runs only the frozen V78 CPU regression suite and immutable provenance checks.
No CUDA model execution, training, BLIND access or scientific V78 GOGIT run.
"""
from __future__ import annotations

import ast
import io
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "tests"
TEST_PATTERN = "test_phase03_v78_identical_context_rebatching_numerical_control_001.py"
CORE = ROOT / "tools" / "v78_identical_context_rebatching_numerical_control.py"
SCIENTIFIC_AUDIT = (
    ROOT
    / "tools"
    / "public-audits"
    / "phase03_v78_identical_context_rebatching_numerical_control_001.py"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.md"
)
RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V78-start.json"
SCIENTIFIC_HISTORY = (
    ROOT
    / "reports"
    / "assistant-results"
    / "history"
    / "PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.json"
)


def load_core():
    spec = importlib.util.spec_from_file_location("v78_preflight_core", CORE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V78 core import unavailable")
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
                raise RuntimeError("V78 GOGIT metric allowlist malformed")
            return value
    raise RuntimeError("V78 GOGIT metric allowlist missing")


def main():
    for path in (CORE, SCIENTIFIC_AUDIT, GOGIT, PROTOCOL, RECEIPT):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("V78 preflight source missing or unsafe")

    if SCIENTIFIC_HISTORY.exists():
        raise RuntimeError(
            "V78 scientific GOGIT already exists; CPU preflight sequence changed"
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
        raise RuntimeError("V78 CPU regression failed")

    core = load_core()
    core.verify_dependency_blobs()
    core.verify_start_receipt()
    v77 = core.verify_v77_report()
    keys = gogit_metric_keys()

    if not (
        total == 20
        and len(core.METRIC_FIELDS) == 30
        and set(core.METRIC_FIELDS) <= keys
        and v77["V77_PASS"] == 1
        and v77["V77_FULL_CORRECT"] == 2594
        and v77["V77_REVERSE_CORRECT"] == 2594
        and v77["V77_PRED_CHANGED"] == 5
        and v77["V77_ALPHA_SIGN_CHANGED"] == 5
        and v77["V77_ALPHA_CORR_ABS_BP"] == 9999
        and v77["V77_ALPHA_DELTA_NONZERO"] == 9123
        and v77["V77_PERTURBED_PREFIXES"] == 9062
        and core.GPU_PEAK_LIMIT_MIB == 6144
        and core.PATH_A_BATCH == 4
        and core.PATH_B_BATCH == 32
        and core.SCORE_CHUNK == 512
        and core.DELTA_1E7 == 1e-7
        and core.DELTA_1E6 == 1e-6
        and core.DELTA_1E5 == 1e-5
    ):
        raise RuntimeError("V78 frozen CPU preflight invariant failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V78_PREFLIGHT_PASS": 1,
        "V78_PREFLIGHT_CPU_ONLY": 1,
        "V78_PREFLIGHT_TESTS_TOTAL": total,
        "V78_PREFLIGHT_TESTS_FAILED": len(result.failures),
        "V78_PREFLIGHT_TESTS_ERRORS": len(result.errors),
        "V78_PREFLIGHT_TESTS_SKIPPED": len(result.skipped),
        "V78_PREFLIGHT_START_RECEIPT": 1,
        "V78_PREFLIGHT_SCHEMA_FIELDS": len(core.METRIC_FIELDS),
        "V78_PREFLIGHT_ALLOWLIST_OK": 1,
        "V78_PREFLIGHT_PINS_OK": 1,
        "V78_PREFLIGHT_DEPENDENCIES_OK": 1,
        "V78_PREFLIGHT_GPU_EXECUTION": 0,
        "V78_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V78_PREFLIGHT_BLIND_ACCESS": 0,
        "V78_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V78_PREFLIGHT_GPU_LIMIT_MIB": core.GPU_PEAK_LIMIT_MIB,
        "V78_PREFLIGHT_PATH_A_BATCH": core.PATH_A_BATCH,
        "V78_PREFLIGHT_PATH_B_BATCH": core.PATH_B_BATCH,
        "V78_PREFLIGHT_SCORE_CHUNK": core.SCORE_CHUNK,
    }

    if not (
        len(metrics) <= 30
        and all(
            type(v) is int and 0 <= v <= 100_000_000
            for v in metrics.values()
        )
        and set(metrics) <= keys
    ):
        raise RuntimeError("V78 preflight metric schema invalid")

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
