#!/usr/bin/env python3
"""Preflight Mini-Kuzai V62 pairwise boundary-margin objective.

Uses V61 cycle-2 checkpoint as diagnostic evidence only.
No V62 training is executed. BLIND remains closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v61_trainer as V61
from mini_kuzai import phase03_v62_margin_loss as MARGIN

OUT = REPO / "reviews" / "smoltalk-v62-margin-objective"
RUN_DIR = Path("/root/Mini-Kuzai/runs/v61-boundary-001")
CHECKPOINT = RUN_DIR / "checkpoint-last.pt"
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"

RUN_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V61-TRAIN-RUN-001.json"
)
EOS_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V61-TRAIN-RUN-001-EOS-CALIBRATION-001.json"
)
INIT_FREEZE = (
    REPO / "reviews" / "smoltalk-v60-initialization-freeze"
    / "INITIALIZATION-FREEZE-001.json"
)

LOSS_SOURCE = REPO / "mini_kuzai" / "phase03_v62_margin_loss.py"
LOSS_TEST = REPO / "tests" / "test_phase03_v62_margin_loss.py"
MODEL_SOURCE = REPO / "mini_kuzai" / "phase03_v60_model.py"
TOKENIZER_FILE = (
    REPO / "data" / "phase-03" / "tokenizers"
    / "tokenizer-v56-final.json"
)
SERIALIZER_SOURCE = REPO / "mini_kuzai" / "phase03_conversation.py"
SEGMENTATION_SOURCE = REPO / "mini_kuzai" / "phase03_segmentation.py"

MARGINS = (0.25, 0.50, 1.00)
BASE_WEIGHTS = (1.0, 2.0, 4.0, 8.0)
TRAIN_TERMINAL = 345
TRAIN_INTERMEDIATE = 159
BALANCE_FACTOR = TRAIN_TERMINAL / TRAIN_INTERMEDIATE
MAX_AUX_RATIO_BP = 500
MIN_TERMINAL_ACTIVE = 12
REQUIRED_INTERMEDIATE_ACTIVE = 13
MEMORY_GATE_BP = 6000
SEED = 42


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checked(command: list[str]) -> str:
    process = subprocess.run(
        command,
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if process.returncode:
        raise RuntimeError(
            "Command failed: {}\n{}".format(
                " ".join(command),
                process.stdout,
            )
        )
    return process.stdout


def load_validation_message_segments(tokenizer):
    master = V61.read_json(V61.VALIDATION_MASTER)
    expected_by_behavior = {
        item["behavior"]: item
        for item in master["behaviors"]
    }
    result = []
    seen = set()

    for declaration_path in V61._validation_declarations():
        declaration = V61.read_json(declaration_path)
        behavior = declaration["behavior"]
        expected = expected_by_behavior[behavior]
        target = REPO / declaration["target_batch"]

        for row in V61.read_jsonl(target):
            if row.get("split") != "validation":
                raise RuntimeError("Non-VALIDATION row found")
            if row.get("group_id") != expected["group_id"]:
                raise RuntimeError("VALIDATION group mismatch")
            source_id = row["id"]
            if source_id in seen:
                raise RuntimeError("Duplicate VALIDATION ID")
            seen.add(source_id)

            def count_text(text: str) -> int:
                return len(tokenizer.encode(text))

            segments = V61.SEG.segment_messages(
                row["messages"],
                serialize_messages=V61.CONV.serialize_messages,
                validate_messages=V61.CONV.validate_messages,
                count_text=count_text,
                context_length=V61.CONTEXT_LENGTH,
            )
            for segment in segments:
                ids = V61.encode_messages(
                    tokenizer,
                    list(segment.messages),
                )
                result.append(
                    {
                        "messages": list(segment.messages),
                        "ids": ids,
                    }
                )

    if len(result) != 36:
        raise RuntimeError("Expected exactly 36 VALIDATION segments")
    return result


def collect_gaps(model, tokenizer, device):
    segments = load_validation_message_segments(tokenizer)
    terminal_gaps = []
    intermediate_gaps = []
    base_sum = 0.0
    valid_tokens = 0

    model.eval()
    with torch.no_grad():
        for item in segments:
            ids = item["ids"]
            token_ids = torch.tensor(
                [ids],
                dtype=torch.long,
                device=device,
            )
            with torch.autocast(
                device_type="cuda",
                dtype=torch.bfloat16,
            ):
                logits = model(token_ids)[0, :-1, :].float()

            targets = torch.tensor(
                ids[1:],
                dtype=torch.long,
                device=device,
            )
            per_token = F.cross_entropy(
                logits,
                targets,
                reduction="none",
            )
            base_sum += float(per_token.sum().item())
            valid_tokens += int(targets.numel())

            terminal = logits[-1]
            eos = float(terminal[V61.EOS_ID].item())
            non_eos = terminal.clone()
            non_eos[V61.EOS_ID] = -torch.inf
            best_other = float(torch.max(non_eos).item())
            terminal_gaps.append(eos - best_other)

            boundaries = V61._intermediate_boundary_indices(
                tokenizer,
                item["messages"],
                ids,
            )
            for index in boundaries:
                true_id = int(targets[index].item())
                if true_id == V61.EOS_ID:
                    raise RuntimeError(
                        "Intermediate boundary unexpectedly targets EOS"
                    )
                current = logits[index]
                intermediate_gaps.append(
                    float(current[true_id].item())
                    - float(current[V61.EOS_ID].item())
                )

    if len(terminal_gaps) != 36:
        raise RuntimeError("Terminal validation inventory changed")
    if len(intermediate_gaps) != 13:
        raise RuntimeError("Intermediate validation inventory changed")
    if valid_tokens <= 0:
        raise RuntimeError("VALIDATION token inventory is empty")

    return {
        "base_ce": base_sum / valid_tokens,
        "valid_tokens": valid_tokens,
        "terminal_gaps": terminal_gaps,
        "intermediate_gaps": intermediate_gaps,
    }


def select_candidate(evidence):
    candidates = []
    base_ce = evidence["base_ce"]
    valid_tokens = evidence["valid_tokens"]

    for margin in MARGINS:
        terminal_violations = [
            max(0.0, margin - gap)
            for gap in evidence["terminal_gaps"]
        ]
        intermediate_violations = [
            max(0.0, margin - gap)
            for gap in evidence["intermediate_gaps"]
        ]
        terminal_active = sum(
            value > 0 for value in terminal_violations
        )
        intermediate_active = sum(
            value > 0 for value in intermediate_violations
        )

        for base_weight in BASE_WEIGHTS:
            terminal_weight = base_weight
            intermediate_weight = (
                base_weight * BALANCE_FACTOR
            )
            extra = (
                terminal_weight * sum(terminal_violations)
                + intermediate_weight
                * sum(intermediate_violations)
            ) / valid_tokens
            ratio_bp = round(extra * 10000 / base_ce)

            candidates.append(
                {
                    "margin": margin,
                    "base_weight": base_weight,
                    "terminal_weight": terminal_weight,
                    "intermediate_weight": intermediate_weight,
                    "terminal_active": terminal_active,
                    "intermediate_active": intermediate_active,
                    "auxiliary_ratio_bp": ratio_bp,
                    "passes": (
                        ratio_bp <= MAX_AUX_RATIO_BP
                        and terminal_active >= MIN_TERMINAL_ACTIVE
                        and intermediate_active
                        == REQUIRED_INTERMEDIATE_ACTIVE
                    ),
                }
            )

    passing = [
        item for item in candidates if item["passes"]
    ]
    if not passing:
        raise RuntimeError(
            "No V62 margin/weight candidate passes preflight"
        )

    lowest_margin = min(
        item["margin"] for item in passing
    )
    within_margin = [
        item
        for item in passing
        if item["margin"] == lowest_margin
    ]
    selected = max(
        within_margin,
        key=lambda item: item["base_weight"],
    )
    return selected, candidates


def hardware_preflight(selected):
    if not torch.cuda.is_available():
        return {"passed": False, "reason": "CUDA_UNAVAILABLE"}
    if not torch.cuda.is_bf16_supported():
        return {"passed": False, "reason": "BF16_UNAVAILABLE"}

    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    device = torch.device("cuda")
    model = V61.MODEL.MiniKuzaiPhase03V60(
        V61.MODEL.Phase03Config()
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=3e-4,
        betas=(0.9, 0.95),
        eps=1e-8,
        weight_decay=0.10,
    )

    token_ids = torch.randint(
        3,
        V61.VOCAB_SIZE,
        (8, V61.CONTEXT_LENGTH),
        dtype=torch.long,
        device=device,
    )
    token_ids[0, -1] = V61.EOS_ID
    token_ids[1, -1] = V61.EOS_ID
    targets = token_ids[:, 1:]

    terminal = torch.zeros_like(targets, dtype=torch.bool)
    terminal[0, -1] = True
    terminal[1, -1] = True
    intermediate = torch.zeros_like(targets, dtype=torch.bool)
    intermediate[0, 127] = True
    intermediate[1, 255] = True

    optimizer.zero_grad(set_to_none=True)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    with torch.autocast(
        device_type="cuda",
        dtype=torch.bfloat16,
    ):
        logits = model(token_ids)[:, :-1, :]
        result = MARGIN.boundary_margin_loss(
            logits,
            targets,
            terminal_mask=terminal,
            intermediate_mask=intermediate,
            eos_id=V61.EOS_ID,
            pad_id=V61.PAD_ID,
            margin=selected["margin"],
            terminal_weight=selected["terminal_weight"],
            intermediate_weight=selected[
                "intermediate_weight"
            ],
        )

    finite_loss = bool(torch.isfinite(result.total).item())
    finite_grad = False
    grad_norm = 0.0
    if finite_loss:
        result.total.backward()
        value = torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            1.0,
        )
        finite_grad = bool(
            torch.isfinite(torch.as_tensor(value)).item()
        )
        if finite_grad:
            grad_norm = float(value.detach().cpu())
            optimizer.step()

    torch.cuda.synchronize()
    reserved = int(torch.cuda.max_memory_reserved())
    total = int(
        torch.cuda.get_device_properties(0).total_memory
    )
    reserved_bp = round(reserved * 10000 / total)

    return {
        "passed": (
            finite_loss
            and finite_grad
            and reserved_bp <= MEMORY_GATE_BP
        ),
        "loss_finite": finite_loss,
        "gradient_norm_finite": finite_grad,
        "preclip_gradient_norm": grad_norm,
        "peak_reserved_mib": reserved // (1024 * 1024),
        "total_memory_mib": total // (1024 * 1024),
        "peak_reserved_bp": reserved_bp,
        "memory_gate_bp": MEMORY_GATE_BP,
    }


def build():
    run = read_json(RUN_REPORT)
    eos = read_json(EOS_REPORT)
    summary = read_json(SUMMARY)
    init = read_json(INIT_FREEZE)

    if run["metrics"].get("V61_RUN1_COMPLETED") != 1:
        raise RuntimeError("V61 RUN 001 evidence missing")
    if eos["metrics"].get("V61_EOS1_LOGIT_DIAG_PASS") != 1:
        raise RuntimeError("V61 EOS evidence missing")
    if run["metrics"].get("V61_RUN1_BLIND_ACCESS") != 0:
        raise RuntimeError("V61 RUN 001 violated BLIND boundary")
    if eos["metrics"].get("V61_EOS1_LOGIT_BLIND_ACCESS") != 0:
        raise RuntimeError("V61 EOS diagnostic violated BLIND boundary")
    if summary.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED":
        raise RuntimeError("V61 RUN 001 did not stop at cycle-2 review")
    if init.get("status") != "FROZEN":
        raise RuntimeError("V60 initialization freeze changed")

    run_checked(
        [
            sys.executable,
            "-m",
            "py_compile",
            str(LOSS_SOURCE),
            str(LOSS_TEST),
        ]
    )
    run_checked([sys.executable, str(LOSS_TEST)])

    runtime = V61.verify_runtime(
        REPO / "mini_kuzai" / "phase03_v61_trainer.py",
        REPO / "tools" / "train_v61_boundary.py",
    )

    if not CHECKPOINT.is_file() or CHECKPOINT.is_symlink():
        raise RuntimeError("V61 cycle-2 checkpoint missing")
    device = torch.device("cuda")
    state = torch.load(
        CHECKPOINT,
        map_location=device,
        weights_only=False,
    )
    if state.get("schema_version") != "v61-boundary-checkpoint-1":
        raise RuntimeError("Unexpected V61 checkpoint schema")
    if (
        state.get("authorization_freeze_fingerprint")
        != runtime["authorization"]["freeze_fingerprint"]
    ):
        raise RuntimeError("V61 checkpoint authorization mismatch")

    model = V61.MODEL.MiniKuzaiPhase03V60(
        V61.MODEL.Phase03Config()
    ).to(device)
    model.load_state_dict(state["model"])
    tokenizer = V61.load_tokenizer()

    evidence = collect_gaps(model, tokenizer, device)
    selected, candidates = select_candidate(evidence)
    hardware = hardware_preflight(selected)
    if not hardware.get("passed"):
        raise RuntimeError("V62 hardware preflight failed")

    objective = {
        "schema_version": "v62-margin-objective-1",
        "status": "OBJECTIVE_DEFINED_PREFLIGHT_PASSED",
        "architecture": "V60_UNCHANGED",
        "initialization": "V60_INITIALIZATION_UNCHANGED",
        "tokenizer": "V56_UNCHANGED",
        "corpus": "V59_V60_FROZEN_CORPUS_UNCHANGED",
        "base_objective": "NEXT_TOKEN_CROSS_ENTROPY_UNCHANGED",
        "margin_objective": {
            "terminal_relation":
                "EOS_GT_BEST_NON_EOS_PLUS_MARGIN",
            "intermediate_relation":
                "TRUE_GT_EOS_PLUS_MARGIN",
            "margin": selected["margin"],
            "terminal_weight": selected["terminal_weight"],
            "intermediate_weight":
                selected["intermediate_weight"],
            "training_boundary_balance_factor":
                BALANCE_FACTOR,
            "normalization": "GLOBAL_NONPAD_TOKEN_COUNT",
        },
        "selection": {
            "margins": list(MARGINS),
            "base_weights": list(BASE_WEIGHTS),
            "maximum_auxiliary_ratio_bp":
                MAX_AUX_RATIO_BP,
            "selected": selected,
            "candidates": candidates,
        },
        "evidence": {
            "source": "V61_CYCLE2_CHECKPOINT_DIAGNOSTIC_ONLY",
            "validation_base_ce": evidence["base_ce"],
            "validation_tokens": evidence["valid_tokens"],
            "terminal_positions": 36,
            "intermediate_positions": 13,
        },
        "fingerprints": {
            "v61_run_report_sha256":
                sha256_file(RUN_REPORT),
            "v61_eos_report_sha256":
                sha256_file(EOS_REPORT),
            "v60_initialization_freeze_sha256":
                sha256_file(INIT_FREEZE),
            "v62_margin_loss_source_sha256":
                sha256_file(LOSS_SOURCE),
            "v62_margin_loss_test_sha256":
                sha256_file(LOSS_TEST),
            "v60_model_source_sha256":
                sha256_file(MODEL_SOURCE),
            "tokenizer_sha256":
                sha256_file(TOKENIZER_FILE),
            "serializer_sha256":
                sha256_file(SERIALIZER_SOURCE),
            "segmentation_sha256":
                sha256_file(SEGMENTATION_SOURCE),
        },
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }

    report = {
        "schema_version": "v62-margin-objective-report-1",
        "status": "PREFLIGHT_PASSED_FREEZE_REQUIRED",
        "objective": objective,
        "hardware_preflight": hardware,
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }
    return objective, report


def write(objective, report):
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V62 margin objective output already exists")
    OUT.mkdir(parents=True)

    (OUT / "OBJECTIVE-001.json").write_text(
        json.dumps(objective, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUT / "REPORT-001.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    selected = objective["selection"]["selected"]
    lines = [
        "# Mini-Kuzai V62 - pairwise boundary-margin preflight",
        "",
        "Status --> **PREFLIGHT PASSED / TRAINING NOT AUTHORIZED**",
        "",
        f"- selected margin --> **{selected['margin']}**",
        f"- terminal weight --> **{selected['terminal_weight']:.4f}**",
        f"- intermediate weight --> **{selected['intermediate_weight']:.4f}**",
        f"- auxiliary loss ratio --> **{selected['auxiliary_ratio_bp'] / 100:.2f}%**",
        f"- terminal active validation boundaries --> **{selected['terminal_active']} / 36**",
        f"- intermediate active validation boundaries --> **{selected['intermediate_active']} / 13**",
        "- training start point --> **fresh V60 initialization**",
        "- V61 checkpoint --> **diagnostic evidence only**",
        "- BLIND TEST --> **CLOSED**",
        "",
        "---",
        "",
        "##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**",
        "",
    ]
    (OUT / "RESULTS-001.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def metrics(report):
    objective = report["objective"]
    selected = objective["selection"]["selected"]
    hardware = report["hardware_preflight"]
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V62_MARGIN_PREFLIGHT_PASS": 1,
        "V62_MARGIN_SELECTED_X1000":
            round(selected["margin"] * 1000),
        "V62_MARGIN_TERMINAL_WEIGHT_X100":
            round(selected["terminal_weight"] * 100),
        "V62_MARGIN_INTERMEDIATE_WEIGHT_X100":
            round(selected["intermediate_weight"] * 100),
        "V62_MARGIN_AUX_RATIO_BP":
            selected["auxiliary_ratio_bp"],
        "V62_MARGIN_TERM_ACTIVE":
            selected["terminal_active"],
        "V62_MARGIN_INTERMEDIATE_ACTIVE":
            selected["intermediate_active"],
        "V62_MARGIN_BALANCE_FACTOR_X1000":
            round(BALANCE_FACTOR * 1000),
        "V62_MARGIN_RESERVED_MIB":
            int(hardware["peak_reserved_mib"]),
        "V62_MARGIN_BLIND_ACCESS": 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--from-report", action="store_true")
    args = parser.parse_args()

    if args.from_report:
        report = read_json(OUT / "REPORT-001.json")
    else:
        objective, report = build()
        if args.write:
            write(objective, report)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics(report).items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
