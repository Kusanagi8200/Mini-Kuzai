#!/usr/bin/env python3
"""V59 weighted diagnostic for bulk quality sample 001.

The sample is deterministic and category-balanced. The weighted estimates use
the observed priority x source x turn strata and finite-population variance as
an approximate diagnostic, not as a formal probability-sampling confidence
statement.
"""

from __future__ import annotations

import importlib.util
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PUBLISHER_PATH = REPO / "tools" / "publish_smoltalk_v59_bulk_sample.py"
ROOT = REPO / "reviews" / "smoltalk-v59-bulk-sample-001"
CASES = ROOT / "cases"

EXPECTED_POPULATION = 1080
EXPECTED_SAMPLE = 72
EXPECTED_STRATA = 10


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PUBLISHER = load_module(
    "phase03_v59_bulk_publisher_for_weighting",
    PUBLISHER_PATH,
)


def page_field(text, name):
    match = re.search(
        rf"^{re.escape(name)}: (.+)$",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError(f"Missing field {name}")
    return match.group(1).strip()


def reviewed_by_sha():
    rows = {}

    for path in sorted(CASES.glob("*.md")):
        if path.is_symlink():
            raise RuntimeError(f"Unsafe case symlink: {path}")

        text = path.read_text(encoding="utf-8")

        sha = page_field(
            text,
            "Public content SHA-256",
        )
        disposition = page_field(
            text,
            "V59 disposition",
        )
        factual_risk = page_field(
            text,
            "V59 factual risk",
        )
        instruction_fit = page_field(
            text,
            "V59 instruction fit",
        )

        if disposition not in {
            "KEEP",
            "REPAIR",
            "EXCLUDE",
        }:
            raise RuntimeError(
                "Sample review is not closed"
            )

        if sha in rows:
            raise RuntimeError(
                "Duplicate reviewed SHA"
            )

        rows[sha] = {
            "disposition": disposition,
            "factual_risk": factual_risk,
            "instruction_fit": instruction_fit,
        }

    if len(rows) != EXPECTED_SAMPLE:
        raise RuntimeError(
            f"Expected {EXPECTED_SAMPLE} reviewed pages"
        )

    return rows


def stratum_key(row):
    return (
        row["priority_hint"],
        row["source_dataset"],
        row["turn_bucket"],
    )


def binary_variance(p, n):
    if n <= 1:
        return 0.0
    return p * (1.0 - p) * n / (n - 1)


def estimate(pop_strata, sample_strata, field, positive):
    total_n = sum(len(values) for values in pop_strata.values())
    estimate_value = 0.0
    variance = 0.0

    for key, population_rows in pop_strata.items():
        N_h = len(population_rows)
        sampled_rows = sample_strata.get(key, [])

        n_h = len(sampled_rows)
        if n_h == 0:
            raise RuntimeError(
                f"Unsampled stratum: {key}"
            )

        x_h = sum(
            1
            for row in sampled_rows
            if row[field] in positive
        )
        p_h = x_h / n_h
        W_h = N_h / total_n

        estimate_value += W_h * p_h

        if N_h > 1 and n_h < N_h:
            s2 = binary_variance(
                p_h,
                n_h,
            )
            variance += (
                (W_h ** 2)
                * (1.0 - n_h / N_h)
                * s2
                / n_h
            )

    se = math.sqrt(
        max(0.0, variance)
    )
    low = max(
        0.0,
        estimate_value - 1.96 * se,
    )
    high = min(
        1.0,
        estimate_value + 1.96 * se,
    )

    return {
        "estimate": estimate_value,
        "se": se,
        "low": low,
        "high": high,
    }


def bp(value):
    return int(
        round(value * 10000)
    )


def main():
    population = PUBLISHER.eligible_population()
    selected, strata_source = PUBLISHER.draw_sample(
        population
    )

    if len(population) != EXPECTED_POPULATION:
        raise RuntimeError(
            "Eligible population changed"
        )

    if len(selected) != EXPECTED_SAMPLE:
        raise RuntimeError(
            "Selected sample changed"
        )

    if len(strata_source) != EXPECTED_STRATA:
        raise RuntimeError(
            "Observed stratum count changed"
        )

    reviews = reviewed_by_sha()

    selected_shas = {
        row["sha"]
        for row in selected
    }

    if selected_shas != set(reviews):
        raise RuntimeError(
            "Reviewed sample differs from deterministic selection"
        )

    pop_strata = defaultdict(list)
    sample_strata = defaultdict(list)

    for row in population:
        pop_strata[
            stratum_key(row)
        ].append(row)

    for row in selected:
        review = reviews[
            row["sha"]
        ]
        sample_strata[
            stratum_key(row)
        ].append(
            {
                **row,
                **review,
            }
        )

    if set(pop_strata) != set(sample_strata):
        raise RuntimeError(
            "Population/sample strata mismatch"
        )

    raw_counts = Counter(
        reviews[sha]["disposition"]
        for sha in reviews
    )

    if raw_counts != Counter({
        "KEEP": 36,
        "REPAIR": 19,
        "EXCLUDE": 17,
    }):
        raise RuntimeError(
            "Reviewed disposition totals changed"
        )

    keep = estimate(
        pop_strata,
        sample_strata,
        "disposition",
        {"KEEP"},
    )
    repair = estimate(
        pop_strata,
        sample_strata,
        "disposition",
        {"REPAIR"},
    )
    exclude = estimate(
        pop_strata,
        sample_strata,
        "disposition",
        {"EXCLUDE"},
    )
    unchanged_unsuitable = estimate(
        pop_strata,
        sample_strata,
        "disposition",
        {"REPAIR", "EXCLUDE"},
    )
    factual_high = estimate(
        pop_strata,
        sample_strata,
        "factual_risk",
        {"HIGH"},
    )
    instruction_bad = estimate(
        pop_strata,
        sample_strata,
        "instruction_fit",
        {"BAD"},
    )

    weights = []
    for key, rows in sample_strata.items():
        N_h = len(
            pop_strata[key]
        )
        n_h = len(rows)
        weights.extend(
            [N_h / n_h] * n_h
        )

    weight_sum = sum(weights)

    n_eff = (
        weight_sum ** 2
        / sum(
            weight ** 2
            for weight in weights
        )
    )

    if abs(weight_sum - EXPECTED_POPULATION) > 1e-9:
        raise RuntimeError(
            "Calibration weights do not close"
        )

    min_n_h = min(
        len(rows)
        for rows in sample_strata.values()
    )
    max_n_h = max(
        len(rows)
        for rows in sample_strata.values()
    )
    min_N_h = min(
        len(rows)
        for rows in pop_strata.values()
    )
    max_N_h = max(
        len(rows)
        for rows in pop_strata.values()
    )

    metrics = {
        "V59_WEIGHTED_POPULATION":
            EXPECTED_POPULATION,
        "V59_WEIGHTED_SAMPLE":
            EXPECTED_SAMPLE,
        "V59_WEIGHTED_STRATA":
            EXPECTED_STRATA,
        "V59_WEIGHTED_MIN_STRATUM_N":
            min_N_h,
        "V59_WEIGHTED_MAX_STRATUM_N":
            max_N_h,
        "V59_WEIGHTED_MIN_SAMPLE_N":
            min_n_h,
        "V59_WEIGHTED_MAX_SAMPLE_N":
            max_n_h,
        "V59_WEIGHTED_NEFF_X100":
            int(round(n_eff * 100)),
        "V59_WEIGHTED_KEEP_BP":
            bp(keep["estimate"]),
        "V59_WEIGHTED_KEEP_CI95_LOW_BP":
            bp(keep["low"]),
        "V59_WEIGHTED_KEEP_CI95_HIGH_BP":
            bp(keep["high"]),
        "V59_WEIGHTED_REPAIR_BP":
            bp(repair["estimate"]),
        "V59_WEIGHTED_REPAIR_CI95_LOW_BP":
            bp(repair["low"]),
        "V59_WEIGHTED_REPAIR_CI95_HIGH_BP":
            bp(repair["high"]),
        "V59_WEIGHTED_EXCLUDE_BP":
            bp(exclude["estimate"]),
        "V59_WEIGHTED_EXCLUDE_CI95_LOW_BP":
            bp(exclude["low"]),
        "V59_WEIGHTED_EXCLUDE_CI95_HIGH_BP":
            bp(exclude["high"]),
        "V59_WEIGHTED_UNCHANGED_UNSUITABLE_BP":
            bp(unchanged_unsuitable["estimate"]),
        "V59_WEIGHTED_UNCHANGED_UNSUITABLE_CI95_LOW_BP":
            bp(unchanged_unsuitable["low"]),
        "V59_WEIGHTED_UNCHANGED_UNSUITABLE_CI95_HIGH_BP":
            bp(unchanged_unsuitable["high"]),
        "V59_WEIGHTED_FACTUAL_HIGH_BP":
            bp(factual_high["estimate"]),
        "V59_WEIGHTED_INSTRUCTION_BAD_BP":
            bp(instruction_bad["estimate"]),
        "V59_WEIGHTED_FORMAL_PROB_SAMPLE":
            0,
        "V59_WEIGHTED_APPROX_DIAGNOSTIC":
            1,
        "V59_MIX_FINALIZED":
            0,
        "SEMANTIC_VALIDATION_COMPLETE":
            1,
        "TRAINING_AUTHORIZED":
            0,
    }

    print(
        "##### SECTION RESULTS FOR ASSISTANT ######"
    )

    for key in sorted(metrics):
        print(
            f"{key}: {metrics[key]}"
        )


if __name__ == "__main__":
    main()
