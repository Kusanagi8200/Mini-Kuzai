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

## Phase 03 current reference environment - 2026-10-25

The V58 architecture baseline was validated on the following local environment:

- Ubuntu 24.04.x
- Linux kernel 7.0.0-38-generic
- Python 3.12.3
- PyTorch 2.13.0+cu130
- CUDA 13.0
- NVIDIA driver 580.178.04
- NVIDIA GeForce RTX 5060 Laptop GPU
- 8151 MiB reported GPU memory
- compute capability 12.0
- BF16 supported
- system RAM 32 GB

The NVIDIA 580 open kernel module is installed for the active 7.0.0-38 kernel. CUDA availability and the V58 model smoke test were verified after the driver and kernel-module stack was realigned.

This environment is the current Phase 03 execution reference. The Phase 01 environment above remains historical.

