#!/usr/bin/env python3
"""Pinned V75 read-only GPU audit and immutable numeric GOGIT publication.

This runner is fail-closed. It never trains, never opens BLIND, never writes a
checkpoint and publishes only the frozen 30-integer V75 aggregate schema.
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

SOURCE = "tools/v75_train_fitted_geometry_transfer.py"
SOURCE_BLOB = "8705d8ca9aebe7281779c704119d26eb82517da2"
AUDIT = "tools/public-audits/phase03_v75_train_fitted_geometry_transfer_001.py"
AUDIT_BLOB = "2a7041ab69f98de9f89ea276f14d6cdc40f8f148"
GOGIT = "tools/gogit_public.py"
GOGIT_BLOB = "6ff2ec6890ec893c12a6bcd0bf1c9cebe7b4489a"
PROTOCOL = "phases/MINI-KUZAI-PHASE-03-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.md"
PROTOCOL_BLOB = "708fbcab624aa6f1f59a0a7b416a98557bcdf4b7"
TEST = "test_phase03_v75_train_fitted_geometry_transfer_001.py"
STEP = "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001"
SOURCE_LABEL = "Mini-Kuzai V75 frozen TRAIN-fitted geometry transfer to VALIDATION"
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
        raise RuntimeError("V75 Git validation failed")
    return p.stdout.strip()


def synced() -> None:
    if (
        git("branch", "--show-current") != "main"
        or git("remote", "get-url", "origin") not in ORIGINS
        or git("status", "--porcelain")
    ):
        raise RuntimeError("V75 requires clean main and approved Git origin")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("V75 local and remote main differ")


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V75 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V75 expected JSON object")
    return value


def pinned_sources() -> None:
    for path, blob in (
        (SOURCE, SOURCE_BLOB),
        (AUDIT, AUDIT_BLOB),
        (GOGIT, GOGIT_BLOB),
        (PROTOCOL, PROTOCOL_BLOB),
    ):
        file = ROOT / path
        if not file.is_file() or file.is_symlink():
            raise RuntimeError("V75 pinned source missing or unsafe")
        if git("rev-parse", "HEAD:" + path) != blob:
            raise RuntimeError("V75 reviewed Git source blob changed")


def preflight() -> None:
    if not PYTHON.is_file() or not os.access(PYTHON, os.X_OK):
        raise RuntimeError("V75 Python interpreter missing or not executable")
    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("V75 frozen V62 run missing or locked")

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
        raise RuntimeError("V75 V62 frozen checkpoint/stop gate failed")

    receipt = read_json(
        ROOT / "automation" / "dev-flow" / "receipts" / "V75-start.json"
    )
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V75"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6"
        and receipt.get("source_commit")
        == "12989645b3d6a2071a8ca0ad4f7fd7a2b590d5e5"
    ):
        raise RuntimeError("V75 official START receipt absent or invalid")

    active = subprocess.run(
        ["systemctl", "is-active", "llama-server-a.service"],
        capture_output=True,
        text=True,
        check=False,
    )
    if active.stdout.strip() == "active":
        raise RuntimeError("V75 GPU occupied by llama-server-a; stop separately")


def validate_history() -> dict:
    report = read_json(HISTORY)
    metrics = report.get("metrics")
    audit_path = ROOT / AUDIT
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V75_PASS": 1,
        "V75_BLIND_ACCESS": 0,
        "V75_TRAIN_LEXICAL": 294726,
        "V75_TRAIN_TYPES": 891,
        "V75_VAL_LEXICAL": 9170,
        "V75_TRAIN_STATE_COUNT": 294726,
        "V75_HIDDEN_DIM": 128,
        "V75_ORIG_CORRECT": 2673,
        "V75_ORIG_DISTINCT": 5,
        "V75_ORIG_TOP1_SHARE_BP": 7255,
        "V75_UNIGRAM_CORRECT": 2535,
        "V75_VAL_PC1_CORRECT": 2455,
        "V75_VAL_PC1_VAR_SHARE_BP": 8288,
        "V75_COVERAGE_BP": 10000,
    }
    dynamic_modes = ("TRAIN_CENTER", "TRAIN_PC1", "TRAIN_MINUS_PC1")
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
        and all(metrics.get(k) == v for k, v in expected.items())
        and all(metrics.get(k) == 0 for k in SAFE)
        and all(
            0 <= metrics.get(f"V75_{mode}_CORRECT", -1) <= 9170
            and 1 <= metrics.get(f"V75_{mode}_DISTINCT", 0) <= 1024
            and 0 <= metrics.get(f"V75_{mode}_TOP1_SHARE_BP", -1) <= 10000
            for mode in dynamic_modes
        )
        and 0 <= metrics.get("V75_TRAIN_VAL_PC1_COS_ABS_BP", -1) <= 10000
        and 1 <= metrics.get("V75_TRAIN_PC1_VAR_SHARE_BP", 0) <= 10000
        and 0 <= metrics.get("V75_PC1_UNIGRAM_SHARED_CORRECT", -1)
        <= min(
            metrics.get("V75_PC1_UNIGRAM_AGREE", -1),
            metrics.get("V75_TRAIN_PC1_CORRECT", -1),
            metrics.get("V75_UNIGRAM_CORRECT", -1),
        )
        and metrics.get("V75_PC1_UNIGRAM_AGREE", -1) <= 9170
    ):
        raise RuntimeError("V75 published GOGIT integrity gate failed")
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
        print("V75_GOGIT=ALREADY_VERIFIED")
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
        "V75 CPU regression",
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
        "V75 GOGIT",
    )

    synced()
    pinned_sources()
    validate_history()

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V75_GOGIT=PUBLISHED_AND_VERIFIED")
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
        print("V75_GOGIT=BLOCKED")
        print("ERROR_TYPE=" + type(exc).__name__)
        print("ERROR=" + str(exc))
        sys.exit(1)
