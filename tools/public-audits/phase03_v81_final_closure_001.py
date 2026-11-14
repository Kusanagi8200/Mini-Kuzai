#!/usr/bin/env python3
"""Public numeric closure audit for Mini-Kuzai V81.

This audit closes the bounded V62 continuation window after the verified
post-train GOGIT. It does not authorize further training and does not access
BLIND data.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")

TRAIN_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V81-CONTINUATION-TRAIN-001.json"
)
BASELINE_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V62-TRAIN-RUN-001.json"
)
START_RECEIPT = (
    REPO / "automation" / "dev-flow" / "receipts" / "V81-start.json"
)
SUMMARY = RUN / "RUN-SUMMARY.json"
MANIFEST = RUN / "RUN-MANIFEST.json"

BASELINE_BEST = 4732514
FINAL_BEST = 4030447
FINAL_STEPS = 136
FINAL_EXPOSURE = 1181302
MAX_EXPOSURE = 1181664
UNUSED_EXPOSURE = 362


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def main() -> None:
    train = read_json(TRAIN_REPORT)
    baseline = read_json(BASELINE_REPORT)
    start = read_json(START_RECEIPT)
    summary = read_json(SUMMARY)
    manifest = read_json(MANIFEST)

    train_metrics = train.get("metrics")
    baseline_metrics = baseline.get("metrics")
    if not isinstance(train_metrics, dict) or not isinstance(baseline_metrics, dict):
        raise RuntimeError("Required GOGIT metrics missing")

    if (
        train.get("step_id") != "PHASE03-SMOLTALK-V81-CONTINUATION-TRAIN-001"
        or train.get("private_conversation_data_included") is not False
        or train_metrics.get("V81_TRAIN_PASS") != 1
        or train_metrics.get("V81_TRAIN_WINDOW_CLOSED") != 1
        or train_metrics.get("V81_TRAIN_BLIND_ACCESS") != 0
        or train_metrics.get("V81_TRAIN_FINAL_STEPS") != FINAL_STEPS
        or train_metrics.get("V81_TRAIN_FINAL_EXPOSURE") != FINAL_EXPOSURE
        or train_metrics.get("V81_TRAIN_UNUSED_EXPOSURE") != UNUSED_EXPOSURE
        or train_metrics.get("V81_TRAIN_BEST_VAL_LOSS_X1E6") != FINAL_BEST
    ):
        raise RuntimeError("V81 post-train GOGIT mismatch")

    if (
        baseline.get("step_id") != "PHASE03-SMOLTALK-V62-TRAIN-RUN-001"
        or baseline_metrics.get("V62_RUN1_BEST_VAL_LOSS_X1E6") != BASELINE_BEST
        or baseline_metrics.get("V62_RUN1_BLIND_ACCESS") != 0
    ):
        raise RuntimeError("V62 cycle-2 baseline GOGIT mismatch")

    if (
        start.get("command") != "START-DEV-FLOW"
        or start.get("step") != "V81"
        or start.get("status") != "PUBLISHED"
    ):
        raise RuntimeError("V81 START receipt mismatch")

    if (
        summary.get("schema_version") != "v62-margin-run-summary-1"
        or summary.get("status") != "STOPPED"
        or summary.get("stop_reason") != "MAX_EXPOSURE_TOKENS"
        or summary.get("training_started") is not True
        or summary.get("optimizer_steps") != FINAL_STEPS
        or summary.get("exposure_tokens") != FINAL_EXPOSURE
        or summary.get("blind_test_accessed") is not False
    ):
        raise RuntimeError("V81 final run summary mismatch")

    if (
        manifest.get("schema_version") != "v62-margin-run-1"
        or manifest.get("status") != "STOPPED"
        or manifest.get("stop_reason") != "MAX_EXPOSURE_TOKENS"
        or manifest.get("training_started") is not True
        or manifest.get("optimizer_steps") != FINAL_STEPS
        or manifest.get("exposure_tokens") != FINAL_EXPOSURE
        or manifest.get("resume") is not True
        or manifest.get("blind_test_during_training") is not False
    ):
        raise RuntimeError("V81 final run manifest mismatch")

    if (RUN / ".training.lock").exists():
        raise RuntimeError("Training lock still present at V81 closure")

    improvement = BASELINE_BEST - FINAL_BEST
    improvement_bp = round(improvement * 10000 / BASELINE_BEST)

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 1,
        "V81_FINAL_PASS": 1,
        "V81_FINAL_BLIND_ACCESS": 0,
        "V81_FINAL_WINDOW_CLOSED": 1,
        "V81_FINAL_FURTHER_TRAINING_AUTHORIZED": 0,
        "V81_FINAL_START_RECEIPT": 1,
        "V81_FINAL_POST_TRAIN_GOGIT": 1,
        "V81_FINAL_STOP_MAX_TOKENS": 1,
        "V81_FINAL_STEPS": FINAL_STEPS,
        "V81_FINAL_EXPOSURE": FINAL_EXPOSURE,
        "V81_FINAL_MAX_EXPOSURE": MAX_EXPOSURE,
        "V81_FINAL_UNUSED_EXPOSURE": UNUSED_EXPOSURE,
        "V81_FINAL_BASELINE_BEST_LOSS_X1E6": BASELINE_BEST,
        "V81_FINAL_BEST_LOSS_X1E6": FINAL_BEST,
        "V81_FINAL_BEST_LOSS_IMPROVEMENT_X1E6": improvement,
        "V81_FINAL_BEST_LOSS_IMPROVEMENT_BP": improvement_bp,
        "V81_FINAL_SEMANTIC_CLAIM": 0,
        "V81_FINAL_CHECKPOINT_LAST": int((RUN / "checkpoint-last.pt").is_file()),
        "V81_FINAL_CHECKPOINT_BEST": int((RUN / "checkpoint-best.pt").is_file()),
        "V81_FINAL_CHECKPOINT_CYCLE2": int((RUN / "checkpoint-cycle-02.pt").is_file()),
        "V81_FINAL_CHECKPOINT_CYCLE4": int((RUN / "checkpoint-cycle-04.pt").is_file()),
        "V81_FINAL_TRAIN_LOCK": 0,
    }

    if metrics["V81_FINAL_CHECKPOINT_LAST"] != 1:
        raise RuntimeError("checkpoint-last missing at V81 closure")
    if metrics["V81_FINAL_CHECKPOINT_BEST"] != 1:
        raise RuntimeError("checkpoint-best missing at V81 closure")
    if metrics["V81_FINAL_CHECKPOINT_CYCLE2"] != 1:
        raise RuntimeError("checkpoint-cycle-02 missing at V81 closure")
    if metrics["V81_FINAL_CHECKPOINT_CYCLE4"] != 0:
        raise RuntimeError("Unexpected cycle-4 checkpoint below frozen threshold")

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
