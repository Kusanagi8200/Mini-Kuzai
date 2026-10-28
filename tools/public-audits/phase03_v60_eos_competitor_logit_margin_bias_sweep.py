#!/usr/bin/env python3
"""V60 EOS competitor, logit-margin and bias-sweep diagnostic.

Uses the frozen final V60 checkpoint and frozen VALIDATION only.
No training, no weight mutation, no BLIND access, no generated text publication.
"""

from __future__ import annotations

import collections
import json
import math
import statistics
import sys
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v60_trainer as T

RUN_DIR = Path("/root/Mini-Kuzai/runs/v60-extended-001")
CHECKPOINT = RUN_DIR / "checkpoint-last.pt"
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"
CALIBRATION_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V60-EOS-LOGIT-RANK-CALIBRATION-DIAGNOSTIC-001.json"
)

BIASES = (0.25, 0.50, 1.00, 2.00)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def scaled_margin(value: float) -> int:
    if not math.isfinite(value):
        raise RuntimeError("Non-finite logit margin")
    if value < -1e-6:
        raise RuntimeError("EOS unexpectedly exceeds competitor at baseline")
    return round(max(0.0, value) * 1000)


def load_validation_message_segments(tokenizer):
    master = T.read_json(T.VALIDATION_MASTER)
    expected_by_behavior = {
        item["behavior"]: item
        for item in master["behaviors"]
    }

    result = []
    seen_ids = set()

    for declaration_path in T._validation_declarations():
        declaration = T.read_json(declaration_path)
        behavior = declaration["behavior"]
        expected = expected_by_behavior[behavior]
        target = REPO / declaration["target_batch"]

        for row in T.read_jsonl(target):
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

            segments = T.SEG.segment_messages(
                row["messages"],
                serialize_messages=T.CONV.serialize_messages,
                validate_messages=T.CONV.validate_messages,
                count_text=count_text,
                context_length=T.CONTEXT_LENGTH,
            )
            for segment in segments:
                ids = T.encode_messages(
                    tokenizer,
                    list(segment.messages),
                )
                result.append(
                    {
                        "source_id": source_id,
                        "messages": list(segment.messages),
                        "ids": ids,
                    }
                )

    if len(result) != 36:
        raise RuntimeError("Expected 36 VALIDATION segments")
    return result


def intermediate_boundary_logit_indices(tokenizer, messages, ids):
    token_bytes = getattr(tokenizer, "_token_bytes", None)
    if not isinstance(token_bytes, dict):
        raise RuntimeError("Tokenizer token-byte table unavailable")

    text = T.CONV.serialize_messages(messages)
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
            T.CONV.USER_HEADER
            if message["role"] == "user"
            else T.CONV.ASSISTANT_HEADER
        )
        section_bytes = (
            header + message["content"]
        ).encode("utf-8")

        if message["role"] == "assistant":
            assistant_end_offsets.append(
                byte_cursor + len(section_bytes)
            )

        byte_cursor += len(section_bytes)
        if index < len(messages) - 1:
            byte_cursor += len(
                T.CONV.TURN_SEPARATOR.encode("utf-8")
            )

    intermediate_offsets = assistant_end_offsets[:-1]
    if not intermediate_offsets:
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
    for offset in intermediate_offsets:
        input_index = offset_to_input_index.get(offset)
        if input_index is None:
            raise RuntimeError(
                "Assistant boundary is not a token boundary"
            )
        result.append(input_index)

    return result


def top_non_eos(logits: torch.Tensor) -> tuple[int, float]:
    values = logits.clone()
    values[T.EOS_ID] = -torch.inf
    token_id = int(torch.argmax(values).item())
    return token_id, float(values[token_id].item())


def eos_top1_after_bias(
    logits: torch.Tensor,
    bias: float,
) -> bool:
    adjusted = logits.clone()
    adjusted[T.EOS_ID] += bias
    return int(torch.argmax(adjusted).item()) == T.EOS_ID


def main() -> None:
    calibration = read_json(CALIBRATION_REPORT)
    calibration_metrics = calibration.get("metrics")
    if not isinstance(calibration_metrics, dict):
        raise RuntimeError("Calibration metrics missing")
    if calibration_metrics.get("V60_EOS_LOGIT_DIAG_PASS") != 1:
        raise RuntimeError("Prior EOS calibration did not pass")
    if calibration_metrics.get("V60_EOS_LOGIT_BLIND_ACCESS") != 0:
        raise RuntimeError("Prior calibration violated BLIND boundary")

    summary = read_json(SUMMARY)
    if summary.get("status") != "STOPPED":
        raise RuntimeError("Final V60 run is not stopped")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("Final V60 summary indicates BLIND access")

    runtime = T.verify_runtime(
        REPO / "mini_kuzai" / "phase03_v60_trainer.py",
        REPO / "tools" / "train_v60_extended.py",
    )

    if not CHECKPOINT.is_file() or CHECKPOINT.is_symlink():
        raise RuntimeError("Final checkpoint missing or unsafe")

    device = torch.device("cuda")
    state = torch.load(
        CHECKPOINT,
        map_location=device,
        weights_only=False,
    )
    if state.get("schema_version") != "v60-extended-checkpoint-1":
        raise RuntimeError("Unexpected checkpoint schema")
    if (
        state.get("authorization_freeze_fingerprint")
        != runtime["authorization"]["freeze_fingerprint"]
    ):
        raise RuntimeError("Checkpoint authorization mismatch")
    if (
        state.get("trainer_freeze_fingerprint")
        != runtime["trainer_freeze"]["trainer_freeze_fingerprint"]
    ):
        raise RuntimeError("Checkpoint trainer mismatch")

    model = T.MODEL.MiniKuzaiPhase03V60(
        T.MODEL.Phase03Config()
    ).to(device)
    model.load_state_dict(state["model"])
    model.eval()

    tokenizer = T.load_tokenizer()
    segments = load_validation_message_segments(tokenizer)

    terminal_margins = []
    intermediate_margins = []
    nonterminal_margins = []
    terminal_competitors = collections.Counter()

    sweep_terminal = {bias: 0 for bias in BIASES}
    sweep_intermediate = {bias: 0 for bias in BIASES}
    sweep_nonterminal = {bias: 0 for bias in BIASES}

    intermediate_positions = 0
    nonterminal_positions = 0

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

            targets = ids[1:]
            if targets[-1] != T.EOS_ID:
                raise RuntimeError(
                    "VALIDATION segment does not terminate in EOS"
                )

            # True terminal position.
            terminal_logits = logits[-1]
            eos_logit = float(
                terminal_logits[T.EOS_ID].item()
            )
            competitor_id, competitor_logit = top_non_eos(
                terminal_logits
            )
            terminal_competitors[competitor_id] += 1
            terminal_margins.append(
                competitor_logit - eos_logit
            )
            for bias in BIASES:
                sweep_terminal[bias] += int(
                    eos_top1_after_bias(
                        terminal_logits,
                        bias,
                    )
                )

            intermediate_indices = set(
                intermediate_boundary_logit_indices(
                    tokenizer,
                    item["messages"],
                    ids,
                )
            )

            # Every position except the true terminal EOS target.
            for position in range(logits.shape[0] - 1):
                current = logits[position]
                eos_value = float(
                    current[T.EOS_ID].item()
                )
                _, other_value = top_non_eos(current)
                margin = other_value - eos_value
                if margin < -1e-6:
                    raise RuntimeError(
                        "Baseline EOS is top-1 at a nonterminal position"
                    )
                nonterminal_margins.append(
                    max(0.0, margin)
                )
                nonterminal_positions += 1

                for bias in BIASES:
                    sweep_nonterminal[bias] += int(
                        eos_top1_after_bias(
                            current,
                            bias,
                        )
                    )

                if position in intermediate_indices:
                    intermediate_positions += 1
                    intermediate_margins.append(
                        max(0.0, margin)
                    )
                    for bias in BIASES:
                        sweep_intermediate[bias] += int(
                            eos_top1_after_bias(
                                current,
                                bias,
                            )
                        )

    if len(terminal_margins) != 36:
        raise RuntimeError("Terminal position count changed")
    if intermediate_positions != 13:
        raise RuntimeError("Intermediate boundary count changed")
    if nonterminal_positions != 9170:
        raise RuntimeError("Nonterminal position count changed")

    dominant_id, dominant_count = (
        terminal_competitors.most_common(1)[0]
    )

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V60_EOS_BIAS_DIAG_PASS": 1,
        "V60_EOS_BIAS_BLIND_ACCESS": 0,
        "V60_EOS_BIAS_TERM_POSITIONS": 36,
        "V60_EOS_BIAS_INTERMEDIATE_POSITIONS":
            intermediate_positions,
        "V60_EOS_BIAS_NONTERM_POSITIONS":
            nonterminal_positions,
        "V60_EOS_BIAS_TERM_COMPETITOR_ID":
            dominant_id,
        "V60_EOS_BIAS_TERM_COMPETITOR_COUNT":
            dominant_count,
        "V60_EOS_BIAS_TERM_MARGIN_MEAN_X1E3":
            scaled_margin(statistics.mean(terminal_margins)),
        "V60_EOS_BIAS_TERM_MARGIN_MEDIAN_X1E3":
            scaled_margin(statistics.median(terminal_margins)),
        "V60_EOS_BIAS_TERM_MARGIN_MAX_X1E3":
            scaled_margin(max(terminal_margins)),
        "V60_EOS_BIAS_INTERMEDIATE_MARGIN_MEAN_X1E3":
            scaled_margin(statistics.mean(intermediate_margins)),
        "V60_EOS_BIAS_NONTERM_MARGIN_MIN_X1E3":
            scaled_margin(min(nonterminal_margins)),
    }

    suffixes = {
        0.25: "025",
        0.50: "050",
        1.00: "100",
        2.00: "200",
    }
    for bias in BIASES:
        suffix = suffixes[bias]
        metrics[
            f"V60_EOS_BIAS_{suffix}_TERM_TOP1"
        ] = sweep_terminal[bias]
        metrics[
            f"V60_EOS_BIAS_{suffix}_INTERMEDIATE_TOP1"
        ] = sweep_intermediate[bias]
        metrics[
            f"V60_EOS_BIAS_{suffix}_NONTERM_TOP1"
        ] = sweep_nonterminal[bias]

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
