#!/usr/bin/env python3
"""Freeze the authorized V61 boundary-aware trainer without training."""

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

from mini_kuzai import phase03_v61_trainer as T

OUT = REPO / "reviews" / "smoltalk-v61-persistent-trainer-freeze"
TRAINER_SOURCE = REPO / "mini_kuzai" / "phase03_v61_trainer.py"
CLI_SOURCE = REPO / "tools" / "train_v61_boundary.py"
TEST_SOURCE = REPO / "tests" / "test_phase03_v61_trainer.py"
LOSS_SOURCE = REPO / "mini_kuzai" / "phase03_v61_boundary_loss.py"
LOSS_TEST = REPO / "tests" / "test_phase03_v61_boundary_loss.py"
PROTOCOL = (
    REPO / "reviews" / "smoltalk-v61-training-protocol"
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
            str(LOSS_SOURCE),
            str(LOSS_TEST),
        ]
    )
    trainer_test_output = run_checked(
        [sys.executable, str(TEST_SOURCE)]
    )
    loss_test_output = run_checked(
        [sys.executable, str(LOSS_TEST)]
    )

    for source in (TRAINER_SOURCE, CLI_SOURCE):
        text = source.read_text(encoding="utf-8")
        for forbidden in (
            "data/phase-03/blind-test",
            "/blind-test/",
        ):
            if forbidden in text:
                raise RuntimeError(
                    "V61 trainer contains forbidden BLIND corpus path"
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
    boundary_index, boundary_inventory = (
        T.build_boundary_index(final_freeze)
    )

    model = T.MODEL.MiniKuzaiPhase03V60(
        T.MODEL.Phase03Config()
    )
    parameter_count = T.MODEL.count_parameters(model)
    del model

    if parameter_count != T.MODEL_PARAMETERS:
        raise RuntimeError("V61 model parameter count changed")

    if sum(
        item["segments"]
        for item in training_inventory.values()
    ) != 345:
        raise RuntimeError("V61 training segment inventory mismatch")
    if sum(
        item["tokens"]
        for item in training_inventory.values()
    ) != 295416:
        raise RuntimeError("V61 training token inventory mismatch")
    if validation_inventory["records"] != 36:
        raise RuntimeError("V61 VALIDATION record count changed")
    if validation_inventory["segments"] != 36:
        raise RuntimeError("V61 VALIDATION segment count changed")

    if boundary_inventory != {
        "segments": 345,
        "terminal_boundaries": 345,
        "intermediate_boundaries": 159,
    }:
        raise RuntimeError("V61 boundary inventory changed")
    if len(boundary_index) != 345:
        raise RuntimeError("V61 boundary index size changed")

    max_tokens = protocol["exposure"][
        "initial_window_max_exposure_tokens"
    ]
    max_steps = protocol["exposure"][
        "initial_window_max_optimizer_steps"
    ]
    if max_tokens != 1181664 or max_steps != 145:
        raise RuntimeError("V61 hard limits changed")
    if protocol["scheduler"]["max_steps"] != 577:
        raise RuntimeError("V61 no longer preserves V60 LR trajectory")
    if schedule_preview["exposure_tokens"] <= 0:
        raise RuntimeError("V61 sampler preview is empty")
    if schedule_preview["exposure_tokens"] > max_tokens:
        raise RuntimeError("V61 sampler preview exceeds authorization")

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
        raise RuntimeError("V61 sampler preview exceeds share tolerance")

    core = {
        "schema_version": "v61-persistent-trainer-freeze-1",
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
        "boundary_loss_sha256":
            T.sha256_file(LOSS_SOURCE),
        "boundary_loss_test_sha256":
            T.sha256_file(LOSS_TEST),
        "protocol_sha256": T.sha256_file(PROTOCOL),
        "public_pool_sha256": T.sha256_file(T.PUBLIC_POOL),
        "py_compile_passed": True,
        "unit_tests_passed": True,
        "runtime_verify_passed": True,
        "model_parameters": parameter_count,
        "training_inventory": training_inventory,
        "validation_inventory": validation_inventory,
        "boundary_inventory": boundary_inventory,
        "schedule_preview": schedule_preview,
        "hard_limits": {
            "max_optimizer_steps": 145,
            "max_exposure_tokens": 1181664,
            "initial_window_cycles": 4,
            "scheduler_horizon_steps": 577,
        },
        "boundary_objective": {
            "terminal_weight": 16,
            "intermediate_weight": 16,
            "base_cross_entropy_unchanged": True,
        },
        "evaluation_policy": {
            "validation_every_exposure_tokens": 147708,
            "milestone_review_cycles": [1, 2, 4],
            "mandatory_continuation_review_cycles": [2],
            "generation_probe_max_new_tokens": 96,
            "blind_test_during_training": False,
        },
        "checkpoint_state": {
            "resume_supported": True,
            "optimizer": True,
            "scheduler": True,
            "rng": True,
            "sampler": True,
        },
        "training_authorized": True,
        "training_started": False,
    }
    freeze = {
        **core,
        "trainer_freeze_fingerprint":
            T.canonical_sha(core),
    }

    report = {
        "schema_version": "v61-persistent-trainer-freeze-report-1",
        "status": "FREEZE_READY_RUNTIME_VERIFY_PENDING",
        "trainer_freeze_fingerprint":
            freeze["trainer_freeze_fingerprint"],
        "training_segments": 345,
        "training_unique_tokens": 295416,
        "terminal_boundaries": 345,
        "intermediate_boundaries": 159,
        "preview_tokens":
            schedule_preview["exposure_tokens"],
        "preview_segments":
            schedule_preview["segments"],
        "preview_max_deviation_bp":
            max_deviation,
        "py_compile_passed": True,
        "unit_tests_passed": True,
        "runtime_verify_passed": False,
        "blind_test_accessed": False,
        "training_authorized": True,
        "training_started": False,
        "_compile_output": compile_output.strip(),
        "_trainer_test_output": trainer_test_output.strip(),
        "_loss_test_output": loss_test_output.strip(),
    }
    return freeze, report


def write_and_verify(freeze: dict, report: dict) -> dict:
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V61 trainer freeze output already exists")
    OUT.mkdir(parents=True)
    freeze_path = OUT / "TRAINER-FREEZE-001.json"

    try:
        freeze_path.write_text(
            json.dumps(freeze, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        runtime = T.verify_runtime(
            TRAINER_SOURCE,
            CLI_SOURCE,
        )
        if runtime["boundary_inventory"] != freeze["boundary_inventory"]:
            raise RuntimeError("V61 runtime boundary inventory mismatch")
        if runtime["schedule_preview"] != freeze["schedule_preview"]:
            raise RuntimeError("V61 runtime sampler preview mismatch")

        report = dict(report)
        report["status"] = "FROZEN_RUNTIME_VERIFIED"
        report["runtime_verify_passed"] = True
        report.pop("_compile_output", None)
        report.pop("_trainer_test_output", None)
        report.pop("_loss_test_output", None)

        (OUT / "REPORT-001.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        lines = [
            "# Mini-Kuzai V61 - persistent boundary trainer freeze",
            "",
            "Status --> **FROZEN / RUNTIME VERIFIED / TRAINING NOT STARTED**",
            "",
            "- trainer py_compile --> **PASS**",
            "- trainer tests --> **PASS**",
            "- boundary loss tests --> **PASS**",
            "- runtime verification --> **PASS**",
            "- model parameters --> **1184512**",
            "- training segments --> **345**",
            "- unique training tokens --> **295416**",
            "- terminal boundaries --> **345**",
            "- intermediate boundaries --> **159**",
            "- initial window --> **4 cycles / 1181664 tokens**",
            "- optimizer-step ceiling --> **145**",
            "- LR scheduler horizon --> **577 steps unchanged from V60**",
            "- mandatory continuation review --> **cycle 2**",
            "- boundary weights --> **16 / 16**",
            "- BLIND TEST --> **CLOSED**",
            "",
            "TRAINING_AUTHORIZED --> **1**",
            "TRAINING_STARTED --> **0**",
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
        return report
    except Exception:
        shutil.rmtree(OUT, ignore_errors=True)
        raise


def metrics(report: dict) -> dict:
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 0,
        "V61_TRAINER_FREEZE_PASS": 1,
        "V61_TRAINER_PYCOMPILE_PASS":
            int(bool(report["py_compile_passed"])),
        "V61_TRAINER_TESTS_PASS":
            int(bool(report["unit_tests_passed"])),
        "V61_TRAINER_RUNTIME_VERIFY_PASS":
            int(bool(report["runtime_verify_passed"])),
        "V61_TRAINER_TRAIN_SEGMENTS":
            report["training_segments"],
        "V61_TRAINER_TRAIN_UNIQUE_TOKENS":
            report["training_unique_tokens"],
        "V61_TRAINER_TERMINAL_BOUNDARIES":
            report["terminal_boundaries"],
        "V61_TRAINER_INTERMEDIATE_BOUNDARIES":
            report["intermediate_boundaries"],
        "V61_TRAINER_PREVIEW_TOKENS":
            report["preview_tokens"],
        "V61_TRAINER_PREVIEW_SEGMENTS":
            report["preview_segments"],
        "V61_TRAINER_PREVIEW_MAX_DEV_BP":
            report["preview_max_deviation_bp"],
        "V61_TRAINER_MAX_STEPS": 145,
        "V61_TRAINER_MAX_TOKENS": 1181664,
        "V61_TRAINER_REVIEW_CYCLE": 2,
        "V61_TRAINER_BLIND_ACCESS": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--from-report", action="store_true")
    args = parser.parse_args()

    if args.from_report:
        report = T.read_json(OUT / "REPORT-001.json")
    else:
        freeze, report = build_freeze()
        if args.write:
            report = write_and_verify(freeze, report)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics(report).items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
