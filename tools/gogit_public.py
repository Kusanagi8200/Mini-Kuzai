#!/usr/bin/env python3
"""Execute a reviewed public SmolTalk audit and publish numeric-only gogit reports.

Only committed Python scripts in tools/public-audits are accepted.
Raw stdout, conversations, commands, prose and unapproved keys are never published.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUDITS = REPO / "tools" / "public-audits"
REPORTS = REPO / "reports" / "assistant-results"
SOURCE = "SmolTalk v0.4 - public external dataset"
MARKER = "##### SECTION RESULTS FOR ASSISTANT ######"
METRIC_KEYS = {
    "TOTAL_SOURCE", "TOTAL_CANDIDATS", "SMOL_MAGPIE", "TWO_ANCHORED",
    "PARTIAL_ANCHOR", "LOW_LEXICAL_ANCHOR", "REVIEWED",
    "RETAINED", "HELD", "REJECTED", "FACTCHECK_PENDING",
    "SEMANTICALLY_COHERENT", "TOPIC_SWITCHES", "UNVERIFIED_CLAIMS",
    "MULTITURN", "SINGLE_TURN", "FOLLOWUP", "CLARIFICATION",
    "REVISION", "DISAGREEMENT", "CREATIVE", "FACTUAL_QA",
    "PROGRAMMING", "MATHEMATICS", "WRITING", "OTHER",
    "CREATIVE_AVAILABLE", "CREATIVE_SELECTED", "CREATIVE_SHORTFALL",
    "CATEGORY_SHORTFALL_TOTAL", "SOURCE_SHORTFALL_TOTAL",
    "SOURCE_SMOL_SELECTED", "SOURCE_HERMES_SELECTED",
    "SOURCE_OSS_SELECTED", "SOURCE_REWRITE_SELECTED",
    "SOURCE_SMOL_SHORTFALL", "SOURCE_HERMES_SHORTFALL",
    "SOURCE_OSS_SHORTFALL", "SOURCE_REWRITE_SHORTFALL",
    "V46_BROAD_CREATIVE_ALL", "V46_BROAD_CREATIVE_UNSELECTED",
    "V46_BROAD_CREATIVE_SELECTED_OTHER", "V46_REVIEW_BASE",
    "V46_REVIEW_RESCUE", "V46_REVIEW_RECLASS", "V46_REVIEW_TOTAL",
    "V47_QUEUE_TOTAL", "V47_BASELINE", "V47_RECLASS",
    "V47_RESCUE", "V47_PRIORITY", "V47_UNREVIEWED",
    "V47_SOURCE_MATCHED", "V47_TRAIN_APPROVED",
    "V48_QUEUE_TOTAL", "V48_REVIEWED", "V48_UNREVIEWED",
    "V48_PRIORITY_REVIEWED", "V48_BASELINE_REVIEWED",
    "V48_RETAINED", "V48_REJECTED", "V48_HELD",
    "V48_REVISIONS", "V48_TRAIN_APPROVED",
    "V50_QUEUE_TOTAL", "V50_REVIEWED", "V50_HIGH_HINT",
    "V50_MEDIUM_HINT", "V50_LOW_HINT", "V50_CREATIVE_HINT",
    "V50_COGNITIVE_HINT", "V50_FOLLOWUP_HINT", "V50_FEEDBACK_HINT",
    "V50_TECHNICAL_HINT", "V50_MULTITURN", "V50_TRAIN_APPROVED",
    "V51_QUEUE_TOTAL", "V51_REVIEWED", "V51_UNREVIEWED",
    "V51_HIGH_REVIEWED", "V51_MEDIUM_REVIEWED", "V51_LOW_REVIEWED",
    "V51_A", "V51_B", "V51_C", "V51_HELD", "V51_TRAIN_APPROVED",
    "V52_QUEUE_TOTAL", "V52_V48_EXCLUDED", "V52_V51_EXCLUDED",
    "V52_AVAILABLE", "V52_MULTITURN", "V52_TRAIN_APPROVED",
    "V52_HIGH_SMOL_TOTAL", "V52_HIGH_SMOL_MULTITURN", "V52_HIGH_HERMES_TOTAL",
    "V52_HIGH_HERMES_MULTITURN", "V52_HIGH_OSS_TOTAL", "V52_HIGH_OSS_MULTITURN",
    "V52_HIGH_REWRITE_TOTAL", "V52_HIGH_REWRITE_MULTITURN", "V52_MEDIUM_SMOL_TOTAL",
    "V52_MEDIUM_SMOL_MULTITURN", "V52_MEDIUM_HERMES_TOTAL", "V52_MEDIUM_HERMES_MULTITURN",
    "V52_MEDIUM_OSS_TOTAL", "V52_MEDIUM_OSS_MULTITURN", "V52_MEDIUM_REWRITE_TOTAL",
    "V52_MEDIUM_REWRITE_MULTITURN", "V52_LOW_SMOL_TOTAL", "V52_LOW_SMOL_MULTITURN",
    "V52_LOW_HERMES_TOTAL", "V52_LOW_HERMES_MULTITURN", "V52_LOW_OSS_TOTAL",
    "V52_LOW_OSS_MULTITURN", "V52_LOW_REWRITE_TOTAL", "V52_LOW_REWRITE_MULTITURN",
    "V52_PUBLIC_QUEUE_TOTAL", "V52_PUBLIC_PENDING", "V52_PUBLIC_REVIEWED",
    "V52_PUBLIC_A", "V52_PUBLIC_B", "V52_PUBLIC_C",
    "V52_PUBLIC_HELD", "V52_PUBLIC_HIGH", "V52_PUBLIC_MEDIUM",
    "V52_PUBLIC_LOW", "V52_PUBLIC_SMOL", "V52_PUBLIC_HERMES",
    "V52_PUBLIC_OSS", "V52_PUBLIC_REWRITE", "V52_PUBLIC_MULTITURN",
    "V52_PUBLIC_TRAIN_APPROVED",
    "V53_PUBLIC_TOTAL", "V53_SOURCE_MATCHED", "V53_DISTINCT_SOURCE_IDS",
    "V53_DUPLICATE_SOURCE_IDS", "V53_V44_REVIEWED",
    "V53_OUTSIDE_V44_REVIEWED", "V53_V48_TOTAL", "V53_V48_RETAINED",
    "V53_V48_REJECTED", "V53_V48_HELD", "V53_V51_TOTAL", "V53_V51_A",
    "V53_V51_B", "V53_V51_C", "V53_V51_HELD", "V53_V52_TOTAL",
    "V53_V52_A", "V53_V52_B", "V53_V52_C", "V53_V52_HELD",
    "V53_V51V52_A", "V53_V51V52_B", "V53_V51V52_C",
    "V53_UNRESOLVED", "V53_TRAIN_APPROVED",
    "V53_G2_REVIEWED_TOTAL", "V53_G2_A_TOTAL",
    "V53_G2_A_LOW_RISK", "V53_G2_A_REVIEW_RISK",
    "V53_G2_A_STRONG_CONTINUITY", "V53_G2_A_STRONG_CREATIVITY",
    "V53_G2_A_STRONG_CORRECTION", "V53_G2_B_TOTAL",
    "V53_G2_B_REPAIR_PRIORITY", "V53_G2_B_SUPPORTING",
    "V53_G2_B_LOW_PERSONA", "V53_G2_B_HIGH_RISK",
    "V53_G2_C_ERROR_ANALYSIS", "V53_G2_UNRESOLVED",
    "V53_G2_TRAIN_APPROVED",
    "V53_G3_REPAIR_TOTAL", "V53_G3_SOURCE_MATCHED",
    "V53_G3_GATE2_PRIORITY_CONFIRMED", "V53_G3_SEGMENTATION_REQUIRED",
    "V53_G3_FACTUAL_NUMERIC_FIX",
    "V53_G3_UNCERTAINTY_LOGIC_CALIBRATION",
    "V53_G3_WORDING_CONSTRAINT_CLEANUP", "V53_G3_TRAIN_APPROVED",
    "V53_DERIVATIVE_TOTAL", "V53_DERIVATIVE_SOURCE_MATCHED",
    "V53_DERIVATIVE_USER_SOURCE_TURNS",
    "V53_DERIVATIVE_ASSISTANT_REWRITES",
    "V53_DERIVATIVE_REVIEW_PENDING",
    "V53_DERIVATIVE_TRAIN_APPROVED",
    "V53_DERIVATIVE_SPLIT_ASSIGNED",
    "V53_DERIVATIVE_SEMANTIC_VALIDATED",
    "V53_DERIV_REVIEW_TOTAL", "V53_DERIV_REVIEW_COMPLETE",
    "V53_DERIV_REVIEW_QUALITY_PASS", "V53_DERIV_REVIEW_FACTUAL_PASS",
    "V53_DERIV_REVIEW_COHERENCE_PASS", "V53_DERIV_REVIEW_BEHAVIOR_PASS",
    "V53_DERIV_REVIEW_INSTRUCTION_PASS",
    "V53_DERIV_REVIEW_ELIGIBILITY_READY",
    "V53_DERIV_REVIEW_FURTHER_REPAIR", "V53_DERIV_REVIEW_NEW_ERRORS",
    "V53_DERIV_REVIEW_TRAIN_APPROVED", "V53_DERIV_REVIEW_SPLIT_ASSIGNED",
    "V53_DERIV_REVIEW_SEMANTIC_VALIDATED",
    "V53_ELIG_TOTAL", "V53_ELIG_PROVENANCE_PASS",
    "V53_ELIG_LICENSE_PASS", "V53_ELIG_CANONICAL_TRAIN_RECORDS",
    "V53_ELIG_EXACT_DUP_HITS", "V53_ELIG_NEAR_DUP_HITS",
    "V53_ELIG_RESERVED_VALIDATION_COLLISIONS",
    "V53_ELIG_SEMANTIC_PASS", "V53_ELIG_SEMANTIC_BLOCKED",
    "V53_ELIG_ADMISSION_READY", "V53_ELIG_TRAIN_APPROVED",
    "V53_ELIG_SPLIT_ASSIGNED",
    "V53_ADMIT_DECISIONS_TOTAL", "V53_ADMIT_CORPUS_APPROVED",
    "V53_ADMIT_TARGET_TRAIN", "V53_ADMIT_GROUP_VALID",
    "V53_ADMIT_RESERVED_ID_FREE", "V53_ADMIT_CANONICAL_TRAIN_RECORDS",
    "V53_ADMIT_SERIALIZED", "V53_ADMIT_MODEL_TRAINING_AUTHORIZED",
    "V53_B08_SERIALIZED_RECORDS", "V53_B08_REVIEWED_RECORDS",
    "V53_B08_METADATA_CORRECTIONS", "V53_B08_MODEL_VISIBLE_CHANGES",
    "V53_B08_GROUP_TRAIN_VALID", "V53_B08_RESERVED_OVERLAP",
    "V53_B08_CANONICAL_TRAIN_RECORDS", "V53_B08_GROUP_CURRENT",
    "V53_B08_GROUP_PLANNED", "V53_B08_TRAIN_COMPLETE",
    "V53_B08_MODEL_TRAINING_AUTHORIZED",
    "V53_B08C_GROUP_RECORDS", "V53_B08C_NEW_DESIGNED_RECORDS",
    "V53_B08C_EXTERNAL_RECORDS", "V53_B08C_REVIEWED_RECORDS",
    "V53_B08C_GROUP_COMPLETE", "V53_B08C_BEHAVIOR_COMPLETE",
    "V53_B08C_RESERVED_OVERLAP", "V53_B08C_CANONICAL_TRAIN_RECORDS",
    "V53_B08C_VALIDATION_TEXT_CREATED",
    "V53_B08C_MODEL_TRAINING_AUTHORIZED",
    "V53_AW2_INSPECTED", "V53_AW2_SOURCE_MATCHED",
    "V53_AW2_LOW_RISK_A", "V53_AW2_DERIVATIVE_READY",
    "V53_AW2_DEFER_NO_GROUP", "V53_AW2_DEFER_RESERVED",
    "V53_AW2_DERIVATIVE_CREATED", "V53_AW2_B12_ROUTE_VALID",
    "V53_AW2_TRAIN_APPROVED",
}
STEP_RE = re.compile(r"PHASE03-SMOLTALK-[A-Z0-9][A-Z0-9-]{3,80}\Z")
METRIC_RE = re.compile(r"([A-Z][A-Z0-9_]+):\s*([0-9]+)\Z")


def git(*args):
    p = subprocess.run(["git", "-C", str(REPO), *args], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=False)
    if p.returncode != 0:
        raise RuntimeError(
            f"Git command failed ({' '.join(args[:2])}): {p.stderr.strip()}"
        )
    return p.stdout.strip()


def require_clean_synchronized():
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Expected branch main")
    if git("status", "--porcelain"):
        raise RuntimeError("Git worktree/index not clean; publication blocked")
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("Local and remote main differ; synchronize before publishing")


def checked_audit(path_string):
    path = (REPO / path_string).resolve()
    try:
        rel = path.relative_to(AUDITS.resolve())
    except ValueError as exc:
        raise RuntimeError("Audit is outside tools/public-audits") from exc
    if not path.is_file() or path.suffix != ".py" or rel.parent != Path("."):
        raise RuntimeError("Only direct tools/public-audits/*.py files are allowed")
    tracked = str(path.relative_to(REPO))
    git("ls-files", "--error-unmatch", "--", tracked)
    if git("status", "--porcelain", "--", tracked):
        raise RuntimeError("Audit script must be committed and clean")
    return path, tracked


def numeric_metrics(raw):
    if raw.count(MARKER) != 1:
        raise RuntimeError("Expected exactly one results marker")
    suffix = raw.split(MARKER, 1)[1].strip()
    if not suffix:
        raise RuntimeError("No public numeric results found")
    metrics = {}
    for line in suffix.splitlines():
        match = METRIC_RE.fullmatch(line.strip())
        if not match:
            raise RuntimeError("Non-numeric or unstructured result rejected")
        key, value = match.groups()
        if key not in METRIC_KEYS or key in metrics:
            raise RuntimeError("Unknown or repeated metric rejected")
        metrics[key] = int(value)
        if metrics[key] > 100000000:
            raise RuntimeError("Unreasonably large metric rejected")
    if len(metrics) > 30:
        raise RuntimeError("Too many metrics")
    return dict(sorted(metrics.items()))


def main():
    parser = argparse.ArgumentParser(
        description="Run a vetted public SmolTalk audit, commit and push numeric reports"
    )
    parser.add_argument("--step", required=True)
    parser.add_argument("--audit", required=True)
    args = parser.parse_args()
    if not STEP_RE.fullmatch(args.step):
        parser.error("STEP_ID must match PHASE03-SMOLTALK-[A-Z0-9-]")
    try:
        require_clean_synchronized()
        audit_path, tracked = checked_audit(args.audit)
        history = REPORTS / "history"
        out_json = history / (args.step + ".json")
        out_txt = history / (args.step + ".txt")
        if out_json.exists() or out_txt.exists():
            raise RuntimeError("STEP_ID history exists; overwriting forbidden")
        if not (REPORTS / "latest.json").is_file() or not (
            REPORTS / "latest.txt"
        ).is_file():
            raise RuntimeError("Existing latest reports not found")

        execution = subprocess.run(
            [sys.executable, str(audit_path)],
            cwd=REPO, capture_output=True, text=True, timeout=300,
            check=False
        )
        if execution.returncode:
            raise RuntimeError(
                f"Audit exited with status {execution.returncode}; nothing published"
            )
        metrics = numeric_metrics(execution.stdout)
        report = {
            "step_id": args.step,
            "project": "Mini-Kuzai",
            "phase": "03",
            "source": SOURCE,
            "producer": tracked,
            "producer_sha256": hashlib.sha256(
                audit_path.read_bytes()
            ).hexdigest(),
            "status": "PUBLIC_AGGREGATE_REVIEW_ONLY",
            "metrics": metrics,
            "semantic_validation_complete": False,
            "training_authorized": False,
            "private_conversation_data_included": False,
        }
        text_json = json.dumps(
            report, indent=2, ensure_ascii=True, sort_keys=True
        ) + "\n"
        text_txt = (
            f"STEP_ID: {args.step}\n{MARKER}\n"
            + "".join(f"{k}: {v}\n" for k, v in metrics.items())
            + "STATUS: PUBLIC_AGGREGATE_REVIEW_ONLY\n"
            + "TRAINING_AUTHORIZED: FALSE\n"
        )

        old_files = {
            name: (REPORTS / name).read_bytes()
            for name in ("latest.json", "latest.txt")
        }
        backup_root = Path("/root/Mini-Kuzai/backups/gogit")
        backup_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        backup = Path(
            tempfile.mkdtemp(prefix="auto-", dir=backup_root)
        )
        os.chmod(backup, 0o700)
        for name, blob in old_files.items():
            (backup / name).write_bytes(blob)
        print("BACKUP:", backup)

        allowed = {
            str((REPORTS / "latest.json").relative_to(REPO)),
            str((REPORTS / "latest.txt").relative_to(REPO)),
            str(out_json.relative_to(REPO)),
            str(out_txt.relative_to(REPO)),
        }
        committed = False
        try:
            (REPORTS / "latest.json").write_text(
                text_json, encoding="utf-8"
            )
            (REPORTS / "latest.txt").write_text(
                text_txt, encoding="utf-8"
            )
            out_json.write_text(text_json, encoding="utf-8")
            out_txt.write_text(text_txt, encoding="utf-8")
            git("add", "--", *sorted(allowed))
            staged = set(git("diff", "--cached", "--name-only").splitlines())
            if staged != allowed:
                raise RuntimeError("Unexpected staged files; commit blocked")
            git("diff", "--cached", "--check")
            git(
                "commit", "-m",
                f"Phase03 public SmolTalk audit {args.step}"
            )
            committed = True
        except Exception:
            if not committed:
                git("reset", "--quiet", "--", *sorted(allowed))
                for name, blob in old_files.items():
                    (REPORTS / name).write_bytes(blob)
                out_json.unlink(missing_ok=True)
                out_txt.unlink(missing_ok=True)
            raise

        push = subprocess.run(
            ["git", "-C", str(REPO), "push", "origin", "main"],
            capture_output=True, text=True, check=False
        )
        if push.returncode:
            raise RuntimeError(
                "Commit created but push failed. Inspect Git; never force push."
            )
        git("fetch", "--quiet", "origin", "main")
        if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
            raise RuntimeError("Push successful but remote verification failed")
        print(MARKER)
        print("PUSH: OK")
        print("STEP_ID:", args.step)
        print("PUBLIC_METRICS:", len(metrics))
        print("HEAD:", git("rev-parse", "--short", "HEAD"))
        print("GOGIT: READY")
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print(MARKER)
        print("PUSH: NOT_CONFIRMED")
        print("ERROR:", str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
