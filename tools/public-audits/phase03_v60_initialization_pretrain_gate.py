#!/usr/bin/env python3
"""Numeric-only V60 initialization pre-train gate.

The gate uses the frozen VALIDATION corpus only. It does not train the model
and it does not access BLIND TEST material.
"""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_model as V58
from mini_kuzai import phase03_v59_trainer as T
from mini_kuzai import phase03_v60_model as V60

TEST = REPO / "tests" / "phase-03" / "test_phase03_v60_initialization.py"


def scaled(value: float) -> int:
    if not math.isfinite(value):
        raise RuntimeError("Non-finite metric")
    return round(value * 1_000_000)


def run_tests() -> None:
    process = subprocess.run(
        [sys.executable, str(TEST)],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if process.returncode:
        raise RuntimeError(
            "V60 initialization tests failed\n"
            + process.stdout
        )


def architecture_matches() -> bool:
    config = V58.Phase03Config()
    old = V58.MiniKuzaiPhase03(config)
    new = V60.MiniKuzaiPhase03V60(config)
    old_state = old.state_dict()
    new_state = new.state_dict()
    if old_state.keys() != new_state.keys():
        return False
    return all(
        tuple(old_state[key].shape)
        == tuple(new_state[key].shape)
        for key in old_state
    )


def validation_stats(model, segments, device) -> dict:
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    entropy_sum = 0.0
    top1_sum = 0.0
    active_rows = 0
    logit_sum = 0.0
    logit_sq_sum = 0.0
    logit_count = 0
    logit_max_abs = 0.0

    with torch.no_grad():
        for start in range(0, len(segments), 8):
            batch = segments[start:start + 8]
            token_ids, _, predicted = T.pad_batch(batch, device)
            if predicted <= 0:
                continue

            with torch.autocast(
                device_type="cuda",
                dtype=torch.bfloat16,
            ):
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
                probs = torch.softmax(active, dim=-1)
                log_probs = torch.log_softmax(active, dim=-1)
                entropy = -(probs * log_probs).sum(dim=-1)
                top1 = probs.max(dim=-1).values

                entropy_sum += float(entropy.sum().cpu())
                top1_sum += float(top1.sum().cpu())
                active_rows += int(entropy.numel())

                logit_sum += float(active.sum().cpu())
                logit_sq_sum += float((active * active).sum().cpu())
                logit_count += int(active.numel())
                logit_max_abs = max(
                    logit_max_abs,
                    float(active.abs().max().cpu()),
                )

            total_loss += float(loss_sum.detach().cpu())
            total_tokens += int(mask.sum().item())

    if total_tokens <= 0 or active_rows <= 0 or logit_count <= 0:
        raise RuntimeError("VALIDATION produced no active tokens")

    mean = logit_sum / logit_count
    variance = max(
        0.0,
        logit_sq_sum / logit_count - mean * mean,
    )
    return {
        "ce": total_loss / total_tokens,
        "entropy": entropy_sum / active_rows,
        "top1": top1_sum / active_rows,
        "logit_std": math.sqrt(variance),
        "logit_max_abs": logit_max_abs,
    }


def main() -> None:
    T.verify_authorization()
    run_tests()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required for V60 pre-train gate")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("BF16 required for V60 pre-train gate")

    arch_match = architecture_matches()
    if not arch_match:
        raise RuntimeError("V60 architecture differs from V58")

    validation_segments, inventory = T.build_validation_segments()
    if inventory["records"] != 36 or inventory["segments"] != 36:
        raise RuntimeError("Frozen VALIDATION inventory changed")

    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    device = torch.device("cuda")
    config = V60.Phase03Config()
    model = V60.MiniKuzaiPhase03V60(config).to(device)

    parameter_count = V60.count_parameters(model)
    tied = (
        model.lm_head.weight
        is model.token_embedding.weight
    )
    pad_zero = (
        int(
            torch.count_nonzero(
                model.token_embedding.weight[
                    config.pad_token_id
                ]
            ).item()
        )
        == 0
    )

    embedding_std = float(
        model.token_embedding.weight[1:]
        .float()
        .std()
        .detach()
        .cpu()
    )
    position_std = float(
        model.position_embedding.weight
        .float()
        .std()
        .detach()
        .cpu()
    )
    residual_stds = []
    for block in model.blocks:
        residual_stds.extend(
            [
                float(
                    block.attention.out_proj.weight
                    .float()
                    .std()
                    .detach()
                    .cpu()
                ),
                float(
                    block.mlp.fc2.weight
                    .float()
                    .std()
                    .detach()
                    .cpu()
                ),
            ]
        )
    residual_std = sum(residual_stds) / len(residual_stds)

    stats = validation_stats(
        model,
        validation_segments,
        device,
    )

    uniform_ce = math.log(config.vocab_size)
    ce_delta = abs(stats["ce"] - uniform_ce)

    checks = {
        "params": parameter_count == 1184512,
        "tied": tied,
        "pad_zero": pad_zero,
        "embedding_std": 0.015 <= embedding_std <= 0.025,
        "position_std": 0.015 <= position_std <= 0.025,
        "ce": ce_delta <= 0.75,
        "entropy": stats["entropy"] >= 6.0,
        "top1": stats["top1"] <= 0.05,
        "logit_std": stats["logit_std"] <= 1.0,
        "logit_max_abs": stats["logit_max_abs"] <= 10.0,
    }
    gate_pass = all(checks.values())

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
        "V60_INIT_GATE_PASS": int(gate_pass),
        "V60_INIT_TESTS_PASS": 1,
        "V60_INIT_ARCH_MATCH": int(arch_match),
        "V60_INIT_PARAMS": parameter_count,
        "V60_INIT_TIED": int(tied),
        "V60_INIT_PAD_ZERO": int(pad_zero),
        "V60_INIT_EMB_STD_X1E6": scaled(embedding_std),
        "V60_INIT_POS_STD_X1E6": scaled(position_std),
        "V60_INIT_RESIDUAL_STD_X1E6": scaled(residual_std),
        "V60_INIT_UNIFORM_CE_X1E6": scaled(uniform_ce),
        "V60_INIT_CE_X1E6": scaled(stats["ce"]),
        "V60_INIT_CE_DELTA_X1E6": scaled(ce_delta),
        "V60_INIT_ENTROPY_X1E6": scaled(stats["entropy"]),
        "V60_INIT_TOP1_BP": round(stats["top1"] * 10000),
        "V60_INIT_LOGIT_STD_X1E6": scaled(stats["logit_std"]),
        "V60_INIT_LOGIT_MAXABS_X1E3": round(
            stats["logit_max_abs"] * 1000
        ),
        "V60_INIT_VALIDATION_RECORDS": inventory["records"],
        "V60_INIT_VALIDATION_SEGMENTS": inventory["segments"],
        "V60_INIT_BLIND_ACCESS": 0,
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
