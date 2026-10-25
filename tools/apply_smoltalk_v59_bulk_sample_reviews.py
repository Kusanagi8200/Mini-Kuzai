#!/usr/bin/env python3
"""Apply the reviewed V59 bulk-sample decisions and publish one Git commit."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "reviews" / "smoltalk-v59-bulk-sample-001"
CASES = ROOT / "cases"
DECISIONS = ROOT / "DECISIONS-001.json"
README = ROOT / "README.md"
RESULTS = ROOT / "RESULTS-001.md"
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"


def git(*args):
    process = subprocess.run(
        ["git", "-C", str(REPO), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(
            "Git command failed: " + process.stderr.strip()
        )
    return process.stdout.strip()


def preflight():
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Expected branch main")
    if git("status", "--porcelain"):
        raise RuntimeError("Clean worktree required")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local and remote main differ")
    if RESULTS.exists() or RESULTS.is_symlink():
        raise RuntimeError("RESULTS-001.md already exists")


def field(text, name):
    match = re.search(
        rf"^{re.escape(name)}: (.+)$",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError(f"Missing field {name}")
    return match.group(1).strip()


def main():
    preflight()

    data = json.loads(
        DECISIONS.read_text(encoding="utf-8")
    )

    if (
        data.get("status") != "REVIEW_COMPLETE_PENDING_APPLICATION"
        or data.get("sample_size") != 72
        or data.get("population") != 1080
        or data.get("training_authorized") is not False
    ):
        raise RuntimeError("Unexpected V59 decision manifest state")

    decisions = data.get("decisions")
    if not isinstance(decisions, list) or len(decisions) != 72:
        raise RuntimeError("Expected exactly 72 decisions")

    grades = Counter()
    risks = Counter()
    fits = Counter()
    persona = Counter()
    dispositions = Counter()
    by_priority = {
        "HIGH": Counter(),
        "MEDIUM": Counter(),
        "LOW": Counter(),
    }
    changed = []

    for expected_case, decision in enumerate(decisions, 1):
        if decision.get("case") != expected_case:
            raise RuntimeError("Decision ordering changed")

        path = REPO / decision["path"]
        if (
            not path.is_file()
            or path.is_symlink()
            or path.parent != CASES
        ):
            raise RuntimeError(f"Unsafe or missing case page: {path}")

        text = path.read_text(encoding="utf-8")

        required = (
            "V59 grade: PENDING",
            "V59 factual risk: PENDING",
            "V59 instruction fit: PENDING",
            "V59 persona value: PENDING",
            "V59 disposition: PENDING",
            "V59 rationale: NOT_REVIEWED",
        )
        for value in required:
            if value not in text:
                raise RuntimeError(
                    f"Unexpected review state in {path.name}: {value}"
                )

        grade = decision["grade"]
        risk = decision["factual_risk"]
        fit = decision["instruction_fit"]
        persona_value = decision["persona_value"]
        disposition = decision["disposition"]
        rationale = decision["rationale"]

        if grade not in {"A", "B", "C"}:
            raise RuntimeError("Invalid grade")
        if risk not in {"LOW", "REVIEW", "HIGH"}:
            raise RuntimeError("Invalid factual risk")
        if fit not in {"GOOD", "PARTIAL", "BAD"}:
            raise RuntimeError("Invalid instruction fit")
        if persona_value not in {"HIGH", "MEDIUM", "LOW"}:
            raise RuntimeError("Invalid persona value")
        if disposition not in {"KEEP", "REPAIR", "EXCLUDE"}:
            raise RuntimeError("Invalid disposition")
        if not isinstance(rationale, str) or len(rationale) < 24:
            raise RuntimeError("Invalid rationale")

        if (
            grade == "A" and disposition != "KEEP"
            or grade == "B" and disposition != "REPAIR"
            or grade == "C" and disposition != "EXCLUDE"
        ):
            raise RuntimeError("Grade/disposition mismatch")

        priority = field(text, "V50 priority hint")
        if priority not in by_priority:
            raise RuntimeError("Unexpected V50 priority")

        text = (
            text
            .replace("V59 grade: PENDING", f"V59 grade: {grade}", 1)
            .replace("V59 factual risk: PENDING", f"V59 factual risk: {risk}", 1)
            .replace("V59 instruction fit: PENDING", f"V59 instruction fit: {fit}", 1)
            .replace("V59 persona value: PENDING", f"V59 persona value: {persona_value}", 1)
            .replace("V59 disposition: PENDING", f"V59 disposition: {disposition}", 1)
            .replace("V59 rationale: NOT_REVIEWED", f"V59 rationale: {rationale}", 1)
        )

        path.write_text(text, encoding="utf-8")
        changed.append(str(path.relative_to(REPO)))

        grades[grade] += 1
        risks[risk] += 1
        fits[fit] += 1
        persona[persona_value] += 1
        dispositions[disposition] += 1
        by_priority[priority][disposition] += 1

    expected = {
        "grades": {"A": 36, "B": 19, "C": 17},
        "risks": {"LOW": 46, "REVIEW": 8, "HIGH": 18},
        "fits": {"GOOD": 58, "PARTIAL": 5, "BAD": 9},
        "persona": {"HIGH": 14, "MEDIUM": 18, "LOW": 40},
        "dispositions": {"KEEP": 36, "REPAIR": 19, "EXCLUDE": 17},
        "high": {"KEEP": 6, "REPAIR": 7, "EXCLUDE": 2},
        "medium": {"KEEP": 12, "REPAIR": 9, "EXCLUDE": 5},
        "low": {"KEEP": 18, "REPAIR": 3, "EXCLUDE": 10},
    }

    if dict(grades) != expected["grades"]:
        raise RuntimeError("Grade totals changed")
    if dict(risks) != expected["risks"]:
        raise RuntimeError("Risk totals changed")
    if dict(fits) != expected["fits"]:
        raise RuntimeError("Instruction-fit totals changed")
    if dict(persona) != expected["persona"]:
        raise RuntimeError("Persona totals changed")
    if dict(dispositions) != expected["dispositions"]:
        raise RuntimeError("Disposition totals changed")
    if dict(by_priority["HIGH"]) != expected["high"]:
        raise RuntimeError("HIGH totals changed")
    if dict(by_priority["MEDIUM"]) != expected["medium"]:
        raise RuntimeError("MEDIUM totals changed")
    if dict(by_priority["LOW"]) != expected["low"]:
        raise RuntimeError("LOW totals changed")

    results = """# Mini-Kuzai V59 - bulk quality sample 001 results

Status: **72/72 public SmolTalk cases semantically reviewed.**

This is a deliberately stratified quality sample from the 1,080 previously
unreviewed members of the V59 candidate population. Raw sample percentages
must not be interpreted as a population acceptance estimate without
stratum weighting.

## Review outcomes

| Dimension | Counts |
| --- | --- |
| Grade | A 36 / B 19 / C 17 |
| Disposition | KEEP 36 / REPAIR 19 / EXCLUDE 17 |
| Factual risk | LOW 46 / REVIEW 8 / HIGH 18 |
| Instruction fit | GOOD 58 / PARTIAL 5 / BAD 9 |
| Persona value | HIGH 14 / MEDIUM 18 / LOW 40 |

## By V50 heuristic priority

| Priority | KEEP | REPAIR | EXCLUDE | Total |
| --- | ---: | ---: | ---: | ---: |
| HIGH | 6 | 7 | 2 | 15 |
| MEDIUM | 12 | 9 | 5 | 26 |
| LOW | 18 | 3 | 10 | 31 |
| **Total** | **36** | **19** | **17** | **72** |

## Interpretation

The sample confirms that V50 HIGH/MEDIUM/LOW is not a quality grade.
Useful and clean cases exist in every priority band, while material
factual, logical, technical, role-boundary and instruction-following
defects also occur across the candidate population.

KEEP means usable unchanged within this review.
REPAIR means useful behavior exists but the source should not be used
unchanged as a supervised-positive target.
EXCLUDE means the reviewed source is unsuitable unchanged.

This result does not authorize the remaining 1,080-case population,
does not finalize the V59 training mix, and does not authorize model training.

Training authorized: **NO**.
"""

    RESULTS.write_text(results, encoding="utf-8")
    changed.append(str(RESULTS.relative_to(REPO)))

    readme = README.read_text(encoding="utf-8")
    old = "Status: 72-case deterministic public SmolTalk review sample."
    new = (
        "Status: **REVIEW COMPLETE - 72/72 cases.** "
        "See [RESULTS-001.md](RESULTS-001.md)."
    )
    if old not in readme:
        raise RuntimeError("README status marker changed")
    README.write_text(
        readme.replace(old, new, 1),
        encoding="utf-8",
    )
    changed.append(str(README.relative_to(REPO)))

    data["status"] = "REVIEW_APPLIED"
    data["summary"] = {
        "grade_a": 36,
        "grade_b": 19,
        "grade_c": 17,
        "keep": 36,
        "repair": 19,
        "exclude": 17,
        "factual_low": 46,
        "factual_review": 8,
        "factual_high": 18,
        "instruction_good": 58,
        "instruction_partial": 5,
        "instruction_bad": 9,
        "persona_high": 14,
        "persona_medium": 18,
        "persona_low": 40,
    }
    DECISIONS.write_text(
        json.dumps(data, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    changed.append(str(DECISIONS.relative_to(REPO)))

    git("add", "--", *changed)
    staged = set(git("diff", "--cached", "--name-only").splitlines())
    if staged != set(changed):
        raise RuntimeError("Unexpected staged paths")
    git("diff", "--cached", "--check")

    git(
        "commit",
        "-m",
        "V59: apply bulk sample 001 semantic review",
    )
    git("push", "origin", "main")
    git("fetch", "--quiet", "origin", "main")

    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Push verification failed")

    print(MARKER)
    print("V59_BULK_SAMPLE_REVIEWED: 72")
    print("V59_BULK_SAMPLE_KEEP: 36")
    print("V59_BULK_SAMPLE_REPAIR: 19")
    print("V59_BULK_SAMPLE_EXCLUDE: 17")
    print("V59_BULK_SAMPLE_FACTUAL_HIGH: 18")
    print("V59_BULK_SAMPLE_INSTRUCTION_BAD: 9")
    print("V59_MIX_FINALIZED: 0")
    print("TRAINING_AUTHORIZED: 0")
    print("GIT_HEAD:", git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    main()
