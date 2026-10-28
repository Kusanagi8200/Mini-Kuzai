#!/usr/bin/env python3
"""CLI for the frozen Mini-Kuzai V59 bounded pilot trainer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v59_trainer as trainer
THIS_FILE = Path(__file__).resolve()
TRAINER_SOURCE = REPO / "mini_kuzai" / "phase03_v59_trainer.py"
DEFAULT_RUN_DIR = Path("/root/Mini-Kuzai/runs/v59-bounded-pilot-001")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=DEFAULT_RUN_DIR,
    )
    parser.add_argument(
        "--resume",
        action="store_true",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
    )
    args = parser.parse_args()

    runtime = trainer.verify_runtime(
        TRAINER_SOURCE,
        THIS_FILE,
    )

    if args.verify_only:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V59_TRAINER_RUNTIME_VERIFY: PASS")
        print(
            "AUTHORIZATION_FREEZE_FINGERPRINT:",
            runtime["authorization"]["freeze_fingerprint"],
        )
        print(
            "TRAINER_FREEZE_FINGERPRINT:",
            runtime["trainer_freeze"]["trainer_freeze_fingerprint"],
        )
        print(
            "TRAINING_SEGMENTS:",
            sum(
                item["segments"]
                for item in runtime["training_inventory"].values()
            ),
        )
        print(
            "TRAINING_UNIQUE_TOKENS:",
            sum(
                item["tokens"]
                for item in runtime["training_inventory"].values()
            ),
        )
        print(
            "VALIDATION_RECORDS:",
            runtime["validation_inventory"]["records"],
        )
        print(
            "VALIDATION_SEGMENTS:",
            runtime["validation_inventory"]["segments"],
        )
        print(
            "SCHEDULE_PREVIEW_TOKENS:",
            runtime["schedule_preview"]["exposure_tokens"],
        )
        print("GPU:", runtime["gpu"])
        print("TRAINING_STARTED: 0")
        return

    summary = trainer.train(
        run_dir=args.run_dir.resolve(),
        trainer_source=TRAINER_SOURCE,
        cli_source=THIS_FILE,
        resume=args.resume,
    )

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print(
        "TRAINING_STARTED:",
        int(summary["training_started"]),
    )
    print(
        "STOP_REASON:",
        summary["stop_reason"],
    )
    print(
        "OPTIMIZER_STEPS:",
        summary["optimizer_steps"],
    )
    print(
        "EXPOSURE_TOKENS:",
        summary["exposure_tokens"],
    )
    print(
        "BEST_VALIDATION_LOSS:",
        summary["best_validation_loss"],
    )
    print(
        "BLIND_TEST_ACCESSED:",
        int(summary["blind_test_accessed"]),
    )
    print(
        "RUN_SUMMARY_JSON:",
        json.dumps(summary, sort_keys=True),
    )


if __name__ == "__main__":
    main()
