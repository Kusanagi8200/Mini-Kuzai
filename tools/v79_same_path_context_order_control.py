#!/usr/bin/env python3
"""V79 same-path context-order control.

Evaluates ORIGINAL and REVERSE_HISTORY_KEEP_LAST through the exact same
prefix-scoring helper and batch size. The frozen V76 residual profile, target,
model and scoring pipeline remain unchanged; only earlier-history order may
differ.

No training, BLIND access, generation, checkpoint write, raw token text,
per-position publication or hidden-state persistence is permitted.
"""
from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mini_kuzai import phase03_v62_trainer as T

STEP_ID = "PHASE03-SMOLTALK-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001"

SAME_PATH_BATCH = 32
SCORE_CHUNK = 512
GPU_PEAK_LIMIT_MIB = 6144
VAL_LEXICAL = 9170
MODEL_DIM = 128
VOCAB = 1024
PERTURBED_PREFIXES = 9062
UNCHANGED_PREFIXES = 108

DELTA_1E7 = 1e-7
DELTA_1E6 = 1e-6
DELTA_1E5 = 1e-5
NANO_SCALE = 1_000_000_000

V77_SOURCE = ROOT / "tools" / "v77_residual_context_order_sensitivity.py"
V78_SOURCE = ROOT / "tools" / "v78_identical_context_rebatching_numerical_control.py"
V77_REPORT = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.json"
)
V78_REPORT = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.json"
)
V79_START_RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V79-start.json"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.md"
)

DEPENDENCY_BLOBS = {
    "tools/v77_residual_context_order_sensitivity.py":
        "941df566949291c55da1b4c6b0b6c63ad52dbd37",
    "tools/v78_identical_context_rebatching_numerical_control.py":
        "4aa901d9a27d03e48e8099fb21799aa8e7cead9e",
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.json":
        "68f7c331942ac50238090fd72e6d3008fe2374a7",
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.json":
        "f32dfdd19e9a56d5a90ce0bfe629760c0d604429",
    "automation/dev-flow/receipts/V79-start.json":
        "613dc5635e8a9b5bd591fc35a87d5d383a3d0900",
    "phases/MINI-KUZAI-PHASE-03-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.md":
        "ca66821d0e844c13350d58e922b8adadd96f6f12",
}

METRIC_FIELDS = (
    "SEMANTIC_VALIDATION_COMPLETE",
    "TRAINING_AUTHORIZED",
    "TRAINING_STARTED",
    "V79_PASS",
    "V79_BLIND_ACCESS",
    "V79_VAL_LEXICAL",
    "V79_SAME_PATH_BATCH",
    "V79_PERTURBED_PREFIXES",
    "V79_UNCHANGED_PREFIXES",
    "V79_ORIGINAL_CORRECT",
    "V79_ORIGINAL_DISTINCT",
    "V79_ORIGINAL_TOP1_SHARE_BP",
    "V79_REVERSE_CORRECT",
    "V79_REVERSE_DISTINCT",
    "V79_REVERSE_TOP1_SHARE_BP",
    "V79_PRED_AGREE",
    "V79_PRED_CHANGED",
    "V79_SHARED_CORRECT",
    "V79_ORIGINAL_ONLY_CORRECT",
    "V79_REVERSE_ONLY_CORRECT",
    "V79_ALPHA_SIGN_AGREE",
    "V79_ALPHA_SIGN_CHANGED",
    "V79_ALPHA_CORR_ABS_BP",
    "V79_ALPHA_DELTA_GT_1E7",
    "V79_ALPHA_DELTA_GT_1E6",
    "V79_ALPHA_DELTA_GT_1E5",
    "V79_ALPHA_MAX_ABS_NANO",
    "V79_ALPHA_MEAN_ABS_NANO",
    "V79_INPUT_INVARIANTS",
    "V79_COVERAGE_BP",
)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V79 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V79 expected JSON object")
    return value


def imported(name: str, source: Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("V79 reviewed dependency unavailable or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V79 dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_blob(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V79 pinned source missing or unsafe")
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError("V79 Git blob calculation failed")
    return proc.stdout.strip()


def verify_dependency_blobs() -> None:
    for relative, expected in DEPENDENCY_BLOBS.items():
        if git_blob(ROOT / relative) != expected:
            raise RuntimeError("V79 frozen dependency blob mismatch")


def verify_start_receipt() -> None:
    receipt = read_json(V79_START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V79"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/10"
        and receipt.get("source_commit")
        == "5f86ce1c143f2574301c18669803d251921bffb7"
    ):
        raise RuntimeError("V79 official START receipt absent or invalid")


def verify_v77_report() -> dict:
    report = read_json(V77_REPORT)
    metrics = report.get("metrics")
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V77_PASS": 1,
        "V77_BLIND_ACCESS": 0,
        "V77_VAL_LEXICAL": 9170,
        "V77_HIDDEN_DIM": 128,
        "V77_VOCAB": 1024,
        "V77_FULL_CORRECT": 2594,
        "V77_FULL_DISTINCT": 2,
        "V77_FULL_TOP1_SHARE_BP": 7043,
        "V77_FULL_UNIGRAM_AGREE": 6458,
        "V77_FULL_UNIGRAM_SHARED_CORRECT": 2451,
        "V77_REVERSE_CORRECT": 2594,
        "V77_REVERSE_DISTINCT": 2,
        "V77_REVERSE_TOP1_SHARE_BP": 7046,
        "V77_REVERSE_UNIGRAM_AGREE": 6461,
        "V77_REVERSE_UNIGRAM_SHARED_CORRECT": 2451,
        "V77_PRED_AGREE": 9165,
        "V77_PRED_CHANGED": 5,
        "V77_FULL_REVERSE_SHARED_CORRECT": 2594,
        "V77_FULL_ONLY_CORRECT": 0,
        "V77_REVERSE_ONLY_CORRECT": 0,
        "V77_ALPHA_SIGN_AGREE": 9165,
        "V77_ALPHA_SIGN_CHANGED": 5,
        "V77_ALPHA_CORR_ABS_BP": 9999,
        "V77_ALPHA_DELTA_NONZERO": 9123,
        "V77_PERTURBED_PREFIXES": 9062,
        "V77_UNCHANGED_PREFIXES": 108,
        "V77_COVERAGE_BP": 10000,
    }
    if not (
        report.get("step_id")
        == "PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
        and all(metrics.get(k) == v for k, v in expected.items())
    ):
        raise RuntimeError("V79 frozen V77 report integrity gate failed")
    return metrics


def verify_v78_report() -> dict:
    report = read_json(V78_REPORT)
    metrics = report.get("metrics")
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V78_PASS": 1,
        "V78_BLIND_ACCESS": 0,
        "V78_VAL_LEXICAL": 9170,
        "V78_PATH_A_BATCH": 4,
        "V78_PATH_B_BATCH": 32,
        "V78_PATH_A_CORRECT": 2594,
        "V78_PATH_A_DISTINCT": 2,
        "V78_PATH_A_TOP1_SHARE_BP": 7043,
        "V78_PATH_B_CORRECT": 2594,
        "V78_PATH_B_DISTINCT": 2,
        "V78_PATH_B_TOP1_SHARE_BP": 7043,
        "V78_PRED_AGREE": 9170,
        "V78_PRED_CHANGED": 0,
        "V78_SHARED_CORRECT": 2594,
        "V78_A_ONLY_CORRECT": 0,
        "V78_B_ONLY_CORRECT": 0,
        "V78_ALPHA_SIGN_AGREE": 9170,
        "V78_ALPHA_SIGN_CHANGED": 0,
        "V78_ALPHA_CORR_ABS_BP": 10000,
        "V78_ALPHA_DELTA_GT_1E7": 4107,
        "V78_ALPHA_DELTA_GT_1E6": 1226,
        "V78_ALPHA_DELTA_GT_1E5": 1209,
        "V78_ALPHA_MAX_ABS_NANO": 10442495,
        "V78_ALPHA_MEAN_ABS_NANO": 238663,
        "V78_IDENTICAL_PREFIXES": 9170,
        "V78_INPUT_MATCHES": 9170,
        "V78_COVERAGE_BP": 10000,
    }
    if not (
        report.get("step_id")
        == "PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
        and all(metrics.get(k) == v for k, v in expected.items())
    ):
        raise RuntimeError("V79 frozen V78 report integrity gate failed")
    return metrics


def reverse_history_keep_last(prefix) -> tuple[int, ...]:
    v77 = imported("v79_v77_transform", V77_SOURCE)
    return v77.reverse_history_keep_last(prefix)


def sign_classes(values: torch.Tensor) -> torch.Tensor:
    x = values.detach().to(device="cpu", dtype=torch.float64)
    if x.ndim != 1 or x.numel() == 0 or not torch.isfinite(x).all():
        raise ValueError("V79 invalid alpha vector")
    return torch.sign(x).to(dtype=torch.int8)


def pair_invariant_count(original: list, transformed: list) -> int:
    if len(original) != len(transformed) or not original:
        raise ValueError("V79 invalid paired prefix collection")
    count = 0
    for source, reverse in zip(original, transformed):
        a = tuple(source)
        b = tuple(reverse)
        valid = (
            len(a) == len(b)
            and len(a) > 0
            and a[0] == b[0] == T.BOS_ID
            and a[-1] == b[-1]
            and Counter(a) == Counter(b)
            and Counter(
                x for x in a[1:-1] if x in {T.PAD_ID, T.BOS_ID, T.EOS_ID}
            )
            == Counter(
                x for x in b[1:-1] if x in {T.PAD_ID, T.BOS_ID, T.EOS_ID}
            )
        )
        if valid:
            count += 1
    return count


def empty_pair_stats() -> dict:
    return {
        "COUNT": 0,
        "SUM_X": 0.0,
        "SUM_Y": 0.0,
        "SUM_X2": 0.0,
        "SUM_Y2": 0.0,
        "SUM_XY": 0.0,
        "SUM_ABS_DELTA": 0.0,
        "MAX_ABS_DELTA": 0.0,
        "PRED_AGREE": 0,
        "PRED_CHANGED": 0,
        "SHARED_CORRECT": 0,
        "ORIGINAL_ONLY_CORRECT": 0,
        "REVERSE_ONLY_CORRECT": 0,
        "SIGN_AGREE": 0,
        "SIGN_CHANGED": 0,
        "DELTA_GT_1E7": 0,
        "DELTA_GT_1E6": 0,
        "DELTA_GT_1E5": 0,
        "PERTURBED_PREFIXES": 0,
        "UNCHANGED_PREFIXES": 0,
        "INPUT_INVARIANTS": 0,
    }


def update_pair_stats(
    stats: dict,
    alpha_original: torch.Tensor,
    alpha_reverse: torch.Tensor,
    pred_original: torch.Tensor,
    pred_reverse: torch.Tensor,
    gold: torch.Tensor,
    changed_prefix: torch.Tensor,
    input_invariants: int,
) -> None:
    x = alpha_original.detach().to(device="cpu", dtype=torch.float64)
    y = alpha_reverse.detach().to(device="cpu", dtype=torch.float64)
    po = pred_original.detach().to(device="cpu", dtype=torch.long)
    pr = pred_reverse.detach().to(device="cpu", dtype=torch.long)
    target = gold.detach().to(device="cpu", dtype=torch.long)
    changed = changed_prefix.detach().to(device="cpu", dtype=torch.bool)

    if not (
        x.ndim == 1
        and x.shape == y.shape == po.shape == pr.shape == target.shape == changed.shape
        and x.numel() > 0
        and torch.isfinite(x).all()
        and torch.isfinite(y).all()
        and type(input_invariants) is int
        and 0 <= input_invariants <= x.numel()
    ):
        raise ValueError("V79 invalid paired accounting input")

    n = int(x.numel())
    so = sign_classes(x)
    sr = sign_classes(y)
    original_correct = po.eq(target)
    reverse_correct = pr.eq(target)
    pred_same = po.eq(pr)
    sign_same = so.eq(sr)
    delta = torch.abs(x - y)

    stats["COUNT"] += n
    stats["SUM_X"] += float(x.sum())
    stats["SUM_Y"] += float(y.sum())
    stats["SUM_X2"] += float(torch.dot(x, x))
    stats["SUM_Y2"] += float(torch.dot(y, y))
    stats["SUM_XY"] += float(torch.dot(x, y))
    stats["SUM_ABS_DELTA"] += float(delta.sum())
    stats["MAX_ABS_DELTA"] = max(stats["MAX_ABS_DELTA"], float(delta.max()))
    stats["PRED_AGREE"] += int(pred_same.sum())
    stats["PRED_CHANGED"] += int((~pred_same).sum())
    stats["SHARED_CORRECT"] += int((original_correct & reverse_correct).sum())
    stats["ORIGINAL_ONLY_CORRECT"] += int((original_correct & ~reverse_correct).sum())
    stats["REVERSE_ONLY_CORRECT"] += int((~original_correct & reverse_correct).sum())
    stats["SIGN_AGREE"] += int(sign_same.sum())
    stats["SIGN_CHANGED"] += int((~sign_same).sum())
    stats["DELTA_GT_1E7"] += int((delta > DELTA_1E7).sum())
    stats["DELTA_GT_1E6"] += int((delta > DELTA_1E6).sum())
    stats["DELTA_GT_1E5"] += int((delta > DELTA_1E5).sum())
    stats["PERTURBED_PREFIXES"] += int(changed.sum())
    stats["UNCHANGED_PREFIXES"] += int((~changed).sum())
    stats["INPUT_INVARIANTS"] += input_invariants


def finalize_pair_stats(stats: dict, expected: int) -> dict:
    n = stats.get("COUNT")
    if type(n) is not int or n != expected or n <= 1:
        raise RuntimeError("V79 paired coverage failed")

    for key in (
        "SUM_X", "SUM_Y", "SUM_X2", "SUM_Y2", "SUM_XY",
        "SUM_ABS_DELTA", "MAX_ABS_DELTA",
    ):
        if not math.isfinite(stats[key]):
            raise RuntimeError("V79 nonfinite paired statistic")

    cov_num = stats["SUM_XY"] - stats["SUM_X"] * stats["SUM_Y"] / n
    var_x = stats["SUM_X2"] - stats["SUM_X"] * stats["SUM_X"] / n
    var_y = stats["SUM_Y2"] - stats["SUM_Y"] * stats["SUM_Y"] / n
    if not (
        math.isfinite(cov_num)
        and math.isfinite(var_x)
        and math.isfinite(var_y)
        and var_x > 0.0
        and var_y > 0.0
    ):
        raise RuntimeError("V79 degenerate alpha correlation")

    corr_abs = abs(cov_num) / math.sqrt(var_x * var_y)
    if not math.isfinite(corr_abs) or not 0.0 <= corr_abs <= 1.0000001:
        raise RuntimeError("V79 invalid alpha correlation")
    corr_abs = min(corr_abs, 1.0)

    for left, right in (
        ("PRED_AGREE", "PRED_CHANGED"),
        ("SIGN_AGREE", "SIGN_CHANGED"),
        ("PERTURBED_PREFIXES", "UNCHANGED_PREFIXES"),
    ):
        if stats[left] + stats[right] != expected:
            raise RuntimeError("V79 paired partition accounting failed")

    if not (
        stats["PERTURBED_PREFIXES"] == PERTURBED_PREFIXES
        and stats["UNCHANGED_PREFIXES"] == UNCHANGED_PREFIXES
        and stats["INPUT_INVARIANTS"] == expected
        and 0 <= stats["SHARED_CORRECT"] <= expected
        and 0 <= stats["ORIGINAL_ONLY_CORRECT"] <= expected
        and 0 <= stats["REVERSE_ONLY_CORRECT"] <= expected
        and 0 <= stats["DELTA_GT_1E5"] <= stats["DELTA_GT_1E6"]
        <= stats["DELTA_GT_1E7"] <= expected
    ):
        raise RuntimeError("V79 paired result outside admissible range")

    max_nano = round(stats["MAX_ABS_DELTA"] * NANO_SCALE)
    mean_nano = round(stats["SUM_ABS_DELTA"] * NANO_SCALE / expected)
    if not (
        0 <= max_nano <= 100_000_000
        and 0 <= mean_nano <= 100_000_000
    ):
        raise RuntimeError("V79 nano-scaled alpha delta outside public range")

    return {
        "PRED_AGREE": stats["PRED_AGREE"],
        "PRED_CHANGED": stats["PRED_CHANGED"],
        "SHARED_CORRECT": stats["SHARED_CORRECT"],
        "ORIGINAL_ONLY_CORRECT": stats["ORIGINAL_ONLY_CORRECT"],
        "REVERSE_ONLY_CORRECT": stats["REVERSE_ONLY_CORRECT"],
        "SIGN_AGREE": stats["SIGN_AGREE"],
        "SIGN_CHANGED": stats["SIGN_CHANGED"],
        "ALPHA_CORR_ABS_BP": round(corr_abs * 10000),
        "DELTA_GT_1E7": stats["DELTA_GT_1E7"],
        "DELTA_GT_1E6": stats["DELTA_GT_1E6"],
        "DELTA_GT_1E5": stats["DELTA_GT_1E5"],
        "ALPHA_MAX_ABS_NANO": max_nano,
        "ALPHA_MEAN_ABS_NANO": mean_nano,
        "PERTURBED_PREFIXES": stats["PERTURBED_PREFIXES"],
        "UNCHANGED_PREFIXES": stats["UNCHANGED_PREFIXES"],
        "INPUT_INVARIANTS": stats["INPUT_INVARIANTS"],
    }


def score_prefix_batch(
    V77,
    model,
    device,
    prefixes: list,
    mean_t: torch.Tensor,
    pc1_t: torch.Tensor,
    taps: list,
) -> torch.Tensor:
    if not prefixes or len(prefixes) > SAME_PATH_BATCH:
        raise ValueError("V79 invalid same-path prefix batch")
    max_len = max(len(prefix) for prefix in prefixes)
    ids = torch.full(
        (len(prefixes), max_len),
        T.PAD_ID,
        dtype=torch.long,
        device=device,
    )
    for row, prefix in enumerate(prefixes):
        if (
            not prefix
            or prefix[0] != T.BOS_ID
            or T.PAD_ID in prefix
        ):
            raise RuntimeError("V79 prefix boundary changed")
        ids[row, : len(prefix)] = torch.as_tensor(
            prefix, dtype=torch.long, device=device
        )

    hidden = V77._forward_hidden(model, ids, taps)
    rows = torch.arange(len(prefixes), device=device, dtype=torch.long)
    last = torch.as_tensor(
        [len(prefix) - 1 for prefix in prefixes],
        device=device,
        dtype=torch.long,
    )
    selected = hidden[rows, last]
    alpha = (selected - mean_t) @ pc1_t
    if not torch.isfinite(alpha).all():
        raise RuntimeError("V79 nonfinite same-path alpha")
    return alpha


def score_validation(
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
        raise RuntimeError("V79 frozen VALIDATION segment count changed")
    if not (
        train_mean.shape == train_pc1.shape == (MODEL_DIM,)
        and residual_profile.shape == (VOCAB,)
        and torch.isfinite(residual_profile).all()
        and 3 <= unigram < VOCAB
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr() == model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V79 scoring geometry/output-head gate failed")

    mean_t = train_mean.to(device=device, dtype=torch.float32)
    pc1_t = train_pc1.to(device=device, dtype=torch.float32)
    residual_t = residual_profile.to(device=device, dtype=torch.float32)

    prefixes = []
    gold_values = []
    for seg in validation:
        tokens = tuple(seg.token_ids)
        if not tokens or tokens[0] != T.BOS_ID or tokens[-1] != T.EOS_ID:
            raise RuntimeError("V79 VALIDATION boundary changed")
        for target_index in range(1, len(tokens)):
            target = tokens[target_index]
            if not 3 <= target < VOCAB:
                continue
            prefix = tokens[:target_index]
            if not prefix or prefix[-1] != tokens[target_index - 1]:
                raise RuntimeError("V79 prefix/target alignment failed")
            prefixes.append(prefix)
            gold_values.append(target)

    if len(prefixes) != VAL_LEXICAL or len(gold_values) != VAL_LEXICAL:
        raise RuntimeError("V79 validation lexical coverage mismatch")

    outcomes = {
        "ORIGINAL": V77.empty_outcome(),
        "REVERSE": V77.empty_outcome(),
    }
    pairs = empty_pair_stats()
    taps = []

    def capture(_module, inputs):
        if (
            len(inputs) != 1
            or inputs[0].ndim != 3
            or inputs[0].shape[-1] != MODEL_DIM
        ):
            raise RuntimeError("V79 output-head hidden state shape changed")
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
                changed = torch.as_tensor(
                    [a != b for a, b in zip(original, transformed)],
                    dtype=torch.bool,
                )
                invariants = pair_invariant_count(original, transformed)
                if invariants != len(original):
                    raise RuntimeError("V79 input invariant failed")

                alpha_original = score_prefix_batch(
                    V77, model, device, original, mean_t, pc1_t, taps
                )
                alpha_reverse = score_prefix_batch(
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
                    raise RuntimeError("V79 nonfinite residual logits")

                pred_original = logits_original.argmax(dim=1)
                pred_reverse = logits_reverse.argmax(dim=1)

                V77.update_outcome(
                    outcomes["ORIGINAL"], pred_original, gold, unigram
                )
                V77.update_outcome(
                    outcomes["REVERSE"], pred_reverse, gold, unigram
                )
                update_pair_stats(
                    pairs,
                    alpha_original,
                    alpha_reverse,
                    pred_original,
                    pred_reverse,
                    gold,
                    changed,
                    invariants,
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
        finalize_pair_stats(pairs, VAL_LEXICAL),
    )


def build_metrics(outcomes: dict, pairs: dict) -> dict:
    if set(outcomes) != {"ORIGINAL", "REVERSE"}:
        raise RuntimeError("V79 scoring modes incomplete")

    original = outcomes["ORIGINAL"]
    reverse = outcomes["REVERSE"]
    if not (
        original["CORRECT"] == 2594
        and original["DISTINCT"] == 2
        and original["TOP1_SHARE_BP"] == 7043
    ):
        raise RuntimeError("V79 frozen V78 PATH_B replay failed")

    for item in (original, reverse):
        if not (
            0 <= item["CORRECT"] <= VAL_LEXICAL
            and 1 <= item["DISTINCT"] <= VOCAB
            and 0 <= item["TOP1_SHARE_BP"] <= 10000
        ):
            raise RuntimeError("V79 invalid aggregate scoring result")

    if not (
        pairs["PRED_AGREE"] + pairs["PRED_CHANGED"] == VAL_LEXICAL
        and pairs["SIGN_AGREE"] + pairs["SIGN_CHANGED"] == VAL_LEXICAL
        and pairs["PERTURBED_PREFIXES"] == PERTURBED_PREFIXES
        and pairs["UNCHANGED_PREFIXES"] == UNCHANGED_PREFIXES
        and pairs["SHARED_CORRECT"] + pairs["ORIGINAL_ONLY_CORRECT"]
        == original["CORRECT"]
        and pairs["SHARED_CORRECT"] + pairs["REVERSE_ONLY_CORRECT"]
        == reverse["CORRECT"]
        and pairs["INPUT_INVARIANTS"] == VAL_LEXICAL
        and 0 <= pairs["ALPHA_CORR_ABS_BP"] <= 10000
    ):
        raise RuntimeError("V79 paired correctness/input partition failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V79_PASS": 1,
        "V79_BLIND_ACCESS": 0,
        "V79_VAL_LEXICAL": VAL_LEXICAL,
        "V79_SAME_PATH_BATCH": SAME_PATH_BATCH,
        "V79_PERTURBED_PREFIXES": pairs["PERTURBED_PREFIXES"],
        "V79_UNCHANGED_PREFIXES": pairs["UNCHANGED_PREFIXES"],
        "V79_ORIGINAL_CORRECT": original["CORRECT"],
        "V79_ORIGINAL_DISTINCT": original["DISTINCT"],
        "V79_ORIGINAL_TOP1_SHARE_BP": original["TOP1_SHARE_BP"],
        "V79_REVERSE_CORRECT": reverse["CORRECT"],
        "V79_REVERSE_DISTINCT": reverse["DISTINCT"],
        "V79_REVERSE_TOP1_SHARE_BP": reverse["TOP1_SHARE_BP"],
        "V79_PRED_AGREE": pairs["PRED_AGREE"],
        "V79_PRED_CHANGED": pairs["PRED_CHANGED"],
        "V79_SHARED_CORRECT": pairs["SHARED_CORRECT"],
        "V79_ORIGINAL_ONLY_CORRECT": pairs["ORIGINAL_ONLY_CORRECT"],
        "V79_REVERSE_ONLY_CORRECT": pairs["REVERSE_ONLY_CORRECT"],
        "V79_ALPHA_SIGN_AGREE": pairs["SIGN_AGREE"],
        "V79_ALPHA_SIGN_CHANGED": pairs["SIGN_CHANGED"],
        "V79_ALPHA_CORR_ABS_BP": pairs["ALPHA_CORR_ABS_BP"],
        "V79_ALPHA_DELTA_GT_1E7": pairs["DELTA_GT_1E7"],
        "V79_ALPHA_DELTA_GT_1E6": pairs["DELTA_GT_1E6"],
        "V79_ALPHA_DELTA_GT_1E5": pairs["DELTA_GT_1E5"],
        "V79_ALPHA_MAX_ABS_NANO": pairs["ALPHA_MAX_ABS_NANO"],
        "V79_ALPHA_MEAN_ABS_NANO": pairs["ALPHA_MEAN_ABS_NANO"],
        "V79_INPUT_INVARIANTS": pairs["INPUT_INVARIANTS"],
        "V79_COVERAGE_BP": 10000,
    }

    if not (
        tuple(metrics) == METRIC_FIELDS
        and len(metrics) == 30
        and all(
            type(v) is int and 0 <= v <= 100_000_000
            for v in metrics.values()
        )
    ):
        raise RuntimeError("V79 strict 30-integer metric schema failed")
    return metrics


def compute():
    torch.set_grad_enabled(False)
    verify_dependency_blobs()
    verify_start_receipt()
    verify_v77_report()
    v78_metrics = verify_v78_report()

    V77 = imported("v79_frozen_v77_control", V77_SOURCE)
    V78 = imported("v79_frozen_v78_control", V78_SOURCE)
    V77.verify_dependency_blobs()
    v76_metrics = V77.verify_v76_report()

    v76 = V77.imported("v79_frozen_v76_control", V77.V76_SOURCE)
    v75 = V77.imported("v79_frozen_v75_geometry", V77.V75_SOURCE)
    v65 = V77.imported("v79_frozen_v65_frequency", V77.V65_SOURCE)
    v64 = v75.imported("v79_v64_preflight", v75.V64)

    model, device, streams, validation = v64.preflight()
    if device.type != "cuda":
        raise RuntimeError("V79 requires reviewed CUDA inference path")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("V79 requires CUDA BF16 support")

    if not (
        V77.COUNTERFACTUAL_BATCH == SAME_PATH_BATCH
        and V78.PATH_B_BATCH == SAME_PATH_BATCH
        and V77.SCORE_CHUNK == SCORE_CHUNK
        and V78.SCORE_CHUNK == SCORE_CHUNK
        and V77.GPU_PEAK_LIMIT_MIB == GPU_PEAK_LIMIT_MIB
        and V78.GPU_PEAK_LIMIT_MIB == GPU_PEAK_LIMIT_MIB
    ):
        raise RuntimeError("V79 inherited runtime constants changed")

    if not (
        v78_metrics["V78_PATH_B_CORRECT"] == 2594
        and v78_metrics["V78_PATH_B_DISTINCT"] == 2
        and v78_metrics["V78_PATH_B_TOP1_SHARE_BP"] == 7043
    ):
        raise RuntimeError("V79 V78 PATH_B baseline provenance changed")

    frequency = v65.count_training_tokens(streams)
    v76.frequency_count_vector(frequency, require_frozen=True)
    unigram = v75.most_frequent(frequency)
    if v76_metrics["V76_UNIGRAM_CORRECT"] != 2535:
        raise RuntimeError("V79 frozen unigram provenance changed")

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
        raise RuntimeError("V79 frozen TRAIN PC1 variance replay failed")

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
        raise RuntimeError("V79 frozen V76 residual decomposition replay failed")

    outcomes, pairs = score_validation(
        V77,
        model,
        device,
        validation,
        train_mean,
        train_pc1,
        profiles["RESIDUAL"],
        unigram,
    )
    metrics = build_metrics(outcomes, pairs)

    peak_mib = math.ceil(
        torch.cuda.max_memory_allocated(device) / (1024 * 1024)
    )
    if peak_mib > GPU_PEAK_LIMIT_MIB:
        raise RuntimeError("V79 GPU peak-memory gate exceeded")
    return metrics, peak_mib


def main():
    metrics, _peak_mib = compute()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
