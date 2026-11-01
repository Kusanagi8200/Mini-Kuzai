#!/usr/bin/env python3
"""V74 bounded read-only GPU controls, 2 x 30-metric immutable GOGIT reports.

Batch workflow with fail-closed gates and resumable CORE/STRATA publication.
No training, BLIND, GitHub Discussion post or DEV-FLOW FINAL request is made.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
RUN = Path("/root/Mini-Kuzai/runs/v62-margin-001")
HISTORY = ROOT / "reports" / "assistant-results" / "history"
HELPER = "tools/v74_frequency_prior.py"
HELPER_BLOB = "a1bbbb103500b5381c7518be88900ab3ddac6a18"
AUDITS = {
    "CORE": (
        "tools/public-audits/phase03_v74_frequency_prior_core_001.py",
        "aa3b8ab654ad9998dafb36cdae980a6704f4f69e",
        "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001",
        "V74_CORE_",
    ),
    "STRATA": (
        "tools/public-audits/phase03_v74_frequency_prior_strata_001.py",
        "fe765fb006bf907b5c2055295878a9ee5a8d6881",
        "PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001",
        "V74_STRATA_",
    ),
}
SAFE = ("SEMANTIC_VALIDATION_COMPLETE", "TRAINING_AUTHORIZED",
        "TRAINING_STARTED")
BINS = ("F0", "F1_9", "F10_99", "F100P")
MODES = ("ORIG", "CENTER", "PC1", "UNIGRAM")
ORIGINS = {
    "https://github.com/Kusanagi8200/Mini-Kuzai.git",
    "https://github.com/Kusanagi8200/Mini-Kuzai",
    "git@github.com:Kusanagi8200/Mini-Kuzai.git",
}


def git(*args):
    p = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True,
        text=True, check=False,
    )
    if p.returncode:
        raise RuntimeError("V74 Git validation failed")
    return p.stdout.strip()


def synced():
    if (git("branch", "--show-current") != "main"
            or git("remote", "get-url", "origin") not in ORIGINS
            or git("status", "--porcelain")):
        raise RuntimeError("V74 requires clean main and approved Git origin")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("V74 local and remote main differ")


def read_json(path: Path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("V74 reviewed JSON missing or unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("V74 JSON object invalid")
    return value


def pinned_sources():
    for file, blob in [(HELPER, HELPER_BLOB)] + [
        (audit, sha) for audit, sha, _step, _prefix in AUDITS.values()
    ]:
        path = ROOT / file
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("V74 source missing or unsafe")
        if git("rev-parse", "HEAD:" + file) != blob:
            raise RuntimeError("V74 reviewed Git source blob changed")


def preflight():
    if not PYTHON.is_file() or PYTHON.is_symlink():
        raise RuntimeError("V74 Python interpreter missing or unsafe")
    if RUN.is_symlink() or not RUN.is_dir() or (RUN / ".training.lock").exists():
        raise RuntimeError("V74 frozen training run missing or locked")
    summary = read_json(RUN / "RUN-SUMMARY.json")
    manifest = read_json(RUN / "RUN-MANIFEST.json")
    checkpoint = RUN / "checkpoint-cycle-02.pt"
    if not (
        summary.get("schema_version") == "v62-margin-run-summary-1"
        and manifest.get("schema_version") == "v62-margin-run-1"
        and summary.get("status") == manifest.get("status") == "STOPPED"
        and summary.get("stop_reason") == "MILESTONE_REVIEW_REQUIRED"
        and summary.get("optimizer_steps") == 69
        and summary.get("exposure_tokens") == 597982
        and summary.get("blind_test_accessed") is False
        and manifest.get("blind_test_during_training") is False
        and manifest.get("resume") is False
        and checkpoint.is_file() and not checkpoint.is_symlink()
    ):
        raise RuntimeError("V74 V62 checkpoint and stop-state gate failed")
    receipt = read_json(ROOT / "automation/dev-flow/receipts/V74-start.json")
    if not all((
        receipt.get("schema_version") == 1,
        receipt.get("command") == "START-DEV-FLOW",
        receipt.get("step") == "V74",
        receipt.get("status") == "PUBLISHED",
        receipt.get("github_url") ==
            "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5",
    )):
        raise RuntimeError("V74 official START receipt absent or invalid")
    for name, producer, keys in [
        ("PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001",
         "tools/public-audits/phase03_v65_token_frequency_diagnostic_001.py",
         {"V65_FREQ_TRAIN_LEXICAL": 294726, "V65_FREQ_TRAIN_TYPES": 891,
          "V65_FREQ_PASS": 1, "V65_FREQ_VAL_LEXICAL": 9170,
          "V65_FREQ_BLIND_ACCESS": 0}),
        ("PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001",
         "tools/public-audits/phase03_v73_principal_axis_attribution_001.py",
         {"V73_AXIS_PASS": 1, "V73_AXIS_VAL_LEXICAL": 9170,
          "V73_AXIS_BLIND_ACCESS": 0, "V73_AXIS_CENTER_CORRECT": 2832,
          "V73_AXIS_PC1_ONLY_CORRECT": 2455}),
    ]:
        report = read_json(HISTORY / (name + ".json"))
        source = ROOT / producer
        metrics = report.get("metrics")
        if not (
            source.is_file() and not source.is_symlink()
            and report.get("step_id") == name
            and report.get("producer") == producer
            and report.get("producer_sha256") ==
                hashlib.sha256(source.read_bytes()).hexdigest()
            and report.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
            and report.get("training_authorized") is False
            and report.get("semantic_validation_complete") is False
            and report.get("private_conversation_data_included") is False
            and isinstance(metrics, dict) and len(metrics) == 30
            and all(type(v) is int and 0 <= v <= 100000000
                    for v in metrics.values())
            and all(metrics.get(key) == val for key, val in keys.items())
            and all(metrics.get(field) == 0 for field in SAFE)
        ):
            raise RuntimeError("V74 V65/V73 immutable evidence gate failed")
    active = subprocess.run(
        ["systemctl", "is-active", "llama-server-a.service"],
        capture_output=True, text=True, check=False,
    )
    if active.stdout.strip() == "active":
        raise RuntimeError("V74 GPU occupied by llama-server-a; stop separately")


def verified_history(mode):
    audit, _blob, step, prefix = AUDITS[mode]
    r = read_json(HISTORY / (step + ".json"))
    metrics = r.get("metrics")
    if not (
        r.get("step_id") == step
        and r.get("source") ==
            "Mini-Kuzai V74 frozen TRAIN unigram versus principal-axis frequency controls"
        and r.get("producer") == audit
        and r.get("producer_sha256") ==
            hashlib.sha256((ROOT / audit).read_bytes()).hexdigest()
        and r.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and r.get("semantic_validation_complete") is False
        and r.get("training_authorized") is False
        and r.get("private_conversation_data_included") is False
        and isinstance(metrics, dict) and len(metrics) == 30
        and all(type(v) is int and 0 <= v <= 100000000
                for v in metrics.values())
        and all(metrics.get(field) == 0 for field in SAFE)
        and all(field in SAFE or field.startswith(prefix) for field in metrics)
        and metrics.get(prefix + "PASS") == 1
        and metrics.get(prefix + "BLIND_ACCESS") == 0
        and metrics.get(prefix + "VAL_LEXICAL") == 9170
        and sum(metrics.get(prefix + b + "_COUNT", 0) for b in BINS) == 9170
    ):
        raise RuntimeError("V74 published metric integrity gate failed")
    return metrics


def verify_pair(core, strata):
    if not (
        core["V74_CORE_VAL_LEXICAL"] == strata["V74_STRATA_VAL_LEXICAL"] == 9170
        and strata["V74_STRATA_TRAIN_LEXICAL"] == 294726
        and strata["V74_STRATA_TRAIN_TYPES"] == 891
        and all(core[f"V74_CORE_{b}_COUNT"] ==
                strata[f"V74_STRATA_{b}_COUNT"] for b in BINS)
        and all(core[f"V74_CORE_{mode}_CORRECT"] ==
                sum(strata[f"V74_STRATA_{mode}_{b}_CORRECT"] for b in BINS)
                for mode in MODES)
        and core["V74_CORE_CENTER_CORRECT"] == 2832
        and core["V74_CORE_PC1_CORRECT"] == 2455
        and core["V74_CORE_ORIG_CORRECT"] == 2673
        and core["V74_CORE_UNIGRAM_DISTINCT"] == 1
        and core["V74_CORE_UNIGRAM_TOP1_SHARE_BP"] == 10000
        and 0 <= strata["V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT"]
        <= min(strata["V74_STRATA_PC1_UNIGRAM_AGREE"],
               core["V74_CORE_PC1_CORRECT"],
               core["V74_CORE_UNIGRAM_CORRECT"])
    ):
        raise RuntimeError("V74 independently published CORE/STRATA disagree")


def checked(cmd, label):
    p = subprocess.run(cmd, cwd=ROOT, check=False)
    if p.returncode:
        raise RuntimeError(label + " failed, exit " + str(p.returncode))


def main():
    synced()
    pinned_sources()
    preflight()

    existing = {mode: (HISTORY / (step + ".json")).exists()
                for mode, (_audit, _blob, step, _p) in AUDITS.items()}
    if not all(existing.values()):
        # A single bounded test pass precedes either potentially expensive GPU GOGIT.
        for test in (
            "test_phase03_v65_token_frequency_diagnostic_001.py",
            "test_phase03_v73_principal_axis_attribution_001.py",
            "test_phase03_v74_frequency_prior_001.py",
        ):
            checked([
                str(PYTHON), "-m", "unittest", "discover",
                "-s", "tests", "-p", test, "-v",
            ], "V74 prerequisite CPU regression " + test)
        synced()
        pinned_sources()

    for mode, (audit, _blob, step, _prefix) in AUDITS.items():
        history_file = HISTORY / (step + ".json")
        if history_file.exists():
            verified_history(mode)
            print("V74_" + mode + "_GOGIT=ALREADY_VERIFIED", flush=True)
            continue
        synced()
        checked([
            str(PYTHON), "tools/gogit_public.py",
            "--step", step, "--audit", audit,
        ], "V74 " + mode + " GOGIT")
        synced()
        verified_history(mode)
        print("V74_" + mode + "_GOGIT=VERIFIED", flush=True)

    core = verified_history("CORE")
    strata = verified_history("STRATA")
    verify_pair(core, strata)
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    print("V74_GOGIT=COMPLETE_AND_CROSS_VERIFIED")
    print("CORE_STEP=" + AUDITS["CORE"][2])
    print("STRATA_STEP=" + AUDITS["STRATA"][2])
    print("TRAINING_STARTED=0")
    print("BLIND_ACCESS=0")
    print("FINAL_DEV_FLOW=NOT_TRIGGERED")
    print("HEAD=" + git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError, KeyboardInterrupt) as exc:
        print("##### SECTION RESULTS FOR ASSISTANT ######")
        print("V74_GOGIT=BLOCKED")
        print("ERROR_TYPE=" + type(exc).__name__)
        # No untrusted payloads or private dataset text in terminal output.
        print("ERROR=" + str(exc))
        sys.exit(1)
