#!/usr/bin/env python3
"""Numeric-only V59 logit / initialization diagnostic.

Uses frozen VALIDATION only. BLIND TEST is never opened.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v59_trainer as T

RUN_DIR = Path("/root/Mini-Kuzai/runs/v59-bounded-pilot-001")
BEST = RUN_DIR / "checkpoint-best.pt"
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"
TRAINER_SOURCE = REPO / "mini_kuzai" / "phase03_v59_trainer.py"
CLI_SOURCE = REPO / "tools" / "train_v59_bounded_pilot.py"


def scaled(value: float) -> int:
    if not math.isfinite(value):
        raise RuntimeError("Non-finite metric")
    return round(value * 1_000_000)


def model_stats(model, segments, device):
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    logit_sum = 0.0
    logit_sq_sum = 0.0
    logit_count = 0
    max_abs = 0.0
    max_prob_sum = 0.0
    entropy_sum = 0.0
    entropy_count = 0

    with torch.no_grad():
        for start in range(0, len(segments), 8):
            batch_segments = segments[start:start + 8]
            token_ids, _, predicted = T.pad_batch(batch_segments, device)
            if predicted <= 0:
                continue

            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits = model(token_ids)
                targets = token_ids[:, 1:]
                shifted = logits[:, :-1, :]
                loss_sum = F.cross_entropy(
                    shifted.reshape(-1, T.VOCAB_SIZE),
                    targets.reshape(-1),
                    ignore_index=T.PAD_ID,
                    reduction="sum",
                )

            mask = targets != T.PAD_ID
            active = shifted[mask].float()
            if active.numel():
                logit_sum += float(active.sum().cpu())
                logit_sq_sum += float((active * active).sum().cpu())
                logit_count += active.numel()
                max_abs = max(max_abs, float(active.abs().max().cpu()))

                probs = torch.softmax(active, dim=-1)
                max_prob_sum += float(probs.max(dim=-1).values.sum().cpu())
                log_probs = torch.log_softmax(active, dim=-1)
                ent = -(probs * log_probs).sum(dim=-1)
                entropy_sum += float(ent.sum().cpu())
                entropy_count += int(ent.numel())

            total_loss += float(loss_sum.detach().cpu())
            total_tokens += int(mask.sum().item())

    if total_tokens <= 0 or logit_count <= 0 or entropy_count <= 0:
        raise RuntimeError("No active VALIDATION tokens")

    mean = logit_sum / logit_count
    variance = max(0.0, logit_sq_sum / logit_count - mean * mean)
    return {
        "loss": total_loss / total_tokens,
        "logit_std": math.sqrt(variance),
        "logit_max_abs": max_abs,
        "mean_max_prob": max_prob_sum / entropy_count,
        "mean_entropy": entropy_sum / entropy_count,
    }


def main():
    runtime = T.verify_runtime(TRAINER_SOURCE, CLI_SOURCE)
    validation_segments, inventory = T.build_validation_segments()
    if inventory["records"] != 36:
        raise RuntimeError("Unexpected VALIDATION inventory")

    summary = T.read_json(SUMMARY)
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("BLIND TEST was accessed")
    if summary.get("training_started") is not True:
        raise RuntimeError("Training did not start")

    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    device = torch.device("cuda")

    fresh = T.MODEL.MiniKuzaiPhase03(T.MODEL.Phase03Config()).to(device)
    fresh_embedding_std = float(fresh.token_embedding.weight.float().std().detach().cpu())
    fresh_position_std = float(fresh.position_embedding.weight.float().std().detach().cpu())
    fresh_stats = model_stats(fresh, validation_segments, device)
    del fresh
    torch.cuda.empty_cache()

    if not BEST.is_file() or BEST.is_symlink():
        raise RuntimeError("Best checkpoint missing")
    checkpoint = torch.load(BEST, map_location="cpu", weights_only=False)
    if not isinstance(checkpoint, dict):
        raise RuntimeError("Invalid best checkpoint")
    if checkpoint.get("trainer_freeze_fingerprint") != runtime["trainer_freeze"]["trainer_freeze_fingerprint"]:
        raise RuntimeError("Checkpoint trainer fingerprint mismatch")
    if checkpoint.get("authorization_freeze_fingerprint") != runtime["authorization"]["freeze_fingerprint"]:
        raise RuntimeError("Checkpoint authorization fingerprint mismatch")

    trained = T.MODEL.MiniKuzaiPhase03(T.MODEL.Phase03Config()).to(device)
    trained.load_state_dict(checkpoint["model"])
    trained_embedding_std = float(trained.token_embedding.weight.float().std().detach().cpu())
    trained_position_std = float(trained.position_embedding.weight.float().std().detach().cpu())
    trained_stats = model_stats(trained, validation_segments, device)

    uniform_ce = math.log(T.VOCAB_SIZE)
    uniform_entropy = math.log(T.VOCAB_SIZE)

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "V59_MIX_FINALIZED": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V59_LOGIT_DIAG_PASS": 1,
        "V59_LOGIT_BLIND_ACCESS": 0,
        "V59_LOGIT_VOCAB": T.VOCAB_SIZE,
        "V59_LOGIT_UNIFORM_CE_X1E6": scaled(uniform_ce),
        "V59_LOGIT_FRESH_CE_X1E6": scaled(fresh_stats["loss"]),
        "V59_LOGIT_TRAINED_CE_X1E6": scaled(trained_stats["loss"]),
        "V59_LOGIT_FRESH_EMB_STD_X1E6": scaled(fresh_embedding_std),
        "V59_LOGIT_TRAINED_EMB_STD_X1E6": scaled(trained_embedding_std),
        "V59_LOGIT_FRESH_POS_STD_X1E6": scaled(fresh_position_std),
        "V59_LOGIT_TRAINED_POS_STD_X1E6": scaled(trained_position_std),
        "V59_LOGIT_FRESH_STD_X1E6": scaled(fresh_stats["logit_std"]),
        "V59_LOGIT_TRAINED_STD_X1E6": scaled(trained_stats["logit_std"]),
        "V59_LOGIT_FRESH_MAXABS_X1E3": round(fresh_stats["logit_max_abs"] * 1000),
        "V59_LOGIT_TRAINED_MAXABS_X1E3": round(trained_stats["logit_max_abs"] * 1000),
        "V59_LOGIT_FRESH_MAXPROB_BP": round(fresh_stats["mean_max_prob"] * 10000),
        "V59_LOGIT_TRAINED_MAXPROB_BP": round(trained_stats["mean_max_prob"] * 10000),
        "V59_LOGIT_UNIFORM_ENTROPY_X1E6": scaled(uniform_entropy),
        "V59_LOGIT_FRESH_ENTROPY_X1E6": scaled(fresh_stats["mean_entropy"]),
        "V59_LOGIT_TRAINED_ENTROPY_X1E6": scaled(trained_stats["mean_entropy"]),
        "V59_LOGIT_BEST_STEP": int(checkpoint["step"]),
        "V59_LOGIT_BEST_EXPOSURE": int(checkpoint["exposure_tokens"]),
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
