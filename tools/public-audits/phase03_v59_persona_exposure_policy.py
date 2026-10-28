#!/usr/bin/env python3
import importlib.util, json, sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/"tools"/"phase03_v59_persona_exposure_policy.py"
REPORT=REPO/"reviews"/"smoltalk-v59-persona-exposure-policy"/"REPORT-001.json"

spec=importlib.util.spec_from_file_location("phase03_v59_persona_exposure_public",SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load persona exposure policy")
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)

report=json.loads(REPORT.read_text(encoding="utf-8"))
print("##### SECTION RESULTS FOR ASSISTANT ######")
for key,value in sorted(module.metrics(report).items()):
    print(f"{key}: {value}")
