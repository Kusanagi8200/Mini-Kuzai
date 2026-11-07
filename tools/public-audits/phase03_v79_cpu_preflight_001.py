#!/usr/bin/env python3
"""V79 CPU-only implementation and safety preflight for GOGIT.

Runs only the frozen V79 CPU regression suite and immutable provenance checks.
No CUDA model execution, training, BLIND access or scientific V79 GOGIT run.
"""
from __future__ import annotations

import ast
import io
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "tests"
TEST_PATTERN = "test_phase03_v79_same_path_context_order_control_001.py"
CORE = ROOT / "tools" / "v79_same_path_context_order_control.py"
SCIENTIFIC_AUDIT = (
    ROOT
    / "tools"
    / "public-audits"
    / "phase03_v79_same_path_context_order_control_001.py"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.md"
)
RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V79-start.json"
SCIENTIFIC_HISTORY = (
    ROOT
    / "reports"
    / "assistant-results"
    / "history"
    / "PHASE03-SMOLTALK-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.json"
)


def load_core():
    spec = importlib.util.spec_from_file_location("v79_preflight_core", CORE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V79 core import unavailable")
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
                raise RuntimeError("V79 GOGIT metric allowlist malformed")
            return value
    raise RuntimeError("V79 GOGIT metric allowlist missing")


def main():
    for path in (CORE, SCIENTIFIC_AUDIT, GOGIT, PROTOCOL, RECEIPT):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("V79 preflight source missing or unsafe")

    if SCIENTIFIC_HISTORY.exists():
        raise RuntimeError(
            "V79 scientific GOGIT already exists; CPU preflight sequence changed"
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
        raise RuntimeError("V79 CPU regression failed")

    core = load_core()
    core.verify_dependency_blobs()
    core.verify_start_receipt()
    v77 = core.verify_v77_report()
    v78 = core.verify_v78_report()
    keys = gogit_metric_keys()

    if not (
        total == 24
        and len(core.METRIC_FIELDS) == 30
        and set(core.METRIC_FIELDS) <= keys
        and v77["V77_PASS"] == 1
        and v77["V77_PRED_CHANGED"] == 5
        and v77["V77_ALPHA_SIGN_CHANGED"] == 5
        and v77["V77_PERTURBED_PREFIXES"] == 9062
        and v77["V77_UNCHANGED_PREFIXES"] == 108
        and v78["V78_PASS"] == 1
        and v78["V78_PATH_B_BATCH"] == 32
        and v78["V78_PATH_B_CORRECT"] == 2594
        and v78["V78_PATH_B_DISTINCT"] == 2
        and v78["V78_PATH_B_TOP1_SHARE_BP"] == 7043
        and v78["V78_PRED_CHANGED"] == 0
        and v78["V78_ALPHA_SIGN_CHANGED"] == 0
        and core.GPU_PEAK_LIMIT_MIB == 6144
        and core.SAME_PATH_BATCH == 32
        and core.SCORE_CHUNK == 512
        and core.PERTURBED_PREFIXES == 9062
        and core.UNCHANGED_PREFIXES == 108
        and core.DELTA_1E7 == 1e-7
        and core.DELTA_1E6 == 1e-6
        and core.DELTA_1E5 == 1e-5
    ):
        raise RuntimeError("V79 frozen CPU preflight invariant failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V79_PREFLIGHT_PASS": 1,
        "V79_PREFLIGHT_CPU_ONLY": 1,
        "V79_PREFLIGHT_TESTS_TOTAL": total,
        "V79_PREFLIGHT_TESTS_FAILED": len(result.failures),
        "V79_PREFLIGHT_TESTS_ERRORS": len(result.errors),
        "V79_PREFLIGHT_TESTS_SKIPPED": len(result.skipped),
        "V79_PREFLIGHT_START_RECEIPT": 1,
        "V79_PREFLIGHT_SCHEMA_FIELDS": len(core.METRIC_FIELDS),
        "V79_PREFLIGHT_ALLOWLIST_OK": 1,
        "V79_PREFLIGHT_PINS_OK": 1,
        "V79_PREFLIGHT_DEPENDENCIES_OK": 1,
        "V79_PREFLIGHT_GPU_EXECUTION": 0,
        "V79_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V79_PREFLIGHT_BLIND_ACCESS": 0,
        "V79_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V79_PREFLIGHT_GPU_LIMIT_MIB": core.GPU_PEAK_LIMIT_MIB,
        "V79_PREFLIGHT_SAME_PATH_BATCH": core.SAME_PATH_BATCH,
        "V79_PREFLIGHT_SCORE_CHUNK": core.SCORE_CHUNK,
        "V79_PREFLIGHT_V77_REPLAY": 1,
        "V79_PREFLIGHT_V78_REPLAY": 1,
    }

    if not (
        len(metrics) <= 30
        and all(
            type(v) is int and 0 <= v <= 100_000_000
            for v in metrics.values()
        )
        and set(metrics) <= keys
    ):
        raise RuntimeError("V79 preflight metric schema invalid")

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
