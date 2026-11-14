#!/usr/bin/env python3
"""Public numeric audit for V81 V62 continuation authorization."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "tools" / "phase03_v81_v62_continuation_authorization.py"
ROOT = REPO / "reviews" / "smoltalk-v81-v62-continuation-authorization"
AUTH = ROOT / "TRAINING-AUTHORIZATION-001.json"
FREEZE = ROOT / "CONTINUATION-FREEZE-001.json"
REPORT = ROOT / "REPORT-001.json"

spec = importlib.util.spec_from_file_location(
    "phase03_v81_v62_continuation_authorization_public",
    SOURCE,
)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load V81 continuation authorization producer")

module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

authorization = module.read_json(AUTH)
freeze = module.read_json(FREEZE)
report = module.read_json(REPORT)

# Revalidate every scientific/runtime dependency at publication time.
module.verify_inputs()

if authorization.get("freeze_fingerprint") != module.canonical_sha(freeze):
    raise RuntimeError("V81 continuation authorization fingerprint mismatch")
if authorization.get("training_authorized") is not True:
    raise RuntimeError("V81 continuation is not authorized")
if authorization.get("training_started") is not False:
    raise RuntimeError("V81 authorization already marks training started")
if authorization.get("blind_test_during_training") is not False:
    raise RuntimeError("V81 authorization permits BLIND access")
if report.get("status") != "TRAINING_AUTHORIZED_NOT_STARTED":
    raise RuntimeError("V81 authorization report status mismatch")
if report.get("training_authorized") is not True:
    raise RuntimeError("V81 report does not authorize training")
if report.get("training_started") is not False:
    raise RuntimeError("V81 report already marks training started")
if report.get("blind_test_accessed") is not False:
    raise RuntimeError("V81 report indicates BLIND access")

print("##### SECTION RESULTS FOR ASSISTANT ######")
for key, value in sorted(module.metrics(report).items()):
    print(f"{key}: {value}")
