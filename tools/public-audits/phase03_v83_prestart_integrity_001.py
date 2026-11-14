#!/usr/bin/env python3
"""V83 pre-START read-only integrity audit. No scientific execution."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
PROTOCOL = ROOT / "phases/MINI-KUZAI-PHASE-03-V83-POST-V81-REFITTED-COORDINATE-CONTEXT-ORDER-CONTROL-001.md"
SOURCE = ROOT / "docs/discussions/steps/V83-start.md"
V82_REPORT = ROOT / "reports/assistant-results/history/PHASE03-SMOLTALK-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001.json"
V82_START = ROOT / "automation/dev-flow/receipts/V82-start.json"
V82_FINAL = ROOT / "automation/dev-flow/receipts/V82-final.json"
V81_FINAL = ROOT / "reports/assistant-results/history/PHASE03-SMOLTALK-V81-FINAL-CLOSURE-001.json"
V83_REQUEST = ROOT / "automation/dev-flow/requests/V83-start.json"
V83_RECEIPT = ROOT / "automation/dev-flow/receipts/V83-start.json"
V83_FINAL_REQUEST = ROOT / "automation/dev-flow/requests/V83-final.json"
V83_FINAL_RECEIPT = ROOT / "automation/dev-flow/receipts/V83-final.json"

def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Required source missing or symlink")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("JSON object expected")
    return value

def main() -> None:
    for path in (PROTOCOL, SOURCE):
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("V83 pre-START source missing or unsafe")
    protocol = PROTOCOL.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8")
    if not (
        "PRE-START PROTOCOL FROZEN / EXECUTION NOT STARTED" in protocol
        and "TRAIN-only" in protocol
        and "START-DEV-FLOW V83" in protocol
        and "V83" in source
        and "checkpoint-last.pt" in source
    ):
        raise RuntimeError("V83 documentation frozen gate failed")
    if any(path.exists() or path.is_symlink() for path in (
        V83_REQUEST, V83_RECEIPT, V83_FINAL_REQUEST, V83_FINAL_RECEIPT
    )):
        raise RuntimeError("V83 has a published request/receipt: pre-START gate invalid")

    report = read_json(V82_REPORT)
    m = report.get("metrics", {})
    if not (
        report.get("step_id") == "PHASE03-SMOLTALK-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("training_authorized") is False
        and report.get("semantic_validation_complete") is False
        and isinstance(m, dict)
        and m.get("V82_PASS") == 1
        and m.get("V82_BASELINE_REPLAY_PASS") == 1
        and m.get("V82_BASELINE_PRED_CHANGED") == 5
        and m.get("V82_FINAL_PRED_CHANGED") == 38
        and m.get("V82_FINAL_SIGN_CHANGED") == 38
        and m.get("V82_VAL_LEXICAL") == 9170
        and m.get("V82_FINAL_EXPOSURE") == 1181302
        and m.get("V82_FINAL_STEPS") == 136
        and m.get("V82_BLIND_ACCESS") == 0
        and m.get("TRAINING_AUTHORIZED") == 0
        and m.get("TRAINING_STARTED") == 0
    ):
        raise RuntimeError("V82 immutable scientific gate failed")

    start = read_json(V82_START)
    final = read_json(V82_FINAL)
    if not (
        start.get("status") == "PUBLISHED"
        and start.get("command") == "START-DEV-FLOW"
        and start.get("step") == "V82"
        and final.get("status") == "PUBLISHED"
        and final.get("command") == "FINAL-DEV-FLOW"
        and final.get("step") == "V82"
    ):
        raise RuntimeError("V82 publication receipt gate failed")
    v81 = read_json(V81_FINAL).get("metrics", {})
    if not (
        v81.get("V81_FINAL_PASS") == 1
        and v81.get("V81_FINAL_FURTHER_TRAINING_AUTHORIZED") == 0
        and v81.get("V81_FINAL_BLIND_ACCESS") == 0
    ):
        raise RuntimeError("V81 closure or authorization gate failed")

    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("Checkpoint directory unsafe or training locked")
    checkpoints = ("checkpoint-cycle-02.pt", "checkpoint-last.pt", "checkpoint-best.pt")
    for filename in checkpoints:
        p = RUN / filename
        if p.is_symlink() or not p.is_file() or p.stat().st_size == 0:
            raise RuntimeError("Checkpoint missing, symlinked, or empty")

    public = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V83_PRESTART_PASS": 1,
        "V83_PRESTART_V82_REPLAY": 1,
        "V83_PRESTART_V82_FINAL_RECEIPT": 1,
        "V83_PRESTART_PROTOCOL": 1,
        "V83_PRESTART_START_SOURCE": 1,
        "V83_PRESTART_CHECKPOINTS": 3,
        "V83_PRESTART_TRAINING_LOCK": 0,
        "V83_PRESTART_PUBLICATION": 0,
        "V83_PRESTART_BLIND_ACCESS": 0,
    }
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(public.items()):
        print(f"{key}: {value}")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError):
        print("V83_PRESTART_SAFE_FAIL: 1", file=sys.stderr)
        sys.exit(1)
