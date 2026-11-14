#!/usr/bin/env python3
"""V82 numeric GOGIT producer for post-continuation context-order replication."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "v82_post_continuation_context_order_replication.py"
FROZEN_GIT_BLOB = "1e0d95235d23c0e7c3a56c3ee99257dc81c6f5f8"


def main():
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("V82 frozen scientific source unavailable")
    digest = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if digest != FROZEN_GIT_BLOB:
        raise RuntimeError("V82 frozen scientific source fingerprint mismatch")

    spec = importlib.util.spec_from_file_location("v82_shared_control", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V82 source import failure")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        module.main()
    except (RuntimeError, ValueError, OSError) as exc:
        message = str(exc).lower()
        if "start receipt" in message:
            code = 1
        elif "v81 closure" in message:
            code = 2
        elif "checkpoint" in message or "fingerprint" in message:
            code = 3
        elif "baseline replay" in message:
            code = 4
        elif "boundary" in message or "threshold" in message:
            code = 5
        elif "coverage" in message or "input invariant" in message:
            code = 6
        elif "gpu peak-memory" in message:
            code = 8
        elif "cuda" in message or "bf16" in message:
            code = 9
        else:
            code = 99
        print(f"V82_SAFE_FAILURE_CODE: {code}")
        sys.exit(82)


if __name__ == "__main__":
    main()
