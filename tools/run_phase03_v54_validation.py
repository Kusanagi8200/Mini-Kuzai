#!/usr/bin/env python3
"""Master resumable runner for Phase 03 V54 validation B01-B18.

Verified frozen behaviors are skipped. B06+ use one generic gate engine driven
by committed per-behavior configuration. The runner stops only when the next
behavior has no reviewed semantic artifacts/configuration or when a real gate
fails. It never authors or rewrites semantic corpus text.
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/"reports/assistant-results/history"
CONFIG=ROOT/"data/phase-03/manifests/validation-master-v54.json"
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
PY=sys.executable
SOURCE="Mini-Kuzai Phase 03 designed validation corpus"
GOGIT=ROOT/"tools/gogit_public.py"

GENERIC_KEYS={
    "VALIDATION_BATCH_INDEX",
    "VALIDATION_BATCH_CANDIDATES",
    "VALIDATION_BATCH_SIGNOFF",
    "VALIDATION_BATCH_SEMANTIC_PASS",
    "VALIDATION_BATCH_FROZEN",
}

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

def ensure_generic_gogit_allowlist():
    raw=GOGIT.read_text(encoding="utf-8")
    if all('"{}"'.format(key) in raw for key in GENERIC_KEYS):
        print("SKIP GENERIC_GOGIT_ALLOWLIST: already installed")
        return
    anchor='    "B05_INDEPENDENT_SIGNOFF", "B05_VALIDATION_FROZEN",\n    "VALIDATION_FROZEN_RECORDS",\n'
    if anchor not in raw:
        raise RuntimeError("GOGIT B05 allowlist anchor not found")
    replacement=(
        '    "B05_INDEPENDENT_SIGNOFF", "B05_VALIDATION_FROZEN",\n'
        '    "VALIDATION_BATCH_INDEX", "VALIDATION_BATCH_CANDIDATES",\n'
        '    "VALIDATION_BATCH_SIGNOFF", "VALIDATION_BATCH_SEMANTIC_PASS",\n'
        '    "VALIDATION_BATCH_FROZEN",\n'
        '    "VALIDATION_FROZEN_RECORDS",\n'
    )
    backup_root=Path("/root/Mini-Kuzai/backups/gogit-v54-generic")
    backup_root.mkdir(parents=True,exist_ok=True,mode=0o700)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup=backup_root/("gogit_public.py."+stamp+".bak")
    shutil.copy2(GOGIT,backup)
    GOGIT.write_text(raw.replace(anchor,replacement,1),encoding="utf-8")
    p=run([PY,"-m","py_compile","tools/gogit_public.py"],capture=True)
    if p.returncode:
        shutil.copy2(backup,GOGIT)
        raise RuntimeError("Generic GOGIT patch compile failed: "+(p.stdout or ""))
    git("add","--","tools/gogit_public.py")
    staged=set(git("diff","--cached","--name-only").splitlines())
    if staged!={"tools/gogit_public.py"}:
        git("reset","--quiet","--","tools/gogit_public.py")
        shutil.copy2(backup,GOGIT)
        raise RuntimeError("Unexpected staged files during generic GOGIT patch")
    git("diff","--cached","--check")
    git("commit","-m","V54: allowlist generic validation pipeline metrics for GOGIT")
    p=run(["git","-C",str(ROOT),"push","origin","main"],capture=True)
    if p.returncode:
        raise RuntimeError("Generic GOGIT allowlist commit created but push failed: "+(p.stdout or "").strip())
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Remote verification failed after generic GOGIT allowlist push")
    if git("status","--porcelain"):
        raise RuntimeError("Worktree not clean after generic GOGIT allowlist push")
    print("PASS GENERIC_GOGIT_ALLOWLIST: installed, committed and verified")

def compile_generic_pipeline():
    files=[
        "tools/phase03_v54_validation_engine.py",
        "tools/public-audits/phase03_v54_validation_integrity.py",
        "tools/public-audits/phase03_v54_validation_freeze.py",
        "tests/phase-03/test_phase03_v54_validation_generic.py",
        "tools/gogit_public.py",
        "tools/run_phase03_v54_validation.py",
    ]
    p=run([PY,"-m","py_compile",*files],capture=True)
    if p.returncode:
        raise RuntimeError("Generic validation py_compile failed:\n"+(p.stdout or ""))

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
    if [x.get("behavior") for x in behaviors]!=expected:
        raise RuntimeError("Master behavior order invalid")
    if data.get("training_authorized") is not False:
        raise RuntimeError("Master manifest unexpectedly authorizes training")
    return data

def generic_config_path(behavior):
    return ROOT/"data/phase-03/manifests"/("validation-{}-v54-config.json".format(behavior.lower()))

def load_generic_config(behavior):
    path=generic_config_path(behavior)
    if not path.is_file() or path.is_symlink():
        return None
    cfg=json.loads(path.read_text(encoding="utf-8"))
    if cfg.get("behavior")!=behavior or cfg.get("version")!="V54" or cfg.get("index")!=int(behavior[1:]):
        raise RuntimeError("Generic behavior config mismatch for "+behavior)
    return cfg

def freeze_step(behavior):
    return "PHASE03-SMOLTALK-V54-{}-VALIDATION-FREEZE-001".format(behavior)

def history_report(step):
    path=HISTORY/(step+".json")
    if not path.is_file():
        return None
    if path.is_symlink():
        raise RuntimeError("Unsafe history symlink for "+step)
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise RuntimeError("Invalid history JSON for "+step)
    return value

def verify_freeze(behavior,index):
    report=history_report(freeze_step(behavior))
    if report is None:
        return False
    if report.get("step_id")!=freeze_step(behavior):
        raise RuntimeError("Freeze STEP_ID mismatch for "+behavior)
    if report.get("source")!=SOURCE:
        raise RuntimeError("Unexpected source in freeze history for "+behavior)
    if report.get("training_authorized") is not False:
        raise RuntimeError("Training unexpectedly authorized in "+behavior)
    metrics=report.get("metrics",{})
    required={"TRAINING_AUTHORIZED":0,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29}
    if index<=5:
        required["{}_VALIDATION_FROZEN".format(behavior)]=1
        if index>=2:
            required["VALIDATION_FROZEN_RECORDS"]=index*2
            required["VALIDATION_BEHAVIORS_FROZEN"]=index
    else:
        required["VALIDATION_BATCH_INDEX"]=index
        required["VALIDATION_BATCH_FROZEN"]=1
        required["VALIDATION_BATCH_SIGNOFF"]=1
        required["VALIDATION_BATCH_SEMANTIC_PASS"]=1
        required["VALIDATION_FROZEN_RECORDS"]=index*2
        required["VALIDATION_BEHAVIORS_FROZEN"]=index
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

def generic_expected(cfg,frozen):
    return {
        "TRAIN_FILES":19,
        "TRAIN_RECORDS":107,
        "TRAIN_GROUPS":29,
        "VALIDATION_BATCH_INDEX":cfg["index"],
        "VALIDATION_BATCH_CANDIDATES":2,
        "VALIDATION_BATCH_SIGNOFF":1,
        "VALIDATION_BATCH_SEMANTIC_PASS":1,
        "VALIDATION_BATCH_FROZEN":1 if frozen else 0,
        "CROSS_SPLIT_ID_COLLISIONS":0,
        "CROSS_SPLIT_GROUP_COLLISIONS":0,
        "EXACT_USER_PROMPT_MATCHES":0,
        "VALIDATION_FROZEN_RECORDS":cfg["cumulative_after_records"] if frozen else cfg["cumulative_before_records"],
        "VALIDATION_BEHAVIORS_FROZEN":cfg["cumulative_after_behaviors"] if frozen else cfg["cumulative_before_behaviors"],
        "TRAINING_AUTHORIZED":0,
    }

def verify_generic_gate(cfg,gate):
    frozen=(gate=="freeze")
    step=cfg["freeze_step_id"] if frozen else cfg["integrity_step_id"]
    report=history_report(step)
    if report is None:
        return False
    if report.get("step_id")!=step or report.get("source")!=SOURCE or report.get("training_authorized") is not False:
        raise RuntimeError("Generic {} history metadata mismatch for {}".format(gate,cfg["behavior"]))
    metrics=report.get("metrics",{})
    for key,value in generic_expected(cfg,frozen).items():
        if metrics.get(key)!=value:
            raise RuntimeError("{} {} metric mismatch: {} expected {} got {}".format(
                cfg["behavior"],gate,key,value,metrics.get(key)))
    return True

def run_generic_gate(cfg,gate):
    if verify_generic_gate(cfg,gate):
        print("SKIP {} {}: already published and verified".format(cfg["behavior"],gate.upper()))
        return
    audit="tools/public-audits/phase03_v54_validation_{}.py".format(gate)
    step=cfg["freeze_step_id"] if gate=="freeze" else cfg["integrity_step_id"]
    env={
        "MINI_KUZAI_VALIDATION_BEHAVIOR":cfg["behavior"],
        "MINI_KUZAI_VALIDATION_GATE":gate,
        "MINI_KUZAI_REQUIRE_GENERIC_GOGIT_KEYS":"1",
    }
    print("RUN {} {}: tests".format(cfg["behavior"],gate.upper()))
    p=run([PY,"-m","unittest","discover","-s","tests/phase-03","-p","test_phase03_v54_validation_generic.py","-v"],capture=True,env=env)
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
    if not verify_generic_gate(cfg,gate):
        raise RuntimeError("{} {} publication missing after success".format(cfg["behavior"],gate))
    print("PASS {} {}: published and verified".format(cfg["behavior"],gate.upper()))

def execute_generic_behavior(cfg):
    run_generic_gate(cfg,"integrity")
    run_generic_gate(cfg,"freeze")
    behavior=cfg["behavior"]
    if not verify_freeze(behavior,cfg["index"]):
        raise RuntimeError("{} generic pipeline returned without valid freeze".format(behavior))
    if git("status","--porcelain"):
        raise RuntimeError("Worktree not clean after "+behavior)
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local/remote divergence after "+behavior)
    print("PASS {}: freeze verified".format(behavior))

def execute_legacy_behavior(behavior,index):
    runner=ROOT/"tools"/("run_phase03_v54_{}_validation.py".format(behavior.lower()))
    if not runner.is_file() or runner.is_symlink():
        return False
    print("RUN {} via legacy {}".format(behavior,runner.relative_to(ROOT)))
    p=run([PY,str(runner.relative_to(ROOT))])
    if p.returncode:
        raise RuntimeError("{} legacy sub-runner exited with status {}".format(behavior,p.returncode))
    if not verify_freeze(behavior,index):
        raise RuntimeError("{} legacy sub-runner returned without valid freeze".format(behavior))
    return True

def print_boundary(frozen,next_item,start_count):
    print(MARKER)
    print("VALIDATION_MASTER_COMPLETE: 0")
    print("VALIDATION_FROZEN_RECORDS: {}".format(len(frozen)*2))
    print("VALIDATION_BEHAVIORS_FROZEN: {}".format(len(frozen)))
    print("TRAINING_AUTHORIZED: 0")
    if frozen:
        print("LAST_FROZEN_BEHAVIOR: {}".format(frozen[-1]))
    if len(frozen)>start_count:
        print("GOGIT: READY")
    if next_item:
        print("NEXT_REQUIRED_BEHAVIOR: {}".format(next_item["behavior"]))
        print("NEXT_REQUIRED_GROUP: {}".format(next_item["group_id"]))
        print("NEXT_REQUIRED_SCENARIO: {}".format(next_item["scenario_type"]))
        print("STOP_REASON: SEMANTIC_ARTIFACTS_REQUIRED")
    else:
        print("STOP_REASON: UNKNOWN_PENDING_STATE")

def main():
    try:
        require_clean_main_and_sync()
        ensure_generic_gogit_allowlist()
        compile_generic_pipeline()
        config=load_config()
        behaviors=config["behaviors"]
        start_frozen,_=current_state(behaviors)
        start_count=len(start_frozen)

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
            cfg=load_generic_config(behavior)

            if cfg is not None:
                execute_generic_behavior(cfg)
                continue

            if index<=5 and execute_legacy_behavior(behavior,index):
                continue

            print_boundary(frozen,next_item,start_count)
            return

    except Exception as exc:
        print(MARKER)
        print("VALIDATION_MASTER_COMPLETE: 0")
        print("ERROR:",str(exc))
        sys.exit(1)

if __name__=="__main__":
    main()
