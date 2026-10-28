#!/usr/bin/env python3
"""Freeze the V61 boundary-aware objective without authorizing training."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO / "reviews" / "smoltalk-v61-boundary-objective"
OBJECTIVE = SOURCE_ROOT / "OBJECTIVE-001.json"
PREFLIGHT_REPORT = SOURCE_ROOT / "REPORT-001.json"

OUT = REPO / "reviews" / "smoltalk-v61-boundary-objective-freeze"

LOSS_SOURCE = REPO / "mini_kuzai" / "phase03_v61_boundary_loss.py"
LOSS_TEST = REPO / "tests" / "test_phase03_v61_boundary_loss.py"
MODEL_SOURCE = REPO / "mini_kuzai" / "phase03_v60_model.py"
TOKENIZER = (
    REPO / "data" / "phase-03" / "tokenizers"
    / "tokenizer-v56-final.json"
)
SERIALIZER = REPO / "mini_kuzai" / "phase03_conversation.py"
SEGMENTATION = REPO / "mini_kuzai" / "phase03_segmentation.py"


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build() -> tuple[dict, dict]:
    objective = read_json(OBJECTIVE)
    report = read_json(PREFLIGHT_REPORT)

    if objective.get("status") != "OBJECTIVE_DEFINED_PREFLIGHT_PASSED":
        raise RuntimeError("V61 objective preflight did not pass")
    if report.get("status") != "PREFLIGHT_PASSED_FREEZE_REQUIRED":
        raise RuntimeError("V61 objective report is not freeze-ready")
    if report.get("objective") != objective:
        raise RuntimeError("V61 objective/report mismatch")
    if objective.get("training_authorized") is not False:
        raise RuntimeError("V61 objective unexpectedly authorizes training")
    if objective.get("training_started") is not False:
        raise RuntimeError("V61 objective marks training started")
    if objective.get("blind_test_accessed") is not False:
        raise RuntimeError("V61 objective indicates BLIND access")

    if objective.get("architecture") != "V60_UNCHANGED":
        raise RuntimeError("V61 architecture is not V60 unchanged")
    if objective.get("initialization") != "V60_INITIALIZATION_UNCHANGED":
        raise RuntimeError("V61 initialization changed")
    if objective.get("tokenizer") != "V56_UNCHANGED":
        raise RuntimeError("V61 tokenizer changed")
    if objective.get("corpus") != "V59_V60_FROZEN_CORPUS_UNCHANGED":
        raise RuntimeError("V61 corpus changed")
    if objective.get("base_objective") != "NEXT_TOKEN_CROSS_ENTROPY_UNCHANGED":
        raise RuntimeError("V61 base CE changed")

    boundary = objective.get("boundary_objective")
    if not isinstance(boundary, dict):
        raise RuntimeError("V61 boundary objective missing")
    if boundary["terminal"].get("weight") != 16:
        raise RuntimeError("V61 terminal boundary weight changed")
    if boundary["intermediate_assistant_boundary"].get("weight") != 16:
        raise RuntimeError("V61 intermediate boundary weight changed")

    selection = objective.get("selection")
    if not isinstance(selection, dict):
        raise RuntimeError("V61 objective selection missing")
    if selection.get("selected_weight") != 16:
        raise RuntimeError("V61 selected weight changed")
    if selection.get("selected_auxiliary_ratio_bp") != 463:
        raise RuntimeError("V61 auxiliary ratio changed")
    if selection.get("selected_boundary_gradient_multiplier") != 17:
        raise RuntimeError("V61 boundary gradient multiplier changed")

    expected_fingerprints = {
        "v61_boundary_loss_source_sha256": sha256_file(LOSS_SOURCE),
        "v61_boundary_loss_test_sha256": sha256_file(LOSS_TEST),
        "v60_model_source_sha256": sha256_file(MODEL_SOURCE),
        "tokenizer_sha256": sha256_file(TOKENIZER),
        "serializer_sha256": sha256_file(SERIALIZER),
        "segmentation_sha256": sha256_file(SEGMENTATION),
    }
    actual_fingerprints = objective.get("fingerprints")
    if not isinstance(actual_fingerprints, dict):
        raise RuntimeError("V61 objective fingerprint map missing")
    for key, expected in expected_fingerprints.items():
        if actual_fingerprints.get(key) != expected:
            raise RuntimeError(f"V61 objective dependency changed: {key}")

    core = {
        "schema_version": "v61-boundary-objective-freeze-1",
        "status": "FROZEN",
        "objective_sha256": sha256_file(OBJECTIVE),
        "preflight_report_sha256": sha256_file(PREFLIGHT_REPORT),
        "architecture": "V60_UNCHANGED",
        "initialization": "V60_INITIALIZATION_UNCHANGED",
        "tokenizer": "V56_UNCHANGED",
        "corpus": "V59_V60_FROZEN_CORPUS_UNCHANGED",
        "base_objective": "NEXT_TOKEN_CROSS_ENTROPY_UNCHANGED",
        "terminal_weight": 16,
        "intermediate_weight": 16,
        "auxiliary_ratio_bp": 463,
        "boundary_gradient_multiplier": 17,
        "dependencies": expected_fingerprints,
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }
    freeze = {
        **core,
        "objective_freeze_fingerprint": canonical_sha(core),
    }

    report_out = {
        "schema_version": "v61-boundary-objective-freeze-report-1",
        "status": "FROZEN_NOT_AUTHORIZED",
        "objective_freeze_fingerprint":
            freeze["objective_freeze_fingerprint"],
        "terminal_weight": 16,
        "intermediate_weight": 16,
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }
    return freeze, report_out


def write(freeze: dict, report: dict) -> None:
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V61 objective freeze output already exists")
    OUT.mkdir(parents=True)

    (OUT / "OBJECTIVE-FREEZE-001.json").write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUT / "REPORT-001.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Mini-Kuzai V61 - boundary-aware objective freeze",
        "",
        "Status --> **FROZEN / TRAINING NOT AUTHORIZED**",
        "",
        f"- terminal boundary weight --> **{freeze['terminal_weight']}**",
        f"- intermediate boundary weight --> **{freeze['intermediate_weight']}**",
        f"- auxiliary loss ratio --> **{freeze['auxiliary_ratio_bp'] / 100:.2f}%**",
        f"- boundary gradient multiplier --> **{freeze['boundary_gradient_multiplier']}x**",
        "- architecture --> **V60 unchanged**",
        "- tokenizer --> **V56 unchanged**",
        "- corpus --> **V59/V60 frozen corpus unchanged**",
        "- BLIND TEST --> **CLOSED**",
        "",
        "TRAINING_AUTHORIZED --> **0**",
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


def metrics(report: dict) -> dict:
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V61_OBJECTIVE_FREEZE_PASS": 1,
        "V61_OBJECTIVE_TERMINAL_WEIGHT": report["terminal_weight"],
        "V61_OBJECTIVE_INTERMEDIATE_WEIGHT":
            report["intermediate_weight"],
        "V61_OBJECTIVE_BLIND_ACCESS": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--from-report", action="store_true")
    args = parser.parse_args()

    if args.from_report:
        report = read_json(OUT / "REPORT-001.json")
    else:
        freeze, report = build()
        if args.write:
            write(freeze, report)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics(report).items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
