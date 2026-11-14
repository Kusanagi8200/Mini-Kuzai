#!/usr/bin/env python3
"""V83 CPU-only implementation and safety preflight for GOGIT.

Runs the V83 regression suite, provenance checks and CPU checkpoint
metadata/hash checks. No CUDA execution, training, BLIND access or scientific
V83 scoring occurs here.
"""
from __future__ import annotations

import ast
import hashlib
import io
import importlib.util
import subprocess
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "tests"
TEST_PATTERN = "test_phase03_v83_post_v81_refitted_coordinate_context_order_001.py"
CORE = ROOT / "tools/v83_post_v81_refitted_coordinate_context_order.py"
CORE_BLOB = "0ee59a66f20aef72536495e47f4d1176ce5ec4a8"
SCIENTIFIC_AUDIT = ROOT / "tools/public-audits/phase03_v83_post_v81_refitted_coordinate_context_order_001.py"
GOGIT = ROOT / "tools/gogit_public.py"
PROTOCOL = ROOT / "phases/MINI-KUZAI-PHASE-03-V83-POST-V81-REFITTED-COORDINATE-CONTEXT-ORDER-CONTROL-001.md"
RECEIPT = ROOT / "automation/dev-flow/receipts/V83-start.json"
V82_REPORT = ROOT / "reports/assistant-results/history/PHASE03-SMOLTALK-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001.json"
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
CYCLE2 = RUN / "checkpoint-cycle-02.pt"
LAST = RUN / "checkpoint-last.pt"
BEST = RUN / "checkpoint-best.pt"
SCIENTIFIC_HISTORY = ROOT / "reports/assistant-results/history/PHASE03-SMOLTALK-V83-POST-V81-REFITTED-COORDINATE-CONTEXT-ORDER-001.json"


def load_core():
    spec = importlib.util.spec_from_file_location("v83_preflight_core", CORE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V83 preflight core import unavailable")
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
        raise RuntimeError("V83 preflight Git blob calculation failed")
    return proc.stdout.strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gogit_metric_keys() -> set[str]:
    tree = ast.parse(GOGIT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "METRIC_KEYS"
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            if not isinstance(value, set):
                raise RuntimeError("V83 GOGIT metric allowlist malformed")
            return value
    raise RuntimeError("V83 GOGIT metric allowlist missing")


def checkpoint_metadata(path: Path, step: int, exposure: int) -> None:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("V83 checkpoint missing or unsafe")
    state = torch.load(path, map_location="cpu", weights_only=False)
    if not (
        isinstance(state, dict)
        and state.get("schema_version") == "v62-margin-checkpoint-1"
        and state.get("step") == step
        and state.get("exposure_tokens") == exposure
        and isinstance(state.get("model"), dict)
    ):
        raise RuntimeError("V83 checkpoint metadata mismatch")


def main():
    for path in (
        CORE,
        SCIENTIFIC_AUDIT,
        GOGIT,
        PROTOCOL,
        RECEIPT,
        V82_REPORT,
    ):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("V83 preflight source missing or unsafe")

    if git_blob(CORE) != CORE_BLOB:
        raise RuntimeError("V83 preflight core fingerprint mismatch")
    if SCIENTIFIC_HISTORY.exists():
        raise RuntimeError(
            "V83 scientific GOGIT already exists; CPU preflight sequence changed"
        )
    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("V83 runtime is missing, unsafe or training-locked")

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
        raise RuntimeError("V83 CPU regression failed")

    core = load_core()
    receipt = core.verify_start_receipt()
    v82 = core.verify_v82_report()

    checkpoint_metadata(CYCLE2, 69, 597982)
    checkpoint_metadata(LAST, 136, 1181302)
    if BEST.is_symlink() or not BEST.is_file() or BEST.stat().st_size == 0:
        raise RuntimeError("V83 best checkpoint missing or unsafe")

    cycle2_sha = sha256_file(CYCLE2)
    last_sha = sha256_file(LAST)
    best_sha = sha256_file(BEST)
    if not (
        len(cycle2_sha) == len(last_sha) == len(best_sha) == 64
        and cycle2_sha != last_sha
    ):
        raise RuntimeError("V83 checkpoint fingerprint gate failed")

    keys = gogit_metric_keys()
    if not (
        total == 14
        and len(core.METRIC_FIELDS) == 30
        and set(core.METRIC_FIELDS) <= keys
        and receipt["step"] == "V83"
        and v82["V82_PASS"] == 1
        and v82["V82_FINAL_PRED_CHANGED"] == 38
        and v82["V82_FINAL_SIGN_CHANGED"] == 38
        and v82["V82_BLIND_ACCESS"] == 0
        and core.SAME_PATH_BATCH == 32
        and core.VAL_LEXICAL == 9170
        and core.TRAIN_LEXICAL == 294726
    ):
        raise RuntimeError("V83 frozen CPU preflight invariant failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V83_PREFLIGHT_PASS": 1,
        "V83_PREFLIGHT_CPU_ONLY": 1,
        "V83_PREFLIGHT_TESTS_TOTAL": total,
        "V83_PREFLIGHT_TESTS_FAILED": len(result.failures),
        "V83_PREFLIGHT_TESTS_ERRORS": len(result.errors),
        "V83_PREFLIGHT_TESTS_SKIPPED": len(result.skipped),
        "V83_PREFLIGHT_START_RECEIPT": 1,
        "V83_PREFLIGHT_V82_REPORT": 1,
        "V83_PREFLIGHT_CHECKPOINT_CYCLE2": 1,
        "V83_PREFLIGHT_CHECKPOINT_LAST": 1,
        "V83_PREFLIGHT_CHECKPOINT_BEST": 1,
        "V83_PREFLIGHT_CHECKPOINT_HASHES": 1,
        "V83_PREFLIGHT_SCHEMA_FIELDS": len(core.METRIC_FIELDS),
        "V83_PREFLIGHT_ALLOWLIST_OK": 1,
        "V83_PREFLIGHT_GPU_EXECUTION": 0,
        "V83_PREFLIGHT_BLIND_ACCESS": 0,
        "V83_PREFLIGHT_TRAINING_AUTHORIZED": 0,
    }

    if not (
        len(metrics) <= 30
        and all(
            type(v) is int and 0 <= v <= 100_000_000
            for v in metrics.values()
        )
        and set(metrics) <= keys
    ):
        raise RuntimeError("V83 preflight metric schema invalid")

    print(f"V83_PREFLIGHT_CYCLE2_SHA256={cycle2_sha}")
    print(f"V83_PREFLIGHT_LAST_SHA256={last_sha}")
    print(f"V83_PREFLIGHT_BEST_SHA256={best_sha}")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
