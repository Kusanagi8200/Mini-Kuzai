#!/usr/bin/env python3
"""V66 numeric GOGIT Part B, exactly 30 metrics, no training or BLIND."""
from __future__ import annotations
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
from tools.phase03_v66_metric_partition import publish_part


if __name__=="__main__":
    publish_part("B")
