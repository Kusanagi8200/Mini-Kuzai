#!/usr/bin/env python3
"""Select, hardware-check and freeze the V58 Phase 03 architecture."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import torch
import torch.nn.functional as F


REPO = Path(__file__).resolve().parents[1]

V57_PATH = (
    REPO
    / "tools"
    / "phase03_v57_architecture_prep.py"
)

MODEL_PATH = (
    REPO
    / "mini_kuzai"
    / "phase03_model.py"
)

V57_REPORT = (
    REPO
    / "data/phase-03/reports"
    / "architecture-prep-v57.json"
)

CONFIG_PATH = (
    REPO
    / "data/phase-03/config"
    / "architecture-v58-final.json"
)

REPORT_PATH = (
    REPO
    / "data/phase-03/reports"
    / "architecture-selection-v58.json"
)

MANIFEST_PATH = (
    REPO
    / "data/phase-03/manifests"
    / "architecture-v58-final.json"
)

CONTEXT = 2048
EXPECTED_PARAMS = 1184512


def load_module(
    name,
    path,
):
    spec = (
        importlib.util
        .spec_from_file_location(
            name,
            path,
        )
    )

    if (
        spec is None
        or spec.loader is None
    ):
        raise RuntimeError(
            f"Unable to load {path}"
        )

    module = (
        importlib.util
        .module_from_spec(
            spec
        )
    )

    sys.modules[
        spec.name
    ] = module

    spec.loader.exec_module(
        module
    )

    return module


V57 = load_module(
    "phase03_v57_for_v58",
    V57_PATH,
)

MODEL = load_module(
    "phase03_model_v58",
    MODEL_PATH,
)


def load_json(path):
    if (
        not path.is_file()
        or path.is_symlink()
    ):
        raise RuntimeError(
            f"Missing or unsafe JSON: {path}"
        )

    value = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def write_json(
    path,
    value,
):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = (
        path.with_suffix(
            path.suffix
            + ".tmp"
        )
    )

    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(
        path
    )


def sha256(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def lengths(
    rows,
    count_text,
):
    return [
        V57.serialized_length(
            row["messages"],
            count_text,
        )
        for row in rows
    ]


def segmentation(
    values,
):
    chunks = [
        math.ceil(
            value
            / CONTEXT
        )
        for value in values
    ]

    return {
        "conversations":
            len(values),
        "tokens":
            sum(values),
        "segmented_conversations":
            sum(
                value > CONTEXT
                for value in values
            ),
        "chunks":
            sum(chunks),
        "max_chunks":
            max(chunks),
        "truncated_tokens":
            0,
    }


def tokens_per_param_x1000(
    tokens,
):
    return round(
        tokens
        * 1000
        / EXPECTED_PARAMS
    )


def gpu_smoke(model):
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA unavailable - architecture freeze blocked"
        )

    device = torch.device(
        "cuda"
    )

    model = model.to(
        device
    )

    use_bf16 = bool(
        torch.cuda.is_bf16_supported()
    )

    dtype = (
        torch.bfloat16
        if use_bf16
        else torch.float16
    )

    optimizer = (
        torch.optim.AdamW(
            model.parameters(),
            lr=1e-4,
        )
    )

    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)

    tokens = torch.randint(
        3,
        1024,
        (
            1,
            CONTEXT,
        ),
        device=device,
    )

    targets = torch.randint(
        3,
        1024,
        (
            1,
            CONTEXT,
        ),
        device=device,
    )

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    optimizer.zero_grad(
        set_to_none=True
    )

    with torch.autocast(
        device_type="cuda",
        dtype=dtype,
    ):
        logits = model(
            tokens
        )

        loss = (
            F.cross_entropy(
                logits.reshape(
                    -1,
                    1024,
                ),
                targets.reshape(
                    -1
                ),
            )
        )

    if not torch.isfinite(
        loss
    ):
        raise RuntimeError(
            "Non-finite CUDA smoke loss"
        )

    loss.backward()
    optimizer.step()

    torch.cuda.synchronize()

    allocated = (
        torch.cuda
        .max_memory_allocated()
        // (1024 * 1024)
    )

    reserved = (
        torch.cuda
        .max_memory_reserved()
        // (1024 * 1024)
    )

    return {
        "passed": True,
        "bf16": use_bf16,
        "peak_allocated_mib":
            int(allocated),
        "peak_reserved_mib":
            int(reserved),
        "loss_finite": True,
    }


def main():
    v57 = load_json(
        V57_REPORT
    )

    if (
        v57.get("status")
        != "ARCHITECTURE_PREPARATION_COMPLETE"
        or v57.get(
            "architecture_selected"
        ) is not False
        or v57.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "V57 architecture state invalid"
        )

    tokenizer = (
        V57.load_tokenizer()
    )

    count_text = (
        V57.make_fast_counter(
            tokenizer
        )
    )

    train_lengths = lengths(
        V57.load_train(),
        count_text,
    )

    v44_lengths = lengths(
        V57.load_v44(),
        count_text,
    )

    pool_lengths = lengths(
        V57.load_pool(),
        count_text,
    )

    train_seg = segmentation(
        train_lengths
    )

    v44_seg = segmentation(
        v44_lengths
    )

    pool_seg = segmentation(
        pool_lengths
    )

    if (
        train_seg[
            "segmented_conversations"
        ]
        != 0
    ):
        raise RuntimeError(
            "2048 context must preserve all controlled TRAIN conversations"
        )

    train_coverage_bp = round(
        sum(
            value <= CONTEXT
            for value in train_lengths
        )
        * 10000
        / len(train_lengths)
    )

    v44_coverage_bp = round(
        sum(
            value <= CONTEXT
            for value in v44_lengths
        )
        * 10000
        / len(v44_lengths)
    )

    if train_coverage_bp != 10000:
        raise RuntimeError(
            "Unexpected controlled TRAIN context coverage"
        )

    config = (
        MODEL.Phase03Config()
    )

    model = (
        MODEL.MiniKuzaiPhase03(
            config
        )
    )

    parameters = (
        MODEL.count_parameters(
            model
        )
    )

    if parameters != EXPECTED_PARAMS:
        raise RuntimeError(
            "Actual model parameter count differs from frozen plan"
        )

    smoke = gpu_smoke(
        model
    )

    config_value = {
        "schema_version":
            "phase03-architecture-v58-1",
        "status":
            "FROZEN",
        "name":
            "micro",
        "model_type":
            "decoder_only_transformer",
        "vocab_size":
            config.vocab_size,
        "context_length":
            config.context_length,
        "d_model":
            config.d_model,
        "num_heads":
            config.num_heads,
        "head_dim":
            config.head_dim,
        "num_layers":
            config.num_layers,
        "ff_dim":
            config.ff_dim,
        "pre_norm":
            True,
        "activation":
            "gelu",
        "learned_position_embedding":
            True,
        "tied_token_embedding_lm_head":
            True,
        "attention_projection_bias":
            False,
        "mlp_bias":
            True,
        "dropout":
            0.0,
        "right_padding_only":
            True,
        "parameters":
            parameters,
    }

    write_json(
        CONFIG_PATH,
        config_value,
    )

    report = {
        "schema_version":
            "v58-architecture-selection-1",
        "status":
            "ARCHITECTURE_SELECTED_AND_FROZEN",
        "selection": {
            **config_value,
            "reason": (
                "2048 preserves all controlled TRAIN conversations; "
                "longer public candidate conversations can be segmented "
                "without truncation. MICRO is the most conservative "
                "candidate relative to the available public token envelope."
            ),
        },
        "context_evidence": {
            "train_coverage_bp":
                train_coverage_bp,
            "v44_unsegmented_coverage_bp":
                v44_coverage_bp,
            "attention_4096_vs_2048_x100":
                400,
        },
        "segmentation": {
            "policy":
                "contiguous non-overlapping token windows",
            "controlled_train":
                train_seg,
            "v44_provisional":
                v44_seg,
            "public_pool_upper_bound":
                pool_seg,
        },
        "data_envelope": {
            "controlled_train_tokens":
                train_seg["tokens"],
            "v44_tokens":
                v44_seg["tokens"],
            "pool_tokens":
                pool_seg["tokens"],
            "v44_tokens_per_param_x1000":
                tokens_per_param_x1000(
                    v44_seg["tokens"]
                ),
            "pool_tokens_per_param_x1000":
                tokens_per_param_x1000(
                    pool_seg["tokens"]
                ),
        },
        "gpu_smoke":
            smoke,
        "tokenizer_fingerprint":
            tokenizer.fingerprint(),
        "serializer_frozen":
            True,
        "architecture_selected":
            True,
        "architecture_frozen":
            True,
        "training_mix_finalized":
            False,
        "training_authorized":
            False,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    manifest = {
        "schema_version":
            "v58-architecture-manifest-1",
        "status":
            "FROZEN",
        "architecture_step_id":
            "PHASE03-SMOLTALK-V58-ARCHITECTURE-FREEZE-001",
        "config_path":
            str(
                CONFIG_PATH.relative_to(
                    REPO
                )
            ),
        "model_source_path":
            str(
                MODEL_PATH.relative_to(
                    REPO
                )
            ),
        "report_path":
            str(
                REPORT_PATH.relative_to(
                    REPO
                )
            ),
        "config_sha256":
            sha256(CONFIG_PATH),
        "model_source_sha256":
            sha256(MODEL_PATH),
        "architecture":
            "micro",
        "context_length":
            CONTEXT,
        "parameters":
            parameters,
        "tokenizer_fingerprint":
            tokenizer.fingerprint(),
        "architecture_selected":
            True,
        "architecture_frozen":
            True,
        "training_mix_finalized":
            False,
        "training_authorized":
            False,
    }

    write_json(
        MANIFEST_PATH,
        manifest,
    )

    print(
        "V58 ARCHITECTURE FROZEN"
    )

    print(
        "PARAMETERS:",
        parameters,
    )

    print(
        "GPU_PEAK_ALLOC_MIB:",
        smoke[
            "peak_allocated_mib"
        ],
    )


if __name__ == "__main__":
    main()
