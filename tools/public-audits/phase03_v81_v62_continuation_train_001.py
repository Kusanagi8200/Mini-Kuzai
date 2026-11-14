#!/usr/bin/env python3
"""Public numeric audit for the completed V81 bounded V62 continuation."""

from __future__ import annotations

import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
SUMMARY = RUN / "RUN-SUMMARY.json"
MANIFEST = RUN / "RUN-MANIFEST.json"
METRICS = RUN / "metrics.jsonl"

V81_AUTH = (
    REPO / "reviews" / "smoltalk-v81-v62-continuation-authorization"
    / "TRAINING-AUTHORIZATION-001.json"
)
V81_AUTH_GOGIT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V81-CONTINUATION-AUTHORIZATION-001.json"
)

START_STEPS = 69
START_EXPOSURE = 597982
MAX_STEPS = 145
MAX_EXPOSURE = 1181664
EXPECTED_V62_AUTH_FP = (
    "f85deb2775f5b5db54472938e22d078198a9a041f88837bb641b26c8ad5f4ffd"
)
EXPECTED_TRAINER_FP = (
    "5ecba62748feba3aaf24c30abd741b3909d455a78c01f8684285e16d7334988c"
)


def load_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"Missing or unsafe JSONL: {path}")
    rows = []
    with path.open(encoding="utf-8") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise RuntimeError(f"Expected JSONL object: {path}")
            rows.append(value)
    return rows


def loss_x1e6(value) -> int:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise RuntimeError("Invalid validation loss")
    scaled = round(number * 1_000_000)
    if not 0 <= scaled <= 100_000_000:
        raise RuntimeError("Validation loss outside public metric range")
    return scaled


def main() -> None:
    summary = load_json(SUMMARY)
    manifest = load_json(MANIFEST)
    rows = load_jsonl(METRICS)
    auth = load_json(V81_AUTH)
    auth_gogit = load_json(V81_AUTH_GOGIT)

    if (
        auth.get("schema_version") != "v81-v62-continuation-authorization-1"
        or auth.get("status") != "FROZEN"
        or auth.get("training_authorized") is not True
        or auth.get("training_started") is not False
        or auth.get("resume_required") is not True
        or auth.get("max_total_optimizer_steps") != MAX_STEPS
        or auth.get("max_total_exposure_tokens") != MAX_EXPOSURE
        or auth.get("blind_test_during_training") is not False
    ):
        raise RuntimeError("V81 continuation authorization mismatch")

    if (
        auth_gogit.get("step_id")
        != "PHASE03-SMOLTALK-V81-CONTINUATION-AUTHORIZATION-001"
        or auth_gogit.get("training_authorized") is not True
        or auth_gogit.get("private_conversation_data_included") is not False
        or auth_gogit.get("metrics", {}).get("V81_AUTH_PASS") != 1
        or auth_gogit.get("metrics", {}).get("TRAINING_STARTED") != 0
        or auth_gogit.get("metrics", {}).get("V81_AUTH_BLIND_ACCESS") != 0
    ):
        raise RuntimeError("V81 continuation authorization GOGIT mismatch")

    if summary.get("schema_version") != "v62-margin-run-summary-1":
        raise RuntimeError("Unexpected V62 run summary schema")
    if manifest.get("schema_version") != "v62-margin-run-1":
        raise RuntimeError("Unexpected V62 run manifest schema")
    if summary.get("status") != "STOPPED" or manifest.get("status") != "STOPPED":
        raise RuntimeError("V81 continuation run is not stopped")
    if summary.get("training_started") is not True:
        raise RuntimeError("V81 continuation did not train")
    if manifest.get("training_started") is not True:
        raise RuntimeError("V81 run manifest does not mark training started")
    if manifest.get("resume") is not True:
        raise RuntimeError("V81 continuation was not a resume")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("V81 continuation accessed BLIND")
    if manifest.get("blind_test_during_training") is not False:
        raise RuntimeError("V81 manifest permits BLIND")
    if summary.get("stop_reason") != "MAX_EXPOSURE_TOKENS":
        raise RuntimeError("V81 continuation did not stop on exposure ceiling")
    if manifest.get("stop_reason") != "MAX_EXPOSURE_TOKENS":
        raise RuntimeError("V81 manifest stop reason mismatch")
    if manifest.get("max_optimizer_steps") != MAX_STEPS:
        raise RuntimeError("V62 optimizer-step ceiling changed")
    if manifest.get("max_exposure_tokens") != MAX_EXPOSURE:
        raise RuntimeError("V62 exposure ceiling changed")
    if summary.get("authorization_freeze_fingerprint") != EXPECTED_V62_AUTH_FP:
        raise RuntimeError("V62 authorization fingerprint changed")
    if summary.get("trainer_freeze_fingerprint") != EXPECTED_TRAINER_FP:
        raise RuntimeError("V62 trainer fingerprint changed")

    final_steps = int(summary["optimizer_steps"])
    final_exposure = int(summary["exposure_tokens"])
    delta_steps = final_steps - START_STEPS
    delta_exposure = final_exposure - START_EXPOSURE
    unused_exposure = MAX_EXPOSURE - final_exposure

    if not START_STEPS < final_steps <= MAX_STEPS:
        raise RuntimeError("Final optimizer steps outside V81 continuation window")
    if not START_EXPOSURE < final_exposure <= MAX_EXPOSURE:
        raise RuntimeError("Final exposure outside V81 continuation window")
    if delta_steps > 76 or delta_exposure > 583682:
        raise RuntimeError("V81 continuation exceeded remaining budget")
    if unused_exposure < 0:
        raise RuntimeError("V81 continuation exceeded exposure ceiling")

    validations = [row for row in rows if row.get("type") == "validation"]
    train_steps = [row for row in rows if row.get("type") == "train_step"]
    if not validations:
        raise RuntimeError("V81 continuation validation inventory empty")
    if len(validations) != int(summary["evaluations"]):
        raise RuntimeError("Validation count does not match run summary")

    final_validation = validations[-1]
    if (
        int(final_validation.get("step", -1)) != final_steps
        or int(final_validation.get("exposure_tokens", -1)) != final_exposure
    ):
        raise RuntimeError("Final validation does not match stop point")

    observed_best = min(float(row["validation_loss"]) for row in validations)
    best_loss = float(summary["best_validation_loss"])
    final_loss = float(final_validation["validation_loss"])
    if abs(observed_best - best_loss) > 1e-9:
        raise RuntimeError("Best validation loss mismatch")

    resumed_steps = [
        row for row in train_steps
        if int(row.get("step", -1)) > START_STEPS
    ]
    if len(resumed_steps) != delta_steps:
        raise RuntimeError("V81 resumed train-step inventory mismatch")
    if resumed_steps:
        if int(resumed_steps[0]["step"]) != START_STEPS + 1:
            raise RuntimeError("V81 resumed step sequence start mismatch")
        if int(resumed_steps[-1]["step"]) != final_steps:
            raise RuntimeError("V81 resumed step sequence end mismatch")

    shares = summary.get("stream_share_bp")
    expected_streams = {
        "CONTROLLED_TRAIN",
        "PERSONA_CORE",
        "GENERAL_SUPPORT",
        "LEGACY_STRUCTURED_KEEP",
    }
    if not isinstance(shares, dict) or set(shares) != expected_streams:
        raise RuntimeError("V81 stream-share inventory mismatch")
    if sum(int(v) for v in shares.values()) not in {9999, 10000, 10001}:
        raise RuntimeError("V81 stream shares do not sum to approximately 10000 bp")

    cycle2 = RUN / "checkpoint-cycle-02.pt"
    cycle4 = RUN / "checkpoint-cycle-04.pt"
    last = RUN / "checkpoint-last.pt"
    best = RUN / "checkpoint-best.pt"

    if cycle2.is_symlink() or not cycle2.is_file():
        raise RuntimeError("Frozen cycle-2 checkpoint missing")
    if cycle4.exists():
        raise RuntimeError("Cycle-4 milestone checkpoint unexpectedly exists below threshold")
    if last.is_symlink() or not last.is_file():
        raise RuntimeError("Final checkpoint-last missing")
    if best.is_symlink() or not best.is_file():
        raise RuntimeError("Best checkpoint missing")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 1,
        "V81_TRAIN_PASS": 1,
        "V81_TRAIN_BLIND_ACCESS": 0,
        "V81_TRAIN_RESUME": 1,
        "V81_TRAIN_STOP_MAX_TOKENS": 1,
        "V81_TRAIN_STOP_MAX_STEPS": 0,
        "V81_TRAIN_STOP_SAMPLER": 0,
        "V81_TRAIN_START_STEPS": START_STEPS,
        "V81_TRAIN_FINAL_STEPS": final_steps,
        "V81_TRAIN_DELTA_STEPS": delta_steps,
        "V81_TRAIN_MAX_STEPS": MAX_STEPS,
        "V81_TRAIN_START_EXPOSURE": START_EXPOSURE,
        "V81_TRAIN_FINAL_EXPOSURE": final_exposure,
        "V81_TRAIN_DELTA_EXPOSURE": delta_exposure,
        "V81_TRAIN_MAX_EXPOSURE": MAX_EXPOSURE,
        "V81_TRAIN_UNUSED_EXPOSURE": unused_exposure,
        "V81_TRAIN_EVALUATIONS": int(summary["evaluations"]),
        "V81_TRAIN_BEST_VAL_LOSS_X1E6": loss_x1e6(best_loss),
        "V81_TRAIN_FINAL_VAL_LOSS_X1E6": loss_x1e6(final_loss),
        "V81_TRAIN_CONTROLLED_SHARE_BP": int(shares["CONTROLLED_TRAIN"]),
        "V81_TRAIN_PERSONA_SHARE_BP": int(shares["PERSONA_CORE"]),
        "V81_TRAIN_GENERAL_SHARE_BP": int(shares["GENERAL_SUPPORT"]),
        "V81_TRAIN_LEGACY_SHARE_BP": int(shares["LEGACY_STRUCTURED_KEEP"]),
        "V81_TRAIN_CYCLE2_CHECKPOINT": 1,
        "V81_TRAIN_CYCLE4_CHECKPOINT": 0,
        "V81_TRAIN_LAST_CHECKPOINT": 1,
        "V81_TRAIN_BEST_CHECKPOINT": 1,
        "V81_TRAIN_WINDOW_CLOSED": 1,
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
