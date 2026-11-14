#!/usr/bin/env python3
"""Create or verify V81 authorization for bounded V62 continuation.

This tool never starts training. It creates a governance freeze permitting only
resume of the existing V62 run inside the original four-cycle window.

Writing authorization artifacts requires both --authorize and --write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "reviews" / "smoltalk-v81-v62-continuation-authorization"

READINESS = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V81-V62-CONTINUATION-READINESS-001.json"
)
START_RECEIPT = REPO / "automation" / "dev-flow" / "receipts" / "V81-start.json"

V62_AUTH = (
    REPO / "reviews" / "smoltalk-v62-training-authorization"
    / "TRAINING-AUTHORIZATION-001.json"
)
V62_TRAIN_FREEZE = (
    REPO / "reviews" / "smoltalk-v62-training-authorization"
    / "TRAINING-FREEZE-001.json"
)
V62_TRAINER_FREEZE = (
    REPO / "reviews" / "smoltalk-v62-persistent-trainer-freeze"
    / "TRAINER-FREEZE-001.json"
)
V62_OBJECTIVE = (
    REPO / "reviews" / "smoltalk-v62-margin-objective-freeze"
    / "OBJECTIVE-FREEZE-001.json"
)
V62_PROTOCOL = (
    REPO / "reviews" / "smoltalk-v62-training-protocol"
    / "PROTOCOL-001.json"
)

RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
TRAINER = REPO / "mini_kuzai" / "phase03_v62_trainer.py"
TRAINER_CLI = REPO / "tools" / "train_v62_margin.py"

AUTH_FP = "f85deb2775f5b5db54472938e22d078198a9a041f88837bb641b26c8ad5f4ffd"
TRAINER_FP = "5ecba62748feba3aaf24c30abd741b3909d455a78c01f8684285e16d7334988c"
OBJECTIVE_FP = "68a0f92735e51e88c197f3e41dfd156e815e2174ae182517fdd045034156f9bd"
CORPUS_FP = "40008ff0b106d3c58d2bf8196f539be2bf692d1e8ed3b7cd0e2dd1429b887503"

CURRENT_STEPS = 69
CURRENT_EXPOSURE = 597982
MAX_STEPS = 145
MAX_EXPOSURE = 1181664
REMAINING_STEPS = 76
REMAINING_EXPOSURE = 583682


class AuthorizationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise AuthorizationError(message)


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        fail(f"Missing or unsafe JSON: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AuthorizationError(f"Invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        fail(f"Expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        fail(f"Missing or unsafe file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha(value: dict) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_inputs() -> dict:
    readiness = read_json(READINESS)
    start = read_json(START_RECEIPT)
    v62_auth = read_json(V62_AUTH)
    v62_freeze = read_json(V62_TRAIN_FREEZE)
    trainer_freeze = read_json(V62_TRAINER_FREEZE)
    objective = read_json(V62_OBJECTIVE)
    protocol = read_json(V62_PROTOCOL)
    summary = read_json(RUN / "RUN-SUMMARY.json")
    manifest = read_json(RUN / "RUN-MANIFEST.json")

    metrics = readiness.get("metrics")
    if not isinstance(metrics, dict):
        fail("V81 readiness metrics missing")
    if readiness.get("step_id") != "PHASE03-SMOLTALK-V81-V62-CONTINUATION-READINESS-001":
        fail("Unexpected V81 readiness report")
    if readiness.get("training_authorized") is not False:
        fail("V81 readiness unexpectedly authorizes training")
    if readiness.get("semantic_validation_complete") is not False:
        fail("V81 readiness unexpectedly claims semantic validation")
    required = {
        "V81_PASS": 1,
        "V81_V80_CLOSED": 1,
        "V81_V62_RUN_STOPPED": 1,
        "V81_V62_STOP_MILESTONE": 1,
        "V81_RESUME_SUPPORTED": 1,
        "V81_CHECKPOINT_CYCLE2_PRESENT": 1,
        "V81_CHECKPOINT_LAST_PRESENT": 1,
        "V81_TRAIN_LOCK_PRESENT": 0,
        "V81_REMAINING_STEPS": REMAINING_STEPS,
        "V81_REMAINING_EXPOSURE": REMAINING_EXPOSURE,
        "V81_BLIND_ACCESS": 0,
        "V81_GPU_EXECUTION": 0,
        "V81_PREFLIGHT_CHECKPOINT_WRITE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
    }
    for key, expected in required.items():
        if metrics.get(key) != expected:
            fail(f"V81 readiness mismatch: {key}")

    if (
        start.get("schema_version") != 1
        or start.get("command") != "START-DEV-FLOW"
        or start.get("step") != "V81"
        or start.get("status") != "PUBLISHED"
    ):
        fail("V81 START receipt is not published")

    if (
        v62_auth.get("status") != "FROZEN"
        or v62_auth.get("freeze_fingerprint") != AUTH_FP
        or v62_auth.get("authorization_scope") != "V62_MARGIN_INITIAL_WINDOW_ONLY"
        or v62_auth.get("v59_corpus_baseline_fingerprint") != CORPUS_FP
        or v62_auth.get("objective_freeze_fingerprint") != OBJECTIVE_FP
    ):
        fail("V62 training authorization freeze mismatch")

    if v62_freeze.get("status") != "FROZEN_FOR_MARGIN_INITIAL_WINDOW":
        fail("V62 training freeze status mismatch")

    scope = v62_freeze.get("authorization_scope")
    if not isinstance(scope, dict):
        fail("V62 training freeze scope missing")
    if (
        scope.get("name") != "V62_MARGIN_INITIAL_WINDOW_ONLY"
        or scope.get("initial_window_cycles") != 4
        or scope.get("max_optimizer_steps") != MAX_STEPS
        or scope.get("max_exposure_tokens") != MAX_EXPOSURE
        or scope.get("blind_test_during_training") is not False
    ):
        fail("V62 training freeze scope mismatch")

    checkpoint_state = trainer_freeze.get("checkpoint_state")
    if (
        trainer_freeze.get("status") != "FROZEN"
        or trainer_freeze.get("trainer_freeze_fingerprint") != TRAINER_FP
        or trainer_freeze.get("authorization_freeze_fingerprint") != AUTH_FP
        or not isinstance(checkpoint_state, dict)
    ):
        fail("V62 trainer freeze mismatch")
    for key in ("optimizer", "scheduler", "rng", "sampler", "resume_supported"):
        if checkpoint_state.get(key) is not True:
            fail(f"V62 checkpoint state missing: {key}")

    if trainer_freeze.get("trainer_source_sha256") != sha256_file(TRAINER):
        fail("Frozen V62 trainer source changed")
    if trainer_freeze.get("trainer_cli_sha256") != sha256_file(TRAINER_CLI):
        fail("Frozen V62 trainer CLI changed")

    if (
        objective.get("status") != "FROZEN"
        or objective.get("objective_freeze_fingerprint") != OBJECTIVE_FP
        or objective.get("margin") != 0.25
        or objective.get("terminal_weight") != 8.0
    ):
        fail("V62 objective freeze mismatch")

    if (
        protocol.get("status") != "PROTOCOL_DEFINED_PREFLIGHT_PASSED"
        or protocol.get("exposure", {}).get("initial_window_cycles") != 4
        or protocol.get("exposure", {}).get("initial_window_max_optimizer_steps") != MAX_STEPS
        or protocol.get("exposure", {}).get("initial_window_max_exposure_tokens") != MAX_EXPOSURE
        or protocol.get("evaluation", {}).get("blind_test_during_training") is not False
    ):
        fail("V62 protocol mismatch")

    if (
        summary.get("status") != "STOPPED"
        or summary.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED"
        or summary.get("optimizer_steps") != CURRENT_STEPS
        or summary.get("exposure_tokens") != CURRENT_EXPOSURE
        or summary.get("blind_test_accessed") is not False
    ):
        fail("V62 stopped run summary mismatch")

    if (
        manifest.get("status") != "STOPPED"
        or manifest.get("stop_reason") != "MILESTONE_REVIEW_REQUIRED"
        or manifest.get("optimizer_steps") != CURRENT_STEPS
        or manifest.get("exposure_tokens") != CURRENT_EXPOSURE
        or manifest.get("blind_test_during_training") is not False
    ):
        fail("V62 stopped run manifest mismatch")

    if (RUN / ".training.lock").exists():
        fail("V62 training lock already active")
    for path in (RUN / "checkpoint-cycle-02.pt", RUN / "checkpoint-last.pt"):
        if path.is_symlink() or not path.is_file():
            fail(f"Required V62 checkpoint missing or unsafe: {path.name}")

    return {
        "readiness_sha256": sha256_file(READINESS),
        "start_receipt_sha256": sha256_file(START_RECEIPT),
        "v62_authorization_sha256": sha256_file(V62_AUTH),
        "v62_training_freeze_sha256": sha256_file(V62_TRAIN_FREEZE),
        "v62_trainer_freeze_sha256": sha256_file(V62_TRAINER_FREEZE),
        "v62_objective_freeze_sha256": sha256_file(V62_OBJECTIVE),
        "v62_protocol_sha256": sha256_file(V62_PROTOCOL),
        "trainer_source_sha256": sha256_file(TRAINER),
        "trainer_cli_sha256": sha256_file(TRAINER_CLI),
    }


def build() -> tuple[dict, dict]:
    dependencies = verify_inputs()

    freeze = {
        "schema_version": "v81-v62-continuation-authorization-1",
        "status": "FROZEN",
        "authorization_scope": "V81_V62_INITIAL_WINDOW_REMAINDER_ONLY",
        "source_run": "v62-margin-001",
        "resume_required": True,
        "starting_optimizer_steps": CURRENT_STEPS,
        "starting_exposure_tokens": CURRENT_EXPOSURE,
        "max_total_optimizer_steps": MAX_STEPS,
        "max_total_exposure_tokens": MAX_EXPOSURE,
        "max_remaining_optimizer_steps": REMAINING_STEPS,
        "max_remaining_exposure_tokens": REMAINING_EXPOSURE,
        "initial_window_cycles": 4,
        "resume_from_cycle": 2,
        "final_review_cycle": 4,
        "v62_authorization_freeze_fingerprint": AUTH_FP,
        "v62_trainer_freeze_fingerprint": TRAINER_FP,
        "v62_objective_freeze_fingerprint": OBJECTIVE_FP,
        "v59_corpus_baseline_fingerprint": CORPUS_FP,
        "trainer_command": "tools/train_v62_margin.py --resume",
        "validation_allowed": True,
        "blind_test_during_training": False,
        "objective_changes_allowed": False,
        "tokenizer_changes_allowed": False,
        "architecture_changes_allowed": False,
        "corpus_changes_allowed": False,
        "stream_weight_changes_allowed": False,
        "scheduler_changes_allowed": False,
        "extension_beyond_cycle4_requires_new_protocol": True,
        "dependencies": dependencies,
        "training_authorized": True,
        "training_started": False,
    }
    fingerprint = canonical_sha(freeze)

    report = {
        "schema_version": "v81-v62-continuation-authorization-report-1",
        "status": "TRAINING_AUTHORIZED_NOT_STARTED",
        "authorization_scope": freeze["authorization_scope"],
        "freeze_fingerprint": fingerprint,
        "starting_optimizer_steps": CURRENT_STEPS,
        "starting_exposure_tokens": CURRENT_EXPOSURE,
        "max_total_optimizer_steps": MAX_STEPS,
        "max_total_exposure_tokens": MAX_EXPOSURE,
        "max_remaining_optimizer_steps": REMAINING_STEPS,
        "max_remaining_exposure_tokens": REMAINING_EXPOSURE,
        "resume_required": True,
        "final_review_cycle": 4,
        "blind_test_accessed": False,
        "training_authorized": True,
        "training_started": False,
    }
    return freeze, report


def write(freeze: dict, report: dict) -> None:
    if OUT.exists() or OUT.is_symlink():
        fail("V81 continuation authorization output already exists")
    OUT.mkdir(parents=True)

    fingerprint = canonical_sha(freeze)
    authorization = {
        "schema_version": "v81-v62-continuation-authorization-1",
        "status": "FROZEN",
        "authorization_scope": freeze["authorization_scope"],
        "freeze_fingerprint": fingerprint,
        "training_authorized": True,
        "training_started": False,
        "blind_test_during_training": False,
        "max_total_optimizer_steps": MAX_STEPS,
        "max_total_exposure_tokens": MAX_EXPOSURE,
        "max_remaining_optimizer_steps": REMAINING_STEPS,
        "max_remaining_exposure_tokens": REMAINING_EXPOSURE,
        "resume_required": True,
        "final_review_cycle": 4,
    }

    (OUT / "CONTINUATION-FREEZE-001.json").write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUT / "TRAINING-AUTHORIZATION-001.json").write_text(
        json.dumps(authorization, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUT / "REPORT-001.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def metrics(report: dict) -> dict[str, int]:
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 0,
        "V81_AUTH_PASS": 1,
        "V81_AUTH_BLIND_ACCESS": 0,
        "V81_AUTH_RESUME_REQUIRED": 1,
        "V81_AUTH_START_STEPS": report["starting_optimizer_steps"],
        "V81_AUTH_START_EXPOSURE": report["starting_exposure_tokens"],
        "V81_AUTH_MAX_TOTAL_STEPS": report["max_total_optimizer_steps"],
        "V81_AUTH_MAX_TOTAL_EXPOSURE": report["max_total_exposure_tokens"],
        "V81_AUTH_MAX_REMAINING_STEPS": report["max_remaining_optimizer_steps"],
        "V81_AUTH_MAX_REMAINING_EXPOSURE": report["max_remaining_exposure_tokens"],
        "V81_AUTH_FINAL_REVIEW_CYCLE": report["final_review_cycle"],
        "V81_AUTH_OBJECTIVE_CHANGES": 0,
        "V81_AUTH_TOKENIZER_CHANGES": 0,
        "V81_AUTH_ARCHITECTURE_CHANGES": 0,
        "V81_AUTH_CORPUS_CHANGES": 0,
        "V81_AUTH_STREAM_WEIGHT_CHANGES": 0,
        "V81_AUTH_SCHEDULER_CHANGES": 0,
        "V81_AUTH_EXTENSION_BEYOND_CYCLE4": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--from-report", action="store_true")
    args = parser.parse_args()

    if args.write and not args.authorize:
        fail("--write requires explicit --authorize")
    if args.from_report and (args.write or args.authorize):
        fail("--from-report cannot be combined with authorization flags")

    if args.from_report:
        report = read_json(OUT / "REPORT-001.json")
    else:
        freeze, report = build()
        if args.write:
            write(freeze, report)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics(report).items()):
        print(f"{key}: {value}")
    print(f"AUTHORIZATION_WRITE={int(args.write)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuthorizationError as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V81_AUTHORIZATION=BLOCKED")
        print(f"ERROR={exc}")
        raise SystemExit(1)
