#!/usr/bin/env python3
"""Master resumable runner for Phase 03 V55 BLIND TEST B01-B18."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/phase-03/manifests/blind-master-v55.json"
HISTORY=ROOT/"reports/assistant-results/history"
PY=sys.executable
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
SOURCE="Mini-Kuzai Phase 03 designed blind-test corpus"

def run(args,capture=False,env=None):
    merged=os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        args,cwd=ROOT,text=True,env=merged,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        check=False,
    )

def git(*args):
    p=run(["git","-C",str(ROOT),*args],capture=True)
    if p.returncode:
        raise RuntimeError("git {} failed: {}".format(" ".join(args),(p.stdout or "").strip()))
    return (p.stdout or "").strip()

def sync():
    if git("branch","--show-current")!="main":
        raise RuntimeError("Expected branch main")
    if git("status","--porcelain"):
        raise RuntimeError("Worktree/index must be clean")
    p=run(["git","-C",str(ROOT),"pull","--ff-only","origin","main"],capture=True)
    if p.returncode:
        raise RuntimeError("git pull --ff-only failed: "+(p.stdout or "").strip())
    if git("status","--porcelain"):
        raise RuntimeError("Worktree changed after pull")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local main and origin/main differ after synchronization")

def load_master():
    if not MASTER.is_file() or MASTER.is_symlink():
        raise RuntimeError("Missing or unsafe V55 BLIND master manifest")
    data=json.loads(MASTER.read_text(encoding="utf-8"))
    allowed_statuses={"REVIEWED_READY_FOR_BLIND_FREEZE","FROZEN_PENDING_GLOBAL_CLOSURE","CLOSED"}
    if (data.get("version")!="V55"
        or data.get("status") not in allowed_statuses
        or data.get("total_behaviors")!=18
        or data.get("target_records")!=36
        or data.get("training_authorized") is not False):
        raise RuntimeError("Unexpected V55 BLIND master state")
    if data.get("status")=="FROZEN_PENDING_GLOBAL_CLOSURE":
        if data.get("freeze_complete") is not True:
            raise RuntimeError("Frozen V55 BLIND master missing freeze_complete=true")
        if data.get("freeze_complete_step_id")!="PHASE03-SMOLTALK-V55-B18-BLIND-FREEZE-001":
            raise RuntimeError("Frozen V55 BLIND master has unexpected completion STEP_ID")
        if data.get("global_blind_closure_complete") is not False:
            raise RuntimeError("BLIND global closure must remain pending at this checkpoint")
    if data.get("status")=="CLOSED":
        if data.get("freeze_complete") is not True:
            raise RuntimeError("Closed V55 BLIND master missing freeze_complete=true")
        if data.get("freeze_complete_step_id")!="PHASE03-SMOLTALK-V55-B18-BLIND-FREEZE-001":
            raise RuntimeError("Closed V55 BLIND master has unexpected freeze STEP_ID")
        if data.get("global_blind_closure_step_id")!="PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001":
            raise RuntimeError("Closed V55 BLIND master has unexpected closure STEP_ID")
        if data.get("global_blind_closure_complete") is not True:
            raise RuntimeError("Closed V55 BLIND master missing global closure")
    behaviors=data.get("behaviors")
    if not isinstance(behaviors,list) or len(behaviors)!=18:
        raise RuntimeError("V55 BLIND behavior inventory invalid")
    expected=["B{:02d}".format(i) for i in range(1,19)]
    if [x.get("behavior") for x in behaviors]!=expected:
        raise RuntimeError("V55 BLIND behavior order invalid")
    return data

def history(step):
    path=HISTORY/(step+".json")
    if not path.is_file():
        return None
    if path.is_symlink():
        raise RuntimeError("Unsafe GOGIT history symlink: "+step)
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise RuntimeError("Invalid GOGIT history JSON: "+step)
    return value

def expected_metrics(cfg,frozen):
    return {
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_RECORDS":36,
        "VALIDATION_GROUPS":18,
        "SEMANTIC_VALIDATION_COMPLETE":1,
        "BLIND_AUTHORING_AUTHORIZED":1,
        "BLIND_BATCH_INDEX":cfg["index"],
        "BLIND_BATCH_CANDIDATES":2,
        "BLIND_BATCH_SIGNOFF":1,
        "BLIND_BATCH_SEMANTIC_PASS":1,
        "BLIND_BATCH_FROZEN":1 if frozen else 0,
        "BLIND_TEST_RECORDS_FROZEN":cfg["cumulative_after_records"] if frozen else cfg["cumulative_before_records"],
        "BLIND_BEHAVIORS_FROZEN":cfg["cumulative_after_behaviors"] if frozen else cfg["cumulative_before_behaviors"],
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "TRAINING_AUTHORIZED":0,
    }

def verify_gate(cfg,gate):
    frozen=(gate=="freeze")
    step=cfg["freeze_step_id"] if frozen else cfg["integrity_step_id"]
    report=history(step)
    if report is None:
        return False
    if report.get("step_id")!=step:
        raise RuntimeError("{} {} STEP_ID mismatch".format(cfg["behavior"],gate))
    if report.get("source")!=SOURCE:
        raise RuntimeError("{} {} source mismatch".format(cfg["behavior"],gate))
    if report.get("semantic_validation_complete") is not True:
        raise RuntimeError("{} {} lost VALIDATION completion flag".format(cfg["behavior"],gate))
    if report.get("training_authorized") is not False:
        raise RuntimeError("{} {} unexpectedly authorizes training".format(cfg["behavior"],gate))
    metrics=report.get("metrics",{})
    for key,value in expected_metrics(cfg,frozen).items():
        if metrics.get(key)!=value:
            raise RuntimeError("{} {} metric mismatch: {} expected {} got {}".format(
                cfg["behavior"],gate,key,value,metrics.get(key)))
    return True

def current_state(master):
    frozen=[]
    first_pending=None
    gap=False
    for cfg in master["behaviors"]:
        ok=verify_gate(cfg,"freeze")
        if ok:
            if gap:
                raise RuntimeError("Non-contiguous BLIND freeze history at "+cfg["behavior"])
            frozen.append(cfg["behavior"])
        else:
            gap=True
            if first_pending is None:
                first_pending=cfg
    return frozen,first_pending

def compile_pipeline():
    files=[
        "tools/gogit_public.py",
        "tools/phase03_v55_blind_engine.py",
        "tools/public-audits/phase03_v55_blind_integrity.py",
        "tools/public-audits/phase03_v55_blind_freeze.py",
        "tests/phase-03/test_phase03_v55_blind_generic.py",
        "tests/phase-03/test_phase03_v55_blind_master.py",
        "tools/run_phase03_v55_blind.py",
    ]
    p=run([PY,"-m","py_compile",*files],capture=True)
    if p.returncode:
        raise RuntimeError("V55 BLIND py_compile failed:\n"+(p.stdout or ""))

def run_gate(cfg,gate):
    if verify_gate(cfg,gate):
        print("SKIP {} {}: already published and verified".format(cfg["behavior"],gate.upper()))
        return
    audit="tools/public-audits/phase03_v55_blind_{}.py".format(gate)
    step=cfg["freeze_step_id"] if gate=="freeze" else cfg["integrity_step_id"]
    env={
        "MINI_KUZAI_BLIND_BEHAVIOR":cfg["behavior"],
        "MINI_KUZAI_BLIND_GATE":gate,
    }
    print("RUN {} {}: tests".format(cfg["behavior"],gate.upper()))
    p=run([PY,"-m","unittest","discover","-s","tests/phase-03",
           "-p","test_phase03_v55_blind_generic.py","-v"],capture=True,env=env)
    if p.returncode:
        raise RuntimeError("{} {} tests failed:\n{}".format(cfg["behavior"],gate,p.stdout or ""))
    print("RUN {} {}: direct audit".format(cfg["behavior"],gate.upper()))
    p=run([PY,audit],capture=True,env=env)
    if p.returncode:
        raise RuntimeError("{} {} audit failed:\n{}".format(cfg["behavior"],gate,p.stdout or ""))
    print("RUN {} {}: GOGIT publish".format(cfg["behavior"],gate.upper()))
    p=run([PY,"tools/gogit_public.py","--step",step,"--audit",audit],capture=True,env=env)
    if p.returncode:
        raise RuntimeError("{} {} GOGIT failed:\n{}".format(cfg["behavior"],gate,p.stdout or ""))
    if not verify_gate(cfg,gate):
        raise RuntimeError("{} {} publication missing after success".format(cfg["behavior"],gate))
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local/remote divergence after {} {}".format(cfg["behavior"],gate))
    if git("status","--porcelain"):
        raise RuntimeError("Worktree not clean after {} {}".format(cfg["behavior"],gate))
    print("PASS {} {}: published and verified".format(cfg["behavior"],gate.upper()))

def main():
    try:
        sync()
        compile_pipeline()
        print("RUN V55 BLIND MASTER: state tests")
        p=run([PY,"-m","unittest","discover","-s","tests/phase-03",
               "-p","test_phase03_v55_blind_master.py","-v"],capture=True)
        if p.returncode:
            raise RuntimeError("V55 BLIND master tests failed:\n"+(p.stdout or ""))
        master=load_master()
        start,_=current_state(master)
        print("STATE: {} / 18 BLIND behaviors frozen".format(len(start)))

        while True:
            frozen,cfg=current_state(master)
            if len(frozen)==18:
                print(MARKER)
                print("BLIND_MASTER_COMPLETE: 1")
                print("BLIND_TEST_RECORDS_FROZEN: 36")
                print("BLIND_BEHAVIORS_FROZEN: 18")
                print("SEMANTIC_VALIDATION_COMPLETE: 1")
                print("TRAINING_AUTHORIZED: 0")
                print("GOGIT: READY")
                return

            print("NEXT: {} / {}".format(cfg["behavior"],cfg["group_id"]))
            run_gate(cfg,"integrity")
            run_gate(cfg,"freeze")

    except Exception as exc:
        print(MARKER)
        print("BLIND_MASTER_COMPLETE: 0")
        print("ERROR:",str(exc))
        sys.exit(1)

if __name__=="__main__":
    main()
