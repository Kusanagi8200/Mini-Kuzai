#!/usr/bin/env python3
"""V46 public SmolTalk: creative-recall audit plus LOCAL semantic review queue.

This is a keyword triage, not a semantic, factual, or training-quality verdict.
Only explicitly allowlisted integer metrics are printed for gogit_public.py.
All complete conversations and review files remain OUTSIDE the Git repository.
"""

import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

ROOT = Path("/root/Mini-Kuzai/data/external/smol-smoltalk")
SOURCE = ROOT / "candidates/external-candidate-pool-v0.4.jsonl"
V44 = ROOT / "review/stratified-candidates-v44.jsonl"
REPORT44 = ROOT / "review/stratified-audit-v44.json"
QUEUE = ROOT / "review/v46-manual-review-queue.jsonl"
TEXT = ROOT / "review/v46-manual-review-readable.txt"
SUMMARY = ROOT / "review/v46-heuristic-summary.json"

CATEGORIES = (
    "FOLLOWUP", "WRITING", "CREATIVE", "FACTUAL_QA",
    "MATHEMATICS", "PROGRAMMING", "PRACTICAL_ADVICE", "GENERAL_OTHER",
)
# This deliberately casts a broader net than V44. It can produce FALSE
# positives: a reviewer, not the regex, decides whether examples are creative.
ACTION = re.compile(
    r"\b(?:imagine|invent|brainstorm|create|develop|write|compose|"
    r"describe|continue|finish|make up|come up with|reimagine|"
    r"turn into|transform into|what if)\b", re.I
)
ARTIFACT = re.compile(
    r"\b(?:story|stories|scene|scenes|poem|poetry|rhyme|lyrics|"
    r"song|character|characters|dialogue|fiction|fictional|"
    r"imaginary|fantasy|fairy tale|plot|narrative|novel|"
    r"alternate ending|screenplay|creative ideas|worldbuilding|"
    r"world-building)\b", re.I
)
EXPLICIT = re.compile(
    r"\b(?:plot twist|alternate ending|creative writing|"
    r"fictional world|storytelling|a short story|"
    r"a poem|dialogue between|creative brainstorming)\b", re.I
)


def broad_creative(messages):
    user = "\n".join(m["content"] for m in messages if m["role"] == "user")
    return bool(EXPLICIT.search(user) or (ACTION.search(user) and ARTIFACT.search(user)))


def stable_sample(items, count, label):
    return sorted(
        items,
        key=lambda r: hashlib.sha256(
            (label + ":" + r["sha"]).encode("ascii")
        ).hexdigest(),
    )[:count]


def write_exclusive(path, text):
    # Never replace a previous queue, and restrict source text to root.
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)


def main():
    if not all(p.is_file() for p in (SOURCE, V44, REPORT44)):
        raise RuntimeError("Missing local public-source inputs")
    if any(p.exists() for p in (QUEUE, TEXT, SUMMARY)):
        raise RuntimeError("V46 artifacts already exist; no overwrite")

    v44_report = json.loads(REPORT44.read_text(encoding="utf-8"))
    if (v44_report.get("step") != "PHASE03-SMOLTALK-V44"
        or v44_report.get("selected_records") != 1139
        or v44_report.get("training_approved") is not False
        or v44_report["selected_by_heuristic_category"].get("CREATIVE") != 69):
        raise RuntimeError("V44 reference audit mismatch")

    selected = {}
    selected_categories = Counter()
    with V44.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            r = json.loads(line)
            sha = r["source_content_sha256"]
            cat = r["heuristic_category"]
            if (sha in selected or cat not in CATEGORIES
                or r.get("training_approved") is not False
                or r.get("semantic_validation_complete") is not False):
                raise RuntimeError("Invalid V44 record")
            selected[sha] = r
            selected_categories[cat] += 1
    if (len(selected) != 1139
        or selected_categories != Counter(v44_report["selected_by_heuristic_category"])):
        raise RuntimeError("V44 selected inventory mismatch")

    all_source = {}
    source_counts = Counter()
    with SOURCE.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            r = json.loads(line)
            sha = r["content_sha256"]
            msgs = r["messages"]
            if (sha in all_source
                or not re.fullmatch(r"[0-9a-f]{64}", sha)
                or len(msgs) not in (2, 4, 6)
                or [m.get("role") for m in msgs] != ["user", "assistant"] * (len(msgs)//2)):
                raise RuntimeError("Invalid external source record")
            all_source[sha] = r
            source_counts[r["source"]] += 1
    if (len(all_source) != 8000 or source_counts != {
        "smol-magpie-ultra-short": 5000,
        "openhermes-50k": 1500,
        "self-oss-instruct": 1000,
        "explore-instruct-rewrite": 500,
    }):
        raise RuntimeError("Unexpected external-source distribution")

    by_category = {c: [] for c in CATEGORIES}
    candidates_outside = []
    candidates_inside_other = []
    broad_count = 0
    for sha, rec in all_source.items():
        sel = selected.get(sha)
        if sel and sel["messages"] != rec["messages"]:
            raise RuntimeError("V44 source conversation changed")
        flagged = broad_creative(rec["messages"])
        if flagged:
            broad_count += 1
        row = {
            "sha": sha,
            "dataset_source": rec["source"],
            "v44_selected": sel is not None,
            "v44_category": sel["heuristic_category"] if sel else None,
            "broad_creative_signal": flagged,
            "messages": rec["messages"],
        }
        if sel:
            by_category[sel["heuristic_category"]].append(row)
            if flagged and sel["heuristic_category"] != "CREATIVE":
                candidates_inside_other.append(row)
        elif flagged:
            candidates_outside.append(row)

    if sum(map(len, by_category.values())) != 1139:
        raise RuntimeError("V44 selection differs from external source")

    queue = []
    seen = set()
    counts = Counter()

    def append_rows(rows, reason):
        for r in rows:
            if r["sha"] in seen:
                continue
            seen.add(r["sha"])
            counts[reason] += 1
            queue.append({
                "source_content_sha256": r["sha"],
                "source_dataset": r["dataset_source"],
                "v44_selected": r["v44_selected"],
                "v44_category": r["v44_category"],
                "broad_creative_signal": r["broad_creative_signal"],
                "review_queue_reason": reason,
                "messages_original": r["messages"],
                "review_decision": "UNREVIEWED",
                "semantic_validation_complete": False,
                "factual_validation_complete": False,
                "training_approved": False,
                "dataset_split_assigned": False,
            })

    # Stratified baseline: no inference of semantic acceptance.
    for cat in CATEGORIES:
        append_rows(stable_sample(by_category[cat], 4, "V46-BASE-"+cat), "BASE")
    # Suspected false negatives INSIDE V44: review category boundaries.
    append_rows(stable_sample(candidates_inside_other, 12, "V46-RELABEL"), "RELABEL")
    # Suspected false negatives OUTSIDE V44: review possible additions.
    append_rows(stable_sample(candidates_outside, 24, "V46-RESCUE"), "RESCUE")

    if not queue or any(r["training_approved"] for r in queue):
        raise RuntimeError("Invalid candidate queue")
    summary = {
        "step": "PHASE03-SMOLTALK-V46",
        "source_records": 8000,
        "v44_selected": 1139,
        "v44_creative_labelled": 69,
        "broad_creative_signal_all": broad_count,
        "broad_creative_signal_v44_noncreative": len(candidates_inside_other),
        "broad_creative_signal_unselected": len(candidates_outside),
        "manual_review_queue_by_reason": dict(counts),
        "manual_review_queue_total": len(queue),
        "review_complete": False,
        "semantic_validation_complete": False,
        "training_approved": False,
        "interpretation": (
            "Broad regex signals are candidate discovery only; manual decisions "
            "must be recorded separately. V44 selected records are not modified."
        ),
    }
    readable = [
        "V46 - LOCAL HUMAN SEMANTIC REVIEW - PRIVATE WORKSPACE ONLY",
        "External public SmolTalk conversation contents: do not publish these files.",
        "Labels are hypotheses, not manual decisions or fact checks.",
        "Review continuity, creativity, coherence, factual accuracy and split risks.",
        "",
    ]
    for row in queue:
        readable.append(
            "=== {} | SOURCE {} | V44 {} ===".format(
                row["review_queue_reason"], row["source_dataset"],
                row["v44_category"] or "NOT_SELECTED"
            )
        )
        for m in row["messages_original"]:
            readable.append(m["role"].upper() + ": " + m["content"] + "\n")

    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    write_exclusive(QUEUE, "".join(
        json.dumps(row, ensure_ascii=False) + "\n" for row in queue
    ))
    write_exclusive(TEXT, "\n".join(readable) + "\n")
    write_exclusive(SUMMARY, json.dumps(summary, indent=2) + "\n")

    metrics = {
        "TOTAL_SOURCE": 8000,
        "TOTAL_CANDIDATS": 1139,
        "CREATIVE_AVAILABLE": 69,
        "V46_BROAD_CREATIVE_ALL": broad_count,
        "V46_BROAD_CREATIVE_UNSELECTED": len(candidates_outside),
        "V46_BROAD_CREATIVE_SELECTED_OTHER": len(candidates_inside_other),
        "V46_REVIEW_BASE": counts["BASE"],
        "V46_REVIEW_RECLASS": counts["RELABEL"],
        "V46_REVIEW_RESCUE": counts["RESCUE"],
        "V46_REVIEW_TOTAL": len(queue),
    }
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
