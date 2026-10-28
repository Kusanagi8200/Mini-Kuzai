#!/usr/bin/env python3
"""Create the explicit V60 extended-window training authorization.

No training is executed. The BLIND corpus is not opened.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "reviews" / "smoltalk-v60-training-authorization"

V59_ROOT = REPO / "reviews" / "smoltalk-v59-final-mix-freeze-authorization"
V59_AUTH = V59_ROOT / "TRAINING-AUTHORIZATION-001.json"
V59_FREEZE = V59_ROOT / "FINAL-MIX-FREEZE-001.json"

INIT_FREEZE = (
    REPO / "reviews" / "smoltalk-v60-initialization-freeze"
    / "INITIALIZATION-FREEZE-001.json"
)
PROTOCOL = (
    REPO / "reviews" / "smoltalk-v60-extended-training-protocol"
    / "PROTOCOL-001.json"
)
PROTOCOL_REPORT = (
    REPO / "reviews" / "smoltalk-v60-extended-training-protocol"
    / "REPORT-001.json"
)

MODEL_SOURCE = REPO / "mini_kuzai" / "phase03_v60_model.py"
TOKENIZER_FILE = (
    REPO / "data" / "phase-03" / "tokenizers"
    / "tokenizer-v56-final.json"
)
SERIALIZER_SOURCE = REPO / "mini_kuzai" / "phase03_conversation.py"
SEGMENTATION_SOURCE = REPO / "mini_kuzai" / "phase03_segmentation.py"
VALIDATION_MASTER = (
    REPO / "data" / "phase-03" / "manifests"
    / "validation-master-v54.json"
)

EXPECTED_V59_FINGERPRINT = (
    "40008ff0b106d3c58d2bf8196f539be2"
    "bf692d1e8ed3b7cd0e2dd1429b887503"
)
EXPECTED_INIT_FINGERPRINT = (
    "2e64f9e4749710e03f32db220cfe1ab5"
    "b0a304ef250ebe9408ad0224799e4cb6"
)


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
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha(value) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build() -> tuple[dict, dict, dict]:
    v59_auth = read_json(V59_AUTH)
    v59_freeze = read_json(V59_FREEZE)
    init = read_json(INIT_FREEZE)
    protocol = read_json(PROTOCOL)
    protocol_report = read_json(PROTOCOL_REPORT)

    if v59_auth.get("freeze_fingerprint") != EXPECTED_V59_FINGERPRINT:
        raise RuntimeError("V59 corpus baseline fingerprint changed")
    if canonical_sha(v59_freeze) != EXPECTED_V59_FINGERPRINT:
        raise RuntimeError("V59 corpus freeze content changed")
    if init.get("status") != "FROZEN":
        raise RuntimeError("V60 initialization is not frozen")
    if (
        init.get("initialization_freeze_fingerprint")
        != EXPECTED_INIT_FINGERPRINT
    ):
        raise RuntimeError("Unexpected V60 initialization fingerprint")
    if init.get("training_authorized") is not False:
        raise RuntimeError("Initialization freeze unexpectedly authorizes training")
    if init.get("training_started") is not False:
        raise RuntimeError("Initialization freeze marks training started")
    if init.get("blind_test_accessed") is not False:
        raise RuntimeError("Initialization freeze indicates BLIND access")

    if protocol.get("status") != "PROTOCOL_DEFINED_PREFLIGHT_REQUIRED":
        raise RuntimeError("Unexpected V60 protocol state")
    if protocol.get("training_authorized") is not False:
        raise RuntimeError("Protocol unexpectedly authorizes training")
    if protocol.get("training_started") is not False:
        raise RuntimeError("Protocol marks training started")
    if (
        protocol.get("initialization_freeze_fingerprint")
        != EXPECTED_INIT_FINGERPRINT
    ):
        raise RuntimeError("Protocol targets another initialization freeze")
    if (
        protocol.get("v59_corpus_baseline_fingerprint")
        != EXPECTED_V59_FINGERPRINT
    ):
        raise RuntimeError("Protocol targets another corpus baseline")
    if protocol.get("parameters") != 1184512:
        raise RuntimeError("V60 parameter count changed")
    if protocol.get("context_length") != 2048:
        raise RuntimeError("V60 context changed")
    if protocol.get("vocab_size") != 1024:
        raise RuntimeError("V60 vocabulary changed")
    if (
        protocol.get("exposure", {}).get(
            "initial_window_max_exposure_tokens"
        )
        != 4726656
    ):
        raise RuntimeError("V60 initial exposure window changed")
    if (
        protocol.get("exposure", {}).get(
            "initial_window_max_optimizer_steps"
        )
        != 577
    ):
        raise RuntimeError("V60 initial step ceiling changed")
    if (
        protocol.get("evaluation", {}).get(
            "blind_test_during_training"
        )
        is not False
    ):
        raise RuntimeError("BLIND TEST access during V60 training is forbidden")

    if protocol_report.get("status") != "PREFLIGHT_PASSED_FREEZE_REQUIRED":
        raise RuntimeError("V60 protocol preflight did not pass")
    if protocol_report.get("protocol_freeze_candidate") is not True:
        raise RuntimeError("V60 protocol is not a freeze candidate")
    if protocol_report.get("training_authorized") is not False:
        raise RuntimeError("Protocol report unexpectedly authorizes training")
    if protocol_report.get("training_started") is not False:
        raise RuntimeError("Protocol report marks training started")
    if protocol_report.get("blind_test_accessed") is not False:
        raise RuntimeError("Protocol report indicates BLIND access")

    inherited = v59_auth.get("fingerprints")
    if not isinstance(inherited, dict):
        raise RuntimeError("V59 inherited fingerprint map missing")

    unchanged = {
        "tokenizer_file_sha256": sha256_file(TOKENIZER_FILE),
        "serializer_source_sha256": sha256_file(SERIALIZER_SOURCE),
        "segmentation_source_sha256": sha256_file(SEGMENTATION_SOURCE),
        "validation_master_sha256": sha256_file(VALIDATION_MASTER),
    }
    for key, actual in unchanged.items():
        if actual != inherited.get(key):
            raise RuntimeError(f"V59 inherited dependency changed: {key}")

    if v59_freeze.get("total_training_conversations") != 272:
        raise RuntimeError("Training conversation count changed")
    if v59_freeze.get("total_unique_training_segments") != 345:
        raise RuntimeError("Training segment count changed")
    if v59_freeze.get("total_unique_training_tokens") != 295416:
        raise RuntimeError("Training unique-token count changed")
    if v59_freeze.get("target_share_bp") != {
        "CONTROLLED_TRAIN": 3000,
        "PERSONA_CORE": 4658,
        "GENERAL_SUPPORT": 1500,
        "LEGACY_STRUCTURED_KEEP": 842,
    }:
        raise RuntimeError("Persona-first stream weighting changed")

    dependencies = {
        "v59_training_authorization_sha256": sha256_file(V59_AUTH),
        "v59_final_mix_freeze_sha256": sha256_file(V59_FREEZE),
        "v60_initialization_freeze_sha256": sha256_file(INIT_FREEZE),
        "v60_training_protocol_sha256": sha256_file(PROTOCOL),
        "v60_protocol_report_sha256": sha256_file(PROTOCOL_REPORT),
        "v60_model_source_sha256": sha256_file(MODEL_SOURCE),
        **unchanged,
    }

    freeze = {
        "schema_version": "v60-training-freeze-1",
        "status": "FROZEN_FOR_EXTENDED_INITIAL_WINDOW",
        "authorization_scope": {
            "name": "V60_EXTENDED_INITIAL_WINDOW_ONLY",
            "initial_window_cycles": 16,
            "max_exposure_tokens": 4726656,
            "max_optimizer_steps": 577,
            "validation_allowed": True,
            "blind_test_during_training": False,
            "extension_requires_new_protocol_freeze": True,
        },
        "v59_corpus_baseline_fingerprint": EXPECTED_V59_FINGERPRINT,
        "initialization_freeze_fingerprint": EXPECTED_INIT_FINGERPRINT,
        "controlled_train": v59_freeze["controlled_train"],
        "public_direct_keep": v59_freeze["public_direct_keep"],
        "training_streams": v59_freeze["training_streams"],
        "excluded_from_training": v59_freeze["excluded_from_training"],
        "total_training_conversations": 272,
        "total_unique_training_segments": 345,
        "total_unique_training_tokens": 295416,
        "target_share_bp": v59_freeze["target_share_bp"],
        "dependencies": dependencies,
        "training_authorized": True,
        "training_started": False,
    }
    fingerprint = canonical_sha(freeze)

    authorization = {
        "schema_version": "v60-training-authorization-1",
        "status": "FROZEN",
        "authorization_scope": "V60_EXTENDED_INITIAL_WINDOW_ONLY",
        "freeze_fingerprint": fingerprint,
        "v59_corpus_baseline_fingerprint": EXPECTED_V59_FINGERPRINT,
        "initialization_freeze_fingerprint": EXPECTED_INIT_FINGERPRINT,
        "max_exposure_tokens": 4726656,
        "max_optimizer_steps": 577,
        "target_share_bp": v59_freeze["target_share_bp"],
        "total_training_conversations": 272,
        "total_unique_training_segments": 345,
        "total_unique_training_tokens": 295416,
        "dependencies": dependencies,
        "blind_test_during_training": False,
        "extension_requires_new_protocol_freeze": True,
        "training_authorized": True,
        "training_started": False,
    }

    report = {
        "schema_version": "v60-training-authorization-report-1",
        "status": "TRAINING_AUTHORIZED_NOT_STARTED",
        "freeze_fingerprint": fingerprint,
        "v59_corpus_baseline_fingerprint": EXPECTED_V59_FINGERPRINT,
        "initialization_freeze_fingerprint": EXPECTED_INIT_FINGERPRINT,
        "max_exposure_tokens": 4726656,
        "max_optimizer_steps": 577,
        "training_segments": 345,
        "training_unique_tokens": 295416,
        "blind_test_accessed": False,
        "training_authorized": True,
        "training_started": False,
    }
    return freeze, authorization, report


def write(freeze: dict, authorization: dict, report: dict) -> None:
    if OUT.exists() or OUT.is_symlink():
        raise RuntimeError("V60 training authorization output already exists")
    OUT.mkdir(parents=True)

    (OUT / "TRAINING-FREEZE-001.json").write_text(
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

    lines = [
        "# Mini-Kuzai V60 - extended training authorization",
        "",
        "Status --> **TRAINING AUTHORIZED / NOT STARTED**",
        "",
        "Authorization freeze fingerprint --> "
        + authorization["freeze_fingerprint"],
        "",
        "## Authorized initial window",
        "",
        "- corpus baseline --> V59 frozen corpus",
        "- V60 initialization --> frozen",
        "- training conversations --> **272**",
        "- unique training segments --> **345**",
        "- unique training tokens --> **295416**",
        "- initial window cycles --> **16**",
        "- maximum exposure tokens --> **4726656**",
        "- maximum optimizer steps --> **577**",
        "- BLIND TEST during training --> **FORBIDDEN**",
        "- extension after cycle 16 --> **NEW PROTOCOL FREEZE REQUIRED**",
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


def metrics(report: dict) -> dict:
    return {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 0,
        "V60_AUTH_PASS": 1,
        "V60_AUTH_MAX_TOKENS": report["max_exposure_tokens"],
        "V60_AUTH_MAX_STEPS": report["max_optimizer_steps"],
        "V60_AUTH_TRAIN_SEGMENTS": report["training_segments"],
        "V60_AUTH_TRAIN_UNIQUE_TOKENS":
            report["training_unique_tokens"],
        "V60_AUTH_BLIND_ACCESS": 0,
        "V60_AUTH_EXTENSION_REQUIRES_FREEZE": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--from-report", action="store_true")
    args = parser.parse_args()

    if args.from_report:
        report = read_json(OUT / "REPORT-001.json")
    else:
        freeze, authorization, report = build()
        if args.write:
            write(freeze, authorization, report)

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics(report).items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
