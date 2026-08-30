# Commands

This directory documents the shell commands used to create, run, test, and inspect Mini-Kuzai.

## Activate the environment

```bash
cd /root/Mini-Kuzai
source .venv/bin/activate
```

## Run a Python experiment

```bash
python <script>.py
```

## Deterministic CUDA experiments

Several Phase 01 experiments used deterministic execution:

```python
import os
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'

import random
import numpy as np
import torch

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

torch.use_deterministic_algorithms(True)
```

## Check GPU usage

```bash
nvidia-smi
```

## Important project rule

Phase 01 experiments were executed incrementally. A model or test was validated before moving to the next mechanism. Checkpoints and generated artifacts are excluded from Git by default.
