#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from collections import Counter
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/"reviews"/"smoltalk-v59-independent-holdout-004"
CASES=ROOT/"cases"; DECISIONS=ROOT/"DECISIONS-004.json"; README=ROOT/"README.md"; RESULTS=ROOT/"RESULTS-004.md"
ALLOWED_TAGS={"NONE","ROLE_CONTAMINATION","FACTUAL_ERROR","LOGICAL_ERROR","TECHNICAL_ERROR","INSTRUCTION_FAILURE","TIME_SENSITIVE","STYLE_QUALITY","OTHER"}

def git(*args):
    p=subprocess.run(["git","-C",str(REPO),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode:
        detail="\n".join(x for x in (p.stdout.strip(),p.stderr.strip()) if x)
        raise RuntimeError("Git command failed: "+(detail or str(p.returncode)))
    return p.stdout.strip()

def main():
    if git("branch","--show-current")!="main": raise RuntimeError("Expected branch main")
    if git("status","--porcelain"): raise RuntimeError("Clean worktree required")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Local and remote main differ")
    if RESULTS.exists() or RESULTS.is_symlink(): raise RuntimeError("RESULTS-004.md already exists")
    if not DECISIONS.is_file() or DECISIONS.is_symlink(): raise RuntimeError("DECISIONS-004.json not published")

    data=json.loads(DECISIONS.read_text(encoding="utf-8"))
    if data.get("status")!="REVIEW_COMPLETE_PENDING_APPLICATION" or data.get("sample_id")!="smoltalk-v59-independent-holdout-004" or data.get("sample_size")!=72 or data.get("training_authorized") is not False:
        raise RuntimeError("Unexpected decision manifest state")
    decisions=data.get("decisions")
    if not isinstance(decisions,list) or len(decisions)!=72: raise RuntimeError("Expected 72 decisions")

    counts=Counter(); tags=Counter(); changed=[]
    for expected,d in enumerate(decisions,1):
        if d.get("case")!=expected: raise RuntimeError("Decision ordering changed")
        path=REPO/d["path"]
        if not path.is_file() or path.is_symlink() or path.parent!=CASES: raise RuntimeError("Unsafe or missing case page")
        text=path.read_text(encoding="utf-8")
        required=("V59 grade: PENDING","V59 factual risk: PENDING","V59 instruction fit: PENDING","V59 persona value: PENDING","V59 disposition: PENDING","V59 defect tags: PENDING","V59 rationale: NOT_REVIEWED")
        if any(x not in text for x in required): raise RuntimeError(f"Unexpected page state: {path.name}")
        grade=d["grade"]; risk=d["factual_risk"]; fit=d["instruction_fit"]; persona=d["persona_value"]; disp=d["disposition"]; rationale=d["rationale"]; defect_tags=d["defect_tags"]
        if grade not in {"A","B","C"} or risk not in {"LOW","REVIEW","HIGH"} or fit not in {"GOOD","PARTIAL","BAD"} or persona not in {"HIGH","MEDIUM","LOW"} or disp not in {"KEEP","REPAIR","EXCLUDE"}:
            raise RuntimeError("Invalid review value")
        if (grade=="A" and disp!="KEEP") or (grade=="B" and disp!="REPAIR") or (grade=="C" and disp!="EXCLUDE"): raise RuntimeError("Grade/disposition mismatch")
        if not isinstance(defect_tags,list) or not defect_tags or set(defect_tags)-ALLOWED_TAGS: raise RuntimeError("Invalid defect tags")
        if disp=="KEEP" and set(defect_tags)!={"NONE"}: raise RuntimeError("KEEP must use NONE")
        if disp!="KEEP" and "NONE" in defect_tags: raise RuntimeError("Non-KEEP cannot use NONE")
        if not isinstance(rationale,str) or len(rationale)<24: raise RuntimeError("Invalid rationale")
        tag_text=",".join(sorted(set(defect_tags)))
        text=(text.replace("V59 grade: PENDING",f"V59 grade: {grade}",1)
                  .replace("V59 factual risk: PENDING",f"V59 factual risk: {risk}",1)
                  .replace("V59 instruction fit: PENDING",f"V59 instruction fit: {fit}",1)
                  .replace("V59 persona value: PENDING",f"V59 persona value: {persona}",1)
                  .replace("V59 disposition: PENDING",f"V59 disposition: {disp}",1)
                  .replace("V59 defect tags: PENDING",f"V59 defect tags: {tag_text}",1)
                  .replace("V59 rationale: NOT_REVIEWED",f"V59 rationale: {rationale}",1))
        path.write_text(text,encoding="utf-8"); changed.append(str(path.relative_to(REPO)))
        counts[disp]+=1
        for tag in set(defect_tags): tags[tag]+=1

    if sum(counts.values())!=72: raise RuntimeError("Disposition accounting changed")
    lines=["# Mini-Kuzai V59 - independent holdout 004 results","","Status: **72/72 cases semantically reviewed and applied.**","",
      "This holdout was selected independently of model score and reviewed with model scores blinded.","",
      "## Semantic outcomes","",f"- KEEP: {counts['KEEP']}",f"- REPAIR: {counts['REPAIR']}",f"- EXCLUDE: {counts['EXCLUDE']}","","## Defect tags",""]
    for tag in sorted(tags): lines.append(f"- {tag}: {tags[tag]}")
    lines+=["","These counts are semantic labels only. Ranking metrics are produced separately by the frozen 216-label retrain audit.","Training remains NOT AUTHORIZED.",""]
    RESULTS.write_text("\n".join(lines),encoding="utf-8"); changed.append(str(RESULTS.relative_to(REPO)))

    readme=README.read_text(encoding="utf-8")
    old="Status: **PUBLISHED FOR BLINDED SEMANTIC REVIEW - 72 cases.**"
    new="Status: **REVIEW COMPLETE - 72/72 cases.** See [RESULTS-004.md](RESULTS-004.md)."
    if old not in readme: raise RuntimeError("README status marker changed")
    README.write_text(readme.replace(old,new,1),encoding="utf-8"); changed.append(str(README.relative_to(REPO)))

    data["status"]="REVIEW_APPLIED"
    data["summary"]={"keep":counts["KEEP"],"repair":counts["REPAIR"],"exclude":counts["EXCLUDE"],"defect_tags":dict(sorted(tags.items()))}
    DECISIONS.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8"); changed.append(str(DECISIONS.relative_to(REPO)))

    git("add","--",*changed)
    if set(git("diff","--cached","--name-only").splitlines())!=set(changed): raise RuntimeError("Unexpected staged paths")
    git("diff","--cached","--check"); git("commit","-m","V59: apply independent holdout 004 review"); git("push","origin","main")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Push verification failed")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V59_HOLDOUT004_REVIEWED: 72"); print("V59_HOLDOUT004_KEEP:",counts["KEEP"]); print("V59_HOLDOUT004_REPAIR:",counts["REPAIR"]); print("V59_HOLDOUT004_EXCLUDE:",counts["EXCLUDE"])
    print("TRAINING_AUTHORIZED: 0"); print("GIT_HEAD:",git("rev-parse","--short","HEAD"))

if __name__=="__main__": main()
