#!/usr/bin/env python3
"""Public numeric V59 turn-aware segmentation audit."""

import importlib.util
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

SOURCE = (
    REPO
    / "tools"
    / "phase03_v59_segmentation_audit.py"
)

MARKER = (
    "##### SECTION RESULTS FOR ASSISTANT ######"
)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load {path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


MODULE = load_module(
    "phase03_v59_segmentation_public",
    SOURCE,
)


if __name__ == "__main__":
    metrics = MODULE.collect_metrics()

    print(MARKER)

    for key in sorted(metrics):
        print(
            f"{key}: {metrics[key]}"
        )
