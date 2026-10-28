#!/usr/bin/env python3
"""Define and preflight the V61 boundary-aware EOS objective.

No persistent training is executed. BLIND TEST remains closed.
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

from mini_kuzai import phase03_v60_trainer as V60
from mini_kuzai import phase03_v61_boundary_loss as BOUNDARY

OUT = REPO / "reviews" / "smoltalk-v61-boundary-objective"
RUN_DIR = Path("/root/Mini-Kuzai/runs/v60-extended-001")
CHECKPOINT = RUN_DIR / "checkpoint-last.pt"

RUN2_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V60-TRAIN-RUN-002.json"
)
EOS_TARGET_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V60-EOS-ASSISTANT-TURN-TARGET-DIAGNOSTIC-001.json"
)
EOS_LOGIT_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V60-EOS-LOGIT-RANK-CALIBRATION-DIAGNOSTIC-001.json"
)
EOS_BIAS_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V60-EOS-COMPETITOR-LOGIT-MARGIN-BIAS-SWEEP-001.json"
)
INIT_FREEZE = (
    REPO / "reviews" / "smoltalk-v60-initialization-freeze"
    / "INITIALIZATION-FREEZE-001.json"
)

LOSS_SOURCE = REPO / "mini_kuzai" / "phase03_v61_boundary_loss.py"
TEST_SOURCE = REPO / "tests" / "test_phase03_v61_boundary_loss.py"
MODEL_SOURCE = REPO / "mini_kuzai" / "phase03_v60_model.py"
TOKENIZER_FILE = (
    REPO / "data" / "phase-03" / "tokenizers"
    / "tokenizer-v56-final.json"
)
SERIALIZER_SOURCE = REPO / "mini_kuzai" / "phase03_conversation.py"
SEGMENTATION_SOURCE = REPO / "mini_kuzai" / "phase03_segmentation.py"

CANDIDATE_WEIGHTS = (4.0, 8.0, 16.0, 32.0)
MAX_AUXILIARY_RATIO_BP = 500
MIN_SELECTED_GRADIENT_MULTIPLIER = 9
SEED = 42
MEMORY_GATE_BP = 6000


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
    master = V60.read_json(V60.VALIDATION_MASTER)
    expected_by_behavior = {
        item["behavior"]: item
        for item in master["behaviors"]
    }

    result = []
    seen_ids = set()

    for declaration_path in V60._validation_declarations():
        declaration = V60.read_json(declaration_path)
        behavior = declaration["behavior"]
        expected = expected_by_behavior[behavior]
        target = REPO / declaration["target_batch"]

        for row in V60.read_jsonl(target):
            if row.get("split") != "validation":
                raise RuntimeError("Non-VALIDATION row found")
            if row.get("group_id") != expected["group_id"]:
                raise RuntimeError("VALIDATION group mismatch")
            source_id = row["id"]
            if source_id in seen_ids:
                raise RuntimeError("Duplicate VALIDATION ID")
            seen_ids.add(source_id)

            def count_text(text: str) -> int:
                return len(tokenizer.encode(text))

            segments = V60.SEG.segment_messages(
                row["messages"],
                serialize_messages=V60.CONV.serialize_messages,
                validate_messages=V60.CONV.validate_messages,
                count_text=count_text,
                context_length=V60.CONTEXT_LENGTH,
            )
            for segment in segments:
                ids = V60.encode_messages(
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


def intermediate_boundary_indices(tokenizer, messages, ids):
    token_bytes = getattr(tokenizer, "_token_bytes", None)
    if not isinstance(token_bytes, dict):
        raise RuntimeError("Tokenizer byte table unavailable")

    text = V60.CONV.serialize_messages(messages)
    expected_ids = tokenizer.encode(
        text,
        add_bos=True,
        add_eos=True,
    )
    if expected_ids != ids:
        raise RuntimeError("VALIDATION re-encoding mismatch")

    assistant_end_offsets = []
    byte_cursor = 0

    for index, message in enumerate(messages):
        header = (
            V60.CONV.USER_HEADER
            if message["role"] == "user"
            else V60.CONV.ASSISTANT_HEADER
        )
        section = (
            header + message["content"]
        ).encode("utf-8")

        if message["role"] == "assistant":
            assistant_end_offsets.append(
                byte_cursor + len(section)
            )

        byte_cursor += len(section)
        if index < len(messages) - 1:
            byte_cursor += len(
                V60.CONV.TURN_SEPARATOR.encode("utf-8")
            )

    offsets = assistant_end_offsets[:-1]
    if not offsets:
        return []

    cumulative = 0
    offset_to_input_index = {}
    for input_index, token_id in enumerate(
        ids[1:-1],
        start=1,
    ):
        value = token_bytes.get(int(token_id))
        if value is None:
            raise RuntimeError("Unknown tokenizer byte token")
        cumulative += len(value)
        offset_to_input_index[cumulative] = input_index

    if cumulative != len(text.encode("utf-8")):
        raise RuntimeError("Tokenizer byte accounting mismatch")

    result = []
    for offset in offsets:
        input_index = offset_to_input_index.get(offset)
        if input_index is None:
            raise RuntimeError(
                "Assistant boundary does not align to token boundary"
            )
        result.append(input_index)
    return result


def collect_loss_components(model, tokenizer, device):
    segments = load_validation_message_segments(tokenizer)

    base_sum = 0.0
    terminal_ce_sum = 0.0
    intermediate_suppression_sum = 0.0
    valid_tokens = 0
    terminal_positions = 0
    intermediate_positions = 0

    model.eval()
    with torch.no_grad():
        for item in segments:
            ids = item["ids"]
            input_ids = torch.tensor(
                [ids],
                dtype=torch.long,
                device=device,
            )
            with torch.autocast(
                device_type="cuda",
                dtype=torch.bfloat16,
            ):
                logits = model(input_ids)[0, :-1, :].float()

            targets = torch.tensor(
                ids[1:],
                dtype=torch.long,
                device=device,
            )
            if int(targets[-1].item()) != V60.EOS_ID:
                raise RuntimeError("Segment lacks terminal EOS target")

            per_token = F.cross_entropy(
                logits,
                targets,
                reduction="none",
            )
            base_sum += float(per_token.sum().item())
            valid_tokens += int(targets.numel())

            terminal_ce_sum += float(
                per_token[-1].item()
            )
            terminal_positions += 1

            for index in intermediate_boundary_indices(
                tokenizer,
                item["messages"],
                ids,
            ):
                if index >= logits.shape[0]:
                    raise RuntimeError("Boundary logit index invalid")
                if int(targets[index].item()) == V60.EOS_ID:
                    raise RuntimeError(
                        "Intermediate boundary unexpectedly targets EOS"
                    )

                selected = logits[index]
                eos_logit = selected[V60.EOS_ID]
                non_eos = selected.clone()
                non_eos[V60.EOS_ID] = -torch.inf
                other_lse = torch.logsumexp(
                    non_eos,
                    dim=-1,
                )
                suppression = F.softplus(
                    eos_logit - other_lse
                )
                intermediate_suppression_sum += float(
                    suppression.item()
                )
                intermediate_positions += 1

    if valid_tokens <= 0:
        raise RuntimeError("VALIDATION produced no target tokens")
    if terminal_positions != 36:
        raise RuntimeError("Terminal boundary count changed")
    if intermediate_positions != 13:
        raise RuntimeError("Intermediate boundary count changed")

    base_ce = base_sum / valid_tokens
    return {
        "base_ce": base_ce,
        "base_sum": base_sum,
        "terminal_ce_sum": terminal_ce_sum,
        "intermediate_suppression_sum":
            intermediate_suppression_sum,
        "valid_tokens": valid_tokens,
        "terminal_positions": terminal_positions,
        "intermediate_positions": intermediate_positions,
    }


def select_weight(components):
    candidates = []
    base = components["base_ce"]
    denominator = components["valid_tokens"]
    boundary_sum = (
        components["terminal_ce_sum"]
        + components["intermediate_suppression_sum"]
    )

    for weight in CANDIDATE_WEIGHTS:
        extra = weight * boundary_sum / denominator
        total = base + extra
        ratio_bp = round(extra * 10000 / base)
        gradient_multiplier = round(1 + weight)

        candidates.append(
            {
                "weight": weight,
                "total_loss": total,
                "extra_loss": extra,
                "auxiliary_ratio_bp": ratio_bp,
                "boundary_gradient_multiplier":
                    gradient_multiplier,
                "passes_ratio_gate":
                    ratio_bp <= MAX_AUXILIARY_RATIO_BP,
                "passes_gradient_gate":
                    gradient_multiplier
                    >= MIN_SELECTED_GRADIENT_MULTIPLIER,
            }
        )

    passing = [
        item
        for item in candidates
        if item["passes_ratio_gate"]
        and item["passes_gradient_gate"]
    ]
    if not passing:
        raise RuntimeError(
            "No V61 boundary-weight candidate passes preflight gates"
        )

    selected = max(
        passing,
        key=lambda item: item["weight"],
    )
    return selected, candidates


def synthetic_hardware_preflight(selected_weight):
    if not torch.cuda.is_available():
        return {"passed": False, "reason": "CUDA_UNAVAILABLE"}
    if not torch.cuda.is_bf16_supported():
        return {"passed": False, "reason": "BF16_UNAVAILABLE"}

    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    device = torch.device("cuda")

    model = V60.MODEL.MiniKuzaiPhase03V60(
        V60.MODEL.Phase03Config()
    ).to(device)
    if V60.MODEL.count_parameters(model) != V60.MODEL_PARAMETERS:
        raise RuntimeError("V60/V61 architecture parameter count changed")

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=3e-4,
        betas=(0.9, 0.95),
        eps=1e-8,
        weight_decay=0.10,
    )

    token_ids = torch.randint(
        3,
        V60.VOCAB_SIZE,
        (8, V60.CONTEXT_LENGTH),
        device=device,
        dtype=torch.long,
    )

    token_ids[0, -1] = V60.EOS_ID
    token_ids[1, -1] = V60.EOS_ID

    targets = token_ids[:, 1:]
    terminal_mask = torch.zeros_like(
        targets,
        dtype=torch.bool,
    )
    terminal_mask[0, -1] = True
    terminal_mask[1, -1] = True

    intermediate_mask = torch.zeros_like(
        targets,
        dtype=torch.bool,
    )
    intermediate_mask[0, 127] = True
    intermediate_mask[1, 255] = True
    if bool(
        (targets[intermediate_mask] == V60.EOS_ID)
        .any()
        .item()
    ):
        raise RuntimeError("Synthetic intermediate target collided with EOS")

    optimizer.zero_grad(set_to_none=True)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    with torch.autocast(
        device_type="cuda",
        dtype=torch.bfloat16,
    ):
        logits = model(token_ids)[:, :-1, :]
        result = BOUNDARY.boundary_aware_eos_loss(
            logits,
            targets,
            terminal_mask=terminal_mask,
            intermediate_mask=intermediate_mask,
            terminal_weight=selected_weight,
            intermediate_weight=selected_weight,
        )

    finite_loss = bool(
        torch.isfinite(result.total).item()
    )
    finite_grad = False
    grad_norm = None

    if finite_loss:
        result.total.backward()
        value = torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            1.0,
        )
        finite_grad = bool(
            torch.isfinite(
                torch.as_tensor(value)
            ).item()
        )
        if finite_grad:
            grad_norm = float(
                value.detach().cpu()
            )
            optimizer.step()

    torch.cuda.synchronize()
    reserved = int(
        torch.cuda.max_memory_reserved()
    )
    allocated = int(
        torch.cuda.max_memory_allocated()
    )
    total = int(
        torch.cuda.get_device_properties(0).total_memory
    )
    reserved_bp = (
        round(reserved * 10000 / total)
        if total
        else 10000
    )

    return {
        "passed": (
            finite_loss
            and finite_grad
            and reserved_bp <= MEMORY_GATE_BP
        ),
        "device_name": torch.cuda.get_device_name(0),
        "bf16": True,
        "loss_finite": finite_loss,
        "gradient_norm_finite": finite_grad,
        "preclip_gradient_norm": grad_norm,
        "peak_allocated_mib":
            allocated // (1024 * 1024),
        "peak_reserved_mib":
            reserved // (1024 * 1024),
        "total_memory_mib":
            total // (1024 * 1024),
        "peak_reserved_bp": reserved_bp,
        "memory_gate_bp": MEMORY_GATE_BP,
    }


def build():
    init = read_json(INIT_FREEZE)
    run2 = read_json(RUN2_REPORT)
    eos_target = read_json(EOS_TARGET_REPORT)
    eos_logit = read_json(EOS_LOGIT_REPORT)
    eos_bias = read_json(EOS_BIAS_REPORT)

    if init.get("status") != "FROZEN":
        raise RuntimeError("V60 initialization freeze is not frozen")
    if init.get("parameters") != 1184512:
        raise RuntimeError("V60 architecture changed")
    if init.get("blind_test_accessed") is not False:
        raise RuntimeError("V60 initialization freeze indicates BLIND access")

    for report, metric in (
        (run2, "V60_RUN2_COMPLETED"),
        (eos_target, "V60_EOS_DIAG_PASS"),
        (eos_logit, "V60_EOS_LOGIT_DIAG_PASS"),
        (eos_bias, "V60_EOS_BIAS_DIAG_PASS"),
    ):
        metrics = report.get("metrics")
        if not isinstance(metrics, dict):
            raise RuntimeError("Required V60 diagnostic metrics missing")
        if metrics.get(metric) != 1:
            raise RuntimeError(
                f"Required V60 diagnostic did not pass: {metric}"
            )

    if (
        eos_target["metrics"].get("V60_EOS_BLIND_ACCESS") != 0
        or eos_logit["metrics"].get(
            "V60_EOS_LOGIT_BLIND_ACCESS"
        ) != 0
        or eos_bias["metrics"].get(
            "V60_EOS_BIAS_BLIND_ACCESS"
        ) != 0
    ):
        raise RuntimeError("V60 EOS diagnostic BLIND boundary violated")

    compile_output = run_checked(
        [
            sys.executable,
            "-m",
            "py_compile",
            str(LOSS_SOURCE),
            str(TEST_SOURCE),
        ]
    )
    test_output = run_checked(
        [sys.executable, str(TEST_SOURCE)]
    )

    if not CHECKPOINT.is_file() or CHECKPOINT.is_symlink():
        raise RuntimeError("V60 final checkpoint missing or unsafe")

    runtime = V60.verify_runtime(
        REPO / "mini_kuzai" / "phase03_v60_trainer.py",
        REPO / "tools" / "train_v60_extended.py",
    )

    device = torch.device("cuda")
    state = torch.load(
        CHECKPOINT,
        map_location=device,
        weights_only=False,
    )
    if state.get("schema_version") != "v60-extended-checkpoint-1":
        raise RuntimeError("Unexpected V60 checkpoint schema")
    if (
        state.get("authorization_freeze_fingerprint")
        != runtime["authorization"]["freeze_fingerprint"]
    ):
        raise RuntimeError("V60 checkpoint authorization mismatch")

    model = V60.MODEL.MiniKuzaiPhase03V60(
        V60.MODEL.Phase03Config()
    ).to(device)
    model.load_state_dict(state["model"])

    tokenizer = V60.load_tokenizer()
    components = collect_loss_components(
        model,
        tokenizer,
        device,
    )
    selected, candidates = select_weight(
        components
    )

    preflight = synthetic_hardware_preflight(
        selected["weight"]
    )
    if not preflight.get("passed"):
        raise RuntimeError("V61 synthetic hardware preflight failed")

    objective = {
        "schema_version": "v61-boundary-objective-1",
        "status": "OBJECTIVE_DEFINED_PREFLIGHT_PASSED",
        "architecture": "V60_UNCHANGED",
        "initialization": "V60_INITIALIZATION_UNCHANGED",
        "tokenizer": "V56_UNCHANGED",
        "corpus": "V59_V60_FROZEN_CORPUS_UNCHANGED",
        "serializer": "PHASE03_CANONICAL_UNCHANGED",
        "segmentation": "PHASE03_CANONICAL_UNCHANGED",
        "base_objective": "NEXT_TOKEN_CROSS_ENTROPY_UNCHANGED",
        "boundary_objective": {
            "terminal": {
                "target": "EOS",
                "term": "EXTRA_EOS_CROSS_ENTROPY",
                "normalization": "GLOBAL_NONPAD_TOKEN_COUNT",
                "weight": selected["weight"],
            },
            "intermediate_assistant_boundary": {
                "target": "NON_EOS_TRUE_CONTINUATION",
                "term": "NEG_LOG_ONE_MINUS_P_EOS",
                "normalization": "GLOBAL_NONPAD_TOKEN_COUNT",
                "weight": selected["weight"],
            },
            "masks_disjoint": True,
            "ordinary_positions_unchanged": True,
        },
        "selection": {
            "candidate_weights": list(CANDIDATE_WEIGHTS),
            "selected_weight": selected["weight"],
            "maximum_auxiliary_ratio_bp":
                MAX_AUXILIARY_RATIO_BP,
            "minimum_boundary_gradient_multiplier":
                MIN_SELECTED_GRADIENT_MULTIPLIER,
            "selected_auxiliary_ratio_bp":
                selected["auxiliary_ratio_bp"],
            "selected_boundary_gradient_multiplier":
                selected["boundary_gradient_multiplier"],
            "candidates": candidates,
        },
        "evidence": {
            "validation_base_ce": components["base_ce"],
            "validation_terminal_positions":
                components["terminal_positions"],
            "validation_intermediate_positions":
                components["intermediate_positions"],
            "validation_valid_tokens":
                components["valid_tokens"],
            "v60_final_checkpoint_used_for_preflight_only": True,
        },
        "fingerprints": {
            "v60_initialization_freeze_sha256":
                sha256_file(INIT_FREEZE),
            "v61_boundary_loss_source_sha256":
                sha256_file(LOSS_SOURCE),
            "v61_boundary_loss_test_sha256":
                sha256_file(TEST_SOURCE),
            "v60_model_source_sha256":
                sha256_file(MODEL_SOURCE),
            "tokenizer_sha256":
                sha256_file(TOKENIZER_FILE),
            "serializer_sha256":
                sha256_file(SERIALIZER_SOURCE),
            "segmentation_sha256":
                sha256_file(SEGMENTATION_SOURCE),
            "v60_run2_report_sha256":
                sha256_file(RUN2_REPORT),
            "v60_eos_target_report_sha256":
                sha256_file(EOS_TARGET_REPORT),
            "v60_eos_logit_report_sha256":
                sha256_file(EOS_LOGIT_REPORT),
            "v60_eos_bias_report_sha256":
                sha256_file(EOS_BIAS_REPORT),
        },
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }

    report = {
        "schema_version": "v61-boundary-objective-report-1",
        "status": "PREFLIGHT_PASSED_FREEZE_REQUIRED",
        "objective": objective,
        "py_compile_output": compile_output.strip(),
        "unit_test_output": test_output.strip(),
        "hardware_preflight": preflight,
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }
    return objective, report


def write(objective, report):
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V61 boundary objective output already exists")
    OUT.mkdir(parents=True)

    (OUT / "OBJECTIVE-001.json").write_text(
        json.dumps(
            objective,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "REPORT-001.json").write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    selection = objective["selection"]
    preflight = report["hardware_preflight"]
    lines = [
        "# Mini-Kuzai V61 - boundary-aware EOS objective",
        "",
        "Status --> **OBJECTIVE DEFINED / PREFLIGHT PASSED / TRAINING NOT AUTHORIZED**",
        "",
        "## Controlled change from V60",
        "",
        "- architecture --> unchanged",
        "- initialization --> unchanged",
        "- tokenizer --> unchanged",
        "- corpus and stream weighting --> unchanged",
        "- serializer and segmentation --> unchanged",
        "- base next-token cross-entropy --> unchanged",
        "- only experimental variable --> boundary-aware EOS objective",
        "",
        "## Boundary objective",
        "",
        "- terminal assistant boundary --> extra EOS cross-entropy",
        "- intermediate assistant boundary --> explicit EOS suppression",
        "- ordinary token positions --> unchanged",
        "- auxiliary normalization --> global non-pad token count",
        f"- selected boundary weight --> **{selection['selected_weight']}**",
        f"- effective local gradient multiplier --> **{selection['selected_boundary_gradient_multiplier']}x**",
        f"- added loss ratio on frozen VALIDATION --> **{selection['selected_auxiliary_ratio_bp'] / 100:.2f}%**",
        "",
        "## Selection gate",
        "",
        "- candidates --> **4 / 8 / 16 / 32**",
        "- maximum allowed auxiliary loss ratio --> **5.00%**",
        "- minimum boundary gradient multiplier --> **9x**",
        "",
        "## Hardware preflight",
        "",
        f"- CUDA/BF16 --> **{'PASS' if preflight['passed'] else 'FAIL'}**",
        f"- peak reserved VRAM --> **{preflight['peak_reserved_mib']} MiB**",
        f"- peak reserved ratio --> **{preflight['peak_reserved_bp'] / 100:.2f}%**",
        "",
        "TRAINING_AUTHORIZED --> **0**",
        "TRAINING_STARTED --> **0**",
        "BLIND TEST --> **CLOSED**",
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
    selection = objective["selection"]
    preflight = report["hardware_preflight"]
    evidence = objective["evidence"]

    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
        "V61_BOUNDARY_OBJECTIVE_DEFINED": 1,
        "V61_BOUNDARY_PREFLIGHT_PASS": int(
            bool(preflight.get("passed"))
        ),
        "V61_BOUNDARY_TESTS_PASS": 1,
        "V61_BOUNDARY_CANDIDATES": len(
            selection["candidate_weights"]
        ),
        "V61_BOUNDARY_SELECTED_WEIGHT_X100":
            round(selection["selected_weight"] * 100),
        "V61_BOUNDARY_GRAD_MULTIPLIER_X100":
            round(
                selection[
                    "selected_boundary_gradient_multiplier"
                ]
                * 100
            ),
        "V61_BOUNDARY_AUX_RATIO_BP":
            selection["selected_auxiliary_ratio_bp"],
        "V61_BOUNDARY_VAL_BASE_CE_X1E6":
            round(evidence["validation_base_ce"] * 1_000_000),
        "V61_BOUNDARY_VAL_TERMINAL":
            evidence["validation_terminal_positions"],
        "V61_BOUNDARY_VAL_INTERMEDIATE":
            evidence["validation_intermediate_positions"],
        "V61_BOUNDARY_VAL_TOKENS":
            evidence["validation_valid_tokens"],
        "V61_BOUNDARY_RESERVED_MIB":
            int(preflight.get("peak_reserved_mib", 0) or 0),
        "V61_BOUNDARY_RESERVED_BP":
            int(preflight.get("peak_reserved_bp", 0) or 0),
        "V61_BOUNDARY_BLIND_ACCESS": 0,
        "V61_BOUNDARY_TRAINING_STARTED": 0,
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
