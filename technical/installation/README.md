# Installation

Mini-Kuzai Phase 01 was developed in a dedicated Python virtual environment on Ubuntu 24.04 with an NVIDIA CUDA GPU.

## Create the project environment

```bash
cd /root
mkdir -p Mini-Kuzai
cd Mini-Kuzai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## Install PyTorch for CUDA 13.0

```bash
pip install \
  torch==2.13.0+cu130 \
  --index-url https://download.pytorch.org/whl/cu130
```

## Install NumPy

```bash
pip install numpy==2.5.2
```

## Verify the GPU environment

```bash
python - <<'PY'
import torch

print('PyTorch :', torch.__version__)
print('CUDA    :', torch.version.cuda)
print('Available:', torch.cuda.is_available())

if torch.cuda.is_available():
    print('GPU     :', torch.cuda.get_device_name(0))
    x = torch.tensor([1.0], device='cuda')
    print('Tensor  :', x)
PY
```

## Phase 01 reference environment

- Ubuntu 24.04.x
- Python 3.12.3
- PyTorch 2.13.0+cu130
- CUDA 13.0
- NumPy 2.5.2
- NVIDIA GeForce RTX 5060 Laptop GPU

The model itself does not require a large GPU; the small architecture is intentionally designed for direct inspection and experimentation.
