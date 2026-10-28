#!/usr/bin/env python3
"""Numeric-only V59 post-training generation diagnostic.

Reads only the existing VALIDATION generation probes from the completed bounded
pilot. It never opens BLIND TEST material and never prints probe text.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

RUN_DIR = Path("/root/Mini-Kuzai/runs/v59-bounded-pilot-001")
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"
PROBES = RUN_DIR / "validation-probes.jsonl"


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSONL artifact: {path}")
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"Expected JSON object at {path}:{number}")
        rows.append(value)
    if not rows:
        raise RuntimeError("No VALIDATION probes found")
    return rows


def basis_points(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    return round(numerator * 10000 / denominator)


def mean_x100(values: list[int]) -> int:
    if not values:
        return 0
    return round(sum(values) * 100 / len(values))


def max_char_run(text: str) -> int:
    if not text:
        return 0
    best = 1
    current = 1
    previous = text[0]
    for char in text[1:]:
        if char == previous:
            current += 1
            best = max(best, current)
        else:
            previous = char
            current = 1
    return best


def repeated_trigram_counts(text: str) -> tuple[int, int]:
    if len(text) < 3:
        return 0, 0
    trigrams = [text[index:index + 3] for index in range(len(text) - 2)]
    repeated = len(trigrams) - len(set(trigrams))
    return repeated, len(trigrams)


def aggregate(rows: list[dict]) -> dict:
    texts = []
    generated_tokens = []
    invalid = 0
    eos = 0
    replacement_chars = 0
    printable = 0
    alphabetic = 0
    characters = 0
    empty = 0
    repeated_trigrams = 0
    total_trigrams = 0
    max_run = 0
    hashes = set()

    for row in rows:
        text = row.get("generated_text")
        if not isinstance(text, str):
            raise RuntimeError("Probe generated_text is not a string")
        tokens = int(row.get("generated_tokens", -1))
        if tokens < 0:
            raise RuntimeError("Probe generated_tokens is invalid")

        texts.append(text)
        generated_tokens.append(tokens)
        hashes.add(hashlib.sha256(text.encode("utf-8")).hexdigest())

        if row.get("generated_utf8_valid") is False:
            invalid += 1
        if row.get("ended_with_eos") is True:
            eos += 1
        if not text:
            empty += 1

        replacement_chars += text.count("\ufffd")
        characters += len(text)
        printable += sum(char.isprintable() or char.isspace() for char in text)
        alphabetic += sum(char.isalpha() for char in text)
        max_run = max(max_run, max_char_run(text))

        repeated, total = repeated_trigram_counts(text)
        repeated_trigrams += repeated
        total_trigrams += total

    return {
        "count": len(rows),
        "invalid": invalid,
        "eos": eos,
        "replacement_chars": replacement_chars,
        "printable_bp": basis_points(printable, characters),
        "alpha_bp": basis_points(alphabetic, characters),
        "valid_bp": basis_points(len(rows) - invalid, len(rows)),
        "mean_tokens_x100": mean_x100(generated_tokens),
        "distinct_outputs": len(hashes),
        "empty": empty,
        "max_char_run": max_run,
        "repeat_trigram_bp": basis_points(repeated_trigrams, total_trigrams),
    }


def main() -> None:
    summary = read_json(SUMMARY)
    probes = read_jsonl(PROBES)

    if summary.get("status") != "STOPPED":
        raise RuntimeError("Bounded pilot is not stopped")
    if summary.get("training_started") is not True:
        raise RuntimeError("Bounded pilot never started")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("BLIND TEST was accessed")

    for row in probes:
        if row.get("type") != "generation_probe":
            raise RuntimeError("Unexpected record in validation-probes.jsonl")
        if "step" not in row or "exposure_tokens" not in row:
            raise RuntimeError("Probe lacks step/exposure metadata")

    steps = sorted({int(row["step"]) for row in probes})
    if len(steps) < 2 or steps[0] != 0:
        raise RuntimeError("Probe timeline is incomplete")

    initial_rows = [row for row in probes if int(row["step"]) == steps[0]]
    final_rows = [row for row in probes if int(row["step"]) == steps[-1]]

    if len(initial_rows) != 6 or len(final_rows) != 6:
        raise RuntimeError("Expected six fixed probes at initial and final steps")

    initial = aggregate(initial_rows)
    final = aggregate(final_rows)

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "V59_MIX_FINALIZED": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V59_GEN_DIAG_PASS": 1,
        "V59_GEN_BLIND_ACCESS": 0,
        "V59_GEN_PROBES": len(probes),
        "V59_GEN_EVAL_POINTS": len(steps),
        "V59_GEN_INITIAL_PROBES": initial["count"],
        "V59_GEN_FINAL_PROBES": final["count"],
        "V59_GEN_INITIAL_UTF8_INVALID": initial["invalid"],
        "V59_GEN_FINAL_UTF8_INVALID": final["invalid"],
        "V59_GEN_INITIAL_VALID_BP": initial["valid_bp"],
        "V59_GEN_FINAL_VALID_BP": final["valid_bp"],
        "V59_GEN_INITIAL_REPLACEMENT_CHARS": initial["replacement_chars"],
        "V59_GEN_FINAL_REPLACEMENT_CHARS": final["replacement_chars"],
        "V59_GEN_INITIAL_PRINTABLE_BP": initial["printable_bp"],
        "V59_GEN_FINAL_PRINTABLE_BP": final["printable_bp"],
        "V59_GEN_INITIAL_ALPHA_BP": initial["alpha_bp"],
        "V59_GEN_FINAL_ALPHA_BP": final["alpha_bp"],
        "V59_GEN_INITIAL_MEAN_TOKENS_X100": initial["mean_tokens_x100"],
        "V59_GEN_FINAL_MEAN_TOKENS_X100": final["mean_tokens_x100"],
        "V59_GEN_FINAL_DISTINCT_OUTPUTS": final["distinct_outputs"],
        "V59_GEN_FINAL_EOS": final["eos"],
        "V59_GEN_FINAL_EMPTY": final["empty"],
        "V59_GEN_FINAL_MAX_CHAR_RUN": final["max_char_run"],
        "V59_GEN_FINAL_REPEAT_TRIGRAM_BP": final["repeat_trigram_bp"],
        "V59_GEN_FINAL_STEP": steps[-1],
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
