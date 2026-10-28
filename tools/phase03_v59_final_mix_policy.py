#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
MIX_PATH=REPO/"tools"/"phase03_v59_final_candidate_mix.py"
OUT=REPO/"reviews"/"smoltalk-v59-final-mix-policy"
SAMPLE_MANIFESTS=[
 REPO/"reviews"/"smoltalk-v59-bulk-sample-001"/"DECISIONS-001.json",
 REPO/"reviews"/"smoltalk-v59-bulk-sample-002"/"DECISIONS-002.json",
 REPO/"reviews"/"smoltalk-v59-active-sample-003"/"DECISIONS-003.json",
 REPO/"reviews"/"smoltalk-v59-independent-holdout-004"/"DECISIONS-004.json"]
SHA_RE=re.compile(r"^Public content SHA-256: ([0-9a-f]{64})$",re.M)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError("module load failed")
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
MIX=load("v59_final_mix_policy_base",MIX_PATH)

def field(text,key):
    m=re.search(rf"^{re.escape(key)}: (.+)$",text,re.M)
    if m is None: raise RuntimeError("missing field "+key)
    return m.group(1).strip()

def sample_reviews():
    out={}
    for manifest in SAMPLE_MANIFESTS:
        data=json.loads(manifest.read_text(encoding="utf-8"))
        decisions=data.get("decisions")
        if not isinstance(decisions,list) or len(decisions)!=72: raise RuntimeError("sample review count changed")
        for d in decisions:
            path=REPO/d["path"]; text=path.read_text(encoding="utf-8"); m=SHA_RE.search(text)
            if m is None: raise RuntimeError("missing sample source sha")
            sha=m.group(1)
            if sha in out: raise RuntimeError("duplicate sample-reviewed source")
            out[sha]={
              "grade":d["grade"],"risk":d["factual_risk"],"fit":d["instruction_fit"],
              "persona":d["persona_value"],"disposition":d["disposition"],
              "defect_tags":d.get("defect_tags",[]),"source":"V59_SAMPLE_REVIEW"}
    if len(out)!=288: raise RuntimeError("expected 288 sample-reviewed sources")
    return out

def structured_reviews():
    base=MIX.reviewed_exclusions()["reviewed"]; out={}
    for cycle,directory in MIX.REVIEW_DIRS:
        for path in sorted(directory.glob("*.md")):
            text=path.read_text(encoding="utf-8"); m=SHA_RE.search(text)
            if m is None: raise RuntimeError("missing structured source sha")
            sha=m.group(1)
            if sha not in base: raise RuntimeError("structured review mismatch")
            scores={}
            for key in ("cognition","creativity","continuity","correction","communication"):
                scores[key]=int(field(text,f"{cycle} {key}"))
            out[sha]={
              "grade":field(text,f"{cycle} grade"),
              "risk":field(text,f"{cycle} factual risk"),
              "fit":field(text,f"{cycle} instruction fit"),
              "behavior_scores":scores,
              "behavior_total":sum(scores.values()),
              "source":cycle}
    if len(out)!=56: raise RuntimeError("expected 56 structured reviews")
    return out

def candidate_rows():
    queue=list(MIX.read_jsonl(MIX.V50_QUEUE))
    if len(queue)!=1139: raise RuntimeError("V50 queue changed")
    queue_by_sha={r["source_content_sha256"]:r for r in queue}
    reviews=MIX.reviewed_exclusions()
    tokenizer=MIX.V57.load_tokenizer(); count_text=MIX.V57.make_fast_counter(tokenizer)
    rows={}
    excluded=Counter()
    for row in MIX.V57.load_v44():
        sha=row["source_content_sha256"]; q=queue_by_sha[sha]
        pair_counts=MIX.SEG.pair_token_counts(row["messages"],serialize_messages=MIX.V57.CONV.serialize_messages,
            validate_messages=MIX.V57.CONV.validate_messages,count_text=count_text)
        if max(pair_counts)>MIX.CONTEXT:
            excluded["oversized"]+=1; continue
        if sha in MIX.CONTROLLED_SOURCE_SHAS:
            excluded["controlled_source"]+=1; continue
        if sha in reviews["union"]:
            excluded["known_negative"]+=1; continue
        seg=MIX.SEG.segment_messages(row["messages"],serialize_messages=MIX.V57.CONV.serialize_messages,
            validate_messages=MIX.V57.CONV.validate_messages,count_text=count_text,context_length=MIX.CONTEXT)
        rows[sha]={
          "sha":sha,"priority":q["priority_hint"],"category":row["heuristic_category"],
          "source_dataset":row["source_dataset"],"turn_bucket":"MULTITURN" if len(row["messages"])>2 else "SINGLE",
          "segments":len(seg),"tokens":sum(x.token_count for x in seg)}
    if excluded!=Counter({"known_negative":22,"oversized":3,"controlled_source":2}): raise RuntimeError("base exclusion accounting changed")
    if len(rows)!=1112: raise RuntimeError("expected 1112 V59 candidates")
    return rows,excluded

def classify():
    rows,base_excl=candidate_rows(); samples=sample_reviews(); structured=structured_reviews()
    groups=defaultdict(list); metadata={}
    for sha,row in rows.items():
        if sha in samples:
            r=samples[sha]; disp=r["disposition"]
            if disp=="KEEP":
                if r["grade"]!="A" or r["risk"]!="LOW" or r["fit"]!="GOOD": raise RuntimeError("KEEP quality invariant failed")
                bucket="DIRECT_KEEP"
                persona_tier="PERSONA_CORE" if r["persona"] in {"HIGH","MEDIUM"} else "GENERAL_SUPPORT"
            elif disp=="REPAIR":
                bucket="REPAIR_QUEUE"; persona_tier="REPAIR_PERSONA" if r["persona"] in {"HIGH","MEDIUM"} else "REPAIR_GENERAL"
            elif disp=="EXCLUDE":
                bucket="EXCLUDE_REVIEWED"; persona_tier="EXCLUDE"
            else: raise RuntimeError("invalid sample disposition")
            metadata[sha]={**row,**r,"bucket":bucket,"persona_tier":persona_tier}
        elif sha in structured:
            r=structured[sha]
            clean=r["grade"]=="A" and r["risk"]=="LOW" and r["fit"]=="GOOD"
            bucket="DIRECT_KEEP" if clean else "REPAIR_QUEUE"
            persona_tier="LEGACY_STRUCTURED_KEEP" if clean else "LEGACY_STRUCTURED_REPAIR"
            metadata[sha]={**row,**r,"bucket":bucket,"persona_tier":persona_tier}
        else:
            metadata[sha]={**row,"bucket":"DEFER_UNREVIEWED","persona_tier":"UNREVIEWED"}
        groups[metadata[sha]["bucket"]].append(sha)

    if len(set().union(*(set(v) for v in groups.values())))!=1112: raise RuntimeError("policy accounting overlap")
    if sum(len(v) for v in groups.values())!=1112: raise RuntimeError("policy accounting mismatch")
    if len(samples)!=288: raise RuntimeError("sample review accounting changed")
    retained_structured=sum(sha in rows for sha in structured)
    if retained_structured!=32: raise RuntimeError("expected 32 structured retained candidates")

    stats={}
    for bucket in ("DIRECT_KEEP","REPAIR_QUEUE","EXCLUDE_REVIEWED","DEFER_UNREVIEWED"):
        vals=[metadata[s] for s in groups[bucket]]
        stats[bucket]={
          "conversations":len(vals),"segments":sum(v["segments"] for v in vals),"tokens":sum(v["tokens"] for v in vals),
          "priority":dict(Counter(v["priority"] for v in vals)),
          "category":dict(Counter(v["category"] for v in vals)),
          "persona_tier":dict(Counter(v["persona_tier"] for v in vals))}
    direct=[metadata[s] for s in groups["DIRECT_KEEP"]]
    controlled_tokens=sum(MIX.V57.serialized_length(row["messages"],MIX.V57.make_fast_counter(MIX.V57.load_tokenizer())) for row in MIX.V57.load_train())
    if controlled_tokens!=24539: raise RuntimeError("controlled token count changed")
    ready_public=sum(v["tokens"] for v in direct)
    report={
      "schema_version":"v59-final-mix-policy-1","status":"POLICY_DEFINED_NOT_FINALIZED",
      "raw_v44":1139,"base_exclusions":dict(base_excl),"candidate_population":1112,
      "sample_reviewed":288,"structured_reviewed_total":56,"structured_retained":retained_structured,
      "candidate_reviewed_total":288+retained_structured,
      "policy":{
        "direct_keep_rule":"Human-reviewed clean only. Sample KEEP requires A/LOW/GOOD. Structured V51/V52 requires A/LOW/GOOD.",
        "repair_rule":"Reviewed useful-but-imperfect material is never admitted unchanged.",
        "exclude_rule":"Reviewed EXCLUDE is removed from the future training mix.",
        "unreviewed_rule":"Never-reviewed candidates are deferred and not admitted to V59 training.",
        "persona_rule":"Persona HIGH/MEDIUM is prioritized inside clean reviewed KEEP. Persona priority never overrides a known quality defect."
      },
      "groups":stats,
      "ready_now_public_tokens":ready_public,
      "controlled_train_tokens":controlled_tokens,
      "ready_now_combined_tokens":ready_public+controlled_tokens,
      "ready_now_public_tpp":ready_public/MIX.PARAMETERS,
      "ready_now_combined_tpp":(ready_public+controlled_tokens)/MIX.PARAMETERS,
      "automatic_filtering_used":False,
      "unreviewed_admitted":False,
      "repair_admitted_unchanged":False,
      "mix_finalized":False,
      "training_authorized":False
    }
    manifests={bucket:sorted(groups[bucket]) for bucket in groups}
    return report,manifests,metadata

def write(report,manifests,metadata):
    if OUT.exists() or OUT.is_symlink(): raise RuntimeError("final-mix policy output already exists")
    OUT.mkdir(parents=True)
    (OUT/"REPORT-001.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    for bucket,shas in sorted(manifests.items()):
        rows=[metadata[s] for s in shas]
        payload={"schema_version":"v59-final-mix-policy-list-1","bucket":bucket,"count":len(rows),"training_authorized":False,
                 "items":[{"sha":r["sha"],"tokens":r["tokens"],"segments":r["segments"],"priority":r["priority"],
                           "category":r["category"],"source_dataset":r["source_dataset"],"persona_tier":r["persona_tier"]} for r in rows]}
        (OUT/(bucket.lower().replace("_","-")+"-001.json")).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    g=report["groups"]
    lines=["# Mini-Kuzai V59 - final mix policy 001","",
      "Status --> **POLICY DEFINED / MIX NOT FINALIZED / TRAINING NOT AUTHORIZED**","",
      "## Conservative admission policy","",
      "- DIRECT_KEEP --> only human-reviewed clean examples",
      "- REPAIR_QUEUE --> never admitted unchanged",
      "- EXCLUDE_REVIEWED --> removed from the future V59 training mix",
      "- DEFER_UNREVIEWED --> never-reviewed candidates remain outside the V59 training mix",
      "- persona priority --> HIGH/MEDIUM persona value is prioritized only after quality gates pass","",
      "## Candidate accounting","",
      "| Bucket | Conversations | Segments | Tokens |","| --- | ---: | ---: | ---: |"]
    for bucket in ("DIRECT_KEEP","REPAIR_QUEUE","EXCLUDE_REVIEWED","DEFER_UNREVIEWED"):
        x=g[bucket]; lines.append(f"| {bucket} | {x['conversations']} | {x['segments']} | {x['tokens']} |")
    lines+=["","## Ready-now data envelope","",
      f"- controlled TRAIN tokens --> {report['controlled_train_tokens']}",
      f"- clean reviewed public tokens --> {report['ready_now_public_tokens']}",
      f"- combined ready-now tokens --> {report['ready_now_combined_tokens']}",
      f"- public tokens / V58 parameter --> {report['ready_now_public_tpp']:.3f}",
      f"- combined tokens / V58 parameter --> {report['ready_now_combined_tpp']:.3f}","",
      "Automatic filtering used --> **NO**",
      "Unreviewed public data admitted --> **NO**",
      "REPAIR admitted unchanged --> **NO**",
      "V59 final mix --> **NOT FINALIZED**",
      "Model training --> **NOT AUTHORIZED / NOT STARTED**","",
      "---","","##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**",""]
    (OUT/"RESULTS-001.md").write_text("\n".join(lines),encoding="utf-8")

def metrics(r):
    g=r["groups"]
    return {
      "V59_POLICY_CANDIDATE_POP":r["candidate_population"],"V59_POLICY_REVIEWED_CANDIDATE_TOTAL":r["candidate_reviewed_total"],
      "V59_POLICY_DIRECT_KEEP":g["DIRECT_KEEP"]["conversations"],"V59_POLICY_DIRECT_KEEP_TOKENS":g["DIRECT_KEEP"]["tokens"],
      "V59_POLICY_REPAIR_QUEUE":g["REPAIR_QUEUE"]["conversations"],"V59_POLICY_REPAIR_TOKENS":g["REPAIR_QUEUE"]["tokens"],
      "V59_POLICY_EXCLUDE_REVIEWED":g["EXCLUDE_REVIEWED"]["conversations"],"V59_POLICY_EXCLUDE_TOKENS":g["EXCLUDE_REVIEWED"]["tokens"],
      "V59_POLICY_DEFER_UNREVIEWED":g["DEFER_UNREVIEWED"]["conversations"],"V59_POLICY_DEFER_TOKENS":g["DEFER_UNREVIEWED"]["tokens"],
      "V59_POLICY_PERSONA_CORE_KEEP":g["DIRECT_KEEP"]["persona_tier"].get("PERSONA_CORE",0),
      "V59_POLICY_GENERAL_SUPPORT_KEEP":g["DIRECT_KEEP"]["persona_tier"].get("GENERAL_SUPPORT",0),
      "V59_POLICY_LEGACY_STRUCTURED_KEEP":g["DIRECT_KEEP"]["persona_tier"].get("LEGACY_STRUCTURED_KEEP",0),
      "V59_POLICY_READY_PUBLIC_TOKENS":r["ready_now_public_tokens"],"V59_POLICY_READY_COMBINED_TOKENS":r["ready_now_combined_tokens"],
      "V59_POLICY_AUTOMATIC_FILTERING_USED":0,"V59_POLICY_UNREVIEWED_ADMITTED":0,"V59_POLICY_REPAIR_ADMITTED_UNCHANGED":0,
      "V59_MIX_FINALIZED":0,"SEMANTIC_VALIDATION_COMPLETE":1,"TRAINING_AUTHORIZED":0}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--write",action="store_true"); ap.add_argument("--from-report",action="store_true"); args=ap.parse_args()
    if args.from_report:
        report=json.loads((OUT/"REPORT-001.json").read_text(encoding="utf-8"))
    else:
        report,manifests,metadata=classify()
        if args.write: write(report,manifests,metadata)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for k,v in sorted(metrics(report).items()): print(f"{k}: {v}")

if __name__=="__main__": main()
