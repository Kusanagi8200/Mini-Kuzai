#!/usr/bin/env python3
"""V75 read-only TRAIN-fitted hidden-state geometry transfer.

Fits mean/covariance/PC1 only on the complete frozen TRAIN lexical population,
then scores frozen VALIDATION with fixed TRAIN geometry. Aggregate integers only.
No optimizer, training, BLIND access, checkpoint write, hidden-state persistence,
token-ID publication or per-position output is performed.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mini_kuzai import phase03_v62_trainer as T

AUDITS = ROOT / "tools" / "public-audits"
HISTORY = ROOT / "reports" / "assistant-results" / "history"
V64 = AUDITS / "phase03_v64_language_learning_diagnostic_002.py"
V65 = AUDITS / "phase03_v65_token_frequency_diagnostic_001.py"
V73 = AUDITS / "phase03_v73_principal_axis_attribution_001.py"
V74_CORE = AUDITS / "phase03_v74_frequency_prior_core_001.py"
V74_STRATA = AUDITS / "phase03_v74_frequency_prior_strata_001.py"

V65_ID = "PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001"
V73_ID = "PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001"
V74_CORE_ID = "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001"
V74_STRATA_ID = "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001"
STEP_ID = "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001"

SAFE = ("SEMANTIC_VALIDATION_COMPLETE", "TRAINING_AUTHORIZED", "TRAINING_STARTED")
TRAIN_BATCH = 2
VAL_BATCH = 4
SCORE_CHUNK = 512
GPU_PEAK_LIMIT_MIB = 6144
TRAIN_LEXICAL = 294726
TRAIN_TYPES = 891
VAL_LEXICAL = 9170
MODEL_DIM = 128
VOCAB = 1024
SYMMETRY_RTOL = 1e-10
SYMMETRY_ATOL = 1e-12
RELATIVE_EIGENGAP_MIN = 1e-8

METRIC_FIELDS = (
    "SEMANTIC_VALIDATION_COMPLETE",
    "TRAINING_AUTHORIZED",
    "TRAINING_STARTED",
    "V75_PASS",
    "V75_BLIND_ACCESS",
    "V75_TRAIN_LEXICAL",
    "V75_TRAIN_TYPES",
    "V75_VAL_LEXICAL",
    "V75_TRAIN_STATE_COUNT",
    "V75_HIDDEN_DIM",
    "V75_ORIG_CORRECT",
    "V75_ORIG_DISTINCT",
    "V75_ORIG_TOP1_SHARE_BP",
    "V75_TRAIN_CENTER_CORRECT",
    "V75_TRAIN_CENTER_DISTINCT",
    "V75_TRAIN_CENTER_TOP1_SHARE_BP",
    "V75_TRAIN_PC1_CORRECT",
    "V75_TRAIN_PC1_DISTINCT",
    "V75_TRAIN_PC1_TOP1_SHARE_BP",
    "V75_TRAIN_MINUS_PC1_CORRECT",
    "V75_TRAIN_MINUS_PC1_DISTINCT",
    "V75_TRAIN_MINUS_PC1_TOP1_SHARE_BP",
    "V75_UNIGRAM_CORRECT",
    "V75_PC1_UNIGRAM_AGREE",
    "V75_PC1_UNIGRAM_SHARED_CORRECT",
    "V75_VAL_PC1_CORRECT",
    "V75_TRAIN_VAL_PC1_COS_ABS_BP",
    "V75_TRAIN_PC1_VAR_SHARE_BP",
    "V75_VAL_PC1_VAR_SHARE_BP",
    "V75_COVERAGE_BP",
)


def imported(name: str, source: Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("V75 reviewed dependency unavailable or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V75 dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V75 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V75 expected JSON object")
    return value


def verify_report(step_id: str, producer: Path, expected: dict) -> dict:
    report = read_json(HISTORY / (step_id + ".json"))
    metrics = report.get("metrics")
    relative = str(producer.relative_to(ROOT))
    if not (
        producer.is_file()
        and not producer.is_symlink()
        and report.get("step_id") == step_id
        and report.get("producer") == relative
        and report.get("producer_sha256")
        == hashlib.sha256(producer.read_bytes()).hexdigest()
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
        and all(metrics.get(k) == v for k, v in expected.items())
        and all(metrics.get(k) == 0 for k in SAFE)
        and all(v == 0 for k, v in metrics.items() if k.endswith("_BLIND_ACCESS"))
    ):
        raise RuntimeError("V75 immutable prerequisite report/fingerprint gate failed")
    return metrics


def prerequisites() -> dict:
    v65 = verify_report(
        V65_ID,
        V65,
        {
            "V65_FREQ_PASS": 1,
            "V65_FREQ_BLIND_ACCESS": 0,
            "V65_FREQ_TRAIN_LEXICAL": TRAIN_LEXICAL,
            "V65_FREQ_TRAIN_TYPES": TRAIN_TYPES,
            "V65_FREQ_VAL_LEXICAL": VAL_LEXICAL,
        },
    )
    v73 = verify_report(
        V73_ID,
        V73,
        {
            "V73_AXIS_PASS": 1,
            "V73_AXIS_BLIND_ACCESS": 0,
            "V73_AXIS_VAL_LEXICAL": VAL_LEXICAL,
            "V73_AXIS_MODEL_DIM": MODEL_DIM,
            "V73_AXIS_CENTER_PC1_BP": 8288,
            "V73_AXIS_PC1_ONLY_CORRECT": 2455,
            "V73_AXIS_PC1_ONLY_DISTINCT": 2,
            "V73_AXIS_PC1_ONLY_TOP1_SHARE_BP": 7034,
        },
    )
    v74_core = verify_report(
        V74_CORE_ID,
        V74_CORE,
        {
            "V74_CORE_PASS": 1,
            "V74_CORE_BLIND_ACCESS": 0,
            "V74_CORE_VAL_LEXICAL": VAL_LEXICAL,
            "V74_CORE_ORIG_CORRECT": 2673,
            "V74_CORE_ORIG_DISTINCT": 5,
            "V74_CORE_ORIG_TOP1_SHARE_BP": 7255,
            "V74_CORE_PC1_CORRECT": 2455,
            "V74_CORE_UNIGRAM_CORRECT": 2535,
        },
    )
    v74_strata = verify_report(
        V74_STRATA_ID,
        V74_STRATA,
        {
            "V74_STRATA_PASS": 1,
            "V74_STRATA_BLIND_ACCESS": 0,
            "V74_STRATA_VAL_LEXICAL": VAL_LEXICAL,
            "V74_STRATA_TRAIN_LEXICAL": TRAIN_LEXICAL,
            "V74_STRATA_TRAIN_TYPES": TRAIN_TYPES,
            "V74_STRATA_PC1_UNIGRAM_AGREE": 6450,
            "V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT": 2449,
        },
    )
    return {
        "V65": v65,
        "V73": v73,
        "V74_CORE": v74_core,
        "V74_STRATA": v74_strata,
    }


def verify_start_receipt() -> None:
    receipt = read_json(ROOT / "automation" / "dev-flow" / "receipts" / "V75-start.json")
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V75"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6"
        and receipt.get("source_commit")
        == "12989645b3d6a2071a8ca0ad4f7fd7a2b590d5e5"
    ):
        raise RuntimeError("V75 official START receipt absent or invalid")


def most_frequent(frequency: Counter) -> int:
    if (
        not frequency
        or any(
            type(token) is not int
            or not 3 <= token < T.VOCAB_SIZE
            or type(count) is not int
            or count <= 0
            for token, count in frequency.items()
        )
    ):
        raise ValueError("V75 invalid TRAIN token-frequency inventory")
    return min(frequency, key=lambda token: (-frequency[token], token))


def empty_stats(dim: int = MODEL_DIM):
    if type(dim) is not int or dim <= 0:
        raise ValueError("V75 invalid geometry dimension")
    return (
        0,
        torch.zeros(dim, dtype=torch.float64),
        torch.zeros((dim, dim), dtype=torch.float64),
    )


def update_stats(count: int, mean: torch.Tensor, m2: torch.Tensor, batch: torch.Tensor):
    """Parallel-Welford merge of one CPU FP64 batch; no sample retention."""
    if (
        type(count) is not int
        or count < 0
        or mean.ndim != 1
        or m2.shape != (mean.numel(), mean.numel())
        or batch.ndim != 2
        or batch.shape[1] != mean.numel()
        or batch.shape[0] <= 0
    ):
        raise ValueError("V75 streaming-statistic shape/count mismatch")
    x = batch.detach().to(device="cpu", dtype=torch.float64)
    if not torch.isfinite(x).all():
        raise RuntimeError("V75 nonfinite hidden state")
    n_b = int(x.shape[0])
    mean_b = x.mean(0)
    centered = x - mean_b
    m2_b = centered.T @ centered
    if count == 0:
        return n_b, mean_b, m2_b
    total = count + n_b
    delta = mean_b - mean
    merged_mean = mean + delta * (n_b / total)
    merged_m2 = m2 + m2_b + torch.outer(delta, delta) * (count * n_b / total)
    if not (torch.isfinite(merged_mean).all() and torch.isfinite(merged_m2).all()):
        raise RuntimeError("V75 nonfinite streaming geometry")
    return total, merged_mean, merged_m2


def finalize_geometry(
    count: int,
    mean: torch.Tensor,
    m2: torch.Tensor,
    *,
    expected_count: int | None = None,
):
    if expected_count is not None and count != expected_count:
        raise RuntimeError("V75 geometry population count mismatch")
    if count < 2 or mean.shape != (MODEL_DIM,) or m2.shape != (MODEL_DIM, MODEL_DIM):
        raise RuntimeError("V75 incomplete geometry sufficient statistics")
    if not (torch.isfinite(mean).all() and torch.isfinite(m2).all()):
        raise RuntimeError("V75 nonfinite geometry sufficient statistics")
    cov = m2 / count
    if not torch.allclose(cov, cov.T, rtol=SYMMETRY_RTOL, atol=SYMMETRY_ATOL):
        raise RuntimeError("V75 covariance symmetry gate failed")
    cov = (cov + cov.T) * 0.5
    values, vectors = torch.linalg.eigh(cov)
    if not (torch.isfinite(values).all() and torch.isfinite(vectors).all()):
        raise RuntimeError("V75 nonfinite eigendecomposition")
    values = values.clamp_min(0)
    total = float(values.sum())
    lead = float(values[-1])
    second = float(values[-2])
    if not math.isfinite(total) or not math.isfinite(lead) or total <= 1e-12 or lead <= 1e-12:
        raise RuntimeError("V75 degenerate covariance spectrum")
    relative_gap = (lead - second) / max(lead, 1e-12)
    if not math.isfinite(relative_gap) or relative_gap < RELATIVE_EIGENGAP_MIN:
        raise RuntimeError("V75 leading spectral axis is degenerate")
    pc1 = vectors[:, -1]
    norm = float(torch.linalg.vector_norm(pc1))
    if not math.isfinite(norm) or abs(norm - 1.0) > 1e-10:
        raise RuntimeError("V75 leading eigenvector normalization failed")
    share_bp = round(10000 * lead / total)
    if not 1 <= share_bp <= 10000:
        raise RuntimeError("V75 invalid leading-axis variance share")
    return mean.clone(), pc1.clone(), share_bp


def project_modes(hidden: torch.Tensor, mean: torch.Tensor, pc1: torch.Tensor):
    if (
        hidden.ndim != 2
        or hidden.shape[1] != MODEL_DIM
        or mean.shape != (MODEL_DIM,)
        or pc1.shape != (MODEL_DIM,)
    ):
        raise RuntimeError("V75 projection shape mismatch")
    centered = hidden - mean
    component = (centered @ pc1).unsqueeze(1) * pc1.unsqueeze(0)
    return {
        "TRAIN_CENTER": centered,
        "TRAIN_PC1": component,
        "TRAIN_MINUS_PC1": centered - component,
    }


def abs_cos_bp(a: torch.Tensor, b: torch.Tensor) -> int:
    if a.shape != (MODEL_DIM,) or b.shape != (MODEL_DIM,):
        raise RuntimeError("V75 PC1 alignment dimension mismatch")
    a64 = a.detach().to(device="cpu", dtype=torch.float64)
    b64 = b.detach().to(device="cpu", dtype=torch.float64)
    den = float(torch.linalg.vector_norm(a64) * torch.linalg.vector_norm(b64))
    if not math.isfinite(den) or den <= 1e-12:
        raise RuntimeError("V75 PC1 alignment norm invalid")
    value = abs(float(torch.dot(a64, b64))) / den
    if not math.isfinite(value) or value > 1.0000001:
        raise RuntimeError("V75 PC1 alignment invalid")
    return round(min(value, 1.0) * 10000)


def _segments_in_order(streams: dict) -> list:
    if tuple(streams) != T.STREAMS:
        raise RuntimeError("V75 frozen TRAIN stream order changed")
    segments = [segment for name in T.STREAMS for segment in streams[name]]
    if len(segments) != 345:
        raise RuntimeError("V75 frozen TRAIN segment inventory changed")
    return segments


def collect_geometry(model, device, segments: list, expected_lexical: int, batch_size: int):
    if (
        not segments
        or type(expected_lexical) is not int
        or expected_lexical <= 0
        or type(batch_size) is not int
        or batch_size <= 0
    ):
        raise RuntimeError("V75 invalid geometry collection request")
    taps = []

    def capture(_module, inputs):
        if len(inputs) != 1 or inputs[0].ndim != 3 or inputs[0].shape[-1] != MODEL_DIM:
            raise RuntimeError("V75 output-head hidden state shape changed")
        taps.append(inputs[0].detach())

    count, mean, m2 = empty_stats()
    handle = model.lm_head.register_forward_pre_hook(capture)
    model.eval()
    try:
        with torch.inference_mode():
            for start in range(0, len(segments), batch_size):
                group = segments[start : start + batch_size]
                ids = torch.full(
                    (len(group), max(len(seg.token_ids) for seg in group)),
                    T.PAD_ID,
                    dtype=torch.long,
                    device=device,
                )
                for row, seg in enumerate(group):
                    if seg.token_ids[0] != T.BOS_ID or seg.token_ids[-1] != T.EOS_ID:
                        raise RuntimeError("V75 frozen sequence boundary changed")
                    ids[row, : len(seg.token_ids)] = torch.as_tensor(
                        seg.token_ids, dtype=torch.long, device=device
                    )
                with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                    model(ids)
                if len(taps) != 1 or taps[0].shape[:2] != ids.shape:
                    raise RuntimeError("V75 hidden-state pre-hook mismatch")
                hidden = taps.pop().float()[:, :-1, :]
                targets = ids[:, 1:]
                lexical = (
                    targets.ne(T.PAD_ID)
                    & targets.ge(3)
                    & targets.lt(T.VOCAB_SIZE)
                )
                selected = hidden[lexical]
                if selected.numel():
                    count, mean, m2 = update_stats(count, mean, m2, selected)
                del selected, hidden, targets, lexical, ids
    finally:
        handle.remove()
        taps.clear()
    if count != expected_lexical:
        raise RuntimeError("V75 lexical geometry coverage changed")
    return count, mean, m2


def _empty_outcomes():
    names = ("ORIG", "TRAIN_CENTER", "TRAIN_PC1", "TRAIN_MINUS_PC1", "VAL_PC1")
    return {
        name: {
            "CORRECT": 0,
            "HIST": torch.zeros(T.VOCAB_SIZE, dtype=torch.long),
        }
        for name in names
    }


def score_validation(
    model,
    device,
    validation: list,
    train_mean: torch.Tensor,
    train_pc1: torch.Tensor,
    val_mean: torch.Tensor,
    val_pc1: torch.Tensor,
    unigram: int,
):
    if len(validation) != 36:
        raise RuntimeError("V75 frozen VALIDATION segment count changed")
    if not (
        train_mean.shape == val_mean.shape == (MODEL_DIM,)
        and train_pc1.shape == val_pc1.shape == (MODEL_DIM,)
        and 3 <= unigram < T.VOCAB_SIZE
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr() == model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V75 scoring geometry/output-head gate failed")

    weights = model.lm_head.weight.detach().float()
    mean_t = train_mean.to(device=device, dtype=torch.float32)
    pc1_t = train_pc1.to(device=device, dtype=torch.float32)
    val_mean_t = val_mean.to(device=device, dtype=torch.float32)
    val_pc1_t = val_pc1.to(device=device, dtype=torch.float32)
    outcomes = _empty_outcomes()
    agree = shared_correct = lexical_total = 0
    taps = []

    def capture(_module, inputs):
        if len(inputs) != 1 or inputs[0].ndim != 3 or inputs[0].shape[-1] != MODEL_DIM:
            raise RuntimeError("V75 validation hidden state shape changed")
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
                        raise RuntimeError("V75 VALIDATION boundary changed")
                    ids[row, : len(seg.token_ids)] = torch.as_tensor(
                        seg.token_ids, dtype=torch.long, device=device
                    )
                with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                    model(ids)
                if len(taps) != 1 or taps[0].shape[:2] != ids.shape:
                    raise RuntimeError("V75 validation pre-hook mismatch")
                hidden = taps.pop().float()[:, :-1, :]
                targets = ids[:, 1:]
                lexical = (
                    targets.ne(T.PAD_ID)
                    & targets.ge(3)
                    & targets.lt(T.VOCAB_SIZE)
                )
                h = hidden[lexical]
                gold = targets[lexical]
                lexical_total += int(gold.numel())

                for offset in range(0, int(gold.numel()), SCORE_CHUNK):
                    stop = min(offset + SCORE_CHUNK, int(gold.numel()))
                    hv = h[offset:stop]
                    gv = gold[offset:stop]
                    train_modes = project_modes(hv, mean_t, pc1_t)
                    val_centered = hv - val_mean_t
                    val_component = (
                        (val_centered @ val_pc1_t).unsqueeze(1)
                        * val_pc1_t.unsqueeze(0)
                    )
                    vectors = {
                        "ORIG": hv,
                        **train_modes,
                        "VAL_PC1": val_component,
                    }
                    predicted = {}
                    for mode, vector in vectors.items():
                        logits = F.linear(vector, weights)
                        if not torch.isfinite(logits).all():
                            raise RuntimeError("V75 nonfinite counterfactual logits")
                        pred = logits.argmax(1)
                        predicted[mode] = pred
                        outcomes[mode]["CORRECT"] += int(pred.eq(gv).sum())
                        outcomes[mode]["HIST"] += torch.bincount(
                            pred.to("cpu"), minlength=T.VOCAB_SIZE
                        )
                    uni = torch.full_like(gv, unigram)
                    agree += int(predicted["TRAIN_PC1"].eq(uni).sum())
                    shared_correct += int(
                        (
                            predicted["TRAIN_PC1"].eq(gv)
                            & uni.eq(gv)
                        ).sum()
                    )
                del h, gold, hidden, targets, lexical, ids
    finally:
        handle.remove()
        taps.clear()

    if lexical_total != VAL_LEXICAL:
        raise RuntimeError("V75 validation lexical coverage changed")
    result = {}
    for mode, item in outcomes.items():
        hist = item["HIST"]
        if int(hist.sum()) != VAL_LEXICAL:
            raise RuntimeError("V75 prediction histogram coverage incomplete")
        result[mode] = {
            "CORRECT": item["CORRECT"],
            "DISTINCT": int(hist.gt(0).sum()),
            "TOP1_SHARE_BP": round(int(hist.max()) * 10000 / VAL_LEXICAL),
        }
        if not (
            0 <= result[mode]["CORRECT"] <= VAL_LEXICAL
            and 1 <= result[mode]["DISTINCT"] <= T.VOCAB_SIZE
            and 0 <= result[mode]["TOP1_SHARE_BP"] <= 10000
        ):
            raise RuntimeError("V75 invalid aggregate scoring result")
    if not 0 <= shared_correct <= agree <= VAL_LEXICAL:
        raise RuntimeError("V75 PC1/unigram overlap invalid")
    return result, agree, shared_correct


def build_metrics(
    outcomes: dict,
    agree: int,
    shared: int,
    train_share_bp: int,
    val_share_bp: int,
    alignment_bp: int,
    unigram_correct: int,
):
    required_modes = {"ORIG", "TRAIN_CENTER", "TRAIN_PC1", "TRAIN_MINUS_PC1", "VAL_PC1"}
    if set(outcomes) != required_modes:
        raise RuntimeError("V75 scoring modes incomplete")
    if not (
        outcomes["ORIG"] == {
            "CORRECT": 2673,
            "DISTINCT": 5,
            "TOP1_SHARE_BP": 7255,
        }
        and outcomes["VAL_PC1"]["CORRECT"] == 2455
        and outcomes["VAL_PC1"]["DISTINCT"] == 2
        and outcomes["VAL_PC1"]["TOP1_SHARE_BP"] == 7034
        and unigram_correct == 2535
        and val_share_bp == 8288
        and 0 <= alignment_bp <= 10000
        and 1 <= train_share_bp <= 10000
        and 0 <= shared <= agree <= VAL_LEXICAL
    ):
        raise RuntimeError("V75 frozen V73/V74 replay or geometry gate failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V75_PASS": 1,
        "V75_BLIND_ACCESS": 0,
        "V75_TRAIN_LEXICAL": TRAIN_LEXICAL,
        "V75_TRAIN_TYPES": TRAIN_TYPES,
        "V75_VAL_LEXICAL": VAL_LEXICAL,
        "V75_TRAIN_STATE_COUNT": TRAIN_LEXICAL,
        "V75_HIDDEN_DIM": MODEL_DIM,
        "V75_ORIG_CORRECT": outcomes["ORIG"]["CORRECT"],
        "V75_ORIG_DISTINCT": outcomes["ORIG"]["DISTINCT"],
        "V75_ORIG_TOP1_SHARE_BP": outcomes["ORIG"]["TOP1_SHARE_BP"],
        "V75_TRAIN_CENTER_CORRECT": outcomes["TRAIN_CENTER"]["CORRECT"],
        "V75_TRAIN_CENTER_DISTINCT": outcomes["TRAIN_CENTER"]["DISTINCT"],
        "V75_TRAIN_CENTER_TOP1_SHARE_BP": outcomes["TRAIN_CENTER"]["TOP1_SHARE_BP"],
        "V75_TRAIN_PC1_CORRECT": outcomes["TRAIN_PC1"]["CORRECT"],
        "V75_TRAIN_PC1_DISTINCT": outcomes["TRAIN_PC1"]["DISTINCT"],
        "V75_TRAIN_PC1_TOP1_SHARE_BP": outcomes["TRAIN_PC1"]["TOP1_SHARE_BP"],
        "V75_TRAIN_MINUS_PC1_CORRECT": outcomes["TRAIN_MINUS_PC1"]["CORRECT"],
        "V75_TRAIN_MINUS_PC1_DISTINCT": outcomes["TRAIN_MINUS_PC1"]["DISTINCT"],
        "V75_TRAIN_MINUS_PC1_TOP1_SHARE_BP": outcomes["TRAIN_MINUS_PC1"]["TOP1_SHARE_BP"],
        "V75_UNIGRAM_CORRECT": unigram_correct,
        "V75_PC1_UNIGRAM_AGREE": agree,
        "V75_PC1_UNIGRAM_SHARED_CORRECT": shared,
        "V75_VAL_PC1_CORRECT": outcomes["VAL_PC1"]["CORRECT"],
        "V75_TRAIN_VAL_PC1_COS_ABS_BP": alignment_bp,
        "V75_TRAIN_PC1_VAR_SHARE_BP": train_share_bp,
        "V75_VAL_PC1_VAR_SHARE_BP": val_share_bp,
        "V75_COVERAGE_BP": 10000,
    }
    if not (
        tuple(metrics) == METRIC_FIELDS
        and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100_000_000 for v in metrics.values())
    ):
        raise RuntimeError("V75 strict 30-integer metric schema failed")
    return metrics


def compute():
    verify_start_receipt()
    refs = prerequisites()
    v64 = imported("v75_v64_preflight", V64)
    v65 = imported("v75_v65_frequency", V65)
    model, device, streams, validation = v64.preflight()
    if device.type != "cuda":
        raise RuntimeError("V75 requires reviewed CUDA inference path")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("V75 requires CUDA BF16 support")
    frequency = v65.count_training_tokens(streams)
    if sum(frequency.values()) != TRAIN_LEXICAL or len(frequency) != TRAIN_TYPES:
        raise RuntimeError("V75 frozen TRAIN lexical inventory mismatch")
    unigram = most_frequent(frequency)

    torch.cuda.reset_peak_memory_stats(device)
    train_segments = _segments_in_order(streams)
    t_count, t_mean, t_m2 = collect_geometry(
        model, device, train_segments, TRAIN_LEXICAL, TRAIN_BATCH
    )
    train_mean, train_pc1, train_share = finalize_geometry(
        t_count, t_mean, t_m2, expected_count=TRAIN_LEXICAL
    )
    v_count, v_mean, v_m2 = collect_geometry(
        model, device, validation, VAL_LEXICAL, VAL_BATCH
    )
    val_mean, val_pc1, val_share = finalize_geometry(
        v_count, v_mean, v_m2, expected_count=VAL_LEXICAL
    )
    alignment = abs_cos_bp(train_pc1, val_pc1)
    outcomes, agree, shared = score_validation(
        model,
        device,
        validation,
        train_mean,
        train_pc1,
        val_mean,
        val_pc1,
        unigram,
    )

    unigram_correct = refs["V74_CORE"]["V74_CORE_UNIGRAM_CORRECT"]
    metrics = build_metrics(
        outcomes,
        agree,
        shared,
        train_share,
        val_share,
        alignment,
        unigram_correct,
    )
    peak_mib = math.ceil(torch.cuda.max_memory_allocated(device) / (1024 * 1024))
    if peak_mib > GPU_PEAK_LIMIT_MIB:
        raise RuntimeError("V75 GPU peak-memory gate exceeded")
    return metrics, peak_mib


def main():
    metrics, _peak_mib = compute()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
