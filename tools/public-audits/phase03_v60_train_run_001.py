#!/usr/bin/env python3
"""Publish numeric-only aggregate metrics for V60 TRAIN RUN 001."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

RUN_DIR = Path("/root/Mini-Kuzai/runs/v60-extended-001")
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"
MANIFEST = RUN_DIR / "RUN-MANIFEST.json"
METRICS = RUN_DIR / "metrics.jsonl"
PROBES = RUN_DIR / "validation-probes.jsonl"


def load_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe run artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe run artifact: {path}")
    values = []
    with path.open(encoding="utf-8") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise RuntimeError(f"Expected JSONL object: {path}")
            values.append(value)
    return values


def loss_x1e6(value) -> int:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise RuntimeError("Invalid validation loss")
    result = round(number * 1_000_000)
    if result > 100_000_000:
        raise RuntimeError("Validation loss outside public metric range")
    return result


def repeated_trigram_bp(text: str) -> int:
    if len(text) < 3:
        return 0
    grams = [
        text[index:index + 3]
        for index in range(len(text) - 2)
    ]
    repeated = len(grams) - len(set(grams))
    return round(repeated * 10000 / len(grams))


def max_char_run(text: str) -> int:
    if not text:
        return 0
    best = 1
    current = 1
    for left, right in zip(text, text[1:]):
        if right == left:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def main() -> None:
    summary = load_json(SUMMARY)
    manifest = load_json(MANIFEST)
    metric_rows = load_jsonl(METRICS)
    probe_rows = load_jsonl(PROBES)

    if summary.get("schema_version") != "v60-extended-run-summary-1":
        raise RuntimeError("Unexpected V60 run summary schema")
    if manifest.get("schema_version") != "v60-extended-run-1":
        raise RuntimeError("Unexpected V60 run manifest schema")
    if summary.get("status") != "STOPPED":
        raise RuntimeError("V60 run is not stopped")
    if manifest.get("status") != "STOPPED":
        raise RuntimeError("V60 run manifest is not stopped")
    if summary.get("training_started") is not True:
        raise RuntimeError("V60 training did not start")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("BLIND TEST was accessed")
    if manifest.get("blind_test_during_training") is not False:
        raise RuntimeError("Run manifest permits BLIND TEST access")
    if manifest.get("max_optimizer_steps") != 577:
        raise RuntimeError("Optimizer-step ceiling changed")
    if manifest.get("max_exposure_tokens") != 4726656:
        raise RuntimeError("Exposure-token window changed")

    steps = int(summary["optimizer_steps"])
    exposure = int(summary["exposure_tokens"])
    evaluations = int(summary["evaluations"])
    if not 0 < steps <= 577:
        raise RuntimeError("Optimizer-step count outside V60 window")
    if not 0 < exposure <= 4726656:
        raise RuntimeError("Exposure-token count outside V60 window")

    validation = [
        row
        for row in metric_rows
        if row.get("type") == "validation"
    ]
    if len(validation) != evaluations or not validation:
        raise RuntimeError("Validation metric inventory mismatch")
    if int(validation[0].get("step", -1)) != 0:
        raise RuntimeError("Initial validation is missing")

    initial_loss = float(validation[0]["validation_loss"])
    final_loss = float(validation[-1]["validation_loss"])
    best_loss = float(summary["best_validation_loss"])
    observed_best = min(
        float(row["validation_loss"])
        for row in validation
    )
    if abs(best_loss - observed_best) > 1e-9:
        raise RuntimeError("Best validation loss mismatch")

    final_step = int(validation[-1]["step"])
    final_exposure = int(validation[-1]["exposure_tokens"])
    if final_step != steps or final_exposure != exposure:
        raise RuntimeError("Final validation does not match run stop point")

    probes = [
        row
        for row in probe_rows
        if row.get("type") == "generation_probe"
    ]
    if not probes:
        raise RuntimeError("Generation probes are missing")
    final_probes = [
        row
        for row in probes
        if int(row.get("step", -1)) == steps
        and int(row.get("exposure_tokens", -1)) == exposure
    ]
    if len(final_probes) != 6:
        raise RuntimeError("Expected exactly six final V60 probes")

    texts = []
    hashes = set()
    final_tokens = 0
    utf8_invalid = 0
    eos = 0
    empty = 0
    repeat_bp_sum = 0
    max_run = 0

    for row in final_probes:
        text = row.get("generated_text")
        if not isinstance(text, str):
            raise RuntimeError("Generated probe text is invalid")
        texts.append(text)
        hashes.add(
            hashlib.sha256(text.encode("utf-8")).hexdigest()
        )
        final_tokens += int(row["generated_tokens"])
        utf8_invalid += int(
            row.get("generated_utf8_valid") is not True
        )
        eos += int(row.get("ended_with_eos") is True)
        empty += int(text == "")
        repeat_bp_sum += repeated_trigram_bp(text)
        max_run = max(max_run, max_char_run(text))

    stop = summary.get("stop_reason")
    allowed = {
        "MILESTONE_REVIEW_REQUIRED",
        "PLATEAU_REVIEW_REQUIRED",
        "EARLY_STOP_VALIDATION_DEGRADATION",
        "MAX_OPTIMIZER_STEPS",
        "MAX_EXPOSURE_TOKENS",
        "SAMPLER_EXHAUSTED",
    }
    if stop not in allowed:
        raise RuntimeError("Unexpected V60 stop reason")

    shares = summary.get("stream_share_bp")
    expected_streams = {
        "CONTROLLED_TRAIN",
        "PERSONA_CORE",
        "GENERAL_SUPPORT",
        "LEGACY_STRUCTURED_KEEP",
    }
    if not isinstance(shares, dict) or set(shares) != expected_streams:
        raise RuntimeError("Invalid stream-share inventory")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V60_RUN_COMPLETED": 1,
        "V60_RUN_OPTIMIZER_STEPS": steps,
        "V60_RUN_EXPOSURE_TOKENS": exposure,
        "V60_RUN_EVALUATIONS": evaluations,
        "V60_RUN_INITIAL_VAL_LOSS_X1E6": loss_x1e6(initial_loss),
        "V60_RUN_FINAL_VAL_LOSS_X1E6": loss_x1e6(final_loss),
        "V60_RUN_BEST_VAL_LOSS_X1E6": loss_x1e6(best_loss),
        "V60_RUN_FINAL_UTF8_INVALID": utf8_invalid,
        "V60_RUN_FINAL_EOS": eos,
        "V60_RUN_FINAL_DISTINCT": len(hashes),
        "V60_RUN_FINAL_MEAN_TOKENS_X100":
            round(final_tokens * 100 / len(final_probes)),
        "V60_RUN_FINAL_REPEAT_TRIGRAM_BP":
            round(repeat_bp_sum / len(final_probes)),
        "V60_RUN_FINAL_MAX_CHAR_RUN": max_run,
        "V60_RUN_FINAL_EMPTY": empty,
        "V60_RUN_BLIND_ACCESS": 0,
        "V60_RUN_STOP_MILESTONE": int(
            stop == "MILESTONE_REVIEW_REQUIRED"
        ),
        "V60_RUN_STOP_PLATEAU": int(
            stop == "PLATEAU_REVIEW_REQUIRED"
        ),
        "V60_RUN_STOP_EARLY_VALIDATION": int(
            stop == "EARLY_STOP_VALIDATION_DEGRADATION"
        ),
        "V60_RUN_STOP_MAX_STEPS": int(
            stop == "MAX_OPTIMIZER_STEPS"
        ),
        "V60_RUN_STOP_MAX_TOKENS": int(
            stop == "MAX_EXPOSURE_TOKENS"
        ),
        "V60_RUN_STOP_SAMPLER": int(
            stop == "SAMPLER_EXHAUSTED"
        ),
        "V60_RUN_CONTROLLED_SHARE_BP":
            int(shares["CONTROLLED_TRAIN"]),
        "V60_RUN_PERSONA_SHARE_BP":
            int(shares["PERSONA_CORE"]),
        "V60_RUN_GENERAL_SHARE_BP":
            int(shares["GENERAL_SUPPORT"]),
        "V60_RUN_LEGACY_SHARE_BP":
            int(shares["LEGACY_STRUCTURED_KEEP"]),
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
