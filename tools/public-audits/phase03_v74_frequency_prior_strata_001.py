#!/usr/bin/env python3
"""V74 STRATA numeric GOGIT - frozen read-only TRAIN/VALIDATION study."""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "v74_frequency_prior.py"
FROZEN_GIT_BLOB = "a1bbbb103500b5381c7518be88900ab3ddac6a18"


def main():
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("V74 frozen scientific source unavailable")
    digest = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--", str(SOURCE)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if digest != FROZEN_GIT_BLOB:
        raise RuntimeError("V74 frozen scientific source fingerprint mismatch")
    spec = importlib.util.spec_from_file_location("v74_shared_strata", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V74 source import failure")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main("STRATA")


if __name__ == "__main__":
    main()
