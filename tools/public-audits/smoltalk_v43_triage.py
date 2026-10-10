#!/usr/bin/env python3
"""V43: local semantic-review queue + numeric-only public SmolTalk triage.

The published figures are heuristic indicators, NOT independently reviewed
semantic decisions, factual approval, or TRAIN admission.
No conversation text is printed or written inside the Git repository.
"""

import json
import random
import re
from collections import Counter
from pathlib import Path

SOURCE = Path(
    "/root/Mini-Kuzai/data/external/smol-smoltalk/review/"
    "continuity-candidates-v42.jsonl"
)
DIRECTORY = SOURCE.parent
QUEUE = DIRECTORY / "v43-semantic-review-queue.jsonl"
SAMPLE = DIRECTORY / "v43-local-review-sample.txt"

TOKEN = re.compile(r"[a-zA-Z]{3,}")
STOP = set(
    "the and for with that this from have has was were are you your can "
    "could would should about into then than they them their what when where "
    "which how why more some other also just make made please like does"
    .split()
)
REFERENCE = re.compile(
    r"\b(?:you (?:said|wrote|mentioned|added|used|provided)|"
    r"your (?:answer|response|explanation|previous|last|wording|version|draft)|"
    r"(?:this|that|the) (?:answer|response|paragraph|sentence|draft|version|"
    r"wording|explanation|text|story|poem)|"
    r"(?:previous|earlier|above) (?:answer|response|text|sentence|paragraph)|"
    r"(?:make|keep|rewrite|rephrase|shorten|expand|remove|change|improve) "
    r"(?:it|that|this)|as before|what you wrote|you just)\b",
    re.I
)
REVISION = re.compile(
    r"\b(?:rewrite|rephrase|revise|edit|improve|shorten|simplify|expand|"
    r"make (?:it|this|that|the text|the sentence) (?:more|less|shorter|"
    r"longer|clearer)|change the (?:tone|wording)|split (?:it|the sentence)|"
    r"add (?:a |some )?(?:transition|detail|paragraph|sentence))\b",
    re.I
)
CLARIFICATION = re.compile(
    r"\b(?:explain|clarify|elaborate|what do you mean|"
    r"why (?:did|do|is|does)|what is the purpose|"
    r"how (?:does|did|would) (?:that|this|it))\b",
    re.I
)
DISAGREEMENT = re.compile(
    r"\b(?:you are wrong|that's wrong|that is wrong|"
    r"not what i (?:meant|asked)|i disagree|incorrect|"
    r"your answer is (?:wrong|incorrect)|but you said)\b",
    re.I
)
NEW_TASK = re.compile(
    r"^\s*(?:how (?:would|can) you (?:improve|edit|rewrite) "
    r"(?:this|the following) (?:sentence|paragraph)|"
    r"consider (?:the following|another|a new)|"
    r"here is (?:another|a different)|"
    r"solve (?:this|the following)|"
    r"what (?:is|are) (?:the|a) )",
    re.I
)
DOMAINS = [
    ("CREATIVE", re.compile(r"\b(?:poem|story|fiction|novel|character|plot)\b", re.I)),
    ("PROGRAMMING", re.compile(r"\b(?:python|javascript|programming|code snippet|function to|algorithm)\b", re.I)),
    ("MATHEMATICS", re.compile(r"\b(?:derivative|integral|equation|probability|calculate|algebra|theorem)\b", re.I)),
    ("WRITING", re.compile(r"\b(?:essay|paragraph|sentence|grammar|rephrase|edit|writing|rewrite|wording|clarity)\b", re.I)),
    ("FACTUAL_QA", re.compile(r"\b(?:scientist|medicine|health|vaccine|planet|history|historical|research|law|experiment)\b", re.I)),
]
FACTUAL_CLAIMS = re.compile(
    r"\b(?:scientist|medicine|health|vaccine|planet|history|historical|research|"
    r"experiment|derivative|equation|probability|calculation|"
    r"statistics|government|law|regulation)\b",
    re.I
)


def tokens(text):
    return {w.lower() for w in TOKEN.findall(text) if w.lower() not in STOP}


def classify(text):
    for label, expression in DOMAINS:
        if expression.search(text):
            return label
    return "OTHER"


def main():
    if QUEUE.exists() or SAMPLE.exists():
        raise RuntimeError("V43 local review files already exist; refusing overwrite")
    if not SOURCE.is_file():
        raise RuntimeError("Missing V42 local candidates")
    rows = [json.loads(line) for line in SOURCE.open(encoding="utf-8") if line.strip()]
    if len(rows) != 128:
        raise RuntimeError("Expected 128 V42 candidates")

    categories = Counter()
    domains = Counter()
    flags = Counter()
    reviewed = []
    seen = set()

    for row in rows:
        index = row["source_index"]
        record = row["source_record"]
        messages = record["messages"]
        if (
            index in seen or not isinstance(index, int) or not 0 <= index < 5000
            or record["source"] != "smol-magpie-ultra-short"
            or row["source_content_sha256"] != record["content_sha256"]
            or row["training_approved"] is not False
            or len(messages) != 6
            or [m["role"] for m in messages] != ["user", "assistant"] * 3
            or any(not isinstance(m["content"], str) or not m["content"].strip()
                   for m in messages)
        ):
            raise RuntimeError("V42 candidate integrity violation")
        seen.add(index)
        categories[row["heuristic_category"]] += 1

        u1, a1, u2, a2, u3, a3 = (m["content"] for m in messages)
        followups = u2 + "\n" + u3
        all_users = u1 + "\n" + followups
        domain = classify(all_users)
        domains[domain] += 1

        explicit_2 = bool(REFERENCE.search(u2))
        explicit_3 = bool(REFERENCE.search(u3))
        revised = bool(REVISION.search(followups))
        clarified = bool(CLARIFICATION.search(followups))
        disagreed = bool(DISAGREEMENT.search(followups))
        needs_check = bool(FACTUAL_CLAIMS.search(all_users))
        overlap2 = len(tokens(u2) & tokens(a1))
        overlap3 = len(tokens(u3) & tokens(a2))
        possible_switch = bool(
            NEW_TASK.search(u3) and not explicit_3 and overlap3 < 2
        )
        flags["FOLLOWUP"] += explicit_2 and explicit_3
        flags["REVISION"] += revised
        flags["CLARIFICATION"] += clarified
        flags["DISAGREEMENT"] += disagreed
        flags["TOPIC_SWITCHES"] += possible_switch
        flags["FACTCHECK_PENDING"] += needs_check

        if possible_switch:
            priority = "POSSIBLE_TOPIC_SWITCH"
        elif explicit_2 and explicit_3 and (revised or clarified):
            priority = "REVIEW_FIRST"
        elif explicit_2 and explicit_3:
            priority = "REVIEW_SECOND"
        else:
            priority = "REVIEW_OPEN"

        reviewed.append({
            "source_index": index,
            "source_content_sha256": row["source_content_sha256"],
            "heuristic_category_v42": row["heuristic_category"],
            "domain_guess": domain,
            "turn2_explicit_reference": explicit_2,
            "turn3_explicit_reference": explicit_3,
            "overlap_turn2_recomputed": overlap2,
            "overlap_turn3_recomputed": overlap3,
            "revision_keyword": revised,
            "clarification_keyword": clarified,
            "disagreement_keyword": disagreed,
            "possible_topic_switch": possible_switch,
            "factual_check_signal": needs_check,
            "review_priority": priority,
            "semantic_human_review_status": "UNREVIEWED",
            "semantic_human_review_decision": None,
            "factual_validation_complete": False,
            "training_approved": False,
            "messages_original": messages,
        })

    if categories != {
        "TWO_ANCHORED": 95,
        "PARTIAL_ANCHOR": 24,
        "LOW_LEXICAL_ANCHOR": 9,
    }:
        raise RuntimeError("V42 category counts changed")

    reviewed.sort(key=lambda r: (
        {"REVIEW_FIRST": 0, "REVIEW_SECOND": 1,
         "POSSIBLE_TOPIC_SWITCH": 2, "REVIEW_OPEN": 3}[r["review_priority"]],
        r["source_index"],
    ))
    # Sampling is deterministic and preserves every original message locally.
    rng = random.Random(43)
    samples = []
    for priority, quota in (
        ("REVIEW_FIRST", 8),
        ("REVIEW_SECOND", 4),
        ("POSSIBLE_TOPIC_SWITCH", 4),
        ("REVIEW_OPEN", 4),
    ):
        group = [r for r in reviewed if r["review_priority"] == priority]
        samples.extend(rng.sample(group, min(quota, len(group))))

    sample_lines = [
        "V43 LOCAL SOURCE REVIEW - NOT APPROVED FOR TRAINING",
        "Heuristic tags and lexical overlap are not semantic validation.",
        "Read each complete conversation and check factual accuracy.",
        "Manual decisions are NOT populated by this script.",
        "",
    ]
    for row in samples:
        sample_lines.append(
            f"=== INDEX {row['source_index']} | {row['review_priority']}"
            f" | {row['domain_guess']} ==="
        )
        for j, message in enumerate(row["messages_original"], 1):
            sample_lines.append(
                f"{j} {message['role'].upper()}:\n{message['content']}\n"
            )

    # All textual source material remains OUTSIDE the Git repository.
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    with QUEUE.open("x", encoding="utf-8") as stream:
        for record in reviewed:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    with SAMPLE.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(sample_lines) + "\n")

    # Only allowlisted integer aggregates are exposed for gogit_public.py.
    counts = {
        "TOTAL_CANDIDATS": len(reviewed),
        "TWO_ANCHORED": categories["TWO_ANCHORED"],
        "PARTIAL_ANCHOR": categories["PARTIAL_ANCHOR"],
        "LOW_LEXICAL_ANCHOR": categories["LOW_LEXICAL_ANCHOR"],
        "FOLLOWUP": flags["FOLLOWUP"],
        "REVISION": flags["REVISION"],
        "CLARIFICATION": flags["CLARIFICATION"],
        "DISAGREEMENT": flags["DISAGREEMENT"],
        "TOPIC_SWITCHES": flags["TOPIC_SWITCHES"],
        "FACTCHECK_PENDING": flags["FACTCHECK_PENDING"],
        **{k: domains[k] for k in (
            "CREATIVE", "PROGRAMMING", "MATHEMATICS", "WRITING",
            "FACTUAL_QA", "OTHER"
        )},
    }
    assert sum(domains.values()) == 128
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(counts.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
