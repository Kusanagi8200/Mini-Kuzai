#!/usr/bin/env python3
"""V63 decoding ablation: four frozen-checkpoint GPU decoding strategies.

Read-only model inference on the same six frozen VALIDATION prompts.
Numeric-only GOGIT publication. BLIND TEST stays closed.
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

RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
CHECKPOINT = RUN / "checkpoint-cycle-02.pt"
PREVIOUS = "PHASE03-SMOLTALK-V63-GENERATION-FAILURE-ANALYSIS-001"
REFERENCE = "PHASE03-SMOLTALK-V63-DIAGNOSTIC-PREFLIGHT-002"
MAX_NEW = 96
SEED = 6301
TEMPERATURE = 0.8
TOP_K = 40
TOP_P = 0.9
REPETITION_PENALTY = 1.2
MODES = ("GREEDY", "TEMP", "TOPP", "REP")


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise RuntimeError(f"JSON is not an object: {path}")
    return result


def previous_metrics(step: str) -> dict:
    record = read_json(
        REPO / "reports" / "assistant-results" / "history" / f"{step}.json"
    )
    if record.get("step_id") != step or record.get("semantic_validation_complete") is not True:
        raise RuntimeError(f"Missing validated GOGIT history: {step}")
    metrics = record.get("metrics")
    if not isinstance(metrics, dict):
        raise RuntimeError("Invalid historical metrics")
    return metrics


def load_gpu_validation():
    summary = read_json(RUN / "RUN-SUMMARY.json")
    manifest = read_json(RUN / "RUN-MANIFEST.json")
    if (
        summary.get("schema_version") != "v62-margin-run-summary-1"
        or manifest.get("schema_version") != "v62-margin-run-1"
        or summary.get("status") != manifest.get("status")
        or summary.get("status") != "STOPPED"
        or summary.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED"
        or summary.get("optimizer_steps") != 69
        or summary.get("exposure_tokens") != 597982
        or summary.get("blind_test_accessed") is not False
        or manifest.get("blind_test_during_training") is not False
        or manifest.get("resume") is not False
    ):
        raise RuntimeError("V62 cycle-2 checkpoint state does not match frozen protocol")
    if (RUN / ".training.lock").exists():
        raise RuntimeError("Training lock exists; diagnostic refused")
    if not CHECKPOINT.is_file() or CHECKPOINT.is_symlink():
        raise RuntimeError("V62 cycle-2 checkpoint is absent or unsafe")
    previous = previous_metrics(PREVIOUS)
    corrected = previous_metrics(REFERENCE)
    if (
        previous.get("V63_FAIL_PASS") != 1
        or previous.get("V63_FAIL_BLIND_ACCESS") != 0
        or previous.get("V63_FAIL_FREE_PROBES") != 6
        or corrected.get("V63_DIAG_TF_TERMINAL_TOP1") != 14
        or corrected.get("V63_DIAG_BLIND_ACCESS") != 0
    ):
        raise RuntimeError("Previous V63 reference results are missing or invalid")
    runtime = T.verify_runtime(
        REPO / "mini_kuzai" / "phase03_v62_trainer.py",
        REPO / "tools" / "train_v62_margin.py",
    )
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError("CUDA and BF16 are required")
    state = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    if (
        state.get("schema_version") != "v62-margin-checkpoint-1"
        or state.get("step") != 69
        or state.get("exposure_tokens") != 597982
        or state.get("authorization_freeze_fingerprint")
           != runtime["authorization"]["freeze_fingerprint"]
        or state.get("trainer_freeze_fingerprint")
           != runtime["trainer_freeze"]["trainer_freeze_fingerprint"]
    ):
        raise RuntimeError("Frozen V62 checkpoint identity mismatch")
    device = torch.device("cuda")
    model = T.MODEL.MiniKuzaiPhase03V60(T.MODEL.Phase03Config()).to(device)
    model.load_state_dict(state["model"], strict=True)
    del state
    model.eval()
    tokenizer = T.load_tokenizer()
    validation, inventory = T.build_validation_segments()
    if inventory.get("records") != 36:
        raise RuntimeError("VALIDATION inventory differs from freeze")
    fixed = T._fixed_probe_segments(validation)
    if len(fixed) != 6:
        raise RuntimeError("Expected six frozen validation prompts")
    marker = "\n\nMINI-KUZAI:\n"
    prompts = []
    for item in fixed:
        serial = tokenizer.decode(item.token_ids)
        at = serial.find(marker)
        if at < 0:
            raise RuntimeError("Frozen validation prompt separator missing")
        prompt = tokenizer.encode(
            serial[:at + len(marker)], add_bos=True, add_eos=False
        )
        if len(prompt) + MAX_NEW >= T.CONTEXT_LENGTH:
            raise RuntimeError("Prompt would exceed context")
        prompts.append(prompt)
    return model, device, prompts, previous


def pad_right(sequences: list[list[int]], device: torch.device):
    if not sequences or max(map(len, sequences)) > T.CONTEXT_LENGTH:
        raise RuntimeError("Invalid GPU input length")
    batch = torch.full(
        (len(sequences), max(map(len, sequences))),
        T.PAD_ID, dtype=torch.long, device=device
    )
    for row, seq in enumerate(sequences):
        batch[row, :len(seq)] = torch.as_tensor(seq, device=device, dtype=torch.long)
    return batch


def decode_logits(
    logits: torch.Tensor,
    mode: str,
    generated: list[list[int]],
    active: list[int],
    generator: torch.Generator,
):
    if mode == "GREEDY":
        return torch.argmax(logits, dim=-1)
    if mode == "REP":
        adjusted = logits.clone()
        for row, index in enumerate(active):
            ids = set(generated[index])
            ids.discard(T.EOS_ID)
            ids.discard(T.PAD_ID)
            ids.discard(T.BOS_ID)
            if ids:
                ix = torch.as_tensor(sorted(ids), device=logits.device, dtype=torch.long)
                values = adjusted[row, ix]
                adjusted[row, ix] = torch.where(
                    values >= 0, values / REPETITION_PENALTY,
                    values * REPETITION_PENALTY
                )
        return adjusted.argmax(dim=-1)
    scaled = logits / TEMPERATURE
    if mode == "TEMP":
        p = torch.softmax(scaled, dim=-1)
        return torch.multinomial(p, num_samples=1, generator=generator)[:, 0]
    if mode == "TOPP":
        scores, token_ids = torch.topk(scaled, k=TOP_K, dim=-1)
        candidates = torch.softmax(scores, dim=-1)
        keep = candidates.cumsum(dim=-1) - candidates < TOP_P
        keep[:, 0] = True
        scores = scores.masked_fill(~keep, -torch.inf)
        p = torch.softmax(scores, dim=-1)
        selected = torch.multinomial(
            p, num_samples=1, generator=generator
        )
        return token_ids.gather(1, selected)[:, 0]
    raise RuntimeError("Unknown diagnostic decoder")


def repetition_bp(seq: list[int], width: int) -> int:
    seq = [t for t in seq if t != T.EOS_ID]
    grams = [tuple(seq[i:i + width]) for i in range(max(0, len(seq) - width + 1))]
    if not grams:
        return 0
    return round((len(grams) - len(set(grams))) * 10000 / len(grams))


def run_mode(
    model, device: torch.device, prompts: list[list[int]], mode: str
) -> dict:
    full = [list(prompt) for prompt in prompts]
    origin = [len(p) for p in prompts]
    generated = [[] for _ in full]
    done = [False for _ in full]
    rng = torch.Generator(device="cuda")
    rng.manual_seed(SEED)
    with torch.inference_mode():
        for _ in range(MAX_NEW):
            active = [i for i, complete in enumerate(done) if not complete]
            if not active:
                break
            batch = pad_right([full[i] for i in active], device)
            tails = torch.as_tensor(
                [len(full[i]) - 1 for i in active],
                device=device, dtype=torch.long
            )
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits = model(batch)[
                    torch.arange(len(active), device=device), tails
                ].float()
            chosen = decode_logits(logits, mode, generated, active, rng)
            for row, index in enumerate(active):
                token = int(chosen[row].item())
                full[index].append(token)
                generated[index].append(token)
                if token == T.EOS_ID:
                    done[index] = True
    if len(generated) != 6 or any(not (0 < len(s) <= MAX_NEW) for s in generated):
        raise RuntimeError("Invalid bounded GPU decoding result")
    return {
        "EOS": sum(done),
        "REPEAT3_BP": round(statistics.mean(repetition_bp(s, 3) for s in generated)),
        "REPEAT8_BP": round(statistics.mean(repetition_bp(s, 8) for s in generated)),
        "DISTINCT_BP": round(statistics.mean(
            len(set(s)) * 10000 / len(s) for s in generated
        )),
        "MEAN_TOKENS_X100": round(
            sum(map(len, generated)) * 100 / len(generated)
        ),
    }


def main():
    model, device, prompts, previous = load_gpu_validation()
    torch.cuda.reset_peak_memory_stats(device)
    results = {mode: run_mode(model, device, prompts, mode) for mode in MODES}
    # Greedy must reproduce the frozen six-prompt reference exactly.
    if (
        results["GREEDY"]["EOS"] != previous["V63_FAIL_FREE_EOS_COMPLETIONS"]
        or results["GREEDY"]["REPEAT3_BP"]
           != previous["V63_FAIL_FREE_REPEAT_TRIGRAM_BP"]
        or results["GREEDY"]["REPEAT8_BP"]
           != previous["V63_FAIL_FREE_REPEAT_8GRAM_BP"]
    ):
        raise RuntimeError("Greedy baseline differs from frozen V63 diagnostic")
    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V63_ABL_PASS": 1,
        "V63_ABL_BLIND_ACCESS": 0,
        "V63_ABL_GPU_BF16": 1,
        "V63_ABL_PROBES_PER_MODE": len(prompts),
        "V63_ABL_SEED": SEED,
        "V63_ABL_GPU_PEAK_MIB": math.ceil(
            torch.cuda.max_memory_allocated(device) / (1024 ** 2)
        ),
    }
    for mode in MODES:
        for key, value in results[mode].items():
            metrics[f"V63_ABL_{mode}_{key}"] = value
    if len(metrics) > 30:
        raise RuntimeError("GOGIT maximum metric count exceeded")
    if any(
        not isinstance(value, int) or not (0 <= value <= 100_000_000)
        for value in metrics.values()
    ):
        raise RuntimeError("Unsafe or non-numeric metric")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
