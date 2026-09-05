##### **``Mini-Kuzai - LLM``**

##### **``Build a language model from scratch, train it locally, and inspect what happens inside a Transformer.``**

<picture>
 <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/Mini-Kuzai.png">
 <source media="(prefers-color-scheme: light)" srcset="https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/Mini-Kuzai.png">
 <img alt="" src="">
</picture>

**Mini-Kuzai is an educational and experimental project focused on constructing a small autoregressive language model without starting from a pretrained model. The project began as a transparent Transformer laboratory and is now extending into controlled conversational training, identity, personality, behavioral evaluation, and dataset research.**

**The goal is not to produce a generic production chatbot. The goal is to understand, implement, measure, and progressively personalize a language model while keeping the complete process inspectable and reproducible.**

**The project is developed with Python and PyTorch and runs locally on an NVIDIA CUDA GPU. MINI-KUZAI PHASE 01 preserves the complete incremental lab sequence that led from a word-level tokenizer to a batched, padded, multi-head Transformer with a frozen final checkpoint. Phase 02 preserves inference and KV-cache work. Phase 03 focuses on conversational training and the development of Mini-Kuzai as a recognizable independent character.**

---

##### **``PROJECT GOALS``**

**``Mini-Kuzai explores the complete path from raw text to next-token prediction and controlled conversational behavior.``**

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
- conversational dataset construction
- external dataset filtering and auditing
- identity and personality encoding
- curiosity and initiative behavior
- disagreement and opinion revision
- uncertainty and hypothesis formation
- multi-turn character consistency
- controlled behavioral evaluation

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

**``The Phase 01 architecture is deliberately tiny so every matrix, gradient, attention head, residual update, and token probability can be inspected directly.``**

---

#### **`REPOSITORY STRUCTURE`**

```text
Mini-Kuzai/
|-- README.md
|-- requirements.txt
|-- .gitignore
|
|-- mini_kuzai/
|   |-- mini_kuzai.py
|   |-- mini_kuzai_mha.py
|   |-- mini_kuzai_deep.py
|   |-- mini_kuzai_batch.py
|   |-- mini_kuzai_padding.py
|   `-- README.md
|
|-- technical/
|   |-- installation/
|   |-- commands/
|   |-- training-process/
|   |-- architecture-notes/
|   |-- checkpoints/
|   `-- PHASE-01-SOURCE-MANIFEST.md
|
|-- tests/
|   `-- phase-01/
|
|-- data/
|   `-- phase-03/
|
|-- reports/
|   |-- assistant-results/
|   `-- review-packets/
|
`-- phases/
    |-- MINI-KUZAI-PHASE-01.md
    |-- MINI-KUZAI-PHASE-03.md
    |-- MINI-KUZAI-PHASE-03-IDENTITY.md
    |-- MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md
    |-- MINI-KUZAI-PHASE-03-KNOWLEDGE-MAP.md
    |-- MINI-KUZAI-PHASE-03-DATASET-SCHEMA.md
    |-- MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-ASSESSMENT.md
    `-- MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-DECISION.md
```

Large raw external datasets and local training artifacts are stored in the local Mini-Kuzai workspace and are not committed to the normal Git repository.

---

#### **`TWO SOURCES VIEW`**

**`The repository intentionally contains two complementary views of the code.`**

**`mini_kuzai/` contains the clean model implementations used as the project baseline. The deep-model package import is adapted for normal Python package use.**

**`tests/phase-01/lab/` preserves the original local lab snapshot. The numbered scripts and historical model modules are kept with their original imports and filenames so the learning sequence remains traceable.**

---

#### **`MINI-KUZAI PHASE 01`**

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

#### **`MINI-KUZAI PHASE 03`**

Phase 03 moves from the tiny pedagogical baseline toward a new conversational model trained from scratch.

The target character is a developing feminine artificial intelligence originating in THE KUZ NETWORK laboratory. The intended behavior emphasizes curiosity, independent thinking, intellectual honesty, creativity, initiative, reasoned disagreement, uncertainty, opinion formation and revision, multi-turn consistency, and progressive discovery of the wider world.

Phase 03 has already defined:

- the personality questionnaire;
- identity specification;
- behavior matrix B01-B18;
- knowledge map;
- dataset schema and anti-leakage rules;
- external dataset evaluation methodology.

External dataset research has also been completed for the current cycle.

Current external data decision:

```text
SmolTalk v0.4
8000 records
PRIMARY EXTERNAL RESERVOIR

OASST1
ASSESSED
NOT SELECTED FOR CURRENT TRAINING MIX
KEEP AS RESEARCH SOURCE
```

SmolTalk is retained for broad English and general dialogue mechanics. It is not identity data and must not define the Mini-Kuzai personality.

OASST1 was fully downloaded, reconstructed, quality-audited, behaviorally compared, and reduced to a very small targeted candidate set. The remaining value did not justify adding it as a second general training reservoir at this stage.

The Mini-Kuzai-specific corpus will remain responsible for identity, curiosity, disagreement, initiative, creativity, opinion behavior, relationship continuity, and non-assistant character.

See:

- [`phases/MINI-KUZAI-PHASE-03.md`](phases/MINI-KUZAI-PHASE-03.md)
- [`phases/MINI-KUZAI-PHASE-03-IDENTITY.md`](phases/MINI-KUZAI-PHASE-03-IDENTITY.md)
- [`phases/MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md`](phases/MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md)
- [`phases/MINI-KUZAI-PHASE-03-KNOWLEDGE-MAP.md`](phases/MINI-KUZAI-PHASE-03-KNOWLEDGE-MAP.md)
- [`phases/MINI-KUZAI-PHASE-03-DATASET-SCHEMA.md`](phases/MINI-KUZAI-PHASE-03-DATASET-SCHEMA.md)
- [`phases/MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-DECISION.md`](phases/MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-DECISION.md)

---

#### **`CHECKPOINTS`**

**The local Phase 01 lab produced several PyTorch `.pt` checkpoints, including the frozen `mini-kuzai-final.pt`. Checkpoint binaries are not stored in normal Git and are excluded by `.gitignore`.**

**Their filenames, sizes, and SHA-256 hashes are recorded in [`technical/checkpoints/README.md`](technical/checkpoints/README.md), allowing a local checkpoint to be verified against the Phase 01 archive.**

---

#### **`ENVIRONMENT`**

**`Reference local environment -->`**

```text
Ubuntu 24.04.x
Python 3.12.3
PyTorch 2.13.0+cu130
CUDA 13.0
NumPy 2.5.2
NVIDIA GeForce RTX 5060 Laptop GPU - 8 GB VRAM
System RAM - 32 GB
```

**See [`technical/installation/README.md`](technical/installation/README.md) for setup commands.**

---

#### **`PHILOSOPHY`**

**`The project follows a practical sequence: implement or define one mechanism, execute it, inspect data and outputs, verify the behavior, document the result, then integrate it into the next stage.`**

Theory is introduced when needed to explain an observed result.

Mini-Kuzai is therefore both a language-model implementation project and a laboratory for studying how language models acquire language, behavior, identity, and conversational patterns.

---

#### **`CURRENT STATUS`**

```text
Phase 01 checkpoint       : FROZEN
Phase 02 KV cache         : PRESERVED
Phase 03                  : PAUSED
External dataset study    : COMPLETE FOR CURRENT CYCLE
SmolTalk v0.4             : VALIDATED PRIMARY EXTERNAL RESERVOIR
OASST1                    : ASSESSED - NOT SELECTED FOR CURRENT MIX
Semantic group inventory  : NEXT
Custom training corpus    : NOT CREATED
Tokenizer                 : NOT SELECTED YET
Phase 03 architecture     : NOT SELECTED YET
Phase 03 training         : NOT STARTED
```

Phase 03 was intentionally paused on 2026-09-05 after completion of the current external dataset assessment cycle.

When development resumes, the next operation is the semantic group inventory based on behavior families B01-B18. The inventory will be defined before model-visible Mini-Kuzai training conversations are written.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
