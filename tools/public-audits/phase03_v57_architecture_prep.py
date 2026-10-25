#!/usr/bin/env python3
"""Public aggregate audit for V57 architecture preparation."""

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

REPORT = (
    REPO
    / "data/phase-03/reports"
    / "architecture-prep-v57.json"
)

TOKENIZER_HISTORY = (
    REPO
    / "reports/assistant-results/history"
    / "PHASE03-SMOLTALK-V56-TOKENIZER-FREEZE-001.json"
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

    if not isinstance(value, dict):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def audit():
    history = load_json(
        TOKENIZER_HISTORY
    )

    if (
        history.get("step_id")
        != "PHASE03-SMOLTALK-V56-TOKENIZER-FREEZE-001"
        or history.get(
            "semantic_validation_complete"
        ) is not True
        or history.get(
            "training_authorized"
        ) is not False
        or history.get("metrics", {}).get(
            "V56_TOKENIZER_FINALIZED"
        ) != 1
    ):
        raise RuntimeError(
            "V56 tokenizer history invalid"
        )

    report = load_json(
        REPORT
    )

    if (
        report.get("status")
        != "ARCHITECTURE_PREPARATION_COMPLETE"
        or report.get(
            "architecture_selected"
        ) is not False
        or report.get(
            "training_mix_finalized"
        ) is not False
        or report.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "Unexpected V57 state"
        )

    if (
        report.get(
            "serializer",
            {},
        ).get("frozen")
        is not True
    ):
        raise RuntimeError(
            "Serializer not frozen"
        )

    tokenizer = report.get(
        "tokenizer",
        {},
    )

    if (
        tokenizer.get(
            "vocab_size"
        ) != 1024
        or tokenizer.get(
            "frozen"
        ) is not True
    ):
        raise RuntimeError(
            "Unexpected tokenizer state"
        )

    populations = report[
        "populations"
    ]

    train = populations[
        "controlled_train"
    ]

    v44 = populations[
        "v44_provisional"
    ]

    pool = populations[
        "public_pool_upper_bound"
    ]

    architectures = report[
        "architecture_candidates"
    ]

    if (
        train["conversations"]
        != 107
        or v44["conversations"]
        != 1139
        or pool["conversations"]
        != 8000
        or len(architectures)
        != 4
    ):
        raise RuntimeError(
            "Unexpected V57 population or candidate count"
        )

    names = [
        item["name"]
        for item in architectures
    ]

    if names != [
        "micro",
        "small",
        "medium",
        "large",
    ]:
        raise RuntimeError(
            "Unexpected architecture candidate order"
        )

    context = report[
        "context"
    ]

    metrics = {
        "V57_SERIALIZER_FROZEN":
            1,
        "V57_TRAIN_CONVERSATIONS":
            train["conversations"],
        "V57_TRAIN_TOKENS":
            train["tokens"],
        "V57_TRAIN_P95":
            train["p95"],
        "V57_TRAIN_P99":
            train["p99"],
        "V57_V44_CONVERSATIONS":
            v44["conversations"],
        "V57_V44_TOKENS":
            v44["tokens"],
        "V57_V44_P95":
            v44["p95"],
        "V57_V44_P99":
            v44["p99"],
        "V57_POOL_CONVERSATIONS":
            pool["conversations"],
        "V57_POOL_TOKENS":
            pool["tokens"],
        "V57_POOL_P95":
            pool["p95"],
        "V57_POOL_P99":
            pool["p99"],
        "V57_TRAIN_CTX1024_BP":
            train[
                "coverage_bp"
            ]["1024"],
        "V57_TRAIN_CTX2048_BP":
            train[
                "coverage_bp"
            ]["2048"],
        "V57_V44_CTX1024_BP":
            v44[
                "coverage_bp"
            ]["1024"],
        "V57_V44_CTX2048_BP":
            v44[
                "coverage_bp"
            ]["2048"],
        "V57_V44_CTX4096_BP":
            v44[
                "coverage_bp"
            ]["4096"],
        "V57_CONTEXT_RECOMMENDED":
            context["recommended"],
        "V57_ARCH_CANDIDATES":
            len(architectures),
        "V57_ARCH_MICRO_PARAMS":
            architectures[0][
                "parameters"
            ],
        "V57_ARCH_SMALL_PARAMS":
            architectures[1][
                "parameters"
            ],
        "V57_ARCH_MEDIUM_PARAMS":
            architectures[2][
                "parameters"
            ],
        "V57_ARCH_LARGE_PARAMS":
            architectures[3][
                "parameters"
            ],
        "V57_ARCH_SELECTED":
            0,
        "V57_MIX_FINALIZED":
            0,
        "V56_TOKENIZER_FINALIZED":
            1,
        "SEMANTIC_VALIDATION_COMPLETE":
            1,
        "TRAINING_AUTHORIZED":
            0,
    }

    if len(metrics) != 29:
        raise RuntimeError(
            "Unexpected public metric count"
        )

    return dict(
        sorted(
            metrics.items()
        )
    )


if __name__ == "__main__":
    result = audit()

    print(MARKER)

    for key, value in result.items():
        print(f"{key}: {value}")
