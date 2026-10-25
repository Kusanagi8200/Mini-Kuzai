#!/usr/bin/env python3
from __future__ import annotations
import hashlib, html, importlib.util, json, shutil, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
TRIAGE_PATH=REPO/"tools"/"phase03_v59_supervised_triage.py"
DEST=REPO/"reviews"/"smoltalk-v59-active-sample-003"
PUBLIC_REVIEW_ROOT=Path("/root/Mini-Kuzai/data/external/smol-smoltalk/review")
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
PER_BUCKET=18

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None: raise RuntimeError("module load failed")
    m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m
TRIAGE=load("v59_active003_triage",TRIAGE_PATH)

def git(*args):
    p=subprocess.run(["git","-C",str(REPO),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode:
        detail="\n".join(x for x in (p.stdout.strip(),p.stderr.strip()) if x)
        raise RuntimeError("Git command failed: "+(detail or str(p.returncode)))
    return p.stdout.strip()

def escape(value):
    safe=html.escape(value,quote=True).replace("\r","&#13;")
    return "\n".join(line.rstrip(" \t")+line[len(line.rstrip(" \t")):].replace(" ","&#32;").replace("\t","&#9;") for line in safe.split("\n"))

def stable_rank(sha):
    return hashlib.sha256(("v59-active-sample-003:"+sha).encode()).hexdigest()

def diverse_control(rows,limit):
    groups=defaultdict(list)
    for r in rows:
        groups[(r["priority_hint"],r["source_dataset"],r["turn_bucket"],r["heuristic_category"])].append(r)
    for vals in groups.values(): vals.sort(key=lambda r:stable_rank(r["sha"]))
    keys=sorted(groups); out=[]
    while len(out)<limit:
        progressed=False
        for key in keys:
            if groups[key]:
                out.append(groups[key].pop(0)); progressed=True
                if len(out)==limit: break
        if not progressed: break
    if len(out)!=limit: raise RuntimeError("unable to fill diversity control")
    return out

def select():
    labels=TRIAGE.labels(); pop=TRIAGE.BASE.eligible_population()
    reviewed=[]; unreviewed=[]
    for row in pop:
        q={**row,"f":TRIAGE.feats(row)}
        if row["sha"] in labels:
            q["disp"]=labels[row["sha"]]; q["bad"]=q["disp"]!="KEEP"; reviewed.append(q)
        else: unreviewed.append(q)
    if len(reviewed)!=144 or len(unreviewed)!=936: raise RuntimeError("review accounting changed")
    model=TRIAGE.MNB(); model.fit(reviewed,"bad")
    scored=sorted([{**r,"score":model.prob(r["f"])} for r in unreviewed],key=lambda r:(-r["score"],r["sha"]))
    high=scored[:PER_BUCKET]
    high_sha={r["sha"] for r in high}
    low=[r for r in reversed(scored) if r["sha"] not in high_sha][:PER_BUCKET]
    used=high_sha|{r["sha"] for r in low}
    middle_pool=[r for r in scored if r["sha"] not in used]
    mid_index=len(middle_pool)//2
    start=max(0,mid_index-PER_BUCKET//2)
    middle=middle_pool[start:start+PER_BUCKET]
    used|={r["sha"] for r in middle}
    control=diverse_control([r for r in scored if r["sha"] not in used],PER_BUCKET)
    buckets=[("HIGH_RISK_RANK",high),("MIDDLE_RANK",middle),("LOW_RISK_RANK",low),("DIVERSITY_CONTROL",control)]
    selected=[]
    for bucket,rows in buckets:
        for r in rows: selected.append({**r,"selection_bucket":bucket})
    if len(selected)!=72 or len({r["sha"] for r in selected})!=72: raise RuntimeError("selection mismatch")
    return selected

def page(index,row):
    parts=[f"# V59 active-learning sample 003 review {index:02d}/72","",
      "V59 grade: PENDING","V59 factual risk: PENDING","V59 instruction fit: PENDING","V59 persona value: PENDING",
      "V59 disposition: PENDING","V59 defect tags: PENDING","V59 rationale: NOT_REVIEWED","",
      f"Selection bucket: {row['selection_bucket']}",f"Ranking score: {row['score']:.8f}",
      "Ranking score note: uncalibrated research ranking only; not a probability claim.",
      f"V50 priority hint: {row['priority_hint']}",f"V44 heuristic category: {row['heuristic_category']}",
      f"Turn bucket: {row['turn_bucket']}",f"Public external subset: {row['source_dataset']}",
      f"Public content SHA-256: {row['sha']}","","## Public external source dialogue","",
      "Source: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk",""]
    for turn,m in enumerate(row["messages"],1):
        parts += [f"### Turn {turn} - {m['role'].upper()}","","<pre>",escape(m["content"]),"</pre>",""]
    parts += ["## Review rubric","",
      "- Grade A / KEEP: coherent positive target unchanged.",
      "- Grade B / REPAIR: useful signal, but repair before positive supervision.",
      "- Grade C / EXCLUDE: unsuitable unchanged.",
      "- Factual risk: LOW / REVIEW / HIGH.",
      "- Instruction fit: GOOD / PARTIAL / BAD.",
      "- Persona value: HIGH / MEDIUM / LOW.",
      "- Defect tags: NONE, ROLE_CONTAMINATION, FACTUAL_ERROR, LOGICAL_ERROR, TECHNICAL_ERROR, INSTRUCTION_FAILURE, TIME_SENSITIVE, STYLE_QUALITY, OTHER.",
      "","Do not let the selection bucket or ranking score determine the semantic review.",""]
    return "\n".join(parts)

def preflight():
    if git("branch","--show-current")!="main": raise RuntimeError("Expected branch main")
    if git("status","--porcelain"): raise RuntimeError("Clean worktree required")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Local and remote main differ")
    if DEST.exists() or DEST.is_symlink(): raise RuntimeError("Sample 003 already exists")

def main():
    preflight(); selected=select()
    with tempfile.TemporaryDirectory(prefix="v59-active003-",dir=PUBLIC_REVIEW_ROOT) as scratch:
        draft=Path(scratch)/"smoltalk-v59-active-sample-003"; cases=draft/"cases"; cases.mkdir(parents=True)
        counts=defaultdict(int)
        lines=["# Mini-Kuzai V59 - active-learning sample 003","","Status: **PUBLISHED FOR REVIEW - 72 cases.**","",
          "This is an active-learning challenge set, not a population-prevalence sample.",
          "The model score is used only to construct ranking buckets and must not bias semantic review.","",
          "Buckets: 18 HIGH_RISK_RANK, 18 MIDDLE_RANK, 18 LOW_RISK_RANK, 18 DIVERSITY_CONTROL.","",
          "No overlap with the 144 already reviewed cases.","","## Review cases","",
          "| Case | Bucket | Priority | Source | Turns | Category | Review |",
          "| ---: | --- | --- | --- | --- | --- | --- |"]
        plan=[]
        for i,row in enumerate(selected,1):
            counts[row["selection_bucket"]]+=1
            filename=f"{i:02d}-{row['sha'][:16]}.md"
            (cases/filename).write_text(page(i,row),encoding="utf-8")
            lines.append("| {} | {} | {} | {} | {} | {} | [Review](cases/{}) |".format(i,row["selection_bucket"],row["priority_hint"],row["source_dataset"],row["turn_bucket"],row["heuristic_category"],filename))
            plan.append({"case":i,"path":"reviews/smoltalk-v59-active-sample-003/cases/"+filename,"sha":row["sha"],"bucket":row["selection_bucket"],"ranking_score":round(row["score"],8)})
        if dict(counts)!={"HIGH_RISK_RANK":18,"MIDDLE_RANK":18,"LOW_RISK_RANK":18,"DIVERSITY_CONTROL":18}: raise RuntimeError("bucket counts changed")
        (draft/"README.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
        (draft/"SAMPLING-PLAN-003.json").write_text(json.dumps({"schema_version":"v59-active-sample-plan-3","status":"PUBLISHED_FOR_REVIEW","reviewed_before":144,"unreviewed_before":936,"sample_size":72,"population_estimator":False,"training_authorized":False,"cases":plan},indent=2,sort_keys=True)+"\n",encoding="utf-8")
        shutil.copytree(draft,DEST)
    staged={str(p.relative_to(REPO)) for p in DEST.rglob("*") if p.is_file()}
    committed=False
    try:
        git("add","--",*sorted(staged))
        if set(git("diff","--cached","--name-only").splitlines())!=staged: raise RuntimeError("unexpected staged files")
        git("diff","--cached","--check"); git("commit","-m","V59: publish active-learning sample 003"); committed=True
    except Exception:
        if not committed:
            git("reset","--quiet","--",*sorted(staged)); shutil.rmtree(DEST,ignore_errors=True)
        raise
    git("push","origin","main"); git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("push verification failed")
    print(MARKER); print("V59_ACTIVE003_SAMPLE: 72"); print("V59_ACTIVE003_HIGH: 18"); print("V59_ACTIVE003_MIDDLE: 18")
    print("V59_ACTIVE003_LOW: 18"); print("V59_ACTIVE003_CONTROL: 18"); print("TRAINING_AUTHORIZED: 0"); print("GIT_HEAD:",git("rev-parse","--short","HEAD"))

if __name__=="__main__": main()
