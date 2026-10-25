#!/usr/bin/env python3
"""V56 tokenizer source-boundary audit.

Public aggregate audit only.

Tokenizer design inputs:
- canonical Phase 03 TRAIN corpus;
- public SmolTalk v0.4 reservoir.

Explicitly excluded:
- VALIDATION;
- BLIND TEST;
- private conversation material.

This audit does not select or freeze a tokenizer.
"""

import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SMOLTALK_POOL = Path(
    "/root/Mini-Kuzai/data/external/smol-smoltalk/"
    "candidates/external-candidate-pool-v0.4.jsonl"
)

TRAIN_DIR = REPO / "data/phase-03/train"

TRAIN_NAMES = [
    "train-pilot-v0.2.jsonl",
    *[
        "train-batch-b{:02d}-{}.jsonl".format(
            n,
            {8: "v0.5", 12: "v0.3"}.get(n, "v0.2"),
        )
        for n in range(1, 19)
    ],
]

MASTER = REPO / "data/phase-03/manifests/blind-master-v55.json"

CLOSURE_HISTORY = (
    REPO
    / "reports/assistant-results/history"
    / "PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001.json"
)

EXPECTED_SMOLTALK_SOURCES = {
    "smol-magpie-ultra-short": 5000,
    "openhermes-50k": 1500,
    "self-oss-instruct": 1000,
    "explore-instruct-rewrite": 500,
}

MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"


def load_json(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")

    value = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")

    return value


def load_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSONL: {path}")

    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not rows or not all(isinstance(row, dict) for row in rows):
        raise RuntimeError(f"Invalid JSONL: {path}")

    return rows


def valid_messages(messages):
    return (
        isinstance(messages, list)
        and bool(messages)
        and all(
            isinstance(message, dict)
            and message.get("role") in {"user", "assistant"}
            and isinstance(message.get("content"), str)
            and message["content"].strip()
            for message in messages
        )
    )


def verify_v55_closure():
    master = load_json(MASTER)

    if (
        master.get("status") != "CLOSED"
        or master.get("freeze_complete") is not True
        or master.get("global_blind_closure_complete") is not True
        or master.get("global_blind_closure_step_id")
        != "PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001"
        or master.get("training_authorized") is not False
    ):
        raise RuntimeError(
            "V55 global BLIND closure state is not valid"
        )

    history = load_json(CLOSURE_HISTORY)

    if (
        history.get("step_id")
        != "PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001"
        or history.get("semantic_validation_complete") is not True
        or history.get("training_authorized") is not False
    ):
        raise RuntimeError(
            "V55 closure history is not valid"
        )


def audit_train():
    rows = []

    for name in TRAIN_NAMES:
        rows.extend(load_jsonl(TRAIN_DIR / name))

    if len(TRAIN_NAMES) != 19:
        raise RuntimeError(
            "Canonical TRAIN file list changed"
        )

    if (
        len(rows) != 107
        or len({row.get("id") for row in rows}) != 107
        or len({row.get("group_id") for row in rows}) != 29
    ):
        raise RuntimeError(
            "Canonical TRAIN state changed"
        )

    messages = 0

    for row in rows:
        if row.get("split") != "train":
            raise RuntimeError(
                "Non-TRAIN record in tokenizer TRAIN input"
            )

        if not valid_messages(row.get("messages")):
            raise RuntimeError(
                "Invalid TRAIN messages"
            )

        messages += len(row["messages"])

    return rows, messages


def audit_smoltalk():
    if SMOLTALK_POOL.resolve().is_relative_to(REPO.resolve()):
        raise RuntimeError(
            "SmolTalk tokenizer source must remain outside Git"
        )

    if not SMOLTALK_POOL.is_file() or SMOLTALK_POOL.is_symlink():
        raise RuntimeError(
            "Public SmolTalk v0.4 reservoir missing or unsafe"
        )

    records = 0
    messages = 0
    sources = Counter()
    fingerprints = set()

    with SMOLTALK_POOL.open(encoding="utf-8") as stream:
        for raw in stream:
            if not raw.strip():
                continue

            row = json.loads(raw)

            source = row.get("source")
            fingerprint = row.get("content_sha256")
            row_messages = row.get("messages")

            if source not in EXPECTED_SMOLTALK_SOURCES:
                raise RuntimeError(
                    "Unexpected SmolTalk source"
                )

            if (
                not isinstance(fingerprint, str)
                or len(fingerprint) != 64
            ):
                raise RuntimeError(
                    "Invalid SmolTalk fingerprint"
                )

            if fingerprint in fingerprints:
                raise RuntimeError(
                    "Duplicate SmolTalk fingerprint"
                )

            if not valid_messages(row_messages):
                raise RuntimeError(
                    "Invalid SmolTalk messages"
                )

            fingerprints.add(fingerprint)
            sources[source] += 1
            records += 1
            messages += len(row_messages)

    if records != 8000:
        raise RuntimeError(
            "Unexpected SmolTalk reservoir size"
        )

    if dict(sources) != EXPECTED_SMOLTALK_SOURCES:
        raise RuntimeError(
            "Unexpected SmolTalk source distribution"
        )

    return records, messages, len(sources)


def audit():
    verify_v55_closure()

    _, train_messages = audit_train()

    (
        smoltalk_records,
        smoltalk_messages,
        smoltalk_sources,
    ) = audit_smoltalk()

    return dict(
        sorted(
            {
                "TRAIN_FILES": 19,
                "TRAIN_RECORDS": 107,
                "TRAIN_GROUPS": 29,
                "V56_TOKENIZER_SCOPE_TRAIN_MESSAGES":
                    train_messages,
                "V56_TOKENIZER_SCOPE_SMOLTALK_RECORDS":
                    smoltalk_records,
                "V56_TOKENIZER_SCOPE_SMOLTALK_MESSAGES":
                    smoltalk_messages,
                "V56_TOKENIZER_SCOPE_SMOLTALK_SOURCES":
                    smoltalk_sources,
                "V56_TOKENIZER_SCOPE_VALIDATION_INCLUDED": 0,
                "V56_TOKENIZER_SCOPE_BLIND_INCLUDED": 0,
                "V56_TOKENIZER_SCOPE_PRIVATE_INCLUDED": 0,
                "V56_TOKENIZER_FINALIZED": 0,
                "SEMANTIC_VALIDATION_COMPLETE": 1,
                "TRAINING_AUTHORIZED": 0,
            }.items()
        )
    )


def require_expected(metrics):
    expected_fixed = {
        "TRAIN_FILES": 19,
        "TRAIN_RECORDS": 107,
        "TRAIN_GROUPS": 29,
        "V56_TOKENIZER_SCOPE_SMOLTALK_RECORDS": 8000,
        "V56_TOKENIZER_SCOPE_SMOLTALK_SOURCES": 4,
        "V56_TOKENIZER_SCOPE_VALIDATION_INCLUDED": 0,
        "V56_TOKENIZER_SCOPE_BLIND_INCLUDED": 0,
        "V56_TOKENIZER_SCOPE_PRIVATE_INCLUDED": 0,
        "V56_TOKENIZER_FINALIZED": 0,
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
    }

    for key, value in expected_fixed.items():
        if metrics.get(key) != value:
            raise RuntimeError(
                f"{key}: expected {value}, "
                f"got {metrics.get(key)}"
            )

    if metrics.get(
        "V56_TOKENIZER_SCOPE_TRAIN_MESSAGES",
        0,
    ) <= 0:
        raise RuntimeError(
            "No canonical TRAIN messages found"
        )

    if metrics.get(
        "V56_TOKENIZER_SCOPE_SMOLTALK_MESSAGES",
        0,
    ) <= 0:
        raise RuntimeError(
            "No SmolTalk messages found"
        )


if __name__ == "__main__":
    result = audit()
    require_expected(result)

    print(MARKER)

    for key, value in result.items():
        print(f"{key}: {value}")
