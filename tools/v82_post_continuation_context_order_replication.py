#!/usr/bin/env python3
"""V82 post-continuation context-order replication control.

Replays the exact frozen V80 cycle-2 diagnostic, then evaluates the V81 final
checkpoint in the same frozen cycle-2 diagnostic coordinate.

No training, BLIND access, generation, checkpoint write, raw token text,
per-position publication or hidden-state persistence is permitted.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mini_kuzai import phase03_v62_trainer as T

STEP_ID = "PHASE03-SMOLTALK-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001"

RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
CYCLE2 = RUN / "checkpoint-cycle-02.pt"
FINAL = RUN / "checkpoint-last.pt"
BEST = RUN / "checkpoint-best.pt"

V80_SOURCE = ROOT / "tools" / "v80_decision_boundary_proximity_control.py"
V81_FINAL_REPORT = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V81-FINAL-CLOSURE-001.json"
)
V82_START_RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V82-start.json"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001.md"
)

VAL_LEXICAL = 9170
SAME_PATH_BATCH = 32
GPU_PEAK_LIMIT_MIB = 6144
FINAL_STEPS = 136
FINAL_EXPOSURE = 1181302
NANO_SCALE = 1_000_000_000
ALPHA_NANO_LIMIT = 2_000_000_000
PUBLIC_METRIC_MAX = 100_000_000

METRIC_FIELDS = (
    "SEMANTIC_VALIDATION_COMPLETE",
    "TRAINING_AUTHORIZED",
    "TRAINING_STARTED",
    "V82_PASS",
    "V82_BLIND_ACCESS",
    "V82_VAL_LEXICAL",
    "V82_SAME_PATH_BATCH",
    "V82_BASELINE_REPLAY_PASS",
    "V82_BASELINE_PRED_CHANGED",
    "V82_BASELINE_SIGN_CHANGED",
    "V82_FINAL_STEPS",
    "V82_FINAL_EXPOSURE",
    "V82_FINAL_ORIGINAL_CORRECT",
    "V82_FINAL_REVERSE_CORRECT",
    "V82_FINAL_PRED_AGREE",
    "V82_FINAL_PRED_CHANGED",
    "V82_FINAL_SIGN_AGREE",
    "V82_FINAL_SIGN_CHANGED",
    "V82_FINAL_ALPHA_CORR_ABS_BP",
    "V82_FINAL_PERTURBED_PREFIXES",
    "V82_FINAL_UNCHANGED_PREFIXES",
    "V82_FINAL_CHANGED_WITHIN_1E3",
    "V82_FINAL_SIGN_WITHIN_1E3",
    "V82_FINAL_BOUNDARY_MAX_NANO_CHANGED",
    "V82_FINAL_BOUNDARY_MEAN_NANO_CHANGED",
    "V82_FINAL_CROSSING_MAX_NANO_CHANGED",
    "V82_FINAL_CROSSING_MEAN_NANO_CHANGED",
    "V82_FINAL_INPUT_INVARIANTS",
    "V82_COVERAGE_BP",
    "V82_GPU_PEAK_MIB",
)


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"V82 reviewed JSON missing or unsafe: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"V82 expected JSON object: {path}")
    return value


def imported(name: str, source: Path):
    if source.is_symlink() or not source.is_file():
        raise RuntimeError("V82 reviewed dependency unavailable or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V82 dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("V82 checkpoint missing or unsafe")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def verify_start_receipt() -> dict:
    receipt = read_json(V82_START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V82"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/14"
        and receipt.get("source_commit")
        == "fbb88b5316ae7139a2c078eda831f5526537fed4"
    ):
        raise RuntimeError("V82 official START receipt absent or invalid")
    return receipt


def verify_v81_closure() -> dict:
    report = read_json(V81_FINAL_REPORT)
    metrics = report.get("metrics")
    if not (
        report.get("step_id") == "PHASE03-SMOLTALK-V81-FINAL-CLOSURE-001"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and metrics.get("V81_FINAL_PASS") == 1
        and metrics.get("V81_FINAL_BLIND_ACCESS") == 0
        and metrics.get("V81_FINAL_WINDOW_CLOSED") == 1
        and metrics.get("V81_FINAL_FURTHER_TRAINING_AUTHORIZED") == 0
        and metrics.get("V81_FINAL_STEPS") == FINAL_STEPS
        and metrics.get("V81_FINAL_EXPOSURE") == FINAL_EXPOSURE
        and metrics.get("V81_FINAL_CHECKPOINT_CYCLE2") == 1
        and metrics.get("V81_FINAL_CHECKPOINT_LAST") == 1
        and metrics.get("V81_FINAL_CHECKPOINT_BEST") == 1
    ):
        raise RuntimeError("V82 V81 closure integrity gate failed")
    return metrics


def verify_checkpoint_state(
    path: Path,
    *,
    expected_step: int,
    expected_exposure: int,
    runtime: dict,
) -> dict:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("V82 checkpoint missing or unsafe")
    state = torch.load(path, map_location="cpu", weights_only=False)
    if not (
        isinstance(state, dict)
        and state.get("schema_version") == "v62-margin-checkpoint-1"
        and state.get("authorization_freeze_fingerprint")
        == runtime["authorization"]["freeze_fingerprint"]
        and state.get("trainer_freeze_fingerprint")
        == runtime["trainer_freeze"]["trainer_freeze_fingerprint"]
        and state.get("step") == expected_step
        and state.get("exposure_tokens") == expected_exposure
        and isinstance(state.get("model"), dict)
    ):
        raise RuntimeError("V82 checkpoint identity mismatch")
    return state


def finalize_boundary_stats_allow_zero(V80, stats: dict, expected: int) -> dict:
    if stats.get("COUNT") != expected:
        raise RuntimeError("V82 boundary coverage failed")
    changed = stats.get("CHANGED_COUNT")
    sign_changed = stats.get("SIGN_CHANGED_COUNT")
    if (
        type(changed) is not int
        or type(sign_changed) is not int
        or not 0 <= changed <= expected
        or not 0 <= sign_changed <= expected
    ):
        raise RuntimeError("V82 changed-set accounting failed")

    labels = ("1E7", "1E6", "1E5", "1E4", "1E3")
    for prefix, total in (
        ("ALL", expected),
        ("CHANGED", changed),
        ("SIGN", sign_changed),
    ):
        values = [stats[f"{prefix}_WITHIN_{label}"] for label in labels]
        if not (
            all(type(v) is int and 0 <= v <= total for v in values)
            and values == sorted(values)
        ):
            raise RuntimeError("V82 cumulative threshold accounting failed")

    floats = (
        stats["BOUNDARY_SUM_CHANGED"],
        stats["BOUNDARY_MAX_CHANGED"],
        stats["CROSSING_SUM_CHANGED"],
        stats["CROSSING_MAX_CHANGED"],
    )
    if not all(math.isfinite(v) and v >= 0.0 for v in floats):
        raise RuntimeError("V82 nonfinite boundary statistic")

    if changed == 0:
        boundary_max = boundary_mean = crossing_max = crossing_mean = 0
    else:
        boundary_max = round(stats["BOUNDARY_MAX_CHANGED"] * NANO_SCALE)
        boundary_mean = round(
            stats["BOUNDARY_SUM_CHANGED"] * NANO_SCALE / changed
        )
        crossing_max = round(stats["CROSSING_MAX_CHANGED"] * NANO_SCALE)
        crossing_mean = round(
            stats["CROSSING_SUM_CHANGED"] * NANO_SCALE / changed
        )

    if not all(
        0 <= value <= ALPHA_NANO_LIMIT
        for value in (
            boundary_max,
            boundary_mean,
            crossing_max,
            crossing_mean,
        )
    ):
        raise RuntimeError("V82 nano-scaled boundary statistic outside range")

    result = {
        key: value
        for key, value in stats.items()
        if (
            key.startswith("ALL_WITHIN_")
            or key.startswith("CHANGED_WITHIN_")
            or key.startswith("SIGN_WITHIN_")
        )
    }
    result.update(
        {
            "BOUNDARY_MAX_NANO_CHANGED": boundary_max,
            "BOUNDARY_MEAN_NANO_CHANGED": boundary_mean,
            "CROSSING_MAX_NANO_CHANGED": crossing_max,
            "CROSSING_MEAN_NANO_CHANGED": crossing_mean,
        }
    )
    return result


def score_validation(
    V80,
    V79,
    V77,
    model,
    device,
    validation: list,
    train_mean: torch.Tensor,
    train_pc1: torch.Tensor,
    residual_profile: torch.Tensor,
    unigram: int,
):
    if len(validation) != 36:
        raise RuntimeError("V82 frozen VALIDATION segment count changed")
    if not (
        train_mean.shape == train_pc1.shape == (V80.MODEL_DIM,)
        and residual_profile.shape == (V80.VOCAB,)
        and torch.isfinite(residual_profile).all()
        and 3 <= unigram < V80.VOCAB
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr()
        == model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V82 scoring geometry/output-head gate failed")

    mean_t = train_mean.to(device=device, dtype=torch.float32)
    pc1_t = train_pc1.to(device=device, dtype=torch.float32)
    residual_t = residual_profile.to(device=device, dtype=torch.float32)

    prefixes = []
    gold_values = []
    for seg in validation:
        tokens = tuple(seg.token_ids)
        if (
            not tokens
            or tokens[0] != T.BOS_ID
            or tokens[-1] != T.EOS_ID
        ):
            raise RuntimeError("V82 VALIDATION boundary changed")
        for target_index in range(1, len(tokens)):
            target = tokens[target_index]
            if not 3 <= target < V80.VOCAB:
                continue
            prefixes.append(tokens[:target_index])
            gold_values.append(target)

    if len(prefixes) != VAL_LEXICAL or len(gold_values) != VAL_LEXICAL:
        raise RuntimeError("V82 validation lexical coverage mismatch")

    outcomes = {
        "ORIGINAL": V77.empty_outcome(),
        "REVERSE": V77.empty_outcome(),
    }
    pairs = V79.empty_pair_stats()
    boundary_stats = V80.empty_boundary_stats()
    taps = []

    def capture(_module, inputs):
        if (
            len(inputs) != 1
            or inputs[0].ndim != 3
            or inputs[0].shape[-1] != V80.MODEL_DIM
        ):
            raise RuntimeError("V82 output-head hidden state shape changed")
        taps.append(inputs[0].detach())

    handle = model.lm_head.register_forward_pre_hook(capture)
    model.eval()
    try:
        with torch.inference_mode():
            for offset in range(0, VAL_LEXICAL, SAME_PATH_BATCH):
                stop = min(offset + SAME_PATH_BATCH, VAL_LEXICAL)
                original = prefixes[offset:stop]
                transformed = [
                    V77.reverse_history_keep_last(prefix)
                    for prefix in original
                ]
                changed_prefix = torch.as_tensor(
                    [a != b for a, b in zip(original, transformed)],
                    dtype=torch.bool,
                )
                invariants = V79.pair_invariant_count(
                    original,
                    transformed,
                )
                if invariants != len(original):
                    raise RuntimeError("V82 input invariant failed")

                alpha_original = V79.score_prefix_batch(
                    V77,
                    model,
                    device,
                    original,
                    mean_t,
                    pc1_t,
                    taps,
                )
                alpha_reverse = V79.score_prefix_batch(
                    V77,
                    model,
                    device,
                    transformed,
                    mean_t,
                    pc1_t,
                    taps,
                )
                gold = torch.as_tensor(
                    gold_values[offset:stop],
                    dtype=torch.long,
                    device=device,
                )
                logits_original = (
                    alpha_original.unsqueeze(1) * residual_t.unsqueeze(0)
                )
                logits_reverse = (
                    alpha_reverse.unsqueeze(1) * residual_t.unsqueeze(0)
                )
                if not (
                    torch.isfinite(logits_original).all()
                    and torch.isfinite(logits_reverse).all()
                ):
                    raise RuntimeError("V82 nonfinite residual logits")

                pred_original = logits_original.argmax(dim=1)
                pred_reverse = logits_reverse.argmax(dim=1)

                V77.update_outcome(
                    outcomes["ORIGINAL"],
                    pred_original,
                    gold,
                    unigram,
                )
                V77.update_outcome(
                    outcomes["REVERSE"],
                    pred_reverse,
                    gold,
                    unigram,
                )
                V79.update_pair_stats(
                    pairs,
                    alpha_original,
                    alpha_reverse,
                    pred_original,
                    pred_reverse,
                    gold,
                    changed_prefix,
                    invariants,
                )
                V80.update_boundary_stats(
                    boundary_stats,
                    alpha_original,
                    alpha_reverse,
                    pred_original,
                    pred_reverse,
                )

                del (
                    alpha_original,
                    alpha_reverse,
                    gold,
                    logits_original,
                    logits_reverse,
                    pred_original,
                    pred_reverse,
                )
    finally:
        handle.remove()
        taps.clear()

    return (
        {
            mode: V77.finalize_outcome(value, VAL_LEXICAL)
            for mode, value in outcomes.items()
        },
        V79.finalize_pair_stats(pairs, VAL_LEXICAL),
        finalize_boundary_stats_allow_zero(
            V80,
            boundary_stats,
            VAL_LEXICAL,
        ),
    )


def prepare_frozen_coordinate(V80):
    V80.verify_dependency_blobs()
    V80.verify_start_receipt()
    V80.verify_v79_report()

    V79 = V80.imported("v82_frozen_v79_control", V80.V79_SOURCE)
    V79.verify_dependency_blobs()
    V79.verify_start_receipt()
    V79.verify_v77_report()
    V79.verify_v78_report()

    V77 = V79.imported("v82_frozen_v77_control", V79.V77_SOURCE)
    V78 = V79.imported("v82_frozen_v78_control", V79.V78_SOURCE)
    V77.verify_dependency_blobs()
    v76_metrics = V77.verify_v76_report()

    v76 = V77.imported("v82_frozen_v76_control", V77.V76_SOURCE)
    v75 = V77.imported("v82_frozen_v75_geometry", V77.V75_SOURCE)
    v65 = V77.imported("v82_frozen_v65_frequency", V77.V65_SOURCE)
    v64 = v75.imported("v82_frozen_v64_preflight", v75.V64)

    model, device, streams, validation = v64.preflight()
    if device.type != "cuda":
        raise RuntimeError("V82 requires reviewed CUDA inference path")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("V82 requires CUDA BF16 support")
    if not (
        V80.SAME_PATH_BATCH == SAME_PATH_BATCH
        and V79.SAME_PATH_BATCH == SAME_PATH_BATCH
        and V78.PATH_B_BATCH == SAME_PATH_BATCH
    ):
        raise RuntimeError("V82 inherited runtime constants changed")

    frequency = v65.count_training_tokens(streams)
    v76.frequency_count_vector(frequency, require_frozen=True)
    unigram = v75.most_frequent(frequency)
    if v76_metrics["V76_UNIGRAM_CORRECT"] != 2535:
        raise RuntimeError("V82 frozen unigram provenance changed")

    train_segments = v75._segments_in_order(streams)
    count, mean, m2 = v75.collect_geometry(
        model,
        device,
        train_segments,
        v76.TRAIN_LEXICAL,
        v75.TRAIN_BATCH,
    )
    train_mean, train_pc1, train_share = v75.finalize_geometry(
        count,
        mean,
        m2,
        expected_count=v76.TRAIN_LEXICAL,
    )
    if train_share != 9019:
        raise RuntimeError("V82 frozen TRAIN PC1 variance replay failed")

    profiles = v76.decompose_output_profile(
        model.lm_head.weight,
        train_pc1,
        frequency,
        require_frozen=True,
    )
    if not (
        round(profiles["CORR_ABS"] * 10000) == 2785
        and round(profiles["R2"] * 10000) == 775
        and round(profiles["RESIDUAL_ENERGY"] * 10000) == 9225
    ):
        raise RuntimeError("V82 frozen V76 residual decomposition replay failed")

    return (
        V79,
        V77,
        model,
        device,
        validation,
        train_mean,
        train_pc1,
        profiles["RESIDUAL"],
        unigram,
    )


def build_metrics(
    baseline: dict,
    outcomes: dict,
    pairs: dict,
    boundary: dict,
    peak_mib: int,
) -> dict:
    original = outcomes["ORIGINAL"]
    reverse = outcomes["REVERSE"]

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V82_PASS": 1,
        "V82_BLIND_ACCESS": 0,
        "V82_VAL_LEXICAL": VAL_LEXICAL,
        "V82_SAME_PATH_BATCH": SAME_PATH_BATCH,
        "V82_BASELINE_REPLAY_PASS": 1,
        "V82_BASELINE_PRED_CHANGED":
            baseline["V80_V79_PRED_CHANGED_REPLAY"],
        "V82_BASELINE_SIGN_CHANGED":
            baseline["V80_V79_SIGN_CHANGED_REPLAY"],
        "V82_FINAL_STEPS": FINAL_STEPS,
        "V82_FINAL_EXPOSURE": FINAL_EXPOSURE,
        "V82_FINAL_ORIGINAL_CORRECT": original["CORRECT"],
        "V82_FINAL_REVERSE_CORRECT": reverse["CORRECT"],
        "V82_FINAL_PRED_AGREE": pairs["PRED_AGREE"],
        "V82_FINAL_PRED_CHANGED": pairs["PRED_CHANGED"],
        "V82_FINAL_SIGN_AGREE": pairs["SIGN_AGREE"],
        "V82_FINAL_SIGN_CHANGED": pairs["SIGN_CHANGED"],
        "V82_FINAL_ALPHA_CORR_ABS_BP": pairs["ALPHA_CORR_ABS_BP"],
        "V82_FINAL_PERTURBED_PREFIXES": pairs["PERTURBED_PREFIXES"],
        "V82_FINAL_UNCHANGED_PREFIXES": pairs["UNCHANGED_PREFIXES"],
        "V82_FINAL_CHANGED_WITHIN_1E3": boundary["CHANGED_WITHIN_1E3"],
        "V82_FINAL_SIGN_WITHIN_1E3": boundary["SIGN_WITHIN_1E3"],
        "V82_FINAL_BOUNDARY_MAX_NANO_CHANGED":
            boundary["BOUNDARY_MAX_NANO_CHANGED"],
        "V82_FINAL_BOUNDARY_MEAN_NANO_CHANGED":
            boundary["BOUNDARY_MEAN_NANO_CHANGED"],
        "V82_FINAL_CROSSING_MAX_NANO_CHANGED":
            boundary["CROSSING_MAX_NANO_CHANGED"],
        "V82_FINAL_CROSSING_MEAN_NANO_CHANGED":
            boundary["CROSSING_MEAN_NANO_CHANGED"],
        "V82_FINAL_INPUT_INVARIANTS": pairs["INPUT_INVARIANTS"],
        "V82_COVERAGE_BP": 10000,
        "V82_GPU_PEAK_MIB": peak_mib,
    }

    nano_keys = {
        "V82_FINAL_BOUNDARY_MAX_NANO_CHANGED",
        "V82_FINAL_BOUNDARY_MEAN_NANO_CHANGED",
        "V82_FINAL_CROSSING_MAX_NANO_CHANGED",
        "V82_FINAL_CROSSING_MEAN_NANO_CHANGED",
    }
    if not (
        tuple(metrics) == METRIC_FIELDS
        and len(metrics) == 30
        and all(
            type(value) is int
            and 0 <= value <= (
                ALPHA_NANO_LIMIT if key in nano_keys else PUBLIC_METRIC_MAX
            )
            for key, value in metrics.items()
        )
        and pairs["INPUT_INVARIANTS"] == VAL_LEXICAL
        and pairs["PERTURBED_PREFIXES"] == V80_PERTURBED
        and pairs["UNCHANGED_PREFIXES"] == V80_UNCHANGED
    ):
        raise RuntimeError("V82 strict public metric schema failed")
    return metrics


V80_PERTURBED = 9062
V80_UNCHANGED = 108


def compute():
    torch.set_grad_enabled(False)
    verify_start_receipt()
    verify_v81_closure()

    if RUN.is_symlink() or not RUN.is_dir():
        raise RuntimeError("V82 run directory missing or unsafe")
    if (RUN / ".training.lock").exists():
        raise RuntimeError("V82 training lock present")
    for path in (CYCLE2, FINAL, BEST, PROTOCOL):
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("V82 required dependency missing or unsafe")

    cycle2_sha = file_sha256(CYCLE2)
    final_sha = file_sha256(FINAL)
    if cycle2_sha == final_sha:
        raise RuntimeError("V82 baseline and final checkpoint fingerprints match")

    V80 = imported("v82_frozen_v80_control", V80_SOURCE)

    (
        V79,
        V77,
        model,
        device,
        validation,
        train_mean,
        train_pc1,
        residual_profile,
        unigram,
    ) = prepare_frozen_coordinate(V80)

    torch.cuda.reset_peak_memory_stats(device)

    baseline_outcomes, baseline_pairs, baseline_boundary = V80.score_validation(
        V79,
        V77,
        model,
        device,
        validation,
        train_mean,
        train_pc1,
        residual_profile,
        unigram,
    )
    baseline = V80.build_metrics(
        baseline_outcomes,
        baseline_pairs,
        baseline_boundary,
    )
    if not (
        baseline["V80_V79_PRED_CHANGED_REPLAY"] == 5
        and baseline["V80_V79_SIGN_CHANGED_REPLAY"] == 5
        and baseline["V80_V79_ORIGINAL_CORRECT_REPLAY"] == 2594
        and baseline["V80_V79_REVERSE_CORRECT_REPLAY"] == 2594
        and baseline["V80_CHANGED_WITHIN_1E3"] == 0
        and baseline["V80_BOUNDARY_MEAN_NANO_CHANGED"] == 30173315
        and baseline["V80_BOUNDARY_MAX_NANO_CHANGED"] == 59604287
        and baseline["V80_CROSSING_MEAN_NANO_CHANGED"] == 150983569
        and baseline["V80_CROSSING_MAX_NANO_CHANGED"] == 249839202
    ):
        raise RuntimeError("V82 exact V80 baseline replay failed")

    runtime = T.verify_runtime(
        ROOT / "mini_kuzai" / "phase03_v62_trainer.py",
        ROOT / "tools" / "train_v62_margin.py",
    )
    final_state = verify_checkpoint_state(
        FINAL,
        expected_step=FINAL_STEPS,
        expected_exposure=FINAL_EXPOSURE,
        runtime=runtime,
    )
    model.load_state_dict(final_state["model"], strict=True)
    model.eval()
    del final_state

    outcomes, pairs, boundary = score_validation(
        V80,
        V79,
        V77,
        model,
        device,
        validation,
        train_mean,
        train_pc1,
        residual_profile,
        unigram,
    )

    peak_mib = math.ceil(
        torch.cuda.max_memory_allocated(device) / (1024 * 1024)
    )
    if peak_mib > GPU_PEAK_LIMIT_MIB:
        raise RuntimeError("V82 GPU peak-memory gate exceeded")

    metrics = build_metrics(
        baseline,
        outcomes,
        pairs,
        boundary,
        peak_mib,
    )
    return metrics, cycle2_sha, final_sha


def main():
    metrics, cycle2_sha, final_sha = compute()
    print(f"V82_CYCLE2_SHA256={cycle2_sha}")
    print(f"V82_FINAL_SHA256={final_sha}")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
