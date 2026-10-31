#!/usr/bin/env python3
"""Prepare, resume and publish V63 local human semantic generation review.

Human scoring is interactive. No automatic semantic judgments are invented.
Raw text and private ratings remain outside Git. No training/BLIND access.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
STEP = "PHASE03-SMOLTALK-V63-SEMANTIC-GENERATION-REVIEW-001"
AUDIT = "tools/public-audits/phase03_v63_semantic_generation_review_001.py"
REVIEW = "tools/phase03_v63_semantic_generation_review_001.py"
HISTORY = REPO / "reports" / "assistant-results" / "history" / f"{STEP}.json"
TEST = "test_phase03_v63_semantic_generation_review_001.py"


def git(*args):
    p = subprocess.run(
        ["git", "-C", str(REPO), *args],
        text=True, capture_output=True, check=False,
    )
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or "Git failure")
    return p.stdout.strip()


def synced():
    if git("branch", "--show-current") != "main" or git("status", "--porcelain"):
        raise RuntimeError("Expected clean Git main")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local and remote main differ")


def read_json(path: Path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe report: {path.name}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Expected JSON object")
    return data


def preflight():
    if not PYTHON.is_file():
        raise RuntimeError("Local frozen Python environment missing")
    if not RUN.is_dir() or RUN.is_symlink() or (RUN / ".training.lock").exists():
        raise RuntimeError("V62 training state missing or active")
    summary = read_json(RUN / "RUN-SUMMARY.json")
    manifest = read_json(RUN / "RUN-MANIFEST.json")
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
    ):
        raise RuntimeError("Frozen V62 cycle-2 manifest differs")
    ckpt = RUN / "checkpoint-cycle-02.pt"
    if not ckpt.is_file() or ckpt.is_symlink():
        raise RuntimeError("Frozen V62 checkpoint missing")
    previous_step = "PHASE03-SMOLTALK-V63-DECODING-ROBUSTNESS-001"
    previous = read_json(
        REPO / "reports" / "assistant-results" / "history"
        / f"{previous_step}.json"
    )
    m = previous.get("metrics", {})
    if not (
        previous.get("step_id") == previous_step
        and previous.get("semantic_validation_complete") is True
        and m.get("V63_ROB_PASS") == 1
        and m.get("V63_ROB_BLIND_ACCESS") == 0
        and m.get("V63_ROB_SEEDS") == 8
    ):
        raise RuntimeError("Frozen V63 robustness GOGIT reference missing")


def test_before_review():
    result = subprocess.run(
        [
            str(PYTHON), "-m", "unittest", "discover",
            "-s", "tests",
            "-p", TEST, "-v",
        ],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(
            "V63 human review unit tests failed: "
            + (result.stderr or result.stdout)[-2200:]
        )


def checked_history():
    report = read_json(HISTORY)
    m = report.get("metrics", {})
    if not (
        report.get("step_id") == STEP
        and report.get("producer") == AUDIT
        and report.get("semantic_validation_complete") is True
        and report.get("training_authorized") is False
        and m.get("TRAINING_AUTHORIZED") == 0
        and m.get("TRAINING_STARTED") == 0
        and m.get("V63_HUM_PASS") == 1
        and m.get("V63_HUM_BLIND_ACCESS") == 0
        and m.get("V63_HUM_SAMPLES") == 24
        and m.get("V63_HUM_REVIEWED") == 24
    ):
        raise RuntimeError("Published V63 human review report invalid")


def run(action):
    result = subprocess.run(
        [str(PYTHON), REVIEW, action],
        cwd=REPO,
        check=False,
    )
    if result.returncode not in (0, 2):
        raise RuntimeError(f"Private V63 review action {action} failed")
    return result.returncode


def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--prepare-only", action="store_true")
    g.add_argument("--review-only", action="store_true")
    g.add_argument("--publish-only", action="store_true")
    args = parser.parse_args()
    synced()
    preflight()
    test_before_review()
    if HISTORY.exists():
        checked_history()
        print("V63_HUM_GOGIT: ALREADY_PUBLISHED")
        return
    if args.prepare_only:
        if run("prepare") != 0:
            raise RuntimeError("Private generation failed")
        print("V63_HUM_GOGIT: PRIVATE_GENERATION_READY")
        return
    if args.review_only:
        if run("review") == 2:
            print("V63_HUM_GOGIT: REVIEW_PAUSED; no publication")
            return
    elif not args.publish_only:
        if run("all") == 2:
            print("V63_HUM_GOGIT: REVIEW_PAUSED; no publication")
            return
    if run("check") != 0:
        raise RuntimeError("Human review is not complete; publishing blocked")
    synced()
    p = subprocess.run(
        [str(PYTHON), "tools/gogit_public.py", "--step", STEP, "--audit", AUDIT],
        cwd=REPO, check=False,
    )
    if p.returncode:
        raise RuntimeError("GOGIT semantic review audit failed; nothing confirmed")
    synced()
    checked_history()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V63_HUM_GOGIT: PUBLISHED")
    print("STEP_ID:", STEP)
    print("HUMAN_REVIEW_COUNT: 24")
    print("TRAINING_RESTARTED: 0")
    print("BLIND_ACCESS: 0")
    print("HEAD:", git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyboardInterrupt) as exc:
        print("V63_HUM_GOGIT: NOT_CONFIRMED")
        print("ERROR:", str(exc))
        sys.exit(1)
