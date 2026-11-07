#!/usr/bin/env python3
"""V76 read-only frequency-residualized TRAIN-PC1 output control.

Reuses the frozen V75 streaming geometry and the V65 TRAIN lexical-frequency
definition. Calibration is TRAIN-only. VALIDATION scoring is aggregate-only.
No optimizer, training, BLIND access, checkpoint write, raw token text,
per-position predictions or hidden-state persistence is permitted.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mini_kuzai import phase03_v62_trainer as T

STEP_ID = "PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001"

TRAIN_BATCH = 2
VAL_BATCH = 4
SCORE_CHUNK = 512
GPU_PEAK_LIMIT_MIB = 6144
TRAIN_LEXICAL = 294726
TRAIN_TYPES = 891
VAL_LEXICAL = 9170
MODEL_DIM = 128
VOCAB = 1024

DECOMP_ATOL = 1e-12
ORTHO_RTOL = 1e-10
IDENTITY_TOL = 1e-10

V75_SOURCE = ROOT / "tools" / "v75_train_fitted_geometry_transfer.py"
V65_SOURCE = ROOT / "tools" / "public-audits" / "phase03_v65_token_frequency_diagnostic_001.py"
V75_REPORT = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json"
)
V74_CORE_REPORT = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001.json"
)
V74_STRATA_REPORT = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001.json"
)
V76_START_RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V76-start.json"

DEPENDENCY_BLOBS = {
    "tools/v75_train_fitted_geometry_transfer.py":
        "8705d8ca9aebe7281779c704119d26eb82517da2",
    "tools/public-audits/phase03_v65_token_frequency_diagnostic_001.py":
        "d88e05933686b369d5236c3bcd465729e2df3407",
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json":
        "51606f42f60c5e53c437cac0be9bc6459fadbd05",
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001.json":
        "8cf575c440d7625bd03d6ce1d77c3951c678f84a",
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001.json":
        "5096c81e32b6140f926930a09e0b6253fa557c01",
}

METRIC_FIELDS = (
    "SEMANTIC_VALIDATION_COMPLETE",
    "TRAINING_AUTHORIZED",
    "TRAINING_STARTED",
    "V76_PASS",
    "V76_BLIND_ACCESS",
    "V76_TRAIN_LEXICAL",
    "V76_TRAIN_TYPES",
    "V76_VAL_LEXICAL",
    "V76_HIDDEN_DIM",
    "V76_FIT_VOCAB",
    "V76_PC1_CORRECT",
    "V76_PC1_DISTINCT",
    "V76_PC1_TOP1_SHARE_BP",
    "V76_UNIGRAM_CORRECT",
    "V76_AXIS_FREQ_CORR_ABS_BP",
    "V76_AXIS_FREQ_R2_BP",
    "V76_FREQ_COMPONENT_CORRECT",
    "V76_FREQ_COMPONENT_DISTINCT",
    "V76_FREQ_COMPONENT_TOP1_SHARE_BP",
    "V76_FREQ_RESIDUAL_CORRECT",
    "V76_FREQ_RESIDUAL_DISTINCT",
    "V76_FREQ_RESIDUAL_TOP1_SHARE_BP",
    "V76_RESIDUAL_UNIGRAM_AGREE",
    "V76_RESIDUAL_UNIGRAM_SHARED_CORRECT",
    "V76_PC1_FREQ_COMPONENT_AGREE",
    "V76_FREQ_COMPONENT_UNIGRAM_AGREE",
    "V76_PC1_VAR_SHARE_BP",
    "V76_TRAIN_VAL_PC1_COS_ABS_BP",
    "V76_RESIDUAL_ENERGY_SHARE_BP",
    "V76_COVERAGE_BP",
)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V76 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V76 expected JSON object")
    return value


def imported(name: str, source: Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("V76 reviewed dependency unavailable or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V76 dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_blob(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V76 pinned source missing or unsafe")
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError("V76 Git blob calculation failed")
    return proc.stdout.strip()


def verify_dependency_blobs() -> None:
    for relative, expected in DEPENDENCY_BLOBS.items():
        path = ROOT / relative
        if git_blob(path) != expected:
            raise RuntimeError("V76 frozen dependency blob mismatch")


def verify_start_receipt() -> None:
    receipt = read_json(V76_START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V76"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/7"
        and receipt.get("source_commit")
        == "368710f58b92876aa2b3b3f1ec196610bd876da1"
    ):
        raise RuntimeError("V76 official START receipt absent or invalid")


def _report_metrics(path: Path, step: str) -> dict:
    report = read_json(path)
    metrics = report.get("metrics")
    if not (
        report.get("step_id") == step
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
    ):
        raise RuntimeError("V76 frozen report integrity gate failed")
    return metrics


def verify_frozen_reports() -> dict:
    verify_dependency_blobs()
    v75 = _report_metrics(
        V75_REPORT,
        "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001",
    )
    v74_core = _report_metrics(
        V74_CORE_REPORT,
        "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001",
    )
    v74_strata = _report_metrics(
        V74_STRATA_REPORT,
        "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001",
    )
    expected_v75 = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V75_PASS": 1,
        "V75_BLIND_ACCESS": 0,
        "V75_TRAIN_LEXICAL": TRAIN_LEXICAL,
        "V75_TRAIN_TYPES": TRAIN_TYPES,
        "V75_VAL_LEXICAL": VAL_LEXICAL,
        "V75_HIDDEN_DIM": MODEL_DIM,
        "V75_TRAIN_PC1_CORRECT": 2457,
        "V75_TRAIN_PC1_DISTINCT": 2,
        "V75_TRAIN_PC1_TOP1_SHARE_BP": 7043,
        "V75_UNIGRAM_CORRECT": 2535,
        "V75_TRAIN_VAL_PC1_COS_ABS_BP": 9995,
        "V75_TRAIN_PC1_VAR_SHARE_BP": 9019,
        "V75_COVERAGE_BP": 10000,
    }
    expected_core = {
        "V74_CORE_PASS": 1,
        "V74_CORE_BLIND_ACCESS": 0,
        "V74_CORE_VAL_LEXICAL": VAL_LEXICAL,
        "V74_CORE_UNIGRAM_CORRECT": 2535,
    }
    expected_strata = {
        "V74_STRATA_PASS": 1,
        "V74_STRATA_BLIND_ACCESS": 0,
        "V74_STRATA_TRAIN_LEXICAL": TRAIN_LEXICAL,
        "V74_STRATA_TRAIN_TYPES": TRAIN_TYPES,
        "V74_STRATA_VAL_LEXICAL": VAL_LEXICAL,
    }
    if not (
        all(v75.get(k) == v for k, v in expected_v75.items())
        and all(v74_core.get(k) == v for k, v in expected_core.items())
        and all(v74_strata.get(k) == v for k, v in expected_strata.items())
    ):
        raise RuntimeError("V76 frozen V74/V75 metric replay gate failed")
    return {"V75": v75, "V74_CORE": v74_core, "V74_STRATA": v74_strata}


def frequency_count_vector(
    frequency: Counter,
    *,
    require_frozen: bool = False,
) -> torch.Tensor:
    if not isinstance(frequency, Counter) or not frequency:
        raise ValueError("V76 invalid TRAIN frequency inventory")
    vector = torch.zeros(VOCAB, dtype=torch.float64)
    for token, count in frequency.items():
        if (
            type(token) is not int
            or not 3 <= token < VOCAB
            or type(count) is not int
            or count <= 0
        ):
            raise ValueError("V76 invalid lexical frequency entry")
        vector[token] = count
    if require_frozen and (
        int(vector.sum().item()) != TRAIN_LEXICAL
        or int(vector.gt(0).sum().item()) != TRAIN_TYPES
    ):
        raise RuntimeError("V76 frozen TRAIN lexical frequency inventory changed")
    if not torch.isfinite(vector).all():
        raise RuntimeError("V76 nonfinite frequency vector")
    return vector


def centered_log_frequency(
    frequency: Counter,
    *,
    require_frozen: bool = False,
) -> tuple[torch.Tensor, torch.Tensor]:
    counts = frequency_count_vector(frequency, require_frozen=require_frozen)
    transformed = torch.log1p(counts)
    centered = transformed - transformed.mean()
    if (
        transformed.shape != (VOCAB,)
        or centered.shape != (VOCAB,)
        or not torch.isfinite(transformed).all()
        or not torch.isfinite(centered).all()
        or float(torch.linalg.vector_norm(centered)) <= 0.0
    ):
        raise RuntimeError("V76 degenerate centered log-frequency")
    return transformed, centered


def centered_ols(q: torch.Tensor, g: torch.Tensor) -> dict:
    q64 = q.detach().to(device="cpu", dtype=torch.float64)
    g64 = g.detach().to(device="cpu", dtype=torch.float64)
    if q64.shape != (VOCAB,) or g64.shape != (VOCAB,):
        raise ValueError("V76 OLS vector shape mismatch")
    if not (torch.isfinite(q64).all() and torch.isfinite(g64).all()):
        raise RuntimeError("V76 nonfinite OLS input")
    q_norm = float(torch.linalg.vector_norm(q64))
    g_norm = float(torch.linalg.vector_norm(g64))
    if not math.isfinite(q_norm) or not math.isfinite(g_norm) or q_norm <= 0 or g_norm <= 0:
        raise RuntimeError("V76 degenerate OLS input")

    gg = float(torch.dot(g64, g64))
    gq = float(torch.dot(g64, q64))
    if not math.isfinite(gg) or not math.isfinite(gq) or gg <= 0:
        raise RuntimeError("V76 invalid OLS denominator")
    beta = gq / gg
    component = beta * g64
    residual = q64 - component
    if not (
        math.isfinite(beta)
        and torch.isfinite(component).all()
        and torch.isfinite(residual).all()
    ):
        raise RuntimeError("V76 nonfinite OLS decomposition")

    decomposition_error = float(torch.max(torch.abs(q64 - component - residual)))
    if not math.isfinite(decomposition_error) or decomposition_error > DECOMP_ATOL:
        raise RuntimeError("V76 centered decomposition identity failed")

    residual_norm = float(torch.linalg.vector_norm(residual))
    orthogonal = abs(float(torch.dot(g64, residual)))
    ortho_scale = g_norm * residual_norm
    if ortho_scale == 0.0:
        if orthogonal > DECOMP_ATOL:
            raise RuntimeError("V76 zero-residual orthogonality failed")
    elif orthogonal / ortho_scale > ORTHO_RTOL:
        raise RuntimeError("V76 residual orthogonality failed")

    corr_abs = abs(gq) / (g_norm * q_norm)
    residual_energy = (residual_norm * residual_norm) / (q_norm * q_norm)
    r2 = 1.0 - residual_energy

    for value in (corr_abs, residual_energy, r2):
        if not math.isfinite(value):
            raise RuntimeError("V76 nonfinite OLS statistic")
    if not (
        -IDENTITY_TOL <= r2 <= 1.0 + IDENTITY_TOL
        and -IDENTITY_TOL <= residual_energy <= 1.0 + IDENTITY_TOL
        and 0.0 <= corr_abs <= 1.0 + IDENTITY_TOL
    ):
        raise RuntimeError("V76 OLS statistic outside admissible range")

    corr_abs = min(max(corr_abs, 0.0), 1.0)
    r2 = min(max(r2, 0.0), 1.0)
    residual_energy = min(max(residual_energy, 0.0), 1.0)
    if abs(r2 - corr_abs * corr_abs) > IDENTITY_TOL:
        raise RuntimeError("V76 Pearson/R2 identity failed")

    return {
        "BETA": beta,
        "COMPONENT": component,
        "RESIDUAL": residual,
        "CORR_ABS": corr_abs,
        "R2": r2,
        "RESIDUAL_ENERGY": residual_energy,
        "DECOMPOSITION_ERROR": decomposition_error,
    }


def decompose_output_profile(
    output_weights: torch.Tensor,
    pc1: torch.Tensor,
    frequency: Counter,
    *,
    require_frozen: bool = False,
) -> dict:
    weights = output_weights.detach().to(device="cpu", dtype=torch.float64)
    axis = pc1.detach().to(device="cpu", dtype=torch.float64)
    if weights.shape != (VOCAB, MODEL_DIM) or axis.shape != (MODEL_DIM,):
        raise ValueError("V76 output-profile shape mismatch")
    if not (torch.isfinite(weights).all() and torch.isfinite(axis).all()):
        raise RuntimeError("V76 nonfinite output profile input")
    axis_norm = float(torch.linalg.vector_norm(axis))
    if not math.isfinite(axis_norm) or axis_norm <= 0:
        raise RuntimeError("V76 degenerate PC1 axis")

    raw = weights @ axis
    q = raw - raw.mean()
    _f, g = centered_log_frequency(
        frequency,
        require_frozen=require_frozen,
    )
    if not torch.isfinite(q).all() or float(torch.linalg.vector_norm(q)) <= 0:
        raise RuntimeError("V76 degenerate centered PC1 output profile")
    fit = centered_ols(q, g)
    return {
        "RAW": raw,
        "Q": q,
        "G": g,
        **fit,
    }


def constant_offset_argmax_equal(
    alpha: torch.Tensor,
    raw: torch.Tensor,
    centered: torch.Tensor,
) -> bool:
    a = alpha.detach().to(device="cpu", dtype=torch.float64).reshape(-1, 1)
    raw64 = raw.detach().to(device="cpu", dtype=torch.float64)
    centered64 = centered.detach().to(device="cpu", dtype=torch.float64)
    if raw64.shape != (VOCAB,) or centered64.shape != (VOCAB,):
        raise ValueError("V76 constant-offset vector shape mismatch")
    if not (
        torch.isfinite(a).all()
        and torch.isfinite(raw64).all()
        and torch.isfinite(centered64).all()
    ):
        raise RuntimeError("V76 nonfinite constant-offset input")
    return torch.equal(
        (a * raw64.unsqueeze(0)).argmax(1),
        (a * centered64.unsqueeze(0)).argmax(1),
    )


def empty_outcome() -> dict:
    return {
        "CORRECT": 0,
        "HIST": torch.zeros(VOCAB, dtype=torch.long),
    }


def update_outcome(outcome: dict, predicted: torch.Tensor, gold: torch.Tensor) -> None:
    pred = predicted.detach().to(device="cpu", dtype=torch.long)
    target = gold.detach().to(device="cpu", dtype=torch.long)
    if pred.ndim != 1 or target.shape != pred.shape or pred.numel() == 0:
        raise ValueError("V76 prediction accounting shape mismatch")
    if not (
        pred.ge(0).all()
        and pred.lt(VOCAB).all()
        and target.ge(3).all()
        and target.lt(VOCAB).all()
    ):
        raise RuntimeError("V76 prediction accounting ID range failed")
    outcome["CORRECT"] += int(pred.eq(target).sum())
    outcome["HIST"] += torch.bincount(pred, minlength=VOCAB)


def finalize_outcome(outcome: dict, expected: int) -> dict:
    hist = outcome.get("HIST")
    correct = outcome.get("CORRECT")
    if (
        type(expected) is not int
        or expected <= 0
        or type(correct) is not int
        or not isinstance(hist, torch.Tensor)
        or hist.shape != (VOCAB,)
        or int(hist.sum()) != expected
        or not 0 <= correct <= expected
    ):
        raise RuntimeError("V76 aggregate histogram/accounting failed")
    return {
        "CORRECT": correct,
        "DISTINCT": int(hist.gt(0).sum()),
        "TOP1_SHARE_BP": round(int(hist.max()) * 10000 / expected),
    }


def score_validation(
    model,
    device,
    validation: list,
    train_mean: torch.Tensor,
    train_pc1: torch.Tensor,
    profiles: dict,
    unigram: int,
):
    if len(validation) != 36:
        raise RuntimeError("V76 frozen VALIDATION segment count changed")
    if not (
        train_mean.shape == train_pc1.shape == (MODEL_DIM,)
        and 3 <= unigram < VOCAB
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr() == model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V76 scoring geometry/output-head gate failed")
    required_profiles = {"RAW", "Q", "COMPONENT", "RESIDUAL"}
    if not required_profiles <= set(profiles):
        raise RuntimeError("V76 scoring profiles incomplete")

    mean_t = train_mean.to(device=device, dtype=torch.float32)
    pc1_t = train_pc1.to(device=device, dtype=torch.float32)
    raw_t = profiles["RAW"].to(device=device, dtype=torch.float32)
    q_t = profiles["Q"].to(device=device, dtype=torch.float32)
    c_t = profiles["COMPONENT"].to(device=device, dtype=torch.float32)
    r_t = profiles["RESIDUAL"].to(device=device, dtype=torch.float32)
    weights = model.lm_head.weight.detach().float()

    outcomes = {
        "PC1": empty_outcome(),
        "FREQ_COMPONENT": empty_outcome(),
        "FREQ_RESIDUAL": empty_outcome(),
    }
    residual_unigram_agree = 0
    residual_unigram_shared_correct = 0
    pc1_component_agree = 0
    component_unigram_agree = 0
    lexical_total = 0
    taps = []

    def capture(_module, inputs):
        if len(inputs) != 1 or inputs[0].ndim != 3 or inputs[0].shape[-1] != MODEL_DIM:
            raise RuntimeError("V76 validation hidden state shape changed")
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
                    if seg.token_ids[0] != T.BOS_ID or seg.token_ids[-1] != T.EOS_ID:
                        raise RuntimeError("V76 VALIDATION boundary changed")
                    ids[row, : len(seg.token_ids)] = torch.as_tensor(
                        seg.token_ids,
                        dtype=torch.long,
                        device=device,
                    )
                with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                    model(ids)
                if len(taps) != 1 or taps[0].shape[:2] != ids.shape:
                    raise RuntimeError("V76 validation pre-hook mismatch")
                hidden = taps.pop().float()[:, :-1, :]
                targets = ids[:, 1:]
                lexical = (
                    targets.ne(T.PAD_ID)
                    & targets.ge(3)
                    & targets.lt(VOCAB)
                )
                h = hidden[lexical]
                gold = targets[lexical]
                lexical_total += int(gold.numel())

                for offset in range(0, int(gold.numel()), SCORE_CHUNK):
                    stop = min(offset + SCORE_CHUNK, int(gold.numel()))
                    hv = h[offset:stop]
                    gv = gold[offset:stop]
                    alpha = (hv - mean_t) @ pc1_t
                    if not torch.isfinite(alpha).all():
                        raise RuntimeError("V76 nonfinite TRAIN-PC1 coefficient")

                    logits_raw = alpha.unsqueeze(1) * raw_t.unsqueeze(0)
                    logits_q = alpha.unsqueeze(1) * q_t.unsqueeze(0)
                    logits_c = alpha.unsqueeze(1) * c_t.unsqueeze(0)
                    logits_r = alpha.unsqueeze(1) * r_t.unsqueeze(0)
                    reference_component = alpha.unsqueeze(1) * pc1_t.unsqueeze(0)
                    logits_reference = F.linear(reference_component, weights)

                    if not all(
                        torch.isfinite(x).all()
                        for x in (
                            logits_raw,
                            logits_q,
                            logits_c,
                            logits_r,
                            logits_reference,
                        )
                    ):
                        raise RuntimeError("V76 nonfinite counterfactual logits")

                    pred_raw = logits_raw.argmax(1)
                    pred_q = logits_q.argmax(1)
                    pred_reference = logits_reference.argmax(1)
                    if not (
                        torch.equal(pred_raw, pred_q)
                        and torch.equal(pred_q, pred_reference)
                    ):
                        raise RuntimeError("V76 PC1 centered/replay argmax mismatch")

                    pred_c = logits_c.argmax(1)
                    pred_r = logits_r.argmax(1)
                    update_outcome(outcomes["PC1"], pred_q, gv)
                    update_outcome(outcomes["FREQ_COMPONENT"], pred_c, gv)
                    update_outcome(outcomes["FREQ_RESIDUAL"], pred_r, gv)

                    uni = torch.full_like(gv, unigram)
                    residual_unigram_agree += int(pred_r.eq(uni).sum())
                    residual_unigram_shared_correct += int(
                        (pred_r.eq(gv) & uni.eq(gv)).sum()
                    )
                    pc1_component_agree += int(pred_q.eq(pred_c).sum())
                    component_unigram_agree += int(pred_c.eq(uni).sum())

                del h, gold, hidden, targets, lexical, ids
    finally:
        handle.remove()
        taps.clear()

    if lexical_total != VAL_LEXICAL:
        raise RuntimeError("V76 validation lexical coverage changed")

    result = {
        mode: finalize_outcome(item, VAL_LEXICAL)
        for mode, item in outcomes.items()
    }
    for value in (
        residual_unigram_agree,
        residual_unigram_shared_correct,
        pc1_component_agree,
        component_unigram_agree,
    ):
        if not 0 <= value <= VAL_LEXICAL:
            raise RuntimeError("V76 agreement accounting invalid")
    if residual_unigram_shared_correct > residual_unigram_agree:
        raise RuntimeError("V76 residual shared-correct accounting invalid")

    return (
        result,
        residual_unigram_agree,
        residual_unigram_shared_correct,
        pc1_component_agree,
        component_unigram_agree,
    )


def build_metrics(
    outcomes: dict,
    *,
    corr_abs: float,
    r2: float,
    residual_energy: float,
    residual_unigram_agree: int,
    residual_unigram_shared_correct: int,
    pc1_component_agree: int,
    component_unigram_agree: int,
    pc1_var_share_bp: int,
    train_val_cos_abs_bp: int,
    unigram_correct: int,
) -> dict:
    required = {"PC1", "FREQ_COMPONENT", "FREQ_RESIDUAL"}
    if set(outcomes) != required:
        raise RuntimeError("V76 scoring modes incomplete")
    if outcomes["PC1"] != {
        "CORRECT": 2457,
        "DISTINCT": 2,
        "TOP1_SHARE_BP": 7043,
    }:
        raise RuntimeError("V76 frozen V75 PC1 replay failed")
    if not (
        unigram_correct == 2535
        and pc1_var_share_bp == 9019
        and train_val_cos_abs_bp == 9995
        and 0.0 <= corr_abs <= 1.0
        and 0.0 <= r2 <= 1.0
        and 0.0 <= residual_energy <= 1.0
        and abs(r2 + residual_energy - 1.0) <= IDENTITY_TOL
    ):
        raise RuntimeError("V76 frozen geometry/statistic gate failed")

    for mode in required:
        item = outcomes[mode]
        if not (
            0 <= item["CORRECT"] <= VAL_LEXICAL
            and 1 <= item["DISTINCT"] <= VOCAB
            and 0 <= item["TOP1_SHARE_BP"] <= 10000
        ):
            raise RuntimeError("V76 invalid aggregate scoring result")

    for value in (
        residual_unigram_agree,
        residual_unigram_shared_correct,
        pc1_component_agree,
        component_unigram_agree,
    ):
        if type(value) is not int or not 0 <= value <= VAL_LEXICAL:
            raise RuntimeError("V76 invalid agreement metric")
    if residual_unigram_shared_correct > min(
        residual_unigram_agree,
        outcomes["FREQ_RESIDUAL"]["CORRECT"],
        unigram_correct,
    ):
        raise RuntimeError("V76 residual/unigram shared-correct gate failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V76_PASS": 1,
        "V76_BLIND_ACCESS": 0,
        "V76_TRAIN_LEXICAL": TRAIN_LEXICAL,
        "V76_TRAIN_TYPES": TRAIN_TYPES,
        "V76_VAL_LEXICAL": VAL_LEXICAL,
        "V76_HIDDEN_DIM": MODEL_DIM,
        "V76_FIT_VOCAB": VOCAB,
        "V76_PC1_CORRECT": outcomes["PC1"]["CORRECT"],
        "V76_PC1_DISTINCT": outcomes["PC1"]["DISTINCT"],
        "V76_PC1_TOP1_SHARE_BP": outcomes["PC1"]["TOP1_SHARE_BP"],
        "V76_UNIGRAM_CORRECT": unigram_correct,
        "V76_AXIS_FREQ_CORR_ABS_BP": round(corr_abs * 10000),
        "V76_AXIS_FREQ_R2_BP": round(r2 * 10000),
        "V76_FREQ_COMPONENT_CORRECT": outcomes["FREQ_COMPONENT"]["CORRECT"],
        "V76_FREQ_COMPONENT_DISTINCT": outcomes["FREQ_COMPONENT"]["DISTINCT"],
        "V76_FREQ_COMPONENT_TOP1_SHARE_BP":
            outcomes["FREQ_COMPONENT"]["TOP1_SHARE_BP"],
        "V76_FREQ_RESIDUAL_CORRECT": outcomes["FREQ_RESIDUAL"]["CORRECT"],
        "V76_FREQ_RESIDUAL_DISTINCT": outcomes["FREQ_RESIDUAL"]["DISTINCT"],
        "V76_FREQ_RESIDUAL_TOP1_SHARE_BP":
            outcomes["FREQ_RESIDUAL"]["TOP1_SHARE_BP"],
        "V76_RESIDUAL_UNIGRAM_AGREE": residual_unigram_agree,
        "V76_RESIDUAL_UNIGRAM_SHARED_CORRECT":
            residual_unigram_shared_correct,
        "V76_PC1_FREQ_COMPONENT_AGREE": pc1_component_agree,
        "V76_FREQ_COMPONENT_UNIGRAM_AGREE": component_unigram_agree,
        "V76_PC1_VAR_SHARE_BP": pc1_var_share_bp,
        "V76_TRAIN_VAL_PC1_COS_ABS_BP": train_val_cos_abs_bp,
        "V76_RESIDUAL_ENERGY_SHARE_BP": round(residual_energy * 10000),
        "V76_COVERAGE_BP": 10000,
    }
    if not (
        tuple(metrics) == METRIC_FIELDS
        and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
    ):
        raise RuntimeError("V76 strict 30-integer metric schema failed")
    return metrics


def compute():
    torch.set_grad_enabled(False)
    verify_start_receipt()
    refs = verify_frozen_reports()

    v75 = imported("v76_frozen_v75_geometry", V75_SOURCE)
    v65 = imported("v76_frozen_v65_frequency", V65_SOURCE)
    v64 = v75.imported("v76_v64_preflight", v75.V64)
    model, device, streams, validation = v64.preflight()

    if device.type != "cuda":
        raise RuntimeError("V76 requires reviewed CUDA inference path")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("V76 requires CUDA BF16 support")
    if not (
        v75.TRAIN_BATCH == TRAIN_BATCH
        and v75.VAL_BATCH == VAL_BATCH
        and v75.SCORE_CHUNK == SCORE_CHUNK
        and v75.GPU_PEAK_LIMIT_MIB == GPU_PEAK_LIMIT_MIB
    ):
        raise RuntimeError("V76 inherited V75 runtime constants changed")

    frequency = v65.count_training_tokens(streams)
    frequency_count_vector(frequency, require_frozen=True)
    unigram = v75.most_frequent(frequency)

    torch.cuda.reset_peak_memory_stats(device)
    train_segments = v75._segments_in_order(streams)
    t_count, t_mean, t_m2 = v75.collect_geometry(
        model,
        device,
        train_segments,
        TRAIN_LEXICAL,
        TRAIN_BATCH,
    )
    train_mean, train_pc1, train_share = v75.finalize_geometry(
        t_count,
        t_mean,
        t_m2,
        expected_count=TRAIN_LEXICAL,
    )
    v_count, v_mean, v_m2 = v75.collect_geometry(
        model,
        device,
        validation,
        VAL_LEXICAL,
        VAL_BATCH,
    )
    _val_mean, val_pc1, val_share = v75.finalize_geometry(
        v_count,
        v_mean,
        v_m2,
        expected_count=VAL_LEXICAL,
    )
    alignment = v75.abs_cos_bp(train_pc1, val_pc1)

    if not (
        train_share == 9019
        and val_share == 8288
        and alignment == 9995
    ):
        raise RuntimeError("V76 exact V75 geometry replay failed")

    if not (
        model.lm_head.bias is None
        and model.lm_head.weight.shape == (VOCAB, MODEL_DIM)
        and model.lm_head.weight.data_ptr() == model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V76 tied bias-free output-head gate failed")

    profiles = decompose_output_profile(
        model.lm_head.weight,
        train_pc1,
        frequency,
        require_frozen=True,
    )

    (
        outcomes,
        residual_unigram_agree,
        residual_unigram_shared_correct,
        pc1_component_agree,
        component_unigram_agree,
    ) = score_validation(
        model,
        device,
        validation,
        train_mean,
        train_pc1,
        profiles,
        unigram,
    )

    metrics = build_metrics(
        outcomes,
        corr_abs=profiles["CORR_ABS"],
        r2=profiles["R2"],
        residual_energy=profiles["RESIDUAL_ENERGY"],
        residual_unigram_agree=residual_unigram_agree,
        residual_unigram_shared_correct=residual_unigram_shared_correct,
        pc1_component_agree=pc1_component_agree,
        component_unigram_agree=component_unigram_agree,
        pc1_var_share_bp=train_share,
        train_val_cos_abs_bp=alignment,
        unigram_correct=refs["V75"]["V75_UNIGRAM_CORRECT"],
    )

    peak_mib = math.ceil(torch.cuda.max_memory_allocated(device) / (1024 * 1024))
    if peak_mib > GPU_PEAK_LIMIT_MIB:
        raise RuntimeError("V76 GPU peak-memory gate exceeded")
    return metrics, peak_mib


def main():
    metrics, _peak_mib = compute()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
