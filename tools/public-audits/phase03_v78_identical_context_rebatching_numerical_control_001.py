#!/usr/bin/env python3
"""V78 numeric GOGIT producer for identical-context rebatching control."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "v78_identical_context_rebatching_numerical_control.py"
FROZEN_GIT_BLOB = "4aa901d9a27d03e48e8099fb21799aa8e7cead9e"


def main():
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("V78 frozen scientific source unavailable")
    digest = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if digest != FROZEN_GIT_BLOB:
        raise RuntimeError("V78 frozen scientific source fingerprint mismatch")

    spec = importlib.util.spec_from_file_location("v78_shared_control", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V78 source import failure")
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
        elif "prefix" in message or "input" in message:
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
        print(f"V78_SAFE_FAILURE_CODE: {code}")
        sys.exit(78)


if __name__ == "__main__":
    main()
