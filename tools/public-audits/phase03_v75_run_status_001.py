#!/usr/bin/env python3
"""Numeric-only V75 scientific-run status publisher.

Reads a local numeric status artifact produced by the reviewed V75 run wrapper.
No raw stdout/stderr, prompts, token IDs, hidden states or private data are read
or published.
"""
from __future__ import annotations

import json
from pathlib import Path

STATUS = Path("/root/Mini-Kuzai/runs/v75-scientific-run-status-001.json")
EXPECTED_KEYS = {
    "V75_RUN_STATUS_PASS",
    "V75_RUN_STATUS_ATTEMPTED",
    "V75_RUN_STATUS_RUNNER_EXIT",
    "V75_RUN_STATUS_FAILURE_CODE",
    "V75_RUN_STATUS_TIMEOUT",
    "V75_RUN_STATUS_OOM",
    "V75_RUN_STATUS_SYNC_FAIL",
    "V75_RUN_STATUS_PIN_FAIL",
    "V75_RUN_STATUS_V62_GATE_FAIL",
    "V75_RUN_STATUS_CPU_TEST_FAIL",
    "V75_RUN_STATUS_PREREQ_FAIL",
    "V75_RUN_STATUS_GEOMETRY_FAIL",
    "V75_RUN_STATUS_REPLAY_FAIL",
    "V75_RUN_STATUS_GOGIT_FAIL",
    "V75_RUN_STATUS_SCIENTIFIC_REPORT_PRESENT",
    "V75_RUN_STATUS_SAFE_FAILURE_CODE",
}


def main():
    if not STATUS.is_file() or STATUS.is_symlink():
        raise RuntimeError("V75 numeric run-status artifact missing or unsafe")
    obj = json.loads(STATUS.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or set(obj) != EXPECTED_KEYS:
        raise RuntimeError("V75 run-status schema mismatch")
    if any(type(v) is not int or not 0 <= v <= 100_000_000 for v in obj.values()):
        raise RuntimeError("V75 run-status value invalid")
    if obj["V75_RUN_STATUS_ATTEMPTED"] != 1:
        raise RuntimeError("V75 run-status attempt marker missing")
    if obj["V75_RUN_STATUS_PASS"] not in (0, 1):
        raise RuntimeError("V75 run-status pass marker invalid")
    if not 0 <= obj["V75_RUN_STATUS_SAFE_FAILURE_CODE"] <= 99:
        raise RuntimeError("V75 safe failure code invalid")

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        **obj,
    }
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
