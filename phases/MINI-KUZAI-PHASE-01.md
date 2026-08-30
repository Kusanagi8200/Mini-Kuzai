# MINI-KUZAI PHASE 01

Phase 01 establishes the first complete Mini-Kuzai language-model laboratory.

## Scope

The phase starts with a simple word-level tokenizer and progressively builds the complete decoder-only Transformer used in the final checkpoint. The source archive preserved in this repository contains the full numbered sequence from `01_tokenizer.py` through `67_beta_additive_identity.py`.

## Main milestones

1. Tokenization and vocabulary creation.
2. Token embeddings.
3. Positional embeddings.
4. Q/K/V projections.
5. Attention-score computation.
6. Causal masking.
7. Context-vector construction.
8. Residual connections.
9. MLP integration.
10. First Transformer block.
11. Complete language-model head and logits.
12. Backpropagation and optimizer updates.
13. Autoregressive generation.
14. EOS support.
15. Sampling and temperature.
16. Parameter inspection.
17. Multi-head attention.
18. Multiple Transformer blocks.
19. Train/validation separation.
20. Early stopping.
21. Deterministic reproducibility.
22. Generalization tests.
23. Data expansion and clean train/validation/test methodology.
24. Batch dimension support.
25. Padding and attention masks.
26. DataLoader and dynamic batching.
27. Batched training.
28. Learning-rate search.
29. Frozen final checkpoint.
30. Blind generalization evaluation.
31. Attention-head ablations.
32. Attention-vs-MLP component ablations.
33. Residual-stream / logit tracing.
34. Logit-margin analysis.
35. Residual-update geometry.
36. Final LayerNorm decomposition.
37. Gamma / beta analysis.
38. Beta-to-vocabulary bias analysis.
39. Frequency-vs-beta regression.
40. Causal beta ablation and confirmation.
41. Prompt-independent beta logit identity.

## Final frozen model

```text
Checkpoint            : mini-kuzai-final.pt
Transformer blocks    : 2
Attention heads       : 2
Embedding dimension   : 8
MLP hidden dimension  : 32
Vocabulary            : 26
Parameters            : 2368
Batch size            : 4
Learning rate         : 0.04
Seed                  : 42
Best epoch            : 11
Validation loss       : 0.665633
```

## Preserved source snapshot

The recovered Phase 01 local directory contained:

```text
67 numbered experiment scripts
5 historical Mini-Kuzai model modules
1 corpus file
1 original project note
9 PyTorch checkpoints
```

The numbered scripts, corpus, original note, and historical model modules are preserved under `tests/phase-01/lab/`.

Clean reusable model implementations are stored under `mini_kuzai/`.

Checkpoint binaries remain outside normal Git and are documented by filename and SHA-256 under `technical/checkpoints/README.md`.

## Key result

Phase 01 demonstrates the full path from raw text to a trained autoregressive Transformer and then opens the model for direct inspection. The emphasis is on understanding mechanisms experimentally rather than treating the LLM as an opaque API.

## End of phase

**MINI-KUZAI PHASE 01 is frozen at experiment 67.**

The next planned experiment, gamma context dependence, belongs to the continuation after this frozen Phase 01 snapshot.
