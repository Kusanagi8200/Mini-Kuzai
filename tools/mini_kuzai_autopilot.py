#!/usr/bin/env python3
"""Mini-Kuzai AUTOPILOT V1 - local, restartable, fail-closed campaign runner.

Only a fixed, reviewed catalog of diagnostic runners can execute. GitHub is
used for synchronized instructions and immutable, numeric-only GOGIT reports.
A future training-window runner requires a NEW protocol, separately approved
local authorization, exact source blob and bounded internal step/token budget.
The present training-runner catalog is intentionally EMPTY.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
PYTHON=Path("/root/Mini-Kuzai/.venv/bin/python")
LOCAL_ROOT=Path("/root/Mini-Kuzai/runs/autopilot-v1")
AUTH_DIR=Path("/root/Mini-Kuzai/autopilot-authorizations")
CAMPAIGN_DIR=REPO/"autopilot"/"campaigns"
CAMPAIGN_SCHEMA="mini-kuzai-autopilot-campaign-v1"
TRAIN_AUTH_SCHEMA="mini-kuzai-autopilot-train-authorization-v1"
FROZEN_V62=Path("/root/Mini-Kuzai/runs/v62-margin-001")
REPO_ORIGINS={
    "https://github.com/Kusanagi8200/Mini-Kuzai.git",
    "https://github.com/Kusanagi8200/Mini-Kuzai",
    "git@github.com:Kusanagi8200/Mini-Kuzai.git",
}
STEP_RE=re.compile(r"PHASE03-SMOLTALK-[A-Z0-9-]{5,100}\Z")
ID_RE=re.compile(r"[a-z][a-z0-9-]{2,62}\Z")
SHA_RE=re.compile(r"[0-9a-f]{40}\Z")
SHA256_RE=re.compile(r"[0-9a-f]{64}\Z")

# V68 is added only after the dedicated audit runner and its frozen Git blob
# are published and reviewed. No manifest-controlled arbitrary commands.
DIAGNOSTIC_RUNNERS={
    "v67-readonly":"tools/run_v67_output_concentration_001_job.py",
    "v68-head":"tools/run_v68_output_head_001_job.py",
    "v69-norm":"tools/run_v69_output_norm_counterfactual_001_job.py",
}
# A subsequent, separate workstream must implement, review and register an
# internal-budget-enforcing NEW trainer before any bounded training can run.
TRAIN_RUNNERS={}

REPORT_PRODUCERS={
    "PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001":
        "tools/public-audits/phase03_v65_token_frequency_diagnostic_001.py",
    "PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-A-001":
        "tools/public-audits/phase03_v66_token_prediction_bias_part_a_001.py",
    "PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-B-001":
        "tools/public-audits/phase03_v66_token_prediction_bias_part_b_001.py",
    "PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001":
        "tools/public-audits/phase03_v67_output_concentration_001.py",
    "PHASE03-SMOLTALK-V68-OUTPUT-HEAD-001":
        "tools/public-audits/phase03_v68_output_head_001.py",
    "PHASE03-SMOLTALK-V68-FAILURE-PROBE-001":
        "tools/public-audits/phase03_v68_failure_probe_001.py",
    "PHASE03-SMOLTALK-V69-OUTPUT-NORM-COUNTERFACTUAL-001":
        "tools/public-audits/phase03_v69_output_norm_counterfactual_001.py",
}
APPROVED_RUN_BLOB={
    "v67-readonly":"a5efc5cc58ec162d3b11cb9e0e11ddf30281ad57",
    "v68-head":"fae721c57c7184ab9a154d91b46a57942d85dcaf",
    "v69-norm":"14eb37c5835a9c93c4a11da301bac25db94bbe0e",
}
FAILURE_PROBE_STEP="PHASE03-SMOLTALK-V68-FAILURE-PROBE-001"
FAILURE_PROBE_SOURCE="tools/public-audits/phase03_v68_failure_probe_001.py"
FAILURE_PROBE_BLOB="f67bacc63079cbf3bf0d5b78ebe30eefd36b7111"


# Standard diagnostic GOGIT flags must be zero, independent of stage rules.
REQUIRED_ZERO=("SEMANTIC_VALIDATION_COMPLETE","TRAINING_AUTHORIZED","TRAINING_STARTED")
OPS={
    "eq":lambda x,y:x==y,
    "ne":lambda x,y:x!=y,
    "lt":lambda x,y:x<y,
    "le":lambda x,y:x<=y,
    "gt":lambda x,y:x>y,
    "ge":lambda x,y:x>=y,
}


class Halt(RuntimeError):
    """Failure or manual authorization boundary - never continue automatically."""


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def strict_json(path:Path):
    if not path.is_file() or path.is_symlink():
        raise Halt("Missing or unsafe JSON file: "+str(path))
    result=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result,dict):
        raise Halt("Expected JSON object: "+str(path))
    return result


def git(*args, timeout=90):
    result=subprocess.run(
        ["git","-C",str(REPO),*args],
        text=True,capture_output=True,timeout=timeout,check=False,
    )
    if result.returncode:
        raise Halt("Git command failed: "+(" ".join(args)))
    return result.stdout.strip()


def git_sync():
    """Fast-forward only; accept GOGIT pushes without discarding local edits."""
    if git("branch","--show-current")!="main":
        raise Halt("AUTOPILOT requires main branch")
    if git("remote","get-url","origin") not in REPO_ORIGINS:
        raise Halt("Unexpected Git origin")
    if git("status","--porcelain"):
        raise Halt("Dirty worktree: auto-sync refused")
    git("fetch","--quiet","origin","main")
    head=git("rev-parse","HEAD")
    remote=git("rev-parse","origin/main")
    if head!=remote:
        if git("merge-base","HEAD","origin/main")!=head:
            raise Halt("Non-fast-forward update: manual resolution required")
        git("merge","--ff-only","origin/main")
    if git("status","--porcelain"):
        raise Halt("Worktree changed unexpectedly after fetch")
    return git("rev-parse","HEAD")


def safe_relative(path:str,base:Path):
    if not isinstance(path,str) or not path or path.startswith("/"):
        raise Halt("Invalid relative path")
    parts=Path(path).parts
    if any(p in ("..",".") for p in parts):
        raise Halt("Directory traversal denied")
    candidate=base/path
    current=base.resolve()
    for part in parts:
        current=current/part
        if current.is_symlink():
            raise Halt("Symlink denied in approved path")
    resolved=candidate.resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise Halt("Path escapes its permitted directory")
    return resolved


def validate_rule(rule):
    if not isinstance(rule,dict) or set(rule)!={"step","metric","op","value"}:
        raise Halt("Unknown rule fields")
    if not isinstance(rule["step"],str) or not STEP_RE.fullmatch(rule["step"]):
        raise Halt("Invalid rule reference step")
    if not isinstance(rule["metric"],str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{1,100}",rule["metric"]):
        raise Halt("Invalid metric name")
    if rule["op"] not in OPS or type(rule["value"]) is not int:
        raise Halt("Invalid metric comparison")


def validate_campaign(plan):
    if set(plan)!={"schema","campaign_id","mode","max_wall_seconds","steps"}:
        raise Halt("Unknown or missing campaign fields")
    if plan["schema"]!=CAMPAIGN_SCHEMA or plan["mode"]!="bounded":
        raise Halt("Unsupported AUTOPILOT campaign schema or mode")
    if not isinstance(plan["campaign_id"],str) or not ID_RE.fullmatch(plan["campaign_id"]):
        raise Halt("Unsafe campaign ID")
    if type(plan["max_wall_seconds"]) is not int or not 60<=plan["max_wall_seconds"]<=86400:
        raise Halt("Invalid campaign wall-time limit")
    steps=plan["steps"]
    if not isinstance(steps,list) or not 1<=len(steps)<=24:
        raise Halt("Expected 1-24 bounded stages")
    names=set()
    for stage in steps:
        keys={"id","kind","step","required","rules","when","runner"}
        if not isinstance(stage,dict) or set(stage)!=keys:
            raise Halt("Invalid stage shape")
        if not isinstance(stage["id"],str) or not ID_RE.fullmatch(stage["id"]) or stage["id"] in names:
            raise Halt("Duplicate or unsafe stage ID")
        names.add(stage["id"])
        if stage["kind"] not in ("verify","diagnostic","train_window"):
            raise Halt("Unknown stage kind")
        if not isinstance(stage["step"],str) or not STEP_RE.fullmatch(stage["step"]):
            raise Halt("Invalid report step ID")
        if type(stage["required"]) is not bool:
            raise Halt("required must be boolean")
        for key in ("rules","when"):
            if not isinstance(stage[key],list) or len(stage[key])>16:
                raise Halt("Rule list exceeds limit")
            for rule in stage[key]:
                validate_rule(rule)
        if stage["kind"]=="verify":
            if stage["runner"] is not None or stage["step"] not in REPORT_PRODUCERS:
                raise Halt("Verify stage must use frozen known GOGIT producer")
        elif stage["kind"]=="diagnostic":
            if stage["runner"] not in DIAGNOSTIC_RUNNERS:
                raise Halt("Unregistered diagnostic runner")
            if stage["step"] not in REPORT_PRODUCERS:
                raise Halt("Unregistered diagnostic report producer")
        else:
            # This branch cannot run in V1 until an independently frozen
            # TRAIN_RUNNERS catalog is populated and operator-armed.
            if stage["runner"] not in TRAIN_RUNNERS:
                raise Halt("No new trainer registered: training prohibited")
    return plan


def load_campaign(filename):
    if not isinstance(filename,str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,60}\.json",filename):
        raise Halt("Campaign selection must be a simple approved JSON filename")
    file=safe_relative(filename,CAMPAIGN_DIR)
    content=file.read_bytes()
    plan=validate_campaign(json.loads(content.decode("utf-8")))
    return plan,hashlib.sha256(content).hexdigest(),file


def verify_frozen_v62():
    summary=strict_json(FROZEN_V62/"RUN-SUMMARY.json")
    manifest=strict_json(FROZEN_V62/"RUN-MANIFEST.json")
    checkpoint=FROZEN_V62/"checkpoint-cycle-02.pt"
    if not (
        summary.get("schema_version")=="v62-margin-run-summary-1"
        and manifest.get("schema_version")=="v62-margin-run-1"
        and summary.get("status")==manifest.get("status")=="STOPPED"
        and summary.get("stop_reason")=="MILESTONE_REVIEW_REQUIRED"
        and summary.get("optimizer_steps")==69
        and summary.get("exposure_tokens")==597982
        and summary.get("blind_test_accessed") is False
        and manifest.get("blind_test_during_training") is False
        and manifest.get("resume") is False
        and not (FROZEN_V62/".training.lock").exists()
        and checkpoint.is_file() and not checkpoint.is_symlink()
    ):
        raise Halt("Frozen V62 stop/checkpoint gate failed")


def report_path(step):
    if step not in REPORT_PRODUCERS:
        raise Halt("Report producer not approved")
    return REPO/"reports"/"assistant-results"/"history"/f"{step}.json"


def read_report(step):
    doc=strict_json(report_path(step))
    metrics=doc.get("metrics")
    producer=REPORT_PRODUCERS[step]
    if not (
        doc.get("step_id")==step
        and doc.get("producer")==producer
        and doc.get("status")=="PUBLIC_AGGREGATE_REVIEW_ONLY"
        and doc.get("semantic_validation_complete") is False
        and doc.get("training_authorized") is False
        and doc.get("private_conversation_data_included") is False
        and isinstance(metrics,dict)
        and len(metrics)<=30 and len(metrics)>=4
        and all(type(x) is int and 0<=x<=100_000_000 for x in metrics.values())
        and all(metrics.get(key)==0 for key in REQUIRED_ZERO)
    ):
        raise Halt("GOGIT report failed safety/metadata gate: "+step)
    blind_keys=[key for key in metrics if key.endswith("_BLIND_ACCESS")]
    if blind_keys:
        if any(metrics[key]!=0 for key in blind_keys):
            raise Halt("BLIND accessed during diagnostic")
    elif step=="PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-B-001":
        # B has no BLIND metric by design; it requires paired A's validated
        # frozen checkpoint, code hash and explicit no-BLIND evidence.
        paired=read_report("PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-A-001")
        if paired.get("V66_BIAS_BLIND_ACCESS")!=0:
            raise Halt("V66-A prerequisite BLIND gate failed")
    else:
        raise Halt("Missing explicit no-BLIND GOGIT metric")
    source=safe_relative(producer,REPO)
    recorded_hash=doc.get("producer_sha256")
    if not isinstance(recorded_hash,str) or not SHA256_RE.fullmatch(recorded_hash):
        raise Halt("GOGIT producer SHA256 missing")
    if hashlib.sha256(source.read_bytes()).hexdigest()!=recorded_hash:
        raise Halt("GOGIT producer changed after immutable report")
    return metrics


def evaluate_rules(rules):
    for rule in rules:
        validate_rule(rule)
        metrics=read_report(rule["step"])
        actual=metrics.get(rule["metric"])
        if type(actual) is not int or not OPS[rule["op"]](actual,rule["value"]):
            return False
    return True


def publish_v68_failure_probe():
    """Preserve the failed V68 status and publish only reviewed numeric errors.

    Never publishes a traceback, exception text, local path or user data.
    Does not change the original experiment or checkpoint.
    """
    existing=report_path(FAILURE_PROBE_STEP)
    if existing.exists():
        metrics=read_report(FAILURE_PROBE_STEP)
    else:
        git_sync()
        git("ls-files","--error-unmatch","--",FAILURE_PROBE_SOURCE)
        if git("rev-parse",f"HEAD:{FAILURE_PROBE_SOURCE}")!=FAILURE_PROBE_BLOB:
            raise Halt("V68 failure probe no longer matches reviewed source")
        checked=safe_relative(FAILURE_PROBE_SOURCE,REPO)
        if not checked.is_file() or checked.is_symlink():
            raise Halt("V68 failure probe file unavailable or unsafe")
        proc=subprocess.run(
            [str(PYTHON),"tools/gogit_public.py",
             "--step",FAILURE_PROBE_STEP,"--audit",FAILURE_PROBE_SOURCE],
            cwd=REPO,timeout=330,check=False,
        )
        if proc.returncode!=0:
            raise Halt("V68 numeric failure probe could not be published")
        git_sync()
        metrics=read_report(FAILURE_PROBE_STEP)
    if not (
        metrics.get("V68_FAIL_DIAG_PASS")==1
        and metrics.get("V68_FAIL_BLIND_ACCESS")==0
        and metrics.get("V68_FAIL_ORIGINAL_FAILED") in (0,1)
        and type(metrics.get("V68_FAIL_EXCEPTION_CLASS_ID")) is int
    ):
        raise Halt("V68 numeric failure diagnostic invalid")
    print("AUTOPILOT_V68_FAILURE_PROBE: PUBLISHED",flush=True)


def checked_runner(runner_key, step, max_seconds):
    """Only fixed local reviewed commands. Never shell=True or manifest argv."""
    if runner_key not in DIAGNOSTIC_RUNNERS:
        raise Halt("Unknown diagnostic runner")
    script=safe_relative(DIAGNOSTIC_RUNNERS[runner_key],REPO)
    if not script.is_file() or script.suffix!=".py" or script.is_symlink():
        raise Halt("Diagnostic runner is absent or unsafe")
    tracked=DIAGNOSTIC_RUNNERS[runner_key]
    git("ls-files","--error-unmatch","--",tracked)
    expected=APPROVED_RUN_BLOB.get(runner_key)
    if expected is None or not SHA_RE.fullmatch(expected):
        raise Halt("Diagnostic runner not pinned to a reviewed Git blob")
    if git("rev-parse",f"HEAD:{tracked}")!=expected:
        raise Halt("Registered runner Git blob changed since review")
    process=subprocess.Popen(
        [str(PYTHON),str(script)],cwd=REPO,
        start_new_session=True,
    )
    try:
        code=process.wait(timeout=max_seconds)
    except subprocess.TimeoutExpired as exc:
        os.killpg(process.pid,signal.SIGKILL)
        process.wait()
        raise Halt("Diagnostic runner exceeded bounded wall time") from exc
    if code!=0:
        if runner_key=="v68-head":
            try:
                publish_v68_failure_probe()
            except (Halt,OSError,subprocess.TimeoutExpired) as exc:
                raise Halt(
                    f"V68 runner failed (exit {code}); numeric failure probe also failed: {type(exc).__name__}"
                ) from exc
            raise Halt(
                f"V68 runner failed (exit {code}); numeric failure report published; campaign stopped for review"
            )
        raise Halt(f"Diagnostic runner failed (exit {code})")


def authorize_training_window(plan,stage,allow_training):
    """A future training runner must be explicitly armed on the local host.

    No trainer is registered in this revision. A repo commit, GitHub report or
    model-generated recommendation alone cannot authorize training.
    """
    if not allow_training:
        raise Halt("Training not explicitly armed by operator")
    if stage["runner"] not in TRAIN_RUNNERS:
        raise Halt("Training adapter unavailable: new trainer freeze required")
    auth_file=AUTH_DIR/f"{plan['campaign_id']}.json"
    auth=strict_json(auth_file)
    if auth_file.stat().st_mode & 0o077:
        raise Halt("Local training authorization must be owner-only (0600)")
    if auth_file.stat().st_uid!=os.getuid():
        raise Halt("Local training authorization owner mismatch")
    protocol=safe_relative(auth.get("protocol_path"),REPO)
    if not (
        auth.get("schema")==TRAIN_AUTH_SCHEMA
        and auth.get("approved") is True
        and auth.get("campaign_id")==plan["campaign_id"]
        and auth.get("runner")==stage["runner"]
        and auth.get("step_id")==stage["step"]
        and isinstance(auth.get("protocol_sha256"),str)
        and SHA256_RE.fullmatch(auth["protocol_sha256"])
        and protocol.is_file()
        and hashlib.sha256(protocol.read_bytes()).hexdigest()==auth["protocol_sha256"]
        and isinstance(auth.get("max_optimizer_steps"),int)
        and type(auth["max_optimizer_steps"]) is int
        and 1<=auth["max_optimizer_steps"]<=1000
        and type(auth.get("max_exposure_tokens")) is int
        and 1<=auth["max_exposure_tokens"]<=5_000_000
        and type(auth.get("max_windows")) is int
        and 1<=auth["max_windows"]<=24
        and type(auth.get("max_wall_seconds")) is int
        and 60<=auth["max_wall_seconds"]<=21600
    ):
        raise Halt("Independent local training authorization invalid")
    raise Halt("No frozen bounded trainer adapter implemented: training remains disabled")


def safe_write(path:Path,data:dict):
    """Atomic state persistence, timestamped backup before each replacement."""
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise Halt("Unsafe AUTOPILOT state path")
    if path.exists():
        backup=path.with_name(path.name+"."+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+".bak")
        backup.write_bytes(path.read_bytes())
        backup.chmod(0o600)
    fd,temp=tempfile.mkstemp(prefix=".autopilot-",dir=str(path.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as stream:
            json.dump(data,stream,sort_keys=True,indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp,0o600)
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def journal(path:Path,event,stage_id,detail=""):
    record={"at":utc_now(),"event":event,"stage":stage_id,"detail":str(detail)[:240]}
    with path.open("a",encoding="utf-8") as stream:
        stream.write(json.dumps(record,sort_keys=True)+"\n")
        stream.flush()
        os.fsync(stream.fileno())


def execute(plan,plan_hash,plan_file,allow_training=False):
    os.umask(0o077)
    root=LOCAL_ROOT/plan["campaign_id"]
    root.mkdir(parents=True,exist_ok=True)
    if root.is_symlink():
        raise Halt("Unsafe campaign run directory")
    lock=root/".autopilot.lock"
    with lock.open("a+") as lock_file:
        try:
            fcntl.flock(lock_file,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Halt("This campaign is already running") from exc
        state_path=root/"state.json"
        journal_path=root/"events.jsonl"
        git_head=git_sync()
        if hashlib.sha256(plan_file.read_bytes()).hexdigest()!=plan_hash:
            raise Halt("Campaign changed after initial review")
        verify_frozen_v62()
        if not PYTHON.is_file():
            raise Halt("Frozen Mini-Kuzai venv Python missing")
        if state_path.exists():
            state=strict_json(state_path)
            if state.get("campaign_id")!=plan["campaign_id"] or state.get("manifest_sha256")!=plan_hash:
                raise Halt("Campaign state cannot be resumed with a different manifest")
            if state.get("status")=="COMPLETED":
                return "ALREADY_COMPLETED",state
        else:
            state={"campaign_id":plan["campaign_id"],"manifest_sha256":plan_hash,
                   "status":"RUNNING","started":utc_now(),"current":None,
                   "completed":[],"skipped":[],"head_at_start":git_head}
            safe_write(state_path,state)
        started=time.monotonic()
        try:
            for stage in plan["steps"]:
                if time.monotonic()-started>=plan["max_wall_seconds"]:
                    raise Halt("Campaign time budget exhausted")
                git_sync()
                if hashlib.sha256(plan_file.read_bytes()).hexdigest()!=plan_hash:
                    raise Halt("Campaign source changed during execution")
                verify_frozen_v62()
                sid=stage["id"]
                state["current"]=sid
                safe_write(state_path,state)
                if not evaluate_rules(stage["when"]):
                    if stage["required"]:
                        raise Halt("Required decision condition rejected next stage")
                    state["skipped"].append(sid)
                    journal(journal_path,"SKIPPED",sid,"Predeclared deterministic branch")
                    safe_write(state_path,state)
                    continue
                if stage["kind"]=="train_window":
                    authorize_training_window(plan,stage,allow_training)
                if stage["kind"]=="diagnostic" and not report_path(stage["step"]).is_file():
                    journal(journal_path,"STARTED",sid,stage["step"])
                    checked_runner(stage["runner"],stage["step"],min(3600,max(1,plan["max_wall_seconds"]-int(time.monotonic()-started))))
                    git_sync()
                metrics=read_report(stage["step"])
                if not evaluate_rules(stage["rules"]):
                    raise Halt("Published GOGIT metrics rejected stage rules: "+sid)
                if sid not in state["completed"]:
                    state["completed"].append(sid)
                journal(journal_path,"VERIFIED",sid,"remote GOGIT "+stage["step"])
                safe_write(state_path,state)
            state["status"]="COMPLETED"
            state["current"]=None
            state["finished"]=utc_now()
            safe_write(state_path,state)
            return "COMPLETED",state
        except (Halt,subprocess.TimeoutExpired,OSError,ValueError,KeyError) as exc:
            state["status"]="HALTED"
            state["reason"]=str(exc)[:240]
            journal(journal_path,"HALTED",state.get("current"),type(exc).__name__)
            safe_write(state_path,state)
            raise Halt(str(exc)) from exc


def main():
    parser=argparse.ArgumentParser(description="Mini-Kuzai local AUTOPILOT V1")
    parser.add_argument("--campaign",default="phase03-autopilot-v1.json")
    parser.add_argument("--check-only",action="store_true")
    parser.add_argument("--allow-training",action="store_true")
    opts=parser.parse_args()
    try:
        plan,digest,source=load_campaign(opts.campaign)
        if opts.check_only:
            print("AUTOPILOT_CHECK: PASS")
            print("CAMPAIGN:",plan["campaign_id"])
            print("STAGES:",len(plan["steps"]))
            print("TRAIN_RUNNERS_REGISTERED:",len(TRAIN_RUNNERS))
            print("TRAINING_STARTED: 0")
            return
        outcome,state=execute(plan,digest,source,allow_training=opts.allow_training)
        print("AUTOPILOT:",outcome)
        print("COMPLETED_STAGES:",len(state["completed"]))
        print("SKIPPED_STAGES:",len(state["skipped"]))
        print("TRAINING_STARTED: 0")
    except (Halt,json.JSONDecodeError,OSError) as exc:
        print("AUTOPILOT: HALTED")
        print("REASON:",str(exc)[:300])
        sys.exit(1)


if __name__=="__main__":
    main()
