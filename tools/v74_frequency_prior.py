"""V74 read-only frequency-prior controls of V62 model and frozen TRAIN/VALIDATION.

Computes four lexical top-1 modes and predefined TRAIN-frequency strata.
Returns aggregate integers only. Does not save tensors, touch BLIND or train.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from collections import Counter
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mini_kuzai import phase03_v62_trainer as T

AUDITS = ROOT / "tools" / "public-audits"
HISTORY = ROOT / "reports" / "assistant-results" / "history"
V65 = AUDITS / "phase03_v65_token_frequency_diagnostic_001.py"
V73 = AUDITS / "phase03_v73_principal_axis_attribution_001.py"
V65_ID = "PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001"
V73_ID = "PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001"
MODES = ("ORIG", "CENTER", "PC1", "UNIGRAM")
BINS = ("F0", "F1_9", "F10_99", "F100P")
SAFE = ("SEMANTIC_VALIDATION_COMPLETE", "TRAINING_AUTHORIZED", "TRAINING_STARTED")
CHUNK = 512
LEXICAL = 9170
BYTE = 4876
MERGED = 4294


def imported(name: str, source: Path):
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("V74 reviewed dependency unavailable or unsafe")
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("V74 dependency import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def report(name: str, source: Path, prefix: str, required: dict):
    path = HISTORY / (name + ".json")
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V74 immutable report missing or unsafe")
    import json
    obj = json.loads(path.read_text(encoding="utf-8"))
    metrics = obj.get("metrics")
    if not (
        obj.get("step_id") == name
        and obj.get("producer") == str(source.relative_to(ROOT))
        and obj.get("producer_sha256") == hashlib.sha256(source.read_bytes()).hexdigest()
        and obj.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and obj.get("semantic_validation_complete") is False
        and obj.get("training_authorized") is False
        and obj.get("private_conversation_data_included") is False
        and isinstance(metrics, dict) and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100000000 for v in metrics.values())
        and all(metrics.get(key) == value for key, value in required.items())
        and all(metrics.get(key) == 0 for key in SAFE)
        and all(key.startswith(prefix) or key in SAFE for key in metrics)
    ):
        raise RuntimeError("V74 immutable V65/V73 provenance or metric mismatch")
    return metrics


def frequency_bin(observed: int) -> str:
    if type(observed) is not int or observed < 0:
        raise ValueError("V74 invalid TRAIN frequency")
    if observed == 0:
        return "F0"
    if observed <= 9:
        return "F1_9"
    if observed <= 99:
        return "F10_99"
    return "F100P"


def most_frequent(frequency: Counter) -> int:
    if not frequency:
        raise ValueError("Empty TRAIN counter")
    if any(type(token) is not int or not 3 <= token < T.VOCAB_SIZE
           or type(count) is not int or count <= 0
           for token, count in frequency.items()):
        raise ValueError("Invalid TRAIN counter")
    # Tie break --> lowest token ID. Selection NEVER observes VALIDATION.
    return min(frequency, key=lambda token: (-frequency[token], token))


def core_keys():
    return set(SAFE) | {
        "V74_CORE_PASS", "V74_CORE_BLIND_ACCESS", "V74_CORE_VAL_LEXICAL",
    } | {f"V74_CORE_{b}_COUNT" for b in BINS} | {
        f"V74_CORE_{m}_{field}"
        for m in MODES
        for field in ("CORRECT", "DISTINCT", "TOP1_SHARE_BP",
                      "BYTE_CORRECT", "MERGE_CORRECT")
    }


def strata_keys():
    return set(SAFE) | {
        "V74_STRATA_PASS", "V74_STRATA_BLIND_ACCESS", "V74_STRATA_VAL_LEXICAL",
        "V74_STRATA_TRAIN_LEXICAL", "V74_STRATA_TRAIN_TYPES",
        "V74_STRATA_PC1_UNIGRAM_AGREE",
        "V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT",
    } | {f"V74_STRATA_{b}_COUNT" for b in BINS} | {
        f"V74_STRATA_{m}_{b}_CORRECT" for m in MODES for b in BINS
    }


def score(hidden, gold, weights, basis, mean, frequency):
    """Return only aggregate counters; neither token IDs nor activations escape."""
    if not (
        hidden.shape == (LEXICAL, 128)
        and gold.shape == (LEXICAL,)
        and weights.shape == (T.VOCAB_SIZE, 128)
        and basis.shape == (128, 2)
        and mean.shape == (128,)
        and int(gold.lt(259).sum()) == BYTE
        and int(gold.ge(259).sum()) == MERGED
    ):
        raise RuntimeError("V74 frozen tensor inventory changed")
    if not all(torch.isfinite(x).all() for x in (hidden, weights, basis, mean)):
        raise RuntimeError("V74 nonfinite frozen tensors")
    unigram = most_frequent(frequency)
    freq = torch.zeros(T.VOCAB_SIZE, dtype=torch.long, device=gold.device)
    for token, count in frequency.items():
        freq[token] = count
    labels = freq[gold]
    stratum = {
        b: torch.as_tensor(
            [frequency_bin(int(v)) == b for v in labels.tolist()],
            dtype=torch.bool, device=gold.device
        )
        for b in BINS
    }
    bins = {b: int(mask.sum()) for b, mask in stratum.items()}
    if sum(bins.values()) != LEXICAL:
        raise RuntimeError("V74 TRAIN-frequency bin coverage incomplete")
    aggregate = {
        mode: {
            "CORRECT": 0, "BYTE_CORRECT": 0, "MERGE_CORRECT": 0,
            "HISTOGRAM": torch.zeros(T.VOCAB_SIZE, dtype=torch.long),
            "STRATA": {b: 0 for b in BINS},
        } for mode in MODES
    }
    agree = shared_correct = 0
    with torch.inference_mode():
        for start in range(0, LEXICAL, CHUNK):
            stop = min(start + CHUNK, LEXICAL)
            targets = gold[start:stop]
            centered = hidden[start:stop] - mean
            pc1only = centered @ basis[:, 1:] @ basis[:, 1:].T
            vectors = {"ORIG": hidden[start:stop], "CENTER": centered,
                       "PC1": pc1only}
            predicted = {}
            for mode, h in vectors.items():
                logits = F.linear(h, weights)
                if not torch.isfinite(logits).all():
                    raise RuntimeError("V74 nonfinite projection scores")
                predicted[mode] = logits.argmax(1)
            predicted["UNIGRAM"] = torch.full_like(targets, unigram)
            agree += int(predicted["PC1"].eq(predicted["UNIGRAM"]).sum())
            shared_correct += int(
                (predicted["PC1"].eq(targets)
                 & predicted["UNIGRAM"].eq(targets)).sum()
            )
            is_byte = targets.lt(259)
            for mode, prediction in predicted.items():
                match = prediction.eq(targets)
                item = aggregate[mode]
                item["CORRECT"] += int(match.sum())
                item["BYTE_CORRECT"] += int((match & is_byte).sum())
                item["MERGE_CORRECT"] += int((match & ~is_byte).sum())
                item["HISTOGRAM"] += torch.bincount(
                    prediction.to("cpu"), minlength=T.VOCAB_SIZE
                )
                for b in BINS:
                    item["STRATA"][b] += int(
                        (match & stratum[b][start:stop]).sum()
                    )
    for mode, item in aggregate.items():
        hist = item.pop("HISTOGRAM")
        if int(hist.sum()) != LEXICAL:
            raise RuntimeError("V74 histogram coverage incomplete")
        item["DISTINCT"] = int(hist.gt(0).sum())
        item["TOP1_SHARE_BP"] = round(int(hist.max()) * 10000 / LEXICAL)
        if not (
            1 <= item["DISTINCT"] <= T.VOCAB_SIZE
            and 0 <= item["TOP1_SHARE_BP"] <= 10000
            and item["CORRECT"] == item["BYTE_CORRECT"] + item["MERGE_CORRECT"]
            and item["CORRECT"] == sum(item["STRATA"].values())
            and all(0 <= item["STRATA"][b] <= bins[b] for b in BINS)
        ):
            raise RuntimeError("V74 aggregate reconciliation failed")
    if not (0 <= shared_correct <= agree <= LEXICAL):
        raise RuntimeError("V74 agreement statistics invalid")
    return aggregate, bins, agree, shared_correct


def verify_v73_replay(v73, h, gold, w, original, published, v72):
    basis, spectrum = v73.principal_axes(h)
    geometry = imported(
        "v74_v72_geom", v73.V72
    ).spectral_summary(h)
    if round(10000 * geometry["center"][0]) != spectrum["PC1_BP"]:
        raise RuntimeError("V74 V72/V73 spectral replay mismatch")
    outcomes, changes, byte, merge, alignment = v73.measure_modes(
        h, gold, w, basis, geometry["mean"]
    )
    got = v73.build_report(
        spectrum, outcomes, changes, byte, merge, alignment, original, v72
    )
    if got != published:
        raise RuntimeError("V74 full immutable V73 metric replay mismatch")
    return basis, geometry["mean"]


def build_reports(aggregate, bins, agree, shared_correct, frequency, v72, v73):
    if not (
        set(aggregate) == set(MODES)
        and set(bins) == set(BINS)
        and sum(bins.values()) == LEXICAL
        and sum(frequency.values()) == 294726
        and len(frequency) == 891
    ):
        raise RuntimeError("V74 frozen TRAIN/VALIDATION shape mismatch")
    for mode, original, field in (
        ("ORIG", v72, "V72_GEOM_ORIG"),
        ("CENTER", v73, "V73_AXIS_CENTER"),
        ("PC1", v73, "V73_AXIS_PC1_ONLY"),
    ):
        item = aggregate[mode]
        for source, target in (
            ("CORRECT", "CORRECT"), ("DISTINCT", "DISTINCT"),
            ("TOP1_SHARE_BP", "TOP1_SHARE_BP")
        ):
            if item[source] != original[field + "_" + target]:
                raise RuntimeError("V74 frozen V72/V73 top1 replay mismatch")
    if aggregate["UNIGRAM"]["DISTINCT"] != 1 or aggregate["UNIGRAM"]["TOP1_SHARE_BP"] != 10000:
        raise RuntimeError("V74 unigram must be constant")
    if not (0 <= shared_correct <= min(agree, aggregate["PC1"]["CORRECT"],
                                       aggregate["UNIGRAM"]["CORRECT"])):
        raise RuntimeError("V74 shared correctness invalid")

    core = {key: 0 for key in SAFE}
    core.update({
        "V74_CORE_PASS": 1,
        "V74_CORE_BLIND_ACCESS": 0,
        "V74_CORE_VAL_LEXICAL": LEXICAL,
    })
    core.update({f"V74_CORE_{b}_COUNT": bins[b] for b in BINS})
    for mode in MODES:
        for field in ("CORRECT", "DISTINCT", "TOP1_SHARE_BP",
                      "BYTE_CORRECT", "MERGE_CORRECT"):
            core[f"V74_CORE_{mode}_{field}"] = aggregate[mode][field]

    strata = {key: 0 for key in SAFE}
    strata.update({
        "V74_STRATA_PASS": 1,
        "V74_STRATA_BLIND_ACCESS": 0,
        "V74_STRATA_VAL_LEXICAL": LEXICAL,
        "V74_STRATA_TRAIN_LEXICAL": sum(frequency.values()),
        "V74_STRATA_TRAIN_TYPES": len(frequency),
        "V74_STRATA_PC1_UNIGRAM_AGREE": agree,
        "V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT": shared_correct,
    })
    strata.update({f"V74_STRATA_{b}_COUNT": bins[b] for b in BINS})
    for mode in MODES:
        for b in BINS:
            strata[f"V74_STRATA_{mode}_{b}_CORRECT"] = aggregate[mode]["STRATA"][b]

    for name, metrics, keys in (("CORE", core, core_keys()),
                                ("STRATA", strata, strata_keys())):
        if not (
            len(metrics) == len(keys) == 30
            and set(metrics) == keys
            and all(type(value) is int and 0 <= value <= 100000000
                    for value in metrics.values())
        ):
            raise RuntimeError(f"V74 {name} strict 30 integer metric gate failed")
    return core, strata


def compute():
    v65 = imported("v74_frozen_v65", V65)
    v73 = imported("v74_frozen_v73", V73)
    v64 = v73.imported("v74_frozen_v64", v73.V64)
    m65 = report(V65_ID, V65, "V65_FREQ_", {
        "V65_FREQ_PASS": 1, "V65_FREQ_BLIND_ACCESS": 0,
        "V65_FREQ_VAL_LEXICAL": 9170,
        "V65_FREQ_TRAIN_LEXICAL": 294726,
        "V65_FREQ_TRAIN_TYPES": 891,
    })
    m73 = report(V73_ID, V73, "V73_AXIS_", {
        "V73_AXIS_PASS": 1, "V73_AXIS_BLIND_ACCESS": 0,
        "V73_AXIS_VAL_LEXICAL": 9170,
        "V73_AXIS_CENTER_CORRECT": 2832,
        "V73_AXIS_PC1_ONLY_CORRECT": 2455,
        "V73_AXIS_PC1_ONLY_DISTINCT": 2,
    })
    v72 = v73.prerequisite(v64.read_json)
    model, device, streams, validation = v64.preflight()
    if device.type != "cuda":
        raise RuntimeError("V74 requires the frozen CUDA diagnostic path")
    frequency = v65.count_training_tokens(streams)
    if (sum(frequency.values()) != m65["V65_FREQ_TRAIN_LEXICAL"]
            or len(frequency) != m65["V65_FREQ_TRAIN_TYPES"]):
        raise RuntimeError("V74 frozen TRAIN frequency mismatch")
    v67 = v73.imported("v74_v67", v73.V67)
    v69 = v73.imported("v74_v69", v73.V69)
    h, gold, weights, original = v73.collect(
        model, device, validation, v69, v67.stable_true_ranks
    )
    basis, mean = verify_v73_replay(
        v73, h, gold, weights, original, m73, v72
    )
    # No stochastic training; all work is with frozen tensors and no-grad.
    outcomes, bins, agree, shared = score(
        h, gold, weights, basis, mean, frequency
    )
    return build_reports(outcomes, bins, agree, shared, frequency, v72, m73)


def main(mode: str):
    if mode not in ("CORE", "STRATA"):
        raise ValueError("V74 unknown report mode")
    core, strata = compute()
    output = core if mode == "CORE" else strata
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(output.items()):
        print(f"{key}: {value}")
