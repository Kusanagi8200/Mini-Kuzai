"""Immutable two-report V74 Discussion closure, never a publication entry point.

The public FINAL must represent both CORE and STRATA in one compact comment.
This module has no GitHub writes and never initiates LinkedIn delivery.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

CORE = "reports/assistant-results/history/PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001.json"
STRATA = "reports/assistant-results/history/PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001.json"
COMMITS = {
    CORE: "54dace24112f920232cb6106422f6da7ab35d24c",
    STRATA: "7b36b3fb18c6f31037f90ada947b56469f73424f",
}
BINS = ("F0", "F1_9", "F10_99", "F100P")
MODES = ("ORIG", "CENTER", "PC1", "UNIGRAM")
SAFE = ("SEMANTIC_VALIDATION_COMPLETE", "TRAINING_AUTHORIZED", "TRAINING_STARTED")
GITHUB = "https://github.com/Kusanagi8200/Mini-Kuzai"
MAX_GITHUB_BODY = 1900  # Conservative limit for downstream LinkedIn 2800-character body.


class V74ClosureError(ValueError):
    pass


def reject(reason: str):
    raise V74ClosureError(reason)


def pinned_report_urls():
    return {path: f"{GITHUB}/blob/{commit}/{path}" for path, commit in COMMITS.items()}


def verify_git_pins(root: Path) -> None:
    """Require Git's actual immutable published blobs to match current files."""
    for path, commit in COMMITS.items():
        disk = root / path
        if not disk.is_file() or disk.is_symlink():
            reject("V74 immutable report unavailable")
        result = subprocess.run(
            ["git", "-C", str(root), "show", f"{commit}:{path}"],
            capture_output=True, check=False,
        )
        if result.returncode or result.stdout != disk.read_bytes():
            reject("V74 immutable report differs from its pinned GOGIT commit")


def validate_pair(core: dict, strata: dict) -> tuple[dict, dict]:
    if not isinstance(core, dict) or not isinstance(strata, dict):
        reject("V74 reports must be objects")
    m = core.get("metrics")
    n = strata.get("metrics")
    if not (isinstance(m, dict) and isinstance(n, dict) and
            len(m) == len(n) == 30 and
            core.get("step_id") == CORE.rsplit("/", 1)[1][:-5] and
            strata.get("step_id") == STRATA.rsplit("/", 1)[1][:-5] and
            all(type(v) is int and 0 <= v <= 100000000
                for v in list(m.values()) + list(n.values())) and
            all(m.get(k) == n.get(k) == 0 for k in SAFE) and
            m.get("V74_CORE_PASS") == n.get("V74_STRATA_PASS") == 1 and
            m.get("V74_CORE_BLIND_ACCESS") == n.get("V74_STRATA_BLIND_ACCESS") == 0 and
            m.get("V74_CORE_VAL_LEXICAL") == n.get("V74_STRATA_VAL_LEXICAL") == 9170 and
            n.get("V74_STRATA_TRAIN_LEXICAL") == 294726 and
            n.get("V74_STRATA_TRAIN_TYPES") == 891):
        reject("V74 dual GOGIT provenance, safety or schema invalid")
    if not (set(m) == set(SAFE) | {
                "V74_CORE_PASS", "V74_CORE_BLIND_ACCESS", "V74_CORE_VAL_LEXICAL"
             } | {f"V74_CORE_{b}_COUNT" for b in BINS} |
             {f"V74_CORE_{mode}_{field}"
              for mode in MODES for field in
              ("CORRECT", "DISTINCT", "TOP1_SHARE_BP", "BYTE_CORRECT", "MERGE_CORRECT")}
            and set(n) == set(SAFE) | {
                "V74_STRATA_PASS", "V74_STRATA_BLIND_ACCESS",
                "V74_STRATA_VAL_LEXICAL", "V74_STRATA_TRAIN_LEXICAL",
                "V74_STRATA_TRAIN_TYPES",
                "V74_STRATA_PC1_UNIGRAM_AGREE",
                "V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT",
             } | {f"V74_STRATA_{b}_COUNT" for b in BINS} |
             {f"V74_STRATA_{mode}_{b}_CORRECT" for mode in MODES for b in BINS}):
        reject("V74 exact frozen metric allowlist mismatch")

    frozen = {
        "ORIG": (2673, 5, 7255, 2533, 140),
        "CENTER": (2832, 15, 5788, 2764, 68),
        "PC1": (2455, 2, 7034, 2449, 6),
        "UNIGRAM": (2535, 1, 10000, 2535, 0),
    }
    for mode, expected in frozen.items():
        actual = tuple(m[f"V74_CORE_{mode}_{key}"] for key in
                       ("CORRECT", "DISTINCT", "TOP1_SHARE_BP",
                        "BYTE_CORRECT", "MERGE_CORRECT"))
        if actual != expected or actual[0] != actual[3] + actual[4]:
            reject("V74 frozen CORE counts differ from verified GOGIT")

    denominators = {"F0": 3, "F1_9": 7, "F10_99": 698, "F100P": 8462}
    for b, expected in denominators.items():
        if (m[f"V74_CORE_{b}_COUNT"] != expected or
                n[f"V74_STRATA_{b}_COUNT"] != expected):
            reject("V74 gold-token TRAIN-frequency strata mismatch")
    if sum(denominators.values()) != 9170:
        reject("V74 denominator invariant failed")
    for mode in MODES:
        if (sum(n[f"V74_STRATA_{mode}_{b}_CORRECT"] for b in BINS)
                != m[f"V74_CORE_{mode}_CORRECT"] or
                any(n[f"V74_STRATA_{mode}_{b}_CORRECT"] >
                    denominators[b] for b in BINS)):
            reject("V74 CORE/STRATA reconciliation failed")
    if (n["V74_STRATA_PC1_UNIGRAM_AGREE"] != 6450 or
            n["V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT"] != 2449):
        reject("V74 frozen overlap counts differ from verified GOGIT")
    return m, n


def closure_body(core: dict, strata: dict, *, header: str, footer: str) -> str:
    """Render one evidence-rich yet compact public GitHub and LinkedIn body."""
    m, n = validate_pair(core, strata)
    urls = pinned_report_urls()
    body = "\n\n".join((
        header,
        "## V74 Frequency-Prior Control - GOGIT CORE + STRATA verified",
        "Two immutable, independently committed numeric reports (30 metrics each):\n"
        f"CORE: {urls[CORE]}\nSTRATA: {urls[STRATA]}",
        "### Frozen VALIDATION results (9,170 lexical targets)\n"
        f"ORIGINAL: {m['V74_CORE_ORIG_CORRECT']} correct (29.15%)\n"
        f"CENTER: {m['V74_CORE_CENTER_CORRECT']} correct (30.88%)\n"
        f"PC1_ONLY: {m['V74_CORE_PC1_CORRECT']} correct (26.77%, 2 predicted IDs)\n"
        f"TRAIN_UNIGRAM: {m['V74_CORE_UNIGRAM_CORRECT']} correct (27.64%, 1 predicted ID)",
        f"PC1_ONLY and unigram agree on {n['V74_STRATA_PC1_UNIGRAM_AGREE']}/9170 predictions. "
        f"{n['V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT']}/{m['V74_CORE_PC1_CORRECT']} "
        "PC1_ONLY hits are also unigram hits. "
        "PC1_ONLY has 6 correct predictions not shared by unigram; unigram has 86 not shared by PC1_ONLY.",
        "### Interpretation limits\n"
        "The strong TRAIN-token-frequency confound explains much of PC1_ONLY top-1 correctness. "
        "Axes and centering were fitted on VALIDATION; this teacher-forced experiment "
        "does not establish causality, semantic ability or independent generalization. "
        "No new training and no BLIND access occurred.",
        "---\n\n" + footer,
    ))
    if not (body.startswith(header + "\n") and body.endswith(footer)
            and len(body) <= MAX_GITHUB_BODY):
        reject("V74 final comment exceeds compact review limit")
    return body
