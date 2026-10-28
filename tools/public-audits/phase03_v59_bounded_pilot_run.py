#!/usr/bin/env python3
"""Publish numeric-only aggregate metrics for the local V59 bounded pilot run."""
from __future__ import annotations
import json
import math
from pathlib import Path

RUN_DIR = Path("/root/Mini-Kuzai/runs/v59-bounded-pilot-001")
SUMMARY = RUN_DIR / "RUN-SUMMARY.json"
MANIFEST = RUN_DIR / "RUN-MANIFEST.json"

def load(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe run artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value

def main():
    summary = load(SUMMARY)
    manifest = load(MANIFEST)

    if summary.get("schema_version") != "v59-pilot-run-summary-1":
        raise RuntimeError("Unexpected V59 run summary schema")
    if summary.get("status") != "STOPPED":
        raise RuntimeError("V59 run is not stopped")
    if manifest.get("status") != "STOPPED":
        raise RuntimeError("V59 run manifest is not stopped")
    if summary.get("training_started") is not True:
        raise RuntimeError("V59 run did not start training")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("BLIND TEST was accessed")
    if manifest.get("blind_test_during_training") is not False:
        raise RuntimeError("Run manifest allows BLIND TEST")
    if manifest.get("max_optimizer_steps") != 145:
        raise RuntimeError("Optimizer-step limit changed")
    if manifest.get("max_exposure_tokens") != 1181664:
        raise RuntimeError("Exposure-token limit changed")

    steps = int(summary["optimizer_steps"])
    exposure = int(summary["exposure_tokens"])
    evaluations = int(summary["evaluations"])
    if steps <= 0 or steps > 145:
        raise RuntimeError("Optimizer-step count outside frozen budget")
    if exposure <= 0 or exposure > 1181664:
        raise RuntimeError("Exposure-token count outside frozen budget")

    loss = float(summary["best_validation_loss"])
    if not math.isfinite(loss) or loss < 0:
        raise RuntimeError("Invalid best validation loss")

    stop = summary.get("stop_reason")
    allowed_stops = {
        "MAX_OPTIMIZER_STEPS",
        "MAX_EXPOSURE_TOKENS",
        "EARLY_STOP_VALIDATION_DEGRADATION",
        "SAMPLER_EXHAUSTED",
    }
    if stop not in allowed_stops:
        raise RuntimeError("Unexpected V59 stop reason")

    streams = summary.get("stream_exposure_tokens")
    shares = summary.get("stream_share_bp")
    expected_streams = {
        "CONTROLLED_TRAIN",
        "PERSONA_CORE",
        "GENERAL_SUPPORT",
        "LEGACY_STRUCTURED_KEEP",
    }
    if not isinstance(streams, dict) or set(streams) != expected_streams:
        raise RuntimeError("Invalid stream exposure inventory")
    if not isinstance(shares, dict) or set(shares) != expected_streams:
        raise RuntimeError("Invalid stream share inventory")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "V59_MIX_FINALIZED": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V59_RUN_COMPLETED": 1,
        "V59_RUN_OPTIMIZER_STEPS": steps,
        "V59_RUN_EXPOSURE_TOKENS": exposure,
        "V59_RUN_EVALUATIONS": evaluations,
        "V59_RUN_BEST_VAL_LOSS_X1E6": round(loss * 1_000_000),
        "V59_RUN_BLIND_ACCESS": 0,
        "V59_RUN_STOP_MAX_STEPS": int(stop == "MAX_OPTIMIZER_STEPS"),
        "V59_RUN_STOP_MAX_TOKENS": int(stop == "MAX_EXPOSURE_TOKENS"),
        "V59_RUN_STOP_EARLY_VALIDATION": int(stop == "EARLY_STOP_VALIDATION_DEGRADATION"),
        "V59_RUN_STOP_SAMPLER": int(stop == "SAMPLER_EXHAUSTED"),
    }
    for stream in sorted(expected_streams):
        key = stream.replace("LEGACY_STRUCTURED_KEEP","LEGACY").replace("CONTROLLED_TRAIN","CONTROLLED").replace("GENERAL_SUPPORT","GENERAL").replace("PERSONA_CORE","PERSONA")
        metrics[f"V59_RUN_{key}_TOKENS"] = int(streams[stream])
        metrics[f"V59_RUN_{key}_SHARE_BP"] = int(shares[stream])

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
