#!/usr/bin/env python3
"""V50: local-only cognitive/creative review priority over PUBLIC SmolTalk V44.

Heuristics are recall aids, never semantic validation, training admission,
correctness verification, or independent evidence of a personality.
Only allowlisted numeric aggregates go to gogit; per-case contents remain
outside Git in the local public-external SmolTalk workspace.
"""

import json
import os
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = Path("/root/Mini-Kuzai/data/external/smol-smoltalk")
POOL = ROOT / "candidates/external-candidate-pool-v0.4.jsonl"
V44 = ROOT / "review/stratified-candidates-v44.jsonl"
OUTPUT = ROOT / "review/v50-cognitive-review-priority.jsonl"
REPORT = ROOT / "review/v50-cognitive-review-summary.json"
SHA = re.compile(r"[0-9a-f]{64}\Z")
EXPECTED_SOURCE = {
    "smol-magpie-ultra-short": 5000,
    "openhermes-50k": 1500,
    "self-oss-instruct": 1000,
    "explore-instruct-rewrite": 500,
}
CATEGORIES = {
    "FOLLOWUP", "WRITING", "CREATIVE", "FACTUAL_QA", "MATHEMATICS",
    "PROGRAMMING", "PRACTICAL_ADVICE", "GENERAL_OTHER",
}
CREATIVE = re.compile(
    r"\b(?:fiction|fictional|story|stories|storytelling|novel|poem|poetry|"
    r"character|characters|plot|screenplay|worldbuild(?:ing)?|fantasy|"
    r"imaginary|imagine|brainstorm|roleplay|role-play|creative|"
    r"narrative voice|alternate ending|dialogue scene)\b", re.I
)
COGNITIVE = re.compile(
    r"\b(?:why|how would|how can|what if|why not|consider|compare|"
    r"contrast|reason(?:ing)?|explain|interpret|meaning|perspective|"
    r"hypothes(?:is|es|ize)|uncertain|alternatives?|possibilit(?:y|ies)|"
    r"consequence|how does|which is better|what do you think|"
    r"do you agree|what should|what might|decision|whether)\b", re.I
)
FOLLOWUP = re.compile(
    r"\b(?:you (?:said|wrote|mentioned|suggested)|your (?:last|earlier|"
    r"previous|answer|response|draft)|(?:this|that|the) (?:story|"
    r"sentence|response|answer|paragraph|idea|character|scene|version|"
    r"approach)|continue|again|as before|following your|what next|"
    r"tell me more|go back to|earlier)\b", re.I
)
FEEDBACK = re.compile(
    r"\b(?:not what i|instead|you didn't|you did not|that's not|"
    r"that is not|correct|mistake|too (?:long|short|vague)|"
    r"remove|rewrite|rephrase|revise|change|shorten|expand|"
    r"try again|can you make|more concise|less|i meant|"
    r"make it|without|don't|do not)\b", re.I
)
TECHNICAL = re.compile(
    r"\b(?:python|javascript|typescript|java|c\+\+|php|sql|"
    r"function|compiler|programming|codebase|debug(?:ging)?|"
    r"source code|algorithm|regex|matrix|integral|lyapunov|"
    r"subnet|router|server|linux|powershell|api endpoint)\b", re.I
)
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"


def read_jsonl(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or unsafe external public SmolTalk input")
    with path.open(encoding="utf-8") as stream:
        for raw in stream:
            if raw.strip():
                yield json.loads(raw)


def valid_messages(messages):
    return (
        isinstance(messages, list)
        and len(messages) in (2, 4, 6)
        and [m.get("role") for m in messages] ==
        ["user", "assistant"] * (len(messages) // 2)
        and all(
            isinstance(m.get("content"), str) and m["content"].strip()
            for m in messages
        )
    )


def signals(messages, category):
    users = [m["content"] for m in messages if m["role"] == "user"]
    first = users[0]
    joined = "\n".join(users)
    later = "\n".join(users[1:])
    creative = bool(CREATIVE.search(joined))
    cognitive = bool(COGNITIVE.search(joined))
    followup = len(users) >= 2 and bool(FOLLOWUP.search(later))
    feedback = len(users) >= 2 and bool(FEEDBACK.search(later))
    technical = bool(TECHNICAL.search(first))
    # Categories from V44 are weak, independently recorded hypotheses.
    # A source-specific programming label must not auto-reject an example.
    if creative and len(users) >= 2 and (followup or feedback):
        priority = "HIGH"
    elif cognitive and len(users) >= 2 and (followup or feedback):
        priority = "HIGH"
    elif creative or cognitive or (len(users) >= 2 and (followup or feedback)):
        priority = "MEDIUM"
    else:
        priority = "LOW"
    return {
        "priority_hint": priority,
        "creative_keyword_signal": creative,
        "cognitive_keyword_signal": cognitive,
        "followup_wording_signal": followup,
        "user_feedback_wording_signal": feedback,
        "technical_domain_signal": technical,
        "v44_heuristic_category": category,
    }


def exclusive_bytes(path, body):
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())


def main():
    if ROOT.resolve().is_relative_to(REPO.resolve()):
        raise RuntimeError("All local SmolTalk inputs and outputs must be outside Git")
    if OUTPUT.exists() or OUTPUT.is_symlink() or REPORT.exists() or REPORT.is_symlink():
        raise RuntimeError("V50 local screening outputs already exist; no overwrite")
    pool, source_counts = {}, Counter()
    for rec in read_jsonl(POOL):
        sha = rec.get("content_sha256")
        source = rec.get("source")
        messages = rec.get("messages")
        if (
            not isinstance(sha, str) or not SHA.fullmatch(sha)
            or sha in pool or source not in EXPECTED_SOURCE
            or not valid_messages(messages)
        ):
            raise RuntimeError("Public source record integrity mismatch")
        pool[sha] = rec
        source_counts[source] += 1
    if len(pool) != 8000 or source_counts != EXPECTED_SOURCE:
        raise RuntimeError("Unexpected public SmolTalk source distribution")

    seen, candidates, counts = set(), [], Counter()
    by_v44 = Counter()
    for rec in read_jsonl(V44):
        sha = rec.get("source_content_sha256")
        cat = rec.get("heuristic_category")
        base = pool.get(sha)
        if (
            not isinstance(sha, str) or not SHA.fullmatch(sha)
            or sha in seen or base is None or cat not in CATEGORIES
            or rec.get("source_dataset") != base["source"]
            or rec.get("messages") != base["messages"]
            or rec.get("review_status") != "HEURISTIC_SELECTION_ONLY"
            or rec.get("semantic_validation_complete") is not False
            or rec.get("dataset_split_assigned") is not False
            or rec.get("training_approved") is not False
        ):
            raise RuntimeError("Provisional V44 does not match verified public source")
        seen.add(sha)
        msg = base["messages"]
        flags = signals(msg, cat)
        by_v44[cat] += 1
        counts[flags["priority_hint"]] += 1
        for name in (
            "creative_keyword_signal", "cognitive_keyword_signal",
            "followup_wording_signal", "user_feedback_wording_signal",
            "technical_domain_signal"
        ):
            counts[name] += int(flags[name])
        counts["multiturn"] += int(len(msg) > 2)
        candidates.append({
            "schema": "mini-kuzai.v50.public-smoltalk-local-screen",
            "source": "SmolTalk v0.4 - external public dataset",
            "source_dataset": base["source"],
            "source_content_sha256": sha,
            "messages": msg,
            **flags,
            "review_state": "UNREVIEWED",
            "semantic_validation_complete": False,
            "factual_validation_complete": False,
            "dataset_split_assigned": False,
            "training_approved": False,
        })
    if len(seen) != 1139:
        raise RuntimeError("V44 must contain exactly 1139 unique public records")
    if counts["multiturn"] != 679 or 1139 - counts["multiturn"] != 460:
        raise RuntimeError("V44 turn structure differs from recorded checkpoint")
    candidates.sort(key=lambda r: (
        {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[r["priority_hint"]],
        r["source_content_sha256"]
    ))
    result = {
        "step": "PHASE03-SMOLTALK-V50-COGNITIVE-SCREEN",
        "source": "External public SmolTalk v0.4 only",
        "candidate_count": 1139,
        "reviewed": 0,
        "training_approved": False,
        "semantic_validation_complete": False,
        "tokenizer_frozen": False,
        "method": "Unvalidated keyword-based triage; no automatic quality judgments",
        "hint_counts": dict(sorted(counts.items())),
        "v44_category_counts": dict(sorted(by_v44.items())),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    lines = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in candidates)
    document = json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    try:
        exclusive_bytes(OUTPUT, lines.encode("utf-8"))
        exclusive_bytes(REPORT, document.encode("utf-8"))
    except Exception:
        # Roll back a partially created run. Never replace an older file.
        # Preconditions require neither destination to exist beforehand.
        OUTPUT.unlink(missing_ok=True)
        REPORT.unlink(missing_ok=True)
        raise
    metrics = {
        "V50_QUEUE_TOTAL": 1139,
        "V50_REVIEWED": 0,
        "V50_HIGH_HINT": counts["HIGH"],
        "V50_MEDIUM_HINT": counts["MEDIUM"],
        "V50_LOW_HINT": counts["LOW"],
        "V50_CREATIVE_HINT": counts["creative_keyword_signal"],
        "V50_COGNITIVE_HINT": counts["cognitive_keyword_signal"],
        "V50_FOLLOWUP_HINT": counts["followup_wording_signal"],
        "V50_FEEDBACK_HINT": counts["user_feedback_wording_signal"],
        "V50_TECHNICAL_HINT": counts["technical_domain_signal"],
        "V50_MULTITURN": counts["multiturn"],
        "V50_TRAIN_APPROVED": 0,
    }
    assert sum(metrics[k] for k in (
        "V50_HIGH_HINT", "V50_MEDIUM_HINT", "V50_LOW_HINT"
    )) == 1139
    print(MARKER)
    for key, value in sorted(metrics.items()):
        print("{}: {}".format(key, value))


if __name__ == "__main__":
    main()
