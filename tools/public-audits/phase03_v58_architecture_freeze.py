#!/usr/bin/env python3
"""Public numeric audit for frozen V58 architecture."""

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

REPORT = (
    REPO
    / "data/phase-03/reports"
    / "architecture-selection-v58.json"
)

MANIFEST = (
    REPO
    / "data/phase-03/manifests"
    / "architecture-v58-final.json"
)

V57_HISTORY = (
    REPO
    / "reports/assistant-results/history"
    / "PHASE03-SMOLTALK-V57-ARCHITECTURE-PREP-002.json"
)

MARKER = (
    "##### SECTION RESULTS FOR ASSISTANT ######"
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


def audit():
    history = load_json(
        V57_HISTORY
    )

    if (
        history.get(
            "semantic_validation_complete"
        ) is not True
        or history.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "Corrected V57 history invalid"
        )

    report = load_json(
        REPORT
    )

    manifest = load_json(
        MANIFEST
    )

    if (
        report.get("status")
        != "ARCHITECTURE_SELECTED_AND_FROZEN"
        or report.get(
            "architecture_selected"
        ) is not True
        or report.get(
            "architecture_frozen"
        ) is not True
        or report.get(
            "training_mix_finalized"
        ) is not False
        or report.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "Unexpected V58 state"
        )

    selection = report[
        "selection"
    ]

    if (
        selection["name"]
        != "micro"
        or selection[
            "context_length"
        ] != 2048
        or selection[
            "parameters"
        ] != 1184512
        or selection[
            "d_model"
        ] != 128
        or selection[
            "num_heads"
        ] != 4
        or selection[
            "num_layers"
        ] != 4
        or selection[
            "ff_dim"
        ] != 512
    ):
        raise RuntimeError(
            "Frozen architecture mismatch"
        )

    smoke = report[
        "gpu_smoke"
    ]

    if (
        smoke.get("passed")
        is not True
        or smoke.get(
            "loss_finite"
        ) is not True
    ):
        raise RuntimeError(
            "CUDA training smoke failed"
        )

    context = report[
        "context_evidence"
    ]

    segmentation = report[
        "segmentation"
    ]

    envelope = report[
        "data_envelope"
    ]

    v44 = segmentation[
        "v44_provisional"
    ]

    pool = segmentation[
        "public_pool_upper_bound"
    ]

    if (
        context[
            "train_coverage_bp"
        ] != 10000
        or v44[
            "truncated_tokens"
        ] != 0
        or pool[
            "truncated_tokens"
        ] != 0
    ):
        raise RuntimeError(
            "Context or segmentation invariant failed"
        )

    if (
        manifest.get(
            "architecture_frozen"
        ) is not True
        or manifest.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "Architecture manifest invalid"
        )

    metrics = {
        "V58_CONTEXT":
            2048,
        "V58_PARAMS":
            1184512,
        "V58_DMODEL":
            128,
        "V58_HEADS":
            4,
        "V58_LAYERS":
            4,
        "V58_FF":
            512,
        "V58_HEAD_DIM":
            32,
        "V58_TRAIN_COVERAGE_BP":
            context[
                "train_coverage_bp"
            ],
        "V58_V44_UNSEG_COVERAGE_BP":
            context[
                "v44_unsegmented_coverage_bp"
            ],
        "V58_V44_SEGMENTED_CONVERSATIONS":
            v44[
                "segmented_conversations"
            ],
        "V58_V44_CHUNKS":
            v44[
                "chunks"
            ],
        "V58_POOL_SEGMENTED_CONVERSATIONS":
            pool[
                "segmented_conversations"
            ],
        "V58_POOL_CHUNKS":
            pool[
                "chunks"
            ],
        "V58_V44_TOKENS_PER_PARAM_X1000":
            envelope[
                "v44_tokens_per_param_x1000"
            ],
        "V58_POOL_TOKENS_PER_PARAM_X1000":
            envelope[
                "pool_tokens_per_param_x1000"
            ],
        "V58_ATTN_4096_VS_2048_X100":
            context[
                "attention_4096_vs_2048_x100"
            ],
        "V58_GPU_SMOKE":
            1,
        "V58_GPU_BF16":
            int(
                smoke["bf16"]
            ),
        "V58_GPU_PEAK_ALLOC_MIB":
            smoke[
                "peak_allocated_mib"
            ],
        "V58_GPU_PEAK_RESERVED_MIB":
            smoke[
                "peak_reserved_mib"
            ],
        "V58_ARCH_SELECTED":
            1,
        "V58_ARCH_FROZEN":
            1,
        "V58_MIX_FINALIZED":
            0,
        "V56_TOKENIZER_FINALIZED":
            1,
        "SEMANTIC_VALIDATION_COMPLETE":
            1,
        "TRAINING_AUTHORIZED":
            0,
    }

    return dict(
        sorted(
            metrics.items()
        )
    )


if __name__ == "__main__":
    result = audit()

    print(MARKER)

    for key, value in result.items():
        print(
            f"{key}: {value}"
        )
