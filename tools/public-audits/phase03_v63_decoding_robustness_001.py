#!/usr/bin/env python3
"""V63 decoding robustness, CUDA/BF16, read-only frozen V62 checkpoint.

Eight deterministic seeds, six frozen VALIDATION prompts, two decoders.
All 96 trajectories are run in seed-batched CUDA forwards. The GOGIT
output contains only finite nonnegative integer aggregate measurements.
No training, no BLIND TEST, no public raw conversation outputs.
"""
from __future__ import annotations

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
HISTORY = REPO / "reports" / "assistant-results" / "history"
PREVIOUS = "PHASE03-SMOLTALK-V63-DECODING-ABLATION-001"
SEEDS = tuple(range(6301, 6309))
MODES = ("TEMP", "TOPP")
PROBES = 6
MAX_NEW = 96
TEMPERATURE = 0.8
TOP_K = 40
TOP_P = 0.9


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"Invalid JSON object: {path}")
    return data


def published_metrics(step: str) -> dict:
    report = read_json(HISTORY / f"{step}.json")
    if (
        report.get("step_id") != step
        or report.get("semantic_validation_complete") is not True
    ):
        raise RuntimeError("Missing validated preceding GOGIT history")
    metrics = report.get("metrics")
    if not isinstance(metrics, dict):
        raise RuntimeError("Missing historical metrics")
    return metrics


def read_model_and_prompts():
    summary = read_json(RUN / "RUN-SUMMARY.json")
    manifest = read_json(RUN / "RUN-MANIFEST.json")
    if (
        summary.get("schema_version") != "v62-margin-run-summary-1"
        or manifest.get("schema_version") != "v62-margin-run-1"
        or summary.get("status") != "STOPPED"
        or manifest.get("status") != "STOPPED"
        or summary.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED"
        or summary.get("optimizer_steps") != 69
        or summary.get("exposure_tokens") != 597982
        or summary.get("training_started") is not True
        or summary.get("blind_test_accessed") is not False
        or manifest.get("blind_test_during_training") is not False
        or manifest.get("resume") is not False
        or (RUN / ".training.lock").exists()
    ):
        raise RuntimeError("V62 mandatory cycle-2 stop verification failed")
    if not CHECKPOINT.is_file() or CHECKPOINT.is_symlink():
        raise RuntimeError("Missing or unsafe frozen V62 cycle-2 checkpoint")

    baseline = published_metrics(PREVIOUS)
    if (
        baseline.get("V63_ABL_PASS") != 1
        or baseline.get("V63_ABL_BLIND_ACCESS") != 0
        or baseline.get("V63_ABL_PROBES_PER_MODE") != PROBES
        or baseline.get("V63_ABL_SEED") != SEEDS[0]
    ):
        raise RuntimeError("V63 decoding ablation reference invalid")
    for step, key in (
        ("PHASE03-SMOLTALK-V63-GENERATION-FAILURE-ANALYSIS-001",
         "V63_FAIL_PASS"),
        ("PHASE03-SMOLTALK-V63-DIAGNOSTIC-PREFLIGHT-002",
         "V63_DIAG_PREFLIGHT_PASS"),
    ):
        if published_metrics(step).get(key) != 1:
            raise RuntimeError("Missing historical frozen V63 diagnostic")

    runtime = T.verify_runtime(
        REPO / "mini_kuzai" / "phase03_v62_trainer.py",
        REPO / "tools" / "train_v62_margin.py",
    )
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError("V63 robustness requires CUDA BF16")
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
        raise RuntimeError("V62 frozen checkpoint integrity failed")

    device = torch.device("cuda")
    model = T.MODEL.MiniKuzaiPhase03V60(T.MODEL.Phase03Config()).to(device)
    model.load_state_dict(state["model"], strict=True)
    del state
    model.eval()

    tokenizer = T.load_tokenizer()
    validation, inventory = T.build_validation_segments()
    if inventory.get("records") != 36:
        raise RuntimeError("Frozen VALIDATION inventory changed")
    fixed = T._fixed_probe_segments(validation)
    if len(fixed) != PROBES:
        raise RuntimeError("Frozen generation probe inventory changed")

    marker = "\n\nMINI-KUZAI:\n"
    prompts = []
    for segment in fixed:
        serialized = tokenizer.decode(segment.token_ids)
        at = serialized.find(marker)
        if at < 0:
            raise RuntimeError("Frozen probe assistant marker missing")
        prompt = tokenizer.encode(
            serialized[:at + len(marker)],
            add_bos=True,
            add_eos=False,
        )
        if len(prompt) + MAX_NEW >= T.CONTEXT_LENGTH:
            raise RuntimeError("Frozen probe would exceed model context")
        prompts.append(prompt)
    return model, tokenizer, device, prompts


def pad_right(sequences: list[list[int]], device: torch.device):
    if not sequences or max(map(len, sequences)) > T.CONTEXT_LENGTH:
        raise RuntimeError("Invalid model input sequence batch")
    batch = torch.full(
        (len(sequences), max(map(len, sequences))),
        T.PAD_ID,
        dtype=torch.long,
        device=device,
    )
    for row, seq in enumerate(sequences):
        batch[row, :len(seq)] = torch.as_tensor(
            seq, dtype=torch.long, device=device
        )
    return batch


def sample_logits(logits: torch.Tensor, mode: str, generator):
    if mode not in MODES:
        raise RuntimeError("Decoder is not in the frozen robustness modes")
    scaled = logits / TEMPERATURE
    if mode == "TEMP":
        probabilities = torch.softmax(scaled, dim=-1)
        return torch.multinomial(
            probabilities, num_samples=1, generator=generator
        )[:, 0]

    scores, ids = torch.topk(scaled, k=TOP_K, dim=-1)
    initial = torch.softmax(scores, dim=-1)
    keep = (initial.cumsum(dim=-1) - initial) < TOP_P
    keep[:, 0] = True
    restricted = torch.softmax(
        scores.masked_fill(~keep, -torch.inf), dim=-1
    )
    index = torch.multinomial(
        restricted, num_samples=1, generator=generator
    )
    return ids.gather(1, index)[:, 0]


def repeated_gram_bp(tokens: list[int], width: int) -> int:
    no_eos = [token for token in tokens if token != T.EOS_ID]
    count = len(no_eos) - width + 1
    if count <= 0:
        return 0
    gram_count = len({
        tuple(no_eos[i:i + width]) for i in range(count)
    })
    return round((count - gram_count) * 10000 / count)


def aggregate(generated: list[list[int]], tokenizer) -> dict:
    if len(generated) != len(SEEDS) * PROBES:
        raise RuntimeError("Unexpected number of seed/prompt trajectories")
    per_seed_eos = [
        sum(
            int(generated[s * PROBES + p][-1] == T.EOS_ID)
            for p in range(PROBES)
        )
        for s in range(len(SEEDS))
    ]
    invalid_utf8 = role_leak = 0
    for ids in generated:
        text, valid = T._decode_generated_probe_text(tokenizer, ids)
        invalid_utf8 += int(valid is not True)
        role_leak += int(
            "USER:\n" in text or "MINI-KUZAI:\n" in text
        )
    result = {
        "EOS": sum(per_seed_eos),
        "MIN_SEED_EOS": min(per_seed_eos),
        "MAX_SEED_EOS": max(per_seed_eos),
        "SHORT8": sum(len(ids) <= 8 for ids in generated),
        "SHORT16": sum(len(ids) <= 16 for ids in generated),
        "MEAN_LEN_X100": round(statistics.mean(
            len(ids) for ids in generated
        ) * 100),
        "REPEAT3_BP": round(statistics.mean(
            repeated_gram_bp(ids, 3) for ids in generated
        )),
        "REPEAT8_BP": round(statistics.mean(
            repeated_gram_bp(ids, 8) for ids in generated
        )),
        "DISTINCT_BP": round(statistics.mean(
            len(set(ids)) * 10000 / len(ids)
            for ids in generated
        )),
        "UTF8_INVALID": invalid_utf8,
        "ROLE_LEAK": role_leak,
    }
    if not (
        0 <= result["MIN_SEED_EOS"] <= result["MAX_SEED_EOS"] <= PROBES
        and 0 <= result["SHORT8"] <= result["SHORT16"] <= len(generated)
        and result["EOS"] <= len(generated)
    ):
        raise RuntimeError("Invalid robustness metrics")
    return result


def run_batched(model, tokenizer, device, prompts, mode):
    # One independent CUDA generator per seed. Each seed's six prompts
    # stay in the same order as the original single-seed ablation.
    full = [list(prompt) for _ in SEEDS for prompt in prompts]
    lengths = [len(prompt) for _ in SEEDS for prompt in prompts]
    done = [False] * len(full)
    rng = [
        torch.Generator(device="cuda").manual_seed(seed)
        for seed in SEEDS
    ]

    with torch.inference_mode():
        for _ in range(MAX_NEW):
            active = [i for i, finished in enumerate(done) if not finished]
            if not active:
                break
            padded = pad_right([full[i] for i in active], device)
            tails = torch.as_tensor(
                [len(full[i]) - 1 for i in active],
                dtype=torch.long, device=device,
            )
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits = model(padded)[
                    torch.arange(len(active), device=device), tails
                ].float()

            # Vectorize the model forward for all active seeds. Keep
            # independent per-seed RNG streams during token selection.
            sampled = [None] * len(active)
            for s in range(len(SEEDS)):
                positions = [
                    j for j, global_index in enumerate(active)
                    if global_index // PROBES == s
                ]
                if not positions:
                    continue
                chosen = sample_logits(
                    logits[positions], mode, rng[s]
                ).tolist()
                for position, token in zip(positions, chosen):
                    sampled[position] = int(token)
            if any(token is None for token in sampled):
                raise RuntimeError("GPU sampling left an active prompt unassigned")
            for j, global_index in enumerate(active):
                token = sampled[j]
                full[global_index].append(token)
                if token == T.EOS_ID:
                    done[global_index] = True

    generated = [
        full[i][lengths[i]:] for i in range(len(full))
    ]
    if any(not 0 < len(tokens) <= MAX_NEW for tokens in generated):
        raise RuntimeError("Unbounded or empty sampled trajectory")
    return aggregate(generated, tokenizer)


def main():
    model, tokenizer, device, prompts = read_model_and_prompts()
    torch.cuda.reset_peak_memory_stats(device)
    results = {
        mode: run_batched(model, tokenizer, device, prompts, mode)
        for mode in MODES
    }
    output = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V63_ROB_PASS": 1,
        "V63_ROB_BLIND_ACCESS": 0,
        "V63_ROB_SEEDS": len(SEEDS),
        "V63_ROB_GPU_BF16": 1,
        "V63_ROB_GPU_PEAK_MIB": math.ceil(
            torch.cuda.max_memory_allocated(device) / (1024 ** 2)
        ),
    }
    for mode in MODES:
        for key, number in results[mode].items():
            output[f"V63_ROB_{mode}_{key}"] = number

    if len(output) != 30:
        raise RuntimeError("GOGIT robustness output must have 30 metrics")
    if any(
        not isinstance(number, int) or not 0 <= number <= 100_000_000
        for number in output.values()
    ):
        raise RuntimeError("Invalid public metric value")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, number in sorted(output.items()):
        print(f"{key}: {number}")


if __name__ == "__main__":
    main()
