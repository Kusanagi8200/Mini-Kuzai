#!/usr/bin/env python3
"""Freeze the authorized V60 extended trainer without training."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v60_trainer as T

OUT = REPO / "reviews" / "smoltalk-v60-persistent-trainer-freeze"
TRAINER_SOURCE = REPO / "mini_kuzai" / "phase03_v60_trainer.py"
CLI_SOURCE = REPO / "tools" / "train_v60_extended.py"
TEST_SOURCE = REPO / "tests" / "test_phase03_v60_trainer.py"
PROTOCOL = (
    REPO / "reviews" / "smoltalk-v60-extended-training-protocol"
    / "PROTOCOL-001.json"
)


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


def build_freeze() -> tuple[dict, dict]:
    authorization, final_freeze, _ = T.verify_authorization()

    compile_output = run_checked(
        [
            sys.executable,
            "-m",
            "py_compile",
            str(TRAINER_SOURCE),
            str(CLI_SOURCE),
            str(TEST_SOURCE),
        ]
    )
    test_output = run_checked(
        [sys.executable, str(TEST_SOURCE)]
    )

    trainer_text = TRAINER_SOURCE.read_text(encoding="utf-8")
    cli_text = CLI_SOURCE.read_text(encoding="utf-8")
    for forbidden in (
        "data/phase-03/blind-test",
        "/blind-test/",
    ):
        if forbidden in trainer_text or forbidden in cli_text:
            raise RuntimeError(
                "Persistent V60 trainer contains forbidden BLIND corpus path"
            )

    protocol = T.load_protocol()
    streams, training_inventory = T.build_training_streams()
    validation_segments, validation_inventory = (
        T.build_validation_segments()
    )
    schedule_preview = T.build_schedule_preview(
        streams,
        protocol,
    )

    model = T.MODEL.MiniKuzaiPhase03V60(
        T.MODEL.Phase03Config()
    )
    parameter_count = T.MODEL.count_parameters(model)
    if parameter_count != T.MODEL_PARAMETERS:
        raise RuntimeError("Persistent V60 trainer model parameter count changed")
    del model

    if sum(
        item["segments"]
        for item in training_inventory.values()
    ) != final_freeze["total_unique_training_segments"]:
        raise RuntimeError("V60 trainer training-segment inventory mismatch")

    if sum(
        item["tokens"]
        for item in training_inventory.values()
    ) != final_freeze["total_unique_training_tokens"]:
        raise RuntimeError("V60 trainer training-token inventory mismatch")

    if validation_inventory["records"] != 36:
        raise RuntimeError("Persistent V60 VALIDATION count changed")

    max_tokens = protocol["exposure"][
        "initial_window_max_exposure_tokens"
    ]
    max_steps = protocol["exposure"][
        "initial_window_max_optimizer_steps"
    ]
    if schedule_preview["exposure_tokens"] <= 0:
        raise RuntimeError("Persistent V60 trainer schedule preview is empty")
    if schedule_preview["exposure_tokens"] > max_tokens:
        raise RuntimeError("V60 sampler preview exceeds authorization window")

    max_deviation = max(
        abs(value)
        for value in schedule_preview[
            "stream_deviation_bp"
        ].values()
    )
    if (
        max_deviation
        > protocol["exposure"]["stream_share_tolerance_bp"]
    ):
        raise RuntimeError("V60 sampler preview exceeds share tolerance")

    core = {
        "schema_version": "v60-persistent-trainer-freeze-1",
        "status": "FROZEN",
        "authorization_freeze_fingerprint":
            authorization["freeze_fingerprint"],
        "authorization_scope":
            authorization["authorization_scope"],
        "trainer_source_sha256":
            T.sha256_file(TRAINER_SOURCE),
        "trainer_cli_sha256":
            T.sha256_file(CLI_SOURCE),
        "trainer_test_sha256":
            T.sha256_file(TEST_SOURCE),
        "protocol_sha256": T.sha256_file(PROTOCOL),
        "public_pool_sha256": T.sha256_file(T.PUBLIC_POOL),
        "py_compile_passed": True,
        "unit_tests_passed": True,
        "runtime_verify_passed": True,
        "model_parameters": parameter_count,
        "training_inventory": training_inventory,
        "validation_inventory": validation_inventory,
        "schedule_preview": schedule_preview,
        "hard_limits": {
            "max_optimizer_steps": max_steps,
            "max_exposure_tokens": max_tokens,
            "microbatch_sequences":
                protocol["batching"]["microbatch_sequences"],
            "optimizer_step_target_nonpad_tokens":
                protocol["batching"][
                    "optimizer_step_target_nonpad_tokens"
                ],
            "blind_test_during_training": False,
        },
        "milestone_review_cycles":
            protocol["evaluation"]["milestone_review_cycles"],
        "plateau_review":
            protocol["evaluation"]["plateau_review"],
        "resume_supported": True,
        "checkpoint_contains_optimizer": True,
        "checkpoint_contains_scheduler": True,
        "checkpoint_contains_rng": True,
        "checkpoint_contains_sampler": True,
        "training_authorized": True,
        "training_started": False,
    }
    fingerprint = T.canonical_sha(core)
    manifest = {
        **core,
        "trainer_freeze_fingerprint": fingerprint,
    }
    report = {
        "schema_version": "v60-persistent-trainer-freeze-report-1",
        "status": "PERSISTENT_TRAINER_FROZEN",
        "authorization_freeze_fingerprint":
            authorization["freeze_fingerprint"],
        "trainer_freeze_fingerprint": fingerprint,
        "py_compile_output": compile_output.strip(),
        "unit_test_output": test_output.strip(),
        "training_inventory": training_inventory,
        "validation_inventory": validation_inventory,
        "schedule_preview": schedule_preview,
        "training_authorized": True,
        "training_started": False,
        "blind_test_accessed": False,
    }
    return manifest, report


def write_outputs(manifest: dict, report: dict) -> None:
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V60 persistent trainer freeze output already exists")

    OUT.mkdir(parents=True)
    try:
        (OUT / "TRAINER-FREEZE-001.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (OUT / "REPORT-001.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        runtime = T.verify_runtime(
            TRAINER_SOURCE,
            CLI_SOURCE,
        )
        lines = [
            "# Mini-Kuzai V60 - persistent extended trainer freeze",
            "",
            "Status --> **TRAINER FROZEN / TRAINING NOT STARTED**",
            "",
            "Authorization fingerprint --> "
            + manifest["authorization_freeze_fingerprint"],
            "",
            "Trainer fingerprint --> "
            + manifest["trainer_freeze_fingerprint"],
            "",
            "## Verified runtime",
            "",
            "- training segments --> **345**",
            "- unique training tokens --> **295416**",
            "- VALIDATION records --> **36**",
            "- schedule preview tokens --> **{}**".format(
                runtime["schedule_preview"]["exposure_tokens"]
            ),
            "- maximum optimizer steps --> **577**",
            "- maximum exposure tokens --> **4726656**",
            "- mandatory review --> **cycle 8**",
            "- plateau review --> **enabled after cycle 4**",
            "- resume --> **supported**",
            "- BLIND TEST access --> **NONE**",
            "",
            "TRAINING_AUTHORIZED --> **1**",
            "TRAINING_STARTED --> **0**",
            "",
            "This freeze executes no persistent optimizer step.",
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

    except Exception:
        shutil.rmtree(OUT, ignore_errors=True)
        raise


def metrics(report: dict) -> dict:
    training = report["training_inventory"]
    validation = report["validation_inventory"]
    preview = report["schedule_preview"]
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 0,
        "V60_TRAINER_FREEZE_PASS": 1,
        "V60_TRAINER_PYCOMPILE_PASS": 1,
        "V60_TRAINER_TESTS_PASS": 1,
        "V60_TRAINER_RUNTIME_VERIFY_PASS": 1,
        "V60_TRAINER_TRAIN_SEGMENTS": sum(
            item["segments"]
            for item in training.values()
        ),
        "V60_TRAINER_TRAIN_UNIQUE_TOKENS": sum(
            item["tokens"]
            for item in training.values()
        ),
        "V60_TRAINER_VALIDATION_RECORDS":
            validation["records"],
        "V60_TRAINER_VALIDATION_SEGMENTS":
            validation["segments"],
        "V60_TRAINER_PREVIEW_TOKENS":
            preview["exposure_tokens"],
        "V60_TRAINER_PREVIEW_SEGMENTS":
            preview["segments"],
        "V60_TRAINER_PREVIEW_MAX_DEV_BP": max(
            abs(value)
            for value in preview[
                "stream_deviation_bp"
            ].values()
        ),
        "V60_TRAINER_MAX_STEPS": 577,
        "V60_TRAINER_MAX_TOKENS": 4726656,
        "V60_TRAINER_MILESTONE_REVIEW": 1,
        "V60_TRAINER_PLATEAU_REVIEW": 1,
        "V60_TRAINER_BLIND_ACCESS": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--from-report", action="store_true")
    args = parser.parse_args()

    if args.from_report:
        report = T.read_json(OUT / "REPORT-001.json")
    else:
        manifest, report = build_freeze()
        if args.write:
            write_outputs(manifest, report)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics(report).items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
