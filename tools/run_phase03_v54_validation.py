#!/usr/bin/env python3
"""Master resumable runner for Phase 03 V54 validation B01-B18.

The master runner is state-driven:
- verified freeze histories are skipped;
- an available per-behavior runner is executed for the first pending behavior;
- after each sub-runner, published state is re-verified;
- if the next behavior has no runner/artifacts yet, the master stops cleanly at
  that semantic boundary instead of treating it as a technical failure;
- no semantic corpus text is generated or rewritten here.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/"reports/assistant-results/history"
CONFIG=ROOT/"data/phase-03/manifests/validation-master-v54.json"
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
PY=sys.executable
SOURCE="Mini-Kuzai Phase 03 designed validation corpus"

def run(args,capture=False):
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        check=False,
    )

def git(*args):
    p=run(["git","-C",str(ROOT),*args],capture=True)
    if p.returncode:
        raise RuntimeError("git {} failed: {}".format(" ".join(args),(p.stdout or "").strip()))
    return (p.stdout or "").strip()

def require_clean_main_and_sync():
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

def load_config():
    if not CONFIG.is_file() or CONFIG.is_symlink():
        raise RuntimeError("Missing or unsafe master manifest")
    data=json.loads(CONFIG.read_text(encoding="utf-8"))
    if data.get("version")!="V54" or data.get("total_behaviors")!=18 or data.get("target_records")!=36:
        raise RuntimeError("Unexpected master validation manifest")
    behaviors=data.get("behaviors")
    if not isinstance(behaviors,list) or len(behaviors)!=18:
        raise RuntimeError("Master behavior inventory invalid")
    expected=["B{:02d}".format(i) for i in range(1,19)]
    actual=[x.get("behavior") for x in behaviors]
    if actual!=expected:
        raise RuntimeError("Master behavior order invalid")
    if data.get("training_authorized") is not False:
        raise RuntimeError("Master manifest unexpectedly authorizes training")
    return data

def freeze_step(behavior):
    return "PHASE03-SMOLTALK-V54-{}-VALIDATION-FREEZE-001".format(behavior)

def freeze_path(behavior):
    return HISTORY/(freeze_step(behavior)+".json")

def runner_path(behavior):
    return ROOT/"tools"/("run_phase03_v54_{}_validation.py".format(behavior.lower()))

def verify_freeze(behavior,index):
    path=freeze_path(behavior)
    if not path.is_file():
        return False
    if path.is_symlink():
        raise RuntimeError("Unsafe freeze history symlink for "+behavior)
    report=json.loads(path.read_text(encoding="utf-8"))
    if report.get("step_id")!=freeze_step(behavior):
        raise RuntimeError("Freeze STEP_ID mismatch for "+behavior)
    if report.get("source")!=SOURCE:
        raise RuntimeError("Unexpected source in freeze history for "+behavior)
    if report.get("training_authorized") is not False:
        raise RuntimeError("Training unexpectedly authorized in "+behavior)
    metrics=report.get("metrics",{})
    required={
        "{}_VALIDATION_FROZEN".format(behavior):1,
        "VALIDATION_FROZEN_RECORDS":index*2,
        "VALIDATION_BEHAVIORS_FROZEN":index,
        "TRAINING_AUTHORIZED":0,
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
    }
    for key,value in required.items():
        if metrics.get(key)!=value:
            raise RuntimeError("{} freeze metric mismatch: {} expected {} got {}".format(
                behavior,key,value,metrics.get(key)))
    return True

def current_state(behaviors):
    frozen=[]
    first_pending=None
    gap_seen=False
    for index,item in enumerate(behaviors,1):
        behavior=item["behavior"]
        ok=verify_freeze(behavior,index)
        if ok:
            if gap_seen:
                raise RuntimeError("Non-contiguous freeze history detected at "+behavior)
            frozen.append(behavior)
        else:
            gap_seen=True
            if first_pending is None:
                first_pending=item
    return frozen,first_pending

def print_boundary(frozen,next_item):
    print(MARKER)
    print("VALIDATION_MASTER_COMPLETE: 0")
    print("VALIDATION_FROZEN_RECORDS: {}".format(len(frozen)*2))
    print("VALIDATION_BEHAVIORS_FROZEN: {}".format(len(frozen)))
    print("TRAINING_AUTHORIZED: 0")
    if next_item:
        print("NEXT_REQUIRED_BEHAVIOR: {}".format(next_item["behavior"]))
        print("NEXT_REQUIRED_GROUP: {}".format(next_item["group_id"]))
        print("NEXT_REQUIRED_SCENARIO: {}".format(next_item["scenario_type"]))
        print("STOP_REASON: SEMANTIC_ARTIFACTS_REQUIRED")
    else:
        print("STOP_REASON: UNKNOWN_PENDING_STATE")

def execute_behavior(behavior,index):
    runner=runner_path(behavior)
    if not runner.is_file() or runner.is_symlink():
        return False
    print("RUN {} via {}".format(behavior,runner.relative_to(ROOT)))
    p=run([PY,str(runner.relative_to(ROOT))],capture=False)
    if p.returncode:
        raise RuntimeError("{} sub-runner exited with status {}".format(behavior,p.returncode))
    if not verify_freeze(behavior,index):
        raise RuntimeError("{} sub-runner returned success but freeze history is not valid".format(behavior))
    if git("status","--porcelain"):
        raise RuntimeError("Worktree not clean after "+behavior)
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local/remote divergence after "+behavior)
    print("PASS {}: freeze verified".format(behavior))
    return True

def main():
    try:
        require_clean_main_and_sync()
        config=load_config()
        behaviors=config["behaviors"]

        while True:
            frozen,next_item=current_state(behaviors)
            if len(frozen)==18:
                print(MARKER)
                print("VALIDATION_MASTER_COMPLETE: 1")
                print("VALIDATION_FROZEN_RECORDS: 36")
                print("VALIDATION_BEHAVIORS_FROZEN: 18")
                print("TRAINING_AUTHORIZED: 0")
                print("GOGIT: READY")
                return

            behavior=next_item["behavior"]
            index=int(behavior[1:])
            print("STATE: {} / 18 behaviors frozen; next {}".format(len(frozen),behavior))

            if not execute_behavior(behavior,index):
                print_boundary(frozen,next_item)
                return

    except Exception as exc:
        print(MARKER)
        print("VALIDATION_MASTER_COMPLETE: 0")
        print("ERROR:",str(exc))
        sys.exit(1)

if __name__=="__main__":
    main()
