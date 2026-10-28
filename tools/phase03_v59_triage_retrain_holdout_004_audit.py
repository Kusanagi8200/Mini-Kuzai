#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, re, sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
PUB_PATH=REPO/"tools"/"publish_smoltalk_v59_independent_holdout_004.py"
ROOT=REPO/"reviews"/"smoltalk-v59-independent-holdout-004"
DECISIONS=ROOT/"DECISIONS-004.json"
REPORT=ROOT/"AUDIT-004.json"
RESULTS=ROOT/"RANKING-RESULTS-004.md"
TH_BAD=.75; TH_EXC=.90; QUARTILE=18

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError("module load failed")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module
PUB=load("v59_holdout004_publisher_for_audit",PUB_PATH)
TRIAGE=PUB.TRIAGE

def sha_from_page(path):
    text=path.read_text(encoding="utf-8")
    m=re.search(r"^Public content SHA-256: (.+)$",text,re.M)
    if m is None: raise RuntimeError("missing source sha")
    return m.group(1).strip()

def auc(labels,scores):
    pos=[s for y,s in zip(labels,scores) if y]; neg=[s for y,s in zip(labels,scores) if not y]
    if not pos or not neg: return 0.0
    wins=0.0
    for p in pos:
        for n in neg:
            if p>n: wins+=1
            elif p==n: wins+=0.5
    return wins/(len(pos)*len(neg))

def confusion(labels,scores,threshold):
    tp=fp=tn=fn=0
    for y,s in zip(labels,scores):
        pred=s>=threshold
        if pred and y: tp+=1
        elif pred: fp+=1
        elif y: fn+=1
        else: tn+=1
    flagged=tp+fp; positives=tp+fn
    precision=tp/flagged if flagged else 0.0; recall=tp/positives if positives else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"tp":tp,"fp":fp,"tn":tn,"fn":fn,"flagged":flagged,"precision":precision,"recall":recall,"f1":f1}

def bp(x): return int(round(x*10000))

def build():
    decisions=json.loads(DECISIONS.read_text(encoding="utf-8"))
    if decisions.get("status")!="REVIEW_APPLIED": raise RuntimeError("Holdout 004 decisions not applied")
    hold=decisions.get("decisions")
    if not isinstance(hold,list) or len(hold)!=72: raise RuntimeError("Expected 72 holdout decisions")

    train_labels=PUB.labels216()
    pop=TRIAGE.BASE.eligible_population()
    if len(pop)!=1080: raise RuntimeError("eligible population changed")
    bysha={r["sha"]:r for r in pop}

    train=[]
    for sha,disp in train_labels.items():
        row=bysha.get(sha)
        if row is None: raise RuntimeError("training source absent")
        q={**row,"f":TRIAGE.feats(row),"disp":disp,"bad":disp!="KEEP","exc":disp=="EXCLUDE"}
        train.append(q)
    if len(train)!=216: raise RuntimeError("training set changed")

    bad_model=TRIAGE.MNB(); bad_model.fit(train,"bad")
    exc_model=TRIAGE.MNB(); exc_model.fit(train,"exc")

    evaluated=[]
    hold_shas=set()
    for d in hold:
        sha=sha_from_page(REPO/d["path"]); hold_shas.add(sha)
        if sha in train_labels: raise RuntimeError("holdout overlaps training labels")
        row=bysha.get(sha)
        if row is None: raise RuntimeError("holdout source absent")
        disp=d["disposition"]
        f=TRIAGE.feats(row)
        evaluated.append({"sha":sha,"disp":disp,"bad":disp!="KEEP","exc":disp=="EXCLUDE",
                          "bad_score":bad_model.prob(f),"exc_score":exc_model.prob(f)})
    if len(hold_shas)!=72: raise RuntimeError("duplicate holdout source")

    y_bad=[r["bad"] for r in evaluated]; s_bad=[r["bad_score"] for r in evaluated]
    y_exc=[r["exc"] for r in evaluated]; s_exc=[r["exc_score"] for r in evaluated]
    bad_auc=auc(y_bad,s_bad); exc_auc=auc(y_exc,s_exc)
    bad_threshold=confusion(y_bad,s_bad,TH_BAD); exc_threshold=confusion(y_exc,s_exc,TH_EXC)

    ranked=sorted(evaluated,key=lambda r:(-r["bad_score"],r["sha"]))
    top=ranked[:QUARTILE]; bottom=ranked[-QUARTILE:]
    top_bad=sum(r["bad"] for r in top)/QUARTILE; bottom_bad=sum(r["bad"] for r in bottom)/QUARTILE
    gradient=top_bad-bottom_bad
    ranking_gate=(bad_auc>=.70 and top_bad>=.65 and bottom_bad<=.35 and gradient>=.30)

    remaining=[r for r in pop if r["sha"] not in train_labels and r["sha"] not in hold_shas]
    if len(remaining)!=792: raise RuntimeError("remaining population changed")
    remaining_scores=[bad_model.prob(TRIAGE.feats(r)) for r in remaining]
    projected_high=sum(s>=TH_BAD for s in remaining_scores)

    report={"schema_version":"v59-triage-retrain-holdout-4","status":"INDEPENDENT_HOLDOUT_EVALUATED",
      "model_family":"multinomial_nb_role_word_unigram_bigram","training_labels":216,"holdout_size":72,
      "remaining_unreviewed":792,"holdout_selection_uses_model_score":False,"scores_blinded_during_review":True,
      "unsuitable":{"auc":bad_auc,"threshold":TH_BAD,"threshold_metrics":bad_threshold,
        "top_quartile_unsuitable_rate":top_bad,"bottom_quartile_unsuitable_rate":bottom_bad,
        "quartile_gradient":gradient,"ranking_gate_pass":ranking_gate,"remaining_projected_at_threshold":projected_high},
      "exclude":{"auc":exc_auc,"threshold":TH_EXC,"threshold_metrics":exc_threshold},
      "ranking_priority_authorized":ranking_gate,"automatic_review_authorized":False,"automatic_exclude_authorized":False,
      "mix_finalized":False,"training_authorized":False}
    return report

def write(report):
    if REPORT.exists() or RESULTS.exists(): raise RuntimeError("Holdout 004 audit output already exists")
    REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    b=report["unsuitable"]; e=report["exclude"]; bt=b["threshold_metrics"]; et=e["threshold_metrics"]
    lines=["# Mini-Kuzai V59 - triage retrain + independent holdout 004","","Status: **INDEPENDENT HOLDOUT EVALUATED**","",
      "Training annotations: **216**","Independent holdout: **72**","Remaining never-reviewed candidates: **792**","",
      "Holdout selection used model score: **NO**","Model scores visible during semantic review: **NO**","",
      "## REPAIR / EXCLUDE ranking","",f"- AUC: {b['auc']:.3f}",f"- top 18 unsuitable rate: {b['top_quartile_unsuitable_rate']:.1%}",
      f"- bottom 18 unsuitable rate: {b['bottom_quartile_unsuitable_rate']:.1%}",f"- top-bottom gradient: {b['quartile_gradient']:.1%}",
      f"- ranking gate: {'PASS' if b['ranking_gate_pass'] else 'FAIL'}","",
      "Fixed threshold 0.75 is diagnostic only:",f"- precision: {bt['precision']:.1%}",f"- recall: {bt['recall']:.1%}",f"- F1: {bt['f1']:.1%}","",
      "## EXCLUDE ranking","",f"- AUC: {e['auc']:.3f}","Fixed threshold 0.90 is diagnostic only:",
      f"- precision: {et['precision']:.1%}",f"- recall: {et['recall']:.1%}",f"- F1: {et['f1']:.1%}","",
      f"Ranking priority authorized: {'YES' if report['ranking_priority_authorized'] else 'NO'}.",
      "Automatic REVIEW authorized: NO.","Automatic EXCLUDE authorized: NO.","V59 mix finalized: NO.","Model training authorized: NO.",""]
    RESULTS.write_text("\n".join(lines),encoding="utf-8")

def metrics(r):
    b=r["unsuitable"]; e=r["exclude"]; bt=b["threshold_metrics"]; et=e["threshold_metrics"]
    return {"V59_HOLDOUT004_TRAIN_LABELS":216,"V59_HOLDOUT004_REVIEWED":72,"V59_HOLDOUT004_TOTAL_REVIEWED":288,"V59_HOLDOUT004_REMAINING":792,
      "V59_HOLDOUT004_SELECTION_USES_SCORE":0,"V59_HOLDOUT004_SCORES_BLINDED":1,
      "V59_HOLDOUT004_BAD_AUC_BP":bp(b["auc"]),"V59_HOLDOUT004_TOP_BAD_BP":bp(b["top_quartile_unsuitable_rate"]),
      "V59_HOLDOUT004_BOTTOM_BAD_BP":bp(b["bottom_quartile_unsuitable_rate"]),"V59_HOLDOUT004_GRADIENT_BP":bp(b["quartile_gradient"]),
      "V59_HOLDOUT004_BAD_TP":bt["tp"],"V59_HOLDOUT004_BAD_FP":bt["fp"],"V59_HOLDOUT004_BAD_FN":bt["fn"],
      "V59_HOLDOUT004_BAD_PREC_BP":bp(bt["precision"]),"V59_HOLDOUT004_BAD_RECALL_BP":bp(bt["recall"]),"V59_HOLDOUT004_BAD_F1_BP":bp(bt["f1"]),
      "V59_HOLDOUT004_EXCLUDE_AUC_BP":bp(e["auc"]),"V59_HOLDOUT004_EXCLUDE_TP":et["tp"],"V59_HOLDOUT004_EXCLUDE_FP":et["fp"],"V59_HOLDOUT004_EXCLUDE_FN":et["fn"],
      "V59_HOLDOUT004_EXCLUDE_PREC_BP":bp(et["precision"]),"V59_HOLDOUT004_EXCLUDE_RECALL_BP":bp(et["recall"]),"V59_HOLDOUT004_EXCLUDE_F1_BP":bp(et["f1"]),
      "V59_HOLDOUT004_RANKING_GATE":int(b["ranking_gate_pass"]),"V59_HOLDOUT004_RANK_PRIORITY_AUTHORIZED":int(r["ranking_priority_authorized"]),
      "V59_AUTOMATIC_REVIEW_AUTHORIZED":0,"V59_AUTOMATIC_EXCLUDE_AUTHORIZED":0,"V59_MIX_FINALIZED":0,"SEMANTIC_VALIDATION_COMPLETE":1,"TRAINING_AUTHORIZED":0}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--write",action="store_true"); ap.add_argument("--from-report",action="store_true"); args=ap.parse_args()
    r=json.loads(REPORT.read_text(encoding="utf-8")) if args.from_report else build()
    if args.write: write(r)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for k,v in sorted(metrics(r).items()): print(f"{k}: {v}")

if __name__=="__main__": main()
