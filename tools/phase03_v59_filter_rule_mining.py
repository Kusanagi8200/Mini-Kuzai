#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, html, importlib.util, itertools, json, re, sys
from collections import Counter
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
BASE_PATH=REPO/"tools"/"publish_smoltalk_v59_bulk_sample.py"
OUT=REPO/"reviews"/"smoltalk-v59-filter-rule-mining"
ROOTS=[
 (REPO/"reviews"/"smoltalk-v59-bulk-sample-001",REPO/"reviews"/"smoltalk-v59-bulk-sample-001"/"DECISIONS-001.json"),
 (REPO/"reviews"/"smoltalk-v59-bulk-sample-002",REPO/"reviews"/"smoltalk-v59-bulk-sample-002"/"DECISIONS-002.json")]
WORD=re.compile(r"[A-Za-z0-9_]+")
TURN=re.compile(r"### Turn \d+ - (USER|ASSISTANT)\n\n<pre>\n(.*?)\n</pre>",re.S)
ANSWER=re.compile(r"\b(?:here(?:'s| is| are)?|below is|the following is)\b.{0,80}\b(?:answer|response|review|revision|rewrite|edited paragraph|solution)\b|\b(?:answer|response|review)\s*:",re.I|re.S)
CURRENT=re.compile(r"\b(?:latest|current|today|now|recent|currently|this year|upcoming)\b",re.I)
ASSIST_Q=re.compile(r"(?:\n|^)\s*(?:Question|Q)\s*:",re.I)
RESEARCH=re.compile(r"\b(?:studies|research)\s+(?:have\s+)?(?:shown|shows|suggests|indicates)\b",re.I)
YEAR=re.compile(r"\b(?:19|20)\d{2}\b")

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None: raise RuntimeError("module load failed")
    m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m
BASE=load("v59_rule_base",BASE_PATH)

def field(text,name):
    m=re.search(rf"^{re.escape(name)}: (.+)$",text,re.M)
    if m is None: raise RuntimeError("missing field "+name)
    return m.group(1).strip()

def parse_page(path):
    text=path.read_text(encoding="utf-8")
    messages=[{"role":r.lower(),"content":html.unescape(c)} for r,c in TURN.findall(text)]
    return {"sha":field(text,"Public content SHA-256"),"messages":messages}

def load_reviews():
    out={}
    for root,manifest in ROOTS:
        data=json.loads(manifest.read_text(encoding="utf-8"))
        if len(data["decisions"])!=72: raise RuntimeError("review count changed")
        for d in data["decisions"]:
            page=parse_page(REPO/d["path"]); sha=page["sha"]
            if sha in out: raise RuntimeError("duplicate reviewed sha")
            out[sha]={"disposition":d["disposition"],**page}
    if len(out)!=144: raise RuntimeError("expected 144 reviewed cases")
    return out

def tokens(text):
    return [x.lower() for x in WORD.findall(text)]

def shingles(text,n=4):
    t=tokens(text)
    return {tuple(t[i:i+n]) for i in range(max(0,len(t)-n+1))}

def overlap(a,b):
    aa=shingles(a); bb=shingles(b)
    return len(aa&bb)/len(bb) if bb else 0.0

def features(row):
    msgs=row["messages"]; users=[m["content"] for m in msgs if m["role"]=="user"]; assists=[m["content"] for m in msgs if m["role"]=="assistant"]
    u="\n".join(users); a="\n".join(assists); alltext=u+"\n"+a
    f={"PRIORITY="+row["priority_hint"],"CATEGORY="+row["heuristic_category"],"SOURCE="+row["source_dataset"],"TURN="+row["turn_bucket"]}
    if row["turn_bucket"]=="MULTITURN": f.add("MULTITURN")
    else: f.add("SINGLE")
    if ANSWER.search(u): f.add("USER_ANSWER_MARKER")
    if ASSIST_Q.search(a): f.add("ASSISTANT_QUESTION_MARKER")
    if CURRENT.search(alltext): f.add("TIME_SENSITIVE_LANGUAGE")
    if RESEARCH.search(a): f.add("ASSERTIVE_RESEARCH_CLAIM")
    years=len(YEAR.findall(alltext))
    if years: f.add("HAS_YEAR")
    if years>=3: f.add("MANY_YEARS")
    aw=sum(len(tokens(x)) for x in assists); uw=sum(len(tokens(x)) for x in users); total=aw+uw
    if total>=500: f.add("LONG_500W")
    if total>=1000: f.add("LONG_1000W")
    if aw>=500: f.add("ASSISTANT_LONG_500W")
    nums=sum(x.isdigit() for x in tokens(alltext))
    if total and nums/total>=0.04: f.add("NUMERIC_DENSE")
    if any(x in alltext for x in ("```","SELECT ","def ","function ","import ")): f.add("CODE_OR_SQL")
    ov=max([overlap(x,y) for x in users for y in assists] or [0.0])
    for threshold,label in ((.20,"20"),(.35,"35"),(.50,"50"),(.70,"70")):
        if ov>=threshold: f.add("ROLE_OVERLAP_"+label)
    return f

def split(sha):
    h=hashlib.sha256(("v59-filter-rule-split:"+sha).encode()).hexdigest()
    return "discovery" if int(h[:16],16)%2==0 else "holdout"

def rule_name(rule):
    return " AND ".join(sorted(rule))

def stats(rows,rule,target):
    flagged=[r for r in rows if rule<=r["features"]]
    tp=sum(r[target] for r in flagged); pos=sum(r[target] for r in rows); n=len(flagged)
    return {"support":n,"tp":tp,"precision":tp/n if n else 0.0,"recall":tp/pos if pos else 0.0}

def candidates(discovery):
    counts=Counter()
    for r in discovery: counts.update(r["features"])
    single=[x for x,n in counts.items() if n>=5]
    rules={frozenset([x]) for x in single}
    for a,b in itertools.combinations(single,2):
        q=frozenset([a,b])
        if sum(q<=r["features"] for r in discovery)>=5: rules.add(q)
    return sorted(rules,key=lambda q:(len(q),rule_name(q)))

def mine(discovery,holdout,rules,target,dp,hp):
    found=[]
    for q in rules:
        d=stats(discovery,q,target)
        if d["support"]<5 or d["precision"]<dp: continue
        h=stats(holdout,q,target)
        if h["support"]<3 or h["precision"]<hp: continue
        found.append({"rule":sorted(q),"name":rule_name(q),"discovery":d,"holdout":h})
    found.sort(key=lambda x:(-x["holdout"]["precision"],-x["holdout"]["support"],len(x["rule"]),x["name"]))
    kept=[]
    for item in found:
        q=frozenset(item["rule"])
        if any(frozenset(k["rule"])<q and k["holdout"]["precision"]>=item["holdout"]["precision"] and k["holdout"]["support"]>=item["holdout"]["support"] for k in kept): continue
        kept.append(item)
    return kept

def union_stats(rows,accepted,target):
    rules=[frozenset(x["rule"]) for x in accepted]
    flagged=[r for r in rows if any(q<=r["features"] for q in rules)]
    tp=sum(r[target] for r in flagged); pos=sum(r[target] for r in rows); n=len(flagged)
    return {"support":n,"tp":tp,"precision":tp/n if n else 0.0,"recall":tp/pos if pos else 0.0}

def build():
    reviewed=load_reviews(); pop=BASE.eligible_population()
    if len(pop)!=1080: raise RuntimeError("population changed")
    bysha={r["sha"]:r for r in pop}; rows=[]
    for sha,rev in reviewed.items():
        base=bysha.get(sha)
        if base is None: raise RuntimeError("reviewed source absent from population")
        rows.append({"sha":sha,"features":features(base),"unsuitable":rev["disposition"]!="KEEP","exclude":rev["disposition"]=="EXCLUDE","split":split(sha)})
    disc=[r for r in rows if r["split"]=="discovery"]; hold=[r for r in rows if r["split"]=="holdout"]
    if min(len(disc),len(hold))<60: raise RuntimeError("imbalanced split")
    rules=candidates(disc)
    bad=mine(disc,hold,rules,"unsuitable",.75,.75)
    exc=mine(disc,hold,rules,"exclude",.85,.85)
    hb=union_stats(hold,bad,"unsuitable"); he=union_stats(hold,exc,"exclude")
    poprows=[{"sha":r["sha"],"features":features(r)} for r in pop]
    badrules=[frozenset(x["rule"]) for x in bad]; exrules=[frozenset(x["rule"]) for x in exc]
    review={r["sha"] for r in poprows if any(q<=r["features"] for q in badrules)}
    exclude={r["sha"] for r in poprows if any(q<=r["features"] for q in exrules)}
    return {"schema_version":"v59-filter-rule-mining-1","status":"MINED_VALIDATED_NOT_APPLIED","reviewed":144,"discovery":len(disc),"holdout":len(hold),"population":1080,"candidate_rules":len(rules),
      "accepted_unsuitable_rules":bad,"accepted_exclude_rules":exc,"holdout_unsuitable_union":hb,"holdout_exclude_union":he,
      "projected_population":{"review_flagged":len(review),"exclude_flagged":len(exclude),"any_flagged":len(review|exclude)},
      "rule_application_authorized":False,"mix_finalized":False,"training_authorized":False}

def write(report):
    if OUT.exists() or OUT.is_symlink(): raise RuntimeError("rule mining output already exists")
    OUT.mkdir(parents=True)
    (OUT/"REPORT-001.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    lines=["# Mini-Kuzai V59 - filter rule mining 001","","Status: MINED / VALIDATED / NOT APPLIED","",
      "Reviewed: "+str(report["reviewed"]),"Discovery: "+str(report["discovery"]),"Holdout: "+str(report["holdout"]),
      "Candidate rules: "+str(report["candidate_rules"]),"","## Accepted rules for REPAIR or EXCLUDE",""]
    if report["accepted_unsuitable_rules"]:
        for x in report["accepted_unsuitable_rules"]:
            lines.append("- {} | discovery {:.1%} | holdout {:.1%} | holdout n={}".format(x["name"],x["discovery"]["precision"],x["holdout"]["precision"],x["holdout"]["support"]))
    else: lines.append("- none")
    lines+=["","## Accepted rules for EXCLUDE",""]
    if report["accepted_exclude_rules"]:
        for x in report["accepted_exclude_rules"]:
            lines.append("- {} | discovery {:.1%} | holdout {:.1%} | holdout n={}".format(x["name"],x["discovery"]["precision"],x["holdout"]["precision"],x["holdout"]["support"]))
    else: lines.append("- none")
    hb=report["holdout_unsuitable_union"]; he=report["holdout_exclude_union"]; p=report["projected_population"]
    lines+=["","## Holdout union","- unsuitable precision {:.1%}, recall {:.1%}, flagged {}".format(hb["precision"],hb["recall"],hb["support"]),
      "- exclude precision {:.1%}, recall {:.1%}, flagged {}".format(he["precision"],he["recall"],he["support"]),"",
      "## Projection on 1080","- review flagged: "+str(p["review_flagged"]),"- exclude flagged: "+str(p["exclude_flagged"]),"- unique flagged: "+str(p["any_flagged"]),"",
      "Projection only. No source is removed.","Rule application authorized: NO.","V59 mix finalized: NO.","Training authorized: NO.",""]
    (OUT/"RESULTS-001.md").write_text("\n".join(lines),encoding="utf-8")

def bp(x): return int(round(x*10000))

def metrics(r):
    hb=r["holdout_unsuitable_union"]; he=r["holdout_exclude_union"]; p=r["projected_population"]
    return {"V59_RULES_REVIEWED":144,"V59_RULES_DISCOVERY":r["discovery"],"V59_RULES_HOLDOUT":r["holdout"],"V59_RULES_CANDIDATES":r["candidate_rules"],
      "V59_RULES_ACCEPTED_UNSUITABLE":len(r["accepted_unsuitable_rules"]),"V59_RULES_ACCEPTED_EXCLUDE":len(r["accepted_exclude_rules"]),
      "V59_RULES_HOLDOUT_UNSUITABLE_FLAGGED":hb["support"],"V59_RULES_HOLDOUT_UNSUITABLE_PREC_BP":bp(hb["precision"]),"V59_RULES_HOLDOUT_UNSUITABLE_RECALL_BP":bp(hb["recall"]),
      "V59_RULES_HOLDOUT_EXCLUDE_FLAGGED":he["support"],"V59_RULES_HOLDOUT_EXCLUDE_PREC_BP":bp(he["precision"]),"V59_RULES_HOLDOUT_EXCLUDE_RECALL_BP":bp(he["recall"]),
      "V59_RULES_POPULATION_REVIEW_FLAGGED":p["review_flagged"],"V59_RULES_POPULATION_EXCLUDE_FLAGGED":p["exclude_flagged"],"V59_RULES_POPULATION_ANY_FLAGGED":p["any_flagged"],
      "V59_RULE_APPLICATION_AUTHORIZED":0,"V59_MIX_FINALIZED":0,"SEMANTIC_VALIDATION_COMPLETE":1,"TRAINING_AUTHORIZED":0}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--write",action="store_true"); ap.add_argument("--from-report",action="store_true"); args=ap.parse_args()
    r=json.loads((OUT/"REPORT-001.json").read_text(encoding="utf-8")) if args.from_report else build()
    if args.write: write(r)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for k,v in sorted(metrics(r).items()): print(f"{k}: {v}")

if __name__=="__main__": main()
