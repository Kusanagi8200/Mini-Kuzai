#!/usr/bin/env python3
"""V80 CPU-only implementation and safety preflight for GOGIT.

Runs only the frozen V80 CPU regression suite and immutable provenance checks.
No CUDA model execution, training, BLIND access or scientific V80 GOGIT run.
"""
from __future__ import annotations

import ast
import io
import importlib.util
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "tests"
TEST_PATTERN = "test_phase03_v80_decision_boundary_proximity_control_001.py"
CORE = ROOT / "tools" / "v80_decision_boundary_proximity_control.py"
CORE_BLOB = "3f395ed8eeaab0caf957323ecd438dc83b5d14dc"
SCIENTIFIC_AUDIT = (
    ROOT
    / "tools"
    / "public-audits"
    / "phase03_v80_decision_boundary_proximity_control_001.py"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V80-DECISION-BOUNDARY-PROXIMITY-CONTROL-001.md"
)
RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V80-start.json"
SCIENTIFIC_HISTORY = (
    ROOT
    / "reports"
    / "assistant-results"
    / "history"
    / "PHASE03-SMOLTALK-V80-DECISION-BOUNDARY-PROXIMITY-CONTROL-001.json"
)


def load_core():
    spec = importlib.util.spec_from_file_location("v80_preflight_core", CORE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V80 core import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_blob(path: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError("V80 preflight Git blob calculation failed")
    return proc.stdout.strip()


def gogit_metric_keys() -> set[str]:
    tree = ast.parse(GOGIT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "METRIC_KEYS"
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            if not isinstance(value, set):
                raise RuntimeError("V80 GOGIT metric allowlist malformed")
            return value
    raise RuntimeError("V80 GOGIT metric allowlist missing")


def main():
    for path in (CORE, SCIENTIFIC_AUDIT, GOGIT, PROTOCOL, RECEIPT):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("V80 preflight source missing or unsafe")

    if git_blob(CORE) != CORE_BLOB:
        raise RuntimeError("V80 preflight core fingerprint mismatch")

    if SCIENTIFIC_HISTORY.exists():
        raise RuntimeError(
            "V80 scientific GOGIT already exists; CPU preflight sequence changed"
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
        raise RuntimeError("V80 CPU regression failed")

    core = load_core()
    core.verify_dependency_blobs()
    core.verify_start_receipt()
    v79 = core.verify_v79_report()
    keys = gogit_metric_keys()

    if not (
        total == 18
        and len(core.METRIC_FIELDS) == 30
        and set(core.METRIC_FIELDS) <= keys
        and v79["V79_PASS"] == 1
        and v79["V79_PRED_CHANGED"] == 5
        and v79["V79_ALPHA_SIGN_CHANGED"] == 5
        and v79["V79_ORIGINAL_CORRECT"] == 2594
        and v79["V79_REVERSE_CORRECT"] == 2594
        and core.GPU_PEAK_LIMIT_MIB == 6144
        and core.SAME_PATH_BATCH == 32
        and core.SCORE_CHUNK == 512
        and core.PERTURBED_PREFIXES == 9062
        and core.UNCHANGED_PREFIXES == 108
        and core.THRESHOLDS == (1e-7, 1e-6, 1e-5, 1e-4, 1e-3)
        and core.ALPHA_NANO_LIMIT == 2_000_000_000
    ):
        raise RuntimeError("V80 frozen CPU preflight invariant failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V80_PREFLIGHT_PASS": 1,
        "V80_PREFLIGHT_CPU_ONLY": 1,
        "V80_PREFLIGHT_TESTS_TOTAL": total,
        "V80_PREFLIGHT_TESTS_FAILED": len(result.failures),
        "V80_PREFLIGHT_TESTS_ERRORS": len(result.errors),
        "V80_PREFLIGHT_TESTS_SKIPPED": len(result.skipped),
        "V80_PREFLIGHT_START_RECEIPT": 1,
        "V80_PREFLIGHT_SCHEMA_FIELDS": len(core.METRIC_FIELDS),
        "V80_PREFLIGHT_ALLOWLIST_OK": 1,
        "V80_PREFLIGHT_PINS_OK": 1,
        "V80_PREFLIGHT_V79_REPLAY": 1,
        "V80_PREFLIGHT_GPU_EXECUTION": 0,
        "V80_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V80_PREFLIGHT_BLIND_ACCESS": 0,
        "V80_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V80_PREFLIGHT_GPU_LIMIT_MIB": core.GPU_PEAK_LIMIT_MIB,
        "V80_PREFLIGHT_SAME_PATH_BATCH": core.SAME_PATH_BATCH,
        "V80_PREFLIGHT_SCORE_CHUNK": core.SCORE_CHUNK,
        "V80_PREFLIGHT_THRESHOLDS": len(core.THRESHOLDS),
    }

    if not (
        len(metrics) <= 30
        and all(
            type(v) is int and 0 <= v <= 100_000_000
            for v in metrics.values()
        )
        and set(metrics) <= keys
    ):
        raise RuntimeError("V80 preflight metric schema invalid")

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
