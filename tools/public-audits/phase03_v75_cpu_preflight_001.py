#!/usr/bin/env python3
"""V75 CPU-only implementation preflight for GOGIT.

Runs the frozen V75 CPU regression suite and emits numeric aggregate status only.
No CUDA model execution, training, BLIND access or scientific V75 GOGIT is run.
"""
from __future__ import annotations

import io
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "tests"
TEST_PATTERN = "test_phase03_v75_train_fitted_geometry_transfer_001.py"
CORE = ROOT / "tools" / "v75_train_fitted_geometry_transfer.py"
RUNNER = ROOT / "tools" / "run_v75_train_fitted_geometry_transfer_001_job.py"
GOGIT = ROOT / "tools" / "gogit_public.py"
PROTOCOL = ROOT / "phases" / "MINI-KUZAI-PHASE-03-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.md"
RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V75-start.json"
SCIENTIFIC_HISTORY = (
    ROOT
    / "reports"
    / "assistant-results"
    / "history"
    / "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json"
)


def load_core():
    spec = importlib.util.spec_from_file_location("v75_preflight_core", CORE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V75 core import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    for path in (CORE, RUNNER, GOGIT, PROTOCOL, RECEIPT):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("V75 preflight source missing or unsafe")
    if SCIENTIFIC_HISTORY.exists():
        raise RuntimeError("V75 scientific GOGIT already exists; CPU preflight sequence changed")

    suite = unittest.defaultTestLoader.discover(
        str(TEST_DIR), pattern=TEST_PATTERN
    )
    total = suite.countTestCases()
    buffer = io.StringIO()
    result = unittest.TextTestRunner(
        stream=buffer, verbosity=0
    ).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("V75 CPU regression failed")

    core = load_core()
    core.verify_start_receipt()
    refs = core.prerequisites()
    if not (
        total == 13
        and refs["V65"]["V65_FREQ_TRAIN_LEXICAL"] == 294726
        and refs["V73"]["V73_AXIS_PC1_ONLY_CORRECT"] == 2455
        and refs["V74_CORE"]["V74_CORE_UNIGRAM_CORRECT"] == 2535
        and refs["V74_STRATA"]["V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT"] == 2449
        and len(core.METRIC_FIELDS) == 30
        and core.GPU_PEAK_LIMIT_MIB == 6144
        and core.TRAIN_BATCH == 2
        and core.VAL_BATCH == 4
        and core.SCORE_CHUNK == 512
    ):
        raise RuntimeError("V75 frozen CPU preflight invariant failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V75_PREFLIGHT_PASS": 1,
        "V75_PREFLIGHT_CPU_ONLY": 1,
        "V75_PREFLIGHT_TESTS_TOTAL": total,
        "V75_PREFLIGHT_TESTS_FAILED": len(result.failures),
        "V75_PREFLIGHT_TESTS_ERRORS": len(result.errors),
        "V75_PREFLIGHT_TESTS_SKIPPED": len(result.skipped),
        "V75_PREFLIGHT_START_RECEIPT": 1,
        "V75_PREFLIGHT_SCHEMA_FIELDS": len(core.METRIC_FIELDS),
        "V75_PREFLIGHT_ALLOWLIST_OK": 1,
        "V75_PREFLIGHT_PINS_OK": 1,
        "V75_PREFLIGHT_GPU_EXECUTION": 0,
        "V75_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V75_PREFLIGHT_BLIND_ACCESS": 0,
        "V75_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V75_PREFLIGHT_GPU_LIMIT_MIB": core.GPU_PEAK_LIMIT_MIB,
        "V75_PREFLIGHT_TRAIN_BATCH": core.TRAIN_BATCH,
        "V75_PREFLIGHT_VAL_BATCH": core.VAL_BATCH,
        "V75_PREFLIGHT_SCORE_CHUNK": core.SCORE_CHUNK,
    }
    if any(type(v) is not int or not 0 <= v <= 100_000_000 for v in metrics.values()):
        raise RuntimeError("V75 preflight metric type/range invalid")

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
