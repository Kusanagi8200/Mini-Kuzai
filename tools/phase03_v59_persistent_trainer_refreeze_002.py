#!/usr/bin/env python3
"""V59 persistent trainer refreeze 002 wrapper."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v59_trainer as T

BASE = REPO / "tools" / "phase03_v59_persistent_trainer_freeze.py"
OUT = REPO / "reviews" / "smoltalk-v59-persistent-trainer-freeze"
MANIFEST = OUT / "TRAINER-FREEZE-002.json"
REPORT = OUT / "REPORT-002.json"
RESULTS = OUT / "RESULTS-002.md"
TRAINER_SOURCE = REPO / "mini_kuzai" / "phase03_v59_trainer.py"
CLI_SOURCE = REPO / "tools" / "train_v59_bounded_pilot.py"

spec = importlib.util.spec_from_file_location("v59_freeze_base", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load base freeze builder")
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)


def main() -> None:
    if not (OUT / "TRAINER-FREEZE-001.json").is_file():
        raise RuntimeError("Historical freeze 001 is missing")
    if any(path.exists() for path in (MANIFEST, REPORT, RESULTS)):
        raise RuntimeError("Refreeze 002 output already exists")

    manifest, report = base.build_freeze()
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(
        json.dumps({
            **report,
            "refreeze_revision": 2,
            "reason": "step-0 generated probe invalid UTF-8 handling",
            "supersedes_trainer_freeze": "TRAINER-FREEZE-001.json",
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    runtime = T.verify_runtime(TRAINER_SOURCE, CLI_SOURCE)
    if runtime["trainer_freeze"]["trainer_freeze_fingerprint"] != manifest["trainer_freeze_fingerprint"]:
        raise RuntimeError("Runtime verified a different trainer freeze")

    RESULTS.write_text(
        "# Mini-Kuzai V59 - persistent trainer refreeze 002\n\n"
        "Status --> **PERSISTENT TRAINER REFROZEN / TRAINING NOT STARTED**\n\n"
        "Reason --> step-0 generated probe invalid UTF-8 handling corrected.\n\n"
        "Authorization freeze fingerprint --> "
        + manifest["authorization_freeze_fingerprint"]
        + "\n\nTrainer freeze fingerprint --> "
        + manifest["trainer_freeze_fingerprint"]
        + "\n\nTRAINING_AUTHORIZED --> **1**\nTRAINING_STARTED --> **0**\n",
        encoding="utf-8",
    )

    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(base.metrics(report).items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
