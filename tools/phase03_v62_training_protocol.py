#!/usr/bin/env python3
"""Define the V62 controlled margin-training protocol."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "reviews" / "smoltalk-v62-training-protocol"

OBJECTIVE_FREEZE = (
    REPO / "reviews" / "smoltalk-v62-margin-objective-freeze"
    / "OBJECTIVE-FREEZE-001.json"
)
OBJECTIVE_PREFLIGHT = (
    REPO / "reviews" / "smoltalk-v62-margin-objective"
    / "REPORT-001.json"
)
V59_AUTH = (
    REPO / "reviews" / "smoltalk-v59-final-mix-freeze-authorization"
    / "TRAINING-AUTHORIZATION-001.json"
)
V60_INIT_FREEZE = (
    REPO / "reviews" / "smoltalk-v60-initialization-freeze"
    / "INITIALIZATION-FREEZE-001.json"
)

REFERENCE_TOKENS = 295416
INITIAL_WINDOW_CYCLES = 4
TOKENS_PER_OPTIMIZER_STEP = 8192
MAX_EXPOSURE = REFERENCE_TOKENS * INITIAL_WINDOW_CYCLES
MAX_OPTIMIZER_STEPS = math.ceil(
    MAX_EXPOSURE / TOKENS_PER_OPTIMIZER_STEP
)
SCHEDULER_HORIZON_STEPS = 577
EVAL_EVERY = math.ceil(REFERENCE_TOKENS / 2)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def build():
    objective = read_json(OBJECTIVE_FREEZE)
    preflight = read_json(OBJECTIVE_PREFLIGHT)
    v59 = read_json(V59_AUTH)
    init = read_json(V60_INIT_FREEZE)

    if objective.get("status") != "FROZEN":
        raise RuntimeError("V62 objective is not frozen")
    if objective.get("training_authorized") is not False:
        raise RuntimeError("V62 objective freeze authorizes training")
    if objective.get("blind_test_accessed") is not False:
        raise RuntimeError("V62 objective freeze indicates BLIND access")
    if preflight.get("status") != "PREFLIGHT_PASSED_FREEZE_REQUIRED":
        raise RuntimeError("V62 preflight is not passing")
    if not preflight["hardware_preflight"].get("passed"):
        raise RuntimeError("V62 hardware preflight is not passing")

    if v59.get("freeze_fingerprint") != (
        "40008ff0b106d3c58d2bf8196f539be2"
        "bf692d1e8ed3b7cd0e2dd1429b887503"
    ):
        raise RuntimeError("V59 corpus baseline changed")
    if init.get("initialization_freeze_fingerprint") != (
        "2e64f9e4749710e03f32db220cfe1ab5"
        "b0a304ef250ebe9408ad0224799e4cb6"
    ):
        raise RuntimeError("V60 initialization fingerprint changed")

    protocol = {
        "schema_version": "v62-margin-training-protocol-1",
        "status": "PROTOCOL_DEFINED_PREFLIGHT_PASSED",
        "architecture": "V60_ARCHITECTURE_V62_MARGIN_OBJECTIVE",
        "initialization_freeze_fingerprint":
            init["initialization_freeze_fingerprint"],
        "v59_corpus_baseline_fingerprint":
            v59["freeze_fingerprint"],
        "objective_freeze_fingerprint":
            objective["objective_freeze_fingerprint"],
        "parameters": 1184512,
        "context_length": 2048,
        "vocab_size": 1024,
        "dtype": "BF16",
        "seed": 42,
        "margin_objective": {
            "margin": objective["margin"],
            "terminal_weight": objective["terminal_weight"],
            "intermediate_weight": objective["intermediate_weight"],
            "training_boundary_balance_factor":
                objective["training_boundary_balance_factor"],
            "base_cross_entropy_unchanged": True,
            "ordinary_positions_unchanged": True,
        },
        "optimizer": {
            "name": "AdamW",
            "learning_rate": 3e-4,
            "betas": [0.9, 0.95],
            "eps": 1e-8,
            "weight_decay": 0.10,
        },
        "scheduler": {
            "name": "linear_warmup_cosine_decay",
            "warmup_steps": 20,
            "max_steps": SCHEDULER_HORIZON_STEPS,
            "min_learning_rate": 3e-5,
            "comparison_policy":
                "PRESERVE_V60_LR_TRAJECTORY_DURING_SHORT_WINDOW",
        },
        "batching": {
            "microbatch_sequences": 8,
            "optimizer_step_target_nonpad_tokens":
                TOKENS_PER_OPTIMIZER_STEP,
            "gradient_accumulation":
                "DYNAMIC_UNTIL_TOKEN_TARGET",
            "right_padding": True,
            "pad_token_id": 0,
            "loss_ignore_pad": True,
            "next_token_shift": True,
        },
        "gradient_clip_norm": 1.0,
        "exposure": {
            "reference_cycle_tokens": REFERENCE_TOKENS,
            "initial_window_cycles": INITIAL_WINDOW_CYCLES,
            "initial_window_max_exposure_tokens": MAX_EXPOSURE,
            "initial_window_max_optimizer_steps":
                MAX_OPTIMIZER_STEPS,
            "milestones": [
                {
                    "cycle": 1,
                    "exposure_tokens": REFERENCE_TOKENS,
                    "action": "RECORDED_MILESTONE",
                },
                {
                    "cycle": 2,
                    "exposure_tokens": REFERENCE_TOKENS * 2,
                    "action": "MANDATORY_CONTINUATION_REVIEW",
                },
                {
                    "cycle": 4,
                    "exposure_tokens": REFERENCE_TOKENS * 4,
                    "action": "FINAL_WINDOW_REVIEW",
                },
            ],
            "extension_requires_new_protocol_freeze": True,
            "unique_clean_tokens": REFERENCE_TOKENS,
            "target_share_bp": v59["target_share_bp"],
            "stream_quota_mode": "TOKEN_QUOTA_WITH_REPLACEMENT",
            "quota_overshoot_rule":
                "LAST_SEGMENT_MAY_OVERSHOOT_STREAM_QUOTA",
            "stream_share_tolerance_bp": 100,
        },
        "evaluation": {
            "validation_split": "FROZEN_VALIDATION_36",
            "validation_every_exposure_tokens": EVAL_EVERY,
            "teacher_forced_validation_loss": True,
            "validation_loss_metric":
                "STANDARD_NEXT_TOKEN_CE_FOR_V60_COMPARABILITY",
            "generation_probe": "FIXED_VALIDATION_PROMPTS",
            "generation_probe_max_new_tokens": 96,
            "blind_test_during_training": False,
            "blind_test_reserved_until_training_finalized": True,
            "continuation_signals": {
                "validation_loss": True,
                "generation_utf8_validity": True,
                "generation_eos": True,
                "generation_mean_length": True,
                "generation_repeat_trigram_rate": True,
                "generation_distinct_outputs": True,
            },
            "stop": {
                "nonfinite_loss": True,
                "nonfinite_gradient_norm": True,
                "relative_validation_loss_degradation_bp": 500,
                "consecutive_degraded_evals": 3,
                "minimum_completed_evals": 4,
            },
            "plateau_review": {
                "minimum_cycle": 2,
                "window_evaluations": 4,
                "minimum_validation_improvement_bp": 50,
                "action": "REVIEW_MARGIN_BEHAVIOR_BEFORE_CONTINUATION",
            },
            "milestone_review_cycles": [1, 2, 4],
            "mandatory_continuation_review_cycles": [2],
        },
        "checkpointing": {
            "every_exposure_tokens": EVAL_EVERY,
            "save_best_validation": True,
            "save_last": True,
            "save_milestones": True,
            "include_optimizer": True,
            "include_scheduler": True,
            "include_rng_state": True,
            "include_sampler_state": True,
        },
        "comparison": {
            "v60_architecture_preserved": True,
            "v60_initialization_preserved": True,
            "same_tokenizer": True,
            "same_training_corpus": True,
            "same_stream_weights": True,
            "same_optimizer": True,
            "same_lr_trajectory": True,
            "primary_change": "PAIRWISE_BOUNDARY_MARGIN_OBJECTIVE",
        },
        "training_authorized": False,
        "training_started": False,
    }

    report = {
        "schema_version": "v62-margin-training-protocol-report-1",
        "status": "PROTOCOL_PASSED_FREEZE_REQUIRED",
        "protocol": protocol,
        "hardware_preflight": preflight["hardware_preflight"],
        "protocol_freeze_candidate": True,
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }
    return protocol, report


def write(protocol, report):
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V62 training protocol output already exists")
    OUT.mkdir(parents=True)
    (OUT / "PROTOCOL-001.json").write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUT / "REPORT-001.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    obj = protocol["margin_objective"]
    lines = [
        "# Mini-Kuzai V62 - pairwise margin training protocol",
        "",
        "Status --> **PROTOCOL DEFINED / TRAINING NOT AUTHORIZED**",
        "",
        f"- margin --> **{obj['margin']}**",
        f"- terminal weight --> **{obj['terminal_weight']:.4f}**",
        f"- intermediate weight --> **{obj['intermediate_weight']:.4f}**",
        "- initial window --> **4 cycles / 1181664 tokens**",
        "- mandatory continuation review --> **cycle 2**",
        "- optimizer-step ceiling --> **145**",
        "- scheduler horizon --> **577 steps unchanged from V60**",
        "- BLIND TEST --> **CLOSED**",
        "",
        "TRAINING_AUTHORIZED --> **0**",
        "TRAINING_STARTED --> **0**",
        "",
        "---",
        "",
        "##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**",
        "",
    ]
    (OUT / "RESULTS-001.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def metrics(report):
    p = report["protocol"]
    obj = p["margin_objective"]
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V62_PROTOCOL_DEFINED": 1,
        "V62_PROTOCOL_PREFLIGHT_PASS": 1,
        "V62_PROTOCOL_INITIAL_CYCLES": 4,
        "V62_PROTOCOL_MAX_TOKENS": 1181664,
        "V62_PROTOCOL_MAX_STEPS": 145,
        "V62_PROTOCOL_SCHEDULER_STEPS": 577,
        "V62_PROTOCOL_REVIEW_CYCLE": 2,
        "V62_PROTOCOL_MARGIN_X1000":
            round(float(obj["margin"]) * 1000),
        "V62_PROTOCOL_TERMINAL_WEIGHT_X100":
            round(float(obj["terminal_weight"]) * 100),
        "V62_PROTOCOL_INTERMEDIATE_WEIGHT_X100":
            round(float(obj["intermediate_weight"]) * 100),
        "V62_PROTOCOL_BLIND_ACCESS": 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--from-report", action="store_true")
    args = parser.parse_args()

    if args.from_report:
        report = read_json(OUT / "REPORT-001.json")
    else:
        protocol, report = build()
        if args.write:
            write(protocol, report)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics(report).items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
