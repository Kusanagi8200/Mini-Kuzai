#!/usr/bin/env python3
"""V73 read-only principal-axis attribution of frozen V62 hidden states.

Teacher-forced VALIDATION only. GOGIT exports 30 aggregate integer fields,
never prompts, raw tokens, eigenvectors, logits or model parameters.
"""
from __future__ import annotations

import hashlib
import importlib.util
import math
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from mini_kuzai import phase03_v62_trainer as T

AUDITS = ROOT / "tools" / "public-audits"
HISTORY = ROOT / "reports" / "assistant-results" / "history"
V64 = AUDITS / "phase03_v64_language_learning_diagnostic_002.py"
V67 = AUDITS / "phase03_v67_output_concentration_001.py"
V69 = AUDITS / "phase03_v69_output_norm_counterfactual_001.py"
V72 = AUDITS / "phase03_v72_hidden_state_anisotropy_001.py"
V72_STEP = "PHASE03-SMOLTALK-V72-HIDDEN-STATE-ANISOTROPY-001"
BATCH = 4
CHUNK = 512
MODES = ("CENTER", "MINUS_PC1", "MINUS_PC12", "PC1_ONLY")
FIELDS = (
    "PASS", "BLIND_ACCESS", "VAL_LEXICAL", "MODEL_DIM",
    "CENTER_PC1_BP", "CENTER_PC2_BP",
    "CENTER_TOP1_SHARE_BP", "CENTER_DISTINCT", "CENTER_CORRECT",
    "MINUS_PC1_DISTINCT", "MINUS_PC1_TOP1_SHARE_BP",
    "MINUS_PC1_CORRECT", "MINUS_PC1_SWITCH",
    "MINUS_PC1_SWITCH_BYTE", "MINUS_PC1_SWITCH_MERGE",
    "MINUS_PC12_DISTINCT", "MINUS_PC12_TOP1_SHARE_BP",
    "MINUS_PC12_CORRECT", "MINUS_PC12_SWITCH",
    "PC1_ONLY_DISTINCT", "PC1_ONLY_TOP1_SHARE_BP", "PC1_ONLY_CORRECT",
    "CENTER_MARGIN_X1000", "MINUS_PC1_MARGIN_X1000",
    "MINUS_PC12_MARGIN_X1000",
    "PC1_WIN_ABS_COS_X1000", "PC1_GOLD_ABS_COS_X1000",
)


def imported(name: str, source: Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("V73 reviewed dependency absent or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V73 reviewed dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prerequisite(read_json):
    if not V72.is_file() or V72.is_symlink():
        raise RuntimeError("V72 frozen source missing")
    report = read_json(HISTORY / (V72_STEP + ".json"))
    m = report.get("metrics", {})
    checks = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V72_GEOM_PASS": 1,
        "V72_GEOM_BLIND_ACCESS": 0,
        "V72_GEOM_VAL_LEXICAL": 9170,
        "V72_GEOM_MODEL_DIM": 128,
        "V72_GEOM_ORIG_CE_X1000": 4732,
        "V72_GEOM_ORIG_DISTINCT": 5,
        "V72_GEOM_ORIG_TOP1_SHARE_BP": 7255,
        "V72_GEOM_CENTER_PC1_SHARE_BP": 8288,
        "V72_GEOM_CENTER_PC5_SHARE_BP": 9738,
        "V72_GEOM_CENTER_DISTINCT": 15,
        "V72_GEOM_CENTER_TOP1_SHARE_BP": 5788,
        "V72_GEOM_CENTER_CORRECT": 2832,
        "V72_GEOM_ORIG_CORRECT": 2673,
    }
    if not (
        report.get("step_id") == V72_STEP
        and report.get("producer") ==
            "tools/public-audits/phase03_v72_hidden_state_anisotropy_001.py"
        and report.get("producer_sha256") ==
            hashlib.sha256(V72.read_bytes()).hexdigest()
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("training_authorized") is False
        and report.get("semantic_validation_complete") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(m, dict) and len(m) == 30
        and all(type(value) is int for value in m.values())
        and all(m.get(key) == value for key, value in checks.items())
    ):
        raise RuntimeError("V73 immutable V72 source/report gate failed")
    return m


def principal_axes(hidden):
    """Fit only frozen VALIDATION centered covariance, in float64 CPU."""
    if hidden.shape != (9170, 128) or not torch.isfinite(hidden).all():
        raise RuntimeError("V73 frozen hidden inventory invalid")
    h = hidden.detach().to(device="cpu", dtype=torch.float64)
    center = h - h.mean(0)
    cov = center.T @ center / 9170
    spectrum, axes = torch.linalg.eigh(cov)
    spectrum = spectrum.clamp_min(0)
    power = float(spectrum.sum())
    if not math.isfinite(power) or power <= 1e-12:
        raise RuntimeError("V73 centered covariance degenerate")
    pc1 = float(spectrum[-1] / power)
    pc2 = float(spectrum[-2] / power)
    pc5 = float(spectrum[-5:].sum() / power)
    if not (0 < pc2 <= pc1 and pc1 <= pc5 <= 1.000001):
        raise RuntimeError("V73 invalid principal axis spectrum")
    basis = axes[:, -2:].float().to(device=hidden.device)
    if not torch.allclose(basis.T @ basis,
                          torch.eye(2, device=hidden.device), atol=2e-5):
        raise RuntimeError("V73 principal axes not orthogonal")
    return basis, {"PC1_BP": round(10000 * pc1),
                   "PC2_BP": round(10000 * pc2),
                   "PC5_BP": round(10000 * pc5)}


def project_modes(centered, basis):
    """Sign-invariant orthogonal projections; no model-state mutation."""
    if centered.ndim != 2 or centered.shape[1] != 128 or basis.shape != (128, 2):
        raise RuntimeError("V73 projection dimension mismatch")
    pc2 = centered @ basis[:, :1] @ basis[:, :1].T
    pc1only = centered @ basis[:, 1:] @ basis[:, 1:].T
    return {
        "CENTER": centered,
        "MINUS_PC1": centered - pc1only,
        "MINUS_PC12": centered - pc1only - pc2,
        "PC1_ONLY": pc1only,
    }


def collect(model, device, validation, v69, ranker):
    if not (
        len(validation) == 36
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr() ==
            model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V73 frozen tied output head changed")
    weights = model.lm_head.weight.detach().float()
    before = weights.clone()
    score = v69.empty()
    memory, gold_tokens = [], []
    taps = []

    def capture(_module, inputs):
        if len(inputs) != 1 or inputs[0].ndim != 3:
            raise RuntimeError("V73 output hidden state shape changed")
        taps.append(inputs[0].detach())

    handle = model.lm_head.register_forward_pre_hook(capture)
    model.eval()
    try:
        with torch.inference_mode():
            for start in range(0, 36, BATCH):
                batch = validation[start:start + BATCH]
                ids = torch.full(
                    (len(batch), max(len(seg.token_ids) for seg in batch)),
                    T.PAD_ID, dtype=torch.long, device=device)
                eos = []
                for row, seg in enumerate(batch):
                    if seg.token_ids[0] != T.BOS_ID or seg.token_ids[-1] != T.EOS_ID:
                        raise RuntimeError("V73 frozen conversation boundary changed")
                    ids[row, :len(seg.token_ids)] = torch.as_tensor(
                        seg.token_ids, dtype=torch.long, device=device)
                    eos.append((row, len(seg.token_ids) - 2))
                with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                    model(ids)
                if len(taps) != 1 or taps[0].shape[:2] != ids.shape:
                    raise RuntimeError("V73 hidden pre-hook mismatch")
                h = taps.pop().float()[:, :-1, :]
                targets = ids[:, 1:]
                valid = targets.ne(T.PAD_ID)
                lexical = valid & targets.ge(3) & targets.lt(T.VOCAB_SIZE)
                with torch.autocast(device_type="cuda", enabled=False):
                    logits = F.linear(h, weights)
                    v69.update_stats(score, logits, targets, valid, eos, ranker)
                    memory.append(h[lexical].clone())
                    gold_tokens.append(targets[lexical].clone())
    finally:
        handle.remove()
        taps.clear()
    if not torch.equal(weights, before):
        raise RuntimeError("V73 modified original output projection")
    hidden, gold = torch.cat(memory), torch.cat(gold_tokens)
    if not (hidden.shape == (9170, 128) and gold.shape == (9170,)
            and int(gold.lt(259).sum()) == 4876
            and int(gold.ge(259).sum()) == 4294):
        raise RuntimeError("V73 frozen lexical count changed")
    return hidden, gold, weights, v69.finalize(score)


def measure_modes(hidden, gold, weights, basis, center_mean):
    if not (
        hidden.shape == (9170, 128) and gold.shape == (9170,)
        and weights.shape == (T.VOCAB_SIZE, 128)
        and center_mean.shape == (128,) and basis.shape == (128, 2)
    ):
        raise RuntimeError("V73 score input shape invalid")
    counts = {m: torch.zeros(T.VOCAB_SIZE, dtype=torch.long,
                            device=hidden.device) for m in MODES}
    correct = {m: 0 for m in MODES}
    margins = {m: 0.0 for m in MODES}
    switches = {m: 0 for m in MODES[1:]}
    switch_byte = switch_merge = 0
    pc1 = basis[:, 1]
    row_norm = weights.norm(dim=1).clamp_min(1e-12)
    cos_winner = cos_gold = 0.0
    with torch.inference_mode():
        for start in range(0, 9170, CHUNK):
            stop = min(9170, start + CHUNK)
            centered = hidden[start:stop] - center_mean
            targets = gold[start:stop]
            vectors = project_modes(centered, basis)
            predictions = {}
            for mode, h in vectors.items():
                logits = F.linear(h, weights)
                if not torch.isfinite(logits).all():
                    raise RuntimeError("V73 nonfinite counterfactual logits")
                top = logits.topk(2, dim=1).values
                margins[mode] += float((top[:, 0] - top[:, 1]).clamp_min(0).sum())
                pred = logits.argmax(1)
                predictions[mode] = pred
                counts[mode] += torch.bincount(pred, minlength=T.VOCAB_SIZE)
                correct[mode] += int(pred.eq(targets).sum().item())
            baseline = predictions["CENTER"]
            for mode in MODES[1:]:
                switches[mode] += int(predictions[mode].ne(baseline).sum())
            changed = predictions["MINUS_PC1"].ne(baseline)
            switch_byte += int((changed & targets.lt(259)).sum())
            switch_merge += int((changed & targets.ge(259)).sum())
            win_alignment = torch.abs(weights[baseline] @ pc1) / row_norm[baseline]
            gold_alignment = torch.abs(weights[targets] @ pc1) / row_norm[targets]
            cos_winner += float(win_alignment.sum())
            cos_gold += float(gold_alignment.sum())
    results = {}
    for mode in MODES:
        hist = counts[mode]
        if int(hist.sum().item()) != 9170:
            raise RuntimeError("V73 mode prediction histogram incomplete")
        results[mode] = {
            "DISTINCT": int(hist.gt(0).sum().item()),
            "TOP1_SHARE_BP": round(int(hist.max().item()) * 10000 / 9170),
            "CORRECT": correct[mode],
            "MARGIN_X1000": round(1000 * margins[mode] / 9170),
        }
    if switches["MINUS_PC1"] != switch_byte + switch_merge:
        raise RuntimeError("V73 per-family PC1 switch sum mismatch")
    return results, switches, switch_byte, switch_merge, {
        "WIN": round(1000 * cos_winner / 9170),
        "GOLD": round(1000 * cos_gold / 9170),
    }


def build_report(spectrum, outcomes, changes, switched_byte,
                 switched_merge, alignment, original, v72):
    expected = {
        "CE_X1000": v72["V72_GEOM_ORIG_CE_X1000"],
        "PRED_DISTINCT": v72["V72_GEOM_ORIG_DISTINCT"],
        "TOP1_SHARE_BP": v72["V72_GEOM_ORIG_TOP1_SHARE_BP"],
    }
    if any(original.get(key) != expected_value
           for key, expected_value in expected.items()):
        raise RuntimeError("V73 original FP32 baseline differs from V72")
    baseline = outcomes["CENTER"]
    if not (
        baseline["DISTINCT"] == v72["V72_GEOM_CENTER_DISTINCT"] == 15
        and baseline["TOP1_SHARE_BP"] ==
            v72["V72_GEOM_CENTER_TOP1_SHARE_BP"] == 5788
        and baseline["CORRECT"] == v72["V72_GEOM_CENTER_CORRECT"] == 2832
        and spectrum["PC1_BP"] == v72["V72_GEOM_CENTER_PC1_SHARE_BP"] == 8288
        and 0 <= spectrum["PC2_BP"] <= spectrum["PC1_BP"]
        and spectrum["PC1_BP"] + spectrum["PC2_BP"] <=
            spectrum["PC5_BP"] <= v72["V72_GEOM_CENTER_PC5_SHARE_BP"] + 1
        and 0 <= switched_byte <= 4876 and 0 <= switched_merge <= 4294
        and changes["MINUS_PC1"] == switched_byte + switched_merge
        and all(0 <= changes[mode] <= 9170 for mode in MODES[1:])
    ):
        raise RuntimeError("V73 centered V72 replay or spectrum invalid")
    measures = {
        "PASS": 1, "BLIND_ACCESS": 0, "VAL_LEXICAL": 9170, "MODEL_DIM": 128,
        "CENTER_PC1_BP": spectrum["PC1_BP"],
        "CENTER_PC2_BP": spectrum["PC2_BP"],
        "CENTER_TOP1_SHARE_BP": baseline["TOP1_SHARE_BP"],
        "CENTER_DISTINCT": baseline["DISTINCT"],
        "CENTER_CORRECT": baseline["CORRECT"],
        "MINUS_PC1_DISTINCT": outcomes["MINUS_PC1"]["DISTINCT"],
        "MINUS_PC1_TOP1_SHARE_BP": outcomes["MINUS_PC1"]["TOP1_SHARE_BP"],
        "MINUS_PC1_CORRECT": outcomes["MINUS_PC1"]["CORRECT"],
        "MINUS_PC1_SWITCH": changes["MINUS_PC1"],
        "MINUS_PC1_SWITCH_BYTE": switched_byte,
        "MINUS_PC1_SWITCH_MERGE": switched_merge,
        "MINUS_PC12_DISTINCT": outcomes["MINUS_PC12"]["DISTINCT"],
        "MINUS_PC12_TOP1_SHARE_BP": outcomes["MINUS_PC12"]["TOP1_SHARE_BP"],
        "MINUS_PC12_CORRECT": outcomes["MINUS_PC12"]["CORRECT"],
        "MINUS_PC12_SWITCH": changes["MINUS_PC12"],
        "PC1_ONLY_DISTINCT": outcomes["PC1_ONLY"]["DISTINCT"],
        "PC1_ONLY_TOP1_SHARE_BP": outcomes["PC1_ONLY"]["TOP1_SHARE_BP"],
        "PC1_ONLY_CORRECT": outcomes["PC1_ONLY"]["CORRECT"],
        "CENTER_MARGIN_X1000": baseline["MARGIN_X1000"],
        "MINUS_PC1_MARGIN_X1000": outcomes["MINUS_PC1"]["MARGIN_X1000"],
        "MINUS_PC12_MARGIN_X1000": outcomes["MINUS_PC12"]["MARGIN_X1000"],
        "PC1_WIN_ABS_COS_X1000": alignment["WIN"],
        "PC1_GOLD_ABS_COS_X1000": alignment["GOLD"],
    }
    report = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        **{"V73_AXIS_" + key: measures[key] for key in FIELDS},
    }
    if not (
        len(FIELDS) == 27 and len(report) == 30
        and all(type(value) is int and 0 <= value <= 100000000
                for value in report.values())
        and all(1 <= outcomes[m]["DISTINCT"] <= T.VOCAB_SIZE and
                0 <= outcomes[m]["CORRECT"] <= 9170 and
                0 <= outcomes[m]["TOP1_SHARE_BP"] <= 10000 for m in MODES)
        and 0 <= alignment["WIN"] <= 1000
        and 0 <= alignment["GOLD"] <= 1000
    ):
        raise RuntimeError("V73 30-field integer schema invalid")
    return report


def main():
    v64 = imported("v73_v64_preflight", V64)
    v67 = imported("v73_v67_ranks", V67)
    v69 = imported("v73_v69_scores", V69)
    v72 = imported("v73_v72_spectrum", V72)
    prev = prerequisite(v64.read_json)
    model, device, streams, validation = v64.preflight()
    if sum(map(len, streams.values())) != 345:
        raise RuntimeError("V73 TRAIN inventory changed")
    h, gold, weights, original = collect(
        model, device, validation, v69, v67.stable_true_ranks)
    geometry = v72.spectral_summary(h)
    mean = geometry["mean"]
    axes, spectrum = principal_axes(h)
    if round(10000 * geometry["center"][0]) != spectrum["PC1_BP"]:
        raise RuntimeError("V73 spectrum disagrees with frozen V72 calculation")
    outcomes, changes, byte, merge, alignment = measure_modes(
        h, gold, weights, axes, mean)
    report = build_report(spectrum, outcomes, changes, byte,
                          merge, alignment, original, prev)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(report.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
