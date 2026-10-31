#!/usr/bin/env python3
"""Publish sanitized numeric failure classification for the unchanged V68 audit.

Run the original audited V68 entry point in-process, discard its stdout/stderr,
and publish only integer error-class, code-location and predeclared-cause IDs.
Never publish exception text, traceback text, prompt or private content.
No optimizer, no checkpoint writes, no BLIND access, no training authorization.
"""
from __future__ import annotations

import contextlib
import runpy
import sys
import time
import traceback
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/"tools"/"public-audits"/"phase03_v68_output_head_001.py"
KNOWN_CAUSES={
    "Frozen V64-002 helper missing":1,
    "Frozen V64 helper import failed":2,
    "V60 tied output projection or no-bias rule violated":3,
    "Frozen output-head row norms invalid":4,
    "Frozen PAD embedding row nonzero":5,
    "V68 inventory/rank baseline mismatch":6,
    "Nonfinite or negative V68 numeric measurement":7,
    "V68 argmax distribution differs from V66/V67":8,
    "V68 concentration differs from V67":9,
    "V68 cross-entropy changed":10,
    "V68 must publish exactly 30 bounded integer metrics":11,
    "Expected 36 frozen VALIDATION segments":12,
    "Frozen VALIDATION segment boundary changed":13,
    "Frozen EOS target mismatch":14,
    "V68 observed token inventory disagrees with V67":15,
    "Frozen V67 prerequisite invalid":16,
    "Frozen TRAIN inventory changed":17,
}
ERROR_CLASSES={
    "RuntimeError":1,
    "ValueError":2,
    "KeyError":3,
    "AttributeError":4,
    "TypeError":5,
    "FileNotFoundError":6,
    "AssertionError":7,
    "OSError":8,
}
FUNCTION_IDS={
    "frozen_helper":1,
    "summarize_head":2,
    "summarize_numeric":3,
    "evaluate":4,
    "main":5,
}
FILE_FAMILIES={
    "phase03_v68_output_head_001.py":1,
    "phase03_v64_language_learning_diagnostic_002.py":2,
    "phase03_v62_trainer.py":3,
    "phase03_v60_model.py":4,
    "gogit_public.py":5,
}

class DiscardOutput:
    """Drop all diagnostic process output; no user data is buffered."""
    def write(self,value):
        return len(value)
    def flush(self):
        return None

def classify(exc:Exception,frames:list[traceback.FrameSummary]):
    """Only compile-time fixed numeric taxonomy, no dynamic error strings."""
    message=str(exc)
    cause=KNOWN_CAUSES.get(message,0)
    own=[f for f in frames if Path(f.filename).name==SOURCE.name]
    last=frames[-1] if frames else None
    latest=own[-1] if own else None
    return {
        "V68_FAIL_EXCEPTION_CLASS_ID":ERROR_CLASSES.get(type(exc).__name__,99),
        "V68_FAIL_CAUSE_ID":cause,
        "V68_FAIL_SOURCE_LINE":latest.lineno if latest else 0,
        "V68_FAIL_SOURCE_FUNCTION_ID":FUNCTION_IDS.get(latest.name,0) if latest else 0,
        "V68_FAIL_LAST_FILE_FAMILY":FILE_FAMILIES.get(Path(last.filename).name,0) if last else 0,
        "V68_FAIL_LAST_LINE":last.lineno if last else 0,
    }

def numeric_report(exc:Exception|None,frames:list[traceback.FrameSummary],duration:int):
    fields=classify(exc,frames) if exc is not None else {
        "V68_FAIL_EXCEPTION_CLASS_ID":0,
        "V68_FAIL_CAUSE_ID":0,
        "V68_FAIL_SOURCE_LINE":0,
        "V68_FAIL_SOURCE_FUNCTION_ID":0,
        "V68_FAIL_LAST_FILE_FAMILY":0,
        "V68_FAIL_LAST_LINE":0,
    }
    data={
        "SEMANTIC_VALIDATION_COMPLETE":0,
        "TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,
        "V68_FAIL_DIAG_PASS":1,
        "V68_FAIL_BLIND_ACCESS":0,
        "V68_FAIL_ORIGINAL_FAILED":int(exc is not None),
        "V68_FAIL_DURATION_SECONDS":duration,
        **fields,
    }
    if not (len(data)==13 and all(type(v) is int and 0<=v<=100_000_000 for v in data.values())):
        raise RuntimeError("Invalid numeric-only V68 failure-probe report")
    return data

def main():
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("Immutable V68 source missing")
    start=time.monotonic()
    failure=None
    frames=[]
    # Avoid accidental stdout/stderr disclosure from called model dependencies.
    with contextlib.redirect_stdout(DiscardOutput()), contextlib.redirect_stderr(DiscardOutput()):
        try:
            runpy.run_path(str(SOURCE),run_name="__main__")
        except Exception as exc:
            failure=exc
            frames=traceback.extract_tb(exc.__traceback__)
    report=numeric_report(failure,frames,int(time.monotonic()-start))
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key,value in sorted(report.items()):
        print(f"{key}: {value}")

if __name__=="__main__":
    main()
