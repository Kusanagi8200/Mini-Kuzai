#!/usr/bin/env python3
"""Bounded, numeric-only V64 stage timer for diagnosing the 300 s timeout.

The worker runs the unchanged read-only V64 diagnostic under instrumentation.
The parent stops after a fixed 155 s, so existing GOGIT 300 s timeout is
preserved. No model/optimizer mutations, BLIND access, or private text output.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))

AUDIT=REPO/"tools"/"public-audits"/"phase03_v64_language_learning_diagnostic_001.py"
TIMEOUT=155
STAGES=(
    "PREFLIGHT", "VERIFY_RUNTIME", "BUILD_TRAIN", "BUILD_VAL",
    "LOAD_POOL", "LOAD_PUBLIC", "LOAD_CONTROLLED", "SCHEDULE",
    "BOUNDARY", "LOAD_TOKENIZER", "TOKEN_STATS", "SCORE",
    "CHECKPOINT_LOAD",
)
CODES={key:i+1 for i,key in enumerate(STAGES)}


def instrument_worker():
    import torch
    from mini_kuzai import phase03_v62_trainer as T
    spec=importlib.util.spec_from_file_location("v64_trace_original",AUDIT)
    if spec is None or spec.loader is None:
        raise RuntimeError("V64 diagnostic source cannot be loaded")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def wrap(name, func):
        def measured(*args, **kwargs):
            print(f"BEGIN:{name}",flush=True)
            before=time.monotonic_ns()
            value=func(*args,**kwargs)
            elapsed=(time.monotonic_ns()-before)//1_000_000
            print(f"END:{name}:{elapsed}",flush=True)
            return value
        return measured

    def patch(obj, attribute, stage):
        original=getattr(obj,attribute)
        setattr(obj,attribute,wrap(stage,original))

    # Nested intervals identify whether the verified workload is dominated
    # by corpus reconstruction, checkpoint loading or CUDA evaluation.
    for attribute,stage in (
        ("verify_runtime","VERIFY_RUNTIME"),
        ("build_training_streams","BUILD_TRAIN"),
        ("build_validation_segments","BUILD_VAL"),
        ("_load_public_pool","LOAD_POOL"),
        ("_load_public_streams","LOAD_PUBLIC"),
        ("_load_controlled_stream","LOAD_CONTROLLED"),
        ("build_schedule_preview","SCHEDULE"),
        ("build_boundary_index","BOUNDARY"),
        ("load_tokenizer","LOAD_TOKENIZER"),
    ):
        patch(T,attribute,stage)
    patch(module,"preflight","PREFLIGHT")
    patch(module,"tally_token_statistics","TOKEN_STATS")
    patch(module,"score","SCORE")
    # Capture checkpoint loading as a separate span when it is reached.
    patch(torch,"load","CHECKPOINT_LOAD")

    module.main()


def parse(stdout):
    durations={key:0 for key in STAGES}
    open_spans=[]
    last_started=0
    finished=0
    invalid=0
    for line in stdout.splitlines():
        if line.startswith("BEGIN:"):
            key=line.split(":",1)[1]
            if key not in CODES:
                invalid=1
                continue
            open_spans.append(key)
            last_started=CODES[key]
        elif line.startswith("END:"):
            pieces=line.split(":")
            if len(pieces)!=3 or pieces[1] not in CODES:
                invalid=1
                continue
            key=pieces[1]
            if not open_spans or open_spans[-1]!=key:
                invalid=1
                continue
            open_spans.pop()
            try:
                millis=int(pieces[2])
            except ValueError:
                invalid=1
                continue
            if millis<0 or millis>100_000_000:
                invalid=1
                continue
            durations[key]+=millis
            finished+=1
    return durations,open_spans,last_started,finished,invalid


def parent():
    from mini_kuzai import phase03_v62_trainer as T
    if not AUDIT.is_file() or AUDIT.is_symlink():
        raise RuntimeError("Original immutable V64 audit missing")
    if not (Path("/root/Mini-Kuzai/runs/v62-margin-001")/"checkpoint-cycle-02.pt").is_file():
        raise RuntimeError("Frozen V62 checkpoint missing")
    before=time.monotonic_ns()
    expired=False
    exit_code=0
    try:
        p=subprocess.run(
            [sys.executable,str(Path(__file__).resolve()),"--worker"],
            cwd=REPO,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=False,timeout=TIMEOUT,check=False,
        )
        raw=p.stdout or b""
        exit_code=p.returncode
    except subprocess.TimeoutExpired as e:
        raw=e.stdout or b""
        expired=True
    elapsed=(time.monotonic_ns()-before)//1_000_000
    lines=raw.decode("utf-8","replace")
    durations,active,last_started,finished,invalid=parse(lines)
    if invalid or (not expired and exit_code!=0):
        raise RuntimeError("V64 trace worker failed or produced invalid stage markers")
    if not last_started:
        raise RuntimeError("V64 trace worker did not reach the first measured stage")
    active_code=CODES[active[-1]] if active else 0
    output={
        "SEMANTIC_VALIDATION_COMPLETE":0,
        "TRAINING_AUTHORIZED":0,
        "TRAINING_STARTED":0,
        "V64_TRACE_PASS":1,
        "V64_TRACE_BLIND_ACCESS":0,
        "V64_TRACE_TIMEOUT":int(expired),
        "V64_TRACE_BUDGET_SEC":TIMEOUT,
        "V64_TRACE_ELAPSED_MS":elapsed,
        "V64_TRACE_ACTIVE_STAGE":active_code,
        "V64_TRACE_LAST_STARTED":last_started,
        "V64_TRACE_COMPLETED_SPANS":finished,
    }
    for key in STAGES:
        output[f"V64_TRACE_{key}_MS"]=durations[key]
    if len(output)!=11+len(STAGES):
        raise RuntimeError("Unexpected public trace metric count")
    if any(type(value) is not int or value<0 or value>100_000_000 for value in output.values()):
        raise RuntimeError("Trace metric is unsafe")
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key,value in sorted(output.items()):
        print(f"{key}: {value}")


if __name__=="__main__":
    if len(sys.argv)==2 and sys.argv[1]=="--worker":
        instrument_worker()
    elif len(sys.argv)==1:
        parent()
    else:
        raise RuntimeError("Unexpected trace command arguments")
