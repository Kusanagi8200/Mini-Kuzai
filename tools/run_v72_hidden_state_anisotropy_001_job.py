#!/usr/bin/env python3
"""Pinned V72 GPU read-only audit and verified numerical GOGIT publication."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
AUDIT = "tools/public-audits/phase03_v72_hidden_state_anisotropy_001.py"
AUDIT_BLOB = "f116ea33f66f36a626f00b3852a2a320e7ee953a"
STEP = "PHASE03-SMOLTALK-V72-HIDDEN-STATE-ANISOTROPY-001"
TEST = "test_phase03_v72_hidden_state_anisotropy_001.py"
HISTORY = ROOT / "reports" / "assistant-results" / "history" / (STEP + ".json")
ORIGINS = {
    "https://github.com/Kusanagi8200/Mini-Kuzai.git",
    "https://github.com/Kusanagi8200/Mini-Kuzai",
    "git@github.com:Kusanagi8200/Mini-Kuzai.git",
}


def git(*args):
    p = subprocess.run(["git", "-C", str(ROOT), *args],
                       capture_output=True, text=True, check=False)
    if p.returncode:
        raise RuntimeError("Git failure: " + " ".join(args[:2]))
    return p.stdout.strip()


def synced():
    if (git("branch", "--show-current") != "main"
            or git("remote", "get-url", "origin") not in ORIGINS
            or git("status", "--porcelain")):
        raise RuntimeError("Expected clean main and approved Git origin")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Git main not synchronized")


def preflight():
    if not PYTHON.is_file():
        raise RuntimeError("Expected frozen Python interpreter missing")
    if not RUN.is_dir() or RUN.is_symlink() or (RUN / ".training.lock").exists():
        raise RuntimeError("Frozen V62 run directory missing/locked")
    for name in ("RUN-SUMMARY.json", "RUN-MANIFEST.json"):
        if not (RUN / name).is_file() or (RUN / name).is_symlink():
            raise RuntimeError("V62 frozen run metadata missing/unsafe")
    summary = json.loads((RUN / "RUN-SUMMARY.json").read_text())
    manifest = json.loads((RUN / "RUN-MANIFEST.json").read_text())
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
        and checkpoint.is_file() and not checkpoint.is_symlink()
    ):
        raise RuntimeError("V62 frozen model state changed")
    if git("rev-parse", "HEAD:" + AUDIT) != AUDIT_BLOB:
        raise RuntimeError("V72 source changed since reviewed Git blob")
    script = ROOT / AUDIT
    if not script.is_file() or script.is_symlink():
        raise RuntimeError("V72 source missing/unsafe")


def validate_history():
    if not HISTORY.is_file() or HISTORY.is_symlink():
        raise RuntimeError("Immutable V72 GOGIT report absent or unsafe")
    report = json.loads(HISTORY.read_text(encoding="utf-8"))
    metrics = report.get("metrics", {})
    source = ROOT / AUDIT
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V72_GEOM_PASS": 1,
        "V72_GEOM_BLIND_ACCESS": 0,
        "V72_GEOM_VAL_LEXICAL": 9170,
        "V72_GEOM_MODEL_DIM": 128,
        "V72_GEOM_ORIG_CE_X1000": 4732,
        "V72_GEOM_ORIG_DISTINCT": 5,
        "V72_GEOM_ORIG_TOP1_SHARE_BP": 7255,
        "V72_GEOM_ORIG_CORRECT": 2673,
    }
    if not (
        report.get("step_id") == STEP
        and report.get("producer") == AUDIT
        and report.get("producer_sha256") ==
            hashlib.sha256(source.read_bytes()).hexdigest()
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict) and len(metrics) == 30
        and all(type(value) is int and 0 <= value <= 100_000_000
                for value in metrics.values())
        and all(metrics.get(k) == v for k, v in expected.items())
        and metrics.get("V72_GEOM_CENTER_SWITCH") ==
            metrics.get("V72_GEOM_CENTER_SWITCH_BYTE", -1) +
            metrics.get("V72_GEOM_CENTER_SWITCH_MERGE", -1)
        and metrics.get("V72_GEOM_RAW_PC1_SHARE_BP", 10001) <=
            metrics.get("V72_GEOM_RAW_PC5_SHARE_BP", -1) <= 10000
        and metrics.get("V72_GEOM_CENTER_PC1_SHARE_BP", 10001) <=
            metrics.get("V72_GEOM_CENTER_PC5_SHARE_BP", -1) <= 10000
        and 0 <= metrics.get("V72_GEOM_CENTER_CORRECT", -1) <= 9170
    ):
        raise RuntimeError("V72 published 30-field GOGIT integrity check failed")


def checked_run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, check=False)
    if p.returncode:
        raise RuntimeError("V72 subprocess failed, exit " + str(p.returncode))


def main():
    synced()
    preflight()
    if HISTORY.exists():
        validate_history()
        print("V72_ATTR_GOGIT: ALREADY_PUBLISHED")
        return
    checked_run([str(PYTHON), "-m", "unittest", "discover",
                 "-s", "tests", "-p", TEST, "-v"])
    synced()
    checked_run([str(PYTHON), "tools/gogit_public.py",
                 "--step", STEP, "--audit", AUDIT])
    synced()
    validate_history()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V72_ATTR_GOGIT: PUBLISHED")
    print("STEP_ID:", STEP)
    print("TRAINING_RESTARTED: 0")
    print("BLIND_ACCESS: 0")
    print("HEAD:", git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyboardInterrupt, ValueError, OSError) as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V72_ATTR_GOGIT: NOT_CONFIRMED")
        print("ERROR:", str(exc))
        sys.exit(1)
