#!/usr/bin/env python3
"""Run/resume the complete Phase 03 V54 B05 validation pipeline."""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/"reports/assistant-results/history"
MARKER="##### SECTION RESULTS FOR ASSISTANT ######"
PY=sys.executable
GOGIT=ROOT/"tools/gogit_public.py"

B05_KEYS={
    "VALIDATION_B05_CANDIDATES",
    "B05_ANSWER_PLUS_QUESTION_RECORDS",
    "B05_INDEPENDENT_SIGNOFF",
    "B05_VALIDATION_FROZEN",
}

GATES=[
    {
        "name":"B05_INTEGRITY",
        "step":"PHASE03-SMOLTALK-V54-B05-VALIDATION-INTEGRITY-001",
        "audit":"tools/public-audits/phase03_v54_b05_validation_integrity.py",
        "test":"test_phase03_v54_b05_validation_integrity.py",
        "env":{"MINI_KUZAI_REQUIRE_B05_GOGIT_KEYS":"1"},
        "expected":{
            "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
            "VALIDATION_B05_CANDIDATES":2,
            "CROSS_SPLIT_ID_COLLISIONS":0,"CROSS_SPLIT_GROUP_COLLISIONS":0,
            "EXACT_USER_PROMPT_MATCHES":0,
            "B05_ANSWER_PLUS_QUESTION_RECORDS":2,
            "B05_INDEPENDENT_SIGNOFF":1,"B05_VALIDATION_FROZEN":0,
            "VALIDATION_FROZEN_RECORDS":10,"VALIDATION_BEHAVIORS_FROZEN":5,
            "TRAINING_AUTHORIZED":0,
        },
    },
    {
        "name":"B05_FREEZE",
        "step":"PHASE03-SMOLTALK-V54-B05-VALIDATION-FREEZE-001",
        "audit":"tools/public-audits/phase03_v54_b05_validation_freeze.py",
        "test":"test_phase03_v54_b05_validation_freeze.py",
        "env":{"MINI_KUZAI_REQUIRE_B05_FREEZE_TEST":"1"},
        "expected":{
            "TRAIN_FILES":19,"TRAIN_RECORDS":107,"TRAIN_GROUPS":29,
            "VALIDATION_B05_CANDIDATES":2,
            "CROSS_SPLIT_ID_COLLISIONS":0,"CROSS_SPLIT_GROUP_COLLISIONS":0,
            "EXACT_USER_PROMPT_MATCHES":0,
            "B05_ANSWER_PLUS_QUESTION_RECORDS":2,
            "B05_INDEPENDENT_SIGNOFF":1,"B05_VALIDATION_FROZEN":1,
            "VALIDATION_FROZEN_RECORDS":8,"VALIDATION_BEHAVIORS_FROZEN":4,
            "TRAINING_AUTHORIZED":0,
        },
    },
]

def run(args,env=None,capture=False):
    merged=os.environ.copy()
    if env: merged.update(env)
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
    if git("branch","--show-current")!="main": raise RuntimeError("Expected branch main")
    if git("status","--porcelain"): raise RuntimeError("Worktree/index must be clean")
    p=run(["git","-C",str(ROOT),"pull","--ff-only","origin","main"],capture=True)
    if p.returncode: raise RuntimeError("git pull --ff-only failed: "+(p.stdout or "").strip())
    if git("status","--porcelain"): raise RuntimeError("Worktree changed after pull")
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Local main and origin/main differ after synchronization")

def ensure_gogit_allowlist():
    raw=GOGIT.read_text(encoding="utf-8")
    if all('"{}"'.format(k) in raw for k in B05_KEYS):
        print("SKIP B05_GOGIT_ALLOWLIST: already installed")
        return
    anchor='    "B04_INDEPENDENT_SIGNOFF", "B04_VALIDATION_FROZEN",\n    "VALIDATION_FROZEN_RECORDS",\n'
    if anchor not in raw:
        raise RuntimeError("GOGIT B04 allowlist anchor not found")
    replacement=(
        '    "B04_INDEPENDENT_SIGNOFF", "B04_VALIDATION_FROZEN",\n'
        '    "VALIDATION_B05_CANDIDATES", "B05_ANSWER_PLUS_QUESTION_RECORDS",\n'
        '    "B05_INDEPENDENT_SIGNOFF", "B05_VALIDATION_FROZEN",\n'
        '    "VALIDATION_FROZEN_RECORDS",\n'
    )
    backup_root=Path("/root/Mini-Kuzai/backups/gogit-v54-b05")
    backup_root.mkdir(parents=True,exist_ok=True,mode=0o700)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup=backup_root/("gogit_public.py."+stamp+".bak")
    shutil.copy2(GOGIT,backup)
    GOGIT.write_text(raw.replace(anchor,replacement,1),encoding="utf-8")
    p=run([PY,"-m","py_compile","tools/gogit_public.py"],capture=True)
    if p.returncode:
        shutil.copy2(backup,GOGIT)
        raise RuntimeError("GOGIT patch compile failed: "+(p.stdout or ""))
    git("add","--","tools/gogit_public.py")
    staged=set(git("diff","--cached","--name-only").splitlines())
    if staged!={"tools/gogit_public.py"}:
        git("reset","--quiet","--","tools/gogit_public.py")
        shutil.copy2(backup,GOGIT)
        raise RuntimeError("Unexpected staged files during GOGIT allowlist patch")
    git("diff","--cached","--check")
    git("commit","-m","V54: allowlist B05 validation pipeline metrics for GOGIT")
    p=run(["git","-C",str(ROOT),"push","origin","main"],capture=True)
    if p.returncode: raise RuntimeError("GOGIT allowlist commit created but push failed: "+(p.stdout or "").strip())
    git("fetch","--quiet","origin","main")
    if git("rev-parse","HEAD")!=git("rev-parse","origin/main"):
        raise RuntimeError("Remote verification failed after GOGIT allowlist push")
    if git("status","--porcelain"): raise RuntimeError("Worktree not clean after GOGIT allowlist push")
    print("PASS B05_GOGIT_ALLOWLIST: installed, committed and verified")

def compile_pipeline():
    files=[
        "tools/public-audits/phase03_v54_b05_validation_integrity.py",
        "tools/public-audits/phase03_v54_b05_validation_freeze.py",
        "tests/phase-03/test_phase03_v54_b05_validation_integrity.py",
        "tests/phase-03/test_phase03_v54_b05_validation_freeze.py",
        "tools/gogit_public.py",
        "tools/run_phase03_v54_b05_validation.py",
    ]
    p=run([PY,"-m","py_compile",*files],capture=True)
    if p.returncode: raise RuntimeError("py_compile failed:\n"+(p.stdout or ""))

def history_report(step):
    path=HISTORY/(step+".json")
    if not path.is_file(): return None
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise RuntimeError("Invalid history JSON for "+step)
    return value

def verify_published(gate):
    report=history_report(gate["step"])
    if report is None: return False
    if report.get("step_id")!=gate["step"]: raise RuntimeError("Published STEP_ID mismatch for "+gate["name"])
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

def run_gate(gate):
    if verify_published(gate):
        print("SKIP {}: already published and verified".format(gate["name"]))
        return
    print("RUN {}: tests".format(gate["name"]))
    p=run([PY,"-m","unittest","discover","-s","tests/phase-03","-p",gate["test"],"-v"],env=gate["env"],capture=True)
    if p.returncode: raise RuntimeError("{} tests failed:\n{}".format(gate["name"],p.stdout or ""))
    print("RUN {}: direct audit".format(gate["name"]))
    p=run([PY,gate["audit"]],env=gate["env"],capture=True)
    if p.returncode: raise RuntimeError("{} audit failed:\n{}".format(gate["name"],p.stdout or ""))
    print("RUN {}: GOGIT publish".format(gate["name"]))
    p=run([PY,"tools/gogit_public.py","--step",gate["step"],"--audit",gate["audit"]],env=gate["env"],capture=True)
    if p.returncode: raise RuntimeError("{} GOGIT failed:\n{}".format(gate["name"],p.stdout or ""))
    if not verify_published(gate): raise RuntimeError("{} publication missing after success".format(gate["name"]))
    print("PASS {}: published and verified".format(gate["name"]))

def main():
    try:
        require_clean_main_and_sync()
        ensure_gogit_allowlist()
        compile_pipeline()
        while True:
            pending=[g for g in GATES if not verify_published(g)]
            if not pending: break
            before=len(pending)
            for gate in GATES: run_gate(gate)
            after=len([g for g in GATES if not verify_published(g)])
            if after>=before: raise RuntimeError("Pipeline made no progress")
        final=history_report(GATES[-1]["step"])["metrics"]
        print(MARKER)
        print("B05_PIPELINE_COMPLETE: 1")
        print("B05_INDEPENDENT_SIGNOFF: {}".format(final["B05_INDEPENDENT_SIGNOFF"]))
        print("B05_VALIDATION_FROZEN: {}".format(final["B05_VALIDATION_FROZEN"]))
        print("B05_ANSWER_PLUS_QUESTION_RECORDS: {}".format(final["B05_ANSWER_PLUS_QUESTION_RECORDS"]))
        print("VALIDATION_FROZEN_RECORDS: {}".format(final["VALIDATION_FROZEN_RECORDS"]))
        print("VALIDATION_BEHAVIORS_FROZEN: {}".format(final["VALIDATION_BEHAVIORS_FROZEN"]))
        print("TRAINING_AUTHORIZED: {}".format(final["TRAINING_AUTHORIZED"]))
        print("GOGIT: READY")
    except Exception as exc:
        print(MARKER)
        print("B05_PIPELINE_COMPLETE: 0")
        print("ERROR:",str(exc))
        sys.exit(1)

if __name__=="__main__":
    main()
