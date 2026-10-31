#### **`Mini-Kuzai - LLM`**

#### **`BUILD A LANGUAGE MODEL FROM SCRATCH, TRAIN IT LOCALLY AND INSPECT WHAT HAPPENS INSIDE A TRANSFORMER.`**

[![GITHUB](https://img.shields.io/badge/GITHUB-555555?style=flat-square&logo=github&logoColor=white)](https://github.com/Kusanagi8200/Mini-Kuzai)&#8202;![MINI-KUZAI](https://img.shields.io/badge/MINI--KUZAI-FFFFFF?style=flat-square)&#8202;![PYTHON](https://img.shields.io/badge/PYTHON-2EA043?style=flat-square)&#8202;![PYTORCH](https://img.shields.io/badge/PYTORCH-2EA043?style=flat-square)&#8202;![CUDA](https://img.shields.io/badge/CUDA-2EA043?style=flat-square)&#8202;![TRANSFORMER](https://img.shields.io/badge/TRANSFORMER-2EA043?style=flat-square)&#8202;![FROM SCRATCH](https://img.shields.io/badge/FROM%20SCRATCH-555555?style=flat-square)&#8202;![PHASE 03](https://img.shields.io/badge/PHASE%2003-D73A49?style=flat-square)

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

##### **``PROJECT EXECUTION POLICY``**

Mini-Kuzai uses a **loop-first, resumable workflow policy** for project operations. When several deterministic gates can be chained safely, they should be executed by one idempotent runner that verifies state, skips already validated gates, publishes evidence, and continues until a genuine semantic, authorization, destructive, or non-verifiable decision boundary is reached.

This policy applies project-wide to suitable dataset, audit, test, GOGIT, documentation-consistency, training-preparation, and evaluation workflows. Automation must never weaken semantic split protection, provenance, private-data restrictions, historical evidence, checkpoint protection, or explicit training authorization.

See [`PROJECT-WORKFLOW-POLICY.md`](PROJECT-WORKFLOW-POLICY.md).

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

1. tokenizer, embeddings and positions
2. Q/K/V and causal self-attention
3. context, residuals, MLP and first Transformer block
4. complete model, training and generation
5. EOS, sampling, temperature and parameter inspection
6. multi-head attention and model depth
7. validation methodology, early stopping and deterministic reproducibility
8. compositional generalization and clean train/validation/test separation
9. batching, dynamic padding, DataLoader and batched training
10. learning-rate search and frozen final training
11. independent and blind evaluation
12. attention/head/component ablation
13. residual-stream and logit tracing
14. LayerNorm decomposition and gamma/beta analysis
15. beta vocabulary bias, target-frequency analysis, regression and additive logit identity.

**See [`phases/MINI-KUZAI-PHASE-01.md`](phases/MINI-KUZAI-PHASE-01.md) for the phase summary and [`technical/PHASE-01-SOURCE-MANIFEST.md`](technical/PHASE-01-SOURCE-MANIFEST.md) for the imported source inventory.**

---

#### **`MINI-KUZAI PHASE 03`**

Phase 03 moves from the tiny pedagogical baseline toward a new conversational model trained from scratch.

The target character is a developing feminine artificial intelligence originating in THE KUZ NETWORK laboratory. The intended behavior emphasizes curiosity, independent thinking, intellectual honesty, creativity, initiative, reasoned disagreement, uncertainty, opinion formation and revision, multi-turn consistency, and progressive discovery of the wider world.

Phase 03 has already defined -->

- the personality questionnaire
- identity specification
- behavior matrix B01-B18
- knowledge map
- dataset schema and anti-leakage rules
- external dataset evaluation methodology
- semantic group inventory v0.3 with 65 groups
- TRAIN / VALIDATION / BLIND TEST split allocation
- conversation authoring policy v0.4
- semantic split exclusion map and manual anti-leakage review.

External dataset research has also been completed for the current cycle.

Current external data decision -->

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

### External SmolTalk curation - historical V44-V53 review work

The public SmolTalk v0.4 reservoir contains 8,000 candidate records, but is not an approved training dataset. V44 produced a provisional stratified selection of 1,139 conversations (679 multi-turn, 460 single-turn). A keyword-based creative category reached 69 of its 130 target records. V46 found broader creative signals and produced a 68-record **local review queue**; neither these signals nor the queue are validated training examples.

V47 verified the integrity of all 68 local review records against their public SmolTalk sources. V48/V49 subsequently reviewed those 68 public-source cases on GitHub (36 priority and 32 baseline); historical local review tools remain available but are not the active completion status. The V44 pool is unchanged and final mixture ratios remain undecided.

Public aggregate results are transmitted using the reviewed [gogit workflow](tools/GOGIT.md) --> the local script publishes only allowlisted numerical SmolTalk metrics to `reports/assistant-results/`, and the user then requests retrieval with `gogit`. This mechanism does not run in the background and must never be used for private conversation data or private-derived results.

**GitHub-native SmolTalk reviews --> ** All 68 public external case files were reviewed in V48 and the 14 HOLD cases were resolved in V49. Current results --> 24 RETAIN, 44 REJECT and 0 HOLD. See the [V49 results](reviews/smoltalk-v48/V49-HOLD-RESOLUTION.md), [historical V48 report](reviews/smoltalk-v48/V48-REVIEW-RESULTS.md) and [GitHub review guide](tools/V48-GITHUB-REVIEW.md). No private ChatGPT-source material is included.

**V50 - revised training-data direction --> ** Mini-Kuzai now prioritizes cognitive exploration, multi-turn understanding, imagination, character development, creative writing, nuanced dialogue, correction after feedback and contextual expression. Specialized IT and programming proficiency is secondary. An imperfect conversational example is not automatically excluded for a technical fault, but an incorrect answer cannot be promoted as a correct supervised target. V48/V49 verdicts are historical quality assessments, not permanent bans on behavioral analysis.

V50 has completed a **local-only heuristic screening of all 1,139 provisional V44 public SmolTalk candidates** --> 200 HIGH, 431 MEDIUM and 508 LOW. These are selection hints, not semantic or quality verdicts. See the [V50 cognitive/creative policy](phases/MINI-KUZAI-PHASE-03-V50-COGNITIVE-CREATIVE-PRIORITY.md), [public numeric report](reports/assistant-results/history/PHASE03-SMOLTALK-V50-COGNITIVE-SCREEN-001.json) and [eight-case methodology pilot](reviews/smoltalk-v50/PILOT-001.md). The full queue remains on fhc2; V44, tokenizer and TRAIN allocation are unchanged.

**V51 - first semantic review completed --> ** 24 new public SmolTalk conversations were evaluated on GitHub --> 9 A, 8 B, 7 C, 0 HOLD. These include 12 HIGH, 6 MEDIUM and 6 LOW V50 hint examples. The results demonstrate both underestimated creative/contextual examples in MEDIUM/LOW and an invalid HIGH example. See the [V51 qualitative results](reviews/smoltalk-v51/RESULTS-001.md), [24 reviewed cases](reviews/smoltalk-v51/README.md) and [V51 methodology](phases/MINI-KUZAI-PHASE-03-V51-SEMANTIC-REVIEW.md). Only public external SmolTalk cases were reviewed. The [V51 numeric GOGIT audit](reports/assistant-results/history/PHASE03-SMOLTALK-V51-PILOT-REVIEW-001.json) was published and verified.

**V52 - 32-case semantic review annotated --> ** The [source-verified V52 inventory](reports/assistant-results/history/PHASE03-SMOLTALK-V52-INVENTORY-001.json) identified 1,071 candidates still available in the provisional V44 selection before the V52 batch (after excluding 44 V48 in-V44 examples and 24 V51 examples). A further 32 distinct public-external cases were published (8 HIGH, 12 MEDIUM and 12 LOW; 20 multi-turn) and all 32 were subsequently annotated on GitHub --> **8 A, 12 B, 12 C, 0 HOLD**. See the [V52 qualitative summary](reviews/smoltalk-v52/RESULTS-001.md), [case index](reviews/smoltalk-v52/README.md) and [V52 workflow](tools/V52-GITHUB-REVIEW.md). The [historical V52 GOGIT progress snapshot](reports/assistant-results/history/PHASE03-SMOLTALK-V52-REVIEW-PROGRESS-001.json) recorded 8/32 before the remaining annotations. The [final V52 GOGIT audit](reports/assistant-results/history/PHASE03-SMOLTALK-V52-REVIEW-FINAL-001.json) was published and verified on 2026-10-17 at commit [`8a28e956`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/8a28e95637377f29d7204f51d49a174f2518929f) --> **32/32 reviewed, 8 A, 12 B, 12 C, 0 HOLD, 0 PENDING, 0 TRAIN approved**. Historical reports must not be rewritten.

The V52 pause checkpoint is now historical. V53 resumed public-only corpus consolidation while preserving all earlier review reports. Across V48/V49, V51 and V52, 124 distinct public SmolTalk examples remain the reviewed source population; V53 adds independent repair, derivative, eligibility and admission gates rather than redefining those historical grades. The tokenizer is frozen at V56 and the V58 experimental architecture baseline is frozen. The final training mixture is not finalized and Phase 03 model training has not started or been authorized.

**V53 - public corpus consolidation and controlled TRAIN expansion --> ** The [V53 workstream](phases/MINI-KUZAI-PHASE-03-V53-CORPUS-CONSOLIDATION.md) has progressed from cross-cycle accounting through repair planning, derivative review, eligibility, admission and behavior-by-behavior TRAIN completion. The last published GoGit state contains **107 unique canonical TRAIN records across all 29 TRAIN semantic groups**. B14 EMOTIONAL EXPRESSION has now been authored and reviewed at the three-record MEDIUM target; one target wording was corrected during semantic review. The audited TRAIN corpus contains **107 unique records across all 29 TRAIN groups**, confirmed by the published B14C GOGIT audit. Audited provenance is **105 `phase03-designed` records plus 2 admitted public SmolTalk derivatives**. V54 subsequently completed and globally closed the **36-record / 18-group VALIDATION corpus**. BLIND TEST authoring is now authorized, no BLIND records existed at V54 closure, and model training remains unauthorized.

### Phase 03 corpus and architecture baseline - 2026-10-28 (historical)

The controlled conversational corpus is closed at **179 conversations across 65 semantic groups** -->

- TRAIN --> **107 records / 29 groups**
- VALIDATION --> **36 records / 18 groups, frozen**
- BLIND TEST --> **36 records / 18 groups, frozen**
- cross-split ID collisions --> 0
- cross-split semantic-group overlap --> 0
- exact cross-split prompt collisions --> 0.

The reproducible pre-training baseline is also frozen -->

- **V56 tokenizer --> ** `byte_bpe_whitespace`, vocabulary 1024, 765 merges, byte fallback, no UNK
- **V57 serialization --> ** ordinary textual `USER:` / `MINI-KUZAI:` labels, BOS at conversation start and EOS at conversation end
- **V58 architecture baseline --> ** decoder-only Transformer, context 2048, `d_model=128`, 4 heads, 4 layers, FFN 512, **1,184,512 parameters**
- **V59 segmentation --> ** turn-aware 2048-token segmentation is implemented and closed; complete USER / MINI-KUZAI pairs are preserved and no arbitrary intra-pair split is allowed.

### V59 public-mixture quality state

The V59 public candidate population contains **1,112 conversations** after structural exclusions, controlled-source reuse protection and known-negative filtering. The main quality-estimation population contains **1,080 conversations**.

Bulk Samples 001 and 002 reviewed **144 unique public conversations**. The stratum-weighted diagnostic estimated -->

- KEEP --> **49.36%**
- REPAIR --> **27.61%**
- EXCLUDE --> **23.03%**
- unchanged-unsuitable = REPAIR + EXCLUDE --> **50.64%**
- approximate diagnostic interval for unchanged-unsuitable --> **42.79% to 58.49%**.

The unchanged-bulk admission gate therefore **FAILED**. The V44-derived public bulk must not be promoted unchanged into supervised training.

Simple V59 filter-rule mining found only one narrow high-precision rule and insufficient recall for broad filtering. A first supervised text triage model also failed its authorization gates -->

- REPAIR / EXCLUDE precision --> **60.3%**
- REPAIR / EXCLUDE recall --> **52.1%**
- EXCLUDE precision --> **16.7%**
- EXCLUDE recall --> **8.8%**.

The failed classifier was then used only as an uncalibrated ranking signal for **Active-Learning Sample 003**, containing 72 new cases.

Sample 003 results -->

| Bucket | KEEP | REPAIR | EXCLUDE | Unchanged unsuitable |
| --- | ---: | ---: | ---: | ---: |
| HIGH_RISK_RANK | 2 | 15 | 1 | 88.9% |
| MIDDLE_RANK | 10 | 6 | 2 | 44.4% |
| LOW_RISK_RANK | 18 | 0 | 0 | 0.0% |
| DIVERSITY_CONTROL | 11 | 3 | 4 | 38.9% |

The ranking direction is therefore **VALIDATED** for prioritizing review, but the score is not a calibrated probability and does not authorize automatic filtering.

Current V59 quality-control total -->

- public conversations semantically reviewed --> **288**
- independent Holdout 004 --> **CLOSED**
- Holdout 004 REPAIR/EXCLUDE AUC --> **0.595**
- Holdout 004 ranking gate --> **FAILED**
- automatic REVIEW --> **NOT AUTHORIZED**
- automatic EXCLUDE --> **NOT AUTHORIZED**
- never-reviewed public candidates remaining --> **792**.

The conservative final-mix policy is now closed -->

- DIRECT_KEEP --> **165 conversations / 270877 tokens**
- REPAIR_QUEUE --> **108 conversations / 198226 tokens**
- EXCLUDE_REVIEWED --> **47 conversations / 56726 tokens**
- DEFER_UNREVIEWED --> **792 conversations / 1204585 tokens**
- controlled TRAIN --> **24539 tokens**
- combined clean frozen envelope --> **295416 tokens**
- V59 final mix --> **FINALIZED**.

The persona-first exposure policy is now finalized -->

- CONTROLLED_TRAIN target --> **30.00%**
- PERSONA_CORE target --> **46.58%**
- GENERAL_SUPPORT target --> **15.00%**
- LEGACY_STRUCTURED_KEEP target --> **8.42%**
- persona-oriented exposure --> **76.58%**
- physical duplication --> **NO**
- REPAIR / EXCLUDE / UNREVIEWED admission --> **NO**.

The bounded training-protocol preflight is closed -->

- CUDA / BF16 --> **PASS**
- full-context microbatch --> **8 x 2048**
- peak reserved VRAM --> **632 MiB / 8.20%**
- preflight memory gate --> **60.00%**
- authorization candidate --> **YES**.

The terminal V59 freeze and authorization gate is also closed -->

```text
SEMANTIC_VALIDATION_COMPLETE = 1
V59_MIX_FINALIZED            = 1
TRAINING_AUTHORIZED          = 1
TRAINING_STARTED             = 0
```

Authorization scope -->

`V59_BOUNDED_PILOT_ONLY`

Freeze fingerprint -->

`40008ff0b106d3c58d2bf8196f539be2bf692d1e8ed3b7cd0e2dd1429b887503`

Final frozen training identity -->

- controlled TRAIN --> **107 conversations**
- public DIRECT_KEEP --> **165 conversations**
- total --> **272 conversations / 345 segments / 295416 unique tokens**
- REPAIR_QUEUE excluded --> **108**
- EXCLUDE_REVIEWED excluded --> **47**
- DEFER_UNREVIEWED excluded --> **792**.

Authorized exposure targets -->

- CONTROLLED_TRAIN --> **30.00%**
- PERSONA_CORE --> **46.58%**
- GENERAL_SUPPORT --> **15.00%**
- LEGACY_STRUCTURED_KEEP --> **8.42%**
- persona-oriented exposure --> **76.58%**.

The authorization is limited to the bounded V59 pilot -->

- architecture --> V58 MICRO FROZEN
- maximum optimizer steps --> **145**
- maximum exposure tokens --> **1181664**
- frozen VALIDATION --> allowed during the pilot
- BLIND TEST --> forbidden during training and reserved for post-training evaluation.

**Training is authorized but has not started.**

The persistent V59 bounded-pilot trainer is now **implemented, frozen and
runtime verified**.

Persistent-trainer state -->

- trainer freeze fingerprint --> `d71fb0fe6e71cbfd46ae06a88ef994b91091c698b8f401237387b5fc7ebe3a84`
- trainer compile / tests / runtime verification --> **PASS**
- TRAIN reconstruction --> **345 segments / 295416 unique tokens**
- VALIDATION reconstruction --> **36 records / 36 segments / 9242 tokens**
- schedule preview --> **2263 segments / 1181302 exposure tokens**
- maximum schedule-share deviation --> **4 basis points**
- BLIND TEST access --> **0**
- checkpoint resume state --> optimizer / scheduler / RNG / sampler
- GPU runtime verification --> **NVIDIA GeForce RTX 5060 Laptop GPU**
- canonical first-run directory --> **ABSENT before launch**
- TRAINING_STARTED --> **0**

Historical V54 VALIDATION declaration schema differences were verified through
**18 / 18 historical GOGIT freeze proofs** and **18 / 18 target Git blob
matches**. No frozen VALIDATION corpus file was rewritten.

A post-authorization segmentation caching experiment improved a bounded
synthetic benchmark but changed the frozen segmentation dependency fingerprint.
It was reverted before trainer freeze. The authorized V59 pilot therefore
retains the original frozen segmentation implementation.

The next workstream is the **first real V59 bounded-pilot training run** using
the frozen trainer without `--resume`. The hard limits remain **145 optimizer
steps** and **1181664 exposure tokens**, with frozen VALIDATION allowed during
training and BLIND TEST forbidden until post-training evaluation.

See -->

- [V59 training mix and segmentation](phases/MINI-KUZAI-PHASE-03-V59-TRAINING-MIX-SEGMENTATION.md)
- [V59 training-authorized checkpoint - 2026-10-28](phases/MINI-KUZAI-PHASE-03-V59-TRAINING-AUTHORIZED-CHECKPOINT-2026-10-28.md)
- [V59 final authorization results](reviews/smoltalk-v59-final-mix-freeze-authorization/RESULTS-001.md)
- [V59 terminal authorization GOGIT audit](reports/assistant-results/history/PHASE03-SMOLTALK-V59-FINAL-MIX-FREEZE-AUTHORIZATION-001.json)
- [V59 persistent trainer freeze results](reviews/smoltalk-v59-persistent-trainer-freeze/RESULTS-001.md)
- [V59 persistent trainer GOGIT audit](reports/assistant-results/history/PHASE03-SMOLTALK-V59-PERSISTENT-TRAINER-FREEZE-001.json)
- [V59 validation compatibility GOGIT audit](reports/assistant-results/history/PHASE03-SMOLTALK-V59-VALIDATION-COMPATIBILITY-001.json)
- [V59 pause checkpoint - 2026-10-25](phases/MINI-KUZAI-PHASE-03-V59-PAUSE-CHECKPOINT-2026-10-25.md)
- [V59 Active-Learning Sample 003 results](reviews/smoltalk-v59-active-sample-003/RESULTS-003.md)

### V60-V62 training evolution - historical training checkpoints

V59 established the frozen persona-first training identity at **272 conversations / 345 segments / 295416 unique tokens**. The subsequent experiments kept architecture, tokenizer, corpus, stream weighting and the V60 corrected initialization controlled so objective changes could be interpreted directly.

**V60 --> corrected initialization and extended training**

- final validation loss --> **3.429395**
- final exposure --> **4,435,262 tokens / 509 optimizer steps**
- stop --> **PLATEAU**
- UTF-8 --> **fixed**
- distinct probe outputs --> **6 / 6**
- EOS completions --> **0 / 6**
- mean generation length --> **96 / 96**
- repeated-trigram rate --> **95.17%**

V60 learned the data numerically but did not learn reliable free-generation termination. Teacher-forced EOS diagnostics showed a real end-of-response signal, while free autoregressive generation drifted away from terminal states.

**V61 --> boundary-aware EOS objective**

- terminal and intermediate boundary weights --> **16 / 16**
- mandatory cycle-2 stop --> **597982 exposure tokens / 69 optimizer steps**
- validation loss --> **6.959721 to 4.713690**
- terminal EOS top-1 --> **24 / 36**
- intermediate EOS top-1 --> **8 / 13**
- intermediate EOS above true continuation --> **13 / 13**
- ordinary nonterminal false EOS top-1 --> **105 / 9170**
- free-generation EOS completions --> **0 / 6**
- repeated-trigram rate --> **96.65%**

V61 proved that terminal EOS can be reinforced, but its asymmetric objective over-generalized EOS. Continuation to cycle 4 was rejected.

**V62 --> pairwise boundary-margin objective**

V62 replaces V61 probability suppression with direct logit relations -->

```text
terminal     -> EOS > best_non_EOS + margin
intermediate -> TRUE_CONTINUATION > EOS + margin
```

The V62 preflight selected -->

- margin --> **0.25**
- terminal weight --> **8.00**
- intermediate weight --> **17.358491**
- TRAIN boundary-balance factor --> **2.169811**
- auxiliary-loss ratio --> **1.32%**
- terminal active validation margins --> **16 / 36**
- intermediate active validation margins --> **13 / 13**
- CUDA/BF16 preflight --> **PASS**

V62 control plane state -->

```text
MARGIN OBJECTIVE PREFLIGHT = PASS
OBJECTIVE FREEZE           = PASS
TRAINING PROTOCOL          = PASS
TRAINING AUTHORIZATION     = PASS
PERSISTENT TRAINER FREEZE  = PASS

TRAINING_AUTHORIZED        = 1
TRAINING_STARTED           = 0
BLIND_ACCESS               = 0
```

Authorized V62 window --> **4 cycles / 1181664 tokens / 145 optimizer steps**, with a mandatory continuation review at **cycle 2** and the V60 scheduler horizon preserved at **577 steps**.

Historical V62 stop --> **cycle-2 mandatory review completed at 69 optimizer steps / 597982 exposure tokens**. No new continuation is authorized by this historical run.

See the [V62 pause checkpoint - 2026-10-28](phases/MINI-KUZAI-PHASE-03-V62-PAUSE-CHECKPOINT-2026-10-28.md).

---

### V63-V64 verified results - 2026-10-31

**Current checkpoint --> V64 LANGUAGE LEARNING DIAGNOSTIC 002 completed. V65 proposed, not executed.**

V62 training stopped at its mandatory cycle-2 gate after **69 optimizer steps / 597982 exposed tokens**. Its frozen checkpoint is retained. V63 and V64 are inference/diagnostic workstreams, **not** new training sessions.

- **V63 decoding** --> greedy termination 0/6 with severe token repetition; top-k 40 / top-p 0.9 / temperature 0.8 achieved **41/48 EOS completions** over eight seeds, compared with **27/48** for temperature-only decoding
- **V63 language screen** --> 24 private generations, **20/24 EOS**, **0/24 invalid UTF-8**, but **10/24** rule-flagged as linguistically suspicious and **2/24** without regex-recognized words. The interrupted human semantic review was **not completed**
- **V64 runtime diagnosis** --> original audit 001 exceeded GOGIT's 300-second timeout; bounded trace found **98.270 s** building TRAIN and an unfinished training-boundary-index step
- **V64 optimized audit 002** --> duplicate corpus construction and unnecessary boundary-index generation removed while keeping frozen integrity checks. GOGIT published successfully at commit [`9d8dcb62`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/9d8dcb62b6e9bc3826f95eb93953c95c28835132)
- **V64 next-token loss** --> TRAIN exploratory sample **4.664 CE / 33.97% top-1**, full VALIDATION **4.733 CE / 29.20% top-1**. Terminal EOS top-1 **14/36**, reproducing historical V63
- **V64 tokenizer findings** --> roughly **51-53%** of non-special token occurrences are raw-byte tokens. VALIDATION mean NLL **3.386** on byte targets versus **6.268** on BPE-merged targets. Different token-frequency distributions prevent declaring the tokenizer defective

The 12 TRAIN segments sampled for V64 are **not representative** of all 345 TRAIN segments. The V63 lexical screen is **not** semantic validation. The model has learned numerical next-token structure, but the available generated texts do **not** demonstrate conversational intelligibility.

**Next gate --> V65 TOKEN LEARNING AND TRAINING READINESS (proposed)**. Investigate token frequency, target-specific accuracy and historical learning progression before deciding whether to authorize any additional training, tokenizer revision or model capacity change. The **BLIND TEST remains closed**.

References -->

- [V64 closure and V65 readiness](phases/MINI-KUZAI-PHASE-03-V64-CLOSURE-V65-READINESS-2026-10-31.md)
- [Latest successful V64-002 GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002.json)
- [V63 decoding robustness](reports/assistant-results/history/PHASE03-SMOLTALK-V63-DECODING-ROBUSTNESS-001.json)
- [V63 automatic language screening](reports/assistant-results/history/PHASE03-SMOLTALK-V63-AUTOMATIC-LANGUAGE-SCREEN-001.json)

---

### V65 verified and V66 prepared - 2026-10-31

**V65 TOKEN FREQUENCY DIAGNOSTIC 001** completed successfully via GOGIT, commit [`358c6b07`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/358c6b07bbcc616ee592d763874cbf8b7bd71da5). Full TRAIN token frequency --> **294726 nonspecial token occurrences / 891 observed token IDs**. On 9170 nonspecial frozen VALIDATION targets, frequent raw-byte tokens achieved **52.00%** exact top-1 accuracy (4873 occurrences) while frequent merged Byte-BPE tokens achieved **3.27%** (4287 occurrences). This gap is **not** explained solely by rare tokens. V65 reproduced VALIDATION CE **4.733** and terminal EOS top-1 **14/36**.

The next diagnostic **V66 TOKEN PREDICTION BIAS 001** is coded and documented but **not yet executed on GPU**. It will compare gold Byte/BPE targets with top-1 predicted Byte/BPE/SPECIAL tokens, the model's probability mass by class, and more detailed token-frequency bands. The result may help determine whether poor BPE accuracy reflects an output-class bias or confusion among merged-token alternatives.

- [Completed V65 GOGIT report](reports/assistant-results/history/PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001.json)
- [V65 documented results](phases/MINI-KUZAI-PHASE-03-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001.md)
- [V66 pre-execution protocol](phases/MINI-KUZAI-PHASE-03-V66-TOKEN-PREDICTION-BIAS-001.md)

**No newly authorized training, no changed checkpoint or tokenizer, and no BLIND TEST access.**

---

### Private local corpus pipeline

Phase 03 includes a local-only pipeline for evaluating private conversational corpora as possible future training material.

A personal ChatGPT export is used locally as one private source for building conversation-specific data. Its purpose is to capture real multi-turn interaction patterns such as troubleshooting, correction after feedback, explanation, reasoning, planning, technical dialogue, and general conversation. The export is never treated as ready-to-train data.

The public repository contains only the generic processing methodology. No source conversation, source-derived excerpt, source-specific statistic, candidate queue, review output, or other information originating from private discussions is committed.

The local pipeline covers conversation reconstruction, topic segmentation, failed-step curation, factual validation, semantic mapping, duplicate control, language-policy decisions, and TRAIN / VALIDATION / BLIND anti-leakage checks.

Multi-turn examples preserve the order and provenance of observed user feedback. Rewritten assistant targets are explicitly distinguished from original responses; partial success is never promoted to unobserved verification. Editorial acceptance into a local candidate pool is not official TRAIN integration or training approval.

The authorized V59 bounded pilot does not include the private corpus. Its final frozen mixture contains only the controlled TRAIN and human-reviewed public DIRECT_KEEP material. Any future private-corpus integration would constitute a new corpus version and would require a new anti-leakage, freeze, weighting and training-authorization cycle.

The private conversation source remains a possible future research input. It is outside the V59 authorization and must not modify or be injected into the frozen bounded-pilot corpus.

See [`phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md`](phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md) for the public methodology.
See -->

- [`phases/MINI-KUZAI-PHASE-03.md`](phases/MINI-KUZAI-PHASE-03.md)
- [`phases/MINI-KUZAI-PHASE-03-IDENTITY.md`](phases/MINI-KUZAI-PHASE-03-IDENTITY.md)
- [`phases/MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md`](phases/MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md)
- [`phases/MINI-KUZAI-PHASE-03-KNOWLEDGE-MAP.md`](phases/MINI-KUZAI-PHASE-03-KNOWLEDGE-MAP.md)
- [`phases/MINI-KUZAI-PHASE-03-DATASET-SCHEMA.md`](phases/MINI-KUZAI-PHASE-03-DATASET-SCHEMA.md)
- [`phases/MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-DECISION.md`](phases/MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-DECISION.md)
- [`phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md`](phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md)
- [`phases/MINI-KUZAI-PHASE-03-CONVERSATION-AUTHORING-POLICY.md`](phases/MINI-KUZAI-PHASE-03-CONVERSATION-AUTHORING-POLICY.md)
- [`phases/MINI-KUZAI-PHASE-03-V53-CORPUS-CONSOLIDATION.md`](phases/MINI-KUZAI-PHASE-03-V53-CORPUS-CONSOLIDATION.md)
- [`phases/MINI-KUZAI-PHASE-03-V54-VALIDATION-CLOSURE.md`](phases/MINI-KUZAI-PHASE-03-V54-VALIDATION-CLOSURE.md)
- [`phases/MINI-KUZAI-PHASE-03-V55-BLIND-FREEZE.md`](phases/MINI-KUZAI-PHASE-03-V55-BLIND-FREEZE.md)
- [`phases/MINI-KUZAI-PHASE-03-V56-TOKENIZER-DESIGN.md`](phases/MINI-KUZAI-PHASE-03-V56-TOKENIZER-DESIGN.md)
- [`phases/MINI-KUZAI-PHASE-03-V57-ARCHITECTURE-PREPARATION.md`](phases/MINI-KUZAI-PHASE-03-V57-ARCHITECTURE-PREPARATION.md)
- [`phases/MINI-KUZAI-PHASE-03-V58-ARCHITECTURE-BASELINE.md`](phases/MINI-KUZAI-PHASE-03-V58-ARCHITECTURE-BASELINE.md)
- [`reviews/phase-03-v55/CODE-DOC-REVIEW-2026-10-17.md`](reviews/phase-03-v55/CODE-DOC-REVIEW-2026-10-17.md)
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
Linux kernel 7.0.0-38-generic
Python 3.12.3
PyTorch 2.13.0+cu130
CUDA 13.0
NVIDIA driver 580.178.04
NVIDIA GeForce RTX 5060 Laptop GPU - 8 GB VRAM
Compute capability 12.0
BF16 supported
NumPy 2.5.2
System RAM - 32 GB
```

**See [`technical/installation/README.md`](technical/installation/README.md) for setup commands.**

---

#### **`PHILOSOPHY`**

**`The project follows a practical sequence: implement or define one mechanism, execute it, inspect data and outputs, verify the behavior, document the result, then integrate it into the next stage.`**

Theory is introduced when needed to explain an observed result.

Mini-Kuzai is therefore both a language-model implementation project and a laboratory for studying how language models acquire language, behavior, identity, and conversational patterns.

---

#### **`CURRENT STATUS - 2026-10-31`**

```text
Phase 01 checkpoint       --> FROZEN
Phase 02 KV cache         --> PRESERVED
Phase 03                  --> V65 COMPLETED / V66 PREPARED
Controlled TRAIN          --> 107 RECORDS / 29 GROUPS
VALIDATION                --> 36 RECORDS / 18 GROUPS FROZEN
BLIND TEST                --> 36 RECORDS / 18 GROUPS FROZEN / CLOSED
Total controlled corpus   --> 179 RECORDS / 65 GROUPS
V59 TRAINING MIX          --> 272 CONVERSATIONS / 345 SEGMENTS
V59 UNIQUE TOKENS         --> 295416
V56 TOKENIZER             --> BYTE-BPE WHITESPACE / 1024 FROZEN
V58/V60 MODEL             --> 1,184,512 PARAMETERS / FROZEN
V62 CHECKPOINT            --> CYCLE 2 FROZEN
V62 OPTIMIZER STEPS       --> 69
V62 EXPOSURE TOKENS       --> 597982
V63 TOP-K/TOP-P EOS       --> 41/48 OVER 8 SEEDS
V63 AUTO LANGUAGE SCREEN  --> 10/24 RULE-FLAGGED / NOT SEMANTIC VALIDATION
V64 TRAIN SAMPLE CE       --> 4.664 / 12 EXPLORATORY SEGMENTS
V64 VALIDATION CE         --> 4.733 / 36 FROZEN SEGMENTS
V64 VALIDATION TOP-1      --> 29.20%
V64 EOS TERMINAL TOP-1    --> 14/36
V64 GOGIT                 --> DIAGNOSTIC 002 PUBLISHED
V65 GOGIT                 --> TOKEN FREQUENCY 001 PUBLISHED
V65 BYTE TOP1             --> 52.00% / FREQUENT TARGETS
V65 MERGED TOP1           --> 3.27% / FREQUENT TARGETS
V66                       --> IMPLEMENTED / GPU EXECUTION PENDING
New training authorized   --> NO
New training started      --> NO
BLIND access in V63/V64   --> 0
Next step                 --> V66 TOKEN PREDICTION BIAS GPU AUDIT
```

**Status qualification** --> Earlier V62 GOGIT records `TRAINING_AUTHORIZED=1` and `TRAINING_STARTED=1` for its historical authorized and executed run. V64 reports `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0` and `SEMANTIC_VALIDATION_COMPLETE=0` for the present diagnostic. They must not be confused.

See the [verified V65 frequency diagnostic](phases/MINI-KUZAI-PHASE-03-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001.md) and [V66 proposed audit](phases/MINI-KUZAI-PHASE-03-V66-TOKEN-PREDICTION-BIAS-001.md). Historical V53-V62 details remain documented above and in the phase archives.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
