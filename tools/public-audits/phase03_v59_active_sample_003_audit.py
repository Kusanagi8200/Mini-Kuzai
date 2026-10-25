#!/usr/bin/env python3
import importlib.util, sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/"tools"/"phase03_v59_active_sample_003_audit.py"

spec=importlib.util.spec_from_file_location("phase03_v59_active003_public",SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load active sample 003 audit")
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)

if __name__=="__main__":
    module.main()
