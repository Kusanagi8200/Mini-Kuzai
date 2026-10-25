#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
BASE_PATH=REPO/"tools"/"publish_smoltalk_v59_bulk_sample.py"
MANIFESTS=[
 REPO/"reviews"/"smoltalk-v59-bulk-sample-001"/"DECISIONS-001.json",
 REPO/"reviews"/"smoltalk-v59-bulk-sample-002"/"DECISIONS-002.json"]
OUT=REPO/"reviews"/"smoltalk-v59-supervised-triage"
FOLDS=5; ALPHA=1.0; TH_BAD=.75; TH_EXC=.90
TOK=re.compile(r"[A-Za-z0-9_]+")
STOP=set("the a an and or but if then to of in on for with as at by is are was were be been being it this that these those i you he she they we me my your our their his her its do does did can could would should will just from into about what how why when where which who not no so than also have has had".split())

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None: raise RuntimeError("module load failed")
    m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m
BASE=load("v59_supervised_base",BASE_PATH)

def labels():
    out={}
    for manifest in MANIFESTS:
        data=json.loads(manifest.read_text(encoding="utf-8"))
        if len(data["decisions"])!=72: raise RuntimeError("review count changed")
        for d in data["decisions"]:
            text=(REPO/d["path"]).read_text(encoding="utf-8")
            m=re.search(r"^Public content SHA-256: (.+)$",text,re.M)
            if m is None: raise RuntimeError("missing source sha")
            sha=m.group(1).strip()
            if sha in out: raise RuntimeError("duplicate reviewed sha")
            out[sha]=d["disposition"]
    if len(out)!=144: raise RuntimeError("expected 144 reviewed labels")
    return out

def words(text):
    return [x for x in TOK.findall(text.lower()) if len(x)>1 and x not in STOP]

def feats(row):
    f={"P="+row["priority_hint"],"C="+row["heuristic_category"],"S="+row["source_dataset"],"T="+row["turn_bucket"]}
    for msg in row["messages"]:
        p="U" if msg["role"]=="user" else "A"; w=words(msg["content"])
        f.update(p+"1="+x for x in w)
        f.update(p+"2="+a+"_"+b for a,b in zip(w,w[1:]))
    return f

def fold_ids(rows):
    groups=defaultdict(list)
    for i,r in enumerate(rows): groups[r["disp"]].append((i,r["sha"]))
    out=[-1]*len(rows)
    for label,vals in groups.items():
        vals.sort(key=lambda z:hashlib.sha256(("v59-supervised:"+label+":"+z[1]).encode()).hexdigest())
        for pos,(i,_) in enumerate(vals): out[i]=pos%FOLDS
    return out

class MNB:
    def fit(self,rows,target):
        df=Counter()
        for r in rows: df.update(r["f"])
        self.vocab={x for x,n in df.items() if n>=2}
        self.classn=Counter(); self.counts={0:Counter(),1:Counter()}; self.total=Counter()
        for r in rows:
            y=int(r[target]); self.classn[y]+=1
            active=r["f"]&self.vocab; self.counts[y].update(active); self.total[y]+=len(active)
        self.n=len(rows)
    def prob(self,f):
        active=f&self.vocab; score={}
        V=max(1,len(self.vocab))
        for y in (0,1):
            s=math.log((self.classn[y]+ALPHA)/(self.n+2*ALPHA))
            den=self.total[y]+ALPHA*V
            for x in active: s+=math.log((self.counts[y][x]+ALPHA)/den)
            score[y]=s
        d=score[1]-score[0]
        return 1/(1+math.exp(-d)) if abs(d)<700 else (1.0 if d>0 else 0.0)

def cm(y,p,t):
    tp=fp=tn=fn=0
    for a,b in zip(y,p):
        q=b>=t
        if q and a: tp+=1
        elif q: fp+=1
        elif a: fn+=1
        else: tn+=1
    flagged=tp+fp; pos=tp+fn
    prec=tp/flagged if flagged else 0; rec=tp/pos if pos else 0
    f1=2*prec*rec/(prec+rec) if prec+rec else 0
    return {"tp":tp,"fp":fp,"tn":tn,"fn":fn,"flagged":flagged,"precision":prec,"recall":rec,"f1":f1}

def cv(rows,target,t):
    folds=fold_ids(rows); probs=[None]*len(rows)
    for k in range(FOLDS):
        train=[r for r,f in zip(rows,folds) if f!=k]; model=MNB(); model.fit(train,target)
        for i,f in enumerate(folds):
            if f==k: probs[i]=model.prob(rows[i]["f"])
    return cm([int(r[target]) for r in rows],probs,t)

def project(rows,unreviewed,target,t):
    model=MNB(); model.fit(rows,target)
    scored=sorted(((model.prob(r["f"]),r["sha"]) for r in unreviewed),reverse=True)
    flagged=[(p,s) for p,s in scored if p>=t]
    return {"flagged":len(flagged),"top":[{"sha":s,"probability":round(p,6)} for p,s in flagged[:100]]}

def bp(x): return int(round(x*10000))

def build():
    lab=labels(); pop=BASE.eligible_population()
    if len(pop)!=1080: raise RuntimeError("population changed")
    rows=[]; un=[]
    for r in pop:
        q={**r,"f":feats(r)}
        if r["sha"] in lab:
            q["disp"]=lab[r["sha"]]; q["bad"]=q["disp"]!="KEEP"; q["exc"]=q["disp"]=="EXCLUDE"; rows.append(q)
        else: un.append(q)
    if len(rows)!=144 or len(un)!=936: raise RuntimeError("review accounting changed")
    bad=cv(rows,"bad",TH_BAD); exc=cv(rows,"exc",TH_EXC)
    bad_gate=bad["precision"]>=.75 and bad["recall"]>=.30 and bad["flagged"]>=10
    exc_gate=exc["precision"]>=.85 and exc["recall"]>=.15 and exc["flagged"]>=5
    return {"schema_version":"v59-supervised-triage-1","status":"CV_VALIDATED_PROJECTION_ONLY","model":"multinomial_nb_role_word_unigram_bigram",
      "reviewed":144,"unreviewed":936,"folds":FOLDS,
      "unsuitable":{"cv":bad,"threshold":TH_BAD,"gate_pass":bad_gate,"projection":project(rows,un,"bad",TH_BAD)},
      "exclude":{"cv":exc,"threshold":TH_EXC,"gate_pass":exc_gate,"projection":project(rows,un,"exc",TH_EXC)},
      "triage_projection_authorized":bad_gate,"automatic_exclude_authorized":False,"mix_finalized":False,"training_authorized":False}

def write(r):
    if OUT.exists() or OUT.is_symlink(): raise RuntimeError("supervised triage output already exists")
    OUT.mkdir(parents=True)
    (OUT/"REPORT-001.json").write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    b=r["unsuitable"]["cv"]; e=r["exclude"]["cv"]
    lines=["# Mini-Kuzai V59 - supervised text triage 001","","Status: CV VALIDATED / PROJECTION ONLY / NOT APPLIED","",
      "Reviewed labels: 144","Unreviewed population: 936","Cross-validation folds: 5","",
      "## REVIEW target (REPAIR or EXCLUDE)",
      f"- threshold: {r['unsuitable']['threshold']:.2f}",f"- precision: {b['precision']:.1%}",f"- recall: {b['recall']:.1%}",f"- F1: {b['f1']:.1%}",
      f"- flagged OOF: {b['flagged']}",f"- gate pass: {r['unsuitable']['gate_pass']}",f"- projected flagged among 936: {r['unsuitable']['projection']['flagged']}","",
      "## EXCLUDE target",f"- threshold: {r['exclude']['threshold']:.2f}",f"- precision: {e['precision']:.1%}",f"- recall: {e['recall']:.1%}",f"- F1: {e['f1']:.1%}",
      f"- flagged OOF: {e['flagged']}",f"- gate pass: {r['exclude']['gate_pass']}",f"- projected flagged among 936: {r['exclude']['projection']['flagged']}","",
      "Projection only. No source is removed, repaired, promoted, or reweighted.",
      f"Triage projection authorized: {'YES' if r['triage_projection_authorized'] else 'NO'}.","Automatic exclude authorized: NO.","V59 mix finalized: NO.","Training authorized: NO.",""]
    (OUT/"RESULTS-001.md").write_text("\n".join(lines),encoding="utf-8")

def metrics(r):
    b=r["unsuitable"]["cv"]; e=r["exclude"]["cv"]
    return {"V59_TRIAGE_REVIEWED":144,"V59_TRIAGE_UNREVIEWED":936,"V59_TRIAGE_FOLDS":5,
      "V59_TRIAGE_UNSUITABLE_TP":b["tp"],"V59_TRIAGE_UNSUITABLE_FP":b["fp"],"V59_TRIAGE_UNSUITABLE_FN":b["fn"],
      "V59_TRIAGE_UNSUITABLE_PREC_BP":bp(b["precision"]),"V59_TRIAGE_UNSUITABLE_RECALL_BP":bp(b["recall"]),"V59_TRIAGE_UNSUITABLE_F1_BP":bp(b["f1"]),
      "V59_TRIAGE_UNSUITABLE_GATE":int(r["unsuitable"]["gate_pass"]),"V59_TRIAGE_UNSUITABLE_PROJECTED":r["unsuitable"]["projection"]["flagged"],
      "V59_TRIAGE_EXCLUDE_TP":e["tp"],"V59_TRIAGE_EXCLUDE_FP":e["fp"],"V59_TRIAGE_EXCLUDE_FN":e["fn"],
      "V59_TRIAGE_EXCLUDE_PREC_BP":bp(e["precision"]),"V59_TRIAGE_EXCLUDE_RECALL_BP":bp(e["recall"]),"V59_TRIAGE_EXCLUDE_F1_BP":bp(e["f1"]),
      "V59_TRIAGE_EXCLUDE_GATE":int(r["exclude"]["gate_pass"]),"V59_TRIAGE_EXCLUDE_PROJECTED":r["exclude"]["projection"]["flagged"],
      "V59_TRIAGE_PROJECTION_AUTHORIZED":int(r["triage_projection_authorized"]),"V59_AUTOMATIC_EXCLUDE_AUTHORIZED":0,
      "V59_MIX_FINALIZED":0,"SEMANTIC_VALIDATION_COMPLETE":1,"TRAINING_AUTHORIZED":0}

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--write",action="store_true"); ap.add_argument("--from-report",action="store_true"); a=ap.parse_args()
    r=json.loads((OUT/"REPORT-001.json").read_text(encoding="utf-8")) if a.from_report else build()
    if a.write: write(r)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for k,v in sorted(metrics(r).items()): print(f"{k}: {v}")

if __name__=="__main__": main()
