# Mini-Kuzai Model Code

This directory contains the model implementation itself, separate from installation notes and experimental scripts.

`mini_kuzai_padding.py` implements the Phase 01 final architecture:

- token embeddings
- learned positional embeddings
- pre-LayerNorm Transformer blocks
- causal multi-head self-attention
- padding-key attention masks
- residual connections
- GELU MLP
- final LayerNorm
- bias-free LM head

The final Phase 01 configuration uses two Transformer blocks, two attention heads, an embedding dimension of 8, and an MLP hidden dimension of 32.

Historical intermediate implementations from the learning process can be kept in the test/experiment history. This directory is intended to hold the clean model implementation used as the project baseline.
