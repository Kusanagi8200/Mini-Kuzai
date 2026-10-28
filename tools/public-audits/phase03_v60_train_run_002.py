#!/usr/bin/env python3
"""Aggregate-only audit for V60 TRAIN RUN 002 resumed from cycle 8."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v60_trainer as T

RUN_DIR = Path("/root/Mini-Kuzai/runs/v60-extended-001")
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"
MANIFEST = RUN_DIR / "RUN-MANIFEST.json"
CHECKPOINT = RUN_DIR / "checkpoint-last.pt"
RUN1_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V60-TRAIN-RUN-001.json"
)
TRAINER_SOURCE = REPO / "mini_kuzai" / "phase03_v60_trainer.py"
CLI_SOURCE = REPO / "tools" / "train_v60_extended.py"

EXPECTED_RUN1_STEPS = 270
EXPECTED_RUN1_TOKENS = 2365162
EXPECTED_RUN1_VAL_X1E6 = 3602280


def load_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def loss_x1e6(value: float) -> int:
    if not math.isfinite(value) or value < 0:
        raise RuntimeError("Invalid validation loss")
    scaled = round(value * 1_000_000)
    if scaled > 100_000_000:
        raise RuntimeError("Validation loss outside public metric range")
    return scaled


def repeated_trigram_bp(text: str) -> int:
    if len(text) < 3:
        return 0
    grams = [
        text[index:index + 3]
        for index in range(len(text) - 2)
    ]
    repeated = len(grams) - len(set(grams))
    return round(repeated * 10000 / len(grams))


def max_char_run(text: str) -> int:
    if not text:
        return 0
    best = 1
    current = 1
    for left, right in zip(text, text[1:]):
        if left == right:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def main() -> None:
    summary = load_json(SUMMARY)
    manifest = load_json(MANIFEST)
    run1 = load_json(RUN1_REPORT)
    run1_metrics = run1.get("metrics")
    if not isinstance(run1_metrics, dict):
        raise RuntimeError("RUN 001 public metrics are missing")

    if run1_metrics.get("V60_RUN_OPTIMIZER_STEPS") != EXPECTED_RUN1_STEPS:
        raise RuntimeError("RUN 001 step baseline changed")
    if run1_metrics.get("V60_RUN_EXPOSURE_TOKENS") != EXPECTED_RUN1_TOKENS:
        raise RuntimeError("RUN 001 exposure baseline changed")
    if run1_metrics.get("V60_RUN_FINAL_VAL_LOSS_X1E6") != EXPECTED_RUN1_VAL_X1E6:
        raise RuntimeError("RUN 001 validation baseline changed")
    if run1_metrics.get("V60_RUN_STOP_MILESTONE") != 1:
        raise RuntimeError("RUN 001 was not the authorized milestone stop")

    if summary.get("schema_version") != "v60-extended-run-summary-1":
        raise RuntimeError("Unexpected V60 summary schema")
    if summary.get("status") != "STOPPED":
        raise RuntimeError("V60 resumed run is not stopped")
    if summary.get("training_started") is not True:
        raise RuntimeError("V60 resumed run did not train")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("BLIND TEST was accessed")

    if manifest.get("schema_version") != "v60-extended-run-1":
        raise RuntimeError("Unexpected V60 manifest schema")
    if manifest.get("status") != "STOPPED":
        raise RuntimeError("V60 resumed manifest is not stopped")
    if manifest.get("resume") is not True:
        raise RuntimeError("RUN 002 is not marked as a resume")
    if manifest.get("blind_test_during_training") is not False:
        raise RuntimeError("Resumed manifest permits BLIND TEST")
    if manifest.get("max_optimizer_steps") != 577:
        raise RuntimeError("V60 optimizer ceiling changed")
    if manifest.get("max_exposure_tokens") != 4726656:
        raise RuntimeError("V60 exposure window changed")

    steps = int(summary["optimizer_steps"])
    exposure = int(summary["exposure_tokens"])
    if not EXPECTED_RUN1_STEPS < steps <= 577:
        raise RuntimeError("RUN 002 final step is outside authorized continuation")
    if not EXPECTED_RUN1_TOKENS < exposure <= 4726656:
        raise RuntimeError("RUN 002 final exposure is outside authorized continuation")

    runtime = T.verify_runtime(
        TRAINER_SOURCE,
        CLI_SOURCE,
    )

    if not CHECKPOINT.is_file() or CHECKPOINT.is_symlink():
        raise RuntimeError("Final checkpoint is missing or unsafe")

    device = torch.device("cuda")
    state = torch.load(
        CHECKPOINT,
        map_location=device,
        weights_only=False,
    )
    if not isinstance(state, dict):
        raise RuntimeError("Final checkpoint payload is invalid")
    if state.get("schema_version") != "v60-extended-checkpoint-1":
        raise RuntimeError("Unexpected V60 checkpoint schema")
    if int(state.get("step", -1)) != steps:
        raise RuntimeError("Checkpoint/final-summary step mismatch")
    if int(state.get("exposure_tokens", -1)) != exposure:
        raise RuntimeError("Checkpoint/final-summary exposure mismatch")
    if (
        state.get("authorization_freeze_fingerprint")
        != runtime["authorization"]["freeze_fingerprint"]
    ):
        raise RuntimeError("Checkpoint authorization fingerprint mismatch")
    if (
        state.get("trainer_freeze_fingerprint")
        != runtime["trainer_freeze"]["trainer_freeze_fingerprint"]
    ):
        raise RuntimeError("Checkpoint trainer fingerprint mismatch")

    sampler_state = state.get("sampler")
    if not isinstance(sampler_state, dict):
        raise RuntimeError("Checkpoint sampler state missing")
    completed_cycles = int(
        sampler_state.get("completed_cycles", -1)
    )
    if not 8 <= completed_cycles <= 16:
        raise RuntimeError("Checkpoint sampler-cycle state is invalid")

    model = T.MODEL.MiniKuzaiPhase03V60(
        T.MODEL.Phase03Config()
    ).to(device)
    model.load_state_dict(state["model"])

    validation_segments, validation_inventory = (
        T.build_validation_segments()
    )
    if validation_inventory["records"] != 36:
        raise RuntimeError("VALIDATION inventory changed")

    final_loss = T._validation_loss(
        model,
        validation_segments,
        device,
    )

    tokenizer = T.load_tokenizer()
    final_probes = [
        T._greedy_probe(
            model,
            tokenizer,
            probe,
            device,
        )
        for probe in T._fixed_probe_segments(
            validation_segments
        )
    ]
    if len(final_probes) != 6:
        raise RuntimeError("Expected six final checkpoint probes")

    utf8_invalid = 0
    eos = 0
    empty = 0
    total_tokens = 0
    repeated_sum = 0
    maximum_run = 0
    output_hashes = set()

    for probe in final_probes:
        text = probe.get("generated_text")
        if not isinstance(text, str):
            raise RuntimeError("Invalid generated probe text")
        output_hashes.add(
            hashlib.sha256(text.encode("utf-8")).hexdigest()
        )
        utf8_invalid += int(
            probe.get("generated_utf8_valid") is not True
        )
        eos += int(probe.get("ended_with_eos") is True)
        empty += int(text == "")
        total_tokens += int(probe["generated_tokens"])
        repeated_sum += repeated_trigram_bp(text)
        maximum_run = max(maximum_run, max_char_run(text))

    stop = summary.get("stop_reason")
    allowed = {
        "PLATEAU_REVIEW_REQUIRED",
        "EARLY_STOP_VALIDATION_DEGRADATION",
        "MAX_OPTIMIZER_STEPS",
        "MAX_EXPOSURE_TOKENS",
        "SAMPLER_EXHAUSTED",
        "MILESTONE_REVIEW_REQUIRED",
    }
    if stop not in allowed:
        raise RuntimeError("Unexpected RUN 002 stop reason")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V60_RUN2_COMPLETED": 1,
        "V60_RUN2_RESUME": 1,
        "V60_RUN2_START_STEPS": EXPECTED_RUN1_STEPS,
        "V60_RUN2_FINAL_STEPS": steps,
        "V60_RUN2_DELTA_STEPS": steps - EXPECTED_RUN1_STEPS,
        "V60_RUN2_START_TOKENS": EXPECTED_RUN1_TOKENS,
        "V60_RUN2_FINAL_TOKENS": exposure,
        "V60_RUN2_DELTA_TOKENS": exposure - EXPECTED_RUN1_TOKENS,
        "V60_RUN2_COMPLETED_CYCLES": completed_cycles,
        "V60_RUN2_START_VAL_LOSS_X1E6": EXPECTED_RUN1_VAL_X1E6,
        "V60_RUN2_FINAL_VAL_LOSS_X1E6": loss_x1e6(final_loss),
        "V60_RUN2_FINAL_UTF8_INVALID": utf8_invalid,
        "V60_RUN2_FINAL_EOS": eos,
        "V60_RUN2_FINAL_DISTINCT": len(output_hashes),
        "V60_RUN2_FINAL_MEAN_TOKENS_X100":
            round(total_tokens * 100 / len(final_probes)),
        "V60_RUN2_FINAL_REPEAT_TRIGRAM_BP":
            round(repeated_sum / len(final_probes)),
        "V60_RUN2_FINAL_MAX_CHAR_RUN": maximum_run,
        "V60_RUN2_FINAL_EMPTY": empty,
        "V60_RUN2_BLIND_ACCESS": 0,
        "V60_RUN2_STOP_PLATEAU": int(
            stop == "PLATEAU_REVIEW_REQUIRED"
        ),
        "V60_RUN2_STOP_EARLY_VALIDATION": int(
            stop == "EARLY_STOP_VALIDATION_DEGRADATION"
        ),
        "V60_RUN2_STOP_MAX_STEPS": int(
            stop == "MAX_OPTIMIZER_STEPS"
        ),
        "V60_RUN2_STOP_MAX_TOKENS": int(
            stop == "MAX_EXPOSURE_TOKENS"
        ),
        "V60_RUN2_STOP_SAMPLER": int(
            stop == "SAMPLER_EXHAUSTED"
        ),
        "V60_RUN2_STOP_MILESTONE": int(
            stop == "MILESTONE_REVIEW_REQUIRED"
        ),
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
