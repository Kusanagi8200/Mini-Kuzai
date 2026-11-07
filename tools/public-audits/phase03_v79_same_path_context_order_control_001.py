#!/usr/bin/env python3
"""V79 numeric GOGIT producer for same-path context-order control."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "v79_same_path_context_order_control.py"
FROZEN_GIT_BLOB = "93eb80c115ce1989e3ca077accd98850667e158f"


def main():
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("V79 frozen scientific source unavailable")
    digest = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if digest != FROZEN_GIT_BLOB:
        raise RuntimeError("V79 frozen scientific source fingerprint mismatch")

    spec = importlib.util.spec_from_file_location("v79_shared_control", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V79 source import failure")
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
        elif "prefix" in message or "input invariant" in message:
            code = 3
        elif "residual" in message or "replay" in message:
            code = 4
        elif "alpha" in message or "correlation" in message:
            code = 5
        elif "paired" in message or "coverage" in message:
            code = 6
        elif "gpu peak-memory" in message:
            code = 8
        elif "cuda" in message or "bf16" in message:
            code = 9
        else:
            code = 99
        print(f"V79_SAFE_FAILURE_CODE: {code}")
        sys.exit(79)


if __name__ == "__main__":
    main()
