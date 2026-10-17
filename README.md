#### **`Mini-Kuzai - LLM`**

#### **`BUILD A LANGUAGE MODEL FROM SCRATCH, TRAIN IT LOCALLY AND INSPECT WHAT HAPPENS INSIDE A TRANSFORMER.`**

------------------------------------------------------------------------

<picture>
 <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/Mini-Kuzai-Project.png">
 <source media="(prefers-color-scheme: light)" srcset="https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/Mini-Kuzai-Project.png">
 <img alt="" src="">
</picture>

---
##### **``PROJECT CONCEPT``**
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
    |-- MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-DECISION.md
    `-- MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md
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
- external dataset evaluation methodology;
- semantic group inventory v0.3 with 65 groups;
- TRAIN / VALIDATION / BLIND TEST split allocation;
- conversation authoring policy v0.2;
- semantic split exclusion map and manual anti-leakage review.

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

### External SmolTalk curation - status 2026-10-17 (V53 corpus consolidation active)

The public SmolTalk v0.4 reservoir contains 8,000 candidate records, but is not an approved training dataset. V44 produced a provisional stratified selection of 1,139 conversations (679 multi-turn, 460 single-turn). A keyword-based creative category reached 69 of its 130 target records. V46 found broader creative signals and produced a 68-record **local review queue**; neither these signals nor the queue are validated training examples.

V47 verified the integrity of all 68 local review records against their public SmolTalk sources. V48/V49 subsequently reviewed those 68 public-source cases on GitHub (36 priority and 32 baseline); historical local review tools remain available but are not the active completion status. The V44 pool is unchanged and final mixture ratios remain undecided.

Public aggregate results are transmitted using the reviewed [gogit workflow](tools/GOGIT.md): the local script publishes only allowlisted numerical SmolTalk metrics to `reports/assistant-results/`, and the user then requests retrieval with `gogit`. This mechanism does not run in the background and must never be used for private conversation data or private-derived results.

**GitHub-native SmolTalk reviews:** All 68 public external case files were reviewed in V48 and the 14 HOLD cases were resolved in V49. Current results: 24 RETAIN, 44 REJECT and 0 HOLD. See the [V49 results](reviews/smoltalk-v48/V49-HOLD-RESOLUTION.md), [historical V48 report](reviews/smoltalk-v48/V48-REVIEW-RESULTS.md) and [GitHub review guide](tools/V48-GITHUB-REVIEW.md). No private ChatGPT-source material is included.

**V50 - revised training-data direction:** Mini-Kuzai now prioritizes cognitive exploration, multi-turn understanding, imagination, character development, creative writing, nuanced dialogue, correction after feedback and contextual expression. Specialized IT and programming proficiency is secondary. An imperfect conversational example is not automatically excluded for a technical fault, but an incorrect answer cannot be promoted as a correct supervised target. V48/V49 verdicts are historical quality assessments, not permanent bans on behavioral analysis.

V50 has completed a **local-only heuristic screening of all 1,139 provisional V44 public SmolTalk candidates**: 200 HIGH, 431 MEDIUM and 508 LOW. These are selection hints, not semantic or quality verdicts. See the [V50 cognitive/creative policy](phases/MINI-KUZAI-PHASE-03-V50-COGNITIVE-CREATIVE-PRIORITY.md), [public numeric report](reports/assistant-results/history/PHASE03-SMOLTALK-V50-COGNITIVE-SCREEN-001.json) and [eight-case methodology pilot](reviews/smoltalk-v50/PILOT-001.md). The full queue remains on fhc2; V44, tokenizer and TRAIN allocation are unchanged.

**V51 - first semantic review completed:** 24 new public SmolTalk conversations were evaluated on GitHub: 9 A, 8 B, 7 C, 0 HOLD. These include 12 HIGH, 6 MEDIUM and 6 LOW V50 hint examples. The results demonstrate both underestimated creative/contextual examples in MEDIUM/LOW and an invalid HIGH example. See the [V51 qualitative results](reviews/smoltalk-v51/RESULTS-001.md), [24 reviewed cases](reviews/smoltalk-v51/README.md) and [V51 methodology](phases/MINI-KUZAI-PHASE-03-V51-SEMANTIC-REVIEW.md). Only public external SmolTalk cases were reviewed. The [V51 numeric GOGIT audit](reports/assistant-results/history/PHASE03-SMOLTALK-V51-PILOT-REVIEW-001.json) was published and verified.

**V52 - 32-case semantic review annotated:** The [source-verified V52 inventory](reports/assistant-results/history/PHASE03-SMOLTALK-V52-INVENTORY-001.json) identified 1,071 candidates still available in the provisional V44 selection before the V52 batch (after excluding 44 V48 in-V44 examples and 24 V51 examples). A further 32 distinct public-external cases were published (8 HIGH, 12 MEDIUM and 12 LOW; 20 multi-turn) and all 32 were subsequently annotated on GitHub: **8 A, 12 B, 12 C, 0 HOLD**. See the [V52 qualitative summary](reviews/smoltalk-v52/RESULTS-001.md), [case index](reviews/smoltalk-v52/README.md) and [V52 workflow](tools/V52-GITHUB-REVIEW.md). The [historical V52 GOGIT progress snapshot](reports/assistant-results/history/PHASE03-SMOLTALK-V52-REVIEW-PROGRESS-001.json) recorded 8/32 before the remaining annotations. The [final V52 GOGIT audit](reports/assistant-results/history/PHASE03-SMOLTALK-V52-REVIEW-FINAL-001.json) was published and verified on 2026-10-17 at commit [`8a28e956`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/8a28e95637377f29d7204f51d49a174f2518929f): **32/32 reviewed, 8 A, 12 B, 12 C, 0 HOLD, 0 PENDING, 0 TRAIN approved**. Historical reports must not be rewritten.

The V52 pause checkpoint is now historical. V53 resumed public-only corpus consolidation while preserving all earlier review reports. Across V48/V49, V51 and V52, 124 distinct public SmolTalk examples remain the reviewed source population; V53 adds independent repair, derivative, eligibility and admission gates rather than redefining those historical grades. No tokenizer vocabulary has been frozen and no Phase 03 model training has started or been authorized.

**V53 - public corpus consolidation and controlled TRAIN expansion:** The [V53 workstream](phases/MINI-KUZAI-PHASE-03-V53-CORPUS-CONSOLIDATION.md) has progressed from cross-cycle accounting through repair planning, derivative review, eligibility, admission and behavior-by-behavior TRAIN completion. The last published GoGit state contains **104 unique canonical TRAIN records across 28 of 29 TRAIN semantic groups**. B14 EMOTIONAL EXPRESSION has now been authored and reviewed at the three-record MEDIUM target; one target wording was corrected during semantic review. The prepared corpus therefore contains **107 unique records across all 29 TRAIN groups**, pending the final B14 GoGit audit. Provenance after a successful audit would be **105 `phase03-designed` records plus 2 admitted public SmolTalk derivatives**. No VALIDATION or BLIND TEST conversation text has been created. Model training remains unauthorized.

### Private local corpus pipeline

Phase 03 includes a local-only pipeline for evaluating private conversational corpora as possible future training material.

A personal ChatGPT export is used locally as one private source for building conversation-specific data. Its purpose is to capture real multi-turn interaction patterns such as troubleshooting, correction after feedback, explanation, reasoning, planning, technical dialogue, and general conversation. The export is never treated as ready-to-train data.

The public repository contains only the generic processing methodology. No source conversation, source-derived excerpt, source-specific statistic, candidate queue, review output, or other information originating from private discussions is committed.

The local pipeline covers conversation reconstruction, topic segmentation, failed-step curation, factual validation, semantic mapping, duplicate control, language-policy decisions, and TRAIN / VALIDATION / BLIND anti-leakage checks.

Multi-turn examples preserve the order and provenance of observed user feedback. Rewritten assistant targets are explicitly distinguished from original responses; partial success is never promoted to unobserved verification. Editorial acceptance into a local candidate pool is not official TRAIN integration or training approval.

Before choosing a final mixture, the project measures dialogue length, multi-turn coverage, and behavioral balance across the private source, the controlled identity corpus, and the external English reservoir. Exact model token counts and mixture weights remain pending tokenizer selection.

The private conversation source is intended to complement the controlled Mini-Kuzai identity/behavior corpus and the general English reservoir. Private corpus work does not authorize training and does not modify the existing controlled Phase 03 dataset until explicit integration approval.

See [`phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md`](phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md) for the public methodology.
See:

- [`phases/MINI-KUZAI-PHASE-03.md`](phases/MINI-KUZAI-PHASE-03.md)
- [`phases/MINI-KUZAI-PHASE-03-IDENTITY.md`](phases/MINI-KUZAI-PHASE-03-IDENTITY.md)
- [`phases/MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md`](phases/MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md)
- [`phases/MINI-KUZAI-PHASE-03-KNOWLEDGE-MAP.md`](phases/MINI-KUZAI-PHASE-03-KNOWLEDGE-MAP.md)
- [`phases/MINI-KUZAI-PHASE-03-DATASET-SCHEMA.md`](phases/MINI-KUZAI-PHASE-03-DATASET-SCHEMA.md)
- [`phases/MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-DECISION.md`](phases/MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-DECISION.md)
- [`phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md`](phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md)
- [`phases/MINI-KUZAI-PHASE-03-CONVERSATION-AUTHORING-POLICY.md`](phases/MINI-KUZAI-PHASE-03-CONVERSATION-AUTHORING-POLICY.md)
- [`phases/MINI-KUZAI-PHASE-03-V53-CORPUS-CONSOLIDATION.md`](phases/MINI-KUZAI-PHASE-03-V53-CORPUS-CONSOLIDATION.md)
- [`phases/MINI-KUZAI-PHASE-03-PAUSE-2026-09-27.md`](phases/MINI-KUZAI-PHASE-03-PAUSE-2026-09-27.md)

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
Phase 03                  : DATA PREPARATION - V53 TRAIN COMPLETION
B01-B05 batches           : HISTORICAL BATCHES PRESERVED
Canonical TRAIN records   : 104 AUDITED / 107 PREPARED
TRAIN semantic groups     : 28 / 29 AUDITED - 29 / 29 PREPARED
CRITICAL TRAIN            : ALL COMPLETE
HIGH TRAIN                : ALL COMPLETE
MEDIUM TRAIN              : B13 AUDITED - B14 REVIEWED / AUDIT PENDING
B14 TRAIN                 : 3 REVIEWED - 1 TARGET CORRECTION
Public SmolTalk TRAIN     : 2 CANONICAL DERIVATIVES
Prepared provenance       : 105 PHASE03-DESIGNED / 2 SMOLTALK
External dataset study    : V49/V51/V52 REVIEWED - V53 ACTIVE
SmolTalk v0.4             : 8000 SOURCE / 1139 V44 PROVISIONAL
OASST1                    : ASSESSED - NOT SELECTED FOR CURRENT MIX
Latest V53 GOGIT          : B13 COMPLETE - 104 TRAIN
Private corpus pipeline   : LOCAL-ONLY - PAUSED
Private source material   : NOT COMMITTED
Derived private metrics   : NOT COMMITTED
Semantic inventory        : V0.3 - 65 GROUPS
B01-B05 custom exchanges  : 35 REVIEWED (31 JSONL RECORDS)
Authoring policy          : V0.2
Semantic split guard      : ACTIVE
VALIDATION records        : 0 / 36 CREATED
BLIND TEST records        : 0 / 36 CREATED
Tokenizer                 : FINAL VOCABULARY NOT FROZEN
Phase 03 architecture     : NOT SELECTED YET
Phase 03 training         : NOT STARTED
Training authorized       : NO
```

B01 through B05 custom TRAIN batches remain preserved and reviewed (31 JSONL records containing 35 USER/ASSISTANT exchanges). V53 subsequently expanded the controlled corpus across the remaining behavior families. The last audited corpus contains **104 unique records** across **28 of 29 TRAIN semantic groups**. B14 `sg-b14-01 discovery_affect` is now authored and reviewed with three records; one target was corrected to remove preference-like wording. If its final audit passes, TRAIN reaches the policy-planned **107 unique records across all 29 groups**, with **105 `phase03-designed` records and 2 admitted public SmolTalk derivatives**. No VALIDATION or BLIND TEST conversation text has been created.

The external SmolTalk review completed V49 (24 RETAIN, 44 REJECT), V51 (9 A, 8 B, 7 C) and V52 (8 A, 12 B, 12 C). V53 then applied repair, independent review, deduplication, semantic anti-leakage, eligibility and admission gates. Both accepted public derivatives are now canonical, while V44 remains provisional; the purposefully sampled reviews still do not establish an acceptance rate for the full reservoir. Private-source curation remains exclusively local and paused. Tokenizer vocabulary, Phase 03 architecture and model training remain unfrozen / unselected / unauthorized.

See the [V53 corpus consolidation status](phases/MINI-KUZAI-PHASE-03-V53-CORPUS-CONSOLIDATION.md), [B13 completion audit](reports/assistant-results/history/PHASE03-SMOLTALK-V53-B13-BEHAVIOR-COMPLETE-001.json), [B17 completion audit](reports/assistant-results/history/PHASE03-SMOLTALK-V53-B17-BEHAVIOR-COMPLETE-001.json), [B15 completion audit](reports/assistant-results/history/PHASE03-SMOLTALK-V53-B15-BEHAVIOR-COMPLETE-001.json), [V52 annotated results](reviews/smoltalk-v52/RESULTS-001.md), [V51 verified results](reviews/smoltalk-v51/RESULTS-001.md), [V49 completed results](reviews/smoltalk-v48/V49-HOLD-RESOLUTION.md), the [historical 2026-10-10 pause checkpoint](phases/MINI-KUZAI-PHASE-03-PAUSE-2026-10-10.md) and the [private corpus methodology](phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md).

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
