#!/usr/bin/env python3
"""V63 automatic output-quality screen, numeric-only GOGIT.

Read 24 already-generated private TOPP probes and the frozen VALIDATION split.
This measures *surface-form linguistic proxies*, NOT semantic comprehension,
reasoning, persona, or human review. No raw prompt/output is published.
"""
from __future__ import annotations

import importlib.util
import math
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v62_trainer as T

PRIVATE = Path("/root/Mini-Kuzai/runs/v63-semantic-generation-review-001")
STEP = "PHASE03-SMOLTALK-V63-DECODING-ROBUSTNESS-001"
HISTORY = REPO / "reports" / "assistant-results" / "history"
WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
FUNCTION_WORDS = frozenset(
    "a i an am as at be by do go he if in is it me my no of on or so to "
    "up us we the and for not but you are can may was were has had her him "
    "his its our out she who why how did yes now all one two".split()
)


def load_helper(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import existing frozen local review")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def word_tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in WORD.finditer(text)]


def gram_repetition_bp(tokens: list[int], width: int) -> int:
    without_eos = [token for token in tokens if token != T.EOS_ID]
    windows = len(without_eos) - width + 1
    if windows < 1:
        return 0
    unique = len({
        tuple(without_eos[i:i + width]) for i in range(windows)
    })
    return round((windows - unique) * 10000 / windows)


def analyze_text(text: str, lexicon: set[str]) -> dict:
    words = word_tokens(text)
    valid = len(words)
    known = sum(w in lexicon for w in words)
    fragments = sum(
        len(w) <= 2 and w not in FUNCTION_WORDS
        for w in words
    )
    chars = len(text)
    nonblank = sum(not c.isspace() for c in text)
    alpha = sum(c.isalpha() for c in text)
    share = round(known * 10000 / valid) if valid else 0
    fragments_bp = round(fragments * 10000 / valid) if valid else 0
    # Proxy only: suspicious does not mean semantically wrong.
    # Thresholds frozen before reviewing aggregate results.
    suspect = (
        valid == 0
        or (valid >= 6 and share < 4500)
        or (valid >= 6 and fragments_bp >= 2000)
    )
    return {
        "words": valid,
        "known": known,
        "fragments": fragments,
        "nonblank": nonblank,
        "alpha": alpha,
        "characters": chars,
        "suspect": int(suspect),
    }


def compute(samples: list[dict], lexicon: set[str]) -> dict:
    if len(samples) != 24 or not lexicon:
        raise RuntimeError("Expected 24 samples and a nonempty lexicon")
    stats = [analyze_text(row["output"], lexicon) for row in samples]
    words = sum(s["words"] for s in stats)
    known = sum(s["known"] for s in stats)
    fragments = sum(s["fragments"] for s in stats)
    nonblank = sum(s["nonblank"] for s in stats)
    chars = sum(s["characters"] for s in stats)
    if not words or not nonblank or not chars:
        raise RuntimeError("Empty or abnormal 24-sample output inventory")
    output = {
        "AUTO_PASS": 1,
        "AUTO_BLIND_ACCESS": 0,
        "AUTO_HUMAN_RATINGS": 0,
        "AUTO_SAMPLES": len(samples),
        "AUTO_SEEDS": 4,
        "AUTO_EOS": sum(int(s["eos"]) for s in samples),
        "AUTO_UTF8_INVALID": sum(int(not s["utf8_valid"]) for s in samples),
        "AUTO_ROLE_LEAK": sum(int(s["role_leak"]) for s in samples),
        "AUTO_SHORT16": sum(len(s["tokens"]) <= 16 for s in samples),
        "AUTO_MAXLEN96": sum(len(s["tokens"]) == 96 for s in samples),
        "AUTO_MEAN_LEN_X100": round(statistics.mean(len(s["tokens"]) for s in samples)*100),
        "AUTO_WORDS": words,
        "AUTO_MEAN_WORDS_X100": round(words*100/len(samples)),
        "AUTO_VOCAB_WORDS": len(lexicon),
        "AUTO_REF_WORD_COVER_BP": round(known*10000/words),
        "AUTO_UNKNOWN_WORD_BP": round((words-known)*10000/words),
        "AUTO_FRAGMENT_WORD_BP": round(fragments*10000/words),
        "AUTO_SUSPECT_OUTPUTS": sum(s["suspect"] for s in stats),
        "AUTO_ZERO_WORD_OUTPUTS": sum(s["words"]==0 for s in stats),
        "AUTO_ALPHABETIC_BP": round(sum(s["alpha"] for s in stats)*10000/nonblank),
        "AUTO_WHITESPACE_BP": round((chars-nonblank)*10000/chars),
        "AUTO_DISTINCT_TOKEN_BP": round(statistics.mean(
            len(set(s["tokens"]))*10000/len(s["tokens"]) for s in samples
        )),
        "AUTO_REPEAT3_BP": round(statistics.mean(
            gram_repetition_bp(s["tokens"], 3) for s in samples
        )),
        "AUTO_REPEAT8_BP": round(statistics.mean(
            gram_repetition_bp(s["tokens"], 8) for s in samples
        )),
        "AUTO_PROMPT_LEX_OVERLAP_BP": round(statistics.mean(
            len(set(word_tokens(s["output"])) & set(word_tokens(s["prompt"])))
            * 10000 / max(1,len(set(word_tokens(s["output"]))))
            for s in samples
        )),
    }
    if len(output)!=25 or any(type(v) is not int or v<0 or v>100_000_000 for v in output.values()):
        raise RuntimeError("Invalid automatic numeric audit metrics")
    return output


def main():
    import json
    earlier = HISTORY / f"{STEP}.json"
    if not earlier.is_file() or earlier.is_symlink():
        raise RuntimeError("V63 robustness prerequisite missing")
    report = json.loads(earlier.read_text(encoding="utf-8"))
    if (
        report.get("step_id")!=STEP
        or report.get("semantic_validation_complete") is not True
        or report.get("metrics",{}).get("V63_ROB_PASS")!=1
        or report.get("metrics",{}).get("V63_ROB_BLIND_ACCESS")!=0
    ):
        raise RuntimeError("Frozen published V63 robustness report invalid")
    private = load_helper(
        "v63_private_review_for_auto_screen",
        REPO/"tools"/"phase03_v63_semantic_generation_review_001.py"
    )
    samples = private.read_json(private.SAMPLES)
    entries = private.check_samples(samples)
    if {row["seed"] for row in entries} != set(private.SEEDS):
        raise RuntimeError("Unexpected frozen semantic review seed inventory")
    # A vocabulary derived only from frozen VALIDATION conversational text.
    # This is a lexical overlap proxy, not a language model quality score.
    tokenizer = T.load_tokenizer()
    validation, inventory = T.build_validation_segments()
    if inventory.get("records") != 36:
        raise RuntimeError("Frozen VALIDATION inventory changed")
    lexicon = set(FUNCTION_WORDS)
    for seg in validation:
        lexicon.update(word_tokens(tokenizer.decode(seg.token_ids)))
    if len(lexicon)<50:
        raise RuntimeError("Frozen reference lexicon insufficient")
    output={
        "SEMANTIC_VALIDATION_COMPLETE":0,
        "TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,
    }
    output.update({
        f"V63_{name}": number for name,number in compute(entries,lexicon).items()
    })
    if len(output)!=28:
        raise RuntimeError("Unexpected number of GOGIT numeric metrics")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key,value in sorted(output.items()):
        print(f"{key}: {value}")


if __name__=="__main__":
    main()
