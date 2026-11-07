#!/usr/bin/env python3
"""V79 CPU regression diagnostic for numeric-only GOGIT publication."""
from __future__ import annotations

import io
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "tests"
TEST_PATTERN = "test_phase03_v79_same_path_context_order_control_001.py"


def first_failure(result):
    entries = [(1, x) for x in result.failures] + [(2, x) for x in result.errors]
    if not entries:
        return 0, 0, 0
    kind, (test, trace) = entries[0]
    name = test.id().rsplit(".", 1)[-1]
    match = re.match(r"test_(\d+)_", name)
    test_no = int(match.group(1)) if match else 0
    line = 0
    for found in re.finditer(
        r'File ".*test_phase03_v79_same_path_context_order_control_001.py", line (\d+)',
        trace,
    ):
        line = int(found.group(1))
    return kind, test_no, line


def main():
    suite = unittest.defaultTestLoader.discover(
        str(TEST_DIR),
        pattern=TEST_PATTERN,
    )
    total = suite.countTestCases()
    result = unittest.TextTestRunner(
        stream=io.StringIO(),
        verbosity=0,
    ).run(suite)
    kind, test_no, line = first_failure(result)

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 0,
        "TRAINING_AUTHORIZED": 0,
        "TRAINING_STARTED": 0,
        "V79_LOOP_PASS": int(result.wasSuccessful()),
        "V79_LOOP_TESTS_TOTAL": total,
        "V79_LOOP_TESTS_FAILED": len(result.failures),
        "V79_LOOP_TESTS_ERRORS": len(result.errors),
        "V79_LOOP_TESTS_SKIPPED": len(result.skipped),
        "V79_LOOP_FIRST_FAIL_KIND": kind,
        "V79_LOOP_FIRST_FAIL_TEST": test_no,
        "V79_LOOP_FIRST_FAIL_LINE": line,
        "V79_LOOP_CPU_ONLY": 1,
        "V79_LOOP_GPU_EXECUTION": 0,
        "V79_LOOP_BLIND_ACCESS": 0,
    }

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
