#!/usr/bin/env python3
"""V80 decision-boundary proximity control.

Replays the frozen V79 ORIGINAL_SAME_PATH / REVERSE_HISTORY_KEEP_LAST pair and
measures how close the five discrete changes are to the alpha=0 residual
decision boundary.

No training, BLIND access, generation, checkpoint write, raw token text,
per-position publication or hidden-state persistence is permitted.
"""
from __future__ import annotations

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

STEP_ID = "PHASE03-SMOLTALK-V80-DECISION-BOUNDARY-PROXIMITY-CONTROL-001"

SAME_PATH_BATCH = 32
SCORE_CHUNK = 512
GPU_PEAK_LIMIT_MIB = 6144
VAL_LEXICAL = 9170
MODEL_DIM = 128
VOCAB = 1024
PERTURBED_PREFIXES = 9062
UNCHANGED_PREFIXES = 108

THRESHOLDS = (1e-7, 1e-6, 1e-5, 1e-4, 1e-3)
NANO_SCALE = 1_000_000_000
PUBLIC_METRIC_MAX = 100_000_000
ALPHA_NANO_LIMIT = 2_000_000_000

V79_SOURCE = ROOT / "tools" / "v79_same_path_context_order_control.py"
V79_REPORT = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.json"
)
V80_START_RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V80-start.json"

DEPENDENCY_BLOBS = {
    "tools/v79_same_path_context_order_control.py":
        "ec3a8702e53789a10486fdcc85dd384b3a89150f",
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.json":
        "d5116977adbad6c3c6eefeff212b97e486a8a15a",
    "automation/dev-flow/receipts/V80-start.json":
        "67214caa28758e132d8030687a42034706d2af04",
}

METRIC_FIELDS = (
    "SEMANTIC_VALIDATION_COMPLETE",
    "TRAINING_AUTHORIZED",
    "TRAINING_STARTED",
    "V80_PASS",
    "V80_BLIND_ACCESS",
    "V80_VAL_LEXICAL",
    "V80_SAME_PATH_BATCH",
    "V80_PERTURBED_PREFIXES",
    "V80_UNCHANGED_PREFIXES",
    "V80_V79_PRED_CHANGED_REPLAY",
    "V80_V79_SIGN_CHANGED_REPLAY",
    "V80_V79_ORIGINAL_CORRECT_REPLAY",
    "V80_V79_REVERSE_CORRECT_REPLAY",
    "V80_ALL_WITHIN_1E7",
    "V80_ALL_WITHIN_1E6",
    "V80_ALL_WITHIN_1E5",
    "V80_ALL_WITHIN_1E4",
    "V80_ALL_WITHIN_1E3",
    "V80_CHANGED_WITHIN_1E7",
    "V80_CHANGED_WITHIN_1E6",
    "V80_CHANGED_WITHIN_1E5",
    "V80_CHANGED_WITHIN_1E4",
    "V80_CHANGED_WITHIN_1E3",
    "V80_SIGN_WITHIN_1E7",
    "V80_SIGN_WITHIN_1E6",
    "V80_SIGN_WITHIN_1E5",
    "V80_BOUNDARY_MAX_NANO_CHANGED",
    "V80_BOUNDARY_MEAN_NANO_CHANGED",
    "V80_CROSSING_MAX_NANO_CHANGED",
    "V80_CROSSING_MEAN_NANO_CHANGED",
)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V80 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V80 expected JSON object")
    return value


def imported(name: str, source: Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("V80 reviewed dependency unavailable or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V80 dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_blob(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V80 pinned source missing or unsafe")
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError("V80 Git blob calculation failed")
    return proc.stdout.strip()


def verify_dependency_blobs() -> None:
    for relative, expected in DEPENDENCY_BLOBS.items():
        if git_blob(ROOT / relative) != expected:
            raise RuntimeError("V80 frozen dependency blob mismatch")


def verify_start_receipt() -> None:
    receipt = read_json(V80_START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V80"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/11"
        and receipt.get("source_commit")
        == "06ea2aa2cea7290aa6c53a2944e5c2ed91ce52b9"
    ):
        raise RuntimeError("V80 official START receipt absent or invalid")


def verify_v79_report() -> dict:
    report = read_json(V79_REPORT)
    metrics = report.get("metrics")
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V79_PASS": 1,
        "V79_BLIND_ACCESS": 0,
        "V79_VAL_LEXICAL": 9170,
        "V79_SAME_PATH_BATCH": 32,
        "V79_PERTURBED_PREFIXES": 9062,
        "V79_UNCHANGED_PREFIXES": 108,
        "V79_ORIGINAL_CORRECT": 2594,
        "V79_ORIGINAL_DISTINCT": 2,
        "V79_ORIGINAL_TOP1_SHARE_BP": 7043,
        "V79_REVERSE_CORRECT": 2594,
        "V79_REVERSE_DISTINCT": 2,
        "V79_REVERSE_TOP1_SHARE_BP": 7046,
        "V79_PRED_AGREE": 9165,
        "V79_PRED_CHANGED": 5,
        "V79_SHARED_CORRECT": 2594,
        "V79_ORIGINAL_ONLY_CORRECT": 0,
        "V79_REVERSE_ONLY_CORRECT": 0,
        "V79_ALPHA_SIGN_AGREE": 9165,
        "V79_ALPHA_SIGN_CHANGED": 5,
        "V79_ALPHA_CORR_ABS_BP": 9999,
        "V79_ALPHA_DELTA_GT_1E7": 9062,
        "V79_ALPHA_DELTA_GT_1E6": 9062,
        "V79_ALPHA_DELTA_GT_1E5": 9057,
        "V79_ALPHA_MAX_ABS_NANO": 1086937904,
        "V79_ALPHA_MEAN_ABS_NANO": 49932920,
        "V79_INPUT_INVARIANTS": 9170,
        "V79_COVERAGE_BP": 10000,
    }
    if not (
        report.get("step_id")
        == "PHASE03-SMOLTALK-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == 30
        and all(type(v) is int and v >= 0 for v in metrics.values())
        and all(metrics.get(k) == v for k, v in expected.items())
    ):
        raise RuntimeError("V80 frozen V79 report integrity gate failed")
    return metrics


def sign_classes(values: torch.Tensor) -> torch.Tensor:
    x = values.detach().to(device="cpu", dtype=torch.float64)
    if x.ndim != 1 or x.numel() == 0 or not torch.isfinite(x).all():
        raise ValueError("V80 invalid alpha vector")
    return torch.sign(x).to(dtype=torch.int8)


def boundary_distance(
    alpha_original: torch.Tensor,
    alpha_reverse: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    x = alpha_original.detach().to(device="cpu", dtype=torch.float64)
    y = alpha_reverse.detach().to(device="cpu", dtype=torch.float64)
    if not (
        x.ndim == 1
        and x.shape == y.shape
        and x.numel() > 0
        and torch.isfinite(x).all()
        and torch.isfinite(y).all()
    ):
        raise ValueError("V80 invalid alpha pair")
    ax = torch.abs(x)
    ay = torch.abs(y)
    return torch.minimum(ax, ay), torch.maximum(ax, ay)


def empty_boundary_stats() -> dict:
    stats = {
        "COUNT": 0,
        "CHANGED_COUNT": 0,
        "SIGN_CHANGED_COUNT": 0,
        "BOUNDARY_SUM_CHANGED": 0.0,
        "BOUNDARY_MAX_CHANGED": 0.0,
        "CROSSING_SUM_CHANGED": 0.0,
        "CROSSING_MAX_CHANGED": 0.0,
    }
    for label in ("1E7", "1E6", "1E5", "1E4", "1E3"):
        stats[f"ALL_WITHIN_{label}"] = 0
        stats[f"CHANGED_WITHIN_{label}"] = 0
        stats[f"SIGN_WITHIN_{label}"] = 0
    return stats


def update_boundary_stats(
    stats: dict,
    alpha_original: torch.Tensor,
    alpha_reverse: torch.Tensor,
    pred_original: torch.Tensor,
    pred_reverse: torch.Tensor,
) -> None:
    x = alpha_original.detach().to(device="cpu", dtype=torch.float64)
    y = alpha_reverse.detach().to(device="cpu", dtype=torch.float64)
    po = pred_original.detach().to(device="cpu", dtype=torch.long)
    pr = pred_reverse.detach().to(device="cpu", dtype=torch.long)
    if not (
        x.ndim == 1
        and x.shape == y.shape == po.shape == pr.shape
        and x.numel() > 0
        and torch.isfinite(x).all()
        and torch.isfinite(y).all()
    ):
        raise ValueError("V80 invalid boundary accounting input")

    boundary, crossing = boundary_distance(x, y)
    changed = po.ne(pr)

    sign_changed = sign_classes(x).ne(sign_classes(y))

    stats["COUNT"] += int(x.numel())
    stats["CHANGED_COUNT"] += int(changed.sum())
    stats["SIGN_CHANGED_COUNT"] += int(sign_changed.sum())

    labels = ("1E7", "1E6", "1E5", "1E4", "1E3")
    for label, threshold in zip(labels, THRESHOLDS):
        within = boundary <= threshold
        stats[f"ALL_WITHIN_{label}"] += int(within.sum())
        stats[f"CHANGED_WITHIN_{label}"] += int((within & changed).sum())
        stats[f"SIGN_WITHIN_{label}"] += int((within & sign_changed).sum())

    if changed.any():
        b = boundary[changed]
        c = crossing[changed]
        stats["BOUNDARY_SUM_CHANGED"] += float(b.sum())
        stats["BOUNDARY_MAX_CHANGED"] = max(
            stats["BOUNDARY_MAX_CHANGED"], float(b.max())
        )
        stats["CROSSING_SUM_CHANGED"] += float(c.sum())
        stats["CROSSING_MAX_CHANGED"] = max(
            stats["CROSSING_MAX_CHANGED"], float(c.max())
        )


def finalize_boundary_stats(stats: dict, expected: int) -> dict:
    if stats.get("COUNT") != expected:
        raise RuntimeError("V80 boundary coverage failed")
    changed = stats.get("CHANGED_COUNT")
    sign_changed = stats.get("SIGN_CHANGED_COUNT")
    if type(changed) is not int or type(sign_changed) is not int or changed <= 0:
        raise RuntimeError("V80 changed-set accounting failed")

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
            raise RuntimeError("V80 cumulative threshold accounting failed")

    floats = (
        stats["BOUNDARY_SUM_CHANGED"],
        stats["BOUNDARY_MAX_CHANGED"],
        stats["CROSSING_SUM_CHANGED"],
        stats["CROSSING_MAX_CHANGED"],
    )
    if not all(math.isfinite(v) and v >= 0.0 for v in floats):
        raise RuntimeError("V80 nonfinite boundary statistic")

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
        for value in (boundary_max, boundary_mean, crossing_max, crossing_mean)
    ):
        raise RuntimeError("V80 nano-scaled boundary statistic outside range")

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
        raise RuntimeError("V80 frozen VALIDATION segment count changed")
    if not (
        train_mean.shape == train_pc1.shape == (MODEL_DIM,)
        and residual_profile.shape == (VOCAB,)
        and torch.isfinite(residual_profile).all()
        and 3 <= unigram < VOCAB
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr() == model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V80 scoring geometry/output-head gate failed")

    mean_t = train_mean.to(device=device, dtype=torch.float32)
    pc1_t = train_pc1.to(device=device, dtype=torch.float32)
    residual_t = residual_profile.to(device=device, dtype=torch.float32)

    prefixes = []
    gold_values = []
    for seg in validation:
        tokens = tuple(seg.token_ids)
        if not tokens or tokens[0] != T.BOS_ID or tokens[-1] != T.EOS_ID:
            raise RuntimeError("V80 VALIDATION boundary changed")
        for target_index in range(1, len(tokens)):
            target = tokens[target_index]
            if not 3 <= target < VOCAB:
                continue
            prefix = tokens[:target_index]
            prefixes.append(prefix)
            gold_values.append(target)

    if len(prefixes) != VAL_LEXICAL or len(gold_values) != VAL_LEXICAL:
        raise RuntimeError("V80 validation lexical coverage mismatch")

    outcomes = {
        "ORIGINAL": V77.empty_outcome(),
        "REVERSE": V77.empty_outcome(),
    }
    replay_pairs = V79.empty_pair_stats()
    boundary_stats = empty_boundary_stats()
    taps = []

    def capture(_module, inputs):
        if (
            len(inputs) != 1
            or inputs[0].ndim != 3
            or inputs[0].shape[-1] != MODEL_DIM
        ):
            raise RuntimeError("V80 output-head hidden state shape changed")
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
                invariants = V79.pair_invariant_count(original, transformed)
                if invariants != len(original):
                    raise RuntimeError("V80 input invariant failed")

                alpha_original = V79.score_prefix_batch(
                    V77, model, device, original, mean_t, pc1_t, taps
                )
                alpha_reverse = V79.score_prefix_batch(
                    V77, model, device, transformed, mean_t, pc1_t, taps
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
                    raise RuntimeError("V80 nonfinite residual logits")

                pred_original = logits_original.argmax(dim=1)
                pred_reverse = logits_reverse.argmax(dim=1)

                V77.update_outcome(
                    outcomes["ORIGINAL"], pred_original, gold, unigram
                )
                V77.update_outcome(
                    outcomes["REVERSE"], pred_reverse, gold, unigram
                )
                V79.update_pair_stats(
                    replay_pairs,
                    alpha_original,
                    alpha_reverse,
                    pred_original,
                    pred_reverse,
                    gold,
                    changed_prefix,
                    invariants,
                )
                update_boundary_stats(
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
        V79.finalize_pair_stats(replay_pairs, VAL_LEXICAL),
        finalize_boundary_stats(boundary_stats, VAL_LEXICAL),
    )


def build_metrics(outcomes: dict, replay: dict, boundary: dict) -> dict:
    original = outcomes["ORIGINAL"]
    reverse = outcomes["REVERSE"]
    if not (
        original["CORRECT"] == 2594
        and reverse["CORRECT"] == 2594
        and replay["PRED_CHANGED"] == 5
        and replay["SIGN_CHANGED"] == 5
        and replay["PERTURBED_PREFIXES"] == PERTURBED_PREFIXES
        and replay["UNCHANGED_PREFIXES"] == UNCHANGED_PREFIXES
        and replay["INPUT_INVARIANTS"] == VAL_LEXICAL
    ):
        raise RuntimeError("V80 exact V79 replay failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V80_PASS": 1,
        "V80_BLIND_ACCESS": 0,
        "V80_VAL_LEXICAL": VAL_LEXICAL,
        "V80_SAME_PATH_BATCH": SAME_PATH_BATCH,
        "V80_PERTURBED_PREFIXES": replay["PERTURBED_PREFIXES"],
        "V80_UNCHANGED_PREFIXES": replay["UNCHANGED_PREFIXES"],
        "V80_V79_PRED_CHANGED_REPLAY": replay["PRED_CHANGED"],
        "V80_V79_SIGN_CHANGED_REPLAY": replay["SIGN_CHANGED"],
        "V80_V79_ORIGINAL_CORRECT_REPLAY": original["CORRECT"],
        "V80_V79_REVERSE_CORRECT_REPLAY": reverse["CORRECT"],
        "V80_ALL_WITHIN_1E7": boundary["ALL_WITHIN_1E7"],
        "V80_ALL_WITHIN_1E6": boundary["ALL_WITHIN_1E6"],
        "V80_ALL_WITHIN_1E5": boundary["ALL_WITHIN_1E5"],
        "V80_ALL_WITHIN_1E4": boundary["ALL_WITHIN_1E4"],
        "V80_ALL_WITHIN_1E3": boundary["ALL_WITHIN_1E3"],
        "V80_CHANGED_WITHIN_1E7": boundary["CHANGED_WITHIN_1E7"],
        "V80_CHANGED_WITHIN_1E6": boundary["CHANGED_WITHIN_1E6"],
        "V80_CHANGED_WITHIN_1E5": boundary["CHANGED_WITHIN_1E5"],
        "V80_CHANGED_WITHIN_1E4": boundary["CHANGED_WITHIN_1E4"],
        "V80_CHANGED_WITHIN_1E3": boundary["CHANGED_WITHIN_1E3"],
        "V80_SIGN_WITHIN_1E7": boundary["SIGN_WITHIN_1E7"],
        "V80_SIGN_WITHIN_1E6": boundary["SIGN_WITHIN_1E6"],
        "V80_SIGN_WITHIN_1E5": boundary["SIGN_WITHIN_1E5"],
        "V80_BOUNDARY_MAX_NANO_CHANGED": boundary["BOUNDARY_MAX_NANO_CHANGED"],
        "V80_BOUNDARY_MEAN_NANO_CHANGED": boundary["BOUNDARY_MEAN_NANO_CHANGED"],
        "V80_CROSSING_MAX_NANO_CHANGED": boundary["CROSSING_MAX_NANO_CHANGED"],
        "V80_CROSSING_MEAN_NANO_CHANGED": boundary["CROSSING_MEAN_NANO_CHANGED"],
    }

    if not (
        tuple(metrics) == METRIC_FIELDS
        and len(metrics) == 30
        and all(
            type(v) is int
            and 0 <= v <= (
                ALPHA_NANO_LIMIT
                if k in {
                    "V80_BOUNDARY_MAX_NANO_CHANGED",
                    "V80_BOUNDARY_MEAN_NANO_CHANGED",
                    "V80_CROSSING_MAX_NANO_CHANGED",
                    "V80_CROSSING_MEAN_NANO_CHANGED",
                }
                else PUBLIC_METRIC_MAX
            )
            for k, v in metrics.items()
        )
    ):
        raise RuntimeError("V80 strict 30-integer metric schema failed")
    return metrics


def compute():
    torch.set_grad_enabled(False)
    verify_dependency_blobs()
    verify_start_receipt()
    verify_v79_report()

    V79 = imported("v80_frozen_v79_control", V79_SOURCE)
    V79.verify_dependency_blobs()
    V79.verify_start_receipt()
    V79.verify_v77_report()
    V79.verify_v78_report()

    V77 = V79.imported("v80_frozen_v77_control", V79.V77_SOURCE)
    V78 = V79.imported("v80_frozen_v78_control", V79.V78_SOURCE)
    V77.verify_dependency_blobs()
    v76_metrics = V77.verify_v76_report()

    v76 = V77.imported("v80_frozen_v76_control", V77.V76_SOURCE)
    v75 = V77.imported("v80_frozen_v75_geometry", V77.V75_SOURCE)
    v65 = V77.imported("v80_frozen_v65_frequency", V77.V65_SOURCE)
    v64 = v75.imported("v80_v64_preflight", v75.V64)

    model, device, streams, validation = v64.preflight()
    if device.type != "cuda":
        raise RuntimeError("V80 requires reviewed CUDA inference path")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("V80 requires CUDA BF16 support")

    if not (
        V79.SAME_PATH_BATCH == SAME_PATH_BATCH
        and V79.SCORE_CHUNK == SCORE_CHUNK
        and V79.GPU_PEAK_LIMIT_MIB == GPU_PEAK_LIMIT_MIB
        and V78.PATH_B_BATCH == SAME_PATH_BATCH
    ):
        raise RuntimeError("V80 inherited runtime constants changed")

    frequency = v65.count_training_tokens(streams)
    v76.frequency_count_vector(frequency, require_frozen=True)
    unigram = v75.most_frequent(frequency)
    if v76_metrics["V76_UNIGRAM_CORRECT"] != 2535:
        raise RuntimeError("V80 frozen unigram provenance changed")

    torch.cuda.reset_peak_memory_stats(device)

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
        raise RuntimeError("V80 frozen TRAIN PC1 variance replay failed")

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
        raise RuntimeError("V80 frozen V76 residual decomposition replay failed")

    outcomes, replay, boundary = score_validation(
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
    metrics = build_metrics(outcomes, replay, boundary)

    peak_mib = math.ceil(
        torch.cuda.max_memory_allocated(device) / (1024 * 1024)
    )
    if peak_mib > GPU_PEAK_LIMIT_MIB:
        raise RuntimeError("V80 GPU peak-memory gate exceeded")
    return metrics, peak_mib


def main():
    metrics, _peak_mib = compute()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
