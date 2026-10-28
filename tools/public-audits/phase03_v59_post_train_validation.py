#!/usr/bin/env python3
"""Public numeric-only post-training VALIDATION analysis for V59 bounded pilot."""

from __future__ import annotations

import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN_DIR = Path("/root/Mini-Kuzai/runs/v59-bounded-pilot-001")
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"
MANIFEST = RUN_DIR / "RUN-MANIFEST.json"
METRICS = RUN_DIR / "metrics.jsonl"
PROBES = RUN_DIR / "validation-probes.jsonl"
BEST_CHECKPOINT = RUN_DIR / "checkpoint-best.pt"
LAST_CHECKPOINT = RUN_DIR / "checkpoint-last.pt"
TRAINER_FREEZE = (
    REPO
    / "reviews"
    / "smoltalk-v59-persistent-trainer-freeze"
    / "TRAINER-FREEZE-002.json"
)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSONL artifact: {path}")
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"Expected JSON object at {path}:{number}")
        rows.append(value)
    if not rows:
        raise RuntimeError(f"Empty JSONL artifact: {path}")
    return rows


def scaled(value: float) -> int:
    if not math.isfinite(value) or value < 0:
        raise RuntimeError("Non-finite or negative loss/gradient metric")
    return round(value * 1_000_000)


def main() -> None:
    summary = read_json(SUMMARY)
    manifest = read_json(MANIFEST)
    freeze = read_json(TRAINER_FREEZE)
    rows = read_jsonl(METRICS)
    probes = read_jsonl(PROBES)

    if summary.get("status") != "STOPPED":
        raise RuntimeError("V59 run summary is not stopped")
    if manifest.get("status") != "STOPPED":
        raise RuntimeError("V59 run manifest is not stopped")
    if summary.get("training_started") is not True:
        raise RuntimeError("Training did not start")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("BLIND TEST was accessed")
    if manifest.get("blind_test_during_training") is not False:
        raise RuntimeError("Run manifest permits BLIND TEST access")
    if (
        summary.get("authorization_freeze_fingerprint")
        != freeze.get("authorization_freeze_fingerprint")
    ):
        raise RuntimeError("Authorization fingerprint mismatch")
    if (
        summary.get("trainer_freeze_fingerprint")
        != freeze.get("trainer_freeze_fingerprint")
    ):
        raise RuntimeError("Trainer freeze fingerprint mismatch")

    validation = [row for row in rows if row.get("type") == "validation"]
    train = [row for row in rows if row.get("type") == "train_step"]

    if len(validation) != int(summary.get("evaluations", -1)):
        raise RuntimeError("VALIDATION evaluation count mismatch")
    if len(train) != int(summary.get("optimizer_steps", -1)):
        raise RuntimeError("Training step count mismatch")
    if len(validation) < 2 or not train:
        raise RuntimeError("Insufficient post-training history")

    validation_losses = [float(row["validation_loss"]) for row in validation]
    if not all(math.isfinite(value) and value >= 0 for value in validation_losses):
        raise RuntimeError("Invalid VALIDATION loss history")

    initial_loss = validation_losses[0]
    final_loss = validation_losses[-1]
    best_index = min(range(len(validation_losses)), key=validation_losses.__getitem__)
    best_row = validation[best_index]
    best_loss = validation_losses[best_index]

    reported_best = float(summary["best_validation_loss"])
    if abs(best_loss - reported_best) > 1e-9:
        raise RuntimeError("Best VALIDATION loss does not match run summary")

    running_best = validation_losses[0]
    improving_evals = 0
    for value in validation_losses[1:]:
        if value < running_best:
            running_best = value
            improving_evals += 1

    initial_to_best_bp = (
        round((initial_loss - best_loss) * 10000 / initial_loss)
        if initial_loss > 0
        else 0
    )
    final_to_best_bp = (
        round((final_loss - best_loss) * 10000 / best_loss)
        if best_loss > 0
        else 0
    )

    train_losses = [float(row["train_loss"]) for row in train]
    gradients = [float(row["preclip_gradient_norm"]) for row in train]
    nonfinite_gradients = sum(not math.isfinite(value) for value in gradients)
    if nonfinite_gradients:
        raise RuntimeError("Non-finite gradient detected")
    if not all(math.isfinite(value) and value >= 0 for value in train_losses):
        raise RuntimeError("Invalid training loss history")

    first_train_loss = train_losses[0]
    final_train_loss = train_losses[-1]
    min_train_loss = min(train_losses)
    train_reduction_bp = (
        round((first_train_loss - final_train_loss) * 10000 / first_train_loss)
        if first_train_loss > 0
        else 0
    )

    invalid_utf8 = sum(
        row.get("generated_utf8_valid") is False
        for row in probes
    )
    eos_probes = sum(
        row.get("ended_with_eos") is True
        for row in probes
    )
    final_probe_step = max(int(row.get("step", -1)) for row in probes)
    final_probes = [
        row for row in probes
        if int(row.get("step", -1)) == final_probe_step
    ]
    final_invalid_utf8 = sum(
        row.get("generated_utf8_valid") is False
        for row in final_probes
    )

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "V59_MIX_FINALIZED": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V59_POST_ANALYSIS_PASS": 1,
        "V59_POST_VAL_EVALS": len(validation),
        "V59_POST_VAL_INITIAL_X1E6": scaled(initial_loss),
        "V59_POST_VAL_FINAL_X1E6": scaled(final_loss),
        "V59_POST_VAL_BEST_X1E6": scaled(best_loss),
        "V59_POST_VAL_BEST_STEP": int(best_row["step"]),
        "V59_POST_VAL_BEST_EXPOSURE": int(best_row["exposure_tokens"]),
        "V59_POST_VAL_INITIAL_TO_BEST_BP": initial_to_best_bp,
        "V59_POST_VAL_FINAL_TO_BEST_BP": final_to_best_bp,
        "V59_POST_VAL_IMPROVING_EVALS": improving_evals,
        "V59_POST_TRAIN_STEPS": len(train),
        "V59_POST_TRAIN_FIRST_LOSS_X1E6": scaled(first_train_loss),
        "V59_POST_TRAIN_FINAL_LOSS_X1E6": scaled(final_train_loss),
        "V59_POST_TRAIN_MIN_LOSS_X1E6": scaled(min_train_loss),
        "V59_POST_TRAIN_REDUCTION_BP": train_reduction_bp,
        "V59_POST_GRAD_MAX_X1E6": scaled(max(gradients)),
        "V59_POST_GRAD_NONFINITE": nonfinite_gradients,
        "V59_POST_PROBES": len(probes),
        "V59_POST_PROBES_UTF8_INVALID": invalid_utf8,
        "V59_POST_PROBES_EOS": eos_probes,
        "V59_POST_FINAL_PROBES": len(final_probes),
        "V59_POST_FINAL_UTF8_INVALID": final_invalid_utf8,
        "V59_POST_BEST_CHECKPOINT": int(BEST_CHECKPOINT.is_file()),
        "V59_POST_LAST_CHECKPOINT": int(LAST_CHECKPOINT.is_file()),
        "V59_POST_BLIND_ACCESS": 0,
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
