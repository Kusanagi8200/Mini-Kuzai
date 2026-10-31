#!/usr/bin/env python3
"""V71 frozen V62 output-dominance attribution, numerical-only and read-only."""
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
BATCH = 4
STEPS = {
    "67": ("PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001",
           "phase03_v67_output_concentration_001.py", "V67_CONC_BLIND_ACCESS"),
    "68": ("PHASE03-SMOLTALK-V68-OUTPUT-HEAD-001",
           "phase03_v68_output_head_001.py", "V68_HEAD_BLIND_ACCESS"),
    "69": ("PHASE03-SMOLTALK-V69-OUTPUT-NORM-COUNTERFACTUAL-001",
           "phase03_v69_output_norm_counterfactual_001.py", "V69_NORM_BLIND_ACCESS"),
    "70": ("PHASE03-SMOLTALK-V70-PRECISION-CONTROL-001",
           "phase03_v70_precision_control_001.py", "V70_CTRL_BLIND_ACCESS"),
}
FIELDS = (
    "PASS", "BLIND_ACCESS", "VAL_LEXICAL", "BYTE_TARGETS", "MERGE_TARGETS",
    "ORIG_CE_X1000", "FULL_CE_X1000",
    "ORIG_DISTINCT", "FULL_DISTINCT",
    "ORIG_TOP1_SHARE_BP", "FULL_TOP1_SHARE_BP",
    "SWITCH_TOTAL", "SWITCH_BYTE", "SWITCH_MERGE",
    "CORRECT_BOTH", "CORRECT_ORIG_ONLY", "CORRECT_FULL_ONLY",
    "CORRECT_NEITHER", "ORIG_MARGIN_MEAN_X1000", "FULL_MARGIN_MEAN_X1000",
    "ORIG_GOLD_DEF_BYTE_X1000", "ORIG_GOLD_DEF_MERGE_X1000",
    "FULL_GOLD_DEF_BYTE_X1000", "FULL_GOLD_DEF_MERGE_X1000",
    "NORM_RATIO_X1000", "COS_WIN_SHIFT_X1000", "COS_GOLD_SHIFT_X1000",
)


def import_reviewed(name: str, source: Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("Frozen helper missing or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Frozen helper import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prior_reports(read_json):
    result = {}
    for version, (step, producer, blind_key) in STEPS.items():
        source = AUDITS / producer
        report = read_json(HISTORY / (step + ".json"))
        metrics = report.get("metrics", {})
        if not (
            source.is_file() and not source.is_symlink()
            and report.get("step_id") == step
            and report.get("producer") == "tools/public-audits/" + producer
            and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
            and report.get("semantic_validation_complete") is False
            and report.get("training_authorized") is False
            and report.get("private_conversation_data_included") is False
            and isinstance(metrics, dict) and len(metrics) == 30
            and all(metrics.get(key) == 0 for key in (
                "SEMANTIC_VALIDATION_COMPLETE", "TRAINING_AUTHORIZED",
                "TRAINING_STARTED", blind_key))
            and metrics.get("V" + version + "_" + {
                "67": "CONC", "68": "HEAD", "69": "NORM", "70": "CTRL",
            }[version] + "_PASS") == 1
            and hashlib.sha256(source.read_bytes()).hexdigest()
            == report.get("producer_sha256")
        ):
            raise RuntimeError("V" + version + " immutable GOGIT prerequisite failed")
        result[version] = metrics
    a, b, c, d = (result[v] for v in ("67", "68", "69", "70"))
    if not (
        a.get("V67_CONC_VAL_LEXICAL") == 9170
        and a.get("V67_CONC_GOLD_DISTINCT") == 606
        and b.get("V68_HEAD_TIED_WEIGHTS") == 1
        and b.get("V68_HEAD_HAS_BIAS") == 0
        and c.get("V69_NORM_FULL_CE_X1000") == 5048
        and d.get("V70_CTRL_VAL_LEXICAL") == 9170
        and d.get("V70_CTRL_FP32_CE_X1000") == 4732
        and d.get("V70_CTRL_FULL_CE_X1000") == 5048
    ):
        raise RuntimeError("V67-V70 numeric identities changed")
    return result


def new_attribution():
    return {
        "lexical": 0, "byte": 0, "merge": 0,
        "switch": 0, "switch_byte": 0, "switch_merge": 0,
        "both": 0, "orig_only": 0, "full_only": 0, "neither": 0,
        "orig_margin": 0.0, "full_margin": 0.0,
        "orig_byte_def": 0.0, "orig_merge_def": 0.0,
        "full_byte_def": 0.0, "full_merge_def": 0.0,
        "winner_norm": 0.0, "gold_norm": 0.0,
        "cos_win": 0.0, "cos_gold": 0.0,
    }


def attribute_batch(stats, hidden, original, full, gold, lexical, weights):
    if not lexical.any():
        return
    h, g = hidden[lexical], gold[lexical]
    a, b = original[lexical], full[lexical]
    if not (torch.isfinite(h).all() and torch.isfinite(a).all()
            and torch.isfinite(b).all()):
        raise RuntimeError("Nonfinite V71 activation/logits")
    orig, neutral = a.argmax(1), b.argmax(1)
    byte, merged = g.lt(259), g.ge(259)
    switched = orig.ne(neutral)
    orig_correct, full_correct = orig.eq(g), neutral.eq(g)
    n = g.numel()
    stats["lexical"] += n
    stats["byte"] += int(byte.sum().item())
    stats["merge"] += int(merged.sum().item())
    stats["switch"] += int(switched.sum().item())
    stats["switch_byte"] += int((switched & byte).sum().item())
    stats["switch_merge"] += int((switched & merged).sum().item())
    stats["both"] += int((orig_correct & full_correct).sum().item())
    stats["orig_only"] += int((orig_correct & ~full_correct).sum().item())
    stats["full_only"] += int((~orig_correct & full_correct).sum().item())
    stats["neither"] += int((~orig_correct & ~full_correct).sum().item())
    norms = torch.linalg.vector_norm(weights, dim=1)
    selected = weights[orig]
    expected = weights[g]
    stats["winner_norm"] += float(norms[orig].sum().item())
    stats["gold_norm"] += float(norms[g].sum().item())
    hnorm = torch.linalg.vector_norm(h, dim=1)
    winner_cos = (h * selected).sum(1) / (
        hnorm * norms[orig]).clamp_min(1e-9)
    gold_cos = (h * expected).sum(1) / (
        hnorm * norms[g]).clamp_min(1e-9)
    stats["cos_win"] += float(winner_cos.clamp(-1, 1).sum().item())
    stats["cos_gold"] += float(gold_cos.clamp(-1, 1).sum().item())
    for name, logits in (("orig", a), ("full", b)):
        top = logits.topk(2, dim=1).values
        margin = (top[:, 0] - top[:, 1]).clamp_min(0)
        deficit = (logits.max(1).values -
                   logits.gather(1, g[:, None]).squeeze(1)).clamp_min(0)
        stats[name + "_margin"] += float(margin.sum().item())
        stats[name + "_byte_def"] += float(deficit[byte].sum().item())
        stats[name + "_merge_def"] += float(deficit[merged].sum().item())


def verify_v70_replay(original: dict, full: dict, metrics: dict):
    for mode, observed in (("FP32", original), ("FULL", full)):
        for field in ("CE_X1000", "PRED_DISTINCT", "TOP1_SHARE_BP",
                      "MERGE_TOP1_BP", "MERGE_TOP5_BP", "EOS_TOP1"):
            expected = metrics.get("V70_CTRL_" + mode + "_" + field)
            if type(expected) is not int or observed.get(field) != expected:
                raise RuntimeError("V71 disagrees with frozen V70 " + mode + " " + field)
    if not (
        original["CE_X1000"] == 4732
        and full["CE_X1000"] == 5048
        and original["PRED_DISTINCT"] == 5
        and full["PRED_DISTINCT"] == 7
    ):
        raise RuntimeError("V71 original/FULL baseline identity failed")


def build_report(stats, original, full, v70):
    verify_v70_replay(original, full, v70)
    n, byte, merged = (stats[k] for k in ("lexical", "byte", "merge"))
    if not (
        n == 9170 and byte == 4876 and merged == 4294
        and stats["switch"] == stats["switch_byte"] + stats["switch_merge"]
        and n == (stats["both"] + stats["orig_only"]
                  + stats["full_only"] + stats["neither"])
        and stats["switch"] >= stats["orig_only"] + stats["full_only"]
        and stats["gold_norm"] > 0
        and all(math.isfinite(value) for value in stats.values())
    ):
        raise RuntimeError("V71 attribution inventory or numeric invariant failed")
    rounded = lambda x: int(round(x))
    fields = {
        "PASS": 1, "BLIND_ACCESS": 0, "VAL_LEXICAL": n,
        "BYTE_TARGETS": byte, "MERGE_TARGETS": merged,
        "ORIG_CE_X1000": original["CE_X1000"],
        "FULL_CE_X1000": full["CE_X1000"],
        "ORIG_DISTINCT": original["PRED_DISTINCT"],
        "FULL_DISTINCT": full["PRED_DISTINCT"],
        "ORIG_TOP1_SHARE_BP": original["TOP1_SHARE_BP"],
        "FULL_TOP1_SHARE_BP": full["TOP1_SHARE_BP"],
        "SWITCH_TOTAL": stats["switch"],
        "SWITCH_BYTE": stats["switch_byte"],
        "SWITCH_MERGE": stats["switch_merge"],
        "CORRECT_BOTH": stats["both"],
        "CORRECT_ORIG_ONLY": stats["orig_only"],
        "CORRECT_FULL_ONLY": stats["full_only"],
        "CORRECT_NEITHER": stats["neither"],
        "ORIG_MARGIN_MEAN_X1000": rounded(1000 * stats["orig_margin"] / n),
        "FULL_MARGIN_MEAN_X1000": rounded(1000 * stats["full_margin"] / n),
        "ORIG_GOLD_DEF_BYTE_X1000": rounded(1000 * stats["orig_byte_def"] / byte),
        "ORIG_GOLD_DEF_MERGE_X1000": rounded(1000 * stats["orig_merge_def"] / merged),
        "FULL_GOLD_DEF_BYTE_X1000": rounded(1000 * stats["full_byte_def"] / byte),
        "FULL_GOLD_DEF_MERGE_X1000": rounded(1000 * stats["full_merge_def"] / merged),
        "NORM_RATIO_X1000": rounded(1000 * stats["winner_norm"] / stats["gold_norm"]),
        "COS_WIN_SHIFT_X1000": rounded(1000 * (1 + stats["cos_win"] / n)),
        "COS_GOLD_SHIFT_X1000": rounded(1000 * (1 + stats["cos_gold"] / n)),
    }
    report = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        **{"V71_ATTR_" + name: fields[name] for name in FIELDS},
    }
    if (
        len(report) != 30 or len(fields) != len(FIELDS)
        or any(type(v) is not int or not 0 <= v <= 100_000_000
               for v in report.values())
        or not 0 <= report["V71_ATTR_COS_WIN_SHIFT_X1000"] <= 2000
        or not 0 <= report["V71_ATTR_COS_GOLD_SHIFT_X1000"] <= 2000
    ):
        raise RuntimeError("V71 public GOGIT metric schema invalid")
    return report


def evaluate(model, device, validation, v69, ranker):
    if not (
        len(validation) == 36
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr() ==
            model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V71 frozen model identity failed")
    weights = model.lm_head.weight.detach().float()
    before = weights.clone()
    neutral_weights = v69.equalize_rows(weights, 1.0)
    scores = {mode: v69.empty() for mode in ("FP32", "FULL")}
    stats = new_attribution()
    taps = []

    def capture(_module, inputs):
        if len(inputs) != 1 or inputs[0].ndim != 3:
            raise RuntimeError("V71 output head input changed")
        taps.append(inputs[0].detach())

    handle = model.lm_head.register_forward_pre_hook(capture)
    model.eval()
    try:
        with torch.inference_mode():
            for start in range(0, 36, BATCH):
                chunk = validation[start:start + BATCH]
                ids = torch.full(
                    (len(chunk), max(len(seg.token_ids) for seg in chunk)),
                    T.PAD_ID, dtype=torch.long, device=device)
                eos_positions = []
                for row, seg in enumerate(chunk):
                    if (seg.token_ids[0] != T.BOS_ID
                            or seg.token_ids[-1] != T.EOS_ID):
                        raise RuntimeError("V71 boundaries differ from frozen V62")
                    ids[row, :len(seg.token_ids)] = torch.as_tensor(
                        seg.token_ids, dtype=torch.long, device=device)
                    eos_positions.append((row, len(seg.token_ids) - 2))
                with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                    model(ids)
                if len(taps) != 1 or taps[0].shape[:2] != ids.shape:
                    raise RuntimeError("V71 LM head tap failed")
                hidden = taps.pop().float()[:, :-1, :]
                gold = ids[:, 1:]
                valid = gold.ne(T.PAD_ID)
                lexical = valid & gold.ge(3) & gold.lt(T.VOCAB_SIZE)
                with torch.autocast(device_type="cuda", enabled=False):
                    original = F.linear(hidden, weights)
                    full = F.linear(hidden, neutral_weights)
                    for name, logits in (("FP32", original), ("FULL", full)):
                        v69.update_stats(scores[name], logits, gold,
                                         valid, eos_positions, ranker)
                    attribute_batch(stats, hidden, original, full,
                                    gold, lexical, weights)
    finally:
        handle.remove()
        taps.clear()
    if not torch.equal(weights, before):
        raise RuntimeError("V71 unexpectedly modified output weights")
    return stats, {k: v69.finalize(v) for k, v in scores.items()}


def main():
    v64 = import_reviewed("v71_v64_preflight", V64)
    v67 = import_reviewed("v71_v67_ranks", V67)
    v69 = import_reviewed("v71_v69_controls", V69)
    priors = prior_reports(v64.read_json)
    model, device, train, validation = v64.preflight()
    if sum(map(len, train.values())) != 345:
        raise RuntimeError("V71 frozen TRAIN inventory drift")
    stats, compared = evaluate(model, device, validation, v69,
                               v67.stable_true_ranks)
    result = build_report(stats, compared["FP32"], compared["FULL"],
                          priors["70"])
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(result.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
