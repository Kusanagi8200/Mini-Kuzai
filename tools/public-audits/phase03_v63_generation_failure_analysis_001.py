#!/usr/bin/env python3
"""V63 GPU generation-failure diagnostic 001 on frozen V62 cycle-2.

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
    token_count = correct_top1 = nonterm_eos_top1 = 0
    true_prob_sum = entropy_sum = 0.0
    term_count = term_top1 = term_margin = 0
    inter_count = inter_top1 = inter_margin = 0
    term_deficit_sum = inter_deficit_sum = 0.0
    with torch.inference_mode():
        for first in range(0, len(items), BATCH):
            group = items[first:first + BATCH]
            x = pad_right([item["ids"] for item in group], device)
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                batched = model(x).float()
            for row, item in enumerate(group):
                ids = item["ids"]
                raw = batched[row, :len(ids) - 1]
                targets = torch.as_tensor(ids[1:], dtype=torch.long, device=device)
                if targets[-1].item() != T.EOS_ID:
                    raise RuntimeError("Terminal EOS missing in frozen VALIDATION")
                p = torch.softmax(raw, dim=-1)
                true_p = p.gather(1, targets[:, None]).squeeze(1)
                entropy = -(p * p.clamp_min(1e-12).log()).sum(dim=-1)
                true_prob_sum += float(true_p.sum().item())
                entropy_sum += float(entropy.sum().item())
                correct_top1 += int((raw.argmax(dim=-1) == targets).sum().item())
                token_count += targets.numel()

                # Never mask a tensor view of the original EOS logit.
                end_logits = raw[-1]
                eos = end_logits[T.EOS_ID]
                competitor = torch.cat((
                    end_logits[:T.EOS_ID], end_logits[T.EOS_ID + 1:]
                )).max()
                gap = eos - competitor
                term_count += 1
                term_top1 += int((gap >= 0).item())
                term_margin += int((gap >= MARGIN).item())
                term_deficit_sum += float((-gap).clamp_min(0).item())

                nonterminal = raw[:-1]
                nonterm_eos_top1 += int((
                    nonterminal[:, T.EOS_ID] >= nonterminal.max(dim=-1).values
                ).sum().item())

                positions = helper.assistant_boundary_target_indices(
                    tokenizer, item["messages"], ids,
                )
                if positions:
                    ix = torch.as_tensor(positions, dtype=torch.long, device=device)
                    true_ix = targets[ix]
                    if bool((true_ix == T.EOS_ID).any().item()):
                        raise RuntimeError("Intermediate target is EOS")
                    logits = raw[ix]
                    true_logits = logits.gather(1, true_ix[:, None]).squeeze(1)
                    eos_logits = logits[:, T.EOS_ID]
                    gap = true_logits - eos_logits
                    inter_count += len(positions)
                    inter_margin += int((gap >= MARGIN).sum().item())
                    inter_deficit_sum += float((-gap).clamp_min(0).sum().item())
                    inter_top1 += int((
                        eos_logits >= logits.max(dim=-1).values
                    ).sum().item())

    if (term_count, inter_count, token_count - term_count) != (36, 13, 9170):
        raise RuntimeError("VALIDATION boundary inventory mismatch")

    return {
        "TF_TOKENS": token_count,
        "TF_TRUE_TOP1": correct_top1,
        "TF_TRUE_PROB_PPM": round(true_prob_sum * 1_000_000 / token_count),
        "TF_ENTROPY_X1000": round(entropy_sum * 1000 / token_count),
        "TF_TERM_GAP_DEFICIT_X1000": round(term_deficit_sum * 1000 / term_count),
        "TF_TERM_TOP1": term_top1,
        "TF_TERM_MARGIN_OK": term_margin,
        "TF_INTER_GAP_DEFICIT_X1000": round(inter_deficit_sum * 1000 / inter_count),
        "TF_INTER_TOP1": inter_top1,
        "TF_INTER_MARGIN_OK": inter_margin,
        "TF_NONTERM_EOS_TOP1": nonterm_eos_top1,
    }


def repeated_token_trigram_bp(token_ids: list[int]) -> int:
    tokens = [value for value in token_ids if value != T.EOS_ID]
    triples = [tuple(tokens[i:i + 3]) for i in range(len(tokens) - 2)]
    return round((len(triples) - len(set(triples))) * 10000 / len(triples)) if triples else 0


def gram_stats(tokens: list[int], width: int):
    seen = set()
    repeated = 0
    first_repeat = 0
    for i in range(max(0, len(tokens) - width + 1)):
        gram = tuple(tokens[i:i + width])
        if gram in seen:
            repeated += 1
            if not first_repeat:
                first_repeat = i + width
        else:
            seen.add(gram)
    windows = max(0, len(tokens) - width + 1)
    return (
        round(repeated * 10000 / windows) if windows else 0,
        first_repeat,
    )


def greedy_batched(model, tokenizer, validation_segments, device):
    fixed = T._fixed_probe_segments(validation_segments)
    marker = "\n\nMINI-KUZAI:\n"
    full, lengths = [], []
    for segment in fixed:
        serial = tokenizer.decode(segment.token_ids)
        pos = serial.find(marker)
        if pos < 0:
            raise RuntimeError("Frozen validation prompt header missing")
        ids = tokenizer.encode(serial[:pos + len(marker)], add_bos=True, add_eos=False)
        if len(ids) + MAX_NEW_TOKENS >= T.CONTEXT_LENGTH:
            raise RuntimeError("Probe context would exceed architecture limit")
        full.append(list(ids))
        lengths.append(len(ids))

    done = [False] * len(full)
    steps = 0
    top_probability_sum = entropy_sum = eos_deficit_sum = 0.0
    with torch.inference_mode():
        for _ in range(MAX_NEW_TOKENS):
            active = [i for i in range(len(full)) if not done[i]]
            if not active:
                break
            batch = pad_right([full[i] for i in active], device)
            tail = torch.as_tensor([len(full[i]) - 1 for i in active],
                                   device=device, dtype=torch.long)
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                raw = model(batch)[
                    torch.arange(len(active), device=device), tail
                ].float()
            p = torch.softmax(raw, dim=-1)
            chosen = torch.argmax(raw, dim=-1)
            entropy = -(p * p.clamp_min(1e-12).log()).sum(dim=-1)
            selected_p = p.gather(1, chosen[:, None]).squeeze(1)
            eos_logits = raw[:, T.EOS_ID]
            competitors = torch.cat(
                (raw[:, :T.EOS_ID], raw[:, T.EOS_ID + 1:]), dim=-1
            ).max(dim=-1).values
            # Positive deficit means EOS is below a non-EOS competitor.
            eos_deficit_sum += float((competitors - eos_logits).clamp_min(0).sum().item())
            top_probability_sum += float(selected_p.sum().item())
            entropy_sum += float(entropy.sum().item())
            next_ids = chosen.tolist()
            steps += len(next_ids)
            for k, i in enumerate(active):
                token = int(next_ids[k])
                full[i].append(token)
                if token == T.EOS_ID:
                    done[i] = True

    generated = [full[i][lengths[i]:] for i in range(len(full))]
    if len(generated) != 6 or not 0 < steps <= 6 * MAX_NEW_TOKENS:
        raise RuntimeError("Invalid greedy probe count")
    repeat3 = [gram_stats(v, 3)[0] for v in generated]
    repeat8 = [gram_stats(v, 8) for v in generated]
    observed_onsets = [position for _, position in repeat8 if position]
    return {
        "FREE_PROBES": len(generated),
        "FREE_EOS_COMPLETIONS": sum(done),
        "FREE_EOS_GAP_DEFICIT_X1000": round(eos_deficit_sum * 1000 / steps),
        "FREE_TOP1_PROB_PPM": round(top_probability_sum * 1_000_000 / steps),
        "FREE_ENTROPY_X1000": round(entropy_sum * 1000 / steps),
        "FREE_REPEAT_TRIGRAM_BP": round(statistics.mean(repeat3)),
        "FREE_REPEAT_8GRAM_BP": round(statistics.mean(pair[0] for pair in repeat8)),
        "FREE_REPEAT_8GRAM_PROBES": len(observed_onsets),
        "FREE_FIRST_REPEAT_8GRAM_MEAN": round(
            statistics.mean(observed_onsets)
        ) if observed_onsets else 0,
        "FREE_DISTINCT_TOKEN_BP": round(statistics.mean(
            len(set(seq)) * 10000 / len(seq) if seq else 0
            for seq in generated
        )),
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

    corrected = prior("PHASE03-SMOLTALK-V63-DIAGNOSTIC-PREFLIGHT-002")
    if (
        corrected.get("V63_DIAG_PREFLIGHT_PASS") != 1
        or corrected.get("V63_DIAG_BLIND_ACCESS") != 0
    ):
        raise RuntimeError("V63 corrected preflight 002 prerequisite invalid")
    reference = {
        "TF_TERM_TOP1": corrected["V63_DIAG_TF_TERMINAL_TOP1"],
        "TF_TERM_MARGIN_OK": corrected["V63_DIAG_TF_TERMINAL_MARGIN_OK"],
        "TF_INTER_TOP1": corrected["V63_DIAG_TF_INTERMEDIATE_TOP1"],
        "TF_INTER_MARGIN_OK": corrected["V63_DIAG_TF_INTERMEDIATE_MARGIN_OK"],
        "TF_NONTERM_EOS_TOP1": corrected["V63_DIAG_TF_NONTERMINAL_TOP1"],
    }
    for key, value in reference.items():
        if tf[key] != value:
            raise RuntimeError(f"V63 reference mismatch in {key}")
    if rollout["FREE_EOS_COMPLETIONS"] != corrected["V63_DIAG_FREE_EOS_COMPLETIONS"]:
        raise RuntimeError("Greedy EOS completion disagrees with frozen V63 preflight")
    if rollout["FREE_REPEAT_TRIGRAM_BP"] != corrected["V63_DIAG_FREE_REPEAT_TOKEN_TRIGRAM_BP"]:
        raise RuntimeError("Greedy trigram recurrence disagrees with frozen V63 preflight")

    output = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V63_FAIL_PASS": 1,
        "V63_FAIL_BLIND_ACCESS": 0,
        "V63_FAIL_GPU_BF16": 1,
        "V63_FAIL_GPU_BATCH": BATCH,
        "V63_FAIL_GPU_PEAK_MIB": peak_mib,
    }
    output.update({f"V63_FAIL_{key}": value for key, value in tf.items()})
    output.update({f"V63_FAIL_{key}": value for key, value in rollout.items()})
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
