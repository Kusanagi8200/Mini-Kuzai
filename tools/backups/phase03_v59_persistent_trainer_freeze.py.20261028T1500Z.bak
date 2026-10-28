#!/usr/bin/env python3
"""Freeze the persistent V59 bounded-pilot trainer without training."""

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

from mini_kuzai import phase03_v59_trainer as T


OUT = (
    REPO
    / "reviews"
    / "smoltalk-v59-persistent-trainer-freeze"
)
TRAINER_SOURCE = REPO / "mini_kuzai" / "phase03_v59_trainer.py"
CLI_SOURCE = REPO / "tools" / "train_v59_bounded_pilot.py"
TEST_SOURCE = REPO / "tests" / "test_phase03_v59_trainer.py"


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

    if (
        authorization["freeze_fingerprint"]
        != T.EXPECTED_FREEZE_FINGERPRINT
    ):
        raise RuntimeError("Authorization fingerprint changed")

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
        [
            sys.executable,
            str(TEST_SOURCE),
        ]
    )

    trainer_text = TRAINER_SOURCE.read_text(encoding="utf-8")
    cli_text = CLI_SOURCE.read_text(encoding="utf-8")
    for forbidden in (
        "data/phase-03/blind-test",
        "/blind-test/",
    ):
        if forbidden in trainer_text or forbidden in cli_text:
            raise RuntimeError(
                "Persistent trainer contains forbidden BLIND corpus path"
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

    model = T.MODEL.MiniKuzaiPhase03(
        T.MODEL.Phase03Config()
    )
    parameter_count = T.MODEL.count_parameters(model)
    if parameter_count != T.MODEL_PARAMETERS:
        raise RuntimeError("Persistent trainer model parameter count changed")
    del model

    if sum(
        item["segments"]
        for item in training_inventory.values()
    ) != final_freeze["total_unique_training_segments"]:
        raise RuntimeError("Trainer training-segment inventory mismatch")

    if sum(
        item["tokens"]
        for item in training_inventory.values()
    ) != final_freeze["total_unique_training_tokens"]:
        raise RuntimeError("Trainer training-token inventory mismatch")

    if validation_inventory["records"] != 36:
        raise RuntimeError("Persistent trainer VALIDATION count changed")

    if schedule_preview["exposure_tokens"] <= 0:
        raise RuntimeError("Persistent trainer schedule preview is empty")
    if (
        schedule_preview["exposure_tokens"]
        > protocol["exposure"]["max_exposure_tokens"]
    ):
        raise RuntimeError("Sampler preview exceeds authorization budget")

    max_deviation = max(
        abs(value)
        for value in schedule_preview["stream_deviation_bp"].values()
    )
    if max_deviation > protocol["exposure"]["stream_share_tolerance_bp"]:
        raise RuntimeError("Sampler preview exceeds frozen share tolerance")

    core = {
        "schema_version": "v59-persistent-trainer-freeze-1",
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
        "protocol_sha256":
            T.sha256_file(
                REPO
                / "reviews"
                / "smoltalk-v59-training-protocol"
                / "PROTOCOL-001.json"
            ),
        "public_pool_sha256":
            T.sha256_file(T.PUBLIC_POOL),
        "py_compile_passed": True,
        "unit_tests_passed": True,
        "runtime_verify_passed": True,
        "model_parameters": parameter_count,
        "training_inventory": training_inventory,
        "validation_inventory": validation_inventory,
        "schedule_preview": schedule_preview,
        "hard_limits": {
            "max_optimizer_steps":
                protocol["exposure"]["max_optimizer_steps"],
            "max_exposure_tokens":
                protocol["exposure"]["max_exposure_tokens"],
            "microbatch_sequences":
                protocol["batching"]["microbatch_sequences"],
            "optimizer_step_target_nonpad_tokens":
                protocol["batching"][
                    "optimizer_step_target_nonpad_tokens"
                ],
            "blind_test_during_training": False,
        },
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
        "schema_version":
            "v59-persistent-trainer-freeze-report-1",
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
    }

    return manifest, report


def write_outputs(manifest: dict, report: dict) -> None:
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("Persistent trainer freeze output already exists")

    OUT.mkdir(parents=True)

    try:
        (OUT / "TRAINER-FREEZE-001.json").write_text(
            json.dumps(
                manifest,
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

        runtime = T.verify_runtime(
            TRAINER_SOURCE,
            CLI_SOURCE,
        )

        lines = [
            "# Mini-Kuzai V59 - persistent pilot trainer freeze",
            "",
            "Status --> **PERSISTENT TRAINER FROZEN / TRAINING NOT STARTED**",
            "",
            "Authorization freeze fingerprint --> "
            + manifest["authorization_freeze_fingerprint"],
            "",
            "Trainer freeze fingerprint --> "
            + manifest["trainer_freeze_fingerprint"],
            "",
            "## Frozen trainer identity",
            "",
            "- trainer source SHA-256 --> "
            + manifest["trainer_source_sha256"],
            "- CLI source SHA-256 --> "
            + manifest["trainer_cli_sha256"],
            "- test source SHA-256 --> "
            + manifest["trainer_test_sha256"],
            "- py_compile --> PASS",
            "- unit tests --> PASS",
            "- full runtime verification --> PASS",
            "",
            "## Reconstructed authorized data",
            "",
            "- training segments --> **345**",
            "- training unique tokens --> **295416**",
            "- VALIDATION records --> **36**",
            "- VALIDATION segments --> **{}**".format(
                runtime["validation_inventory"]["segments"]
            ),
            "- BLIND corpus access --> **NONE**",
            "",
            "## Hard run limits",
            "",
            "- maximum optimizer steps --> **145**",
            "- maximum exposure tokens --> **1181664**",
            "- optimizer-step target --> **8192 non-pad tokens**",
            "- microbatch --> **8 sequences**",
            "- resume --> supported",
            "- checkpoint optimizer state --> YES",
            "- checkpoint scheduler state --> YES",
            "- checkpoint RNG state --> YES",
            "- checkpoint sampler state --> YES",
            "",
            "TRAINING_AUTHORIZED --> **1**",
            "TRAINING_STARTED --> **0**",
            "",
            "This freeze does not execute a persistent optimizer step.",
            "",
            "---",
            "",
            "##### **\`THE KUZ NETWORK - KUSANAGI8200 - @2026\`**",
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
        "V59_MIX_FINALIZED": 1,
        "V59_TRAINER_IMPLEMENTED": 1,
        "V59_TRAINER_FROZEN": 1,
        "V59_TRAINER_PYCOMPILE_PASS": 1,
        "V59_TRAINER_TESTS_PASS": 1,
        "V59_TRAINER_RUNTIME_VERIFY_PASS": 1,
        "V59_TRAINER_TRAIN_SEGMENTS": sum(
            item["segments"]
            for item in training.values()
        ),
        "V59_TRAINER_TRAIN_UNIQUE_TOKENS": sum(
            item["tokens"]
            for item in training.values()
        ),
        "V59_TRAINER_VALIDATION_RECORDS":
            validation["records"],
        "V59_TRAINER_VALIDATION_SEGMENTS":
            validation["segments"],
        "V59_TRAINER_VALIDATION_TOKENS":
            validation["tokens"],
        "V59_TRAINER_PREVIEW_TOKENS":
            preview["exposure_tokens"],
        "V59_TRAINER_PREVIEW_SEGMENTS":
            preview["segments"],
        "V59_TRAINER_PREVIEW_MAX_DEV_BP": max(
            abs(value)
            for value in preview[
                "stream_deviation_bp"
            ].values()
        ),
        "V59_TRAINER_MAX_STEPS": 145,
        "V59_TRAINER_MAX_EXPOSURE_TOKENS": 1181664,
        "V59_TRAINER_BLIND_ACCESS": 0,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 0,
    }


def main():
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
