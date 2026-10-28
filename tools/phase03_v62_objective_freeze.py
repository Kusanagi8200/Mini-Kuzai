#!/usr/bin/env python3
"""Freeze the V62 pairwise margin objective without authorizing training."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO / "reviews" / "smoltalk-v62-margin-objective"
OBJECTIVE = SOURCE_ROOT / "OBJECTIVE-001.json"
PREFLIGHT_REPORT = SOURCE_ROOT / "REPORT-001.json"
OUT = REPO / "reviews" / "smoltalk-v62-margin-objective-freeze"

LOSS_SOURCE = REPO / "mini_kuzai" / "phase03_v62_margin_loss.py"
LOSS_TEST = REPO / "tests" / "test_phase03_v62_margin_loss.py"
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


def build():
    objective = read_json(OBJECTIVE)
    report = read_json(PREFLIGHT_REPORT)

    if objective.get("status") != "OBJECTIVE_DEFINED_PREFLIGHT_PASSED":
        raise RuntimeError("V62 objective preflight did not pass")
    if report.get("status") != "PREFLIGHT_PASSED_FREEZE_REQUIRED":
        raise RuntimeError("V62 preflight report is not freeze-ready")
    if report.get("objective") != objective:
        raise RuntimeError("V62 objective/report mismatch")
    if objective.get("training_authorized") is not False:
        raise RuntimeError("V62 objective unexpectedly authorizes training")
    if objective.get("training_started") is not False:
        raise RuntimeError("V62 objective marks training started")
    if objective.get("blind_test_accessed") is not False:
        raise RuntimeError("V62 objective indicates BLIND access")
    if objective.get("architecture") != "V60_UNCHANGED":
        raise RuntimeError("V62 architecture changed")
    if objective.get("initialization") != "V60_INITIALIZATION_UNCHANGED":
        raise RuntimeError("V62 initialization changed")
    if objective.get("tokenizer") != "V56_UNCHANGED":
        raise RuntimeError("V62 tokenizer changed")
    if objective.get("corpus") != "V59_V60_FROZEN_CORPUS_UNCHANGED":
        raise RuntimeError("V62 corpus changed")

    margin_objective = objective.get("margin_objective")
    if not isinstance(margin_objective, dict):
        raise RuntimeError("V62 margin objective missing")

    margin = float(margin_objective["margin"])
    terminal_weight = float(margin_objective["terminal_weight"])
    intermediate_weight = float(
        margin_objective["intermediate_weight"]
    )
    balance = float(
        margin_objective["training_boundary_balance_factor"]
    )
    if margin <= 0 or terminal_weight <= 0 or intermediate_weight <= 0:
        raise RuntimeError("V62 selected objective is invalid")
    if abs(balance - (345 / 159)) > 1e-12:
        raise RuntimeError("V62 boundary balance factor changed")

    expected = {
        "v62_margin_loss_source_sha256": sha256_file(LOSS_SOURCE),
        "v62_margin_loss_test_sha256": sha256_file(LOSS_TEST),
        "v60_model_source_sha256": sha256_file(MODEL_SOURCE),
        "tokenizer_sha256": sha256_file(TOKENIZER),
        "serializer_sha256": sha256_file(SERIALIZER),
        "segmentation_sha256": sha256_file(SEGMENTATION),
    }
    actual = objective.get("fingerprints")
    if not isinstance(actual, dict):
        raise RuntimeError("V62 fingerprint map missing")
    for key, value in expected.items():
        if actual.get(key) != value:
            raise RuntimeError(f"V62 dependency changed: {key}")

    core = {
        "schema_version": "v62-margin-objective-freeze-1",
        "status": "FROZEN",
        "objective_sha256": sha256_file(OBJECTIVE),
        "preflight_report_sha256": sha256_file(PREFLIGHT_REPORT),
        "architecture": "V60_UNCHANGED",
        "initialization": "V60_INITIALIZATION_UNCHANGED",
        "tokenizer": "V56_UNCHANGED",
        "corpus": "V59_V60_FROZEN_CORPUS_UNCHANGED",
        "base_objective": "NEXT_TOKEN_CROSS_ENTROPY_UNCHANGED",
        "margin": margin,
        "terminal_weight": terminal_weight,
        "intermediate_weight": intermediate_weight,
        "training_boundary_balance_factor": balance,
        "dependencies": expected,
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }
    freeze = {
        **core,
        "objective_freeze_fingerprint": canonical_sha(core),
    }

    report_out = {
        "schema_version": "v62-margin-objective-freeze-report-1",
        "status": "FROZEN_NOT_AUTHORIZED",
        "objective_freeze_fingerprint":
            freeze["objective_freeze_fingerprint"],
        "margin": margin,
        "terminal_weight": terminal_weight,
        "intermediate_weight": intermediate_weight,
        "training_authorized": False,
        "training_started": False,
        "blind_test_accessed": False,
    }
    return freeze, report_out


def write(freeze, report):
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V62 objective freeze output already exists")
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
        "# Mini-Kuzai V62 - pairwise margin objective freeze",
        "",
        "Status --> **FROZEN / TRAINING NOT AUTHORIZED**",
        "",
        f"- margin --> **{freeze['margin']}**",
        f"- terminal weight --> **{freeze['terminal_weight']:.4f}**",
        f"- intermediate weight --> **{freeze['intermediate_weight']:.4f}**",
        f"- TRAIN balance factor --> **{freeze['training_boundary_balance_factor']:.6f}**",
        "- architecture / initialization / tokenizer / corpus --> **unchanged**",
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


def metrics(report):
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V62_OBJECTIVE_FREEZE_PASS": 1,
        "V62_OBJECTIVE_MARGIN_X1000":
            round(float(report["margin"]) * 1000),
        "V62_OBJECTIVE_TERMINAL_WEIGHT_X100":
            round(float(report["terminal_weight"]) * 100),
        "V62_OBJECTIVE_INTERMEDIATE_WEIGHT_X100":
            round(float(report["intermediate_weight"]) * 100),
        "V62_OBJECTIVE_BLIND_ACCESS": 0,
    }


def main():
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
