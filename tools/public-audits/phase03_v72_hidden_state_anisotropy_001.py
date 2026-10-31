#!/usr/bin/env python3
"""V72 read-only spectral geometry of frozen V62 output-head hidden states.

No parameter updates, BLIND, prompts, token IDs or per-position material leave
the ephemeral process. GOGIT publishes only 30 aggregate integers.
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
V71 = AUDITS / "phase03_v71_output_dominance_attribution_001.py"
V71_STEP = "PHASE03-SMOLTALK-V71-OUTPUT-DOMINANCE-ATTRIBUTION-001"
BATCH = 4
CHUNK = 1024
FIELDS = (
    "PASS", "BLIND_ACCESS", "VAL_LEXICAL", "MODEL_DIM",
    "ORIG_CE_X1000", "ORIG_DISTINCT", "ORIG_TOP1_SHARE_BP",
    "MEAN_ENERGY_BP", "RAW_PC1_SHARE_BP", "RAW_PC5_SHARE_BP",
    "CENTER_PC1_SHARE_BP", "CENTER_PC5_SHARE_BP",
    "RAW_PARTICIPATION_X100", "CENTER_PARTICIPATION_X100",
    "PAIR_COS_SHIFT_X1000", "MEAN_NORM_X1000", "H_NORM_MEAN_X1000",
    "CENTER_DISTINCT", "CENTER_TOP1_SHARE_BP", "CENTER_SWITCH",
    "CENTER_CORRECT", "ORIG_CORRECT",
    "CENTER_GOLD_BYTE_DEF_X1000", "CENTER_GOLD_MERGE_DEF_X1000",
    "MEAN_PC1_ABS_COS_X1000", "CENTER_SWITCH_BYTE",
    "CENTER_SWITCH_MERGE",
)


def imported(name: str, path: Path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Reviewed dependency missing or unsafe")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Reviewed dependency cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_v71(read_json):
    report = read_json(HISTORY / (V71_STEP + ".json"))
    metrics = report.get("metrics", {})
    if not (
        report.get("step_id") == V71_STEP
        and report.get("producer") ==
            "tools/public-audits/phase03_v71_output_dominance_attribution_001.py"
        and report.get("producer_sha256") ==
            hashlib.sha256(V71.read_bytes()).hexdigest()
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict) and len(metrics) == 30
        and all(metrics.get(k) == 0 for k in (
            "SEMANTIC_VALIDATION_COMPLETE", "TRAINING_AUTHORIZED",
            "TRAINING_STARTED", "V71_ATTR_BLIND_ACCESS"))
        and metrics.get("V71_ATTR_PASS") == 1
        and metrics.get("V71_ATTR_VAL_LEXICAL") == 9170
        and metrics.get("V71_ATTR_BYTE_TARGETS") == 4876
        and metrics.get("V71_ATTR_MERGE_TARGETS") == 4294
        and metrics.get("V71_ATTR_ORIG_CE_X1000") == 4732
        and metrics.get("V71_ATTR_ORIG_DISTINCT") == 5
        and metrics.get("V71_ATTR_ORIG_TOP1_SHARE_BP") == 7255
        and sum(metrics.get("V71_ATTR_CORRECT_" + x, -1)
                for x in ("BOTH", "ORIG_ONLY", "FULL_ONLY", "NEITHER")) == 9170
    ):
        raise RuntimeError("V71 source fingerprint or immutable metrics invalid")
    return metrics


def spectral_summary(hidden):
    """Uncentered and centered 128x128 second moments, deterministic FP64."""
    if hidden.ndim != 2 or hidden.shape != (9170, 128):
        raise RuntimeError("V72 frozen lexical hidden shape mismatch")
    h = hidden.detach().to(dtype=torch.float64, device="cpu")
    if not torch.isfinite(h).all():
        raise RuntimeError("V72 nonfinite hidden state")
    norm = torch.linalg.vector_norm(h, dim=1)
    if (norm <= 1e-12).any():
        raise RuntimeError("V72 zero-norm hidden state")
    mean = h.mean(0)
    centered = h - mean
    raw_cov = h.T @ h / h.shape[0]
    center_cov = centered.T @ centered / h.shape[0]
    raw_eig = torch.linalg.eigvalsh(raw_cov).clamp_min(0)
    center_eig, center_vec = torch.linalg.eigh(center_cov)
    center_eig = center_eig.clamp_min(0)
    def describe(values):
        mass = values.sum()
        if not torch.isfinite(mass) or mass <= 1e-12:
            raise RuntimeError("V72 degenerate hidden covariance")
        share1 = float(values[-1] / mass)
        share5 = float(values[-5:].sum() / mass)
        participation = float(mass.square() / values.square().sum())
        if not (
            math.isfinite(participation) and
            1 <= participation <= 128.0001 and
            0 <= share1 <= share5 <= 1.000001
        ):
            raise RuntimeError("V72 invalid spectral shape")
        return share1, share5, participation
    raw = describe(raw_eig)
    centered_spec = describe(center_eig)
    mean_norm = float(torch.linalg.vector_norm(mean))
    mean_energy = float(mean.dot(mean) / torch.trace(raw_cov))
    normalized = h / norm[:, None]
    sum_normalized = normalized.sum(0)
    cosine = float(
        (sum_normalized.dot(sum_normalized) - h.shape[0]) /
        (h.shape[0] * (h.shape[0] - 1))
    )
    mean_pc1 = float(
        abs(mean.dot(center_vec[:, -1]) / max(mean_norm, 1e-12))
    )
    if not all(math.isfinite(x) for x in
               (mean_norm, mean_energy, cosine, mean_pc1)):
        raise RuntimeError("V72 invalid mean/cosine values")
    if not (0 <= mean_energy <= 1.000001
            and -1 <= cosine <= 1
            and 0 <= mean_pc1 <= 1.000001):
        raise RuntimeError("V72 out-of-range geometry")
    return {
        "mean": mean.float().to(device=hidden.device),
        "mean_energy": mean_energy, "raw": raw, "center": centered_spec,
        "pair_cos": cosine, "mean_norm": mean_norm,
        "mean_h_norm": float(norm.mean()), "mean_pc1": mean_pc1,
    }


def center_control(hidden, targets, orig_prediction, weight, mean):
    """Read-only comparison after subtracting validation mean from hidden."""
    n = targets.numel()
    if not (hidden.shape == (9170, 128)
            and targets.shape == (9170,)
            and orig_prediction.shape == (9170,)
            and weight.shape == (T.VOCAB_SIZE, 128)
            and mean.shape == (128,)):
        raise RuntimeError("V72 center-control shapes changed")
    counts = torch.zeros(T.VOCAB_SIZE, device=hidden.device, dtype=torch.long)
    summary = {
        "switch": 0, "switch_byte": 0, "switch_merge": 0,
        "correct": 0, "orig_correct": 0,
        "byte_deficit": 0.0, "merge_deficit": 0.0,
    }
    for start in range(0, n, CHUNK):
        stop = min(n, start + CHUNK)
        g = targets[start:stop]
        orig = orig_prediction[start:stop]
        logits = F.linear(hidden[start:stop] - mean, weight)
        if not torch.isfinite(logits).all():
            raise RuntimeError("Nonfinite mean-centered logits")
        prediction = logits.argmax(1)
        changed = prediction.ne(orig)
        byte, merge = g.lt(259), g.ge(259)
        summary["switch"] += int(changed.sum().item())
        summary["switch_byte"] += int((changed & byte).sum().item())
        summary["switch_merge"] += int((changed & merge).sum().item())
        summary["correct"] += int(prediction.eq(g).sum().item())
        summary["orig_correct"] += int(orig.eq(g).sum().item())
        deficit = (logits.max(1).values -
                   logits.gather(1, g[:, None]).squeeze(1)).clamp_min(0)
        summary["byte_deficit"] += float(deficit[byte].sum().item())
        summary["merge_deficit"] += float(deficit[merge].sum().item())
        counts += torch.bincount(prediction, minlength=T.VOCAB_SIZE)
    summary["distinct"] = int(counts.gt(0).sum().item())
    summary["top1_share"] = int(round(counts.max().item() * 10000 / n))
    if not (
        summary["switch"] == summary["switch_byte"] + summary["switch_merge"]
        and int(counts.sum().item()) == n
        and 0 <= summary["correct"] <= n
        and 1 <= summary["distinct"] <= T.VOCAB_SIZE
    ):
        raise RuntimeError("V72 centered prediction accounting mismatch")
    return summary


def evaluate(model, device, validation, v69, ranker):
    if not (
        len(validation) == 36
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr() ==
            model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V72 frozen tied head / validation invalid")
    weights = model.lm_head.weight.detach().float()
    before = weights.clone()
    scores = v69.empty()
    memory, targets, predictions = [], [], []
    taps = []

    def capture(_module, inputs):
        if len(inputs) != 1 or inputs[0].ndim != 3:
            raise RuntimeError("Unexpected V72 hidden-state shape")
        taps.append(inputs[0].detach())

    handle = model.lm_head.register_forward_pre_hook(capture)
    model.eval()
    try:
        with torch.inference_mode():
            for offset in range(0, 36, BATCH):
                batch = validation[offset:offset + BATCH]
                ids = torch.full(
                    (len(batch), max(len(seg.token_ids) for seg in batch)),
                    T.PAD_ID, device=device, dtype=torch.long)
                eos = []
                for row, seg in enumerate(batch):
                    if (seg.token_ids[0] != T.BOS_ID
                            or seg.token_ids[-1] != T.EOS_ID):
                        raise RuntimeError("V72 BOS/EOS boundaries changed")
                    ids[row, :len(seg.token_ids)] = torch.as_tensor(
                        seg.token_ids, device=device, dtype=torch.long)
                    eos.append((row, len(seg.token_ids) - 2))
                with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                    model(ids)
                if len(taps) != 1 or taps[0].shape[:2] != ids.shape:
                    raise RuntimeError("V72 hidden-state hook failure")
                h = taps.pop().float()[:, :-1, :]
                gold = ids[:, 1:]
                valid = gold.ne(T.PAD_ID)
                lexical = valid & gold.ge(3) & gold.lt(T.VOCAB_SIZE)
                with torch.autocast(device_type="cuda", enabled=False):
                    logits = F.linear(h, weights)
                    v69.update_stats(scores, logits, gold, valid, eos, ranker)
                    memory.append(h[lexical].clone())
                    targets.append(gold[lexical].clone())
                    predictions.append(logits[lexical].argmax(1).clone())
    finally:
        handle.remove()
        taps.clear()
    if not torch.equal(weights, before):
        raise RuntimeError("V72 changed frozen projection")
    hidden = torch.cat(memory, dim=0)
    true = torch.cat(targets)
    orig = torch.cat(predictions)
    if not (hidden.shape == (9170, 128)
            and int(true.lt(259).sum().item()) == 4876
            and int(true.ge(259).sum().item()) == 4294):
        raise RuntimeError("V72 frozen lexical sample changed")
    with torch.inference_mode():
        geom = spectral_summary(hidden)
        center = center_control(hidden, true, orig, weights, geom["mean"])
    return geom, center, v69.finalize(scores)


def build_report(geometry, centering, original, v71):
    expected = {
        "CE_X1000": v71["V71_ATTR_ORIG_CE_X1000"],
        "PRED_DISTINCT": v71["V71_ATTR_ORIG_DISTINCT"],
        "TOP1_SHARE_BP": v71["V71_ATTR_ORIG_TOP1_SHARE_BP"],
    }
    if any(original.get(k) != v for k, v in expected.items()):
        raise RuntimeError("V72 original FP32 baseline fails V71 replay")
    orig_correct = (v71["V71_ATTR_CORRECT_BOTH"]
                    + v71["V71_ATTR_CORRECT_ORIG_ONLY"])
    if not (
        centering["orig_correct"] == orig_correct == 2673
        and 0 <= centering["switch"] <= 9170
        and centering["switch"] == centering["switch_byte"]
            + centering["switch_merge"]
        and 1 <= centering["distinct"] <= T.VOCAB_SIZE
        and 0 <= centering["top1_share"] <= 10000
    ):
        raise RuntimeError("V72 center-control replay/accounting invalid")
    scaled = lambda x, scale: int(round(x * scale))
    g, c = geometry, centering
    measurements = {
        "PASS": 1, "BLIND_ACCESS": 0,
        "VAL_LEXICAL": 9170, "MODEL_DIM": 128,
        "ORIG_CE_X1000": original["CE_X1000"],
        "ORIG_DISTINCT": original["PRED_DISTINCT"],
        "ORIG_TOP1_SHARE_BP": original["TOP1_SHARE_BP"],
        "MEAN_ENERGY_BP": scaled(g["mean_energy"], 10000),
        "RAW_PC1_SHARE_BP": scaled(g["raw"][0], 10000),
        "RAW_PC5_SHARE_BP": scaled(g["raw"][1], 10000),
        "CENTER_PC1_SHARE_BP": scaled(g["center"][0], 10000),
        "CENTER_PC5_SHARE_BP": scaled(g["center"][1], 10000),
        "RAW_PARTICIPATION_X100": scaled(g["raw"][2], 100),
        "CENTER_PARTICIPATION_X100": scaled(g["center"][2], 100),
        "PAIR_COS_SHIFT_X1000": scaled(1 + g["pair_cos"], 1000),
        "MEAN_NORM_X1000": scaled(g["mean_norm"], 1000),
        "H_NORM_MEAN_X1000": scaled(g["mean_h_norm"], 1000),
        "CENTER_DISTINCT": c["distinct"],
        "CENTER_TOP1_SHARE_BP": c["top1_share"],
        "CENTER_SWITCH": c["switch"],
        "CENTER_CORRECT": c["correct"],
        "ORIG_CORRECT": c["orig_correct"],
        "CENTER_GOLD_BYTE_DEF_X1000":
            scaled(c["byte_deficit"] / 4876, 1000),
        "CENTER_GOLD_MERGE_DEF_X1000":
            scaled(c["merge_deficit"] / 4294, 1000),
        "MEAN_PC1_ABS_COS_X1000": scaled(g["mean_pc1"], 1000),
        "CENTER_SWITCH_BYTE": c["switch_byte"],
        "CENTER_SWITCH_MERGE": c["switch_merge"],
    }
    output = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        **{"V72_GEOM_" + field: measurements[field] for field in FIELDS},
    }
    if not (
        len(FIELDS) == 27
        and len(output) == 30
        and all(type(value) is int and 0 <= value <= 100000000
                for value in output.values())
        and output["V72_GEOM_RAW_PC1_SHARE_BP"] <=
            output["V72_GEOM_RAW_PC5_SHARE_BP"] <= 10000
        and output["V72_GEOM_CENTER_PC1_SHARE_BP"] <=
            output["V72_GEOM_CENTER_PC5_SHARE_BP"] <= 10000
        and 0 <= output["V72_GEOM_MEAN_ENERGY_BP"] <= 10000
        and 0 <= output["V72_GEOM_PAIR_COS_SHIFT_X1000"] <= 2000
    ):
        raise RuntimeError("V72 30-field GOGIT schema failed")
    return output


def main():
    v64 = imported("v72_v64_preflight", V64)
    v67 = imported("v72_v67_ranks", V67)
    v69 = imported("v72_v69_stats", V69)
    baseline = require_v71(v64.read_json)
    model, device, training, validation = v64.preflight()
    if sum(map(len, training.values())) != 345:
        raise RuntimeError("V72 frozen TRAIN inventory mismatch")
    geometry, centering, original = evaluate(
        model, device, validation, v69, v67.stable_true_ranks)
    report = build_report(geometry, centering, original, baseline)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(report.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
