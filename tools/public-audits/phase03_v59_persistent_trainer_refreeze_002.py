#!/usr/bin/env python3
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "tools" / "phase03_v59_persistent_trainer_freeze.py"
REPORT = REPO / "reviews" / "smoltalk-v59-persistent-trainer-freeze" / "REPORT-002.json"

spec = importlib.util.spec_from_file_location("v59_refreeze_public", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load V59 trainer freeze metrics")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

report = json.loads(REPORT.read_text(encoding="utf-8"))

print("##### SECTION RESULTS FOR ASSISTANT ######")
for key, value in sorted(module.metrics(report).items()):
    print(f"{key}: {value}")
