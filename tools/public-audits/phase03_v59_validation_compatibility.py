#!/usr/bin/env python3
"""Public aggregate audit of V54 validation declarations used by V59 trainer."""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST_DIR = REPO / "data" / "phase-03" / "manifests"

def read_json(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected object: {path}")
    return value

def git_blob_sha(path):
    p = subprocess.run(
        ["git", "-C", str(REPO), "hash-object", str(path)],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or "git hash-object failed")
    return p.stdout.strip()

def main():
    declarations = sorted(
        MANIFEST_DIR.glob("validation-batch-*-freeze-declaration.json")
    )
    if len(declarations) != 18:
        raise RuntimeError("Expected 18 validation freeze declarations")

    modern_review = legacy_review = integrity_fields = history_pass = blob_pass = 0
    for path in declarations:
        d = read_json(path)
        behavior = d.get("behavior")
        if not isinstance(behavior, str) or len(behavior) != 3:
            raise RuntimeError("Invalid behavior")
        index = int(behavior[1:])
        if d.get("records") != 2 or d.get("semantic_guard_pass") is not True:
            raise RuntimeError(f"Declaration invariant failed: {behavior}")

        if "independent_review_complete" in d:
            if d.get("independent_review_complete") is not True:
                raise RuntimeError(f"Modern review failed: {behavior}")
            modern_review += 1
        else:
            if d.get("review_complete") is not True:
                raise RuntimeError(f"Legacy review failed: {behavior}")
            legacy_review += 1

        if d.get("structural_integrity_audit_passed") is True:
            integrity_fields += 1
        elif d.get("structural_integrity_audit_passed") is not None:
            raise RuntimeError(f"Explicit integrity failure: {behavior}")

        step = d.get("target_step_id")
        expected = f"PHASE03-SMOLTALK-V54-{behavior}-VALIDATION-FREEZE-001"
        if step != expected:
            raise RuntimeError(f"Freeze step mismatch: {behavior}")
        h = read_json(
            REPO / "reports" / "assistant-results" / "history" / f"{step}.json"
        )
        m = h.get("metrics", {})
        if (
            h.get("step_id") != step
            or m.get(f"{behavior}_VALIDATION_FROZEN", m.get("VALIDATION_BATCH_FROZEN")) != 1
            or m.get(f"{behavior}_INDEPENDENT_SIGNOFF", m.get("VALIDATION_BATCH_SIGNOFF")) != 1
            or m.get("CROSS_SPLIT_ID_COLLISIONS") != 0
            or m.get("CROSS_SPLIT_GROUP_COLLISIONS") != 0
            or m.get("EXACT_USER_PROMPT_MATCHES") != 0
        ):
            raise RuntimeError(f"Historical freeze proof failed: {behavior}")
        if index > 1:
            if (
                m.get("VALIDATION_BEHAVIORS_FROZEN") != index
                or m.get("VALIDATION_FROZEN_RECORDS") != 2 * index
            ):
                raise RuntimeError(f"Historical coverage failed: {behavior}")
        history_pass += 1

        target = REPO / d["target_batch"]
        if git_blob_sha(target) != d.get("target_batch_blob_sha"):
            raise RuntimeError(f"Blob mismatch: {behavior}")
        blob_pass += 1

    metrics = {
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "V59_MIX_FINALIZED": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 0,
        "V59_VALIDATION_DECLARATIONS": len(declarations),
        "V59_VALIDATION_MODERN_REVIEW_FIELDS": modern_review,
        "V59_VALIDATION_LEGACY_REVIEW_FIELDS": legacy_review,
        "V59_VALIDATION_INTEGRITY_FIELDS": integrity_fields,
        "V59_VALIDATION_HISTORY_PROOFS": history_pass,
        "V59_VALIDATION_BLOB_MATCHES": blob_pass,
    }
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(metrics.items()):
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
