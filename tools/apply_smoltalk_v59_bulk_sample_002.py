#!/usr/bin/env python3
"""Apply reviewed decisions for V59 bulk sample 002 and publish one commit."""

from __future__ import annotations
import json, subprocess
from collections import Counter
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/"reviews"/"smoltalk-v59-bulk-sample-002"
CASES=ROOT/"cases"
DECISIONS=ROOT/"DECISIONS-002.json"
README=ROOT/"README.md"
RESULTS=ROOT/"RESULTS-002.md"
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
ALLOWED_TAGS={"NONE","ROLE_CONTAMINATION","FACTUAL_ERROR","LOGICAL_ERROR","TECHNICAL_ERROR","INSTRUCTION_FAILURE","TIME_SENSITIVE","STYLE_QUALITY","OTHER"}

def git(*args):
    p=subprocess.run(["git","-C",str(REPO),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode: raise RuntimeError("Git command failed: "+p.stderr.strip())
    return p.stdout.strip()

def preflight():
    if git("branch","--show-current")!="main": raise RuntimeError("Expected branch main")
    if git("status","--porcelain"): raise RuntimeError("Clean worktree required")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Local and remote main differ")
    if RESULTS.exists() or RESULTS.is_symlink(): raise RuntimeError("RESULTS-002.md already exists")
    if not DECISIONS.is_file() or DECISIONS.is_symlink(): raise RuntimeError("DECISIONS-002.json not published")

def main():
    preflight()
    data=json.loads(DECISIONS.read_text(encoding="utf-8"))
    if (data.get("status")!="REVIEW_COMPLETE_PENDING_APPLICATION" or data.get("sample_id")!="smoltalk-v59-bulk-sample-002"
        or data.get("sample_size")!=72 or data.get("population")!=1080 or data.get("training_authorized") is not False):
        raise RuntimeError("Unexpected decision manifest state")
    decisions=data.get("decisions")
    if not isinstance(decisions,list) or len(decisions)!=72: raise RuntimeError("Expected 72 decisions")

    counts=Counter(); risks=Counter(); fits=Counter(); persona=Counter(); tags=Counter(); changed=[]
    for expected_case,decision in enumerate(decisions,1):
        if decision.get("case")!=expected_case: raise RuntimeError("Decision ordering changed")
        path=REPO/decision["path"]
        if not path.is_file() or path.is_symlink() or path.parent!=CASES: raise RuntimeError("Unsafe or missing case page")
        text=path.read_text(encoding="utf-8")
        required=("V59 grade: PENDING","V59 factual risk: PENDING","V59 instruction fit: PENDING",
                  "V59 persona value: PENDING","V59 disposition: PENDING","V59 defect tags: PENDING","V59 rationale: NOT_REVIEWED")
        if any(value not in text for value in required): raise RuntimeError(f"Unexpected page state: {path.name}")

        grade=decision["grade"]; risk=decision["factual_risk"]; fit=decision["instruction_fit"]; pvalue=decision["persona_value"]
        disposition=decision["disposition"]; rationale=decision["rationale"]; defect_tags=decision["defect_tags"]
        if grade not in {"A","B","C"} or risk not in {"LOW","REVIEW","HIGH"} or fit not in {"GOOD","PARTIAL","BAD"}:
            raise RuntimeError("Invalid review value")
        if pvalue not in {"HIGH","MEDIUM","LOW"} or disposition not in {"KEEP","REPAIR","EXCLUDE"}: raise RuntimeError("Invalid review value")
        if (grade=="A" and disposition!="KEEP") or (grade=="B" and disposition!="REPAIR") or (grade=="C" and disposition!="EXCLUDE"):
            raise RuntimeError("Grade/disposition mismatch")
        if not isinstance(defect_tags,list) or not defect_tags or set(defect_tags)-ALLOWED_TAGS: raise RuntimeError("Invalid defect tags")
        if disposition=="KEEP" and set(defect_tags)!={"NONE"}: raise RuntimeError("KEEP must use NONE")
        if disposition!="KEEP" and "NONE" in defect_tags: raise RuntimeError("Non-KEEP cannot use NONE")
        if not isinstance(rationale,str) or len(rationale)<24: raise RuntimeError("Invalid rationale")

        tag_text=",".join(sorted(set(defect_tags)))
        text=(text.replace("V59 grade: PENDING",f"V59 grade: {grade}",1)
                  .replace("V59 factual risk: PENDING",f"V59 factual risk: {risk}",1)
                  .replace("V59 instruction fit: PENDING",f"V59 instruction fit: {fit}",1)
                  .replace("V59 persona value: PENDING",f"V59 persona value: {pvalue}",1)
                  .replace("V59 disposition: PENDING",f"V59 disposition: {disposition}",1)
                  .replace("V59 defect tags: PENDING",f"V59 defect tags: {tag_text}",1)
                  .replace("V59 rationale: NOT_REVIEWED",f"V59 rationale: {rationale}",1))
        path.write_text(text,encoding="utf-8"); changed.append(str(path.relative_to(REPO)))
        counts[disposition]+=1; risks[risk]+=1; fits[fit]+=1; persona[pvalue]+=1
        for tag in set(defect_tags): tags[tag]+=1

    if sum(counts.values())!=72: raise RuntimeError("Disposition accounting changed")

    lines=["# Mini-Kuzai V59 - bulk quality sample 002 results","","Status: **72/72 cases reviewed and applied.**","",
           "## Review outcomes","","| Dimension | Counts |","| --- | --- |",
           f"| Disposition | KEEP {counts['KEEP']} / REPAIR {counts['REPAIR']} / EXCLUDE {counts['EXCLUDE']} |",
           f"| Factual risk | LOW {risks['LOW']} / REVIEW {risks['REVIEW']} / HIGH {risks['HIGH']} |",
           f"| Instruction fit | GOOD {fits['GOOD']} / PARTIAL {fits['PARTIAL']} / BAD {fits['BAD']} |",
           f"| Persona value | HIGH {persona['HIGH']} / MEDIUM {persona['MEDIUM']} / LOW {persona['LOW']} |",
           "","## Defect tags",""]
    for tag in sorted(tags): lines.append(f"- {tag}: {tags[tag]}")
    lines += ["","Sample 002 is combined with Sample 001 by the V59 cumulative weighted audit.","Training remains NOT AUTHORIZED.",""]
    RESULTS.write_text("\n".join(lines),encoding="utf-8"); changed.append(str(RESULTS.relative_to(REPO)))

    readme=README.read_text(encoding="utf-8")
    old="Status: **PUBLISHED FOR REVIEW - 72 new cases.**"
    new="Status: **REVIEW COMPLETE - 72/72 cases.** See [RESULTS-002.md](RESULTS-002.md)."
    if old not in readme: raise RuntimeError("README status marker changed")
    README.write_text(readme.replace(old,new,1),encoding="utf-8"); changed.append(str(README.relative_to(REPO)))

    data["status"]="REVIEW_APPLIED"
    data["summary"]={"keep":counts["KEEP"],"repair":counts["REPAIR"],"exclude":counts["EXCLUDE"],
                     "factual_high":risks["HIGH"],"instruction_bad":fits["BAD"],"persona_high":persona["HIGH"],
                     "defect_tags":dict(sorted(tags.items()))}
    DECISIONS.write_text(json.dumps(data,indent=2,ensure_ascii=True,sort_keys=True)+"\n",encoding="utf-8")
    changed.append(str(DECISIONS.relative_to(REPO)))

    git("add","--",*changed)
    if set(git("diff","--cached","--name-only").splitlines())!=set(changed): raise RuntimeError("Unexpected staged paths")
    git("diff","--cached","--check"); git("commit","-m","V59: apply bulk sample 002 semantic review"); git("push","origin","main")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Push verification failed")
    print(MARKER); print("V59_SAMPLE_002_REVIEWED: 72"); print("V59_SAMPLE_002_KEEP:",counts["KEEP"])
    print("V59_SAMPLE_002_REPAIR:",counts["REPAIR"]); print("V59_SAMPLE_002_EXCLUDE:",counts["EXCLUDE"])
    print("TRAINING_AUTHORIZED: 0"); print("GIT_HEAD:",git("rev-parse","--short","HEAD"))

if __name__=="__main__": main()
