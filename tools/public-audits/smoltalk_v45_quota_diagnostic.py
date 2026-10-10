#!/usr/bin/env python3
"""V45: SmolTalk v0.4 aggregate quota diagnostics from local V44 report."""
import json
from pathlib import Path
p = Path("/root/Mini-Kuzai/data/external/smol-smoltalk/review/stratified-audit-v44.json")
d = json.loads(p.read_text(encoding="utf-8"))
assert d["step"] == "PHASE03-SMOLTALK-V44"
assert d["training_approved"] is False
assert d["semantic_review_complete"] is False
assert d["target_records"] == 1200
selected = d["selected_by_heuristic_category"]
available = d["available_by_heuristic_category"]
target = d["target_by_category"]
sources = d["selected_by_source"]
source_target = d["target_by_source"]
mapping = {
 "smol-magpie-ultra-short": ("SOURCE_SMOL_SELECTED", "SOURCE_SMOL_SHORTFALL"),
 "openhermes-50k": ("SOURCE_HERMES_SELECTED", "SOURCE_HERMES_SHORTFALL"),
 "self-oss-instruct": ("SOURCE_OSS_SELECTED", "SOURCE_OSS_SHORTFALL"),
 "explore-instruct-rewrite": ("SOURCE_REWRITE_SELECTED", "SOURCE_REWRITE_SHORTFALL"),
}
total = d["selected_records"]
assert total == sum(selected.values()) == sum(sources.values())
assert 0 <= total <= 1200
assert all(0 <= selected.get(k,0) <= target[k] for k in target)
assert all(0 <= sources.get(k,0) <= source_target[k] for k in source_target)
assert all(isinstance(v,int) and v >= 0 for v in d["selected_turn_structure"].values())
assert sum(d["selected_turn_structure"].values()) == total
m = {
 "TOTAL_SOURCE": 8000,
 "TOTAL_CANDIDATS": total,
 "CREATIVE_AVAILABLE": available.get("CREATIVE",0),
 "CREATIVE_SELECTED": selected.get("CREATIVE",0),
 "CREATIVE_SHORTFALL": target["CREATIVE"]-selected.get("CREATIVE",0),
 "CATEGORY_SHORTFALL_TOTAL": sum(target[k]-selected.get(k,0) for k in target),
 "SOURCE_SHORTFALL_TOTAL": sum(source_target[k]-sources.get(k,0) for k in source_target),
 "SINGLE_TURN": int(d["selected_turn_structure"].get("2",0)),
 "MULTITURN": sum(int(v) for k,v in d["selected_turn_structure"].items() if str(k) != "2"),
}
for source,(a,b) in mapping.items():
 m[a] = sources.get(source,0)
 m[b] = source_target[source]-sources.get(source,0)
assert all(type(v) is int and v >= 0 for v in m.values())
assert m["TOTAL_CANDIDATS"] == m["SINGLE_TURN"] + m["MULTITURN"]
print("##### SECTION RESULTS FOR ASSISTANT ######")
for k,v in sorted(m.items()):
 print(f"{k}: {v}")
