#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/"reviews"/"smoltalk-v59-active-sample-003"
DECISIONS=ROOT/"DECISIONS-003.json"
BUCKETS=("HIGH_RISK_RANK","MIDDLE_RANK","LOW_RISK_RANK","DIVERSITY_CONTROL")

def bp(n,d=18): return int(round(n/d*10000))

def main():
    data=json.loads(DECISIONS.read_text(encoding="utf-8"))
    if data.get("status")!="REVIEW_APPLIED": raise RuntimeError("Sample 003 review not applied")
    decisions=data.get("decisions")
    if not isinstance(decisions,list) or len(decisions)!=72: raise RuntimeError("Expected 72 decisions")
    counts=Counter()
    for d in decisions:
        b=d["selection_bucket"]; disp=d["disposition"]
        if b not in BUCKETS or disp not in {"KEEP","REPAIR","EXCLUDE"}: raise RuntimeError("Unexpected decision value")
        counts[(b,disp)]+=1
    for b in BUCKETS:
        if sum(counts[(b,d)] for d in ("KEEP","REPAIR","EXCLUDE"))!=18: raise RuntimeError("Bucket size changed")
    metrics={"SEMANTIC_VALIDATION_COMPLETE":1,"TRAINING_AUTHORIZED":0,"V59_MIX_FINALIZED":0,
      "V59_ACTIVE003_REVIEWED":72,"V59_ACTIVE003_TOTAL_REVIEWED":216,"V59_ACTIVE003_POPULATION_ESTIMATOR":0,
      "V59_ACTIVE003_HIGH_KEEP":counts[("HIGH_RISK_RANK","KEEP")],"V59_ACTIVE003_HIGH_REPAIR":counts[("HIGH_RISK_RANK","REPAIR")],"V59_ACTIVE003_HIGH_EXCLUDE":counts[("HIGH_RISK_RANK","EXCLUDE")],
      "V59_ACTIVE003_HIGH_UNSUITABLE_BP":bp(counts[("HIGH_RISK_RANK","REPAIR")]+counts[("HIGH_RISK_RANK","EXCLUDE")]),
      "V59_ACTIVE003_MIDDLE_KEEP":counts[("MIDDLE_RANK","KEEP")],"V59_ACTIVE003_MIDDLE_REPAIR":counts[("MIDDLE_RANK","REPAIR")],"V59_ACTIVE003_MIDDLE_EXCLUDE":counts[("MIDDLE_RANK","EXCLUDE")],
      "V59_ACTIVE003_MIDDLE_UNSUITABLE_BP":bp(counts[("MIDDLE_RANK","REPAIR")]+counts[("MIDDLE_RANK","EXCLUDE")]),
      "V59_ACTIVE003_LOW_KEEP":counts[("LOW_RISK_RANK","KEEP")],"V59_ACTIVE003_LOW_REPAIR":counts[("LOW_RISK_RANK","REPAIR")],"V59_ACTIVE003_LOW_EXCLUDE":counts[("LOW_RISK_RANK","EXCLUDE")],
      "V59_ACTIVE003_LOW_UNSUITABLE_BP":bp(counts[("LOW_RISK_RANK","REPAIR")]+counts[("LOW_RISK_RANK","EXCLUDE")]),
      "V59_ACTIVE003_CONTROL_KEEP":counts[("DIVERSITY_CONTROL","KEEP")],"V59_ACTIVE003_CONTROL_REPAIR":counts[("DIVERSITY_CONTROL","REPAIR")],"V59_ACTIVE003_CONTROL_EXCLUDE":counts[("DIVERSITY_CONTROL","EXCLUDE")],
      "V59_ACTIVE003_CONTROL_UNSUITABLE_BP":bp(counts[("DIVERSITY_CONTROL","REPAIR")]+counts[("DIVERSITY_CONTROL","EXCLUDE")])}
    high=metrics["V59_ACTIVE003_HIGH_UNSUITABLE_BP"]; low=metrics["V59_ACTIVE003_LOW_UNSUITABLE_BP"]; control=metrics["V59_ACTIVE003_CONTROL_UNSUITABLE_BP"]
    metrics["V59_ACTIVE003_RANKING_DIRECTION_OK"]=int(high>control and low<control)
    metrics["V59_ACTIVE003_RETRAIN_AUTHORIZED"]=int(metrics["V59_ACTIVE003_RANKING_DIRECTION_OK"]==1)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for k,v in sorted(metrics.items()): print(f"{k}: {v}")

if __name__=="__main__": main()
