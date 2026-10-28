#!/usr/bin/env python3
"""V60 EOS logit, rank and calibration diagnostic.

Reads only the local final V60 checkpoint and frozen VALIDATION split.
Publishes aggregate numeric metrics only. No BLIND TEST access.
"""

from __future__ import annotations

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
RUN2_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V60-TRAIN-RUN-002.json"
)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def ppm(value: float) -> int:
    if not math.isfinite(value) or value < 0:
        raise RuntimeError("Invalid probability metric")
    return round(value * 1_000_000)


def nll_x1e3(probability: float) -> int:
    if not math.isfinite(probability) or probability <= 0:
        raise RuntimeError("Invalid probability for NLL")
    value = -math.log(probability)
    result = round(value * 1000)
    if result > 100_000_000:
        raise RuntimeError("NLL metric exceeds public range")
    return result


def token_rank(logits: torch.Tensor, token_id: int) -> int:
    target = logits[token_id]
    # Rank 1 means no logit is strictly greater than the target.
    return int((logits > target).sum().item()) + 1


def load_validation_message_segments(tokenizer):
    master = T.read_json(T.VALIDATION_MASTER)
    expected_by_behavior = {
        item["behavior"]: item
        for item in master["behaviors"]
    }

    result = []
    seen = set()

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
            if source_id in seen:
                raise RuntimeError("Duplicate VALIDATION ID")
            seen.add(source_id)

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
        raise RuntimeError("Expected exactly 36 VALIDATION segments")
    return result


def assistant_boundary_target_indices(tokenizer, messages, ids):
    """Return target indices after intermediate assistant responses.

    Each index addresses the shifted target array ids[1:].
    The boundary is mapped by exact UTF-8 byte offsets against tokenizer token
    bytes. Unmappable boundaries are rejected rather than approximated.
    """
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
        raise RuntimeError("Validation re-encoding mismatch")

    # Byte offsets at the end of each assistant content except the terminal one.
    sections = []
    assistant_end_offsets = []
    byte_cursor = 0

    for index, message in enumerate(messages):
        if message["role"] == "user":
            header = T.CONV.USER_HEADER
        else:
            header = T.CONV.ASSISTANT_HEADER

        section = header + message["content"]
        section_bytes = section.encode("utf-8")
        sections.append(section)

        if message["role"] == "assistant":
            assistant_end_offsets.append(
                byte_cursor + len(section_bytes)
            )

        byte_cursor += len(section_bytes)
        if index < len(messages) - 1:
            byte_cursor += len(
                T.CONV.TURN_SEPARATOR.encode("utf-8")
            )

    if len(assistant_end_offsets) != len(messages) // 2:
        raise RuntimeError("Assistant boundary accounting mismatch")

    intermediate_offsets = assistant_end_offsets[:-1]
    if not intermediate_offsets:
        return []

    # ids[0] is BOS. Map cumulative source bytes to the next-token target index.
    cumulative = 0
    offset_to_input_index = {}
    for input_index, token_id in enumerate(ids[1:-1], start=1):
        value = token_bytes.get(int(token_id))
        if value is None:
            raise RuntimeError("Unknown tokenizer byte token")
        cumulative += len(value)
        offset_to_input_index[cumulative] = input_index

    if cumulative != len(text.encode("utf-8")):
        raise RuntimeError("Tokenizer byte accounting mismatch")

    target_indices = []
    for boundary in intermediate_offsets:
        input_index = offset_to_input_index.get(boundary)
        if input_index is None:
            raise RuntimeError(
                "Assistant boundary does not align to tokenizer token boundary"
            )
        # logits[input_index] predicts ids[input_index + 1].
        # shifted target array ids[1:] uses the same logit position input_index.
        target_indices.append(input_index)

    return target_indices


def probe_eos_stats(model, tokenizer, validation_segments, device):
    probes = T._fixed_probe_segments(validation_segments)

    best_ranks = []
    max_probs = []
    top1_total = 0
    steps_total = 0

    model.eval()
    with torch.no_grad():
        for segment in probes:
            serialized = tokenizer.decode(segment.token_ids)
            marker = "\n\nMINI-KUZAI:\n"
            position = serialized.find(marker)
            if position < 0:
                raise RuntimeError("Probe lacks assistant header")
            prompt = serialized[: position + len(marker)]
            generated = tokenizer.encode(
                prompt,
                add_bos=True,
                add_eos=False,
            )

            best_rank = T.VOCAB_SIZE + 1
            max_prob = 0.0

            for _ in range(96):
                input_ids = torch.tensor(
                    [generated],
                    dtype=torch.long,
                    device=device,
                )
                with torch.autocast(
                    device_type="cuda",
                    dtype=torch.bfloat16,
                ):
                    logits = model(input_ids)[0, -1].float()

                probs = torch.softmax(logits, dim=-1)
                eos_prob = float(probs[T.EOS_ID].item())
                eos_rank = token_rank(logits, T.EOS_ID)

                best_rank = min(best_rank, eos_rank)
                max_prob = max(max_prob, eos_prob)
                top1_total += int(eos_rank == 1)
                steps_total += 1

                next_id = int(torch.argmax(logits).item())
                generated.append(next_id)
                if next_id == T.EOS_ID:
                    break
                if len(generated) >= T.CONTEXT_LENGTH:
                    break

            best_ranks.append(best_rank)
            max_probs.append(max_prob)

    model.train()
    return {
        "probes": len(probes),
        "best_rank_mean": statistics.mean(best_ranks),
        "best_rank_median": statistics.median(best_ranks),
        "max_prob_mean": statistics.mean(max_probs),
        "max_prob_max": max(max_probs),
        "top1_total": top1_total,
        "steps_total": steps_total,
    }


def main() -> None:
    run2 = read_json(RUN2_REPORT)
    metrics = run2.get("metrics")
    if not isinstance(metrics, dict):
        raise RuntimeError("RUN 002 public metrics missing")
    if metrics.get("V60_RUN2_COMPLETED") != 1:
        raise RuntimeError("RUN 002 is not complete")
    if metrics.get("V60_RUN2_BLIND_ACCESS") != 0:
        raise RuntimeError("RUN 002 BLIND boundary violated")

    summary = read_json(SUMMARY)
    if summary.get("status") != "STOPPED":
        raise RuntimeError("V60 final run is not stopped")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("Final summary indicates BLIND access")

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
        raise RuntimeError("Unexpected V60 checkpoint schema")
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
    message_segments = load_validation_message_segments(tokenizer)
    validation_segments, validation_inventory = T.build_validation_segments()
    if validation_inventory["records"] != 36:
        raise RuntimeError("VALIDATION inventory changed")

    terminal_probs = []
    terminal_ranks = []
    terminal_top1 = 0

    nonterminal_prob_sum = 0.0
    nonterminal_positions = 0
    nonterminal_top1 = 0
    nonterminal_max_prob = 0.0

    intermediate_count = 0
    intermediate_eos_probs = []
    intermediate_eos_ranks = []
    intermediate_eos_top1 = 0
    intermediate_eos_over_true = 0

    with torch.no_grad():
        for item in message_segments:
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
                raw = model(token_ids)[0, :-1, :].float()

            targets = torch.tensor(
                ids[1:],
                dtype=torch.long,
                device=device,
            )
            if int(targets[-1].item()) != T.EOS_ID:
                raise RuntimeError("VALIDATION segment does not terminate in EOS")

            probs = torch.softmax(raw, dim=-1)
            eos_probs = probs[:, T.EOS_ID]

            # True terminal EOS position.
            terminal_logits = raw[-1]
            terminal_prob = float(eos_probs[-1].item())
            terminal_rank = token_rank(
                terminal_logits,
                T.EOS_ID,
            )
            terminal_probs.append(terminal_prob)
            terminal_ranks.append(terminal_rank)
            terminal_top1 += int(terminal_rank == 1)

            # All positions except the terminal EOS target.
            for position in range(raw.shape[0] - 1):
                probability = float(eos_probs[position].item())
                rank = token_rank(raw[position], T.EOS_ID)
                nonterminal_prob_sum += probability
                nonterminal_positions += 1
                nonterminal_top1 += int(rank == 1)
                nonterminal_max_prob = max(
                    nonterminal_max_prob,
                    probability,
                )

            # Intermediate assistant boundaries where the true target is
            # continuation toward a new USER turn.
            boundaries = assistant_boundary_target_indices(
                tokenizer,
                item["messages"],
                ids,
            )
            for logit_index in boundaries:
                if logit_index >= raw.shape[0]:
                    raise RuntimeError("Assistant boundary logit index invalid")
                true_id = int(ids[logit_index + 1])
                if true_id == T.EOS_ID:
                    raise RuntimeError("Intermediate assistant boundary targets EOS")

                logits = raw[logit_index]
                probabilities = probs[logit_index]
                eos_probability = float(
                    probabilities[T.EOS_ID].item()
                )
                true_probability = float(
                    probabilities[true_id].item()
                )
                eos_rank = token_rank(logits, T.EOS_ID)

                intermediate_count += 1
                intermediate_eos_probs.append(eos_probability)
                intermediate_eos_ranks.append(eos_rank)
                intermediate_eos_top1 += int(eos_rank == 1)
                intermediate_eos_over_true += int(
                    eos_probability > true_probability
                )

    if len(terminal_probs) != 36:
        raise RuntimeError("Terminal EOS position count changed")
    if intermediate_count <= 0:
        raise RuntimeError("No intermediate assistant boundaries found")
    if nonterminal_positions <= 0:
        raise RuntimeError("No nonterminal positions found")

    probe = probe_eos_stats(
        model,
        tokenizer,
        validation_segments,
        device,
    )

    terminal_mean_prob = statistics.mean(terminal_probs)
    terminal_mean_rank = statistics.mean(terminal_ranks)
    terminal_median_rank = statistics.median(terminal_ranks)

    metrics_out = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V60_EOS_LOGIT_DIAG_PASS": 1,
        "V60_EOS_LOGIT_BLIND_ACCESS": 0,
        "V60_EOS_TERM_POSITIONS": len(terminal_probs),
        "V60_EOS_TERM_PROB_PPM": ppm(terminal_mean_prob),
        "V60_EOS_TERM_NLL_X1E3": nll_x1e3(terminal_mean_prob),
        "V60_EOS_TERM_MEAN_RANK_X100": round(
            terminal_mean_rank * 100
        ),
        "V60_EOS_TERM_MEDIAN_RANK_X100": round(
            terminal_median_rank * 100
        ),
        "V60_EOS_TERM_TOP1": terminal_top1,
        "V60_EOS_NONTERM_POSITIONS": nonterminal_positions,
        "V60_EOS_NONTERM_PROB_PPM": ppm(
            nonterminal_prob_sum / nonterminal_positions
        ),
        "V60_EOS_NONTERM_MAX_PROB_PPM": ppm(
            nonterminal_max_prob
        ),
        "V60_EOS_NONTERM_TOP1": nonterminal_top1,
        "V60_EOS_INTERMEDIATE_BOUNDARIES": intermediate_count,
        "V60_EOS_INTERMEDIATE_PROB_PPM": ppm(
            statistics.mean(intermediate_eos_probs)
        ),
        "V60_EOS_INTERMEDIATE_MEAN_RANK_X100": round(
            statistics.mean(intermediate_eos_ranks) * 100
        ),
        "V60_EOS_INTERMEDIATE_TOP1": intermediate_eos_top1,
        "V60_EOS_INTERMEDIATE_OVER_TRUE": intermediate_eos_over_true,
        "V60_EOS_PROBE_COUNT": probe["probes"],
        "V60_EOS_PROBE_STEPS": probe["steps_total"],
        "V60_EOS_PROBE_MAXPROB_MEAN_PPM": ppm(
            probe["max_prob_mean"]
        ),
        "V60_EOS_PROBE_MAXPROB_MAX_PPM": ppm(
            probe["max_prob_max"]
        ),
        "V60_EOS_PROBE_BEST_RANK_MEAN_X100": round(
            probe["best_rank_mean"] * 100
        ),
        "V60_EOS_PROBE_BEST_RANK_MEDIAN_X100": round(
            probe["best_rank_median"] * 100
        ),
        "V60_EOS_PROBE_TOP1": probe["top1_total"],
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics_out.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
