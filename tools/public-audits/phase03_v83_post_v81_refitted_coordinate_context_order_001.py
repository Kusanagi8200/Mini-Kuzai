#!/usr/bin/env python3
"""V83 numeric GOGIT producer for post-V81 refitted-coordinate control."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools/v83_post_v81_refitted_coordinate_context_order.py"
FROZEN_GIT_BLOB = "0ee59a66f20aef72536495e47f4d1176ce5ec4a8"


def main():
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("V83 frozen scientific source unavailable")
    digest = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if digest != FROZEN_GIT_BLOB:
        raise RuntimeError("V83 frozen scientific source fingerprint mismatch")

    spec = importlib.util.spec_from_file_location("v83_shared_control", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V83 source import failure")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        module.main()
    except (RuntimeError, ValueError, OSError) as exc:
        message = str(exc).lower()
        if "start receipt" in message:
            code = 1
        elif "v82" in message and ("report" in message or "replay" in message):
            code = 2
        elif "checkpoint" in message or "fingerprint" in message:
            code = 3
        elif "train" in message and ("inventory" in message or "geometry" in message):
            code = 4
        elif "refit" in message or "cosine" in message or "coordinate" in message:
            code = 5
        elif "coverage" in message or "input invariant" in message:
            code = 6
        elif "boundary" in message or "threshold" in message:
            code = 7
        elif "gpu peak-memory" in message:
            code = 8
        elif "cuda" in message or "bf16" in message:
            code = 9
        else:
            code = 99
        print(f"V83_SAFE_FAILURE_CODE: {code}")
        sys.exit(83)


if __name__ == "__main__":
    main()
