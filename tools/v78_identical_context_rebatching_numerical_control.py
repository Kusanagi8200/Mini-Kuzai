#!/usr/bin/env python3
"""V78 identical-context rebatching numerical control.

Evaluates the exact same frozen VALIDATION prefixes through the two execution
shapes used by V77: FULL_CONTEXT batch-4 and prefix/rebatch batch-32. The model,
targets, token order, residual profile and logical prefixes remain identical.

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

STEP_ID = "PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001"

PATH_A_BATCH = 4
PATH_B_BATCH = 32
SCORE_CHUNK = 512
GPU_PEAK_LIMIT_MIB = 6144
VAL_LEXICAL = 9170
MODEL_DIM = 128
VOCAB = 1024

DELTA_1E7 = 1e-7
DELTA_1E6 = 1e-6
DELTA_1E5 = 1e-5
NANO_SCALE = 1_000_000_000

V77_SOURCE = ROOT / "tools" / "v77_residual_context_order_sensitivity.py"
V77_REPORT = ROOT / "reports" / "assistant-results" / "history" / (
    "PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.json"
)
V78_START_RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V78-start.json"
PROTOCOL = ROOT / "phases" / (
    "MINI-KUZAI-PHASE-03-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.md"
)

DEPENDENCY_BLOBS = {
    "tools/v77_residual_context_order_sensitivity.py":
        "941df566949291c55da1b4c6b0b6c63ad52dbd37",
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.json":
        "68f7c331942ac50238090fd72e6d3008fe2374a7",
    "automation/dev-flow/receipts/V78-start.json":
        "6d6d01d31693c39464d5bf27e2efec4b787c0937",
    "phases/"
    "MINI-KUZAI-PHASE-03-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.md":
        "f408b734016eed3a33228ca83763b9e7643185ab",
}

METRIC_FIELDS = (
    "SEMANTIC_VALIDATION_COMPLETE",
    "TRAINING_AUTHORIZED",
    "TRAINING_STARTED",
    "V78_PASS",
    "V78_BLIND_ACCESS",
    "V78_VAL_LEXICAL",
    "V78_PATH_A_BATCH",
    "V78_PATH_B_BATCH",
    "V78_PATH_A_CORRECT",
    "V78_PATH_A_DISTINCT",
    "V78_PATH_A_TOP1_SHARE_BP",
    "V78_PATH_B_CORRECT",
    "V78_PATH_B_DISTINCT",
    "V78_PATH_B_TOP1_SHARE_BP",
    "V78_PRED_AGREE",
    "V78_PRED_CHANGED",
    "V78_SHARED_CORRECT",
    "V78_A_ONLY_CORRECT",
    "V78_B_ONLY_CORRECT",
    "V78_ALPHA_SIGN_AGREE",
    "V78_ALPHA_SIGN_CHANGED",
    "V78_ALPHA_CORR_ABS_BP",
    "V78_ALPHA_DELTA_GT_1E7",
    "V78_ALPHA_DELTA_GT_1E6",
    "V78_ALPHA_DELTA_GT_1E5",
    "V78_ALPHA_MAX_ABS_NANO",
    "V78_ALPHA_MEAN_ABS_NANO",
    "V78_IDENTICAL_PREFIXES",
    "V78_INPUT_MATCHES",
    "V78_COVERAGE_BP",
)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V78 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V78 expected JSON object")
    return value


def imported(name: str, source: Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("V78 reviewed dependency unavailable or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V78 dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_blob(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V78 pinned source missing or unsafe")
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError("V78 Git blob calculation failed")
    return proc.stdout.strip()


def verify_dependency_blobs() -> None:
    for relative, expected in DEPENDENCY_BLOBS.items():
        if git_blob(ROOT / relative) != expected:
            raise RuntimeError("V78 frozen dependency blob mismatch")


def verify_start_receipt() -> None:
    receipt = read_json(V78_START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V78"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/9"
        and receipt.get("source_commit")
        == "f72f0323fb9f8eb16a0ba095f9fd3f6572194e6b"
    ):
        raise RuntimeError("V78 official START receipt absent or invalid")


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
        raise RuntimeError("V78 frozen V77 report integrity gate failed")
    return metrics


def identical_prefix(prefix) -> tuple[int, ...]:
    values = tuple(prefix)
    if not values or any(type(x) is not int for x in values):
        raise ValueError("V78 invalid prefix")
    if values[0] != T.BOS_ID:
        raise ValueError("V78 prefix must begin with BOS")
    if any(not 0 <= x < VOCAB for x in values):
        raise ValueError("V78 prefix token out of range")
    if T.PAD_ID in values:
        raise ValueError("V78 real prefix may not contain PAD")
    copied = tuple(values)
    if copied != values:
        raise RuntimeError("V78 identity transform changed prefix")
    return copied


def sign_classes(values: torch.Tensor) -> torch.Tensor:
    x = values.detach().to(device="cpu", dtype=torch.float64)
    if x.ndim != 1 or x.numel() == 0 or not torch.isfinite(x).all():
        raise ValueError("V78 invalid alpha vector")
    return torch.sign(x).to(dtype=torch.int8)


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
        "A_ONLY_CORRECT": 0,
        "B_ONLY_CORRECT": 0,
        "SIGN_AGREE": 0,
        "SIGN_CHANGED": 0,
        "DELTA_GT_1E7": 0,
        "DELTA_GT_1E6": 0,
        "DELTA_GT_1E5": 0,
        "IDENTICAL_PREFIXES": 0,
        "INPUT_MATCHES": 0,
    }


def update_pair_stats(
    stats: dict,
    alpha_a: torch.Tensor,
    alpha_b: torch.Tensor,
    pred_a: torch.Tensor,
    pred_b: torch.Tensor,
    gold: torch.Tensor,
    identical_prefixes: int,
    input_matches: int,
) -> None:
    x = alpha_a.detach().to(device="cpu", dtype=torch.float64)
    y = alpha_b.detach().to(device="cpu", dtype=torch.float64)
    pa = pred_a.detach().to(device="cpu", dtype=torch.long)
    pb = pred_b.detach().to(device="cpu", dtype=torch.long)
    target = gold.detach().to(device="cpu", dtype=torch.long)

    if not (
        x.ndim == 1
        and x.shape == y.shape == pa.shape == pb.shape == target.shape
        and x.numel() > 0
        and torch.isfinite(x).all()
        and torch.isfinite(y).all()
        and type(identical_prefixes) is int
        and type(input_matches) is int
        and 0 <= identical_prefixes <= x.numel()
        and 0 <= input_matches <= x.numel()
    ):
        raise ValueError("V78 invalid paired accounting input")

    n = int(x.numel())
    sa = sign_classes(x)
    sb = sign_classes(y)
    a_correct = pa.eq(target)
    b_correct = pb.eq(target)
    pred_same = pa.eq(pb)
    sign_same = sa.eq(sb)
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
    stats["SHARED_CORRECT"] += int((a_correct & b_correct).sum())
    stats["A_ONLY_CORRECT"] += int((a_correct & ~b_correct).sum())
    stats["B_ONLY_CORRECT"] += int((~a_correct & b_correct).sum())
    stats["SIGN_AGREE"] += int(sign_same.sum())
    stats["SIGN_CHANGED"] += int((~sign_same).sum())
    stats["DELTA_GT_1E7"] += int((delta > DELTA_1E7).sum())
    stats["DELTA_GT_1E6"] += int((delta > DELTA_1E6).sum())
    stats["DELTA_GT_1E5"] += int((delta > DELTA_1E5).sum())
    stats["IDENTICAL_PREFIXES"] += identical_prefixes
    stats["INPUT_MATCHES"] += input_matches


def finalize_pair_stats(stats: dict, expected: int) -> dict:
    n = stats.get("COUNT")
    if type(n) is not int or n != expected or n <= 1:
        raise RuntimeError("V78 paired coverage failed")

    for key in (
        "SUM_X", "SUM_Y", "SUM_X2", "SUM_Y2", "SUM_XY",
        "SUM_ABS_DELTA", "MAX_ABS_DELTA",
    ):
        if not math.isfinite(stats[key]):
            raise RuntimeError("V78 nonfinite paired statistic")

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
        raise RuntimeError("V78 degenerate alpha correlation")

    corr_abs = abs(cov_num) / math.sqrt(var_x * var_y)
    if not math.isfinite(corr_abs) or not 0.0 <= corr_abs <= 1.0000001:
        raise RuntimeError("V78 invalid alpha correlation")
    corr_abs = min(corr_abs, 1.0)

    for left, right in (
        ("PRED_AGREE", "PRED_CHANGED"),
        ("SIGN_AGREE", "SIGN_CHANGED"),
    ):
        if stats[left] + stats[right] != expected:
            raise RuntimeError("V78 paired partition accounting failed")

    if not (
        stats["IDENTICAL_PREFIXES"] == expected
        and stats["INPUT_MATCHES"] == expected
        and 0 <= stats["SHARED_CORRECT"] <= expected
        and 0 <= stats["A_ONLY_CORRECT"] <= expected
        and 0 <= stats["B_ONLY_CORRECT"] <= expected
        and 0 <= stats["DELTA_GT_1E5"] <= stats["DELTA_GT_1E6"]
        <= stats["DELTA_GT_1E7"] <= expected
    ):
        raise RuntimeError("V78 paired result outside admissible range")

    max_nano = round(stats["MAX_ABS_DELTA"] * NANO_SCALE)
    mean_nano = round(stats["SUM_ABS_DELTA"] * NANO_SCALE / expected)
    if not (
        0 <= max_nano <= 100_000_000
        and 0 <= mean_nano <= 100_000_000
    ):
        raise RuntimeError("V78 nano-scaled alpha delta outside public range")

    return {
        "PRED_AGREE": stats["PRED_AGREE"],
        "PRED_CHANGED": stats["PRED_CHANGED"],
        "SHARED_CORRECT": stats["SHARED_CORRECT"],
        "A_ONLY_CORRECT": stats["A_ONLY_CORRECT"],
        "B_ONLY_CORRECT": stats["B_ONLY_CORRECT"],
        "SIGN_AGREE": stats["SIGN_AGREE"],
        "SIGN_CHANGED": stats["SIGN_CHANGED"],
        "ALPHA_CORR_ABS_BP": round(corr_abs * 10000),
        "DELTA_GT_1E7": stats["DELTA_GT_1E7"],
        "DELTA_GT_1E6": stats["DELTA_GT_1E6"],
        "DELTA_GT_1E5": stats["DELTA_GT_1E5"],
        "ALPHA_MAX_ABS_NANO": max_nano,
        "ALPHA_MEAN_ABS_NANO": mean_nano,
        "IDENTICAL_PREFIXES": stats["IDENTICAL_PREFIXES"],
        "INPUT_MATCHES": stats["INPUT_MATCHES"],
    }


def score_validation(
    V,
    model,
    device,
    validation: list,
    train_mean: torch.Tensor,
    train_pc1: torch.Tensor,
    residual_profile: torch.Tensor,
    unigram: int,
):
    if len(validation) != 36:
        raise RuntimeError("V78 frozen VALIDATION segment count changed")
    if not (
        train_mean.shape == train_pc1.shape == (MODEL_DIM,)
        and residual_profile.shape == (VOCAB,)
        and torch.isfinite(residual_profile).all()
        and 3 <= unigram < VOCAB
        and model.lm_head.bias is None
        and model.lm_head.weight.data_ptr() == model.token_embedding.weight.data_ptr()
    ):
        raise RuntimeError("V78 scoring geometry/output-head gate failed")

    mean_t = train_mean.to(device=device, dtype=torch.float32)
    pc1_t = train_pc1.to(device=device, dtype=torch.float32)
    residual_t = residual_profile.to(device=device, dtype=torch.float32)

    outcomes = {"A": V.empty_outcome(), "B": V.empty_outcome()}
    pairs = empty_pair_stats()
    lexical_total = 0
    taps = []

    def capture(_module, inputs):
        if (
            len(inputs) != 1
            or inputs[0].ndim != 3
            or inputs[0].shape[-1] != MODEL_DIM
        ):
            raise RuntimeError("V78 output-head hidden state shape changed")
        taps.append(inputs[0].detach())

    handle = model.lm_head.register_forward_pre_hook(capture)
    model.eval()
    try:
        with torch.inference_mode():
            for start in range(0, len(validation), PATH_A_BATCH):
                group = validation[start : start + PATH_A_BATCH]
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
                        raise RuntimeError("V78 VALIDATION boundary changed")
                    ids[row, : len(tokens)] = torch.as_tensor(
                        tokens, dtype=torch.long, device=device
                    )

                hidden = V._forward_hidden(model, ids, taps)
                jobs_prefix = []
                jobs_gold = []
                jobs_alpha_a = []

                for row, seg in enumerate(group):
                    tokens = tuple(seg.token_ids)
                    row_hidden = hidden[row]
                    for target_index in range(1, len(tokens)):
                        target = tokens[target_index]
                        if not 3 <= target < VOCAB:
                            continue
                        prefix = tokens[:target_index]
                        if not prefix or prefix[-1] != tokens[target_index - 1]:
                            raise RuntimeError("V78 prefix/target alignment failed")
                        alpha = torch.dot(
                            row_hidden[target_index - 1] - mean_t,
                            pc1_t,
                        )
                        if not torch.isfinite(alpha):
                            raise RuntimeError("V78 nonfinite PATH_A alpha")
                        jobs_prefix.append(prefix)
                        jobs_gold.append(target)
                        jobs_alpha_a.append(alpha)

                del hidden, ids

                if not jobs_prefix:
                    raise RuntimeError("V78 empty VALIDATION group")

                alpha_a_all = torch.stack(jobs_alpha_a)
                gold_all = torch.as_tensor(
                    jobs_gold,
                    dtype=torch.long,
                    device=device,
                )
                if alpha_a_all.shape != gold_all.shape:
                    raise RuntimeError("V78 PATH_A paired shape mismatch")

                lexical_total += int(gold_all.numel())

                for offset in range(0, len(jobs_prefix), PATH_B_BATCH):
                    stop = min(offset + PATH_B_BATCH, len(jobs_prefix))
                    original = jobs_prefix[offset:stop]
                    copied = [identical_prefix(prefix) for prefix in original]

                    prefix_matches = sum(
                        int(tuple(a) == tuple(b))
                        for a, b in zip(original, copied)
                    )
                    input_matches = prefix_matches
                    if not (
                        prefix_matches == len(copied)
                        and input_matches == len(copied)
                    ):
                        raise RuntimeError("V78 identical-input invariant failed")

                    max_len = max(len(prefix) for prefix in copied)
                    b_ids = torch.full(
                        (len(copied), max_len),
                        T.PAD_ID,
                        dtype=torch.long,
                        device=device,
                    )
                    for row, prefix in enumerate(copied):
                        b_ids[row, : len(prefix)] = torch.as_tensor(
                            prefix,
                            dtype=torch.long,
                            device=device,
                        )

                    b_hidden = V._forward_hidden(model, b_ids, taps)
                    rows = torch.arange(
                        len(copied),
                        device=device,
                        dtype=torch.long,
                    )
                    last = torch.as_tensor(
                        [len(prefix) - 1 for prefix in copied],
                        device=device,
                        dtype=torch.long,
                    )
                    selected = b_hidden[rows, last]
                    alpha_b = (selected - mean_t) @ pc1_t
                    if not torch.isfinite(alpha_b).all():
                        raise RuntimeError("V78 nonfinite PATH_B alpha")

                    alpha_a = alpha_a_all[offset:stop]
                    gold = gold_all[offset:stop]

                    logits_a = alpha_a.unsqueeze(1) * residual_t.unsqueeze(0)
                    logits_b = alpha_b.unsqueeze(1) * residual_t.unsqueeze(0)
                    if not (
                        torch.isfinite(logits_a).all()
                        and torch.isfinite(logits_b).all()
                    ):
                        raise RuntimeError("V78 nonfinite residual logits")

                    pred_a = logits_a.argmax(dim=1)
                    pred_b = logits_b.argmax(dim=1)

                    V.update_outcome(outcomes["A"], pred_a, gold, unigram)
                    V.update_outcome(outcomes["B"], pred_b, gold, unigram)
                    update_pair_stats(
                        pairs,
                        alpha_a,
                        alpha_b,
                        pred_a,
                        pred_b,
                        gold,
                        prefix_matches,
                        input_matches,
                    )

                    del b_hidden, b_ids, selected, alpha_b
                    del logits_a, logits_b, pred_a, pred_b

                del alpha_a_all, gold_all
    finally:
        handle.remove()

    if taps:
        raise RuntimeError("V78 hidden-state tap leak")
    if lexical_total != VAL_LEXICAL:
        raise RuntimeError("V78 validation lexical coverage mismatch")

    final = {
        "A": V.finalize_outcome(outcomes["A"], VAL_LEXICAL),
        "B": V.finalize_outcome(outcomes["B"], VAL_LEXICAL),
    }
    paired = finalize_pair_stats(pairs, VAL_LEXICAL)
    return final, paired


def build_metrics(outcomes: dict, pairs: dict) -> dict:
    if set(outcomes) != {"A", "B"}:
        raise RuntimeError("V78 scoring modes incomplete")

    a = outcomes["A"]
    b = outcomes["B"]
    expected_a = {
        "CORRECT": 2594,
        "DISTINCT": 2,
        "TOP1_SHARE_BP": 7043,
        "UNIGRAM_AGREE": 6458,
        "UNIGRAM_SHARED_CORRECT": 2451,
    }
    if a != expected_a:
        raise RuntimeError("V78 frozen V76/V77 PATH_A replay failed")

    for item in (a, b):
        if not (
            0 <= item["CORRECT"] <= VAL_LEXICAL
            and 1 <= item["DISTINCT"] <= VOCAB
            and 0 <= item["TOP1_SHARE_BP"] <= 10000
        ):
            raise RuntimeError("V78 invalid aggregate scoring result")

    if not (
        pairs["PRED_AGREE"] + pairs["PRED_CHANGED"] == VAL_LEXICAL
        and pairs["SIGN_AGREE"] + pairs["SIGN_CHANGED"] == VAL_LEXICAL
        and pairs["SHARED_CORRECT"] + pairs["A_ONLY_CORRECT"] == a["CORRECT"]
        and pairs["SHARED_CORRECT"] + pairs["B_ONLY_CORRECT"] == b["CORRECT"]
        and pairs["IDENTICAL_PREFIXES"] == VAL_LEXICAL
        and pairs["INPUT_MATCHES"] == VAL_LEXICAL
        and 0 <= pairs["ALPHA_CORR_ABS_BP"] <= 10000
    ):
        raise RuntimeError("V78 paired correctness/input partition failed")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V78_PASS": 1,
        "V78_BLIND_ACCESS": 0,
        "V78_VAL_LEXICAL": VAL_LEXICAL,
        "V78_PATH_A_BATCH": PATH_A_BATCH,
        "V78_PATH_B_BATCH": PATH_B_BATCH,
        "V78_PATH_A_CORRECT": a["CORRECT"],
        "V78_PATH_A_DISTINCT": a["DISTINCT"],
        "V78_PATH_A_TOP1_SHARE_BP": a["TOP1_SHARE_BP"],
        "V78_PATH_B_CORRECT": b["CORRECT"],
        "V78_PATH_B_DISTINCT": b["DISTINCT"],
        "V78_PATH_B_TOP1_SHARE_BP": b["TOP1_SHARE_BP"],
        "V78_PRED_AGREE": pairs["PRED_AGREE"],
        "V78_PRED_CHANGED": pairs["PRED_CHANGED"],
        "V78_SHARED_CORRECT": pairs["SHARED_CORRECT"],
        "V78_A_ONLY_CORRECT": pairs["A_ONLY_CORRECT"],
        "V78_B_ONLY_CORRECT": pairs["B_ONLY_CORRECT"],
        "V78_ALPHA_SIGN_AGREE": pairs["SIGN_AGREE"],
        "V78_ALPHA_SIGN_CHANGED": pairs["SIGN_CHANGED"],
        "V78_ALPHA_CORR_ABS_BP": pairs["ALPHA_CORR_ABS_BP"],
        "V78_ALPHA_DELTA_GT_1E7": pairs["DELTA_GT_1E7"],
        "V78_ALPHA_DELTA_GT_1E6": pairs["DELTA_GT_1E6"],
        "V78_ALPHA_DELTA_GT_1E5": pairs["DELTA_GT_1E5"],
        "V78_ALPHA_MAX_ABS_NANO": pairs["ALPHA_MAX_ABS_NANO"],
        "V78_ALPHA_MEAN_ABS_NANO": pairs["ALPHA_MEAN_ABS_NANO"],
        "V78_IDENTICAL_PREFIXES": pairs["IDENTICAL_PREFIXES"],
        "V78_INPUT_MATCHES": pairs["INPUT_MATCHES"],
        "V78_COVERAGE_BP": 10000,
    }

    if not (
        tuple(metrics) == METRIC_FIELDS
        and len(metrics) == 30
        and all(
            type(v) is int and 0 <= v <= 100_000_000
            for v in metrics.values()
        )
    ):
        raise RuntimeError("V78 strict 30-integer metric schema failed")
    return metrics


def compute():
    torch.set_grad_enabled(False)
    verify_dependency_blobs()
    verify_start_receipt()
    verify_v77_report()

    V = imported("v78_frozen_v77_control", V77_SOURCE)
    V.verify_dependency_blobs()
    v76_metrics = V.verify_v76_report()

    v76 = V.imported("v78_frozen_v76_control", V.V76_SOURCE)
    v75 = V.imported("v78_frozen_v75_geometry", V.V75_SOURCE)
    v65 = V.imported("v78_frozen_v65_frequency", V.V65_SOURCE)
    v64 = v75.imported("v78_v64_preflight", v75.V64)

    model, device, streams, validation = v64.preflight()
    if device.type != "cuda":
        raise RuntimeError("V78 requires reviewed CUDA inference path")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("V78 requires CUDA BF16 support")

    if not (
        V.VAL_BATCH == PATH_A_BATCH
        and V.COUNTERFACTUAL_BATCH == PATH_B_BATCH
        and V.SCORE_CHUNK == SCORE_CHUNK
        and V.GPU_PEAK_LIMIT_MIB == GPU_PEAK_LIMIT_MIB
    ):
        raise RuntimeError("V78 inherited V77 runtime constants changed")

    frequency = v65.count_training_tokens(streams)
    v76.frequency_count_vector(frequency, require_frozen=True)
    unigram = v75.most_frequent(frequency)
    if v76_metrics["V76_UNIGRAM_CORRECT"] != 2535:
        raise RuntimeError("V78 frozen unigram provenance changed")

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
        raise RuntimeError("V78 frozen TRAIN PC1 variance replay failed")

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
        raise RuntimeError("V78 frozen V76 residual decomposition replay failed")

    outcomes, pairs = score_validation(
        V,
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
        raise RuntimeError("V78 GPU peak-memory gate exceeded")
    return metrics, peak_mib


def main():
    metrics, _peak_mib = compute()
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
