#!/usr/bin/env python3
"""Public aggregate audit for V56.3 + V56.4 tokenizer benchmark."""

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

REPORT = (
    REPO
    / "data/phase-03/reports/"
    "tokenizer-benchmark-v56.json"
)

CANDIDATE_HISTORY = (
    REPO
    / "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V56-"
    "TOKENIZER-CANDIDATES-001.json"
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
        CANDIDATE_HISTORY
    )

    if (
        history.get("step_id")
        != (
            "PHASE03-SMOLTALK-V56-"
            "TOKENIZER-CANDIDATES-001"
        )
        or history.get(
            "semantic_validation_complete"
        ) is not True
        or history.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "V56.2 candidate history invalid"
        )

    report = load_json(REPORT)

    if (
        report.get("status")
        != (
            "BENCHMARK_AND_COST_"
            "COMPARISON_COMPLETE"
        )
        or report.get(
            "tokenizer_finalized"
        ) is not False
        or report.get(
            "vocabulary_frozen"
        ) is not False
        or report.get(
            "training_authorized"
        ) is not False
    ):
        raise RuntimeError(
            "V56 benchmark state invalid"
        )

    scope = report.get("scope")

    if not isinstance(scope, dict):
        raise RuntimeError(
            "Benchmark scope missing"
        )

    expected_scope = {
        "train_records": 107,
        "train_groups": 29,
        "train_messages": 248,
        "smoltalk_records": 8000,
        "smoltalk_messages": 36002,
        "smoltalk_sources": 4,
        "total_messages": 36250,
        "validation_included": False,
        "blind_included": False,
        "private_included": False,
    }

    for key, expected in (
        expected_scope.items()
    ):
        if scope.get(key) != expected:
            raise RuntimeError(
                f"Unexpected scope value: {key}"
            )

    configs = report.get("configs")

    if (
        not isinstance(configs, list)
        or len(configs) != 7
    ):
        raise RuntimeError(
            "Expected seven benchmark configs"
        )

    by_name = {
        config["name"]: config
        for config in configs
    }

    expected_names = {
        "byte_baseline",
        "byte_bpe_whitespace_512",
        "byte_bpe_whitespace_1024",
        "byte_bpe_whitespace_2048",
        "byte_bpe_unicode_512",
        "byte_bpe_unicode_1024",
        "byte_bpe_unicode_2048",
    }

    if set(by_name) != expected_names:
        raise RuntimeError(
            "Unexpected benchmark config set"
        )

    if any(
        config.get(
            "roundtrip_failures"
        )
        != 0
        for config in configs
    ):
        raise RuntimeError(
            "Round-trip failure in benchmark"
        )

    baseline = by_name[
        "byte_baseline"
    ]

    def metrics_for(
        config_name,
        prefix,
    ):
        config = by_name[
            config_name
        ]

        return {
            f"{prefix}_VOCAB":
                config["vocab_size"],
            f"{prefix}_COMP_BP":
                config["compression_bp"],
            f"{prefix}_P95":
                config["p95_tokens"],
        }

    metrics = {
        "V56_BENCHMARK_MESSAGES":
            scope["total_messages"],
        "V56_BENCHMARK_CONFIGS":
            len(configs),
        "V56_BENCHMARK_TARGETS":
            len(report["targets"]),
        "V56_BENCHMARK_ROUNDTRIP_FAILURES":
            report["summary"][
                "roundtrip_failures"
            ],
        "V56_BENCHMARK_BASELINE_TOKENS":
            baseline["total_tokens"],
        "V56_BENCHMARK_BASELINE_P95":
            baseline["p95_tokens"],
        "V56_BENCHMARK_PARETO_CONFIGS":
            report["summary"][
                "pareto_config_count"
            ],
        "V56_TOKENIZER_FINALIZED": 0,
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "TRAINING_AUTHORIZED": 0,
    }

    metrics.update(
        metrics_for(
            "byte_bpe_whitespace_512",
            "V56_WS512",
        )
    )

    metrics.update(
        metrics_for(
            "byte_bpe_whitespace_1024",
            "V56_WS1024",
        )
    )

    metrics.update(
        metrics_for(
            "byte_bpe_whitespace_2048",
            "V56_WS2048",
        )
    )

    metrics.update(
        metrics_for(
            "byte_bpe_unicode_512",
            "V56_UN512",
        )
    )

    metrics.update(
        metrics_for(
            "byte_bpe_unicode_1024",
            "V56_UN1024",
        )
    )

    metrics.update(
        metrics_for(
            "byte_bpe_unicode_2048",
            "V56_UN2048",
        )
    )

    if len(metrics) != 28:
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
