#!/usr/bin/env python3
"""Pinned V77 read-only GPU audit and immutable numeric GOGIT publication.

Execution is authorized only for the frozen V77 context-order sensitivity
control. This runner never trains, never opens BLIND, never writes a checkpoint
and publishes only the frozen 30-integer V77 aggregate schema.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
HISTORY_DIR = ROOT / "reports" / "assistant-results" / "history"

SOURCE = "tools/v77_residual_context_order_sensitivity.py"
SOURCE_BLOB = "941df566949291c55da1b4c6b0b6c63ad52dbd37"
AUDIT = "tools/public-audits/phase03_v77_residual_context_order_sensitivity_001.py"
AUDIT_BLOB = "827fc7d69702247f7043ba70ad2ad23e40328a3f"
GOGIT = "tools/gogit_public.py"
GOGIT_BLOB = "488803536bee3d73d6256e1e8e7cb1e878e24a99"
PROTOCOL = "phases/MINI-KUZAI-PHASE-03-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.md"
PROTOCOL_BLOB = "12601e2da0627aceabb3ccd28702db2833374963"
CPU_PREFLIGHT = (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V77-CPU-PREFLIGHT-001.json"
)
CPU_PREFLIGHT_BLOB = "034d1958c751c95f3b03751a6ce52e83c8c5f660"
TEST = "test_phase03_v77_residual_context_order_sensitivity_001.py"
TEST_BLOB = "0d6f388e22e951a6fb52afffca89a4dcd5194e91"
START_RECEIPT = "automation/dev-flow/receipts/V77-start.json"
START_RECEIPT_BLOB = "ae4be23571fb98b09ba01d3163daf0bf1cc88b3f"
STEP = "PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001"
SOURCE_LABEL = "Mini-Kuzai V77 frozen residual context-order sensitivity control"
HISTORY = HISTORY_DIR / (STEP + ".json")

ORIGINS = {
    "https://github.com/Kusanagi8200/Mini-Kuzai.git",
    "https://github.com/Kusanagi8200/Mini-Kuzai",
    "git@github.com:Kusanagi8200/Mini-Kuzai.git",
}
SAFE = ("SEMANTIC_VALIDATION_COMPLETE", "TRAINING_AUTHORIZED", "TRAINING_STARTED")


def git(*args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode:
        raise RuntimeError("V77 Git validation failed")
    return p.stdout.strip()


def synced() -> None:
    if (
        git("branch", "--show-current") != "main"
        or git("remote", "get-url", "origin") not in ORIGINS
        or git("status", "--porcelain")
    ):
        raise RuntimeError("V77 requires clean main and approved Git origin")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("V77 local and remote main differ")


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V77 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V77 expected JSON object")
    return value


def pinned_sources() -> None:
    for path, blob in (
        (SOURCE, SOURCE_BLOB),
        (AUDIT, AUDIT_BLOB),
        (GOGIT, GOGIT_BLOB),
        (PROTOCOL, PROTOCOL_BLOB),
        (CPU_PREFLIGHT, CPU_PREFLIGHT_BLOB),
        ("tests/" + TEST, TEST_BLOB),
        (START_RECEIPT, START_RECEIPT_BLOB),
    ):
        file = ROOT / path
        if not file.is_file() or file.is_symlink():
            raise RuntimeError("V77 pinned source missing or unsafe")
        if git("rev-parse", "HEAD:" + path) != blob:
            raise RuntimeError("V77 reviewed Git source blob changed")


def verify_cpu_preflight() -> None:
    report = read_json(ROOT / CPU_PREFLIGHT)
    metrics = report.get("metrics")
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V77_PREFLIGHT_PASS": 1,
        "V77_PREFLIGHT_CPU_ONLY": 1,
        "V77_PREFLIGHT_TESTS_TOTAL": 18,
        "V77_PREFLIGHT_TESTS_FAILED": 0,
        "V77_PREFLIGHT_TESTS_ERRORS": 0,
        "V77_PREFLIGHT_TESTS_SKIPPED": 0,
        "V77_PREFLIGHT_START_RECEIPT": 1,
        "V77_PREFLIGHT_SCHEMA_FIELDS": 30,
        "V77_PREFLIGHT_ALLOWLIST_OK": 1,
        "V77_PREFLIGHT_PINS_OK": 1,
        "V77_PREFLIGHT_DEPENDENCIES_OK": 1,
        "V77_PREFLIGHT_GPU_EXECUTION": 0,
        "V77_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V77_PREFLIGHT_BLIND_ACCESS": 0,
        "V77_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V77_PREFLIGHT_GPU_LIMIT_MIB": 6144,
        "V77_PREFLIGHT_VAL_BATCH": 4,
        "V77_PREFLIGHT_COUNTERFACTUAL_BATCH": 32,
        "V77_PREFLIGHT_SCORE_CHUNK": 512,
    }
    if not (
        report.get("step_id") == "PHASE03-SMOLTALK-V77-CPU-PREFLIGHT-001"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and all(metrics.get(k) == v for k, v in expected.items())
    ):
        raise RuntimeError("V77 CPU preflight integrity gate failed")


def preflight() -> None:
    if not PYTHON.is_file() or not os.access(PYTHON, os.X_OK):
        raise RuntimeError("V77 Python interpreter missing or not executable")
    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("V77 frozen V62 run missing or locked")

    summary = read_json(RUN / "RUN-SUMMARY.json")
    manifest = read_json(RUN / "RUN-MANIFEST.json")
    checkpoint = RUN / "checkpoint-cycle-02.pt"
    if not (
        summary.get("schema_version") == "v62-margin-run-summary-1"
        and manifest.get("schema_version") == "v62-margin-run-1"
        and summary.get("status") == manifest.get("status") == "STOPPED"
        and summary.get("stop_reason") == "MILESTONE_REVIEW_REQUIRED"
        and summary.get("optimizer_steps") == 69
        and summary.get("exposure_tokens") == 597982
        and summary.get("blind_test_accessed") is False
        and manifest.get("blind_test_during_training") is False
        and manifest.get("resume") is False
        and checkpoint.is_file()
        and not checkpoint.is_symlink()
    ):
        raise RuntimeError("V77 V62 frozen checkpoint/stop gate failed")

    receipt = read_json(ROOT / START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V77"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/8"
        and receipt.get("source_commit")
        == "2bdce4c378cef45d22b164a99b6b3e191e104965"
    ):
        raise RuntimeError("V77 official START receipt absent or invalid")

    verify_cpu_preflight()

    active = subprocess.run(
        ["systemctl", "is-active", "llama-server-a.service"],
        capture_output=True,
        text=True,
        check=False,
    )
    if active.stdout.strip() == "active":
        raise RuntimeError("V77 GPU occupied by llama-server-a; stop separately")


def validate_history() -> dict:
    report = read_json(HISTORY)
    metrics = report.get("metrics")
    audit_path = ROOT / AUDIT
    fixed = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V77_PASS": 1,
        "V77_BLIND_ACCESS": 0,
        "V77_VAL_LEXICAL": 9170,
        "V77_HIDDEN_DIM": 128,
        "V77_VOCAB": 1024,
        "V77_FULL_CORRECT": 2594,
        "V77_FULL_DISTINCT": 2,
        "V77_FULL_TOP1_SHARE_BP": 7043,
        "V77_FULL_UNIGRAM_AGREE": 6458,
        "V77_FULL_UNIGRAM_SHARED_CORRECT": 2451,
        "V77_COVERAGE_BP": 10000,
    }
    if not (
        report.get("step_id") == STEP
        and report.get("source") == SOURCE_LABEL
        and report.get("producer") == AUDIT
        and report.get("producer_sha256")
        == hashlib.sha256(audit_path.read_bytes()).hexdigest()
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
        and all(metrics.get(k) == v for k, v in fixed.items())
        and all(metrics.get(k) == 0 for k in SAFE)
        and 0 <= metrics.get("V77_REVERSE_CORRECT", -1) <= 9170
        and 1 <= metrics.get("V77_REVERSE_DISTINCT", 0) <= 1024
        and 0 <= metrics.get("V77_REVERSE_TOP1_SHARE_BP", -1) <= 10000
        and 0 <= metrics.get("V77_REVERSE_UNIGRAM_AGREE", -1) <= 9170
        and 0 <= metrics.get("V77_REVERSE_UNIGRAM_SHARED_CORRECT", -1)
        <= min(
            metrics.get("V77_REVERSE_CORRECT", -1),
            metrics.get("V77_REVERSE_UNIGRAM_AGREE", -1),
            2535,
        )
        and metrics.get("V77_PRED_AGREE", -1)
        + metrics.get("V77_PRED_CHANGED", -1) == 9170
        and metrics.get("V77_ALPHA_SIGN_AGREE", -1)
        + metrics.get("V77_ALPHA_SIGN_CHANGED", -1) == 9170
        and metrics.get("V77_PERTURBED_PREFIXES", -1)
        + metrics.get("V77_UNCHANGED_PREFIXES", -1) == 9170
        and metrics.get("V77_FULL_REVERSE_SHARED_CORRECT", -1)
        + metrics.get("V77_FULL_ONLY_CORRECT", -1) == 2594
        and metrics.get("V77_FULL_REVERSE_SHARED_CORRECT", -1)
        + metrics.get("V77_REVERSE_ONLY_CORRECT", -1)
        == metrics.get("V77_REVERSE_CORRECT", -2)
        and 0 <= metrics.get("V77_ALPHA_CORR_ABS_BP", -1) <= 10000
        and 0 <= metrics.get("V77_ALPHA_DELTA_NONZERO", -1) <= 9170
        and 0 <= metrics.get("V77_FULL_REVERSE_SHARED_CORRECT", -1) <= 2594
        and 0 <= metrics.get("V77_FULL_ONLY_CORRECT", -1) <= 2594
        and 0 <= metrics.get("V77_REVERSE_ONLY_CORRECT", -1) <= 9170
    ):
        raise RuntimeError("V77 published GOGIT integrity gate failed")
    return metrics


def checked(cmd: list[str], label: str) -> None:
    p = subprocess.run(cmd, cwd=ROOT, check=False)
    if p.returncode:
        raise RuntimeError(label + " failed, exit " + str(p.returncode))


def main() -> None:
    synced()
    pinned_sources()
    preflight()

    if HISTORY.exists():
        validate_history()
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V77_GOGIT=ALREADY_VERIFIED")
        print("STEP_ID=" + STEP)
        print("TRAINING_STARTED=0")
        print("BLIND_ACCESS=0")
        print("FINAL_DEV_FLOW=NOT_TRIGGERED")
        print("HEAD=" + git("rev-parse", "--short", "HEAD"))
        return

    checked(
        [
            str(PYTHON),
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            TEST,
            "-v",
        ],
        "V77 CPU regression",
    )
    synced()
    pinned_sources()
    preflight()

    checked(
        [
            str(PYTHON),
            GOGIT,
            "--step",
            STEP,
            "--audit",
            AUDIT,
        ],
        "V77 GOGIT",
    )

    synced()
    pinned_sources()
    validate_history()

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V77_GOGIT=PUBLISHED_AND_VERIFIED")
    print("STEP_ID=" + STEP)
    print("TRAINING_STARTED=0")
    print("BLIND_ACCESS=0")
    print("FINAL_DEV_FLOW=NOT_TRIGGERED")
    print("HEAD=" + git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError, KeyboardInterrupt) as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V77_GOGIT=BLOCKED")
        print("ERROR_TYPE=" + type(exc).__name__)
        print("ERROR=" + str(exc))
        sys.exit(1)
