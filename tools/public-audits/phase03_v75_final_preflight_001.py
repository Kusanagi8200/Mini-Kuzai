#!/usr/bin/env python3
"""V75 FINAL DEV-FLOW read-only preflight for GOGIT.

This audit performs no GitHub mutation. It validates the immutable V75
scientific report, the published START receipt and the existing Discussion #6,
then runs github_discussions_step.py in dry-run close mode without --publish.
Only numeric aggregate readiness metrics are emitted.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
DISCUSSIONS = ROOT / "tools" / "github_discussions_step.py"
REPORT_REL = (
    "reports/assistant-results/history/"
    "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json"
)
REPORT = ROOT / REPORT_REL
START_RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V75-start.json"
FINAL_REQUEST = ROOT / "automation" / "dev-flow" / "requests" / "V75-final.json"
FINAL_RECEIPT = ROOT / "automation" / "dev-flow" / "receipts" / "V75-final.json"

EXPECTED_STEP_ID = "PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001"
EXPECTED_START_URL = "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6"


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected JSON object")
    return value


def main() -> None:
    if not PYTHON.is_file() or not DISCUSSIONS.is_file() or DISCUSSIONS.is_symlink():
        raise RuntimeError("V75 FINAL preflight tooling unavailable")
    if FINAL_REQUEST.exists() or FINAL_RECEIPT.exists():
        raise RuntimeError("V75 FINAL request/receipt already exists; preflight boundary changed")

    report = read_json(REPORT)
    metrics = report.get("metrics")
    if not (
        report.get("step_id") == EXPECTED_STEP_ID
        and report.get("project") == "Mini-Kuzai"
        and report.get("phase") == "03"
        and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and report.get("semantic_validation_complete") is False
        and report.get("training_authorized") is False
        and report.get("private_conversation_data_included") is False
        and isinstance(metrics, dict)
        and len(metrics) == 30
        and metrics.get("V75_PASS") == 1
        and metrics.get("V75_BLIND_ACCESS") == 0
        and metrics.get("TRAINING_STARTED") == 0
        and metrics.get("TRAINING_AUTHORIZED") == 0
        and metrics.get("V75_COVERAGE_BP") == 10000
    ):
        raise RuntimeError("V75 immutable scientific report gate failed")

    receipt = read_json(START_RECEIPT)
    if not (
        receipt.get("schema_version") == 1
        and receipt.get("command") == "START-DEV-FLOW"
        and receipt.get("step") == "V75"
        and receipt.get("status") == "PUBLISHED"
        and receipt.get("github_url") == EXPECTED_START_URL
    ):
        raise RuntimeError("V75 START receipt gate failed")

    proc = subprocess.run(
        [
            str(PYTHON),
            str(DISCUSSIONS),
            "--step",
            "V75",
            "--action",
            "close",
            "--report",
            REPORT_REL,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("V75 FINAL dry-run failed")

    lines = {
        line.strip()
        for line in (proc.stdout or "").splitlines()
        if line.strip()
    }
    expected = {
        "STEP=V75",
        "STEP_ID=" + EXPECTED_STEP_ID,
        "MODE=DRY_RUN",
        "DISCUSSION_URL=" + EXPECTED_START_URL,
        "GOGIT_CLOSURE=READY_TO_COMMENT",
        "PUBLICATION=DISABLED",
    }
    if not expected <= lines:
        raise RuntimeError("V75 FINAL dry-run output gate failed")

    public = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V75_FINAL_PREFLIGHT_PASS": 1,
        "V75_FINAL_PREFLIGHT_BLIND_ACCESS": 0,
        "V75_FINAL_PREFLIGHT_REPORT_FIELDS": len(metrics),
        "V75_FINAL_PREFLIGHT_REPORT_VERIFIED": 1,
        "V75_FINAL_PREFLIGHT_START_RECEIPT": 1,
        "V75_FINAL_PREFLIGHT_DISCUSSION_PRESENT": 1,
        "V75_FINAL_PREFLIGHT_CLOSURE_READY": 1,
        "V75_FINAL_PREFLIGHT_PUBLICATION_DISABLED": 1,
        "V75_FINAL_PREFLIGHT_REQUEST_PRESENT": 0,
        "V75_FINAL_PREFLIGHT_RECEIPT_PRESENT": 0,
        "V75_FINAL_PREFLIGHT_FINAL_AUTHORIZED": 0,
        "V75_FINAL_PREFLIGHT_V75_PASS": metrics["V75_PASS"],
        "V75_FINAL_PREFLIGHT_COVERAGE_BP": metrics["V75_COVERAGE_BP"],
    }
    if any(type(v) is not int or not 0 <= v <= 100_000_000 for v in public.values()):
        raise RuntimeError("V75 FINAL preflight public metric type/range invalid")

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(public.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print("V75_FINAL_PREFLIGHT_SAFE_FAIL: 1")
        sys.exit(1)
