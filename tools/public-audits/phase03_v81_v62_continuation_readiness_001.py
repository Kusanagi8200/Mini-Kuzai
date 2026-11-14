#!/usr/bin/env python3
"""CPU-only V81 readiness audit for resuming the frozen V62 initial window.

This audit performs no CUDA work, no optimizer step, no checkpoint write and
never opens BLIND data.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")

AUTH = REPO / "reviews/smoltalk-v62-training-authorization/TRAINING-AUTHORIZATION-001.json"
TRAIN_FREEZE = REPO / "reviews/smoltalk-v62-training-authorization/TRAINING-FREEZE-001.json"
TRAINER_FREEZE = REPO / "reviews/smoltalk-v62-persistent-trainer-freeze/TRAINER-FREEZE-001.json"
OBJECTIVE_FREEZE = REPO / "reviews/smoltalk-v62-margin-objective-freeze/OBJECTIVE-FREEZE-001.json"
V62_REPORT = REPO / "reports/assistant-results/history/PHASE03-SMOLTALK-V62-TRAIN-RUN-001.json"
V80_REPORT = REPO / "reports/assistant-results/history/PHASE03-SMOLTALK-V80-DECISION-BOUNDARY-PROXIMITY-CONTROL-001.json"
V80_RECEIPT = REPO / "automation/dev-flow/receipts/V80-final.json"
TRAINER = REPO / "mini_kuzai/phase03_v62_trainer.py"
TRAINER_CLI = REPO / "tools/train_v62_margin.py"

AUTH_FP = "f85deb2775f5bdb54472938e22d078198a9a041f88837bb641b26c8ad5f4ffd"
TRAINER_FP = "5ecba62748feba3aaf24c30abd741b3909d455a78c01f8684285e16d7334988c"
OBJECTIVE_FP = "68a0f92735e51e88c197f3e41dfd156e815e2174ae182517fdd045034156f9bd"
CORPUS_FP = "40008ff0b106d3c58d2bf8196f539be2bf692d1e8ed3b7cd0e2dd1429b887503"

CURRENT_STEPS = 69
CURRENT_EXPOSURE = 597982
MAX_STEPS = 145
MAX_EXPOSURE = 1181664
REMAINING_STEPS = MAX_STEPS - CURRENT_STEPS
REMAINING_EXPOSURE = MAX_EXPOSURE - CURRENT_EXPOSURE

MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"


def load_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"Missing or unsafe file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compute() -> dict[str, int]:
    auth = load_json(AUTH)
    train_freeze = load_json(TRAIN_FREEZE)
    trainer_freeze = load_json(TRAINER_FREEZE)
    objective = load_json(OBJECTIVE_FREEZE)
    v62 = load_json(V62_REPORT)
    v80 = load_json(V80_REPORT)
    receipt = load_json(V80_RECEIPT)

    summary = load_json(RUN / "RUN-SUMMARY.json")
    manifest = load_json(RUN / "RUN-MANIFEST.json")

    if auth.get("status") != "FROZEN":
        raise RuntimeError("V62 authorization is not frozen")
    if auth.get("freeze_fingerprint") != AUTH_FP:
        raise RuntimeError("V62 authorization fingerprint mismatch")
    if auth.get("authorization_scope") != "V62_MARGIN_INITIAL_WINDOW_ONLY":
        raise RuntimeError("V62 authorization scope mismatch")
    if auth.get("v59_corpus_baseline_fingerprint") != CORPUS_FP:
        raise RuntimeError("V59 corpus fingerprint mismatch")
    if auth.get("objective_freeze_fingerprint") != OBJECTIVE_FP:
        raise RuntimeError("V62 objective fingerprint mismatch")
    if auth.get("max_optimizer_steps") != MAX_STEPS:
        raise RuntimeError("V62 max optimizer steps mismatch")
    if auth.get("max_exposure_tokens") != MAX_EXPOSURE:
        raise RuntimeError("V62 max exposure mismatch")
    if auth.get("mandatory_continuation_review_cycle") != 2:
        raise RuntimeError("V62 continuation review cycle mismatch")
    if auth.get("blind_test_during_training") is not False:
        raise RuntimeError("V62 authorization permits BLIND access")

    scope = train_freeze.get("authorization_scope")
    if not isinstance(scope, dict):
        raise RuntimeError("V62 training freeze scope missing")
    if scope.get("name") != "V62_MARGIN_INITIAL_WINDOW_ONLY":
        raise RuntimeError("V62 training freeze scope mismatch")
    if scope.get("initial_window_cycles") != 4:
        raise RuntimeError("V62 initial window cycle count mismatch")
    if scope.get("max_optimizer_steps") != MAX_STEPS:
        raise RuntimeError("V62 training freeze step limit mismatch")
    if scope.get("max_exposure_tokens") != MAX_EXPOSURE:
        raise RuntimeError("V62 training freeze exposure limit mismatch")
    if scope.get("blind_test_during_training") is not False:
        raise RuntimeError("V62 training freeze permits BLIND access")

    if trainer_freeze.get("status") != "FROZEN":
        raise RuntimeError("V62 trainer freeze status mismatch")
    if trainer_freeze.get("trainer_freeze_fingerprint") != TRAINER_FP:
        raise RuntimeError("V62 trainer fingerprint mismatch")
    if trainer_freeze.get("authorization_freeze_fingerprint") != AUTH_FP:
        raise RuntimeError("V62 trainer targets another authorization")
    if trainer_freeze.get("authorization_scope") != "V62_MARGIN_INITIAL_WINDOW_ONLY":
        raise RuntimeError("V62 trainer authorization scope mismatch")

    checkpoint_state = trainer_freeze.get("checkpoint_state")
    if not isinstance(checkpoint_state, dict):
        raise RuntimeError("V62 checkpoint state missing")
    for key in ("optimizer", "scheduler", "rng", "sampler", "resume_supported"):
        if checkpoint_state.get(key) is not True:
            raise RuntimeError(f"V62 checkpoint state missing {key}")

    limits = trainer_freeze.get("hard_limits")
    if not isinstance(limits, dict):
        raise RuntimeError("V62 trainer limits missing")
    if limits.get("initial_window_cycles") != 4:
        raise RuntimeError("V62 trainer cycle limit mismatch")
    if limits.get("max_optimizer_steps") != MAX_STEPS:
        raise RuntimeError("V62 trainer max steps mismatch")
    if limits.get("max_exposure_tokens") != MAX_EXPOSURE:
        raise RuntimeError("V62 trainer max exposure mismatch")

    boundaries = trainer_freeze.get("boundary_inventory")
    if not isinstance(boundaries, dict):
        raise RuntimeError("V62 boundary inventory missing")
    if boundaries.get("segments") != 345:
        raise RuntimeError("V62 training segment inventory mismatch")
    if boundaries.get("terminal_boundaries") != 345:
        raise RuntimeError("V62 terminal boundary inventory mismatch")
    if boundaries.get("intermediate_boundaries") != 159:
        raise RuntimeError("V62 intermediate boundary inventory mismatch")

    if trainer_freeze.get("trainer_source_sha256") != sha256_file(TRAINER):
        raise RuntimeError("Frozen V62 trainer source changed")
    if trainer_freeze.get("trainer_cli_sha256") != sha256_file(TRAINER_CLI):
        raise RuntimeError("Frozen V62 trainer CLI changed")

    if objective.get("status") != "FROZEN":
        raise RuntimeError("V62 objective is not frozen")
    if objective.get("objective_freeze_fingerprint") != OBJECTIVE_FP:
        raise RuntimeError("V62 objective freeze fingerprint mismatch")
    if objective.get("margin") != 0.25:
        raise RuntimeError("V62 margin changed")
    if objective.get("terminal_weight") != 8.0:
        raise RuntimeError("V62 terminal weight changed")
    if abs(float(objective.get("intermediate_weight", 0.0)) - 17.358490566037737) > 1e-12:
        raise RuntimeError("V62 intermediate weight changed")

    v62_metrics = v62.get("metrics")
    if not isinstance(v62_metrics, dict):
        raise RuntimeError("Historical V62 metrics missing")
    if v62_metrics.get("V62_RUN1_OPTIMIZER_STEPS") != CURRENT_STEPS:
        raise RuntimeError("Historical V62 optimizer-step mismatch")
    if v62_metrics.get("V62_RUN1_EXPOSURE_TOKENS") != CURRENT_EXPOSURE:
        raise RuntimeError("Historical V62 exposure mismatch")
    if v62_metrics.get("V62_RUN1_STOP_MILESTONE") != 1:
        raise RuntimeError("Historical V62 milestone stop missing")
    if v62_metrics.get("V62_RUN1_BLIND_ACCESS") != 0:
        raise RuntimeError("Historical V62 BLIND access mismatch")

    v80_metrics = v80.get("metrics")
    if not isinstance(v80_metrics, dict):
        raise RuntimeError("V80 metrics missing")
    if v80_metrics.get("V80_PASS") != 1:
        raise RuntimeError("V80 is not scientifically closed")
    if v80_metrics.get("TRAINING_AUTHORIZED") != 0:
        raise RuntimeError("V80 unexpectedly authorizes training")
    if v80_metrics.get("TRAINING_STARTED") != 0:
        raise RuntimeError("V80 unexpectedly started training")
    if v80_metrics.get("V80_BLIND_ACCESS") != 0:
        raise RuntimeError("V80 BLIND access mismatch")

    if receipt.get("command") != "FINAL-DEV-FLOW":
        raise RuntimeError("V80 FINAL receipt command mismatch")
    if receipt.get("step") != "V80" or receipt.get("status") != "PUBLISHED":
        raise RuntimeError("V80 FINAL receipt not published")

    if summary.get("status") != "STOPPED":
        raise RuntimeError("V62 local run is not stopped")
    if summary.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED":
        raise RuntimeError("V62 local stop reason mismatch")
    if summary.get("optimizer_steps") != CURRENT_STEPS:
        raise RuntimeError("V62 local optimizer steps mismatch")
    if summary.get("exposure_tokens") != CURRENT_EXPOSURE:
        raise RuntimeError("V62 local exposure mismatch")
    if summary.get("blind_test_accessed") is not False:
        raise RuntimeError("V62 local run indicates BLIND access")

    if manifest.get("status") != "STOPPED":
        raise RuntimeError("V62 local manifest is not stopped")
    if manifest.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED":
        raise RuntimeError("V62 local manifest stop reason mismatch")
    if manifest.get("optimizer_steps") != CURRENT_STEPS:
        raise RuntimeError("V62 local manifest steps mismatch")
    if manifest.get("exposure_tokens") != CURRENT_EXPOSURE:
        raise RuntimeError("V62 local manifest exposure mismatch")
    if manifest.get("blind_test_during_training") is not False:
        raise RuntimeError("V62 local manifest permits BLIND access")

    cycle2 = RUN / "checkpoint-cycle-02.pt"
    last = RUN / "checkpoint-last.pt"
    if cycle2.is_symlink() or not cycle2.is_file():
        raise RuntimeError("V62 cycle-2 checkpoint missing or unsafe")
    if last.is_symlink() or not last.is_file():
        raise RuntimeError("V62 checkpoint-last missing or unsafe")

    lock_present = int((RUN / ".training.lock").exists())
    if lock_present:
        raise RuntimeError("V62 training lock is active")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V81_PASS": 1,
        "V81_BLIND_ACCESS": 0,
        "V81_V80_CLOSED": 1,
        "V81_V62_RUN_STOPPED": 1,
        "V81_V62_STOP_MILESTONE": 1,
        "V81_RESUME_SUPPORTED": 1,
        "V81_CHECKPOINT_CYCLE2_PRESENT": 1,
        "V81_CHECKPOINT_LAST_PRESENT": 1,
        "V81_TRAIN_LOCK_PRESENT": lock_present,
        "V81_CURRENT_STEPS": CURRENT_STEPS,
        "V81_CURRENT_EXPOSURE": CURRENT_EXPOSURE,
        "V81_MAX_STEPS": MAX_STEPS,
        "V81_MAX_EXPOSURE": MAX_EXPOSURE,
        "V81_REMAINING_STEPS": REMAINING_STEPS,
        "V81_REMAINING_EXPOSURE": REMAINING_EXPOSURE,
        "V81_INITIAL_WINDOW_CYCLES": 4,
        "V81_REVIEW_CYCLE": 2,
        "V81_TERMINAL_BOUNDARIES": 345,
        "V81_INTERMEDIATE_BOUNDARIES": 159,
        "V81_TRAIN_SEGMENTS": 345,
        "V81_TRAIN_UNIQUE_TOKENS": 295416,
        "V81_AUTH_FREEZE_MATCH": 1,
        "V81_TRAINER_FREEZE_MATCH": 1,
        "V81_OBJECTIVE_FREEZE_MATCH": 1,
        "V81_CORPUS_FREEZE_MATCH": 1,
        "V81_PREFLIGHT_CHECKPOINT_WRITE": 0,
        "V81_GPU_EXECUTION": 0,
    }

    if len(metrics) != 30:
        raise RuntimeError("V81 readiness schema must contain exactly 30 metrics")
    return metrics


def main() -> int:
    metrics = compute()
    print(MARKER)
    for key in sorted(metrics):
        print(f"{key}: {metrics[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
