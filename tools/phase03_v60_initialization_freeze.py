#!/usr/bin/env python3
"""Freeze the validated V60 initialization baseline without training."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "reviews" / "smoltalk-v60-initialization-freeze"
MODEL = REPO / "mini_kuzai" / "phase03_v60_model.py"
TEST = REPO / "tests" / "phase-03" / "test_phase03_v60_initialization.py"
GATE_AUDIT = REPO / "tools" / "public-audits" / "phase03_v60_initialization_pretrain_gate.py"
GATE_REPORT = (
    REPO / "reports" / "assistant-results" / "history"
    / "PHASE03-SMOLTALK-V60-INITIALIZATION-PRETRAIN-GATE-001.json"
)
V59_AUTH = (
    REPO / "reviews" / "smoltalk-v59-final-mix-freeze-authorization"
    / "TRAINING-AUTHORIZATION-001.json"
)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe input: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha(value: dict) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build() -> tuple[dict, dict]:
    gate = read_json(GATE_REPORT)
    auth = read_json(V59_AUTH)
    metrics = gate.get("metrics")
    if not isinstance(metrics, dict):
        raise RuntimeError("V60 gate metrics missing")

    required = {
        "V60_INIT_GATE_PASS": 1,
        "V60_INIT_TESTS_PASS": 1,
        "V60_INIT_ARCH_MATCH": 1,
        "V60_INIT_PARAMS": 1184512,
        "V60_INIT_TIED": 1,
        "V60_INIT_PAD_ZERO": 1,
        "V60_INIT_BLIND_ACCESS": 0,
        "TRAINING_AUTHORIZED": 0,
    }
    for key, expected in required.items():
        if metrics.get(key) != expected:
            raise RuntimeError(f"V60 initialization gate mismatch: {key}")

    if auth.get("freeze_fingerprint") != (
        "40008ff0b106d3c58d2bf8196f539be2"
        "bf692d1e8ed3b7cd0e2dd1429b887503"
    ):
        raise RuntimeError("V59 corpus baseline fingerprint changed")

    core = {
        "schema_version": "v60-initialization-freeze-1",
        "status": "FROZEN",
        "architecture": "V58_SHAPE_IDENTICAL_V60_INITIALIZATION",
        "parameters": 1184512,
        "context_length": 2048,
        "vocab_size": 1024,
        "initialization": {
            "token_embedding_std": 0.02,
            "position_embedding_std": 0.02,
            "linear_weight_std": 0.02,
            "linear_bias": 0.0,
            "layernorm_weight": 1.0,
            "layernorm_bias": 0.0,
            "residual_output_std_formula": "0.02/sqrt(2*num_layers)",
            "pad_embedding_zero": True,
            "lm_head_tied_to_token_embedding": True,
        },
        "model_source_sha256": sha256_file(MODEL),
        "test_source_sha256": sha256_file(TEST),
        "gate_audit_sha256": sha256_file(GATE_AUDIT),
        "gate_report_sha256": sha256_file(GATE_REPORT),
        "v59_corpus_baseline_fingerprint": auth["freeze_fingerprint"],
        "tokenizer_file_sha256": auth["fingerprints"]["tokenizer_file_sha256"],
        "canonical_train_files_sha256": auth["fingerprints"][
            "canonical_train_files_sha256"
        ],
        "validation_master_sha256": auth["fingerprints"][
            "validation_master_sha256"
        ],
        "gate_metrics": {
            key: metrics[key]
            for key in sorted(metrics)
            if key.startswith("V60_INIT_")
        },
        "blind_test_accessed": False,
        "training_authorized": False,
        "training_started": False,
    }
    fingerprint = canonical_sha(core)
    manifest = {
        **core,
        "initialization_freeze_fingerprint": fingerprint,
    }
    report = {
        "schema_version": "v60-initialization-freeze-report-1",
        "status": "V60_INITIALIZATION_FROZEN",
        "initialization_freeze_fingerprint": fingerprint,
        "v59_corpus_baseline_fingerprint": auth["freeze_fingerprint"],
        "architecture_shape_unchanged": True,
        "gate_passed": True,
        "blind_test_accessed": False,
        "training_authorized": False,
        "training_started": False,
    }
    return manifest, report


def write(manifest: dict, report: dict) -> None:
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V60 initialization freeze output already exists")
    OUT.mkdir(parents=True)

    (OUT / "INITIALIZATION-FREEZE-001.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUT / "REPORT-001.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Mini-Kuzai V60 - initialization freeze",
        "",
        "Status --> **V60 INITIALIZATION FROZEN / TRAINING NOT AUTHORIZED**",
        "",
        "## Frozen baseline",
        "",
        "- architecture shape --> identical to V58",
        "- parameters --> **1184512**",
        "- token embedding initialization --> **N(0, 0.02)**",
        "- position embedding initialization --> **N(0, 0.02)**",
        "- linear initialization --> **N(0, 0.02)**",
        "- residual output projections --> **0.02 / sqrt(2 x num_layers)**",
        "- LM head / token embedding tying --> **YES**",
        "- PAD embedding --> **ZERO**",
        "- initialization gate --> **PASS**",
        "- BLIND TEST access --> **NONE**",
        "",
        "Initialization freeze fingerprint --> "
        + manifest["initialization_freeze_fingerprint"],
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


def metrics(manifest: dict) -> dict:
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
        "V60_INIT_FREEZE_PASS": 1,
        "V60_INIT_FREEZE_PARAMS": manifest["parameters"],
        "V60_INIT_FREEZE_BLIND_ACCESS": 0,
        "V60_INIT_FREEZE_TRAINING_STARTED": 0,
        "V60_INIT_FREEZE_GATE_PASS": int(
            manifest["gate_metrics"]["V60_INIT_GATE_PASS"]
        ),
    }


def main() -> None:
    manifest, report = build()
    write(manifest, report)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics(manifest).items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
