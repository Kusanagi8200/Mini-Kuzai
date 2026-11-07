#!/usr/bin/env python3
"""Pinned V76 read-only GPU audit and immutable numeric GOGIT publication.

Execution is authorized only for the frozen V76 scientific control. This runner
never trains, never opens BLIND, never writes a checkpoint and publishes only
the frozen 30-integer V76 aggregate schema.
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

SOURCE = "tools/v76_frequency_residualized_pc1_control.py"
SOURCE_BLOB = "d0db771c2f022a2e94293f8b0345ba834580407e"
AUDIT = "tools/public-audits/phase03_v76_frequency_residualized_pc1_control_001.py"
AUDIT_BLOB = "aaf6032e86a59172310c274d2ba3e578e67b00da"
GOGIT = "tools/gogit_public.py"
GOGIT_BLOB = "b5bf32e6b54d842afa43e09b70baf3965c9429e6"
PROTOCOL = "phases/MINI-KUZAI-PHASE-03-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.md"
PROTOCOL_BLOB = "553dd7c3ebf6eb5fac74f55afe64e22bc93a76a2"
CPU_PREFLIGHT = (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V76-CPU-PREFLIGHT-001.json"
)
CPU_PREFLIGHT_BLOB = "819b3f2aae73758306df7404a622d13898283d34"
TEST = "test_phase03_v76_frequency_residualized_pc1_control_001.py"
STEP = "PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001"
SOURCE_LABEL = "Mini-Kuzai V76 frozen frequency-residualized TRAIN-PC1 output control"
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
        raise RuntimeError("V76 Git validation failed")
    return p.stdout.strip()


def synced() -> None:
    if (
        git("branch", "--show-current") != "main"
        or git("remote", "get-url", "origin") not in ORIGINS
        or git("status", "--porcelain")
    ):
        raise RuntimeError("V76 requires clean main and approved Git origin")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("V76 local and remote main differ")


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V76 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V76 expected JSON object")
    return value


def pinned_sources() -> None:
    for path, blob in (
        (SOURCE, SOURCE_BLOB),
        (AUDIT, AUDIT_BLOB),
        (GOGIT, GOGIT_BLOB),
        (PROTOCOL, PROTOCOL_BLOB),
        (CPU_PREFLIGHT, CPU_PREFLIGHT_BLOB),
    ):
        file = ROOT / path
        if not file.is_file() or file.is_symlink():
            raise RuntimeError("V76 pinned source missing or unsafe")
        if git("rev-parse", "HEAD:" + path) != blob:
            raise RuntimeError("V76 reviewed Git source blob changed")


def verify_cpu_preflight() -> None:
    report = read_json(ROOT / CPU_PREFLIGHT)
    metrics = report.get("metrics")
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V76_PREFLIGHT_PASS": 1,
        "V76_PREFLIGHT_CPU_ONLY": 1,
        "V76_PREFLIGHT_TESTS_TOTAL": 15,
        "V76_PREFLIGHT_TESTS_FAILED": 0,
        "V76_PREFLIGHT_TESTS_ERRORS": 0,
        "V76_PREFLIGHT_TESTS_SKIPPED": 0,
        "V76_PREFLIGHT_START_RECEIPT": 1,
        "V76_PREFLIGHT_SCHEMA_FIELDS": 30,
        "V76_PREFLIGHT_ALLOWLIST_OK": 1,
        "V76_PREFLIGHT_PINS_OK": 1,
        "V76_PREFLIGHT_DEPENDENCIES_OK": 1,
        "V76_PREFLIGHT_GPU_EXECUTION": 0,
        "V76_PREFLIGHT_GPU_AUTHORIZED": 0,
        "V76_PREFLIGHT_BLIND_ACCESS": 0,
        "V76_PREFLIGHT_SCIENTIFIC_GOGIT_PRESENT": 0,
        "V76_PREFLIGHT_GPU_LIMIT_MIB": 6144,
        "V76_PREFLIGHT_TRAIN_BATCH": 2,
        "V76_PREFLIGHT_VAL_BATCH": 4,
        "V76_PREFLIGHT_SCORE_CHUNK": 512,
    }
    if not (
        report.get("step_id") == "PHASE03-SMOLTALK-V76-CPU-PREFLIGHT-001"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and all(metrics.get(k) == v for k, v in expected.items())
    ):
        raise RuntimeError("V76 CPU preflight integrity gate failed")


def preflight() -> None:
    if not PYTHON.is_file() or not os.access(PYTHON, os.X_OK):
        raise RuntimeError("V76 Python interpreter missing or not executable")
    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("V76 frozen V62 run missing or locked")

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
        raise RuntimeError("V76 V62 frozen checkpoint/stop gate failed")

    receipt = read_json(
        ROOT / "automation" / "dev-flow" / "receipts" / "V76-start.json"
    )
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V76"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/7"
        and receipt.get("source_commit")
        == "368710f58b92876aa2b3b3f1ec196610bd876da1"
    ):
        raise RuntimeError("V76 official START receipt absent or invalid")

    verify_cpu_preflight()

    active = subprocess.run(
        ["systemctl", "is-active", "llama-server-a.service"],
        capture_output=True,
        text=True,
        check=False,
    )
    if active.stdout.strip() == "active":
        raise RuntimeError("V76 GPU occupied by llama-server-a; stop separately")


def validate_history() -> dict:
    report = read_json(HISTORY)
    metrics = report.get("metrics")
    audit_path = ROOT / AUDIT
    fixed = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V76_PASS": 1,
        "V76_BLIND_ACCESS": 0,
        "V76_TRAIN_LEXICAL": 294726,
        "V76_TRAIN_TYPES": 891,
        "V76_VAL_LEXICAL": 9170,
        "V76_HIDDEN_DIM": 128,
        "V76_FIT_VOCAB": 1024,
        "V76_PC1_CORRECT": 2457,
        "V76_PC1_DISTINCT": 2,
        "V76_PC1_TOP1_SHARE_BP": 7043,
        "V76_UNIGRAM_CORRECT": 2535,
        "V76_PC1_VAR_SHARE_BP": 9019,
        "V76_TRAIN_VAL_PC1_COS_ABS_BP": 9995,
        "V76_COVERAGE_BP": 10000,
    }
    dynamic_modes = ("FREQ_COMPONENT", "FREQ_RESIDUAL")
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
        and all(
            0 <= metrics.get(f"V76_{mode}_CORRECT", -1) <= 9170
            and 1 <= metrics.get(f"V76_{mode}_DISTINCT", 0) <= 1024
            and 0 <= metrics.get(f"V76_{mode}_TOP1_SHARE_BP", -1) <= 10000
            for mode in dynamic_modes
        )
        and 0 <= metrics.get("V76_AXIS_FREQ_CORR_ABS_BP", -1) <= 10000
        and 0 <= metrics.get("V76_AXIS_FREQ_R2_BP", -1) <= 10000
        and 0 <= metrics.get("V76_RESIDUAL_ENERGY_SHARE_BP", -1) <= 10000
        and abs(
            metrics.get("V76_AXIS_FREQ_R2_BP", -10001)
            + metrics.get("V76_RESIDUAL_ENERGY_SHARE_BP", -10001)
            - 10000
        ) <= 1
        and 0 <= metrics.get("V76_RESIDUAL_UNIGRAM_AGREE", -1) <= 9170
        and 0 <= metrics.get("V76_RESIDUAL_UNIGRAM_SHARED_CORRECT", -1)
        <= min(
            metrics.get("V76_RESIDUAL_UNIGRAM_AGREE", -1),
            metrics.get("V76_FREQ_RESIDUAL_CORRECT", -1),
            metrics.get("V76_UNIGRAM_CORRECT", -1),
        )
        and 0 <= metrics.get("V76_PC1_FREQ_COMPONENT_AGREE", -1) <= 9170
        and 0 <= metrics.get("V76_FREQ_COMPONENT_UNIGRAM_AGREE", -1) <= 9170
    ):
        raise RuntimeError("V76 published GOGIT integrity gate failed")
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
        print("V76_GOGIT=ALREADY_VERIFIED")
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
        "V76 CPU regression",
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
        "V76 GOGIT",
    )

    synced()
    pinned_sources()
    validate_history()

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V76_GOGIT=PUBLISHED_AND_VERIFIED")
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
        print("V76_GOGIT=BLOCKED")
        print("ERROR_TYPE=" + type(exc).__name__)
        print("ERROR=" + str(exc))
        sys.exit(1)
