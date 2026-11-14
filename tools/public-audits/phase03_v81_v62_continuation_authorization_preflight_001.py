#!/usr/bin/env python3
"""Public CPU-only preflight for V81 V62 continuation authorization.

This audit validates the proposed authorization object and launcher guards
without writing authorization artifacts, starting training, touching CUDA,
writing checkpoints, or opening BLIND data.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "tools" / "phase03_v81_v62_continuation_authorization.py"
LAUNCHER = REPO / "tools" / "train_v81_v62_continuation.py"
OUT = REPO / "reviews" / "smoltalk-v81-v62-continuation-authorization"

spec = importlib.util.spec_from_file_location(
    "phase03_v81_v62_continuation_authorization_preflight",
    SOURCE,
)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load V81 continuation authorization producer")

module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

if OUT.exists() or OUT.is_symlink():
    raise RuntimeError("V81 authorization artifacts already exist before preflight")

freeze, report = module.build()

if freeze.get("status") != "FROZEN":
    raise RuntimeError("Proposed V81 continuation freeze status mismatch")
if freeze.get("authorization_scope") != "V81_V62_INITIAL_WINDOW_REMAINDER_ONLY":
    raise RuntimeError("Proposed V81 authorization scope mismatch")
if freeze.get("resume_required") is not True:
    raise RuntimeError("V81 continuation does not require resume")
if freeze.get("starting_optimizer_steps") != 69:
    raise RuntimeError("V81 starting optimizer steps mismatch")
if freeze.get("starting_exposure_tokens") != 597982:
    raise RuntimeError("V81 starting exposure mismatch")
if freeze.get("max_total_optimizer_steps") != 145:
    raise RuntimeError("V81 max total optimizer steps mismatch")
if freeze.get("max_total_exposure_tokens") != 1181664:
    raise RuntimeError("V81 max total exposure mismatch")
if freeze.get("max_remaining_optimizer_steps") != 76:
    raise RuntimeError("V81 remaining optimizer-step budget mismatch")
if freeze.get("max_remaining_exposure_tokens") != 583682:
    raise RuntimeError("V81 remaining exposure budget mismatch")
if freeze.get("final_review_cycle") != 4:
    raise RuntimeError("V81 final review cycle mismatch")
if freeze.get("blind_test_during_training") is not False:
    raise RuntimeError("V81 proposed authorization permits BLIND access")
if freeze.get("extension_beyond_cycle4_requires_new_protocol") is not True:
    raise RuntimeError("V81 continuation extension boundary missing")
if any(
    freeze.get(key) is not False
    for key in (
        "objective_changes_allowed",
        "tokenizer_changes_allowed",
        "architecture_changes_allowed",
        "corpus_changes_allowed",
        "stream_weight_changes_allowed",
        "scheduler_changes_allowed",
    )
):
    raise RuntimeError("V81 proposed authorization permits frozen-scope changes")

if report.get("status") != "TRAINING_AUTHORIZED_NOT_STARTED":
    raise RuntimeError("Proposed V81 report status mismatch")
if report.get("training_authorized") is not True:
    raise RuntimeError("Proposed V81 report does not represent authorization")
if report.get("training_started") is not False:
    raise RuntimeError("Proposed V81 report already marks training started")
if report.get("blind_test_accessed") is not False:
    raise RuntimeError("Proposed V81 report indicates BLIND access")

source_text = SOURCE.read_text(encoding="utf-8")
launcher_text = LAUNCHER.read_text(encoding="utf-8")

required_source_guards = (
    'parser.add_argument("--authorize", action="store_true")',
    'parser.add_argument("--write", action="store_true")',
    'if args.write and not args.authorize:',
    'fail("--write requires explicit --authorize")',
)
if not all(item in source_text for item in required_source_guards):
    raise RuntimeError("V81 authorization write guards are incomplete")

required_launcher_guards = (
    'parser.add_argument("--execute", action="store_true")',
    'os.environ.get("MINI_KUZAI_V81_TRAINING_ENABLED") != "YES"',
    '"--resume"',
)
if not all(item in launcher_text for item in required_launcher_guards):
    raise RuntimeError("V81 launcher live guards are incomplete")

metrics = {
    "SEMANTIC_VALIDATION_COMPLETE": 0,
    "TRAINING_AUTHORIZED": 0,
    "TRAINING_STARTED": 0,
    "V81_AUTH_PREFLIGHT_PASS": 1,
    "V81_AUTH_PREFLIGHT_START_RECEIPT": 1,
    "V81_AUTH_PREFLIGHT_READINESS": 1,
    "V81_AUTH_PREFLIGHT_BUILD": 1,
    "V81_AUTH_PREFLIGHT_OUTPUT_ABSENT": 1,
    "V81_AUTH_PREFLIGHT_AUTHORIZE_FLAG": 1,
    "V81_AUTH_PREFLIGHT_WRITE_GUARD": 1,
    "V81_AUTH_PREFLIGHT_EXECUTE_FLAG": 1,
    "V81_AUTH_PREFLIGHT_ENV_GATE": 1,
    "V81_AUTH_PREFLIGHT_RESUME_ARG": 1,
    "V81_AUTH_PREFLIGHT_BLIND_ACCESS": 0,
    "V81_AUTH_PREFLIGHT_GPU_EXECUTION": 0,
    "V81_AUTH_PREFLIGHT_CHECKPOINT_WRITE": 0,
    "V81_AUTH_PREFLIGHT_START_STEPS": 69,
    "V81_AUTH_PREFLIGHT_START_EXPOSURE": 597982,
    "V81_AUTH_PREFLIGHT_MAX_TOTAL_STEPS": 145,
    "V81_AUTH_PREFLIGHT_MAX_TOTAL_EXPOSURE": 1181664,
    "V81_AUTH_PREFLIGHT_MAX_REMAINING_STEPS": 76,
    "V81_AUTH_PREFLIGHT_MAX_REMAINING_EXPOSURE": 583682,
    "V81_AUTH_PREFLIGHT_FINAL_REVIEW_CYCLE": 4,
    "V81_AUTH_PREFLIGHT_FROZEN_SCOPE_CHANGES": 0,
}

print("##### SECTION RESULTS FOR ASSISTANT ######")
for key, value in sorted(metrics.items()):
    print(f"{key}: {value}")
