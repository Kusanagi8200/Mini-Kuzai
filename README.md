#### **`Mini-Kuzai - LLM`**

#### **`BUILD A LANGUAGE MODEL FROM SCRATCH, TRAIN IT LOCALLY AND INSPECT WHAT HAPPENS INSIDE A TRANSFORMER.`**

[![GITHUB](https://img.shields.io/badge/GITHUB-555555?style=flat-square&logo=github&logoColor=white)](https://github.com/Kusanagi8200/Mini-Kuzai)&#8202;![MINI-KUZAI](https://img.shields.io/badge/MINI--KUZAI-FFFFFF?style=flat-square)&#8202;![PYTHON](https://img.shields.io/badge/PYTHON-2EA043?style=flat-square)&#8202;![PYTORCH](https://img.shields.io/badge/PYTORCH-2EA043?style=flat-square)&#8202;![CUDA](https://img.shields.io/badge/CUDA-2EA043?style=flat-square)&#8202;![TRANSFORMER](https://img.shields.io/badge/TRANSFORMER-2EA043?style=flat-square)&#8202;![FROM SCRATCH](https://img.shields.io/badge/FROM%20SCRATCH-555555?style=flat-square)&#8202;![PHASE 03](https://img.shields.io/badge/PHASE%2003-D73A49?style=flat-square)

---

![Mini-Kuzai project illustration](Mini-Kuzai-Project.png)

## Project overview

**Mini-Kuzai** is an experimental autoregressive language model developed **from scratch** with Python and PyTorch, trained and inspected locally using NVIDIA CUDA. It is not built from pretrained weights and is not intended to be a production chatbot.

The project progresses from a fully inspectable Transformer laboratory to a small conversational model with a distinct identity. Its priorities are **curiosity, creative and cognitive development, reasoned disagreement, uncertainty, opinion revision and multi-turn consistency**, rather than specialist technical expertise.

Each stage is documented through source code, reproducible protocols, frozen checkpoints, diagnostic reports and explicit authorization boundaries.

## Navigate the project

**[Phases](#development-phases)** · **[Research steps V48-V79](#phase-03-research-steps)** · **[Current status](#current-status---2026-11-07)** · **[Source code and operations](#code-operations-and-evidence)** · **[Full original documentation](README-DETAILED-20261031T192526Z.md)**

## Development phases

| Phase | Purpose | Documentation |
| --- | --- | --- |
| **01 - Transformer fundamentals** | Tokenization, attention, MLP, LayerNorm, training, ablations and frozen tiny model | [Phase 01](phases/MINI-KUZAI-PHASE-01.md) · [Source manifest](technical/PHASE-01-SOURCE-MANIFEST.md) |
| **02 - Inference** | Autoregressive decoding and KV-cache experiments | [Phase 02](phases/MINI-KUZAI-PHASE-02.md) |
| **03 - Conversational Mini-Kuzai** | Persona, curated corpus, Byte-BPE, new architecture, controlled training and diagnostic evaluation | [Phase 03 overview](phases/MINI-KUZAI-PHASE-03.md) · [Identity](phases/MINI-KUZAI-PHASE-03-IDENTITY.md) · [Behavior matrix](phases/MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md) |

## Phase 03 research steps

Read the steps in order, or open the relevant protocol directly. The detailed historical narrative remains available in the [archived original README](README-DETAILED-20261031T192526Z.md).

| Steps | Focus and result | Detailed documentation |
| --- | --- | --- |
| **V48-V52** | Public SmolTalk semantic reviews and cognitive/creative selection priorities | [V50 policy](phases/MINI-KUZAI-PHASE-03-V50-COGNITIVE-CREATIVE-PRIORITY.md) · [V51 review](phases/MINI-KUZAI-PHASE-03-V51-SEMANTIC-REVIEW.md) · [V52 results](reviews/smoltalk-v52/RESULTS-001.md) |
| **V53-V55** | Controlled corpus consolidation, VALIDATION closure and BLIND TEST freeze | [V53](phases/MINI-KUZAI-PHASE-03-V53-CORPUS-CONSOLIDATION.md) · [V54](phases/MINI-KUZAI-PHASE-03-V54-VALIDATION-CLOSURE.md) · [V55](phases/MINI-KUZAI-PHASE-03-V55-BLIND-FREEZE.md) |
| **V56-V58** | Byte-BPE tokenizer, conversation serialization and 1.18M-parameter Transformer baseline | [V56](phases/MINI-KUZAI-PHASE-03-V56-TOKENIZER-DESIGN.md) · [V57](phases/MINI-KUZAI-PHASE-03-V57-ARCHITECTURE-PREPARATION.md) · [V58](phases/MINI-KUZAI-PHASE-03-V58-ARCHITECTURE-BASELINE.md) |
| **V59** | Training mix, segmentation, public-source quality gates and frozen preparation | [V59 protocol](phases/MINI-KUZAI-PHASE-03-V59-TRAINING-MIX-SEGMENTATION.md) |
| **V60-V62** | Bounded training, EOS objectives, boundary margins and mandatory cycle-2 stop | [V62 run pipeline](phases/MINI-KUZAI-PHASE-03-V62-RUN-001-GOGIT-PIPELINE.md) · [V62 pause checkpoint](phases/MINI-KUZAI-PHASE-03-V62-PAUSE-CHECKPOINT-2026-10-28.md) |
| **V63-V64** | Generation robustness, EOS behavior, runtime profiling and language-learning evaluation | [V63 decoding](phases/MINI-KUZAI-PHASE-03-V63-DECODING-ROBUSTNESS-001.md) · [V64 diagnostic](phases/MINI-KUZAI-PHASE-03-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002.md) |
| **V65-V66** | Token-frequency learning and byte/BPE prediction bias | [V65](phases/MINI-KUZAI-PHASE-03-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001.md) · [V66](phases/MINI-KUZAI-PHASE-03-V66-TOKEN-PREDICTION-BIAS-001.md) |
| **V67-V68** | Output concentration, tied output head, embedding norms and logit margins | [V67](phases/MINI-KUZAI-PHASE-03-V67-OUTPUT-CONCENTRATION-001.md) · [V68](phases/MINI-KUZAI-PHASE-03-V68-OUTPUT-HEAD-DIAGNOSTIC-001.md) |
| **V69-V70** | In-memory output-norm counterfactual and BF16/FP32 precision control | [V69](phases/MINI-KUZAI-PHASE-03-V69-OUTPUT-NORM-COUNTERFACTUAL-001.md) · [V70](phases/MINI-KUZAI-PHASE-03-V70-PRECISION-CONTROL-001.md) · [V70 GOGIT results](reports/assistant-results/history/PHASE03-SMOLTALK-V70-PRECISION-CONTROL-001.json) |
| **V71 - GOGIT verified** | Frozen V62 norm-versus-direction attribution, 30 numeric metrics; 275 changed argmax positions out of 9170 | [V71 research protocol](phases/MINI-KUZAI-PHASE-03-V71-OUTPUT-DOMINANCE-ATTRIBUTION-001.md) · [V71 audit](tools/public-audits/phase03_v71_output_dominance_attribution_001.py) · [V71 tests](tests/test_phase03_v71_output_dominance_attribution_001.py) |
| **V72 - GOGIT verified** | Strong 128D anisotropy: centered PC1 82.88%, effective rank 1.44; mean-center switches 2889/9170 lexical predictions | [V72 protocol and findings](phases/MINI-KUZAI-PHASE-03-V72-HIDDEN-STATE-ANISOTROPY-001.md) · [V72 numeric GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V72-HIDDEN-STATE-ANISOTROPY-001.json) |
| **V73 - GOGIT verified** | PC1 alone yields 2455/9170 correct predictions with only 2 distinct output IDs; removing PC1 yields 1124/9170 correct despite 522 distinct IDs | [V73 findings](phases/MINI-KUZAI-PHASE-03-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.md) · [V73 GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.json) |
| **V74 - CLOSED and delivered** | CORE + STRATA GOGIT verified, 2449/2455 PC1 hits shared with unigram, real START and FINAL published on GitHub and LinkedIn without duplicate | [V74 verified closure](phases/MINI-KUZAI-PHASE-03-V74-FREQUENCY-PRIOR-CONTROL-001.md) · [CORE GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001.json) · [STRATA GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001.json) |
| **V75 - CLOSED and delivered** | TRAIN-fitted PC1 transfers to frozen VALIDATION with 99.95% absolute cosine alignment; scientific GOGIT, GitHub START/FINAL and LinkedIn START/FINAL all verified | [V75 closed findings](phases/MINI-KUZAI-PHASE-03-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.md) · [V75 GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json) · [Discussion #6](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6) |
| **V76 - CLOSED and delivered** | TRAIN frequency explains 7.75% of PC1 output-profile energy; residual retains 92.25% and reaches 2594/9170 correct but remains collapsed to 2 IDs; START/FINAL GitHub and LinkedIn verified | [V76 closed findings](phases/MINI-KUZAI-PHASE-03-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.md) · [V76 GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.json) · [Discussion #7](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/7) |
| **V77 - CLOSED and delivered** | Reverse-history control changed only 5/9170 top-1 predictions; FULL and REVERSE both remained 2594/9170 correct, while alpha correlation stayed at 99.99%; START/FINAL GitHub and LinkedIn verified | [V77 protocol](phases/MINI-KUZAI-PHASE-03-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.md) · [V77 GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.json) · [Discussion #8](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/8) |
| **V78 - SCIENTIFIC CLOSED / GitHub FINAL published** | Identical-input rebatching produced continuous alpha noise but 0/9170 prediction changes, 0 sign changes and identical 2594/9170 correctness; GitHub START/FINAL published, LinkedIn FINAL verification pending | [V78 closed protocol](phases/MINI-KUZAI-PHASE-03-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.md) · [V78 GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.json) · [Discussion #9](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/9) |
| **V79 - CLOSED and delivered** | Same-path batch-32 control reproduced the five V77 prediction/sign changes exactly; ORIGINAL and REVERSE both remained 2594/9170 correct, alpha correlation stayed at 99.99%; GitHub START/FINAL and LinkedIn START/FINAL verified | [V79 protocol](phases/MINI-KUZAI-PHASE-03-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.md) · [V79 GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.json) · [Discussion #10](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/10) |

## Current status - 2026-11-07

| Component | Verified state |
| --- | --- |
| **Hardware** | Ubuntu 24.04 / RTX 5060 Laptop GPU 8 GB |
| **Model** | Decoder-only Transformer, 1,184,512 parameters |
| **Tokenizer** | Byte-BPE, 1024-token vocabulary |
| **Controlled corpus** | 107 TRAIN / 36 VALIDATION / 36 BLIND conversations |
| **Training inventory** | 345 segments, frozen V59 mixture |
| **Checkpoint V62** | Frozen after 69 optimizer steps and 597,982 exposed tokens |
| **V70** | **GOGIT published and verified**, commit [`d239bcf509be`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/d239bcf509be2113ea8d8807487a57ec6116b00f) |
| **VALIDATION cross-entropy** | BF16 original 4.733 / FP32 original 4.732 / HALF 4.892 / FULL 5.048 |
| **Observed limitation** | Only 4-5 distinct original-projection argmax tokens across 9,170 lexical validation positions |
| **Safety** | No new training authorized, V62 unchanged, BLIND remains closed |
| **V71 status** | Read-only GPU GOGIT completed at [commit dcac14ea](https://github.com/Kusanagi8200/Mini-Kuzai/commit/dcac14ea7286642ec0cd9a670dded7fd981bd99c); **275/9170 argmax changed (3.00%)**, 5 to 7 predicted IDs, CE 4.732 to 5.048 |
| **V72 status** | **GPU/GOGIT verified** at [commit `41aed7aef84c`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/41aed7aef84c832e78ae2ac7bfc2f8cd681bd1b7), original lexical top-1 correct 2673, mean-centered 2832; no new training |
| **V73 status** | **GOGIT verified**, [commit `1dcd4e8dc613`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/1dcd4e8dc6138992486f70cdee3620751c4f2940). Removing PC1 changes 6841/9170 argmax decisions and reduces lexical top-1 accuracy from 30.88% to 12.26%. No training / BLIND access |
| **V74 status** | **Dual GOGIT verified**, [CORE `54dace24112f`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/54dace24112f920232cb6106422f6da7ab35d24c) and [STRATA `7b36b3fb18c6`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/7b36b3fb18c6f31037f90ada947b56469f73424f). Frozen TRAIN-unigram baseline outperforms PC1_ONLY by 80 correct predictions; safety gates 0 |
| **V75 status** | **CLOSED**. Scientific GOGIT verified; GitHub FINAL [comment #19458251](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6#discussioncomment-19458251); FINAL receipt commit [`7c1265603ff1`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/7c1265603ff102ebe54d9bd87b845e885c593c8f); KUZ-DIN delivery audit PASS with LinkedIn FINAL `PUBLISHED`, no PREPARED/IN_FLIGHT |
| **V76 status** | **CLOSED**. Scientific GOGIT PASS; residual-energy share 92.25%, residual 2594/9170 correct with 2 predicted IDs; GitHub FINAL [comment #19459204](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/7#discussioncomment-19459204); KUZ-DIN FINAL delivery PASS; no training / BLIND access |
| **V77 status** | **CLOSED**. Scientific GOGIT PASS; only 5/9170 top-1 decisions changed under reverse-history while correctness remained 2594/9170 in both modes; GitHub FINAL [comment #19459823](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/8#discussioncomment-19459823); LinkedIn FINAL `PUBLISHED`; no training / BLIND access |
| **V78 status** | **SCIENTIFIC CLOSED / GitHub FINAL PUBLISHED**. GOGIT PASS with 0 prediction changes and 0 sign changes under identical-input rebatching; [FINAL comment #19461051](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/9#discussioncomment-19461051) and [FINAL receipt](automation/dev-flow/receipts/V78-final.json) verified. LinkedIn FINAL verification pending; no training / BLIND access |
| **V79 status** | **CLOSED**. Scientific GOGIT PASS; same-path ORIGINAL/REVERSE preserved 2594/9170 correctness with exactly 5/9170 prediction changes and 5 alpha-sign changes; GitHub FINAL [comment #19462368](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/10#discussioncomment-19462368); FINAL receipt verified; KUZ-DIN V79 FINAL delivery PASS with valid LinkedIn URN, 0 PREPARED / 0 IN_FLIGHT; no training / BLIND access |
| **V80 status** | **CLOSED AND DELIVERED**. Exact V79 replay preserved 5 prediction/sign changes and 2594/9170 correctness in both modes. None of the changed positions fell within the frozen 1e-3 boundary-proximity threshold; mean boundary distance was 0.030173315 and maximum 0.059604287. GitHub FINAL, LinkedIn FINAL and public YouTube Short are verified. No training / BLIND access. |

**V70-V75 finding -->** V71 equalizing output-head norms changed just 275/9170 lexical predictions. V72 found a centered hidden-state participation ratio of 1.44/128D and PC1 containing 82.88% of centered variance. V73 now shows that **deleting PC1 increases distinct predicted IDs from 15 to 522 but reduces correct predictions from 2832 to 1124**; removing PC1 plus PC2 yields 715 distinct IDs and only 818 correct. **PC1 alone** yields 2455 correct predictions from only 2 predicted IDs. This is an in-sample teacher-forced diagnostic: diversity without preserved accuracy is not useful learning. Keep V62 frozen, do not treat any ablation as a model patch, and do not use BLIND or restart training. V74 confirms that 2449 of 2455 PC1_ONLY correct predictions coincide with a context-free TRAIN unigram baseline, which correctly predicts 2535 tokens. V75 then removes the VALIDATION-fit bias: the independently fitted TRAIN PC1 aligns with VALIDATION PC1 at 99.95% absolute cosine, and TRAIN_PC1_ONLY reproduces essentially the same concentrated behavior (2457 correct, 2 predicted IDs). V76 further shows that TRAIN lexical frequency explains only 7.75% of the centered PC1 output-profile energy; the residual retains 92.25% and reaches 2594 correct predictions, but still collapses to 2 output IDs. V77 found that reversing earlier history changed only 5/9170 top-1 decisions while preserving 2594/9170 correct predictions in both modes, with 99.99% absolute alpha correlation. Because alpha deltas above 1e-7 appeared on 9123 positions although only 9062 prefixes were actually perturbed, V78 measured the numerical floor of the two execution paths using identical logical inputs. V78 found 0/9170 top-1 changes and 0 alpha-sign changes despite measurable continuous alpha noise, so rebatching alone does not explain the five V77 discrete changes. V79 repeated ORIGINAL versus REVERSE_HISTORY_KEEP_LAST through the same prefix scorer and batch 32 and reproduced exactly five prediction changes and five alpha-sign changes. This strengthens evidence that the weak effect is tied to context-order perturbation rather than rebatching alone, but it remains a teacher-forced boundary-sensitive diagnostic and does not establish semantic competence or a causal semantic feature. Keep V62 frozen, BLIND closed and training unauthorized.

## DEV-FLOW and V76 closure - 2026-11-07

V76 is fully closed. The immutable scientific GOGIT is [PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001](reports/assistant-results/history/PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.json).

GitHub START and FINAL are complete on [Discussion #7](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/7). The FINAL is [comment #19459204](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/7#discussioncomment-19459204), with [FINAL receipt](automation/dev-flow/receipts/V76-final.json).

KUZ-DIN verified the exact V76 FINAL delivery as PUBLISHED with a valid LinkedIn URN, active QUEUE/DELIVERY timers, 6 total published DEV-FLOW events and zero PREPARED / IN_FLIGHT rows.

Scientific result --> TRAIN lexical frequency explains 7.75% of the centered PC1 output-profile energy. The orthogonal residual retains 92.25%, reaches 2594/9170 correct frozen VALIDATION predictions and exceeds both the full PC1 replay at 2457 and the TRAIN unigram at 2535. However the residual still predicts only 2 output IDs with a 70.43% dominant share. This is evidence that frequency alone does not explain the stable PC1 profile, not evidence of semantic competence.

V62 remains frozen. `TRAINING_STARTED=0` and BLIND remained closed throughout V76.

The next research item is [V77 Residual Context-Order Sensitivity Control](phases/MINI-KUZAI-PHASE-03-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.md). Its protocol is frozen and START is published in [Discussion #8](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/8), with a verified [START receipt](automation/dev-flow/receipts/V77-start.json). Implementation and CPU-only preflight are prepared. GPU scientific execution is explicitly authorized after the verified V77 CPU preflight. New training, BLIND access and FINAL remain unauthorized.

## V78 closure and V79 preparation - 2026-11-07

V77 is fully closed. The immutable scientific GOGIT is [PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001](reports/assistant-results/history/PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.json).

GitHub START and FINAL are complete on [Discussion #8](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/8). The FINAL is [comment #19459823](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/8#discussioncomment-19459823), with [FINAL receipt](automation/dev-flow/receipts/V77-final.json). KUZ-DIN verified the LinkedIn FINAL as PUBLISHED with a valid URN and no PREPARED / IN_FLIGHT residue.

Scientific result --> reverse-history changed only 5/9170 residual top-1 decisions. FULL and REVERSE both remained 2594/9170 correct, all 2594 correct positions were shared, and alpha correlation remained 99.99%. However, 9123 alpha values moved above 1e-7 while only 9062 prefixes were actually perturbed, so the smallest alpha deltas cannot be attributed exclusively to context order.

The next research item is [V78 Identical-Context Rebatching Numerical Control](phases/MINI-KUZAI-PHASE-03-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.md). Its protocol is frozen and START is published in [Discussion #9](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/9), with a verified [START receipt](automation/dev-flow/receipts/V78-start.json). CPU-only implementation/preflight is authorized. Scientific GPU execution, new training, BLIND access and FINAL remain separately unauthorized.

V78 is scientifically closed. The immutable GOGIT is [PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001](reports/assistant-results/history/PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.json). Identical-input rebatching changed no top-1 decision, no alpha sign and no correctness outcome, while producing measurable continuous alpha deltas.

GitHub FINAL is [comment #19461051](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/9#discussioncomment-19461051), with [FINAL receipt](automation/dev-flow/receipts/V78-final.json). LinkedIn FINAL delivery remains pending independent KUZ-DIN verification.

The next active research item is [V79 Same-Path Context-Order Control](phases/MINI-KUZAI-PHASE-03-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001.md). START is published in [Discussion #10](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/10), with a verified [START receipt](automation/dev-flow/receipts/V79-start.json). Implementation and CPU-only preflight are authorized; GPU scientific execution remains separately unauthorized.

## Code, operations and evidence

| Entry point | Content |
| --- | --- |
| [Model implementations](mini_kuzai/README.md) | Transformer code and model variants |
| [Installation](technical/installation/README.md) | Reference environment and setup |
| [Checkpoint inventory](technical/checkpoints/README.md) | Historical Phase 01 checkpoint metadata |
| [GOGIT](tools/GOGIT.md) | Verified numeric audit publication, immutable history and manual ChatGPT review |
| [GitHub Discussions and KUZ-DIN Publisher](docs/discussions/README.md) | V78 GitHub START/FINAL completed; V79 prepared, not started |
| [DEV-FLOW closure checkpoint](docs/DEV-FLOW-REPRISE-2026-11-01.md) | V74-V78 scientific/GitHub closure; V79 prepared |
| [AUTOPILOT](autopilot/README.md) | Bounded diagnostic campaigns, reproducibility checks and training restrictions |
| [Latest GOGIT report](reports/assistant-results/latest.json) | Most recently published numerical results |
| [Workflow policy](PROJECT-WORKFLOW-POLICY.md) | Fail-closed automation and authorization boundaries |
| [Private-corpus methodology](phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md) | Public process description only - private source data remains local |

## README maintenance

Update this project index **after verified major milestones**, such as a frozen corpus/architecture revision, published GOGIT diagnostic, approved protocol or controlled training stop. Keep the current state, research-step links and next action accurate; preserve detailed methods and older results in their dedicated documents. **Code publication is not execution**, historical authorization is never renewed implicitly, and there is no automatic ChatGPT polling. The enabled local DEV-FLOW worker polls committed explicit requests, and cannot create a research step on its own.

The [original full README snapshot](README-DETAILED-20261031T192526Z.md) preserves the longer chronology, older experiment notes, architecture tables and historical decisions **without rewriting them**. Some historical status blocks there are superseded by the verified V74 status above.

All new training requires a separate, reviewed protocol and explicit authorization. Historical V62 approval does not authorize continuation. No BLIND TEST evaluation is triggered by documentation or GOGIT.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**


## Post-V79 workflow checkpoint - 2026-11-07

V79 is fully closed. Scientific GOGIT, GitHub FINAL receipt/comment and KUZ-DIN LinkedIn delivery audit are verified. The exact FINAL LinkedIn event is `close-V79-d10-c19462368`; KUZ-DIN reports a valid provider URN, active QUEUE/DELIVERY timers, 12 total PUBLISHED DEV-FLOW events, 0 PREPARED and 0 IN_FLIGHT.

No new training is authorized. V62 remains frozen and BLIND remains closed.

Operational rule for subsequent Vxx steps --> `START-DEV-FLOW` and `FINAL-DEV-FLOW` are treated as autonomous end-to-end commands. The flow must create/consume the committed request, verify GitHub publication and receipt, verify KUZ-DIN/LinkedIn delivery through GOGIT, and after a verified FINAL perform a documentation review of both Mini-Kuzai and KUZ-DIN before preparing the next step. Technical tests and deterministic corrections should be looped as far as safely possible inside the frozen scope. When conversation context becomes critical, issue `CONTEXT WARNING - REPRISE RECOMMENDED` early enough to produce a complete resume checkpoint.


## YouTube DEV-FLOW publication

Mini-Kuzai development Shorts are handled by the separate [Mini-Kuzai_YOUTUBE](https://github.com/Kusanagi8200/Mini-Kuzai_YOUTUBE) repository.

Publication boundary -->

- GitHub scientific FINAL remains authoritative
- LinkedIn remains handled independently through KUZ-DIN
- YouTube is FINAL-only and never triggered by START
- the YouTube worker is isolated from the scientific worker
- production OAuth readiness and no-upload preflight are validated
- real Short upload remains gated until a future eligible FINAL-DEV-FLOW
- a YouTube failure never invalidates scientific completion



## V80 full publication closure - 2026-11-11

V80 scientific GOGIT --> PASS.

GitHub FINAL --> Discussion #11 comment #19546266.

FINAL receipt --> `automation/dev-flow/receipts/V80-final.json`, status `PUBLISHED`.

LinkedIn FINAL --> event `close-V80-d11-c19546266`, status `PUBLISHED`, provider URN `urn:li:share:7526323656042455041`.

YouTube FINAL --> public Short `y-YnlPLbT9Q`, worker state `PUBLIC_PUBLISHED`.

Verified media SHA256 --> `f2788466831c8f17886df4a531fad058e1f18d8aa02adcdeb14f08f4e13a8ca6`.

V80 therefore validates the first real GitHub + LinkedIn + YouTube FINAL publication flow.

The V80 video remains an immutable historical 10-50 second narration-window artifact.

For V81+ the media contract changes to a 5-55 second narration window. Before V81 scientific work advances, the non-scientific `FLOW-PRESENTATION-001` publication is used to validate the extended media path:

```text
verified MP4
  -> YouTube public
  -> LinkedIn native video
  -> GitHub media publication / YouTube fallback
  -> publication verification
  -> documentation update
```

This presentation test is communication infrastructure only. It is not V81 scientific evidence and does not authorize training, optimizer steps, checkpoint mutation or BLIND access.



## Pre-V81 cross-channel media validation - completed

`FLOW-PRESENTATION-001` validated the extended media path before V81.

Verified result -->

- media SHA256 --> `c34b3dc19788e6770e4edb9dffc2331df2438b23c6663858b7d5299ad5731034`
- 60-second Short
- narration window --> 5-55 seconds
- YouTube --> PUBLIC, video ID `vhQmddUuMcg`
- LinkedIn --> native video PUBLISHED, post URN `urn:li:ugcPost:7526340708715327488`
- GitHub --> Discussion #12, using the verified public YouTube media fallback

Discussion #12 -->

https://github.com/Kusanagi8200/Mini-Kuzai/discussions/12

This test is communication infrastructure only. It is not V81 scientific evidence.

The remaining V81 engineering objective is orchestration: once a genuine V81 FINAL receipt exists, the validated media path should execute automatically without manual transfer or publication commands.

