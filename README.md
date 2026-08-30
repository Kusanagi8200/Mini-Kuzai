# Mini-Kuzai

**Build a language model from scratch, train it locally, and inspect what happens inside a Transformer.**

Mini-Kuzai is an educational and experimental project focused on constructing a small autoregressive language model without starting from a pretrained model. The objective is not to build a production chatbot, but to understand the mechanics of a modern LLM by implementing, training, testing, and inspecting each component directly.

The project is developed locally with Python and PyTorch on an NVIDIA GPU. Every major mechanism is introduced as working code, measured experimentally, and then integrated into the complete model.

## Project goals

Mini-Kuzai is designed to explore the complete path from raw text to next-token prediction:

- word-level tokenization and vocabulary construction
- token embeddings
- positional embeddings
- query, key, and value projections
- causal self-attention
- multi-head attention
- residual connections
- feed-forward / MLP layers
- LayerNorm
- stacked Transformer blocks
- language-model head and logits
- cross-entropy loss
- backpropagation and optimizer updates
- autoregressive generation and EOS handling
- sampling and temperature
- train / validation / test separation
- overfitting and early stopping
- deterministic training and reproducibility
- compositional generalization
- batching, dynamic padding, and attention masks
- internal analysis through attention inspection, ablations, residual-stream tracing, logit margins, and LayerNorm decomposition

## Current model

The Phase 01 final checkpoint was trained with the following compact architecture:

| Component | Value |
| --- | --- |
| Transformer blocks | 2 |
| Attention heads | 2 |
| Embedding dimension | 8 |
| MLP hidden dimension | 32 |
| Vocabulary | 26 tokens |
| Parameters | 2,368 |
| Batch size | 4 |
| Optimizer | AdamW |
| Learning rate | 0.04 |
| Training device | NVIDIA CUDA GPU |

The model is intentionally tiny. Its purpose is to make every matrix, vector, gradient, attention head, and prediction small enough to inspect directly.

## Repository structure

```text
Mini-Kuzai/
├── README.md
├── requirements.txt
├── .gitignore
│
├── technical/
│   ├── installation/
│   ├── commands/
│   ├── training-process/
│   └── architecture-notes/
│
├── tests/
│   └── phase-01/
│       ├── tokenizer/
│       ├── embeddings/
│       ├── attention/
│       ├── training/
│       ├── batching/
│       ├── generalization/
│       └── interpretability/
│
├── mini_kuzai/
│   └── mini_kuzai_padding.py
│
└── phases/
    └── MINI-KUZAI-PHASE-01.md
```

## MINI-KUZAI PHASE 01

Phase 01 covers the construction of the model from the first tokenizer experiment through a complete batched Transformer and a detailed analysis of its internal behavior.

The phase includes experiments on:

- model depth and multi-head attention
- validation leakage and clean test methodology
- early stopping
- reproducibility
- generalization beyond exact training prefixes
- batched training with dynamic padding
- learning-rate search
- blind evaluation
- attention-head ablation
- Transformer-component ablation
- residual-stream / logit tracing
- LayerNorm gamma and beta analysis
- vocabulary bias induced by the final LayerNorm beta vector

The frozen Phase 01 checkpoint is named `mini-kuzai-final.pt`. Model checkpoints are intentionally excluded from Git by default because they are generated artifacts.

## Philosophy

The project follows a practical approach: implement one mechanism, run it, inspect the tensors and outputs, verify the behavior, then move to the next mechanism. Theory is introduced when it becomes necessary to explain an observed result.

Mini-Kuzai is therefore both a small language model and a laboratory for understanding how language models actually work under the hood.

## Status

**MINI-KUZAI PHASE 01: complete.**

The model architecture and Phase 01 checkpoint are frozen. Future phases can extend the tokenizer, dataset, model capacity, training pipeline, evaluation methodology, GPU profiling, and inference performance while preserving Phase 01 as a reproducible baseline.
