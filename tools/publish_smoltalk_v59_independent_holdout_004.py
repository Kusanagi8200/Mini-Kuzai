#!/usr/bin/env python3
from __future__ import annotations
import hashlib, html, importlib.util, json, shutil, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
TRIAGE_PATH=REPO/"tools"/"phase03_v59_supervised_triage.py"
DEST=REPO/"reviews"/"smoltalk-v59-independent-holdout-004"
PUBLIC_REVIEW_ROOT=Path("/root/Mini-Kuzai/data/external/smol-smoltalk/review")
SAMPLE_SIZE=72
MANIFESTS=[
 REPO/"reviews"/"smoltalk-v59-bulk-sample-001"/"DECISIONS-001.json",
 REPO/"reviews"/"smoltalk-v59-bulk-sample-002"/"DECISIONS-002.json",
 REPO/"reviews"/"smoltalk-v59-active-sample-003"/"DECISIONS-003.json"]
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError("module load failed")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module
TRIAGE=load("v59_holdout004_triage",TRIAGE_PATH)

def git(*args):
    p=subprocess.run(["git","-C",str(REPO),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode:
        detail="\n".join(x for x in (p.stdout.strip(),p.stderr.strip()) if x)
        raise RuntimeError("Git command failed: "+(detail or str(p.returncode)))
    return p.stdout.strip()

def source_sha(path):
    text=path.read_text(encoding="utf-8")
    import re
    m=re.search(r"^Public content SHA-256: (.+)$",text,re.M)
    if m is None: raise RuntimeError("missing source sha")
    return m.group(1).strip()

def labels216():
    out={}
    for manifest in MANIFESTS:
        data=json.loads(manifest.read_text(encoding="utf-8"))
        decisions=data.get("decisions")
        if not isinstance(decisions,list) or len(decisions)!=72: raise RuntimeError("review manifest changed")
        for d in decisions:
            sha=source_sha(REPO/d["path"])
            if sha in out: raise RuntimeError("duplicate reviewed source")
            out[sha]=d["disposition"]
    if len(out)!=216: raise RuntimeError("expected 216 reviewed labels")
    return out

def stable_rank(sha):
    return hashlib.sha256(("v59-independent-holdout-004:"+sha).encode()).hexdigest()

def allocation(groups):
    total=sum(len(v) for v in groups.values())
    if total!=864: raise RuntimeError("expected 864 never-reviewed candidates")
    keys=sorted(groups)
    quota={k:SAMPLE_SIZE*len(groups[k])/total for k in keys}
    target={k:int(quota[k]) for k in keys}
    for k in keys:
        if target[k]==0 and groups[k]: target[k]=1
    while sum(target.values())<SAMPLE_SIZE:
        candidates=[k for k in keys if target[k]<len(groups[k])]
        k=max(candidates,key=lambda x:(quota[x]-int(quota[x]),len(groups[x]),str(x)))
        target[k]+=1
        quota[k]=-1
    while sum(target.values())>SAMPLE_SIZE:
        candidates=[k for k in keys if target[k]>1]
        k=max(candidates,key=lambda x:(target[x]-SAMPLE_SIZE*len(groups[x])/total,-len(groups[x]),str(x)))
        target[k]-=1
    return target

def select():
    reviewed=labels216(); pop=TRIAGE.BASE.eligible_population()
    if len(pop)!=1080: raise RuntimeError("eligible population changed")
    remaining=[r for r in pop if r["sha"] not in reviewed]
    if len(remaining)!=864: raise RuntimeError("remaining population changed")
    groups=defaultdict(list)
    for row in remaining:
        key=(row["priority_hint"],row["source_dataset"],row["turn_bucket"])
        groups[key].append(row)
    targets=allocation(groups)
    selected=[]
    for key in sorted(groups):
        rows=sorted(groups[key],key=lambda r:stable_rank(r["sha"]))
        selected.extend(rows[:targets[key]])
    selected=sorted(selected,key=lambda r:stable_rank(r["sha"]))
    if len(selected)!=SAMPLE_SIZE or len({r["sha"] for r in selected})!=SAMPLE_SIZE: raise RuntimeError("holdout selection mismatch")
    return selected,targets

def esc(value):
    safe=html.escape(value,quote=True).replace("\r","&#13;")
    return "\n".join(line.rstrip(" \t")+line[len(line.rstrip(" \t")):].replace(" ","&#32;").replace("\t","&#9;") for line in safe.split("\n"))

def page(index,row):
    parts=[f"# V59 independent holdout 004 review {index:02d}/72","",
      "V59 grade: PENDING","V59 factual risk: PENDING","V59 instruction fit: PENDING","V59 persona value: PENDING",
      "V59 disposition: PENDING","V59 defect tags: PENDING","V59 rationale: NOT_REVIEWED","",
      "Holdout policy: selected independently of retrained model score.",
      "Model score: BLINDED DURING SEMANTIC REVIEW.",
      f"V50 priority hint: {row['priority_hint']}",f"V44 heuristic category: {row['heuristic_category']}",
      f"Turn bucket: {row['turn_bucket']}",f"Public external subset: {row['source_dataset']}",
      f"Public content SHA-256: {row['sha']}","","## Public external source dialogue","",
      "Source: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk",""]
    for turn,m in enumerate(row["messages"],1):
        parts += [f"### Turn {turn} - {m['role'].upper()}","","<pre>",esc(m["content"]),"</pre>",""]
    parts += ["## Review rubric","",
      "- Grade A / KEEP: coherent positive target unchanged.",
      "- Grade B / REPAIR: useful signal, but repair before positive supervision.",
      "- Grade C / EXCLUDE: unsuitable unchanged.",
      "- Factual risk: LOW / REVIEW / HIGH.",
      "- Instruction fit: GOOD / PARTIAL / BAD.",
      "- Persona value: HIGH / MEDIUM / LOW.",
      "- Defect tags: NONE, ROLE_CONTAMINATION, FACTUAL_ERROR, LOGICAL_ERROR, TECHNICAL_ERROR, INSTRUCTION_FAILURE, TIME_SENSITIVE, STYLE_QUALITY, OTHER.",
      "","Review the dialogue semantically without access to the retrained model score.",""]
    return "\n".join(parts)

def model_fingerprint(labels):
    payload="\n".join(f"{sha}:{labels[sha]}" for sha in sorted(labels))
    return hashlib.sha256(("mnb-role-unigram-bigram-v2\n"+payload).encode()).hexdigest()

def preflight():
    if git("branch","--show-current")!="main": raise RuntimeError("Expected branch main")
    if git("status","--porcelain"): raise RuntimeError("Clean worktree required")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Local and remote main differ")
    if DEST.exists() or DEST.is_symlink(): raise RuntimeError("Holdout 004 already exists")

def main():
    preflight(); selected,targets=select(); labels=labels216()
    with tempfile.TemporaryDirectory(prefix="v59-holdout004-",dir=PUBLIC_REVIEW_ROOT) as scratch:
        draft=Path(scratch)/"smoltalk-v59-independent-holdout-004"; cases=draft/"cases"; cases.mkdir(parents=True)
        lines=["# Mini-Kuzai V59 - independent holdout 004","","Status: **PUBLISHED FOR BLINDED SEMANTIC REVIEW - 72 cases.**","",
          "This holdout is selected from 864 never-reviewed V59 candidates.",
          "Selection is deterministic and stratified by priority x public source x turn bucket.",
          "Selection does not use the retrained model score.",
          "Model scores are intentionally absent from review pages and sampling plan.","",
          "The holdout is for independent ranking validation, not training.","","## Review cases","",
          "| Case | Priority | Source | Turns | Category | Review |","| ---: | --- | --- | --- | --- | --- |"]
        plan=[]
        for i,row in enumerate(selected,1):
            filename=f"{i:02d}-{row['sha'][:16]}.md"
            (cases/filename).write_text(page(i,row),encoding="utf-8")
            lines.append("| {} | {} | {} | {} | {} | [Review](cases/{}) |".format(i,row["priority_hint"],row["source_dataset"],row["turn_bucket"],row["heuristic_category"],filename))
            plan.append({"case":i,"path":"reviews/smoltalk-v59-independent-holdout-004/cases/"+filename,"sha":row["sha"],
                         "priority":row["priority_hint"],"source":row["source_dataset"],"turn_bucket":row["turn_bucket"]})
        (draft/"README.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
        stratum_plan=[{"priority":k[0],"source":k[1],"turn_bucket":k[2],"sample":targets[k]} for k in sorted(targets)]
        manifest={"schema_version":"v59-independent-holdout-plan-4","status":"PUBLISHED_FOR_BLINDED_REVIEW",
          "training_labels":216,"never_reviewed_population":864,"holdout_size":72,"selection_uses_model_score":False,
          "model_scores_blinded":True,"model_family":"multinomial_nb_role_word_unigram_bigram","training_fingerprint":model_fingerprint(labels),
          "strata":stratum_plan,"training_authorized":False,"cases":plan}
        (draft/"SAMPLING-PLAN-004.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        shutil.copytree(draft,DEST)
    staged={str(p.relative_to(REPO)) for p in DEST.rglob("*") if p.is_file()}; committed=False
    try:
        git("add","--",*sorted(staged))
        if set(git("diff","--cached","--name-only").splitlines())!=staged: raise RuntimeError("unexpected staged files")
        git("diff","--cached","--check"); git("commit","-m","V59: publish independent holdout 004"); committed=True
    except Exception:
        if not committed:
            git("reset","--quiet","--",*sorted(staged)); shutil.rmtree(DEST,ignore_errors=True)
        raise
    git("push","origin","main"); git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("push verification failed")
    print(MARKER); print("V59_HOLDOUT004_TRAIN_LABELS: 216"); print("V59_HOLDOUT004_REMAINING_BEFORE: 864")
    print("V59_HOLDOUT004_SAMPLE: 72"); print("V59_HOLDOUT004_SELECTION_USES_SCORE: 0"); print("TRAINING_AUTHORIZED: 0")
    print("GIT_HEAD:",git("rev-parse","--short","HEAD"))

if __name__=="__main__": main()
