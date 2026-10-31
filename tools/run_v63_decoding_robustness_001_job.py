#!/usr/bin/env python3
"""Run V63 eight-seed robustness GPU audit and GOGIT publication."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
STEP = "PHASE03-SMOLTALK-V63-DECODING-ROBUSTNESS-001"
AUDIT = "tools/public-audits/phase03_v63_decoding_robustness_001.py"
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
    previous_step = "PHASE03-SMOLTALK-V63-DECODING-ABLATION-001"
    previous = read_json(
        REPO / "reports" / "assistant-results" / "history"
        / f"{previous_step}.json"
    )
    if (
        previous.get("step_id") != previous_step
        or previous.get("semantic_validation_complete") is not True
        or previous.get("metrics", {}).get("V63_ABL_PASS") != 1
        or previous.get("metrics", {}).get("V63_ABL_BLIND_ACCESS") != 0
        or previous.get("metrics", {}).get("V63_ABL_PROBES_PER_MODE") != 6
    ):
        raise RuntimeError("Frozen V63 decoding ablation history invalid")
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
        or metrics.get("V63_ROB_PASS") != 1
        or metrics.get("V63_ROB_BLIND_ACCESS") != 0
        or metrics.get("V63_ROB_GPU_BF16") != 1
    ):
        raise RuntimeError("V63 GOGIT history failed validation")


def main():
    require_synced()
    preflight()
    if HISTORY.exists():
        validate_history()
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V63_ROB_GOGIT: ALREADY_PUBLISHED")
        print("STEP_ID:", STEP)
        print("TRAINING_RESTARTED: 0")
        return
    test = subprocess.run(
        [
            str(PYTHON), "-m", "unittest", "discover",
            "-s", "tests",
            "-p", "test_phase03_v63_decoding_robustness.py",
            "-v",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if test.returncode:
        raise RuntimeError(
            "V63 decoder CPU unit tests failed: "
            + (test.stderr or test.stdout)[-2000:]
        )
    print("V63_DECODER_UNIT_TESTS: PASS")
    p = subprocess.run(
        [str(PYTHON), "tools/gogit_public.py", "--step", STEP, "--audit", AUDIT],
        cwd=REPO, text=True, check=False,
    )
    if p.returncode:
        raise RuntimeError(f"GOGIT diagnostic publication exited {p.returncode}")
    require_synced()
    validate_history()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V63_ROB_GOGIT: COMPLETE")
    print("STEP_ID:", STEP)
    print("TRAINING_RESTARTED: 0")
    print("BLIND_ACCESS: 0")
    print("HEAD:", git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V63_ROB_GOGIT: NOT_CONFIRMED")
        print("ERROR:", str(exc))
        sys.exit(1)
