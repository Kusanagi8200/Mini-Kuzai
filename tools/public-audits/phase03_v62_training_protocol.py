#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "tools/phase03_v62_training_protocol.py"
REPORT = REPO / "reviews/smoltalk-v62-training-protocol/REPORT-001.json"

module_spec = importlib.util.spec_from_file_location(
    "phase03_v62_training_protocol_public",
    SOURCE,
)
if module_spec is None or module_spec.loader is None:
    raise RuntimeError("Unable to load V62 public audit producer")

module = importlib.util.module_from_spec(module_spec)
sys.modules[module_spec.name] = module
module_spec.loader.exec_module(module)

report = json.loads(REPORT.read_text(encoding="utf-8"))

print("##### SECTION RESULTS FOR ASSISTANT ######")
for key, value in sorted(module.metrics(report).items()):
    print(f"{key}: {value}")
