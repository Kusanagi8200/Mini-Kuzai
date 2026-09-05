# Phase 01 Tests and Experiments

This directory groups the executable experiments used during MINI-KUZAI PHASE 01.

The original learning sequence was intentionally incremental: each script isolates one mechanism or diagnostic before that mechanism is integrated into the full model.

## Categories

- `tokenizer/` - vocabulary construction and encode/decode experiments
- `embeddings/` - token and positional embedding experiments
- `attention/` - Q/K/V, causal masking, context vectors, and multi-head attention
- `training/` - loss, backpropagation, EOS, early stopping, reproducibility, and learning-rate experiments
- `batching/` - batch dimensions, padding, masks, DataLoader, and batched training
- `generalization/` - clean validation, train/validation/test separation, blind and compositional generalization
- `interpretability/` - attention inspection, ablations, residual tracing, logit margins, LayerNorm, gamma, and beta analysis

## Phase 01 script lineage

The local lab produced scripts from `01_tokenizer.py` through the later interpretability experiments. The repository structure separates those scripts by purpose rather than keeping every file in one flat directory.

The exact frozen model checkpoint is not committed. Reproducible source, configuration, and test code are the primary repository artifacts.
