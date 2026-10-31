#!/usr/bin/env python3
"""V63 corrected GPU diagnostic 002 for frozen V62 cycle-2.

GPU batched VALIDATION teacher forcing plus six separately labelled batched
greedy rollouts. Emits only numeric aggregates acceptable to GOGIT.
No training, checkpoint mutation, BLIND data or raw conversation publication.
"""
from __future__ import annotations

import importlib.util
import json
import math
import statistics
import sys
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v62_trainer as T

BASE = Path("/root/Mini-Kuzai/runs/v62-margin-001")
CHECKPOINT = BASE / "checkpoint-cycle-02.pt"
V62_RUN_STEP = "PHASE03-SMOLTALK-V62-TRAIN-RUN-001"
V62_EOS_STEP = "PHASE03-SMOLTALK-V62-TRAIN-RUN-001-EOS-CALIBRATION-001"
V61_EOS_STEP = "PHASE03-SMOLTALK-V61-TRAIN-RUN-001-EOS-CALIBRATION-001"
BATCH = 4
MAX_NEW_TOKENS = 96
MARGIN = 0.25


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"Invalid JSON object: {path}")
    return obj


def prior(step: str) -> dict:
    path = REPO / "reports" / "assistant-results" / "history" / f"{step}.json"
    report = read_json(path)
    if report.get("step_id") != step or report.get("semantic_validation_complete") is not True:
        raise RuntimeError(f"Published diagnostic gate invalid: {step}")
    metrics = report.get("metrics")
    if not isinstance(metrics, dict):
        raise RuntimeError(f"Missing published metrics: {step}")
    return metrics


def load_validation_helper():
    path = REPO / "tools" / "public-audits" / "phase03_v62_train_run_001_eos_calibration.py"
    spec = importlib.util.spec_from_file_location("v62_eos_helper_v63", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to import frozen V62 EOS audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pad_right(sequences: list[list[int]], device: torch.device) -> torch.Tensor:
    if not sequences or max(map(len, sequences)) > T.CONTEXT_LENGTH:
        raise RuntimeError("Invalid or over-context GPU batch")
    padded = torch.full(
        (len(sequences), max(map(len, sequences))),
        T.PAD_ID, dtype=torch.long, device=device,
    )
    for row, ids in enumerate(sequences):
        padded[row, :len(ids)] = torch.as_tensor(ids, dtype=torch.long, device=device)
    return padded


def teacher_forced(model, tokenizer, items, helper, device):
    terminal_total = terminal_top1 = terminal_margin_ok = 0
    inter_total = inter_top1 = inter_margin_ok = inter_eos_over_true = 0
    nonterm_total = nonterm_top1 = 0
    with torch.inference_mode():
        for first in range(0, len(items), BATCH):
            group = items[first:first + BATCH]
            x = pad_right([item["ids"] for item in group], device)
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits = model(x).float()
            for row, item in enumerate(group):
                ids = item["ids"]
                raw = logits[row, :len(ids) - 1]
                if ids[-1] != T.EOS_ID:
                    raise RuntimeError("VALIDATION terminal EOS missing")
                terminal = raw[-1].clone()
                eos_value = terminal[T.EOS_ID].clone()
                terminal[T.EOS_ID] = -torch.inf
                best_non_eos = terminal.max()
                gap = eos_value - best_non_eos
                terminal_total += 1
                terminal_top1 += int((gap >= 0).item())
                terminal_margin_ok += int((gap >= MARGIN).item())

                normal = raw[:-1]
                best_logits = normal.max(dim=-1).values
                eos_logits = normal[:, T.EOS_ID]
                nonterm_total += normal.shape[0]
                nonterm_top1 += int((eos_logits >= best_logits).sum().item())

                indices = helper.assistant_boundary_target_indices(
                    tokenizer, item["messages"], ids,
                )
                if indices:
                    idx = torch.as_tensor(indices, device=device, dtype=torch.long)
                    true_targets = torch.as_tensor(
                        [ids[i + 1] for i in indices], device=device, dtype=torch.long,
                    )
                    if bool((true_targets == T.EOS_ID).any().item()):
                        raise RuntimeError("Intermediate true continuation is EOS")
                    candidates = raw[idx]
                    true_logit = candidates.gather(1, true_targets[:, None]).squeeze(1)
                    eos_logit = candidates[:, T.EOS_ID]
                    inter_gap = true_logit - eos_logit
                    inter_total += len(indices)
                    inter_margin_ok += int((inter_gap >= MARGIN).sum().item())
                    inter_eos_over_true += int((eos_logit > true_logit).sum().item())
                    inter_top1 += int((
                        eos_logit >= candidates.max(dim=-1).values
                    ).sum().item())
    if (terminal_total, inter_total, nonterm_total) != (36, 13, 9170):
        raise RuntimeError("Frozen VALIDATION EOS position inventory changed")
    return {
        "TF_TERMINAL_COUNT": terminal_total,
        "TF_TERMINAL_TOP1": terminal_top1,
        "TF_TERMINAL_MARGIN_OK": terminal_margin_ok,
        "TF_INTERMEDIATE_COUNT": inter_total,
        "TF_INTERMEDIATE_TOP1": inter_top1,
        "TF_INTERMEDIATE_MARGIN_OK": inter_margin_ok,
        "TF_INTERMEDIATE_EOS_OVER_TRUE": inter_eos_over_true,
        "TF_NONTERMINAL_COUNT": nonterm_total,
        "TF_NONTERMINAL_TOP1": nonterm_top1,
    }


def repeated_token_trigram_bp(token_ids: list[int]) -> int:
    tokens = [value for value in token_ids if value != T.EOS_ID]
    triples = [tuple(tokens[i:i + 3]) for i in range(len(tokens) - 2)]
    return round((len(triples) - len(set(triples))) * 10000 / len(triples)) if triples else 0


def greedy_batched(model, tokenizer, validation_segments, device):
    fixed = T._fixed_probe_segments(validation_segments)
    marker = "\n\nMINI-KUZAI:\n"
    full = []
    prompt_lengths = []
    for segment in fixed:
        serial = tokenizer.decode(segment.token_ids)
        at = serial.find(marker)
        if at < 0:
            raise RuntimeError("Validation probe assistant header missing")
        prompt = serial[:at + len(marker)]
        ids = tokenizer.encode(prompt, add_bos=True, add_eos=False)
        if len(ids) + MAX_NEW_TOKENS >= T.CONTEXT_LENGTH:
            raise RuntimeError("Diagnostic generation context too long")
        full.append(list(ids))
        prompt_lengths.append(len(ids))

    done = [False] * len(full)
    best_rank = [T.VOCAB_SIZE + 1] * len(full)
    eos_max_probability = 0.0
    sum_eos_probability = 0.0
    sum_entropy = 0.0
    eos_top1 = 0
    total_steps = 0

    model.eval()
    with torch.inference_mode():
        for _ in range(MAX_NEW_TOKENS):
            active = [i for i in range(len(full)) if not done[i]]
            if not active:
                break
            x = pad_right([full[i] for i in active], device)
            ends = torch.as_tensor(
                [len(full[i]) - 1 for i in active], dtype=torch.long, device=device,
            )
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                raw = model(x)[
                    torch.arange(len(active), device=device), ends,
                ].float()
            probs = torch.softmax(raw, dim=-1)
            eos_p = probs[:, T.EOS_ID]
            ranks = (raw > raw[:, T.EOS_ID:T.EOS_ID + 1]).sum(dim=-1) + 1
            entropy = -(probs * probs.clamp_min(1e-12).log()).sum(dim=-1)
            token_ids = torch.argmax(raw, dim=-1)

            # One bounded transfer per GPU decode step, not per vocabulary token.
            ranks_cpu = ranks.tolist()
            eos_cpu = eos_p.tolist()
            entropy_cpu = entropy.tolist()
            tokens_cpu = token_ids.tolist()
            for j, i in enumerate(active):
                total_steps += 1
                best_rank[i] = min(best_rank[i], int(ranks_cpu[j]))
                eos_max_probability = max(eos_max_probability, eos_cpu[j])
                sum_eos_probability += eos_cpu[j]
                sum_entropy += entropy_cpu[j]
                eos_top1 += int(ranks_cpu[j] == 1)
                full[i].append(int(tokens_cpu[j]))
                if tokens_cpu[j] == T.EOS_ID:
                    done[i] = True

    if not 0 < total_steps <= 6 * MAX_NEW_TOKENS:
        raise RuntimeError("Invalid bounded GPU greedy rollout")
    generated = [full[i][prompt_lengths[i]:] for i in range(len(full))]
    if len(generated) != 6:
        raise RuntimeError("Fixed probe count changed")
    return {
        "FREE_PROBES": len(generated),
        "FREE_STEPS": total_steps,
        "FREE_EOS_COMPLETIONS": sum(done),
        "FREE_EOS_TOP1": eos_top1,
        "FREE_MAX_EOS_PROB_PPM": round(eos_max_probability * 1_000_000),
        "FREE_MEAN_EOS_PROB_PPM": round(sum_eos_probability * 1_000_000 / total_steps),
        "FREE_MEAN_BEST_EOS_RANK_X100": round(statistics.mean(best_rank) * 100),
        "FREE_REPEAT_TOKEN_TRIGRAM_BP": round(statistics.mean(repeated_token_trigram_bp(v) for v in generated)),
        "FREE_MEAN_TOKENS_X100": round(sum(map(len, generated)) * 100 / 6),
        "FREE_ENTROPY_X1000": round(sum_entropy * 1000 / total_steps),
    }


def main():
    run = read_json(BASE / "RUN-SUMMARY.json")
    manifest = read_json(BASE / "RUN-MANIFEST.json")
    if (run.get("schema_version"), manifest.get("schema_version")) != (
        "v62-margin-run-summary-1", "v62-margin-run-1"
    ):
        raise RuntimeError("Not a frozen V62 cycle-2 training run")
    if (
        run.get("status") != "STOPPED"
        or manifest.get("status") != "STOPPED"
        or run.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED"
        or manifest.get("resume") is not False
        or run.get("optimizer_steps") != 69
        or run.get("exposure_tokens") != 597982
        or run.get("blind_test_accessed") is not False
        or manifest.get("blind_test_during_training") is not False
    ):
        raise RuntimeError("V62 cycle-2 stop state is invalid")
    if (BASE / ".training.lock").exists():
        raise RuntimeError("V62 training lock present")
    if not CHECKPOINT.is_file() or CHECKPOINT.is_symlink():
        raise RuntimeError("Unsafe or absent V62 cycle-2 checkpoint")

    r62 = prior(V62_RUN_STEP)
    e62 = prior(V62_EOS_STEP)
    e61 = prior(V61_EOS_STEP)
    if (
        r62.get("V62_RUN1_COMPLETED") != 1
        or e62.get("V62_EOS1_LOGIT_DIAG_PASS") != 1
        or e61.get("V61_EOS1_LOGIT_DIAG_PASS") != 1
        or e62.get("V62_EOS1_LOGIT_BLIND_ACCESS") != 0
        or e61.get("V61_EOS1_LOGIT_BLIND_ACCESS") != 0
    ):
        raise RuntimeError("Historical GOGIT evidence is incomplete")

    runtime = T.verify_runtime(
        REPO / "mini_kuzai" / "phase03_v62_trainer.py",
        REPO / "tools" / "train_v62_margin.py",
    )
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError("V63 diagnostics require GPU CUDA/BF16")
    state = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    if (
        state.get("schema_version") != "v62-margin-checkpoint-1"
        or state.get("authorization_freeze_fingerprint")
            != runtime["authorization"]["freeze_fingerprint"]
        or state.get("trainer_freeze_fingerprint")
            != runtime["trainer_freeze"]["trainer_freeze_fingerprint"]
        or state.get("step") != 69
        or state.get("exposure_tokens") != 597982
    ):
        raise RuntimeError("V62 checkpoint identity mismatch")
    device = torch.device("cuda")
    model = T.MODEL.MiniKuzaiPhase03V60(T.MODEL.Phase03Config()).to(device)
    model.load_state_dict(state["model"])
    model.eval()
    del state

    tokenizer = T.load_tokenizer()
    helper = load_validation_helper()
    messages = helper.load_validation_message_segments(tokenizer)
    validation, inventory = T.build_validation_segments()
    if inventory.get("records") != 36:
        raise RuntimeError("VALIDATION inventory no longer frozen")

    torch.cuda.reset_peak_memory_stats(device)
    tf = teacher_forced(model, tokenizer, messages, helper, device)
    rollout = greedy_batched(model, tokenizer, validation, device)
    peak_mib = math.ceil(torch.cuda.max_memory_allocated(device) / (1024 ** 2))

    # Compare the new batched teacher-forced diagnostic with the historical
    # per-sequence V62 audit, and keep the differences visible if present.
    # No equality assertion: BF16 kernels can round differently by batch.
    output = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V63_DIAG_PREFLIGHT_PASS": 1,
        "V63_DIAG_BLIND_ACCESS": 0,
        "V63_DIAG_GPU_BF16": 1,
        "V63_DIAG_GPU_BATCH": BATCH,
        "V63_DIAG_GPU_PEAK_MIB": peak_mib,
    }
    output.update({f"V63_DIAG_{key}": value for key, value in tf.items()})
    output.update({f"V63_DIAG_{key}": value for key, value in rollout.items()})
    reference = {
        "V63_DIAG_TF_TERMINAL_TOP1": e62["V62_EOS1_TERM_TOP1"],
        "V63_DIAG_TF_INTERMEDIATE_TOP1": e62["V62_EOS1_INTERMEDIATE_TOP1"],
        "V63_DIAG_TF_INTERMEDIATE_EOS_OVER_TRUE": e62["V62_EOS1_INTERMEDIATE_OVER_TRUE"],
        "V63_DIAG_TF_NONTERMINAL_TOP1": e62["V62_EOS1_NONTERM_TOP1"],
    }
    for key, expected in reference.items():
        if output[key] != expected:
            raise RuntimeError(f"V63 corrected reference mismatch: {key}")
    if len(output) > 30:
        raise RuntimeError("GOGIT public metric limit exceeded")
    if any(
        not isinstance(value, int) or not 0 <= value <= 100_000_000
        for value in output.values()
    ):
        raise RuntimeError("Invalid public numeric diagnostic metric")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(output.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
