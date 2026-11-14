#!/usr/bin/env python3
"""V82 CPU-only implementation and safety preflight for GOGIT.

Runs the V82 regression suite, immutable provenance checks and CPU checkpoint
metadata/hash checks. No CUDA execution, training, BLIND access or scientific
V82 scoring occurs here.
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
TEST_PATTERN = "test_phase03_v82_post_continuation_context_order_replication_001.py"
CORE = ROOT / "tools" / "v82_post_continuation_context_order_replication.py"
CORE_BLOB = "8de656ae9c52711049d7dd47861bf1124fa7dbf1"
SCIENTIFIC_AUDIT = ROOT / "tools" / "public-audits" / (
    "phase03_v82_post_continuation_context_order_replication_001.py"
)
GOGIT = ROOT / "tools" / "gogit_public.py"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001.md"
)
RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V82-start.json"
V81_FINAL = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V81-FINAL-CLOSURE-001.json"
)
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
CYCLE2 = RUN / "checkpoint-cycle-02.pt"
LAST = RUN / "checkpoint-last.pt"
BEST = RUN / "checkpoint-best.pt"
SCIENTIFIC_HISTORY = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001.json"
)


def load_core():
    spec = importlib.util.spec_from_file_location("v82_preflight_core", CORE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V82 core import unavailable")
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
        raise RuntimeError("V82 preflight Git blob calculation failed")
    return proc.stdout.strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
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
                raise RuntimeError("V82 GOGIT metric allowlist malformed")
            return value
    raise RuntimeError("V82 GOGIT metric allowlist missing")


def checkpoint_metadata(path: Path, step: int, exposure: int) -> None:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("V82 checkpoint missing or unsafe")
    state = torch.load(path, map_location="cpu", weights_only=False)
    if not (
        isinstance(state, dict)
        and state.get("schema_version") == "v62-margin-checkpoint-1"
        and state.get("step") == step
        and state.get("exposure_tokens") == exposure
        and isinstance(state.get("model"), dict)
    ):
        raise RuntimeError("V82 checkpoint metadata mismatch")


def main():
    for path in (
        CORE,
        SCIENTIFIC_AUDIT,
        GOGIT,
        PROTOCOL,
        RECEIPT,
        V81_FINAL,
    ):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("V82 preflight source missing or unsafe")

    if git_blob(CORE) != CORE_BLOB:
        raise RuntimeError("V82 preflight core fingerprint mismatch")
    if SCIENTIFIC_HISTORY.exists():
        raise RuntimeError(
            "V82 scientific GOGIT already exists; CPU preflight sequence changed"
        )
    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("V82 runtime is missing, unsafe or training-locked")

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
        raise RuntimeError("V82 CPU regression failed")

    core = load_core()
    receipt = core.verify_start_receipt()
    closure = core.verify_v81_closure()

    checkpoint_metadata(CYCLE2, 69, 597982)
    checkpoint_metadata(LAST, 136, 1181302)
    if BEST.is_symlink() or not BEST.is_file():
        raise RuntimeError("V82 best checkpoint missing or unsafe")

    cycle2_sha = sha256_file(CYCLE2)
    last_sha = sha256_file(LAST)
    best_sha = sha256_file(BEST)
    if not (
        len(cycle2_sha) == len(last_sha) == len(best_sha) == 64
        and cycle2_sha != last_sha
    ):
        raise RuntimeError("V82 checkpoint fingerprint gate failed")

    keys = gogit_metric_keys()
    if not (
        total == 12
        and len(core.METRIC_FIELDS) == 30
        and set(core.METRIC_FIELDS) <= keys
        and receipt["step"] == "V82"
        and closure["V81_FINAL_PASS"] == 1
        and closure["V81_FINAL_BLIND_ACCESS"] == 0
        and closure["V81_FINAL_FURTHER_TRAINING_AUTHORIZED"] == 0
        and core.SAME_PATH_BATCH == 32
        and core.VAL_LEXICAL == 9170
        and core.V80_PERTURBED == 9062
        and core.V80_UNCHANGED == 108
    ):
        raise RuntimeError("V82 frozen CPU preflight invariant failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V82_PREFLIGHT_PASS": 1,
        "V82_PREFLIGHT_CPU_ONLY": 1,
        "V82_PREFLIGHT_TESTS_TOTAL": total,
        "V82_PREFLIGHT_TESTS_FAILED": len(result.failures),
        "V82_PREFLIGHT_TESTS_ERRORS": len(result.errors),
        "V82_PREFLIGHT_TESTS_SKIPPED": len(result.skipped),
        "V82_PREFLIGHT_START_RECEIPT": 1,
        "V82_PREFLIGHT_V81_CLOSURE": 1,
        "V82_PREFLIGHT_CHECKPOINT_CYCLE2": 1,
        "V82_PREFLIGHT_CHECKPOINT_LAST": 1,
        "V82_PREFLIGHT_CHECKPOINT_BEST": 1,
        "V82_PREFLIGHT_CHECKPOINT_HASHES": 1,
        "V82_PREFLIGHT_SCHEMA_FIELDS": len(core.METRIC_FIELDS),
        "V82_PREFLIGHT_ALLOWLIST_OK": 1,
        "V82_PREFLIGHT_BASELINE_PINS": 1,
        "V82_PREFLIGHT_GPU_EXECUTION": 0,
        "V82_PREFLIGHT_BLIND_ACCESS": 0,
        "V82_PREFLIGHT_TRAINING_AUTHORIZED": 0,
    }

    if not (
        len(metrics) <= 30
        and all(
            type(v) is int and 0 <= v <= 100_000_000
            for v in metrics.values()
        )
        and set(metrics) <= keys
    ):
        raise RuntimeError("V82 preflight metric schema invalid")

    print(f"V82_PREFLIGHT_CYCLE2_SHA256={cycle2_sha}")
    print(f"V82_PREFLIGHT_LAST_SHA256={last_sha}")
    print(f"V82_PREFLIGHT_BEST_SHA256={best_sha}")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
