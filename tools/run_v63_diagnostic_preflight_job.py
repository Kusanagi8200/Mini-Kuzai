#!/usr/bin/env python3
"""Publish V63 read-only diagnostic preflight via GOGIT, safely and idempotently."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
STEP = "PHASE03-SMOLTALK-V63-DIAGNOSTIC-PREFLIGHT-001"
AUDIT = "tools/public-audits/phase03_v63_diagnostic_preflight.py"
HISTORY = REPO / "reports" / "assistant-results" / "history" / f"{STEP}.json"


def git(*args):
    p = subprocess.run(
        ["git", "-C", str(REPO), *args],
        text=True, capture_output=True, check=False,
    )
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or "Git failure")
    return p.stdout.strip()


def require_synced():
    if git("branch", "--show-current") != "main" or git("status", "--porcelain"):
        raise RuntimeError("Expected clean main")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local and remote main differ")


def read_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def preflight():
    if not PYTHON.is_file():
        raise RuntimeError("Frozen Python environment missing")
    if not RUN.is_dir() or RUN.is_symlink() or (RUN / ".training.lock").exists():
        raise RuntimeError("Frozen run directory unavailable or locked")
    summary = read_json(RUN / "RUN-SUMMARY.json")
    manifest = read_json(RUN / "RUN-MANIFEST.json")
    if not (
        summary.get("status") == manifest.get("status") == "STOPPED"
        and summary.get("stop_reason") == "MILESTONE_REVIEW_REQUIRED"
        and summary.get("optimizer_steps") == 69
        and summary.get("exposure_tokens") == 597982
        and summary.get("blind_test_accessed") is False
        and manifest.get("resume") is False
        and manifest.get("blind_test_during_training") is False
    ):
        raise RuntimeError("V62 cycle-2 run no longer matches frozen state")
    checkpoint = RUN / "checkpoint-cycle-02.pt"
    if not checkpoint.is_file() or checkpoint.is_symlink():
        raise RuntimeError("V62 cycle-2 checkpoint missing or unsafe")
    for name in (
        "PHASE03-SMOLTALK-V62-TRAIN-RUN-001",
        "PHASE03-SMOLTALK-V62-TRAIN-RUN-001-EOS-CALIBRATION-001",
    ):
        proof = read_json(REPO / "reports" / "assistant-results" / "history" / f"{name}.json")
        if proof.get("step_id") != name or proof.get("semantic_validation_complete") is not True:
            raise RuntimeError(f"Missing frozen GOGIT proof: {name}")


def validate_history():
    report = read_json(HISTORY)
    metrics = report.get("metrics", {})
    if (
        report.get("step_id") != STEP
        or report.get("producer") != AUDIT
        or report.get("semantic_validation_complete") is not True
        or metrics.get("V63_DIAG_PREFLIGHT_PASS") != 1
        or metrics.get("V63_DIAG_BLIND_ACCESS") != 0
        or metrics.get("V63_DIAG_GPU_BF16") != 1
    ):
        raise RuntimeError("V63 GOGIT history failed validation")


def main():
    require_synced()
    preflight()
    if HISTORY.exists():
        validate_history()
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V63_GOGIT: ALREADY_PUBLISHED")
        print("STEP_ID:", STEP)
        print("TRAINING_RESTARTED: 0")
        return
    p = subprocess.run(
        [str(PYTHON), "tools/gogit_public.py", "--step", STEP, "--audit", AUDIT],
        cwd=REPO, text=True, check=False,
    )
    if p.returncode:
        raise RuntimeError(f"GOGIT diagnostic publication exited {p.returncode}")
    require_synced()
    validate_history()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V63_GOGIT: COMPLETE")
    print("STEP_ID:", STEP)
    print("TRAINING_RESTARTED: 0")
    print("BLIND_ACCESS: 0")
    print("HEAD:", git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V63_GOGIT: NOT_CONFIRMED")
        print("ERROR:", str(exc))
        sys.exit(1)
