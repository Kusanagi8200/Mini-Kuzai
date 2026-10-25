#!/usr/bin/env python3
"""Public wrapper for V59 final candidate-mix audit."""

import importlib.util
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "tools" / "phase03_v59_final_candidate_mix.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module(
    "phase03_v59_final_candidate_mix_public",
    SOURCE,
)

if __name__ == "__main__":
    MODULE.main()
