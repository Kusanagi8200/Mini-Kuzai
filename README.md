##### **``Mini-Kuzai - LLM``**

##### **``Build a language model from scratch, train it locally, and inspect what happens inside a Transformer.``**

<picture>
 <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/Mini-Kuzai.png">
 <source media="(prefers-color-scheme: light)" srcset="https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/Mini-Kuzai.png">
 <img alt="" src="">
</picture> 

**Mini-Kuzai is an educational and experimental project focused on constructing a small autoregressive language model without starting from a pretrained model. The goal is not to produce a production chatbot. The goal is to implement the mechanisms of a modern decoder-only Transformer directly, train the resulting model, measure it, and inspect the learned behavior layer by layer.**

**The project is developed with Python and PyTorch and was trained locally on an NVIDIA CUDA GPU. MINI-KUZAI PHASE 01 preserves the complete incremental lab sequence that led from a word-level tokenizer to a batched, padded, multi-head Transformer with a frozen final checkpoint.**

--- 

##### **``PROJECT GOALS``**

**``Mini-Kuzai explores the complete path from raw text to next-token prediction -->``**

- word-level tokenization and vocabulary construction
- token embeddings
- positional embeddings
- query, key, and value projections
- causal self-attention
- context vectors
- residual connections
- feed-forward / MLP layers
- LayerNorm
- Transformer blocks
- language-model head and logits
- cross-entropy loss
- backpropagation and optimizer updates
- autoregressive generation and EOS handling
- sampling and temperature
- multi-head attention
- model depth
- train / validation / test separation
- overfitting and early stopping
- deterministic training and reproducibility
- compositional generalization
- batch dimensions
- dynamic padding and attention masks
- DataLoader-based training
- learning-rate search
- attention-head and component ablations
- residual-stream tracing
- logit-margin analysis
- LayerNorm gamma / beta analysis

---

##### **``PHASE 01 FINAL MODEL``**

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
| Seed | 42 |
| Best epoch | 11 |
| Best validation loss | 0.665633 |

**``The architecture is deliberately tiny so every matrix, gradient, attention head, residual update, and token probability can be inspected directly.``**

---

#### **`REPOSITORY STRUCTURE`**

```text
Mini-Kuzai/
├── README.md
├── requirements.txt
├── .gitignore
│
├── mini_kuzai/
│   ├── mini_kuzai.py
│   ├── mini_kuzai_mha.py
│   ├── mini_kuzai_deep.py
│   ├── mini_kuzai_batch.py
│   ├── mini_kuzai_padding.py
│   └── README.md
│
├── technical/
│   ├── installation/
│   ├── commands/
│   ├── training-process/
│   ├── architecture-notes/
│   ├── checkpoints/
│   └── PHASE-01-SOURCE-MANIFEST.md
│
├── tests/
│   └── phase-01/
│       ├── lab/
│       │   ├── 01_tokenizer.py
│       │   ├── ...
│       │   ├── 67_beta_additive_identity.py
│       │   ├── corpus.txt
│       │   └── historical model modules
│       ├── tokenizer/
│       ├── embeddings/
│       ├── attention/
│       ├── training/
│       ├── batching/
│       ├── generalization/
│       └── interpretability/
│
└── phases/
    └── MINI-KUZAI-PHASE-01.md
```

---

####  **`TWO SOURCES VIEW`**

 **`The repository intentionally contains two complementary views of the code.`**

**`mini_kuzai/` contains the clean model implementations used as the project baseline. The deep-model package import is adapted for normal Python package use.**

**`tests/phase-01/lab/` preserves the original local lab snapshot. The numbered scripts and historical model modules are kept with their original imports and filenames so the learning sequence remains traceable.**

---

####  **`MINI-KUZAI PHASE 01`**

**Phase 01 contains 67 numbered Python experiments, beginning with `01_tokenizer.py` and ending with `67_beta_additive_identity.py`.**

 **`Major stages include -->`** 

1. tokenizer, embeddings and positions;
2. Q/K/V and causal self-attention;
3. context, residuals, MLP and first Transformer block;
4. complete model, training and generation;
5. EOS, sampling, temperature and parameter inspection;
6. multi-head attention and model depth;
7. validation methodology, early stopping and deterministic reproducibility;
8. compositional generalization and clean train/validation/test separation;
9. batching, dynamic padding, DataLoader and batched training;
10. learning-rate search and frozen final training;
11. independent and blind evaluation;
12. attention/head/component ablation;
13. residual-stream and logit tracing;
14. LayerNorm decomposition and gamma/beta analysis;
15. beta vocabulary bias, target-frequency analysis, regression and additive logit identity.

**See [`phases/MINI-KUZAI-PHASE-01.md`](phases/MINI-KUZAI-PHASE-01.md) for the phase summary and [`technical/PHASE-01-SOURCE-MANIFEST.md`](technical/PHASE-01-SOURCE-MANIFEST.md) for the imported source inventory.**

---

####  **`CHECKPOINTS`**

**The local Phase 01 lab produced several PyTorch `.pt` checkpoints, including the frozen `mini-kuzai-final.pt`. Checkpoint binaries are not stored in normal Git and are excluded by `.gitignore`.**

**Their filenames, sizes, and SHA-256 hashes are recorded in [`technical/checkpoints/README.md`](technical/checkpoints/README.md), allowing a local checkpoint to be verified against the Phase 01 archive.**

---

#### **`ENVIRONMENT`**

**`Phase 01 reference environment -->`**

```text
Ubuntu 24.04.x
Python 3.12.3
PyTorch 2.13.0+cu130
CUDA 13.0
NumPy 2.5.2
NVIDIA GeForce RTX 5060 Laptop GPU
```

**See [`technical/installation/README.md`](technical/installation/README.md) for setup commands.**

---

#### **`PHILOSOPHY`**

**`The project follows a practical sequence: implement one mechanism, execute it, inspect tensors and outputs, verify the behavior, then integrate it into the next stage. Theory is introduced when needed to explain an observed result.``**

Mini-Kuzai is therefore both a tiny language model and a laboratory for understanding how language models work under the hood.

---

#### **`STATUS`**

**`MINI-KUZAI PHASE 01 --> Complete and source-frozen.`**

The source archive imported into this repository preserves the Phase 01 baseline. Future work can extend tokenizer design, dataset scale, model capacity, training methodology, GPU profiling, and inference performance without rewriting the Phase 01 history.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**

