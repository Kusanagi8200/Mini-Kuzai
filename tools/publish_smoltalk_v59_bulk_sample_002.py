#!/usr/bin/env python3
"""Publish V59 bulk quality sample 002."""

from __future__ import annotations
import hashlib, html, importlib.util, json, re, shutil, subprocess, sys, tempfile
from collections import Counter, defaultdict
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
BASE_PATH=REPO/"tools"/"publish_smoltalk_v59_bulk_sample.py"
ROOT_001=REPO/"reviews"/"smoltalk-v59-bulk-sample-001"
DEST=REPO/"reviews"/"smoltalk-v59-bulk-sample-002"
PUBLIC_REVIEW_ROOT=Path("/root/Mini-Kuzai/data/external/smol-smoltalk/review")
POPULATION=1080
SAMPLE_001=72
SAMPLE_002=72
TARGET_CUMULATIVE=144
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError(f"Unable to load {path}")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module

BASE=load_module("v59_bulk_sample_001_for_002",BASE_PATH)

def git(*args):
    p=subprocess.run(["git","-C",str(REPO),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode: raise RuntimeError("Git command failed: "+p.stderr.strip())
    return p.stdout.strip()

def field(text,name):
    m=re.search(rf"^{re.escape(name)}: (.+)$",text,flags=re.MULTILINE)
    if m is None: raise RuntimeError(f"Missing field: {name}")
    return m.group(1).strip()

def previous_sample_shas():
    rows=set()
    for path in sorted((ROOT_001/"cases").glob("*.md")):
        if path.is_symlink(): raise RuntimeError("Unsafe sample 001 symlink")
        text=path.read_text(encoding="utf-8")
        if field(text,"V59 disposition") not in {"KEEP","REPAIR","EXCLUDE"}: raise RuntimeError("Sample 001 review not closed")
        sha=field(text,"Public content SHA-256")
        if sha in rows: raise RuntimeError("Duplicate sample 001 SHA")
        rows.add(sha)
    if len(rows)!=SAMPLE_001: raise RuntimeError("Expected 72 sample 001 cases")
    return rows

def key(row):
    return (row["priority_hint"],row["source_dataset"],row["turn_bucket"])

def rank_002(sha):
    return hashlib.sha256(("v59-bulk-sample-002:"+sha).encode("ascii")).hexdigest()

def allocate(population,previous):
    strata=defaultdict(list); by_sha={}
    for source in population:
        row=dict(source); row["rank_002"]=rank_002(row["sha"]); strata[key(row)].append(row); by_sha[row["sha"]]=row
    existing=Counter()
    for sha in previous:
        row=by_sha.get(sha)
        if row is None: raise RuntimeError("Sample 001 SHA absent from population")
        existing[key(row)]+=1
    targets={k:existing[k] for k in strata}
    raw={k:TARGET_CUMULATIVE*len(v)/POPULATION for k,v in strata.items()}
    if sum(targets.values())!=SAMPLE_001: raise RuntimeError("Sample 001 accounting changed")
    while sum(targets.values())<TARGET_CUMULATIVE:
        available=[k for k,v in strata.items() if targets[k]<len(v)]
        if not available: raise RuntimeError("No capacity for sample 002")
        chosen=max(available,key=lambda k:(raw[k]-targets[k],len(strata[k])-targets[k],k))
        targets[chosen]+=1
    allocation={k:targets[k]-existing[k] for k in strata}
    if sum(allocation.values())!=SAMPLE_002: raise RuntimeError("Sample 002 allocation does not total 72")
    return strata,existing,targets,allocation

def diverse_pick(rows,limit,previous):
    by_category=defaultdict(list)
    for row in rows:
        if row["sha"] not in previous: by_category[row["heuristic_category"]].append(row)
    for values in by_category.values(): values.sort(key=lambda r:r["rank_002"])
    selected=[]; categories=sorted(by_category)
    while len(selected)<limit:
        progressed=False
        for category in categories:
            if by_category[category]:
                selected.append(by_category[category].pop(0)); progressed=True
                if len(selected)==limit: break
        if not progressed: break
    if len(selected)!=limit: raise RuntimeError("Unable to fill sample 002 stratum")
    return selected

def escape_content(value):
    return html.escape(value,quote=True).replace("\r","&#13;")

def case_page(index,row,N_h,n1_h,n2_h):
    parts=[
        f"# V59 public bulk sample 002 review {index:02d}/72","",
        "V59 grade: PENDING","V59 factual risk: PENDING","V59 instruction fit: PENDING",
        "V59 persona value: PENDING","V59 disposition: PENDING","V59 defect tags: PENDING",
        "V59 rationale: NOT_REVIEWED","",
        f"V50 priority hint: {row['priority_hint']}",f"V44 heuristic category: {row['heuristic_category']}",
        f"Turn bucket: {row['turn_bucket']}",f"Public external subset: {row['source_dataset']}",
        f"Public content SHA-256: {row['sha']}",f"Stratum population: {N_h}",
        f"Sample 001 in stratum: {n1_h}",f"Sample 002 allocation: {n2_h}","",
        "## Public external source dialogue","","Source: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk",""
    ]
    for turn,message in enumerate(row["messages"],1):
        parts += [f"### Turn {turn} - {message['role'].upper()}","","<pre>",escape_content(message["content"]),"</pre>",""]
    parts += [
        "## Review rubric","",
        "- Grade A / KEEP: coherent positive target unchanged.",
        "- Grade B / REPAIR: useful signal, but repair before positive supervision.",
        "- Grade C / EXCLUDE: unsuitable unchanged.",
        "- Factual risk: LOW / REVIEW / HIGH.",
        "- Instruction fit: GOOD / PARTIAL / BAD.",
        "- Persona value: HIGH / MEDIUM / LOW.",
        "- Defect tags: NONE, ROLE_CONTAMINATION, FACTUAL_ERROR, LOGICAL_ERROR, TECHNICAL_ERROR, INSTRUCTION_FAILURE, TIME_SENSITIVE, STYLE_QUALITY, OTHER.",
        "","V50 priority remains heuristic and must not determine the review.",""
    ]
    return "\n".join(parts)

def preflight():
    if git("branch","--show-current")!="main": raise RuntimeError("Expected branch main")
    if git("status","--porcelain"): raise RuntimeError("Clean worktree required")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Local and remote main differ")
    if DEST.exists() or DEST.is_symlink(): raise RuntimeError("Sample 002 already exists")
    if not PUBLIC_REVIEW_ROOT.is_dir(): raise RuntimeError("Public SmolTalk workspace missing")

def main():
    preflight()
    population=BASE.eligible_population()
    if len(population)!=POPULATION: raise RuntimeError("Eligible population changed")
    previous=previous_sample_shas()
    strata,existing,targets,allocation=allocate(population,previous)
    selected=[]
    for stratum in sorted(strata): selected += diverse_pick(strata[stratum],allocation[stratum],previous)
    if len(selected)!=SAMPLE_002 or len({r["sha"] for r in selected})!=SAMPLE_002: raise RuntimeError("Sample 002 size/duplicate mismatch")
    if previous & {r["sha"] for r in selected}: raise RuntimeError("Sample 001/002 overlap")
    selected.sort(key=lambda r:(r["priority_hint"],r["source_dataset"],r["turn_bucket"],r["rank_002"]))

    plan={"schema_version":"v59-bulk-sample-plan-2","status":"PUBLISHED_FOR_REVIEW","population":POPULATION,
          "sample_001":SAMPLE_001,"sample_002":SAMPLE_002,"target_cumulative":TARGET_CUMULATIVE,
          "formal_probability_sample":False,"training_authorized":False,"strata":[]}
    for stratum in sorted(strata):
        priority,source,turns=stratum
        plan["strata"].append({"priority":priority,"source":source,"turn_bucket":turns,"population":len(strata[stratum]),
                               "sample_001":existing[stratum],"sample_002":allocation[stratum],"cumulative":targets[stratum]})

    with tempfile.TemporaryDirectory(prefix="v59-bulk-sample-002-",dir=PUBLIC_REVIEW_ROOT) as scratch:
        draft=Path(scratch)/"smoltalk-v59-bulk-sample-002"; cases=draft/"cases"; cases.mkdir(parents=True)
        lines=["# Mini-Kuzai V59 - bulk quality sample 002","","Status: **PUBLISHED FOR REVIEW - 72 new cases.**","",
               "Sample 002 adds 72 new public cases with no overlap with Sample 001.",
               "The cumulative 144-case design is rebalanced toward the real sizes of the 10 observed priority × source × turn strata.","",
               "No private, VALIDATION or BLIND TEST material is included.","","## Stratum allocation","",
               "| Priority | Source | Turns | Population | S001 | S002 | Cumulative |",
               "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
        for item in plan["strata"]:
            lines.append("| {priority} | {source} | {turn_bucket} | {population} | {sample_001} | {sample_002} | {cumulative} |".format(**item))
        lines += ["","## Review cases","","| Case | Priority | Source | Turns | Category | Review |","| ---: | --- | --- | --- | --- | --- |"]
        for index,row in enumerate(selected,1):
            stratum=key(row); filename=f"{index:02d}-{row['sha'][:16]}.md"
            (cases/filename).write_text(case_page(index,row,len(strata[stratum]),existing[stratum],allocation[stratum]),encoding="utf-8")
            lines.append("| {} | {} | {} | {} | {} | [Review](cases/{}) |".format(index,row["priority_hint"],row["source_dataset"],row["turn_bucket"],row["heuristic_category"],filename))
        lines += ["","Review output is recorded in DECISIONS-002.json before finalization.","Training remains NOT AUTHORIZED.",""]
        (draft/"README.md").write_text("\n".join(lines),encoding="utf-8")
        (draft/"SAMPLING-PLAN-002.json").write_text(json.dumps(plan,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        shutil.copytree(draft,DEST)

    staged={str(path.relative_to(REPO)) for path in DEST.rglob("*") if path.is_file()}
    git("add","--",*sorted(staged))
    if set(git("diff","--cached","--name-only").splitlines())!=staged: raise RuntimeError("Unexpected staged files")
    git("diff","--cached","--check")
    git("commit","-m","V59: publish proportional bulk quality sample 002")
    git("push","origin","main"); git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"): raise RuntimeError("Push verification failed")
    print(MARKER); print("V59_SAMPLE_002_POPULATION: 1080"); print("V59_SAMPLE_002_NEW_CASES: 72")
    print("V59_SAMPLE_002_CUMULATIVE: 144"); print("V59_SAMPLE_002_STRATA: 10"); print("TRAINING_AUTHORIZED: 0")
    print("GIT_HEAD:",git("rev-parse","--short","HEAD"))

if __name__=="__main__":
    try: main()
    except Exception as exc:
        print(MARKER); print("V59_SAMPLE_002_EXPORT: NOT_CONFIRMED"); print("ERROR:",str(exc)); raise
