#!/usr/bin/env python3
"""V75 numeric GOGIT producer for frozen TRAIN-fitted geometry transfer."""
from __future__ import annotations

import importlib.util
import subprocess
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
    module.main()


if __name__ == "__main__":
    main()
