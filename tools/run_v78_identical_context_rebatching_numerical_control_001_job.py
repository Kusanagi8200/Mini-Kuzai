#!/usr/bin/env python3
"""Pinned V78 read-only GPU audit and immutable numeric GOGIT publication.

Authorized scope: V78 identical-context rebatching numerical control only.
This runner never trains, never opens BLIND, never generates text, never writes
a checkpoint and publishes only the frozen 30-integer V78 aggregate schema.
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

SOURCE = "tools/v78_identical_context_rebatching_numerical_control.py"
SOURCE_BLOB = "4aa901d9a27d03e48e8099fb21799aa8e7cead9e"
AUDIT = "tools/public-audits/phase03_v78_identical_context_rebatching_numerical_control_001.py"
AUDIT_BLOB = "d3fca8536e56c74c1c3732b14f69ec7b6c65aee1"
GOGIT = "tools/gogit_public.py"
GOGIT_BLOB = "01f0c27a179dc246d0dcf2a0b10dca8cb382a988"
PROTOCOL = "phases/MINI-KUZAI-PHASE-03-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.md"
PROTOCOL_BLOB = "f408b734016eed3a33228ca83763b9e7643185ab"
CPU_PREFLIGHT_AUDIT = "tools/public-audits/phase03_v78_cpu_preflight_001.py"
CPU_PREFLIGHT_AUDIT_BLOB = "c1617c82c4f2ff0c95967624af44a54802a3f23a"
CPU_PREFLIGHT = (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V78-CPU-PREFLIGHT-001.json"
)
CPU_PREFLIGHT_BLOB = "9ff3dd04f57ce0bb31b21a9547dc40d47519b0c3"
TEST = "tests/test_phase03_v78_identical_context_rebatching_numerical_control_001.py"
TEST_BLOB = "8c4e83dd4a25b56eca4cfc674acd6115457e82f0"
START_RECEIPT = "automation/dev-flow/receipts/V78-start.json"
START_RECEIPT_BLOB = "6d6d01d31693c39464d5bf27e2efec4b787c0937"

STEP = "PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001"
SOURCE_LABEL = "Mini-Kuzai V78 identical-context rebatching numerical control"
HISTORY = HISTORY_DIR / (STEP + ".json")

ORIGINS = {
    "https://github.com/Kusanagi8200/Mini-Kuzai.git",
    "https://github.com/Kusanagi8200/Mini-Kuzai",
    "git@github.com:Kusanagi8200/Mini-Kuzai.git",
}
SAFE = ("SEMANTIC_VALIDATION_COMPLETE", "TRAINING_AUTHORIZED", "TRAINING_STARTED")


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError("V78 Git validation failed")
    return proc.stdout.strip()


def synced() -> None:
    if (
        git("branch", "--show-current") != "main"
        or git("remote", "get-url", "origin") not in ORIGINS
        or git("status", "--porcelain")
    ):
        raise RuntimeError("V78 requires clean main and approved Git origin")

    fetch = subprocess.run(
        [
            "git", "-C", str(ROOT), "fetch", "--no-tags", "origin",
            "refs/heads/main:refs/remotes/origin/main",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if fetch.returncode:
        raise RuntimeError("V78 Git fetch failed")

    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("V78 local and remote main differ")


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V78 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V78 expected JSON object")
    return value


def pinned_sources() -> None:
    for path, blob in (
        (SOURCE, SOURCE_BLOB),
        (AUDIT, AUDIT_BLOB),
        (GOGIT, GOGIT_BLOB),
        (PROTOCOL, PROTOCOL_BLOB),
        (CPU_PREFLIGHT_AUDIT, CPU_PREFLIGHT_AUDIT_BLOB),
        (CPU_PREFLIGHT, CPU_PREFLIGHT_BLOB),
        (TEST, TEST_BLOB),
        (START_RECEIPT, START_RECEIPT_BLOB),
    ):
        file = ROOT / path
        if not file.is_file() or file.is_symlink():
            raise RuntimeError("V78 pinned source missing or unsafe")
        if git("rev-parse", "HEAD:" + path) != blob:
            raise RuntimeError("V78 reviewed Git source blob changed")


def verify_cpu_preflight() -> None:
    report = read_json(ROOT / CPU_PREFLIGHT)
    metrics = report.get("metrics")
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V78_PREFLIGHT_PASS": 1,
        "V78_PREFLIGHT_CPU_ONLY": 1,
        "V78_PREFLIGHT_TESTS_TOTAL": 20,
        "V78_PREFLIGHT_TESTS_FAILED": 0,
        "V78_PREFLIGHT_TESTS_ERRORS": 0,
        "V78_PREFLIGHT_TESTS_SKIPPED": 0,
        "V78_PREFLIGHT_START_RECEIPT": 1,
        "V78_PREFLIGHT_SCHEMA_FIELDS": 30,
        "V78_PREFLIGHT_ALLOWLIST_OK": 1,
        "V78_PREFLIGHT_PINS_OK": 1,
        "V78_PREFLIGHT_DEPENDENCIES_OK": 1,
        "V78_PREFLIGHT_GPU_EXECUTION": 0,
        "V78_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V78_PREFLIGHT_BLIND_ACCESS": 0,
        "V78_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V78_PREFLIGHT_GPU_LIMIT_MIB": 6144,
        "V78_PREFLIGHT_PATH_A_BATCH": 4,
        "V78_PREFLIGHT_PATH_B_BATCH": 32,
        "V78_PREFLIGHT_SCORE_CHUNK": 512,
    }
    if not (
        report.get("step_id") == "PHASE03-SMOLTALK-V78-CPU-PREFLIGHT-001"
        and report.get("source")
        == "Mini-Kuzai V78 CPU-only implementation and safety preflight"
        and report.get("producer") == CPU_PREFLIGHT_AUDIT
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and all(metrics.get(k) == v for k, v in expected.items())
    ):
        raise RuntimeError("V78 CPU preflight integrity gate failed")


def preflight() -> None:
    if not PYTHON.is_file() or not os.access(PYTHON, os.X_OK):
        raise RuntimeError("V78 Python interpreter missing or not executable")

    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("V78 frozen V62 run missing or locked")

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
        raise RuntimeError("V78 V62 frozen checkpoint/stop gate failed")

    receipt = read_json(ROOT / START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V78"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/9"
        and receipt.get("source_commit")
        == "f72f0323fb9f8eb16a0ba095f9fd3f6572194e6b"
    ):
        raise RuntimeError("V78 official START receipt absent or invalid")

    verify_cpu_preflight()

    active = subprocess.run(
        ["systemctl", "is-active", "llama-server-a.service"],
        capture_output=True,
        text=True,
        check=False,
    )
    if active.stdout.strip() == "active":
        raise RuntimeError("V78 GPU occupied by llama-server-a; stop separately")


def validate_history() -> dict:
    report = read_json(HISTORY)
    metrics = report.get("metrics")
    audit_path = ROOT / AUDIT

    fixed = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V78_PASS": 1,
        "V78_BLIND_ACCESS": 0,
        "V78_VAL_LEXICAL": 9170,
        "V78_PATH_A_BATCH": 4,
        "V78_PATH_B_BATCH": 32,
        "V78_PATH_A_CORRECT": 2594,
        "V78_PATH_A_DISTINCT": 2,
        "V78_PATH_A_TOP1_SHARE_BP": 7043,
        "V78_IDENTICAL_PREFIXES": 9170,
        "V78_INPUT_MATCHES": 9170,
        "V78_COVERAGE_BP": 10000,
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
        and 0 <= metrics.get("V78_PATH_B_CORRECT", -1) <= 9170
        and 1 <= metrics.get("V78_PATH_B_DISTINCT", 0) <= 1024
        and 0 <= metrics.get("V78_PATH_B_TOP1_SHARE_BP", -1) <= 10000
        and metrics.get("V78_PRED_AGREE", -1)
        + metrics.get("V78_PRED_CHANGED", -1) == 9170
        and metrics.get("V78_ALPHA_SIGN_AGREE", -1)
        + metrics.get("V78_ALPHA_SIGN_CHANGED", -1) == 9170
        and metrics.get("V78_SHARED_CORRECT", -1)
        + metrics.get("V78_A_ONLY_CORRECT", -1) == 2594
        and metrics.get("V78_SHARED_CORRECT", -1)
        + metrics.get("V78_B_ONLY_CORRECT", -1)
        == metrics.get("V78_PATH_B_CORRECT", -2)
        and 0 <= metrics.get("V78_ALPHA_CORR_ABS_BP", -1) <= 10000
        and 0 <= metrics.get("V78_ALPHA_DELTA_GT_1E5", -1)
        <= metrics.get("V78_ALPHA_DELTA_GT_1E6", -1)
        <= metrics.get("V78_ALPHA_DELTA_GT_1E7", -1)
        <= 9170
        and 0 <= metrics.get("V78_ALPHA_MAX_ABS_NANO", -1) <= 100_000_000
        and 0 <= metrics.get("V78_ALPHA_MEAN_ABS_NANO", -1) <= 100_000_000
    ):
        raise RuntimeError("V78 published GOGIT integrity gate failed")

    return metrics


def checked(cmd: list[str], label: str) -> None:
    proc = subprocess.run(cmd, cwd=ROOT, check=False)
    if proc.returncode:
        raise RuntimeError(label + " failed, exit " + str(proc.returncode))


def main() -> None:
    synced()
    pinned_sources()
    preflight()

    if HISTORY.exists():
        validate_history()
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V78_GOGIT=ALREADY_VERIFIED")
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
            "tests.test_phase03_v78_identical_context_rebatching_numerical_control_001",
            "-v",
        ],
        "V78 CPU regression",
    )

    synced()
    pinned_sources()
    preflight()

    checked(
        [
            str(PYTHON),
            str(ROOT / GOGIT),
            "--step",
            STEP,
            "--audit",
            AUDIT,
        ],
        "V78 GOGIT",
    )

    synced()
    pinned_sources()
    validate_history()

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V78_GOGIT=PUBLISHED_AND_VERIFIED")
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
        print("V78_GOGIT=BLOCKED")
        print("ERROR_TYPE=" + type(exc).__name__)
        print("ERROR=" + str(exc))
        sys.exit(1)
