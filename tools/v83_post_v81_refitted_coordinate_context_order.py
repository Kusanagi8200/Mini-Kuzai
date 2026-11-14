#!/usr/bin/env python3
"""V83 post-V81 refitted-coordinate context-order control.

Replays the V82 final-checkpoint result in the inherited cycle-2 coordinate,
then refits the TRAIN-derived diagnostic coordinate on the same final V81
checkpoint and evaluates the identical frozen VALIDATION prefix pairs.

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

STEP_ID = "PHASE03-SMOLTALK-V83-POST-V81-REFITTED-COORDINATE-CONTEXT-ORDER-001"
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
CYCLE2 = RUN / "checkpoint-cycle-02.pt"
FINAL = RUN / "checkpoint-last.pt"
BEST = RUN / "checkpoint-best.pt"

V82_SOURCE = ROOT / "tools/v82_post_continuation_context_order_replication.py"
V82_SOURCE_BLOB = "1e0d95235d23c0e7c3a56c3ee99257dc81c6f5f8"
V82_REPORT = ROOT / "reports/assistant-results/history/PHASE03-SMOLTALK-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001.json"
V83_START_RECEIPT = ROOT / "automation/dev-flow/receipts/V83-start.json"
PROTOCOL = ROOT / "phases/MINI-KUZAI-PHASE-03-V83-POST-V81-REFITTED-COORDINATE-CONTEXT-ORDER-CONTROL-001.md"

VAL_LEXICAL = 9170
TRAIN_LEXICAL = 294726
SAME_PATH_BATCH = 32
FINAL_STEPS = 136
FINAL_EXPOSURE = 1181302
GPU_PEAK_LIMIT_MIB = 6144
NANO_LIMIT = 2_000_000_000
PUBLIC_MAX = 100_000_000

METRIC_FIELDS = (
    "SEMANTIC_VALIDATION_COMPLETE",
    "TRAINING_AUTHORIZED",
    "TRAINING_STARTED",
    "V83_PASS",
    "V83_BLIND_ACCESS",
    "V83_VAL_LEXICAL",
    "V83_SAME_PATH_BATCH",
    "V83_OLD_REPLAY_PASS",
    "V83_OLD_PRED_CHANGED",
    "V83_OLD_SIGN_CHANGED",
    "V83_REFIT_TRAIN_LEXICAL",
    "V83_REFIT_PC1_VAR_SHARE_BP",
    "V83_AXIS_COS_ABS_BP",
    "V83_RESIDUAL_COS_ABS_BP",
    "V83_REFIT_ORIGINAL_CORRECT",
    "V83_REFIT_REVERSE_CORRECT",
    "V83_REFIT_PRED_CHANGED",
    "V83_REFIT_SIGN_CHANGED",
    "V83_REFIT_ALPHA_CORR_ABS_BP",
    "V83_REFIT_PERTURBED_PREFIXES",
    "V83_REFIT_UNCHANGED_PREFIXES",
    "V83_REFIT_CHANGED_WITHIN_1E3",
    "V83_REFIT_SIGN_WITHIN_1E3",
    "V83_REFIT_BOUNDARY_MAX_NANO_CHANGED",
    "V83_REFIT_BOUNDARY_MEAN_NANO_CHANGED",
    "V83_REFIT_CROSSING_MAX_NANO_CHANGED",
    "V83_REFIT_CROSSING_MEAN_NANO_CHANGED",
    "V83_REFIT_INPUT_INVARIANTS",
    "V83_COVERAGE_BP",
    "V83_GPU_PEAK_MIB",
)


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"V83 reviewed JSON missing or unsafe: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"V83 expected JSON object: {path}")
    return value


def imported(name: str, source: Path):
    if source.is_symlink() or not source.is_file():
        raise RuntimeError("V83 reviewed dependency unavailable or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V83 dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_blob(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError("V83 Git blob calculation failed")
    return result.stdout.strip()


def file_sha256(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("V83 checkpoint missing or unsafe")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def abs_cos_bp(a: torch.Tensor, b: torch.Tensor) -> int:
    if a.ndim != 1 or b.shape != a.shape or a.numel() == 0:
        raise RuntimeError("V83 cosine vector shape mismatch")
    aa = a.detach().to(device="cpu", dtype=torch.float64)
    bb = b.detach().to(device="cpu", dtype=torch.float64)
    den = float(torch.linalg.vector_norm(aa) * torch.linalg.vector_norm(bb))
    if not math.isfinite(den) or den <= 1e-12:
        raise RuntimeError("V83 cosine denominator invalid")
    value = abs(float(torch.dot(aa, bb))) / den
    if not math.isfinite(value) or value > 1.0000001:
        raise RuntimeError("V83 cosine value invalid")
    return round(min(value, 1.0) * 10000)


def verify_start_receipt() -> dict:
    receipt = read_json(V83_START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V83"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url")
        == "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/15"
        and receipt.get("source_commit")
        == "0201cc31d3c10d13a59cf7701ed2bb52b59da4aa"
    ):
        raise RuntimeError("V83 official START receipt absent or invalid")
    return receipt


def verify_v82_report() -> dict:
    report = read_json(V82_REPORT)
    metrics = report.get("metrics")
    if not (
        report.get("step_id")
        == "PHASE03-SMOLTALK-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001"
        and report.get("project") == "Mini-Kuzai"
        and report.get("phase") == "03"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == 30
        and metrics.get("V82_PASS") == 1
        and metrics.get("V82_BLIND_ACCESS") == 0
        and metrics.get("TRAINING_AUTHORIZED") == 0
        and metrics.get("TRAINING_STARTED") == 0
        and metrics.get("V82_VAL_LEXICAL") == VAL_LEXICAL
        and metrics.get("V82_FINAL_STEPS") == FINAL_STEPS
        and metrics.get("V82_FINAL_EXPOSURE") == FINAL_EXPOSURE
        and metrics.get("V82_FINAL_PRED_CHANGED") == 38
        and metrics.get("V82_FINAL_SIGN_CHANGED") == 38
        and metrics.get("V82_FINAL_ORIGINAL_CORRECT") == 2552
        and metrics.get("V82_FINAL_REVERSE_CORRECT") == 2560
        and metrics.get("V82_FINAL_PERTURBED_PREFIXES") == 9062
        and metrics.get("V82_FINAL_UNCHANGED_PREFIXES") == 108
    ):
        raise RuntimeError("V83 immutable V82 report gate failed")
    return metrics


def verify_checkpoint_metadata(
    V82,
    path: Path,
    *,
    expected_step: int,
    expected_exposure: int,
    runtime: dict,
) -> dict:
    return V82.verify_checkpoint_state(
        path,
        expected_step=expected_step,
        expected_exposure=expected_exposure,
        runtime=runtime,
    )


def exact_old_replay_gate(outcomes: dict, pairs: dict, boundary: dict) -> None:
    if not (
        outcomes["ORIGINAL"]["CORRECT"] == 2552
        and outcomes["REVERSE"]["CORRECT"] == 2560
        and pairs["PRED_CHANGED"] == 38
        and pairs["SIGN_CHANGED"] == 38
        and pairs["ALPHA_CORR_ABS_BP"] == 9999
        and pairs["PERTURBED_PREFIXES"] == 9062
        and pairs["UNCHANGED_PREFIXES"] == 108
        and pairs["INPUT_INVARIANTS"] == VAL_LEXICAL
        and boundary["CHANGED_WITHIN_1E3"] == 0
        and boundary["SIGN_WITHIN_1E3"] == 0
        and boundary["BOUNDARY_MAX_NANO_CHANGED"] == 254721880
        and boundary["BOUNDARY_MEAN_NANO_CHANGED"] == 54510100
        and boundary["CROSSING_MAX_NANO_CHANGED"] == 583478630
        and boundary["CROSSING_MEAN_NANO_CHANGED"] == 154062261
    ):
        raise RuntimeError("V83 exact V82 final-checkpoint replay failed")


def build_metrics(
    old_pairs: dict,
    refit_outcomes: dict,
    refit_pairs: dict,
    refit_boundary: dict,
    *,
    refit_share_bp: int,
    axis_cos_bp: int,
    residual_cos_bp: int,
    peak_mib: int,
) -> dict:
    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V83_PASS": 1,
        "V83_BLIND_ACCESS": 0,
        "V83_VAL_LEXICAL": VAL_LEXICAL,
        "V83_SAME_PATH_BATCH": SAME_PATH_BATCH,
        "V83_OLD_REPLAY_PASS": 1,
        "V83_OLD_PRED_CHANGED": old_pairs["PRED_CHANGED"],
        "V83_OLD_SIGN_CHANGED": old_pairs["SIGN_CHANGED"],
        "V83_REFIT_TRAIN_LEXICAL": TRAIN_LEXICAL,
        "V83_REFIT_PC1_VAR_SHARE_BP": refit_share_bp,
        "V83_AXIS_COS_ABS_BP": axis_cos_bp,
        "V83_RESIDUAL_COS_ABS_BP": residual_cos_bp,
        "V83_REFIT_ORIGINAL_CORRECT": refit_outcomes["ORIGINAL"]["CORRECT"],
        "V83_REFIT_REVERSE_CORRECT": refit_outcomes["REVERSE"]["CORRECT"],
        "V83_REFIT_PRED_CHANGED": refit_pairs["PRED_CHANGED"],
        "V83_REFIT_SIGN_CHANGED": refit_pairs["SIGN_CHANGED"],
        "V83_REFIT_ALPHA_CORR_ABS_BP": refit_pairs["ALPHA_CORR_ABS_BP"],
        "V83_REFIT_PERTURBED_PREFIXES": refit_pairs["PERTURBED_PREFIXES"],
        "V83_REFIT_UNCHANGED_PREFIXES": refit_pairs["UNCHANGED_PREFIXES"],
        "V83_REFIT_CHANGED_WITHIN_1E3": refit_boundary["CHANGED_WITHIN_1E3"],
        "V83_REFIT_SIGN_WITHIN_1E3": refit_boundary["SIGN_WITHIN_1E3"],
        "V83_REFIT_BOUNDARY_MAX_NANO_CHANGED": refit_boundary["BOUNDARY_MAX_NANO_CHANGED"],
        "V83_REFIT_BOUNDARY_MEAN_NANO_CHANGED": refit_boundary["BOUNDARY_MEAN_NANO_CHANGED"],
        "V83_REFIT_CROSSING_MAX_NANO_CHANGED": refit_boundary["CROSSING_MAX_NANO_CHANGED"],
        "V83_REFIT_CROSSING_MEAN_NANO_CHANGED": refit_boundary["CROSSING_MEAN_NANO_CHANGED"],
        "V83_REFIT_INPUT_INVARIANTS": refit_pairs["INPUT_INVARIANTS"],
        "V83_COVERAGE_BP": 10000,
        "V83_GPU_PEAK_MIB": peak_mib,
    }
    nano = {
        "V83_REFIT_BOUNDARY_MAX_NANO_CHANGED",
        "V83_REFIT_BOUNDARY_MEAN_NANO_CHANGED",
        "V83_REFIT_CROSSING_MAX_NANO_CHANGED",
        "V83_REFIT_CROSSING_MEAN_NANO_CHANGED",
    }
    if not (
        tuple(metrics) == METRIC_FIELDS
        and len(metrics) == 30
        and all(
            type(v) is int
            and 0 <= v <= (NANO_LIMIT if k in nano else PUBLIC_MAX)
            for k, v in metrics.items()
        )
        and refit_pairs["INPUT_INVARIANTS"] == VAL_LEXICAL
        and refit_pairs["PERTURBED_PREFIXES"] == 9062
        and refit_pairs["UNCHANGED_PREFIXES"] == 108
    ):
        raise RuntimeError("V83 strict public metric schema failed")
    return metrics


def compute():
    torch.set_grad_enabled(False)
    verify_start_receipt()
    verify_v82_report()

    if git_blob(V82_SOURCE) != V82_SOURCE_BLOB:
        raise RuntimeError("V83 V82 source fingerprint mismatch")
    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("V83 runtime missing, unsafe, or training-locked")
    for path in (CYCLE2, FINAL, BEST, PROTOCOL):
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("V83 required dependency missing or unsafe")

    before = {
        "cycle2": file_sha256(CYCLE2),
        "final": file_sha256(FINAL),
        "best": file_sha256(BEST),
    }
    if len(set(before.values())) < 2:
        raise RuntimeError("V83 checkpoint fingerprint gate failed")

    V82 = imported("v83_v82_control", V82_SOURCE)
    V80 = V82.imported("v83_v80_control", V82.V80_SOURCE)
    (
        V79,
        V77,
        model,
        device,
        validation,
        old_mean,
        old_pc1,
        old_residual,
        unigram,
    ) = V82.prepare_frozen_coordinate(V80)

    if device.type != "cuda" or not torch.cuda.is_bf16_supported():
        raise RuntimeError("V83 requires reviewed CUDA BF16 inference path")

    runtime = T.verify_runtime(
        ROOT / "mini_kuzai/phase03_v62_trainer.py",
        ROOT / "tools/train_v62_margin.py",
    )
    final_state = verify_checkpoint_metadata(
        V82,
        FINAL,
        expected_step=FINAL_STEPS,
        expected_exposure=FINAL_EXPOSURE,
        runtime=runtime,
    )
    model.load_state_dict(final_state["model"], strict=True)
    model.eval()
    del final_state

    torch.cuda.reset_peak_memory_stats(device)

    old_outcomes, old_pairs, old_boundary = V82.score_validation(
        V80,
        V79,
        V77,
        model,
        device,
        validation,
        old_mean,
        old_pc1,
        old_residual,
        unigram,
    )
    exact_old_replay_gate(old_outcomes, old_pairs, old_boundary)

    V77.verify_dependency_blobs()
    v76 = V82.imported("v83_v76_control", V77.V76_SOURCE)
    v75 = V82.imported("v83_v75_geometry", V77.V75_SOURCE)
    v65 = V82.imported("v83_v65_frequency", V77.V65_SOURCE)

    streams, inventory = T.build_training_streams()
    if inventory != runtime["training_inventory"]:
        raise RuntimeError("V83 frozen TRAIN inventory changed")
    frequency = v65.count_training_tokens(streams)
    v76.frequency_count_vector(frequency, require_frozen=True)
    if v75.most_frequent(frequency) != unigram:
        raise RuntimeError("V83 TRAIN unigram provenance changed")

    train_segments = v75._segments_in_order(streams)
    count, mean, m2 = v75.collect_geometry(
        model,
        device,
        train_segments,
        TRAIN_LEXICAL,
        v75.TRAIN_BATCH,
    )
    refit_mean, refit_pc1, refit_share = v75.finalize_geometry(
        count,
        mean,
        m2,
        expected_count=TRAIN_LEXICAL,
    )
    repeat_mean, repeat_pc1, repeat_share = v75.finalize_geometry(
        count,
        mean,
        m2,
        expected_count=TRAIN_LEXICAL,
    )
    if not (
        repeat_share == refit_share
        and torch.equal(repeat_mean, refit_mean)
        and abs_cos_bp(repeat_pc1, refit_pc1) == 10000
    ):
        raise RuntimeError("V83 deterministic refit replay failed")

    profiles = v76.decompose_output_profile(
        model.lm_head.weight,
        refit_pc1,
        frequency,
        require_frozen=True,
    )
    refit_residual = profiles["RESIDUAL"]
    axis_cos = abs_cos_bp(old_pc1, refit_pc1)
    residual_cos = abs_cos_bp(old_residual, refit_residual)

    refit_outcomes, refit_pairs, refit_boundary = V82.score_validation(
        V80,
        V79,
        V77,
        model,
        device,
        validation,
        refit_mean,
        refit_pc1,
        refit_residual,
        unigram,
    )

    peak_mib = math.ceil(torch.cuda.max_memory_allocated(device) / (1024 * 1024))
    if peak_mib > GPU_PEAK_LIMIT_MIB:
        raise RuntimeError("V83 GPU peak-memory gate exceeded")

    after = {
        "cycle2": file_sha256(CYCLE2),
        "final": file_sha256(FINAL),
        "best": file_sha256(BEST),
    }
    if after != before:
        raise RuntimeError("V83 checkpoint changed during read-only evaluation")

    metrics = build_metrics(
        old_pairs,
        refit_outcomes,
        refit_pairs,
        refit_boundary,
        refit_share_bp=refit_share,
        axis_cos_bp=axis_cos,
        residual_cos_bp=residual_cos,
        peak_mib=peak_mib,
    )
    return metrics, before


def main():
    metrics, fingerprints = compute()
    print(f"V83_CYCLE2_SHA256={fingerprints['cycle2']}")
    print(f"V83_FINAL_SHA256={fingerprints['final']}")
    print(f"V83_BEST_SHA256={fingerprints['best']}")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
