#!/usr/bin/env python3
"""Define the V60 extended local-training protocol without authorizing training."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v60_model as MODEL

INIT_FREEZE = (
    REPO / "reviews" / "smoltalk-v60-initialization-freeze"
    / "INITIALIZATION-FREEZE-001.json"
)
V59_AUTH = (
    REPO / "reviews" / "smoltalk-v59-final-mix-freeze-authorization"
    / "TRAINING-AUTHORIZATION-001.json"
)
OUT = REPO / "reviews" / "smoltalk-v60-extended-training-protocol"

PARAMETERS = 1184512
REFERENCE_TOKENS = 295416
MILESTONE_CYCLES = [1, 4, 8, 16]
INITIAL_WINDOW_CYCLES = 16
EXTENSION_BLOCK_CYCLES = 8
TOKENS_PER_OPTIMIZER_STEP = 8192
MICROBATCH_SEQUENCES = 8
BASE_LR = 3e-4
MIN_LR = 3e-5
WARMUP_STEPS = 20
WEIGHT_DECAY = 0.10
BETA1 = 0.9
BETA2 = 0.95
EPS = 1e-8
GRAD_CLIP = 1.0
SEED = 42
MEMORY_GATE_BP = 6000


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe input: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def build_protocol() -> dict:
    freeze = read_json(INIT_FREEZE)
    auth = read_json(V59_AUTH)

    if freeze.get("status") != "FROZEN":
        raise RuntimeError("V60 initialization is not frozen")
    if freeze.get("training_authorized") is not False:
        raise RuntimeError("V60 initialization freeze unexpectedly authorizes training")
    if freeze.get("training_started") is not False:
        raise RuntimeError("V60 initialization freeze marks training as started")
    if freeze.get("blind_test_accessed") is not False:
        raise RuntimeError("V60 initialization freeze accessed BLIND TEST")
    if freeze.get("parameters") != PARAMETERS:
        raise RuntimeError("V60 parameter count changed")

    if auth.get("freeze_fingerprint") != freeze.get(
        "v59_corpus_baseline_fingerprint"
    ):
        raise RuntimeError("Corpus baseline fingerprint mismatch")
    if auth.get("total_unique_training_tokens") != REFERENCE_TOKENS:
        raise RuntimeError("Reference training-token count changed")

    max_exposure = REFERENCE_TOKENS * INITIAL_WINDOW_CYCLES
    max_steps = math.ceil(
        max_exposure / TOKENS_PER_OPTIMIZER_STEP
    )
    eval_every = math.ceil(REFERENCE_TOKENS / 2)

    milestones = [
        {
            "cycle": cycle,
            "exposure_tokens": REFERENCE_TOKENS * cycle,
            "action": (
                "MANDATORY_CONTINUATION_REVIEW"
                if cycle in {8, 16}
                else "RECORDED_MILESTONE"
            ),
        }
        for cycle in MILESTONE_CYCLES
    ]

    return {
        "schema_version": "v60-extended-training-protocol-1",
        "status": "PROTOCOL_DEFINED_PREFLIGHT_REQUIRED",
        "architecture": "V58_SHAPE_V60_INITIALIZATION_FROZEN",
        "initialization_freeze_fingerprint": freeze[
            "initialization_freeze_fingerprint"
        ],
        "v59_corpus_baseline_fingerprint": auth[
            "freeze_fingerprint"
        ],
        "parameters": PARAMETERS,
        "context_length": 2048,
        "vocab_size": 1024,
        "dtype": "BF16",
        "seed": SEED,
        "optimizer": {
            "name": "AdamW",
            "learning_rate": BASE_LR,
            "betas": [BETA1, BETA2],
            "eps": EPS,
            "weight_decay": WEIGHT_DECAY,
        },
        "scheduler": {
            "name": "linear_warmup_cosine_decay",
            "warmup_steps": WARMUP_STEPS,
            "max_steps": max_steps,
            "min_learning_rate": MIN_LR,
            "extension_policy": (
                "NEW_PROTOCOL_FREEZE_REQUIRED_BEYOND_INITIAL_WINDOW"
            ),
        },
        "batching": {
            "microbatch_sequences": MICROBATCH_SEQUENCES,
            "optimizer_step_target_nonpad_tokens":
                TOKENS_PER_OPTIMIZER_STEP,
            "gradient_accumulation":
                "DYNAMIC_UNTIL_TOKEN_TARGET",
            "right_padding": True,
            "pad_token_id": 0,
            "loss_ignore_pad": True,
            "next_token_shift": True,
        },
        "gradient_clip_norm": GRAD_CLIP,
        "exposure": {
            "reference_cycle_tokens": REFERENCE_TOKENS,
            "initial_window_cycles": INITIAL_WINDOW_CYCLES,
            "initial_window_max_exposure_tokens": max_exposure,
            "initial_window_max_optimizer_steps": max_steps,
            "milestones": milestones,
            "extension_block_cycles": EXTENSION_BLOCK_CYCLES,
            "extension_requires_new_protocol_freeze": True,
            "unique_clean_tokens": REFERENCE_TOKENS,
            "target_share_bp": auth["target_share_bp"],
            "stream_quota_mode":
                "TOKEN_QUOTA_WITH_REPLACEMENT",
            "quota_overshoot_rule":
                "LAST_SEGMENT_MAY_OVERSHOOT_STREAM_QUOTA",
            "stream_share_tolerance_bp": 100,
        },
        "evaluation": {
            "validation_split": "FROZEN_VALIDATION_36",
            "validation_every_exposure_tokens": eval_every,
            "teacher_forced_validation_loss": True,
            "generation_probe": "FIXED_VALIDATION_PROMPTS",
            "generation_probe_max_new_tokens": 96,
            "blind_test_during_training": False,
            "blind_test_reserved_until_training_finalized": True,
            "continuation_signals": {
                "validation_loss": True,
                "generation_utf8_validity": True,
                "generation_eos": True,
                "generation_repeat_trigram_rate": True,
                "generation_distinct_outputs": True,
            },
            "stop": {
                "nonfinite_loss": True,
                "nonfinite_gradient_norm": True,
                "relative_validation_loss_degradation_bp": 500,
                "consecutive_degraded_evals": 3,
                "minimum_completed_evals": 6,
            },
            "plateau_review": {
                "minimum_cycle": 4,
                "window_evaluations": 4,
                "minimum_validation_improvement_bp": 50,
                "action":
                    "REVIEW_GENERATION_BEFORE_STOP_OR_EXTENSION",
            },
            "milestone_review_cycles": [1, 4, 8, 16],
        },
        "checkpointing": {
            "every_exposure_tokens": eval_every,
            "save_best_validation": True,
            "save_last": True,
            "save_milestones": True,
            "include_optimizer": True,
            "include_scheduler": True,
            "include_rng_state": True,
            "include_sampler_state": True,
        },
        "hardware_preflight": {
            "full_context_microbatch_sequences":
                MICROBATCH_SEQUENCES,
            "memory_gate_bp": MEMORY_GATE_BP,
            "require_cuda": True,
            "require_bf16": True,
        },
        "comparison": {
            "v59_baseline_preserved": True,
            "same_tokenizer": True,
            "same_training_corpus": True,
            "same_stream_weights": True,
            "primary_model_change":
                "CORRECTED_PARAMETER_INITIALIZATION",
        },
        "torch_compile": False,
        "training_authorized": False,
        "training_started": False,
    }


def hardware_preflight() -> dict:
    if not torch.cuda.is_available():
        return {"passed": False, "reason": "CUDA_UNAVAILABLE"}
    if not torch.cuda.is_bf16_supported():
        return {"passed": False, "reason": "BF16_UNAVAILABLE"}

    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    device = torch.device("cuda")
    model = MODEL.MiniKuzaiPhase03V60(
        MODEL.Phase03Config()
    ).to(device)
    if MODEL.count_parameters(model) != PARAMETERS:
        raise RuntimeError("V60 parameter count changed")

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=BASE_LR,
        betas=(BETA1, BETA2),
        eps=EPS,
        weight_decay=WEIGHT_DECAY,
    )

    token_ids = torch.randint(
        3,
        1024,
        (MICROBATCH_SEQUENCES, 2048),
        device=device,
        dtype=torch.long,
    )

    optimizer.zero_grad(set_to_none=True)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    with torch.autocast(
        device_type="cuda",
        dtype=torch.bfloat16,
    ):
        logits = model(token_ids)
        targets = token_ids[:, 1:]
        loss = F.cross_entropy(
            logits[:, :-1, :].reshape(-1, 1024),
            targets.reshape(-1),
        )

    finite_loss = bool(torch.isfinite(loss).item())
    finite_grad = False
    grad_norm = None
    if finite_loss:
        loss.backward()
        value = torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            GRAD_CLIP,
        )
        finite_grad = bool(
            torch.isfinite(torch.as_tensor(value)).item()
        )
        if finite_grad:
            grad_norm = float(value.detach().cpu())
            optimizer.step()

    torch.cuda.synchronize()
    reserved = int(torch.cuda.max_memory_reserved())
    allocated = int(torch.cuda.max_memory_allocated())
    total = int(
        torch.cuda.get_device_properties(0).total_memory
    )
    reserved_bp = (
        round(reserved * 10000 / total)
        if total
        else 10000
    )
    passed = (
        finite_loss
        and finite_grad
        and reserved_bp <= MEMORY_GATE_BP
    )

    return {
        "passed": passed,
        "device_name": torch.cuda.get_device_name(0),
        "bf16": True,
        "loss_finite": finite_loss,
        "gradient_norm_finite": finite_grad,
        "preclip_gradient_norm": grad_norm,
        "peak_allocated_mib":
            allocated // (1024 * 1024),
        "peak_reserved_mib":
            reserved // (1024 * 1024),
        "total_memory_mib":
            total // (1024 * 1024),
        "peak_reserved_bp": reserved_bp,
        "memory_gate_bp": MEMORY_GATE_BP,
    }


def write(protocol: dict, preflight: dict) -> dict:
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V60 protocol output already exists")
    OUT.mkdir(parents=True)

    candidate = bool(preflight.get("passed"))
    report = {
        "schema_version":
            "v60-extended-training-protocol-report-1",
        "status": (
            "PREFLIGHT_PASSED_FREEZE_REQUIRED"
            if candidate
            else "PREFLIGHT_FAILED"
        ),
        "protocol": protocol,
        "hardware_preflight": preflight,
        "protocol_freeze_candidate": candidate,
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }

    (OUT / "PROTOCOL-001.json").write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUT / "REPORT-001.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    max_tokens = protocol["exposure"][
        "initial_window_max_exposure_tokens"
    ]
    max_steps = protocol["exposure"][
        "initial_window_max_optimizer_steps"
    ]
    lines = [
        "# Mini-Kuzai V60 - extended local training protocol",
        "",
        "Status --> **PROTOCOL DEFINED / TRAINING NOT AUTHORIZED**",
        "",
        "## Initial training window",
        "",
        "- reference cycle --> **295416 tokens**",
        "- milestones --> **1 / 4 / 8 / 16 cycles**",
        f"- initial window --> **{max_tokens} exposure tokens**",
        f"- initial optimizer-step ceiling --> **{max_steps}**",
        "- extension block --> **8 cycles**",
        "- extension beyond cycle 16 --> **new protocol freeze required**",
        "",
        "## Optimization",
        "",
        "- optimizer --> **AdamW**",
        "- base learning rate --> **0.0003**",
        "- minimum learning rate --> **0.00003**",
        "- warmup --> **20 optimizer steps**",
        "- scheduler --> **linear warmup + cosine decay**",
        "- gradient clip --> **1.0**",
        "- microbatch --> **8 sequences**",
        "- optimizer target --> **8192 non-pad tokens**",
        "",
        "## Evaluation policy",
        "",
        "- VALIDATION --> every half reference cycle",
        "- fixed generation probes --> every validation point",
        "- BLIND TEST --> closed during training",
        "- mandatory milestone reviews --> cycles 1 / 4 / 8 / 16",
        "- degradation stop --> 5 percent over best for 3 consecutive evaluations",
        "- plateau review --> less than 0.5 percent validation improvement across 4 evaluations after cycle 4",
        "- continuation decision --> VALIDATION plus generation quality",
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
    return report


def metrics(report: dict) -> dict:
    protocol = report["protocol"]
    preflight = report["hardware_preflight"]
    exposure = protocol["exposure"]
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
        "V60_PROTOCOL_DEFINED": 1,
        "V60_PROTOCOL_PREFLIGHT_PASS": int(
            bool(preflight.get("passed"))
        ),
        "V60_PROTOCOL_INITIAL_CYCLES":
            exposure["initial_window_cycles"],
        "V60_PROTOCOL_MAX_TOKENS":
            exposure["initial_window_max_exposure_tokens"],
        "V60_PROTOCOL_MAX_STEPS":
            exposure["initial_window_max_optimizer_steps"],
        "V60_PROTOCOL_EXTENSION_CYCLES":
            exposure["extension_block_cycles"],
        "V60_PROTOCOL_MILESTONES": len(
            exposure["milestones"]
        ),
        "V60_PROTOCOL_EVAL_EVERY_TOKENS":
            protocol["evaluation"][
                "validation_every_exposure_tokens"
            ],
        "V60_PROTOCOL_MICROBATCH":
            protocol["batching"]["microbatch_sequences"],
        "V60_PROTOCOL_STEP_TOKENS":
            protocol["batching"][
                "optimizer_step_target_nonpad_tokens"
            ],
        "V60_PROTOCOL_LR_X1E9": round(
            protocol["optimizer"]["learning_rate"] * 1e9
        ),
        "V60_PROTOCOL_MIN_LR_X1E9": round(
            protocol["scheduler"]["min_learning_rate"] * 1e9
        ),
        "V60_PROTOCOL_WARMUP_STEPS":
            protocol["scheduler"]["warmup_steps"],
        "V60_PROTOCOL_RESERVED_BP": int(
            preflight.get("peak_reserved_bp", 0) or 0
        ),
        "V60_PROTOCOL_RESERVED_MIB": int(
            preflight.get("peak_reserved_mib", 0) or 0
        ),
        "V60_PROTOCOL_BLIND_ACCESS": 0,
        "V60_PROTOCOL_TRAINING_STARTED": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--from-report", action="store_true")
    args = parser.parse_args()

    if args.from_report:
        report = read_json(OUT / "REPORT-001.json")
    else:
        protocol = build_protocol()
        preflight = hardware_preflight()
        report = {
            "protocol": protocol,
            "hardware_preflight": preflight,
        }
        if args.write:
            report = write(protocol, preflight)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics(report).items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
