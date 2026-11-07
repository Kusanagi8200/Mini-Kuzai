#!/usr/bin/env python3
"""V77 read-only residual context-order sensitivity control.

Reconstructs the frozen V76 TRAIN-derived frequency-residualized PC1 output
profile, then compares frozen VALIDATION scoring under original context and a
deterministic earlier-history reversal that preserves BOS, immediate predecessor,
prefix length, token multiset and target.

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

STEP_ID = "PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001"

VAL_BATCH = 4
COUNTERFACTUAL_BATCH = 32
SCORE_CHUNK = 512
GPU_PEAK_LIMIT_MIB = 6144
ALPHA_DELTA_THRESHOLD = 1e-7

VAL_LEXICAL = 9170
MODEL_DIM = 128
VOCAB = 1024

V76_SOURCE = ROOT / "tools" / "v76_frequency_residualized_pc1_control.py"
V75_SOURCE = ROOT / "tools" / "v75_train_fitted_geometry_transfer.py"
V65_SOURCE = ROOT / "tools" / "public-audits" / "phase03_v65_token_frequency_diagnostic_001.py"
V76_REPORT = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.json"
)
V77_START_RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V77-start.json"

DEPENDENCY_BLOBS = {
    "tools/v76_frequency_residualized_pc1_control.py":
        "d0db771c2f022a2e94293f8b0345ba834580407e",
    "tools/v75_train_fitted_geometry_transfer.py":
        "8705d8ca9aebe7281779c704119d26eb82517da2",
    "tools/public-audits/phase03_v65_token_frequency_diagnostic_001.py":
        "d88e05933686b369d5236c3bcd465729e2df3407",
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.json":
        "49290fdb267060130aae781f01e84936265eb426",
}

METRIC_FIELDS = (
    "SEMANTIC_VALIDATION_COMPLETE",
    "TRAINING_AUTHORIZED",
    "TRAINING_STARTED",
    "V77_PASS",
    "V77_BLIND_ACCESS",
    "V77_VAL_LEXICAL",
    "V77_HIDDEN_DIM",
    "V77_VOCAB",
    "V77_FULL_CORRECT",
    "V77_FULL_DISTINCT",
    "V77_FULL_TOP1_SHARE_BP",
    "V77_FULL_UNIGRAM_AGREE",
    "V77_FULL_UNIGRAM_SHARED_CORRECT",
    "V77_REVERSE_CORRECT",
    "V77_REVERSE_DISTINCT",
    "V77_REVERSE_TOP1_SHARE_BP",
    "V77_REVERSE_UNIGRAM_AGREE",
    "V77_REVERSE_UNIGRAM_SHARED_CORRECT",
    "V77_PRED_AGREE",
    "V77_PRED_CHANGED",
    "V77_FULL_REVERSE_SHARED_CORRECT",
    "V77_FULL_ONLY_CORRECT",
    "V77_REVERSE_ONLY_CORRECT",
    "V77_ALPHA_SIGN_AGREE",
    "V77_ALPHA_SIGN_CHANGED",
    "V77_ALPHA_CORR_ABS_BP",
    "V77_ALPHA_DELTA_NONZERO",
    "V77_PERTURBED_PREFIXES",
    "V77_UNCHANGED_PREFIXES",
    "V77_COVERAGE_BP",
)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V77 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V77 expected JSON object")
    return value


def imported(name: str, source: Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("V77 reviewed dependency unavailable or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V77 dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_blob(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V77 pinned source missing or unsafe")
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError("V77 Git blob calculation failed")
    return proc.stdout.strip()


def verify_dependency_blobs() -> None:
    for relative, expected in DEPENDENCY_BLOBS.items():
        if git_blob(ROOT / relative) != expected:
            raise RuntimeError("V77 frozen dependency blob mismatch")


def verify_start_receipt() -> None:
    receipt = read_json(V77_START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V77"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/8"
        and receipt.get("source_commit")
        == "2bdce4c378cef45d22b164a99b6b3e191e104965"
    ):
        raise RuntimeError("V77 official START receipt absent or invalid")


def verify_v76_report() -> dict:
    verify_dependency_blobs()
    report = read_json(V76_REPORT)
    metrics = report.get("metrics")
    expected = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V76_PASS": 1,
        "V76_BLIND_ACCESS": 0,
        "V76_VAL_LEXICAL": VAL_LEXICAL,
        "V76_HIDDEN_DIM": MODEL_DIM,
        "V76_FIT_VOCAB": VOCAB,
        "V76_PC1_CORRECT": 2457,
        "V76_PC1_DISTINCT": 2,
        "V76_PC1_TOP1_SHARE_BP": 7043,
        "V76_UNIGRAM_CORRECT": 2535,
        "V76_AXIS_FREQ_CORR_ABS_BP": 2785,
        "V76_AXIS_FREQ_R2_BP": 775,
        "V76_FREQ_COMPONENT_CORRECT": 2451,
        "V76_FREQ_COMPONENT_DISTINCT": 2,
        "V76_FREQ_COMPONENT_TOP1_SHARE_BP": 7043,
        "V76_FREQ_RESIDUAL_CORRECT": 2594,
        "V76_FREQ_RESIDUAL_DISTINCT": 2,
        "V76_FREQ_RESIDUAL_TOP1_SHARE_BP": 7043,
        "V76_RESIDUAL_UNIGRAM_AGREE": 6458,
        "V76_RESIDUAL_UNIGRAM_SHARED_CORRECT": 2451,
        "V76_PC1_VAR_SHARE_BP": 9019,
        "V76_TRAIN_VAL_PC1_COS_ABS_BP": 9995,
        "V76_RESIDUAL_ENERGY_SHARE_BP": 9225,
        "V76_COVERAGE_BP": 10000,
    }
    if not (
        report.get("step_id")
        == "PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
        and all(metrics.get(k) == v for k, v in expected.items())
    ):
        raise RuntimeError("V77 frozen V76 report integrity gate failed")
    return metrics


def reverse_history_keep_last(prefix) -> tuple[int, ...]:
    values = tuple(prefix)
    if not values or any(type(x) is not int for x in values):
        raise ValueError("V77 invalid prefix")
    if values[0] != T.BOS_ID:
        raise ValueError("V77 prefix must begin with BOS")
    if any(not 0 <= x < VOCAB for x in values):
        raise ValueError("V77 prefix token out of range")
    if T.PAD_ID in values:
        raise ValueError("V77 real prefix may not contain PAD")

    if len(values) < 3:
        transformed = values
    else:
        transformed = (values[0], *reversed(values[1:-1]), values[-1])

    if not (
        len(transformed) == len(values)
        and transformed[0] == values[0] == T.BOS_ID
        and transformed[-1] == values[-1]
        and Counter(transformed) == Counter(values)
        and Counter(
            x for x in transformed[1:-1]
            if x in {T.PAD_ID, T.BOS_ID, T.EOS_ID}
        )
        == Counter(
            x for x in values[1:-1]
            if x in {T.PAD_ID, T.BOS_ID, T.EOS_ID}
        )
    ):
        raise RuntimeError("V77 prefix perturbation invariant failed")
    return transformed


def sign_classes(values: torch.Tensor) -> torch.Tensor:
    x = values.detach().to(device="cpu", dtype=torch.float64)
    if x.ndim != 1 or x.numel() == 0 or not torch.isfinite(x).all():
        raise ValueError("V77 invalid alpha vector")
    return torch.sign(x).to(dtype=torch.int8)


def empty_outcome() -> dict:
    return {
        "CORRECT": 0,
        "HIST": torch.zeros(VOCAB, dtype=torch.long),
        "UNIGRAM_AGREE": 0,
        "UNIGRAM_SHARED_CORRECT": 0,
    }


def update_outcome(
    outcome: dict,
    predicted: torch.Tensor,
    gold: torch.Tensor,
    unigram: int,
) -> None:
    pred = predicted.detach().to(device="cpu", dtype=torch.long)
    target = gold.detach().to(device="cpu", dtype=torch.long)
    if (
        pred.ndim != 1
        or target.shape != pred.shape
        or pred.numel() == 0
        or not 3 <= unigram < VOCAB
    ):
        raise ValueError("V77 outcome shape or unigram invalid")
    if not (
        pred.ge(0).all()
        and pred.lt(VOCAB).all()
        and target.ge(3).all()
        and target.lt(VOCAB).all()
    ):
        raise RuntimeError("V77 outcome token range failed")

    uni = torch.full_like(target, unigram)
    outcome["CORRECT"] += int(pred.eq(target).sum())
    outcome["HIST"] += torch.bincount(pred, minlength=VOCAB)
    outcome["UNIGRAM_AGREE"] += int(pred.eq(uni).sum())
    outcome["UNIGRAM_SHARED_CORRECT"] += int(
        (pred.eq(target) & uni.eq(target)).sum()
    )


def finalize_outcome(outcome: dict, expected: int) -> dict:
    hist = outcome.get("HIST")
    if not (
        type(expected) is int
        and expected > 0
        and isinstance(hist, torch.Tensor)
        and hist.shape == (VOCAB,)
        and int(hist.sum()) == expected
        and type(outcome.get("CORRECT")) is int
        and type(outcome.get("UNIGRAM_AGREE")) is int
        and type(outcome.get("UNIGRAM_SHARED_CORRECT")) is int
    ):
        raise RuntimeError("V77 aggregate histogram/accounting failed")

    correct = outcome["CORRECT"]
    agree = outcome["UNIGRAM_AGREE"]
    shared = outcome["UNIGRAM_SHARED_CORRECT"]
    if not (
        0 <= correct <= expected
        and 0 <= agree <= expected
        and 0 <= shared <= min(correct, agree)
    ):
        raise RuntimeError("V77 outcome accounting range failed")
    return {
        "CORRECT": correct,
        "DISTINCT": int(hist.gt(0).sum()),
        "TOP1_SHARE_BP": round(int(hist.max()) * 10000 / expected),
        "UNIGRAM_AGREE": agree,
        "UNIGRAM_SHARED_CORRECT": shared,
    }


def empty_pair_stats() -> dict:
    return {
        "COUNT": 0,
        "SUM_X": 0.0,
        "SUM_Y": 0.0,
        "SUM_X2": 0.0,
        "SUM_Y2": 0.0,
        "SUM_XY": 0.0,
        "PRED_AGREE": 0,
        "PRED_CHANGED": 0,
        "SHARED_CORRECT": 0,
        "FULL_ONLY_CORRECT": 0,
        "REVERSE_ONLY_CORRECT": 0,
        "SIGN_AGREE": 0,
        "SIGN_CHANGED": 0,
        "ALPHA_DELTA_NONZERO": 0,
        "PERTURBED_PREFIXES": 0,
        "UNCHANGED_PREFIXES": 0,
    }


def update_pair_stats(
    stats: dict,
    alpha_full: torch.Tensor,
    alpha_reverse: torch.Tensor,
    pred_full: torch.Tensor,
    pred_reverse: torch.Tensor,
    gold: torch.Tensor,
    changed_prefix: torch.Tensor,
) -> None:
    x = alpha_full.detach().to(device="cpu", dtype=torch.float64)
    y = alpha_reverse.detach().to(device="cpu", dtype=torch.float64)
    pf = pred_full.detach().to(device="cpu", dtype=torch.long)
    pr = pred_reverse.detach().to(device="cpu", dtype=torch.long)
    target = gold.detach().to(device="cpu", dtype=torch.long)
    changed = changed_prefix.detach().to(device="cpu", dtype=torch.bool)

    if not (
        x.ndim == 1
        and x.shape == y.shape == pf.shape == pr.shape == target.shape == changed.shape
        and x.numel() > 0
        and torch.isfinite(x).all()
        and torch.isfinite(y).all()
    ):
        raise ValueError("V77 invalid paired accounting input")

    n = int(x.numel())
    sf = sign_classes(x)
    sr = sign_classes(y)
    full_correct = pf.eq(target)
    reverse_correct = pr.eq(target)
    pred_same = pf.eq(pr)
    sign_same = sf.eq(sr)

    stats["COUNT"] += n
    stats["SUM_X"] += float(x.sum())
    stats["SUM_Y"] += float(y.sum())
    stats["SUM_X2"] += float(torch.dot(x, x))
    stats["SUM_Y2"] += float(torch.dot(y, y))
    stats["SUM_XY"] += float(torch.dot(x, y))
    stats["PRED_AGREE"] += int(pred_same.sum())
    stats["PRED_CHANGED"] += int((~pred_same).sum())
    stats["SHARED_CORRECT"] += int((full_correct & reverse_correct).sum())
    stats["FULL_ONLY_CORRECT"] += int((full_correct & ~reverse_correct).sum())
    stats["REVERSE_ONLY_CORRECT"] += int((~full_correct & reverse_correct).sum())
    stats["SIGN_AGREE"] += int(sign_same.sum())
    stats["SIGN_CHANGED"] += int((~sign_same).sum())
    stats["ALPHA_DELTA_NONZERO"] += int(
        (torch.abs(x - y) > ALPHA_DELTA_THRESHOLD).sum()
    )
    stats["PERTURBED_PREFIXES"] += int(changed.sum())
    stats["UNCHANGED_PREFIXES"] += int((~changed).sum())


def finalize_pair_stats(stats: dict, expected: int) -> dict:
    n = stats.get("COUNT")
    if type(n) is not int or n != expected or n <= 1:
        raise RuntimeError("V77 paired coverage failed")
    for key in (
        "SUM_X", "SUM_Y", "SUM_X2", "SUM_Y2", "SUM_XY"
    ):
        if not math.isfinite(stats[key]):
            raise RuntimeError("V77 nonfinite paired statistic")

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
        raise RuntimeError("V77 degenerate alpha correlation")
    corr_abs = abs(cov_num) / math.sqrt(var_x * var_y)
    if not math.isfinite(corr_abs) or not 0.0 <= corr_abs <= 1.0000001:
        raise RuntimeError("V77 invalid alpha correlation")
    corr_abs = min(corr_abs, 1.0)

    integer_pairs = (
        ("PRED_AGREE", "PRED_CHANGED"),
        ("SIGN_AGREE", "SIGN_CHANGED"),
        ("PERTURBED_PREFIXES", "UNCHANGED_PREFIXES"),
    )
    for left, right in integer_pairs:
        if stats[left] + stats[right] != expected:
            raise RuntimeError("V77 paired partition accounting failed")

    if not (
        0 <= stats["SHARED_CORRECT"] <= expected
        and 0 <= stats["FULL_ONLY_CORRECT"] <= expected
        and 0 <= stats["REVERSE_ONLY_CORRECT"] <= expected
        and 0 <= stats["ALPHA_DELTA_NONZERO"] <= expected
        and stats["PERTURBED_PREFIXES"] > 0
    ):
        raise RuntimeError("V77 paired result outside admissible range")

    return {
        **{
            k: stats[k]
            for k in (
                "PRED_AGREE",
                "PRED_CHANGED",
                "SHARED_CORRECT",
                "FULL_ONLY_CORRECT",
                "REVERSE_ONLY_CORRECT",
                "SIGN_AGREE",
                "SIGN_CHANGED",
                "ALPHA_DELTA_NONZERO",
                "PERTURBED_PREFIXES",
                "UNCHANGED_PREFIXES",
            )
        },
        "ALPHA_CORR_ABS_BP": round(corr_abs * 10000),
    }


def _forward_hidden(model, ids: torch.Tensor, taps: list) -> torch.Tensor:
    if ids.ndim != 2 or ids.numel() == 0:
        raise ValueError("V77 invalid inference batch")
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        model(ids)
    if len(taps) != 1 or taps[0].shape[:2] != ids.shape:
        raise RuntimeError("V77 hidden-state pre-hook mismatch")
    hidden = taps.pop().float()
    if not torch.isfinite(hidden).all():
        raise RuntimeError("V77 nonfinite hidden state")
    return hidden


def score_validation(
    model,
    device,
    validation: list,
    train_mean: torch.Tensor,
    train_pc1: torch.Tensor,
    residual_profile: torch.Tensor,
    unigram: int,
):
    if len(validation) != 36:
        raise RuntimeError("V77 frozen VALIDATION segment count changed")
    if not (
        train_mean.shape == train_pc1.shape == (MODEL_DIM,)
        and residual_profile.shape == (VOCAB,)
        and torch.isfinite(residual_profile).all()
        and 3 <= unigram < VOCAB
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr() == model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V77 scoring geometry/output-head gate failed")

    mean_t = train_mean.to(device=device, dtype=torch.float32)
    pc1_t = train_pc1.to(device=device, dtype=torch.float32)
    residual_t = residual_profile.to(device=device, dtype=torch.float32)

    outcomes = {
        "FULL": empty_outcome(),
        "REVERSE": empty_outcome(),
    }
    pairs = empty_pair_stats()
    lexical_total = 0
    taps = []

    def capture(_module, inputs):
        if len(inputs) != 1 or inputs[0].ndim != 3 or inputs[0].shape[-1] != MODEL_DIM:
            raise RuntimeError("V77 output-head hidden state shape changed")
        taps.append(inputs[0].detach())

    handle = model.lm_head.register_forward_pre_hook(capture)
    model.eval()
    try:
        with torch.inference_mode():
            for start in range(0, len(validation), VAL_BATCH):
                group = validation[start : start + VAL_BATCH]
                ids = torch.full(
                    (len(group), max(len(seg.token_ids) for seg in group)),
                    T.PAD_ID,
                    dtype=torch.long,
                    device=device,
                )
                for row, seg in enumerate(group):
                    tokens = tuple(seg.token_ids)
                    if (
                        not tokens
                        or tokens[0] != T.BOS_ID
                        or tokens[-1] != T.EOS_ID
                    ):
                        raise RuntimeError("V77 VALIDATION boundary changed")
                    ids[row, : len(tokens)] = torch.as_tensor(
                        tokens, dtype=torch.long, device=device
                    )

                hidden = _forward_hidden(model, ids, taps)
                jobs_prefix = []
                jobs_gold = []
                jobs_alpha_full = []

                for row, seg in enumerate(group):
                    tokens = tuple(seg.token_ids)
                    row_hidden = hidden[row]
                    for target_index in range(1, len(tokens)):
                        target = tokens[target_index]
                        if not 3 <= target < VOCAB:
                            continue
                        prefix = tokens[:target_index]
                        if not prefix or prefix[-1] != tokens[target_index - 1]:
                            raise RuntimeError("V77 prefix/target alignment failed")
                        alpha = torch.dot(
                            row_hidden[target_index - 1] - mean_t,
                            pc1_t,
                        )
                        if not torch.isfinite(alpha):
                            raise RuntimeError("V77 nonfinite FULL alpha")
                        jobs_prefix.append(prefix)
                        jobs_gold.append(target)
                        jobs_alpha_full.append(alpha)

                del hidden, ids

                if not jobs_prefix:
                    raise RuntimeError("V77 empty VALIDATION group")
                full_alpha = torch.stack(jobs_alpha_full)
                gold_all = torch.as_tensor(
                    jobs_gold,
                    dtype=torch.long,
                    device=device,
                )
                if full_alpha.numel() == 0 or full_alpha.shape != gold_all.shape:
                    raise RuntimeError("V77 FULL paired shape mismatch")

                lexical_total += int(gold_all.numel())

                for offset in range(0, len(jobs_prefix), COUNTERFACTUAL_BATCH):
                    stop = min(offset + COUNTERFACTUAL_BATCH, len(jobs_prefix))
                    original = jobs_prefix[offset:stop]
                    transformed = [
                        reverse_history_keep_last(prefix)
                        for prefix in original
                    ]
                    changed = torch.as_tensor(
                        [a != b for a, b in zip(original, transformed)],
                        dtype=torch.bool,
                    )

                    max_len = max(len(prefix) for prefix in transformed)
                    cf_ids = torch.full(
                        (len(transformed), max_len),
                        T.PAD_ID,
                        dtype=torch.long,
                        device=device,
                    )
                    for row, prefix in enumerate(transformed):
                        cf_ids[row, : len(prefix)] = torch.as_tensor(
                            prefix,
                            dtype=torch.long,
                            device=device,
                        )

                    cf_hidden = _forward_hidden(model, cf_ids, taps)
                    rows = torch.arange(
                        len(transformed),
                        device=device,
                        dtype=torch.long,
                    )
                    last = torch.as_tensor(
                        [len(prefix) - 1 for prefix in transformed],
                        device=device,
                        dtype=torch.long,
                    )
                    selected = cf_hidden[rows, last]
                    alpha_reverse = (selected - mean_t) @ pc1_t
                    if not torch.isfinite(alpha_reverse).all():
                        raise RuntimeError("V77 nonfinite REVERSE alpha")

                    alpha_full = full_alpha[offset:stop]
                    gold = gold_all[offset:stop]

                    logits_full = alpha_full.unsqueeze(1) * residual_t.unsqueeze(0)
                    logits_reverse = (
                        alpha_reverse.unsqueeze(1) * residual_t.unsqueeze(0)
                    )
                    if not (
                        torch.isfinite(logits_full).all()
                        and torch.isfinite(logits_reverse).all()
                    ):
                        raise RuntimeError("V77 nonfinite residual logits")

                    pred_full = logits_full.argmax(1)
                    pred_reverse = logits_reverse.argmax(1)
                    update_outcome(outcomes["FULL"], pred_full, gold, unigram)
                    update_outcome(
                        outcomes["REVERSE"],
                        pred_reverse,
                        gold,
                        unigram,
                    )
                    update_pair_stats(
                        pairs,
                        alpha_full,
                        alpha_reverse,
                        pred_full,
                        pred_reverse,
                        gold,
                        changed,
                    )

                    del (
                        cf_ids,
                        cf_hidden,
                        selected,
                        alpha_reverse,
                        logits_full,
                        logits_reverse,
                        pred_full,
                        pred_reverse,
                    )

                del full_alpha, gold_all, jobs_alpha_full, jobs_gold, jobs_prefix
    finally:
        handle.remove()
        taps.clear()

    if lexical_total != VAL_LEXICAL:
        raise RuntimeError("V77 validation lexical coverage changed")

    return (
        {
            mode: finalize_outcome(value, VAL_LEXICAL)
            for mode, value in outcomes.items()
        },
        finalize_pair_stats(pairs, VAL_LEXICAL),
    )


def build_metrics(outcomes: dict, pairs: dict) -> dict:
    if set(outcomes) != {"FULL", "REVERSE"}:
        raise RuntimeError("V77 scoring modes incomplete")

    full = outcomes["FULL"]
    reverse = outcomes["REVERSE"]
    expected_full = {
        "CORRECT": 2594,
        "DISTINCT": 2,
        "TOP1_SHARE_BP": 7043,
        "UNIGRAM_AGREE": 6458,
        "UNIGRAM_SHARED_CORRECT": 2451,
    }
    if full != expected_full:
        raise RuntimeError("V77 frozen V76 residual replay failed")

    for item in (full, reverse):
        if not (
            0 <= item["CORRECT"] <= VAL_LEXICAL
            and 1 <= item["DISTINCT"] <= VOCAB
            and 0 <= item["TOP1_SHARE_BP"] <= 10000
            and 0 <= item["UNIGRAM_AGREE"] <= VAL_LEXICAL
            and 0 <= item["UNIGRAM_SHARED_CORRECT"]
            <= min(item["CORRECT"], item["UNIGRAM_AGREE"])
        ):
            raise RuntimeError("V77 invalid aggregate scoring result")

    if not (
        pairs["PRED_AGREE"] + pairs["PRED_CHANGED"] == VAL_LEXICAL
        and pairs["SIGN_AGREE"] + pairs["SIGN_CHANGED"] == VAL_LEXICAL
        and pairs["PERTURBED_PREFIXES"] + pairs["UNCHANGED_PREFIXES"]
        == VAL_LEXICAL
        and pairs["SHARED_CORRECT"]
        + pairs["FULL_ONLY_CORRECT"] == full["CORRECT"]
        and pairs["SHARED_CORRECT"]
        + pairs["REVERSE_ONLY_CORRECT"] == reverse["CORRECT"]
        and 0 <= pairs["ALPHA_CORR_ABS_BP"] <= 10000
    ):
        raise RuntimeError("V77 paired correctness partition failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V77_PASS": 1,
        "V77_BLIND_ACCESS": 0,
        "V77_VAL_LEXICAL": VAL_LEXICAL,
        "V77_HIDDEN_DIM": MODEL_DIM,
        "V77_VOCAB": VOCAB,
        "V77_FULL_CORRECT": full["CORRECT"],
        "V77_FULL_DISTINCT": full["DISTINCT"],
        "V77_FULL_TOP1_SHARE_BP": full["TOP1_SHARE_BP"],
        "V77_FULL_UNIGRAM_AGREE": full["UNIGRAM_AGREE"],
        "V77_FULL_UNIGRAM_SHARED_CORRECT": full["UNIGRAM_SHARED_CORRECT"],
        "V77_REVERSE_CORRECT": reverse["CORRECT"],
        "V77_REVERSE_DISTINCT": reverse["DISTINCT"],
        "V77_REVERSE_TOP1_SHARE_BP": reverse["TOP1_SHARE_BP"],
        "V77_REVERSE_UNIGRAM_AGREE": reverse["UNIGRAM_AGREE"],
        "V77_REVERSE_UNIGRAM_SHARED_CORRECT":
            reverse["UNIGRAM_SHARED_CORRECT"],
        "V77_PRED_AGREE": pairs["PRED_AGREE"],
        "V77_PRED_CHANGED": pairs["PRED_CHANGED"],
        "V77_FULL_REVERSE_SHARED_CORRECT": pairs["SHARED_CORRECT"],
        "V77_FULL_ONLY_CORRECT": pairs["FULL_ONLY_CORRECT"],
        "V77_REVERSE_ONLY_CORRECT": pairs["REVERSE_ONLY_CORRECT"],
        "V77_ALPHA_SIGN_AGREE": pairs["SIGN_AGREE"],
        "V77_ALPHA_SIGN_CHANGED": pairs["SIGN_CHANGED"],
        "V77_ALPHA_CORR_ABS_BP": pairs["ALPHA_CORR_ABS_BP"],
        "V77_ALPHA_DELTA_NONZERO": pairs["ALPHA_DELTA_NONZERO"],
        "V77_PERTURBED_PREFIXES": pairs["PERTURBED_PREFIXES"],
        "V77_UNCHANGED_PREFIXES": pairs["UNCHANGED_PREFIXES"],
        "V77_COVERAGE_BP": 10000,
    }
    if not (
        tuple(metrics) == METRIC_FIELDS
        and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
    ):
        raise RuntimeError("V77 strict 30-integer metric schema failed")
    return metrics


def compute():
    torch.set_grad_enabled(False)
    verify_start_receipt()
    v76_metrics = verify_v76_report()

    v76 = imported("v77_frozen_v76_control", V76_SOURCE)
    v75 = imported("v77_frozen_v75_geometry", V75_SOURCE)
    v65 = imported("v77_frozen_v65_frequency", V65_SOURCE)
    v64 = v75.imported("v77_v64_preflight", v75.V64)

    model, device, streams, validation = v64.preflight()
    if device.type != "cuda":
        raise RuntimeError("V77 requires reviewed CUDA inference path")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("V77 requires CUDA BF16 support")
    if not (
        v76.VAL_BATCH == VAL_BATCH
        and v76.SCORE_CHUNK == SCORE_CHUNK
        and v76.GPU_PEAK_LIMIT_MIB == GPU_PEAK_LIMIT_MIB
    ):
        raise RuntimeError("V77 inherited runtime constants changed")

    frequency = v65.count_training_tokens(streams)
    v76.frequency_count_vector(frequency, require_frozen=True)
    unigram = v75.most_frequent(frequency)
    if v76_metrics["V76_UNIGRAM_CORRECT"] != 2535:
        raise RuntimeError("V77 frozen unigram provenance changed")

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
        raise RuntimeError("V77 frozen TRAIN PC1 variance replay failed")

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
        raise RuntimeError("V77 frozen V76 residual decomposition replay failed")

    outcomes, pairs = score_validation(
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
        raise RuntimeError("V77 GPU peak-memory gate exceeded")
    return metrics, peak_mib


def main():
    metrics, _peak_mib = compute()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
