#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
BASE_PATH=REPO/"tools"/"publish_smoltalk_v59_bulk_sample.py"
ROOTS=[REPO/"reviews"/"smoltalk-v59-bulk-sample-001",REPO/"reviews"/"smoltalk-v59-bulk-sample-002"]

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None: raise RuntimeError("module load failed")
    m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m
BASE=load("v59_bulk_base_combined",BASE_PATH)

def field(text,name):
    m=re.search(rf"^{re.escape(name)}: (.+)$",text,re.MULTILINE)
    if m is None: raise RuntimeError("missing "+name)
    return m.group(1).strip()

def skey(row):
    return (row["priority_hint"],row["source_dataset"],row["turn_bucket"])

def read_reviews():
    out={}; sizes=[]
    for root in ROOTS:
        n=0
        for path in sorted((root/"cases").glob("*.md")):
            text=path.read_text(encoding="utf-8")
            sha=field(text,"Public content SHA-256")
            disp=field(text,"V59 disposition")
            if disp not in {"KEEP","REPAIR","EXCLUDE"}: raise RuntimeError("review pending")
            if sha in out: raise RuntimeError("duplicate reviewed SHA")
            out[sha]={"disposition":disp,"factual_risk":field(text,"V59 factual risk"),
                      "instruction_fit":field(text,"V59 instruction fit")}; n+=1
        sizes.append(n)
    if sizes!=[72,72] or len(out)!=144: raise RuntimeError("expected 72+72 reviewed cases")
    return out

def estimate(pop,sample,field_name,positive):
    total=sum(len(v) for v in pop.values()); value=0.0; variance=0.0
    for key,poprows in pop.items():
        N=len(poprows); rows=sample[key]; n=len(rows)
        if n==0: raise RuntimeError("unsampled stratum")
        x=sum(1 for row in rows if row[field_name] in positive); p=x/n; W=N/total
        value+=W*p
        if N>1 and n>1 and n<N:
            variance+=W*W*(1-n/N)*(p*(1-p)*n/(n-1))/n
    se=math.sqrt(max(0.0,variance))
    return value,max(0.0,value-1.96*se),min(1.0,value+1.96*se)

def bp(x): return int(round(x*10000))

def main():
    population=BASE.eligible_population()
    if len(population)!=1080: raise RuntimeError("population changed")
    reviews=read_reviews(); by_sha={r["sha"]:r for r in population}
    pop=defaultdict(list); sample=defaultdict(list)
    for row in population: pop[skey(row)].append(row)
    for sha,review in reviews.items():
        row=by_sha.get(sha)
        if row is None: raise RuntimeError("reviewed SHA missing")
        sample[skey(row)].append({**row,**review})
    if len(pop)!=10 or set(pop)!=set(sample): raise RuntimeError("strata changed")
    raw=Counter(v["disposition"] for v in reviews.values())
    keep=estimate(pop,sample,"disposition",{"KEEP"}); repair=estimate(pop,sample,"disposition",{"REPAIR"})
    exclude=estimate(pop,sample,"disposition",{"EXCLUDE"}); unsuitable=estimate(pop,sample,"disposition",{"REPAIR","EXCLUDE"})
    factual=estimate(pop,sample,"factual_risk",{"HIGH"}); bad=estimate(pop,sample,"instruction_fit",{"BAD"})
    weights=[]
    for key,rows in sample.items(): weights += [len(pop[key])/len(rows)]*len(rows)
    neff=sum(weights)**2/sum(w*w for w in weights)
    metrics={
      "V59_C2_POPULATION":1080,"V59_C2_SAMPLE_001":72,"V59_C2_SAMPLE_002":72,"V59_C2_REVIEWED":144,
      "V59_C2_STRATA":10,"V59_C2_NEFF_X100":int(round(neff*100)),
      "V59_C2_RAW_KEEP":raw["KEEP"],"V59_C2_RAW_REPAIR":raw["REPAIR"],"V59_C2_RAW_EXCLUDE":raw["EXCLUDE"],
      "V59_C2_KEEP_BP":bp(keep[0]),"V59_C2_KEEP_LOW_BP":bp(keep[1]),"V59_C2_KEEP_HIGH_BP":bp(keep[2]),
      "V59_C2_REPAIR_BP":bp(repair[0]),"V59_C2_EXCLUDE_BP":bp(exclude[0]),
      "V59_C2_UNSUITABLE_BP":bp(unsuitable[0]),"V59_C2_UNSUITABLE_LOW_BP":bp(unsuitable[1]),
      "V59_C2_UNSUITABLE_HIGH_BP":bp(unsuitable[2]),"V59_C2_FACTUAL_HIGH_BP":bp(factual[0]),
      "V59_C2_INSTRUCTION_BAD_BP":bp(bad[0]),"V59_C2_FORMAL_PROB_SAMPLE":0,"V59_C2_APPROX_DIAGNOSTIC":1,
      "V59_C2_SAMPLE_COMPLETE":1,"V59_MIX_FINALIZED":0,"SEMANTIC_VALIDATION_COMPLETE":1,"TRAINING_AUTHORIZED":0}
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key in sorted(metrics): print(f"{key}: {metrics[key]}")

if __name__=="__main__": main()
