#!/usr/bin/env python3
"""Persistent trainer for the authorized Mini-Kuzai V59 bounded pilot.

This module is deliberately fail-closed.

It does not accept hyperparameter overrides. The authorized corpus identity,
stream weights, architecture, optimizer protocol, validation boundary and hard
budgets are read from frozen repository manifests. The BLIND TEST corpus is
never opened by this module.

Persistent training is allowed only after:
- the terminal V59 authorization freeze verifies;
- the persistent trainer itself has a matching trainer-freeze manifest;
- the local public source pool matches its historical SHA-256;
- the reconstructed four training streams match frozen counts and token totals.
"""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
import math
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Iterator

import torch
import torch.nn.functional as F


REPO = Path(__file__).resolve().parents[1]

AUTH_ROOT = (
    REPO
    / "reviews"
    / "smoltalk-v59-final-mix-freeze-authorization"
)
AUTH_MANIFEST = AUTH_ROOT / "TRAINING-AUTHORIZATION-001.json"
FINAL_FREEZE = AUTH_ROOT / "FINAL-MIX-FREEZE-001.json"
AUTH_REPORT = AUTH_ROOT / "REPORT-001.json"

TRAINER_FREEZE_ROOT = (
    REPO
    / "reviews"
    / "smoltalk-v59-persistent-trainer-freeze"
)
TRAINER_FREEZE_MANIFEST = TRAINER_FREEZE_ROOT / "TRAINER-FREEZE-001.json"

TOKENIZER_MODULE = REPO / "mini_kuzai" / "tokenizer_v56.py"
TOKENIZER_FILE = (
    REPO
    / "data"
    / "phase-03"
    / "tokenizers"
    / "tokenizer-v56-final.json"
)
MODEL_MODULE = REPO / "mini_kuzai" / "phase03_model.py"
CONVERSATION_MODULE = REPO / "mini_kuzai" / "phase03_conversation.py"
SEGMENTATION_MODULE = REPO / "mini_kuzai" / "phase03_segmentation.py"

TRAIN_DIR = REPO / "data" / "phase-03" / "train"
VALIDATION_DIR = REPO / "data" / "phase-03" / "validation"
VALIDATION_MANIFEST_DIR = REPO / "data" / "phase-03" / "manifests"
VALIDATION_MASTER = (
    VALIDATION_MANIFEST_DIR / "validation-master-v54.json"
)

PUBLIC_POOL = Path(
    "/root/Mini-Kuzai/data/external/smol-smoltalk/"
    "candidates/external-candidate-pool-v0.4.jsonl"
)
PUBLIC_POOL_SHA256 = (
    "66867339aff94414d8b62ba2a2b7410c32db1771445b0475072729928ff08e5d"
)

TRAIN_NAMES = [
    "train-pilot-v0.2.jsonl",
    *[
        "train-batch-b{:02d}-{}.jsonl".format(
            number,
            {
                8: "v0.5",
                12: "v0.3",
            }.get(number, "v0.2"),
        )
        for number in range(1, 19)
    ],
]

STREAMS = (
    "CONTROLLED_TRAIN",
    "PERSONA_CORE",
    "GENERAL_SUPPORT",
    "LEGACY_STRUCTURED_KEEP",
)

EXPECTED_FREEZE_FINGERPRINT = (
    "40008ff0b106d3c58d2bf8196f539be2bf692d1e8ed3b7cd0e2dd1429b887503"
)

PAD_ID = 0
BOS_ID = 1
EOS_ID = 2
CONTEXT_LENGTH = 2048
VOCAB_SIZE = 1024
MODEL_PARAMETERS = 1184512


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TOK = _load_module(
    "mini_kuzai_v59_trainer_tokenizer",
    TOKENIZER_MODULE,
)
MODEL = _load_module(
    "mini_kuzai_v59_trainer_model",
    MODEL_MODULE,
)
CONV = _load_module(
    "mini_kuzai_v59_trainer_conversation",
    CONVERSATION_MODULE,
)
SEG = _load_module(
    "mini_kuzai_v59_trainer_segmentation",
    SEGMENTATION_MODULE,
)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe JSONL: {path}")
    values = []
    with path.open(encoding="utf-8") as stream:
        for line_number, raw in enumerate(stream, 1):
            if not raw.strip():
                continue
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise RuntimeError(
                    f"Invalid JSONL object: {path}:{line_number}"
                )
            values.append(value)
    return values


def sha256_file(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
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


def git_blob_sha(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe Git file: {path}")
    process = subprocess.run(
        ["git", "-C", str(REPO), "hash-object", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode:
        detail = process.stderr.strip() or process.stdout.strip()
        raise RuntimeError(
            f"Unable to compute Git blob SHA for {path}: {detail}"
        )
    return process.stdout.strip()


def _path_for_fingerprint(key: str) -> Path:
    mapping = {
        "final_policy_report_sha256":
            REPO
            / "reviews"
            / "smoltalk-v59-final-mix-policy"
            / "REPORT-001.json",
        "direct_keep_manifest_sha256":
            REPO
            / "reviews"
            / "smoltalk-v59-final-mix-policy"
            / "direct-keep-001.json",
        "exposure_report_sha256":
            REPO
            / "reviews"
            / "smoltalk-v59-persona-exposure-policy"
            / "REPORT-001.json",
        "sampler_policy_sha256":
            REPO
            / "reviews"
            / "smoltalk-v59-persona-exposure-policy"
            / "SAMPLER-POLICY-001.json",
        "preflight_report_sha256":
            REPO
            / "reviews"
            / "smoltalk-v59-training-protocol"
            / "REPORT-001.json",
        "training_protocol_sha256":
            REPO
            / "reviews"
            / "smoltalk-v59-training-protocol"
            / "PROTOCOL-001.json",
        "tokenizer_manifest_sha256":
            REPO
            / "data"
            / "phase-03"
            / "manifests"
            / "tokenizer-v56-final.json",
        "tokenizer_file_sha256":
            TOKENIZER_FILE,
        "architecture_manifest_sha256":
            REPO
            / "data"
            / "phase-03"
            / "manifests"
            / "architecture-v58-final.json",
        "architecture_config_sha256":
            REPO
            / "data"
            / "phase-03"
            / "config"
            / "architecture-v58-final.json",
        "model_source_sha256":
            MODEL_MODULE,
        "serializer_source_sha256":
            CONVERSATION_MODULE,
        "segmentation_source_sha256":
            SEGMENTATION_MODULE,
        "validation_master_sha256":
            VALIDATION_MASTER,
        "blind_master_sha256":
            REPO
            / "data"
            / "phase-03"
            / "manifests"
            / "blind-master-v55.json",
        "semantic_split_manifest_sha256":
            REPO
            / "data"
            / "phase-03"
            / "schema"
            / "semantic-group-split-manifest-v0.1.json",
    }
    path = mapping.get(key)
    if path is None:
        raise KeyError(key)
    return path


def _canonical_train_file_inventory() -> list[dict]:
    inventory = []
    for name in TRAIN_NAMES:
        path = TRAIN_DIR / name
        rows = read_jsonl(path)
        inventory.append(
            {
                "path": str(path.relative_to(REPO)),
                "sha256": sha256_file(path),
                "records": len(rows),
            }
        )
    return inventory


def verify_authorization() -> tuple[dict, dict, dict]:
    authorization = read_json(AUTH_MANIFEST)
    freeze = read_json(FINAL_FREEZE)
    report = read_json(AUTH_REPORT)

    if authorization.get("status") != "FROZEN":
        raise RuntimeError("V59 training authorization is not frozen")
    if authorization.get("training_authorized") is not True:
        raise RuntimeError("V59 training is not authorized")
    if authorization.get("training_started") is not False:
        raise RuntimeError(
            "Authorization manifest unexpectedly marks training as started"
        )
    if (
        authorization.get("authorization_scope")
        != "V59_BOUNDED_PILOT_ONLY"
    ):
        raise RuntimeError("Unexpected V59 authorization scope")

    fingerprint = authorization.get("freeze_fingerprint")
    if fingerprint != EXPECTED_FREEZE_FINGERPRINT:
        raise RuntimeError("Unexpected terminal V59 freeze fingerprint")
    if canonical_sha(freeze) != fingerprint:
        raise RuntimeError("Terminal V59 freeze content fingerprint mismatch")
    if report.get("freeze_fingerprint") != fingerprint:
        raise RuntimeError("Authorization report freeze fingerprint mismatch")
    if report.get("training_authorized") is not True:
        raise RuntimeError("Authorization report does not authorize training")
    if report.get("training_started") is not False:
        raise RuntimeError("Authorization report marks training as started")

    if authorization.get("max_optimizer_steps") != 145:
        raise RuntimeError("Authorized optimizer-step budget changed")
    if authorization.get("max_exposure_tokens") != 1181664:
        raise RuntimeError("Authorized exposure-token budget changed")
    if authorization.get("blind_test_during_training") is not False:
        raise RuntimeError("BLIND TEST access during training is forbidden")

    if freeze.get("status") != "FROZEN_FOR_BOUNDED_PILOT":
        raise RuntimeError("Final mix is not frozen for the bounded pilot")
    if freeze.get("total_training_conversations") != 272:
        raise RuntimeError("Frozen training conversation count changed")
    if freeze.get("total_unique_training_segments") != 345:
        raise RuntimeError("Frozen training segment count changed")
    if freeze.get("total_unique_training_tokens") != 295416:
        raise RuntimeError("Frozen unique training-token count changed")

    frozen_fingerprints = authorization.get("fingerprints")
    if not isinstance(frozen_fingerprints, dict):
        raise RuntimeError("Missing frozen dependency fingerprints")

    for key, expected in sorted(frozen_fingerprints.items()):
        if key == "canonical_train_files_sha256":
            actual = canonical_sha(_canonical_train_file_inventory())
        else:
            actual = sha256_file(_path_for_fingerprint(key))
        if actual != expected:
            raise RuntimeError(
                f"Frozen dependency changed: {key}"
            )

    return authorization, freeze, report


def verify_trainer_freeze(
    trainer_source: Path,
    cli_source: Path,
) -> dict:
    freeze = read_json(TRAINER_FREEZE_MANIFEST)

    fingerprint = freeze.get("trainer_freeze_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise RuntimeError("Persistent trainer freeze fingerprint is invalid")
    core = {
        key: value
        for key, value in freeze.items()
        if key != "trainer_freeze_fingerprint"
    }
    if canonical_sha(core) != fingerprint:
        raise RuntimeError("Persistent trainer freeze content mismatch")

    if freeze.get("status") != "FROZEN":
        raise RuntimeError("Persistent trainer is not frozen")
    if freeze.get("training_authorized") is not True:
        raise RuntimeError("Trainer freeze lost V59 authorization")
    if freeze.get("training_started") is not False:
        raise RuntimeError("Trainer freeze marks training as already started")
    if (
        freeze.get("authorization_freeze_fingerprint")
        != EXPECTED_FREEZE_FINGERPRINT
    ):
        raise RuntimeError("Trainer freeze targets a different authorization")

    expected_trainer = freeze.get("trainer_source_sha256")
    expected_cli = freeze.get("trainer_cli_sha256")

    if sha256_file(trainer_source) != expected_trainer:
        raise RuntimeError("Persistent trainer source changed after freeze")
    if sha256_file(cli_source) != expected_cli:
        raise RuntimeError("Persistent trainer CLI changed after freeze")

    return freeze


def load_tokenizer():
    value = read_json(TOKENIZER_FILE)
    tokenizer = TOK.ByteBPETokenizer.from_dict(value)
    if tokenizer.family != "byte_bpe_whitespace":
        raise RuntimeError("Unexpected tokenizer family")
    if tokenizer.vocab_size != VOCAB_SIZE:
        raise RuntimeError("Unexpected tokenizer vocabulary")
    return tokenizer


def encode_messages(tokenizer, messages: list[dict]) -> list[int]:
    text = CONV.serialize_messages(messages)
    ids = tokenizer.encode(
        text,
        add_bos=True,
        add_eos=True,
    )
    if not ids or ids[0] != BOS_ID or ids[-1] != EOS_ID:
        raise RuntimeError("Serialized segment lost BOS/EOS")
    if len(ids) > CONTEXT_LENGTH:
        raise RuntimeError("Encoded segment exceeds context")
    return ids


@dataclasses.dataclass(frozen=True)
class FrozenSegment:
    stream: str
    source_id: str
    segment_index: int
    token_ids: tuple[int, ...]

    @property
    def exposure_tokens(self) -> int:
        return len(self.token_ids)

    @property
    def predicted_tokens(self) -> int:
        return max(0, len(self.token_ids) - 1)


def _segment_messages(
    tokenizer,
    messages: list[dict],
) -> list[tuple[int, list[int]]]:
    def count_text(text: str) -> int:
        return len(tokenizer.encode(text))

    segments = SEG.segment_messages(
        messages,
        serialize_messages=CONV.serialize_messages,
        validate_messages=CONV.validate_messages,
        count_text=count_text,
        context_length=CONTEXT_LENGTH,
    )

    encoded = []
    for segment in segments:
        ids = encode_messages(
            tokenizer,
            list(segment.messages),
        )
        if len(ids) != segment.token_count:
            raise RuntimeError(
                "Tokenizer/segmentation token-count mismatch"
            )
        encoded.append((segment.segment_index, ids))
    return encoded


def _load_controlled_stream(
    tokenizer,
    freeze: dict,
) -> list[FrozenSegment]:
    expected_files = freeze.get("controlled_train", {}).get("files")
    if not isinstance(expected_files, list) or len(expected_files) != 19:
        raise RuntimeError("Frozen controlled TRAIN file inventory changed")

    expected_by_path = {
        item["path"]: item
        for item in expected_files
    }

    records = []
    ids = set()
    groups = set()

    for name in TRAIN_NAMES:
        path = TRAIN_DIR / name
        relative = str(path.relative_to(REPO))
        expected = expected_by_path.get(relative)
        if expected is None:
            raise RuntimeError(
                f"Controlled TRAIN file absent from freeze: {relative}"
            )
        if sha256_file(path) != expected.get("sha256"):
            raise RuntimeError(
                f"Controlled TRAIN file hash mismatch: {relative}"
            )
        rows = read_jsonl(path)
        if len(rows) != expected.get("records"):
            raise RuntimeError(
                f"Controlled TRAIN record count mismatch: {relative}"
            )
        for row in rows:
            if row.get("split") != "train":
                raise RuntimeError("Non-TRAIN row in controlled stream")
            rid = row.get("id")
            gid = row.get("group_id")
            if not isinstance(rid, str) or rid in ids:
                raise RuntimeError("Controlled TRAIN ID invariant failed")
            if not isinstance(gid, str):
                raise RuntimeError("Controlled TRAIN group invariant failed")
            ids.add(rid)
            groups.add(gid)
            records.append(row)

    if len(records) != 107 or len(ids) != 107 or len(groups) != 29:
        raise RuntimeError("Controlled TRAIN inventory changed")

    result = []
    for row in records:
        segments = _segment_messages(
            tokenizer,
            row["messages"],
        )
        for segment_index, token_ids in segments:
            result.append(
                FrozenSegment(
                    stream="CONTROLLED_TRAIN",
                    source_id=row["id"],
                    segment_index=segment_index,
                    token_ids=tuple(token_ids),
                )
            )

    expected_stream = freeze["training_streams"]["CONTROLLED_TRAIN"]
    if len(result) != expected_stream["segments"]:
        raise RuntimeError("Controlled segment count changed")
    if sum(x.exposure_tokens for x in result) != expected_stream["tokens"]:
        raise RuntimeError("Controlled token count changed")

    return result


def _load_public_pool() -> dict[str, dict]:
    if sha256_file(PUBLIC_POOL) != PUBLIC_POOL_SHA256:
        raise RuntimeError("Local SmolTalk v0.4 pool SHA-256 mismatch")

    rows = read_jsonl(PUBLIC_POOL)
    if len(rows) != 8000:
        raise RuntimeError("Local SmolTalk v0.4 pool size changed")

    by_sha = {}
    for row in rows:
        sha = row.get("content_sha256")
        messages = row.get("messages")
        if not isinstance(sha, str) or len(sha) != 64:
            raise RuntimeError("Invalid public pool content SHA")
        if sha in by_sha:
            raise RuntimeError("Duplicate public pool content SHA")
        CONV.validate_messages(messages)
        by_sha[sha] = row

    return by_sha


def _load_public_streams(
    tokenizer,
    freeze: dict,
) -> dict[str, list[FrozenSegment]]:
    pool = _load_public_pool()
    public = freeze.get("public_direct_keep")
    if not isinstance(public, dict):
        raise RuntimeError("Missing frozen public DIRECT_KEEP")

    streams = {}
    for stream in (
        "PERSONA_CORE",
        "GENERAL_SUPPORT",
        "LEGACY_STRUCTURED_KEEP",
    ):
        frozen = public["streams"].get(stream)
        if not isinstance(frozen, dict):
            raise RuntimeError(f"Missing frozen stream: {stream}")
        shas = frozen.get("source_shas")
        if not isinstance(shas, list):
            raise RuntimeError(f"Missing source SHAs for {stream}")
        if len(shas) != frozen.get("conversations"):
            raise RuntimeError(
                f"Conversation count mismatch in frozen stream: {stream}"
            )
        if len(set(shas)) != len(shas):
            raise RuntimeError(
                f"Duplicate public source SHA in frozen stream: {stream}"
            )

        segments = []
        for sha in shas:
            row = pool.get(sha)
            if row is None:
                raise RuntimeError(
                    f"Frozen public source absent from local pool: {sha}"
                )
            for segment_index, token_ids in _segment_messages(
                tokenizer,
                row["messages"],
            ):
                segments.append(
                    FrozenSegment(
                        stream=stream,
                        source_id=sha,
                        segment_index=segment_index,
                        token_ids=tuple(token_ids),
                    )
                )

        if len(segments) != frozen.get("segments"):
            raise RuntimeError(
                f"Public segment count changed for {stream}"
            )
        if (
            sum(x.exposure_tokens for x in segments)
            != frozen.get("tokens")
        ):
            raise RuntimeError(
                f"Public token count changed for {stream}"
            )

        streams[stream] = segments

    all_shas = [
        x
        for stream in public["streams"].values()
        for x in stream["source_shas"]
    ]
    if len(all_shas) != 165 or len(set(all_shas)) != 165:
        raise RuntimeError("Frozen public DIRECT_KEEP identity changed")

    if sum(len(v) for v in streams.values()) != 238:
        raise RuntimeError("Frozen public segment total changed")
    if (
        sum(
            x.exposure_tokens
            for values in streams.values()
            for x in values
        )
        != 270877
    ):
        raise RuntimeError("Frozen public token total changed")

    return streams


def build_training_streams() -> tuple[dict[str, list[FrozenSegment]], dict]:
    _, freeze, _ = verify_authorization()
    tokenizer = load_tokenizer()

    streams = {
        "CONTROLLED_TRAIN":
            _load_controlled_stream(tokenizer, freeze)
    }
    streams.update(
        _load_public_streams(tokenizer, freeze)
    )

    if tuple(streams.keys()) != STREAMS:
        raise RuntimeError("Training stream order changed")
    if sum(len(v) for v in streams.values()) != 345:
        raise RuntimeError("Final training segment total changed")
    if (
        sum(
            segment.exposure_tokens
            for values in streams.values()
            for segment in values
        )
        != 295416
    ):
        raise RuntimeError("Final unique training-token total changed")

    inventory = {
        stream: {
            "segments": len(values),
            "tokens": sum(x.exposure_tokens for x in values),
        }
        for stream, values in streams.items()
    }
    return streams, inventory


def _validation_declarations() -> list[Path]:
    paths = sorted(
        VALIDATION_MANIFEST_DIR.glob(
            "validation-batch-*-freeze-declaration.json"
        )
    )
    if len(paths) != 18:
        raise RuntimeError(
            "Expected exactly 18 validation freeze declarations"
        )
    return paths


def build_validation_segments() -> tuple[list[FrozenSegment], dict]:
    master = read_json(VALIDATION_MASTER)
    tokenizer = load_tokenizer()

    if master.get("status") != "CLOSED":
        raise RuntimeError("VALIDATION master is not closed")
    if master.get("target_records") != 36:
        raise RuntimeError("VALIDATION target record count changed")
    if master.get("total_behaviors") != 18:
        raise RuntimeError("VALIDATION behavior count changed")
    if master.get("semantic_validation_complete") is not True:
        raise RuntimeError("Semantic validation is not complete")

    master_by_behavior = {
        item["behavior"]: item
        for item in master["behaviors"]
    }
    if len(master_by_behavior) != 18:
        raise RuntimeError("VALIDATION master behavior inventory changed")

    records = []
    file_inventory = []
    seen_behaviors = set()
    seen_ids = set()

    for declaration_path in _validation_declarations():
        declaration = read_json(declaration_path)
        behavior = declaration.get("behavior")
        if behavior in seen_behaviors:
            raise RuntimeError(
                f"Duplicate VALIDATION freeze declaration: {behavior}"
            )
        seen_behaviors.add(behavior)

        expected = master_by_behavior.get(behavior)
        if expected is None:
            raise RuntimeError(
                f"VALIDATION declaration absent from master: {behavior}"
            )

        if declaration.get("records") != 2:
            raise RuntimeError(
                f"VALIDATION freeze record count changed: {behavior}"
            )
        if declaration.get("group_id") != expected["group_id"]:
            raise RuntimeError(
                f"VALIDATION group changed: {behavior}"
            )
        if "independent_review_complete" in declaration:
            review_complete = declaration.get("independent_review_complete")
        else:
            review_complete = declaration.get("review_complete")
        if review_complete is not True:
            raise RuntimeError(
                f"VALIDATION independent review incomplete: {behavior}"
            )
        if declaration.get("semantic_guard_pass") is not True:
            raise RuntimeError(
                f"VALIDATION semantic guard failed: {behavior}"
            )
        integrity_flag = declaration.get("structural_integrity_audit_passed")
        if integrity_flag is not True:
            if integrity_flag is not None:
                raise RuntimeError(
                    f"VALIDATION integrity audit failed: {behavior}"
                )
            # V54 B02-B18 predate the declaration-level integrity flag.
            # Require their independently published, immutable GOGIT freeze
            # evidence rather than treating a missing flag as success.
            step_id = declaration.get("target_step_id")
            expected_step = (
                f"PHASE03-SMOLTALK-V54-{behavior}-VALIDATION-FREEZE-001"
            )
            if step_id != expected_step:
                raise RuntimeError(
                    f"VALIDATION freeze step mismatch: {behavior}"
                )
            history = read_json(
                REPO / "reports" / "assistant-results" / "history"
                / f"{step_id}.json"
            )
            metrics = history.get("metrics", {})
            batch_number = int(behavior[1:])
            if (
                history.get("step_id") != step_id
                or metrics.get(
                    f"{behavior}_VALIDATION_FROZEN",
                    metrics.get("VALIDATION_BATCH_FROZEN"),
                ) != 1
                or metrics.get(
                    f"{behavior}_INDEPENDENT_SIGNOFF",
                    metrics.get("VALIDATION_BATCH_SIGNOFF"),
                ) != 1
                or metrics.get("CROSS_SPLIT_ID_COLLISIONS") != 0
                or metrics.get("CROSS_SPLIT_GROUP_COLLISIONS") != 0
                or metrics.get("EXACT_USER_PROMPT_MATCHES") != 0
                or metrics.get("VALIDATION_BEHAVIORS_FROZEN")
                    != batch_number
                or metrics.get("VALIDATION_FROZEN_RECORDS")
                    != 2 * batch_number
            ):
                raise RuntimeError(
                    f"VALIDATION historical freeze proof failed: {behavior}"
                )

        target = REPO / declaration["target_batch"]
        if target.parent != VALIDATION_DIR:
            raise RuntimeError(
                f"Unsafe VALIDATION target path: {target}"
            )
        if git_blob_sha(target) != declaration.get("target_batch_blob_sha"):
            raise RuntimeError(
                f"VALIDATION Git blob changed: {behavior}"
            )

        rows = read_jsonl(target)
        if len(rows) != 2:
            raise RuntimeError(
                f"VALIDATION target file count changed: {behavior}"
            )
        for row in rows:
            if row.get("split") != "validation":
                raise RuntimeError("Non-VALIDATION row in validation corpus")
            if row.get("group_id") != expected["group_id"]:
                raise RuntimeError(
                    f"VALIDATION row group mismatch: {behavior}"
                )
            rid = row.get("id")
            if not isinstance(rid, str) or rid in seen_ids:
                raise RuntimeError("VALIDATION ID invariant failed")
            seen_ids.add(rid)
            records.append(row)

        file_inventory.append(
            {
                "behavior": behavior,
                "path": str(target.relative_to(REPO)),
                "sha256": sha256_file(target),
                "git_blob_sha": git_blob_sha(target),
                "records": len(rows),
            }
        )

    if seen_behaviors != set(master_by_behavior):
        raise RuntimeError("VALIDATION behavior coverage changed")
    if len(records) != 36 or len(seen_ids) != 36:
        raise RuntimeError("VALIDATION record inventory changed")

    segments = []
    for row in records:
        for segment_index, token_ids in _segment_messages(
            tokenizer,
            row["messages"],
        ):
            segments.append(
                FrozenSegment(
                    stream="VALIDATION",
                    source_id=row["id"],
                    segment_index=segment_index,
                    token_ids=tuple(token_ids),
                )
            )

    inventory = {
        "records": len(records),
        "segments": len(segments),
        "tokens": sum(x.exposure_tokens for x in segments),
        "files": sorted(
            file_inventory,
            key=lambda item: item["behavior"],
        ),
        "record_ids_sha256": canonical_sha(
            sorted(seen_ids)
        ),
    }
    return segments, inventory


class StreamQuotaSampler:
    """Deterministic stream sampler with replacement and token quotas."""

    def __init__(
        self,
        streams: dict[str, list[FrozenSegment]],
        target_share_bp: dict[str, int],
        reference_cycle_tokens: int,
        seed: int,
    ):
        if tuple(streams.keys()) != STREAMS:
            raise ValueError("Sampler stream order changed")
        if sum(target_share_bp.values()) != 10000:
            raise ValueError("Sampler target shares do not close to 10000 bp")
        if reference_cycle_tokens <= 0:
            raise ValueError("Invalid reference cycle token budget")

        self.streams = streams
        self.target_share_bp = dict(target_share_bp)
        self.reference_cycle_tokens = int(reference_cycle_tokens)
        self.seed = int(seed)

        self._rngs = {}
        self._orders = {}
        self._cursors = {}
        for index, stream in enumerate(STREAMS):
            rng = random.Random(self.seed + 1009 * (index + 1))
            order = list(range(len(streams[stream])))
            rng.shuffle(order)
            self._rngs[stream] = rng
            self._orders[stream] = order
            self._cursors[stream] = 0

        self._mix_rng = random.Random(self.seed + 7919)
        self.completed_cycles = 0
        self._segment_by_key = {
            stream: {
                (segment.source_id, segment.segment_index): segment
                for segment in streams[stream]
            }
            for stream in STREAMS
        }
        self._pending: list[FrozenSegment] = []

    def _next_from_stream(self, stream: str) -> FrozenSegment:
        order = self._orders[stream]
        cursor = self._cursors[stream]

        if cursor >= len(order):
            self._rngs[stream].shuffle(order)
            cursor = 0

        index = order[cursor]
        self._cursors[stream] = cursor + 1
        return self.streams[stream][index]

    def cycle_quotas(self) -> dict[str, int]:
        quotas = {}
        allocated = 0
        for stream in (
            "CONTROLLED_TRAIN",
            "GENERAL_SUPPORT",
            "LEGACY_STRUCTURED_KEEP",
        ):
            value = (
                self.reference_cycle_tokens
                * self.target_share_bp[stream]
            ) // 10000
            quotas[stream] = value
            allocated += value

        quotas["PERSONA_CORE"] = (
            self.reference_cycle_tokens
            - allocated
        )
        return quotas

    def next_cycle(self) -> list[FrozenSegment]:
        quotas = self.cycle_quotas()
        selected = []

        for stream in STREAMS:
            exposed = 0
            while exposed < quotas[stream]:
                segment = self._next_from_stream(stream)
                selected.append(segment)
                exposed += segment.exposure_tokens

        self._mix_rng.shuffle(selected)
        self.completed_cycles += 1
        return selected

    def next_segment(
        self,
        reference_cycles: int,
    ) -> FrozenSegment | None:
        if not self._pending:
            if self.completed_cycles >= reference_cycles:
                return None
            self._pending = self.next_cycle()

        return self._pending.pop(0)

    def state_dict(self) -> dict:
        return {
            "seed": self.seed,
            "target_share_bp": dict(self.target_share_bp),
            "reference_cycle_tokens": self.reference_cycle_tokens,
            "orders": {
                stream: list(self._orders[stream])
                for stream in STREAMS
            },
            "cursors": dict(self._cursors),
            "rng_states": {
                stream: self._rngs[stream].getstate()
                for stream in STREAMS
            },
            "mix_rng_state": self._mix_rng.getstate(),
            "completed_cycles": self.completed_cycles,
            "pending": [
                {
                    "stream": segment.stream,
                    "source_id": segment.source_id,
                    "segment_index": segment.segment_index,
                }
                for segment in self._pending
            ],
        }

    def load_state_dict(self, state: dict) -> None:
        if state.get("seed") != self.seed:
            raise RuntimeError("Sampler resume seed mismatch")
        if state.get("target_share_bp") != self.target_share_bp:
            raise RuntimeError("Sampler resume target-share mismatch")
        if (
            state.get("reference_cycle_tokens")
            != self.reference_cycle_tokens
        ):
            raise RuntimeError("Sampler resume cycle-token mismatch")

        for stream in STREAMS:
            order = state["orders"][stream]
            if sorted(order) != list(range(len(self.streams[stream]))):
                raise RuntimeError(
                    f"Sampler resume order mismatch: {stream}"
                )
            self._orders[stream] = list(order)
            self._cursors[stream] = int(
                state["cursors"][stream]
            )
            self._rngs[stream].setstate(
                state["rng_states"][stream]
            )

        self._mix_rng.setstate(state["mix_rng_state"])
        self.completed_cycles = int(state["completed_cycles"])

        pending = []
        for item in state.get("pending", []):
            stream = item["stream"]
            key = (
                item["source_id"],
                int(item["segment_index"]),
            )
            segment = self._segment_by_key.get(stream, {}).get(key)
            if segment is None:
                raise RuntimeError(
                    "Sampler resume pending-segment mismatch"
                )
            pending.append(segment)
        self._pending = pending


@dataclasses.dataclass
class FrozenLRSchedule:
    base_lr: float
    min_lr: float
    warmup_steps: int
    max_steps: int
    current_step: int = 0

    def lr_for_step(self, step: int) -> float:
        if not 1 <= step <= self.max_steps:
            raise ValueError("Scheduler step outside frozen budget")

        if step <= self.warmup_steps:
            return self.base_lr * step / self.warmup_steps

        span = max(1, self.max_steps - self.warmup_steps)
        progress = (
            step - self.warmup_steps
        ) / span
        progress = min(1.0, max(0.0, progress))
        cosine = 0.5 * (
            1.0 + math.cos(math.pi * progress)
        )
        return (
            self.min_lr
            + (self.base_lr - self.min_lr) * cosine
        )

    def state_dict(self) -> dict:
        return dataclasses.asdict(self)

    def load_state_dict(self, state: dict) -> None:
        for key in (
            "base_lr",
            "min_lr",
            "warmup_steps",
            "max_steps",
        ):
            if state.get(key) != getattr(self, key):
                raise RuntimeError(
                    f"Scheduler resume mismatch: {key}"
                )
        self.current_step = int(state["current_step"])


def pad_batch(
    segments: list[FrozenSegment],
    device: torch.device,
) -> tuple[torch.Tensor, int, int]:
    if not segments:
        raise ValueError("Cannot pad empty segment batch")
    if len(segments) > 8:
        raise ValueError("Microbatch exceeds frozen size 8")

    max_length = max(
        segment.exposure_tokens
        for segment in segments
    )
    if max_length > CONTEXT_LENGTH:
        raise RuntimeError("Microbatch contains over-context segment")

    batch = torch.full(
        (len(segments), max_length),
        PAD_ID,
        dtype=torch.long,
        device=device,
    )

    exposure_tokens = 0
    predicted_tokens = 0
    for row, segment in enumerate(segments):
        ids = torch.tensor(
            segment.token_ids,
            dtype=torch.long,
            device=device,
        )
        batch[row, : ids.numel()] = ids
        exposure_tokens += ids.numel()
        predicted_tokens += max(0, ids.numel() - 1)

    return batch, exposure_tokens, predicted_tokens


def _step_segment_groups(
    iterator: Iterator[FrozenSegment],
    target_tokens: int,
    max_total_tokens: int,
    current_total_tokens: int,
) -> tuple[list[FrozenSegment], int, bool]:
    selected = []
    exposed = 0
    hit_global_limit = False

    while exposed < target_tokens:
        try:
            segment = next(iterator)
        except StopIteration:
            break

        if (
            current_total_tokens
            + exposed
            + segment.exposure_tokens
            > max_total_tokens
        ):
            hit_global_limit = True
            break

        selected.append(segment)
        exposed += segment.exposure_tokens

    return selected, exposed, hit_global_limit


def _iter_cycles(
    sampler: StreamQuotaSampler,
    reference_cycles: int,
) -> Iterator[FrozenSegment]:
    while True:
        segment = sampler.next_segment(reference_cycles)
        if segment is None:
            break
        yield segment


def build_schedule_preview(
    streams: dict[str, list[FrozenSegment]],
    protocol: dict,
) -> dict:
    exposure = protocol["exposure"]
    sampler = StreamQuotaSampler(
        streams=streams,
        target_share_bp=exposure["target_share_bp"],
        reference_cycle_tokens=exposure["reference_cycle_tokens"],
        seed=protocol["seed"],
    )

    totals = {stream: 0 for stream in STREAMS}
    total = 0
    segments = 0
    iterator = _iter_cycles(
        sampler,
        exposure["reference_cycles"],
    )

    for segment in iterator:
        if (
            total + segment.exposure_tokens
            > exposure["max_exposure_tokens"]
        ):
            break
        totals[segment.stream] += segment.exposure_tokens
        total += segment.exposure_tokens
        segments += 1

    shares_bp = {
        stream: (
            round(totals[stream] * 10000 / total)
            if total
            else 0
        )
        for stream in STREAMS
    }
    deviation_bp = {
        stream: (
            shares_bp[stream]
            - exposure["target_share_bp"][stream]
        )
        for stream in STREAMS
    }

    tolerance = exposure["stream_share_tolerance_bp"]
    if any(
        abs(value) > tolerance
        for value in deviation_bp.values()
    ):
        raise RuntimeError(
            "Deterministic sampler preview exceeds frozen stream-share tolerance"
        )

    return {
        "segments": segments,
        "exposure_tokens": total,
        "stream_tokens": totals,
        "stream_share_bp": shares_bp,
        "stream_deviation_bp": deviation_bp,
        "completed_sampler_cycles": sampler.completed_cycles,
    }


def load_protocol() -> dict:
    path = (
        REPO
        / "reviews"
        / "smoltalk-v59-training-protocol"
        / "PROTOCOL-001.json"
    )
    protocol = read_json(path)

    if protocol.get("architecture") != "V58_MICRO_FROZEN":
        raise RuntimeError("Unexpected training architecture")
    if protocol.get("dtype") != "BF16":
        raise RuntimeError("Unexpected training dtype")
    if protocol.get("parameters") != MODEL_PARAMETERS:
        raise RuntimeError("Unexpected model parameter count")
    if protocol.get("context_length") != CONTEXT_LENGTH:
        raise RuntimeError("Unexpected context length")
    if protocol.get("pilot_only") is not True:
        raise RuntimeError("Persistent trainer is pilot-only")
    if protocol.get("blind_test_reserved") is not True:
        raise RuntimeError("BLIND TEST reservation changed")
    if (
        protocol["evaluation"].get("blind_test_during_training")
        is not False
    ):
        raise RuntimeError("BLIND TEST access during training is forbidden")

    if protocol["batching"].get("microbatch_sequences") != 8:
        raise RuntimeError("Frozen microbatch size changed")
    if (
        protocol["batching"].get(
            "optimizer_step_target_nonpad_tokens"
        )
        != 8192
    ):
        raise RuntimeError("Frozen optimizer token target changed")
    if protocol["exposure"].get("max_optimizer_steps") != 145:
        raise RuntimeError("Frozen optimizer-step budget changed")
    if protocol["exposure"].get("max_exposure_tokens") != 1181664:
        raise RuntimeError("Frozen exposure-token budget changed")

    return protocol


def _validation_loss(
    model,
    validation_segments: list[FrozenSegment],
    device: torch.device,
) -> float:
    model.eval()
    total_loss = 0.0
    total_tokens = 0

    with torch.no_grad():
        for start in range(0, len(validation_segments), 8):
            batch_segments = validation_segments[start:start + 8]
            token_ids, _, predicted = pad_batch(
                batch_segments,
                device,
            )
            if predicted <= 0:
                continue

            with torch.autocast(
                device_type="cuda",
                dtype=torch.bfloat16,
            ):
                logits = model(token_ids)
                targets = token_ids[:, 1:]
                loss_sum = F.cross_entropy(
                    logits[:, :-1, :].reshape(-1, VOCAB_SIZE),
                    targets.reshape(-1),
                    ignore_index=PAD_ID,
                    reduction="sum",
                )

            total_loss += float(loss_sum.detach().cpu())
            total_tokens += int(
                (targets != PAD_ID).sum().item()
            )

    model.train()

    if total_tokens <= 0:
        raise RuntimeError("VALIDATION produced zero predicted tokens")
    return total_loss / total_tokens


def _fixed_probe_segments(
    validation_segments: list[FrozenSegment],
) -> list[FrozenSegment]:
    preferred = (
        "p03-val-b01-000001",
        "p03-val-b05-000001",
        "p03-val-b09-000001",
        "p03-val-b13-000001",
        "p03-val-b16-000001",
        "p03-val-b18-000001",
    )
    by_id = {}
    for segment in validation_segments:
        if segment.segment_index == 0:
            by_id.setdefault(segment.source_id, segment)
    result = [
        by_id[source_id]
        for source_id in preferred
        if source_id in by_id
    ]
    if len(result) != len(preferred):
        raise RuntimeError("Fixed validation probe inventory changed")
    return result


def _decode_generated_probe_text(
    tokenizer,
    token_ids: Iterable[int],
) -> tuple[str, bool]:
    ids = [int(token_id) for token_id in token_ids]
    try:
        return tokenizer.decode(ids), True
    except UnicodeDecodeError:
        # A byte-level model can emit incomplete or invalid UTF-8 while it is
        # still untrained. This is diagnostic output only and must not abort
        # the bounded pilot. Source and target decoding remains strict.
        token_bytes = getattr(tokenizer, "_token_bytes", None)
        if not isinstance(token_bytes, dict):
            raise
        payload = bytearray()
        for token_id in ids:
            if token_id in {PAD_ID, BOS_ID, EOS_ID}:
                continue
            value = token_bytes.get(token_id)
            if value is None:
                raise ValueError(
                    f"Unknown generated token id: {token_id}"
                )
            payload.extend(value)
        return (
            bytes(payload).decode("utf-8", errors="replace"),
            False,
        )


def _greedy_probe(
    model,
    tokenizer,
    segment: FrozenSegment,
    device: torch.device,
    max_new_tokens: int = 96,
) -> dict:
    # The probe uses only the first serialized USER turn as a prompt.
    # It never uses the frozen assistant target for generation input.
    # Retrieve source text by validation ID through the already-loaded
    # validation corpus would complicate the segment representation, so
    # reconstruct from the token sequence by locating the first assistant
    # header in decoded text.
    serialized = tokenizer.decode(segment.token_ids)
    marker = "\n\nMINI-KUZAI:\n"
    position = serialized.find(marker)
    if position < 0:
        raise RuntimeError("Validation probe lacks assistant header")
    prompt_text = serialized[: position + len(marker)]

    ids = tokenizer.encode(
        prompt_text,
        add_bos=True,
        add_eos=False,
    )
    if len(ids) >= CONTEXT_LENGTH:
        raise RuntimeError("Validation probe prompt fills context")

    generated = list(ids)
    model.eval()
    with torch.no_grad():
        for _ in range(max_new_tokens):
            input_ids = torch.tensor(
                [generated],
                dtype=torch.long,
                device=device,
            )
            with torch.autocast(
                device_type="cuda",
                dtype=torch.bfloat16,
            ):
                logits = model(input_ids)
            next_id = int(
                torch.argmax(logits[0, -1]).item()
            )
            generated.append(next_id)
            if next_id == EOS_ID:
                break
            if len(generated) >= CONTEXT_LENGTH:
                break
    model.train()

    new_ids = generated[len(ids):]
    generated_text, generated_utf8_valid = (
        _decode_generated_probe_text(tokenizer, new_ids)
    )

    return {
        "source_id": segment.source_id,
        "prompt": prompt_text,
        "generated_text": generated_text,
        "generated_tokens": len(new_ids),
        "generated_utf8_valid": generated_utf8_valid,
        "ended_with_eos": bool(new_ids and new_ids[-1] == EOS_ID),
    }


def _write_json_atomic(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _append_jsonl(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps(
                value,
                sort_keys=True,
                ensure_ascii=True,
            )
            + "\n"
        )
        stream.flush()
        os.fsync(stream.fileno())


def _checkpoint_payload(
    *,
    model,
    optimizer,
    schedule: FrozenLRSchedule,
    sampler: StreamQuotaSampler,
    protocol: dict,
    authorization: dict,
    trainer_freeze: dict,
    step: int,
    exposure_tokens: int,
    best_validation_loss: float,
    evaluations: list[dict],
    consecutive_degraded: int,
    stream_exposure_tokens: dict[str, int],
) -> dict:
    return {
        "schema_version": "v59-pilot-checkpoint-1",
        "authorization_freeze_fingerprint":
            authorization["freeze_fingerprint"],
        "trainer_freeze_fingerprint":
            trainer_freeze["trainer_freeze_fingerprint"],
        "protocol_sha256": sha256_file(
            REPO
            / "reviews"
            / "smoltalk-v59-training-protocol"
            / "PROTOCOL-001.json"
        ),
        "step": step,
        "exposure_tokens": exposure_tokens,
        "best_validation_loss": best_validation_loss,
        "evaluations": evaluations,
        "consecutive_degraded": consecutive_degraded,
        "stream_exposure_tokens": dict(stream_exposure_tokens),
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "scheduler": schedule.state_dict(),
        "sampler": sampler.state_dict(),
        "torch_rng_state": torch.get_rng_state(),
        "cuda_rng_state_all": torch.cuda.get_rng_state_all(),
        "python_random_state": random.getstate(),
        "protocol": protocol,
    }


def _save_checkpoint(
    path: Path,
    payload: dict,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, temporary)
    temporary.replace(path)


def _load_checkpoint(
    path: Path,
    *,
    model,
    optimizer,
    schedule: FrozenLRSchedule,
    sampler: StreamQuotaSampler,
    authorization: dict,
    trainer_freeze: dict,
) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Unsafe or missing checkpoint: {path}")

    value = torch.load(
        path,
        map_location="cpu",
        weights_only=False,
    )
    if not isinstance(value, dict):
        raise RuntimeError("Invalid checkpoint payload")
    if (
        value.get("authorization_freeze_fingerprint")
        != authorization["freeze_fingerprint"]
    ):
        raise RuntimeError("Checkpoint authorization fingerprint mismatch")
    if (
        value.get("trainer_freeze_fingerprint")
        != trainer_freeze["trainer_freeze_fingerprint"]
    ):
        raise RuntimeError("Checkpoint trainer fingerprint mismatch")

    model.load_state_dict(value["model"])
    optimizer.load_state_dict(value["optimizer"])
    schedule.load_state_dict(value["scheduler"])
    sampler.load_state_dict(value["sampler"])
    torch.set_rng_state(value["torch_rng_state"])
    torch.cuda.set_rng_state_all(value["cuda_rng_state_all"])
    random.setstate(value["python_random_state"])

    return value


def verify_runtime(
    trainer_source: Path,
    cli_source: Path,
) -> dict:
    authorization, freeze, _ = verify_authorization()
    trainer_freeze = verify_trainer_freeze(
        trainer_source,
        cli_source,
    )
    protocol = load_protocol()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the authorized V59 pilot")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("BF16 is required for the authorized V59 pilot")

    streams, training_inventory = build_training_streams()
    validation_segments, validation_inventory = build_validation_segments()
    preview = build_schedule_preview(streams, protocol)

    if trainer_freeze.get("training_inventory") != training_inventory:
        raise RuntimeError("Training inventory differs from trainer freeze")
    if trainer_freeze.get("validation_inventory") != validation_inventory:
        raise RuntimeError("VALIDATION inventory differs from trainer freeze")
    if trainer_freeze.get("schedule_preview") != preview:
        raise RuntimeError("Sampler preview differs from trainer freeze")

    if freeze["total_training_conversations"] != 272:
        raise RuntimeError("Authorization freeze changed unexpectedly")

    return {
        "authorization": authorization,
        "trainer_freeze": trainer_freeze,
        "protocol": protocol,
        "training_inventory": training_inventory,
        "validation_inventory": validation_inventory,
        "schedule_preview": preview,
        "gpu": torch.cuda.get_device_name(0),
    }


def train(
    *,
    run_dir: Path,
    trainer_source: Path,
    cli_source: Path,
    resume: bool = False,
) -> dict:
    runtime = verify_runtime(
        trainer_source,
        cli_source,
    )
    authorization = runtime["authorization"]
    trainer_freeze = runtime["trainer_freeze"]
    protocol = runtime["protocol"]

    if not run_dir.is_absolute():
        raise RuntimeError("Run directory must be absolute")
    if run_dir.is_symlink():
        raise RuntimeError("Run directory cannot be a symlink")

    run_dir.mkdir(parents=True, exist_ok=True)
    lock = run_dir / ".training.lock"
    try:
        descriptor = os.open(
            lock,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
    except FileExistsError as exc:
        raise RuntimeError(
            f"Training lock already exists: {lock}"
        ) from exc

    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(str(os.getpid()) + "\n")
            stream.flush()

        run_manifest = run_dir / "RUN-MANIFEST.json"
        if run_manifest.exists() and not resume:
            raise RuntimeError(
                "Run directory already contains a run manifest; use --resume"
            )
        if resume and not run_manifest.is_file():
            raise RuntimeError(
                "Cannot resume: run manifest is missing"
            )

        torch.manual_seed(protocol["seed"])
        torch.cuda.manual_seed_all(protocol["seed"])
        random.seed(protocol["seed"])

        device = torch.device("cuda")
        model = MODEL.MiniKuzaiPhase03(
            MODEL.Phase03Config()
        ).to(device)

        if MODEL.count_parameters(model) != MODEL_PARAMETERS:
            raise RuntimeError("Model parameter count changed")

        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=protocol["optimizer"]["learning_rate"],
            betas=tuple(protocol["optimizer"]["betas"]),
            eps=protocol["optimizer"]["eps"],
            weight_decay=protocol["optimizer"]["weight_decay"],
        )

        schedule = FrozenLRSchedule(
            base_lr=protocol["optimizer"]["learning_rate"],
            min_lr=protocol["scheduler"]["min_learning_rate"],
            warmup_steps=protocol["scheduler"]["warmup_steps"],
            max_steps=protocol["scheduler"]["max_steps"],
        )

        streams, _ = build_training_streams()
        validation_segments, _ = build_validation_segments()
        tokenizer = load_tokenizer()

        sampler = StreamQuotaSampler(
            streams=streams,
            target_share_bp=protocol["exposure"]["target_share_bp"],
            reference_cycle_tokens=
                protocol["exposure"]["reference_cycle_tokens"],
            seed=protocol["seed"],
        )

        step = 0
        exposure_tokens = 0
        best_validation_loss = float("inf")
        evaluations = []
        consecutive_degraded = 0
        stream_exposure_tokens = {
            stream: 0
            for stream in STREAMS
        }

        last_checkpoint = run_dir / "checkpoint-last.pt"
        best_checkpoint = run_dir / "checkpoint-best.pt"

        if resume:
            state = _load_checkpoint(
                last_checkpoint,
                model=model,
                optimizer=optimizer,
                schedule=schedule,
                sampler=sampler,
                authorization=authorization,
                trainer_freeze=trainer_freeze,
            )
            step = int(state["step"])
            exposure_tokens = int(state["exposure_tokens"])
            best_validation_loss = float(
                state["best_validation_loss"]
            )
            evaluations = list(state["evaluations"])
            consecutive_degraded = int(
                state["consecutive_degraded"]
            )
            restored_stream_tokens = state.get(
                "stream_exposure_tokens"
            )
            if (
                not isinstance(restored_stream_tokens, dict)
                or set(restored_stream_tokens) != set(STREAMS)
            ):
                raise RuntimeError(
                    "Checkpoint stream-exposure state is invalid"
                )
            stream_exposure_tokens = {
                stream: int(restored_stream_tokens[stream])
                for stream in STREAMS
            }

        manifest = {
            "schema_version": "v59-pilot-run-1",
            "status": "RUNNING",
            "authorization_scope":
                authorization["authorization_scope"],
            "authorization_freeze_fingerprint":
                authorization["freeze_fingerprint"],
            "trainer_freeze_fingerprint":
                trainer_freeze["trainer_freeze_fingerprint"],
            "started_unix": int(time.time()),
            "resume": bool(resume),
            "run_dir": str(run_dir),
            "gpu": torch.cuda.get_device_name(0),
            "max_optimizer_steps":
                protocol["exposure"]["max_optimizer_steps"],
            "max_exposure_tokens":
                protocol["exposure"]["max_exposure_tokens"],
            "blind_test_during_training": False,
        }
        _write_json_atomic(run_manifest, manifest)

        metrics_path = run_dir / "metrics.jsonl"
        probes_path = run_dir / "validation-probes.jsonl"

        if not resume:
            initial_validation = _validation_loss(
                model,
                validation_segments,
                device,
            )
            best_validation_loss = initial_validation
            initial_record = {
                "type": "validation",
                "step": 0,
                "exposure_tokens": 0,
                "validation_loss": initial_validation,
            }
            evaluations.append(initial_record)
            _append_jsonl(metrics_path, initial_record)

            initial_payload = _checkpoint_payload(
                model=model,
                optimizer=optimizer,
                schedule=schedule,
                sampler=sampler,
                protocol=protocol,
                authorization=authorization,
                trainer_freeze=trainer_freeze,
                step=0,
                exposure_tokens=0,
                best_validation_loss=best_validation_loss,
                evaluations=evaluations,
                consecutive_degraded=0,
                stream_exposure_tokens=stream_exposure_tokens,
            )
            _save_checkpoint(
                best_checkpoint,
                initial_payload,
            )
            _save_checkpoint(
                last_checkpoint,
                initial_payload,
            )

            for probe in _fixed_probe_segments(
                validation_segments
            ):
                probe_result = _greedy_probe(
                    model,
                    tokenizer,
                    probe,
                    device,
                )
                probe_result.update(
                    {
                        "type": "generation_probe",
                        "step": 0,
                        "exposure_tokens": 0,
                    }
                )
                _append_jsonl(
                    probes_path,
                    probe_result,
                )

        next_eval = (
            (exposure_tokens // protocol["evaluation"][
                "validation_every_exposure_tokens"
            ]) + 1
        ) * protocol["evaluation"][
            "validation_every_exposure_tokens"
        ]

        segment_iterator = _iter_cycles(
            sampler,
            protocol["exposure"]["reference_cycles"],
        )

        stop_reason = None
        model.train()

        while (
            step < protocol["exposure"]["max_optimizer_steps"]
            and exposure_tokens
            < protocol["exposure"]["max_exposure_tokens"]
        ):
            selected, step_exposure, hit_limit = _step_segment_groups(
                segment_iterator,
                protocol["batching"][
                    "optimizer_step_target_nonpad_tokens"
                ],
                protocol["exposure"]["max_exposure_tokens"],
                exposure_tokens,
            )

            if not selected:
                stop_reason = (
                    "MAX_EXPOSURE_TOKENS"
                    if hit_limit
                    else "SAMPLER_EXHAUSTED"
                )
                break

            step += 1
            schedule.current_step = step
            learning_rate = schedule.lr_for_step(step)
            for group in optimizer.param_groups:
                group["lr"] = learning_rate

            total_predicted = sum(
                segment.predicted_tokens
                for segment in selected
            )
            if total_predicted <= 0:
                raise RuntimeError(
                    "Optimizer step has zero predicted tokens"
                )

            optimizer.zero_grad(set_to_none=True)
            step_loss_sum = 0.0

            for start in range(0, len(selected), 8):
                micro = selected[start:start + 8]
                token_ids, _, _ = pad_batch(
                    micro,
                    device,
                )

                with torch.autocast(
                    device_type="cuda",
                    dtype=torch.bfloat16,
                ):
                    logits = model(token_ids)
                    targets = token_ids[:, 1:]
                    loss_sum = F.cross_entropy(
                        logits[:, :-1, :].reshape(
                            -1,
                            VOCAB_SIZE,
                        ),
                        targets.reshape(-1),
                        ignore_index=PAD_ID,
                        reduction="sum",
                    )
                    scaled_loss = (
                        loss_sum / total_predicted
                    )

                if not torch.isfinite(loss_sum):
                    stop_reason = "NONFINITE_LOSS"
                    break

                scaled_loss.backward()
                step_loss_sum += float(
                    loss_sum.detach().cpu()
                )

            if stop_reason == "NONFINITE_LOSS":
                optimizer.zero_grad(set_to_none=True)
                break

            gradient_norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                protocol["gradient_clip_norm"],
            )
            if not torch.isfinite(
                torch.as_tensor(gradient_norm)
            ):
                optimizer.zero_grad(set_to_none=True)
                stop_reason = "NONFINITE_GRADIENT_NORM"
                break

            optimizer.step()
            exposure_tokens += step_exposure
            for segment in selected:
                stream_exposure_tokens[segment.stream] += (
                    segment.exposure_tokens
                )

            step_record = {
                "type": "train_step",
                "step": step,
                "exposure_tokens": exposure_tokens,
                "step_exposure_tokens": step_exposure,
                "predicted_tokens": total_predicted,
                "train_loss": step_loss_sum / total_predicted,
                "learning_rate": learning_rate,
                "stream_exposure_tokens": dict(
                    stream_exposure_tokens
                ),
                "preclip_gradient_norm": float(
                    torch.as_tensor(
                        gradient_norm
                    ).detach().cpu()
                ),
            }
            _append_jsonl(metrics_path, step_record)

            should_evaluate = exposure_tokens >= next_eval
            hit_final_budget = (
                step >= protocol["exposure"]["max_optimizer_steps"]
                or exposure_tokens
                >= protocol["exposure"]["max_exposure_tokens"]
                or hit_limit
            )

            if should_evaluate or hit_final_budget:
                validation_loss = _validation_loss(
                    model,
                    validation_segments,
                    device,
                )
                evaluation = {
                    "type": "validation",
                    "step": step,
                    "exposure_tokens": exposure_tokens,
                    "validation_loss": validation_loss,
                }
                evaluations.append(evaluation)
                _append_jsonl(metrics_path, evaluation)

                if validation_loss < best_validation_loss:
                    best_validation_loss = validation_loss
                    consecutive_degraded = 0
                    payload = _checkpoint_payload(
                        model=model,
                        optimizer=optimizer,
                        schedule=schedule,
                        sampler=sampler,
                        protocol=protocol,
                        authorization=authorization,
                        trainer_freeze=trainer_freeze,
                        step=step,
                        exposure_tokens=exposure_tokens,
                        best_validation_loss=best_validation_loss,
                        evaluations=evaluations,
                        consecutive_degraded=
                            consecutive_degraded,
                        stream_exposure_tokens=
                            stream_exposure_tokens,
                    )
                    _save_checkpoint(
                        best_checkpoint,
                        payload,
                    )
                else:
                    degradation = (
                        validation_loss
                        / best_validation_loss
                        - 1.0
                    )
                    threshold = (
                        protocol["evaluation"]["early_stop"][
                            "relative_validation_loss_degradation_bp"
                        ]
                        / 10000
                    )
                    if degradation >= threshold:
                        consecutive_degraded += 1
                    else:
                        consecutive_degraded = 0

                payload = _checkpoint_payload(
                    model=model,
                    optimizer=optimizer,
                    schedule=schedule,
                    sampler=sampler,
                    protocol=protocol,
                    authorization=authorization,
                    trainer_freeze=trainer_freeze,
                    step=step,
                    exposure_tokens=exposure_tokens,
                    best_validation_loss=best_validation_loss,
                    evaluations=evaluations,
                    consecutive_degraded=consecutive_degraded,
                    stream_exposure_tokens=stream_exposure_tokens,
                )
                _save_checkpoint(
                    last_checkpoint,
                    payload,
                )

                for probe in _fixed_probe_segments(
                    validation_segments
                ):
                    probe_result = _greedy_probe(
                        model,
                        tokenizer,
                        probe,
                        device,
                    )
                    probe_result.update(
                        {
                            "type": "generation_probe",
                            "step": step,
                            "exposure_tokens":
                                exposure_tokens,
                        }
                    )
                    _append_jsonl(
                        probes_path,
                        probe_result,
                    )

                if should_evaluate:
                    interval = protocol["evaluation"][
                        "validation_every_exposure_tokens"
                    ]
                    while next_eval <= exposure_tokens:
                        next_eval += interval

                early = protocol["evaluation"]["early_stop"]
                if (
                    len(evaluations)
                    >= early["minimum_completed_evals"]
                    and consecutive_degraded
                    >= early["consecutive_degraded_evals"]
                ):
                    stop_reason = (
                        "EARLY_STOP_VALIDATION_DEGRADATION"
                    )
                    break

            if hit_limit:
                stop_reason = "MAX_EXPOSURE_TOKENS"
                break

        if stop_reason is None:
            if step >= protocol["exposure"]["max_optimizer_steps"]:
                stop_reason = "MAX_OPTIMIZER_STEPS"
            elif (
                exposure_tokens
                >= protocol["exposure"]["max_exposure_tokens"]
            ):
                stop_reason = "MAX_EXPOSURE_TOKENS"
            else:
                stop_reason = "SAMPLER_EXHAUSTED"

        final_payload = _checkpoint_payload(
            model=model,
            optimizer=optimizer,
            schedule=schedule,
            sampler=sampler,
            protocol=protocol,
            authorization=authorization,
            trainer_freeze=trainer_freeze,
            step=step,
            exposure_tokens=exposure_tokens,
            best_validation_loss=best_validation_loss,
            evaluations=evaluations,
            consecutive_degraded=consecutive_degraded,
            stream_exposure_tokens=stream_exposure_tokens,
        )
        _save_checkpoint(
            last_checkpoint,
            final_payload,
        )

        summary = {
            "schema_version": "v59-pilot-run-summary-1",
            "status": "STOPPED",
            "stop_reason": stop_reason,
            "training_started": bool(step > 0),
            "optimizer_steps": step,
            "exposure_tokens": exposure_tokens,
            "best_validation_loss": best_validation_loss,
            "evaluations": len(evaluations),
            "stream_exposure_tokens": dict(
                stream_exposure_tokens
            ),
            "stream_share_bp": {
                stream: (
                    round(
                        stream_exposure_tokens[stream]
                        * 10000
                        / exposure_tokens
                    )
                    if exposure_tokens
                    else 0
                )
                for stream in STREAMS
            },
            "authorization_freeze_fingerprint":
                authorization["freeze_fingerprint"],
            "trainer_freeze_fingerprint":
                trainer_freeze["trainer_freeze_fingerprint"],
            "blind_test_accessed": False,
            "last_checkpoint": str(last_checkpoint),
            "best_checkpoint": (
                str(best_checkpoint)
                if best_checkpoint.exists()
                else None
            ),
        }
        _write_json_atomic(
            run_dir / "RUN-SUMMARY.json",
            summary,
        )

        manifest["status"] = "STOPPED"
        manifest["stop_reason"] = stop_reason
        manifest["optimizer_steps"] = step
        manifest["exposure_tokens"] = exposure_tokens
        manifest["training_started"] = bool(step > 0)
        _write_json_atomic(run_manifest, manifest)

        return summary

    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass
