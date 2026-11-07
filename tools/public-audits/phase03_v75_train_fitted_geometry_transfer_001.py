#!/usr/bin/env python3
"""V75 numeric GOGIT producer for frozen TRAIN-fitted geometry transfer."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "v75_train_fitted_geometry_transfer.py"
FROZEN_GIT_BLOB = "8705d8ca9aebe7281779c704119d26eb82517da2"


def main():
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("V75 frozen scientific source unavailable")
    digest = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if digest != FROZEN_GIT_BLOB:
        raise RuntimeError("V75 frozen scientific source fingerprint mismatch")
    spec = importlib.util.spec_from_file_location("v75_shared_geometry", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V75 source import failure")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.main()
    except (RuntimeError, ValueError, OSError) as exc:
        message = str(exc).lower()
        if "start receipt" in message:
            code = 1
        elif "prerequisite" in message or "report/fingerprint" in message:
            code = 2
        elif "train lexical" in message or "train token" in message or "train stream" in message:
            code = 3
        elif "geometry" in message or "covariance" in message or "eigen" in message or "spectral" in message:
            code = 4
        elif "validation lexical" in message or "prediction histogram" in message:
            code = 5
        elif "replay" in message or "v73/v74" in message:
            code = 6
        elif "gpu peak-memory" in message:
            code = 7
        elif "cuda" in message or "bf16" in message:
            code = 8
        else:
            code = 99
        print(f"V75_SAFE_FAILURE_CODE: {code}")
        sys.exit(75)


if __name__ == "__main__":
    main()
