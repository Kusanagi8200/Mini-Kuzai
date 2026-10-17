#!/usr/bin/env python3
"""Run and resume the complete Phase 03 V54 B02 validation pipeline.

One start command. The runner is idempotent at the GOGIT gate level:
already-published passing STEP_IDs are verified and skipped; missing gates
are executed in order. Semantic data is never rewritten by this runner.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
HISTORY=ROOT/"reports/assistant-results/history"
PY=sys.executable

GATES=[
    {
        "name":"B02_INTEGRITY",
        "step":"PHASE03-SMOLTALK-V54-B02-VALIDATION-INTEGRITY-001",
        "audit":"tools/public-audits/phase03_v54_b02_validation_integrity.py",
        "test":"test_phase03_v54_b02_validation_integrity.py",
        "env":{},
        "expected":{
            "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
            "VALIDATION_B02_CANDIDATES":2,
            "CROSS_SPLIT_ID_COLLISIONS":0,"CROSS_SPLIT_GROUP_COLLISIONS":0,
            "EXACT_USER_PROMPT_MATCHES":0,"B02_INDEPENDENT_SIGNOFF":1,
            "B02_VALIDATION_FROZEN":0,"VALIDATION_FROZEN_RECORDS":2,
            "VALIDATION_BEHAVIORS_FROZEN":1,"TRAINING_AUTHORIZED":0,
        },
    },
    {
        "name":"B02_FREEZE",
        "step":"PHASE03-SMOLTALK-V54-B02-VALIDATION-FREEZE-001",
        "audit":"tools/public-audits/phase03_v54_b02_validation_freeze.py",
        "test":"test_phase03_v54_b02_validation_freeze.py",
        "env":{"MINI_KUZAI_REQUIRE_B02_FREEZE_TEST":"1"},
        "expected":{
            "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
            "VALIDATION_B02_CANDIDATES":2,
            "CROSS_SPLIT_ID_COLLISIONS":0,"CROSS_SPLIT_GROUP_COLLISIONS":0,
            "EXACT_USER_PROMPT_MATCHES":0,"B02_INDEPENDENT_SIGNOFF":1,
            "B02_VALIDATION_FROZEN":1,"VALIDATION_FROZEN_RECORDS":4,
            "VALIDATION_BEHAVIORS_FROZEN":2,"TRAINING_AUTHORIZED":0,
        },
    },
]

def run(args,env=None,capture=False):
    merged=None
    if env:
        import os
        merged=os.environ.copy(); merged.update(env)
    p=subprocess.run(args,cwd=ROOT,text=True,env=merged,
                     stdout=subprocess.PIPE if capture else None,
                     stderr=subprocess.STDOUT if capture else None,
                     check=False)
    return p

def git(*args,capture=True):
    p=run(["git","-C",str(ROOT),*args],capture=capture)
    if p.returncode:
        raise RuntimeError("git {} failed: {}".format(" ".join(args), (p.stdout or "").strip()))
    return (p.stdout or "").strip()

def history_report(step):
    path=HISTORY/(step+".json")
    if not path.is_file(): return None
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise RuntimeError("Invalid history JSON for "+step)
    return value

def verify_published(gate):
    report=history_report(gate["step"])
    if report is None: return False
    if report.get("step_id")!=gate["step"]:
        raise RuntimeError("Published STEP_ID mismatch for "+gate["name"])
    if report.get("source")!="Mini-Kuzai Phase 03 designed validation corpus":
        raise RuntimeError("Unexpected GOGIT source for "+gate["name"])
    if report.get("training_authorized") is not False:
        raise RuntimeError("Unexpected training authorization in "+gate["name"])
    metrics=report.get("metrics",{})
    for key,value in gate["expected"].items():
        if metrics.get(key)!=value:
            raise RuntimeError("{} published metric mismatch: {} expected {} got {}".format(
                gate["name"],key,value,metrics.get(key)))
    return True

def require_clean_main_and_sync():
    if git("branch","--show-current")!="main": raise RuntimeError("Expected branch main")
    if git("status","--porcelain"): raise RuntimeError("Worktree/index must be clean")
    p=run(["git","-C",str(ROOT),"pull","--ff-only","origin","main"],capture=True)
    if p.returncode:
        raise RuntimeError("git pull --ff-only failed: "+(p.stdout or "").strip())
    if git("status","--porcelain"): raise RuntimeError("Worktree changed after pull")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local main and origin/main differ after synchronization")

def compile_pipeline():
    files=[
        "tools/public-audits/phase03_v54_b02_validation_integrity.py",
        "tools/public-audits/phase03_v54_b02_validation_freeze.py",
        "tests/phase-03/test_phase03_v54_b02_validation_integrity.py",
        "tests/phase-03/test_phase03_v54_b02_validation_freeze.py",
        "tools/gogit_public.py",
        "tools/run_phase03_v54_b02_validation.py",
    ]
    p=run([PY,"-m","py_compile",*files],capture=True)
    if p.returncode: raise RuntimeError("py_compile failed:\n"+(p.stdout or ""))

def run_gate(gate):
    if verify_published(gate):
        print("SKIP {}: already published and verified".format(gate["name"]))
        return
    print("RUN {}: tests".format(gate["name"]))
    p=run([PY,"-m","unittest","discover","-s","tests/phase-03","-p",gate["test"],"-v"],
          env=gate["env"],capture=True)
    if p.returncode:
        raise RuntimeError("{} tests failed:\n{}".format(gate["name"],p.stdout or ""))
    print("RUN {}: direct audit".format(gate["name"]))
    p=run([PY,gate["audit"]],env=gate["env"],capture=True)
    if p.returncode:
        raise RuntimeError("{} audit failed:\n{}".format(gate["name"],p.stdout or ""))
    print("RUN {}: GOGIT publish".format(gate["name"]))
    p=run([PY,"tools/gogit_public.py","--step",gate["step"],"--audit",gate["audit"]],
          env=gate["env"],capture=True)
    if p.returncode:
        raise RuntimeError("{} GOGIT failed:\n{}".format(gate["name"],p.stdout or ""))
    if not verify_published(gate):
        raise RuntimeError("{} GOGIT returned success but history is missing".format(gate["name"]))
    print("PASS {}: published and verified".format(gate["name"]))

def main():
    try:
        require_clean_main_and_sync()
        compile_pipeline()
        # Loop semantics: resume any gate not yet validated; stop only on a real failure.
        while True:
            pending=[g for g in GATES if not verify_published(g)]
            if not pending: break
            before=len(pending)
            for gate in GATES:
                run_gate(gate)
            after=len([g for g in GATES if not verify_published(g)])
            if after>=before:
                raise RuntimeError("Pipeline made no progress")
        final=history_report(GATES[-1]["step"])
        metrics=final["metrics"]
        print(MARKER)
        print("B02_PIPELINE_COMPLETE: 1")
        print("B02_INDEPENDENT_SIGNOFF: {}".format(metrics["B02_INDEPENDENT_SIGNOFF"]))
        print("B02_VALIDATION_FROZEN: {}".format(metrics["B02_VALIDATION_FROZEN"]))
        print("VALIDATION_FROZEN_RECORDS: {}".format(metrics["VALIDATION_FROZEN_RECORDS"]))
        print("VALIDATION_BEHAVIORS_FROZEN: {}".format(metrics["VALIDATION_BEHAVIORS_FROZEN"]))
        print("TRAINING_AUTHORIZED: {}".format(metrics["TRAINING_AUTHORIZED"]))
        print("GOGIT: READY")
    except Exception as exc:
        print(MARKER)
        print("B02_PIPELINE_COMPLETE: 0")
        print("ERROR:",str(exc))
        sys.exit(1)

if __name__=="__main__":
    main()
