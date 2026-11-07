#!/usr/bin/env python3
"""Pinned V79 read-only GPU audit and immutable numeric GOGIT publication.

Authorized scope: V79 same-path context-order control only.
This runner never trains, never opens BLIND, never generates text, never writes
a checkpoint and publishes only the frozen 30-integer V79 aggregate schema.
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

SOURCE = "tools/v79_same_path_context_order_control.py"
SOURCE_BLOB = "ec3a8702e53789a10486fdcc85dd384b3a89150f"
AUDIT = "tools/public-audits/phase03_v79_same_path_context_order_control_001.py"
AUDIT_BLOB = "ef35044aeb14ce129756f27f76793c52ec083f73"
GOGIT = "tools/gogit_public.py"
GOGIT_BLOB = "f374f10cc8db36e4b146b3a172c6e5433e513fff"
PROTOCOL = "phases/MINI-KUZAI-PHASE-03-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.md"
PROTOCOL_BLOB = "ca66821d0e844c13350d58e922b8adadd96f6f12"
CPU_PREFLIGHT_AUDIT = "tools/public-audits/phase03_v79_cpu_preflight_001.py"
CPU_PREFLIGHT_AUDIT_BLOB = "78fef7cdae1546cb594c6ee09f3a3a6281c1b88d"
CPU_PREFLIGHT = (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V79-CPU-PREFLIGHT-001.json"
)
CPU_PREFLIGHT_BLOB = "855e96ec567b3a81f483aa51767da40dd8b8421b"
TEST = "tests/test_phase03_v79_same_path_context_order_control_001.py"
TEST_BLOB = "5137ec2c8d8f556a85a2323b08bb2acc2935d795"
START_RECEIPT = "automation/dev-flow/receipts/V79-start.json"
START_RECEIPT_BLOB = "613dc5635e8a9b5bd591fc35a87d5d383a3d0900"

STEP = "PHASE03-SMOLTALK-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001"
SOURCE_LABEL = "Mini-Kuzai V79 same-path context-order control"
HISTORY = HISTORY_DIR / (STEP + ".json")

ORIGINS = {
    "https://github.com/Kusanagi8200/Mini-Kuzai.git",
    "https://github.com/Kusanagi8200/Mini-Kuzai",
    "git@github.com:Kusanagi8200/Mini-Kuzai.git",
}
SAFE = ("SEMANTIC_VALIDATION_COMPLETE", "TRAINING_AUTHORIZED", "TRAINING_STARTED")
PUBLIC_METRIC_MAX = 100_000_000
ALPHA_MAX_ABS_NANO_LIMIT = 2_000_000_000


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError("V79 Git validation failed")
    return proc.stdout.strip()


def synced() -> None:
    if (
        git("branch", "--show-current") != "main"
        or git("remote", "get-url", "origin") not in ORIGINS
        or git("status", "--porcelain")
    ):
        raise RuntimeError("V79 requires clean main and approved Git origin")

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
        raise RuntimeError("V79 Git fetch failed")

    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("V79 local and remote main differ")


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V79 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V79 expected JSON object")
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
            raise RuntimeError("V79 pinned source missing or unsafe")
        if git("rev-parse", "HEAD:" + path) != blob:
            raise RuntimeError("V79 reviewed Git source blob changed")


def verify_cpu_preflight() -> None:
    report = read_json(ROOT / CPU_PREFLIGHT)
    metrics = report.get("metrics")
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V79_PREFLIGHT_PASS": 1,
        "V79_PREFLIGHT_CPU_ONLY": 1,
        "V79_PREFLIGHT_TESTS_TOTAL": 24,
        "V79_PREFLIGHT_TESTS_FAILED": 0,
        "V79_PREFLIGHT_TESTS_ERRORS": 0,
        "V79_PREFLIGHT_TESTS_SKIPPED": 0,
        "V79_PREFLIGHT_START_RECEIPT": 1,
        "V79_PREFLIGHT_SCHEMA_FIELDS": 30,
        "V79_PREFLIGHT_ALLOWLIST_OK": 1,
        "V79_PREFLIGHT_PINS_OK": 1,
        "V79_PREFLIGHT_DEPENDENCIES_OK": 1,
        "V79_PREFLIGHT_GPU_EXECUTION": 0,
        "V79_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V79_PREFLIGHT_BLIND_ACCESS": 0,
        "V79_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V79_PREFLIGHT_GPU_LIMIT_MIB": 6144,
        "V79_PREFLIGHT_SAME_PATH_BATCH": 32,
        "V79_PREFLIGHT_SCORE_CHUNK": 512,
        "V79_PREFLIGHT_V77_REPLAY": 1,
        "V79_PREFLIGHT_V78_REPLAY": 1,
    }
    if not (
        report.get("step_id") == "PHASE03-SMOLTALK-V79-CPU-PREFLIGHT-001"
        and report.get("source")
        == "Mini-Kuzai V79 CPU-only implementation and safety preflight"
        and report.get("producer") == CPU_PREFLIGHT_AUDIT
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == len(expected)
        and all(metrics.get(k) == v for k, v in expected.items())
    ):
        raise RuntimeError("V79 CPU preflight integrity gate failed")


def preflight() -> None:
    if not PYTHON.is_file() or not os.access(PYTHON, os.X_OK):
        raise RuntimeError("V79 Python interpreter missing or not executable")

    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("V79 frozen V62 run missing or locked")

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
        raise RuntimeError("V79 V62 frozen checkpoint/stop gate failed")

    receipt = read_json(ROOT / START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V79"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/10"
        and receipt.get("source_commit")
        == "5f86ce1c143f2574301c18669803d251921bffb7"
    ):
        raise RuntimeError("V79 official START receipt absent or invalid")

    verify_cpu_preflight()

    active = subprocess.run(
        ["systemctl", "is-active", "llama-server-a.service"],
        capture_output=True,
        text=True,
        check=False,
    )
    if active.stdout.strip() == "active":
        raise RuntimeError("V79 GPU occupied by llama-server-a; stop separately")


def validate_history() -> dict:
    report = read_json(HISTORY)
    metrics = report.get("metrics")
    audit_path = ROOT / AUDIT

    fixed = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V79_PASS": 1,
        "V79_BLIND_ACCESS": 0,
        "V79_VAL_LEXICAL": 9170,
        "V79_SAME_PATH_BATCH": 32,
        "V79_PERTURBED_PREFIXES": 9062,
        "V79_UNCHANGED_PREFIXES": 108,
        "V79_ORIGINAL_CORRECT": 2594,
        "V79_ORIGINAL_DISTINCT": 2,
        "V79_ORIGINAL_TOP1_SHARE_BP": 7043,
        "V79_INPUT_INVARIANTS": 9170,
        "V79_COVERAGE_BP": 10000,
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
        and all(
            type(v) is int
            and 0 <= v <= (
                ALPHA_MAX_ABS_NANO_LIMIT
                if k == "V79_ALPHA_MAX_ABS_NANO"
                else PUBLIC_METRIC_MAX
            )
            for k, v in metrics.items()
        )
        and all(metrics.get(k) == v for k, v in fixed.items())
        and all(metrics.get(k) == 0 for k in SAFE)
        and 0 <= metrics.get("V79_REVERSE_CORRECT", -1) <= 9170
        and 1 <= metrics.get("V79_REVERSE_DISTINCT", 0) <= 1024
        and 0 <= metrics.get("V79_REVERSE_TOP1_SHARE_BP", -1) <= 10000
        and metrics.get("V79_PRED_AGREE", -1)
        + metrics.get("V79_PRED_CHANGED", -1) == 9170
        and metrics.get("V79_ALPHA_SIGN_AGREE", -1)
        + metrics.get("V79_ALPHA_SIGN_CHANGED", -1) == 9170
        and metrics.get("V79_SHARED_CORRECT", -1)
        + metrics.get("V79_ORIGINAL_ONLY_CORRECT", -1) == 2594
        and metrics.get("V79_SHARED_CORRECT", -1)
        + metrics.get("V79_REVERSE_ONLY_CORRECT", -1)
        == metrics.get("V79_REVERSE_CORRECT", -2)
        and 0 <= metrics.get("V79_ALPHA_CORR_ABS_BP", -1) <= 10000
        and 0 <= metrics.get("V79_ALPHA_DELTA_GT_1E5", -1)
        <= metrics.get("V79_ALPHA_DELTA_GT_1E6", -1)
        <= metrics.get("V79_ALPHA_DELTA_GT_1E7", -1)
        <= 9170
        and 0 <= metrics.get("V79_ALPHA_MAX_ABS_NANO", -1)
        <= ALPHA_MAX_ABS_NANO_LIMIT
        and 0 <= metrics.get("V79_ALPHA_MEAN_ABS_NANO", -1)
        <= PUBLIC_METRIC_MAX
    ):
        raise RuntimeError("V79 published GOGIT integrity gate failed")

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
        print("V79_GOGIT=ALREADY_VERIFIED")
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
            "tests.test_phase03_v79_same_path_context_order_control_001",
            "-v",
        ],
        "V79 CPU regression",
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
        "V79 GOGIT",
    )

    synced()
    pinned_sources()
    validate_history()

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V79_GOGIT=PUBLISHED_AND_VERIFIED")
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
        print("V79_GOGIT=BLOCKED")
        print("ERROR_TYPE=" + type(exc).__name__)
        print("ERROR=" + str(exc))
        sys.exit(1)
