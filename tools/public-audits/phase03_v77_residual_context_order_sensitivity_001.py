#!/usr/bin/env python3
"""V77 numeric GOGIT producer for frozen residual context-order sensitivity."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "v77_residual_context_order_sensitivity.py"
FROZEN_GIT_BLOB = "941df566949291c55da1b4c6b0b6c63ad52dbd37"


def main():
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("V77 frozen scientific source unavailable")
    digest = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if digest != FROZEN_GIT_BLOB:
        raise RuntimeError("V77 frozen scientific source fingerprint mismatch")
    spec = importlib.util.spec_from_file_location("v77_shared_control", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V77 source import failure")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.main()
    except (RuntimeError, ValueError, OSError) as exc:
        message = str(exc).lower()
        if "start receipt" in message:
            code = 1
        elif "dependency blob" in message or "report integrity" in message:
            code = 2
        elif "prefix" in message or "perturbation" in message:
            code = 3
        elif "residual" in message or "replay" in message:
            code = 4
        elif "alpha" in message or "correlation" in message:
            code = 5
        elif "paired" in message or "histogram" in message:
            code = 6
        elif "validation lexical" in message:
            code = 7
        elif "gpu peak-memory" in message:
            code = 8
        elif "cuda" in message or "bf16" in message:
            code = 9
        else:
            code = 99
        print(f"V77_SAFE_FAILURE_CODE: {code}")
        sys.exit(77)


if __name__ == "__main__":
    main()
