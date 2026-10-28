# MINI-KUZAI PHASE 03 - V59 TRAINING MIX AND SEGMENTATION

Status --> **CLOSED - FINAL MIX FROZEN - PERSISTENT TRAINER FROZEN - RUNTIME VERIFIED - TRAINING NOT STARTED**

V59 data preparation is complete. The public mixture, persona-first exposure
policy, tokenizer, serialization, segmentation, architecture and bounded pilot
protocol are frozen under one terminal authorization manifest.

Training is **AUTHORIZED FOR THE V59 BOUNDED PILOT ONLY / NOT STARTED**.

## Scope

V59 must produce an explicit, reproducible public training-data plan while
preserving -->

- the frozen TRAIN / VALIDATION / BLIND boundary
- source provenance
- duplicate and semantic-split protection
- frozen V56 tokenizer behavior
- frozen V57 serialization
- V58 experimental architecture reproducibility
- the persona-first quality policy
- the rule that known incorrect positive targets cannot be trained unchanged.

## Frozen controlled baseline

The controlled corpus remains unchanged -->

- TRAIN --> **107 records / 29 groups**
- VALIDATION --> **36 records / 18 groups - FROZEN**
- BLIND TEST --> **36 records / 18 groups - FROZEN**
- total --> **179 conversations / 65 semantic groups**.

TRAIN provenance -->

- 105 `phase03-designed`
- 2 admitted public SmolTalk derivatives.

Tokenizer -->

- V56 `byte_bpe_whitespace`
- vocabulary 1024
- 765 merges
- byte fallback
- no UNK.

Conversation serialization -->

- V57 frozen
- ordinary textual `USER:` and `MINI-KUZAI:` labels
- BOS at conversation start
- EOS at conversation end.

Architecture baseline -->

- V58 decoder-only autoregressive Transformer
- context 2048
- `d_model=128`
- 4 heads
- 4 layers
- FFN 512
- **1,184,512 parameters**.

V58 remains an experimental baseline rather than an irreversible final
architecture decision.

## V59 segmentation - CLOSED

The V59 segmentation policy is implemented, tested and frozen.

Policy -->

- preserve complete USER / MINI-KUZAI pairs
- cut only between complete pairs
- greedy packing up to 2048 tokens
- preserve source text and order
- no truncation
- no silent intra-message split
- no silent intra-pair split
- block an individual pair that cannot fit within 2048 tokens.

Controlled TRAIN -->

- 107 conversations
- 107 segments
- 0 blocked pairs.

Public oversized-pair review -->

- 10 blocked public cases reviewed
- 8 EXCLUDE
- 2 REPLACE
- both replacement behaviors already existed in suitable public candidates
- no duplicate replacement was added
- no arbitrary special split policy was introduced.

Segmentation is no longer a pre-training blocker.

## V59 public candidate population

Starting V44 population -->

- **1,139 conversations**.

V59 removes -->

- 3 sources containing incompatible >2048-token complete pairs
- 2 public source SHAs already represented by controlled TRAIN derivatives
- 22 unique structured known-negative V51/V52 sources.

Resulting V59 public candidate population -->

- **1,112 conversations**
- **1,554 turn-aware segments**
- **1,730,414 public tokens**
- public tokens / model parameter --> **1.460**
- controlled TRAIN + public tokens --> **1,754,953**
- combined tokens / model parameter --> **1.481**.

Within these 1,112 candidates -->

- 32 had already passed structured V51/V52 review
- 1,080 formed the V59 bulk quality-estimation population.

## Bulk quality Sample 001 - CLOSED

Sample 001 -->

- reviewed --> 72
- KEEP --> 36
- REPAIR --> 19
- EXCLUDE --> 17
- factual risk HIGH --> 18
- instruction fit BAD --> 9.

Initial weighted diagnostic -->

- KEEP --> 52.00%
- REPAIR --> 26.95%
- EXCLUDE --> 21.05%
- unchanged-unsuitable --> 48.00%.

This sample established that V50 HIGH / MEDIUM / LOW priority is not a quality
grade.

## Bulk quality Sample 002 - CLOSED

Sample 002 added 72 new public cases with zero Sample 001 overlap and rebalanced
the cumulative sample toward the real sizes of the 10 observed
priority x source x turn strata.

Sample 002 -->

- KEEP --> 35
- REPAIR --> 20
- EXCLUDE --> 17.

Structured defect tags were added -->

- NONE
- ROLE_CONTAMINATION
- FACTUAL_ERROR
- LOGICAL_ERROR
- TECHNICAL_ERROR
- INSTRUCTION_FAILURE
- TIME_SENSITIVE
- STYLE_QUALITY
- OTHER.

## Cumulative bulk-quality gate - FAILED

Samples 001 + 002 -->

- **144 unique reviewed cases**
- raw KEEP --> 71
- raw REPAIR --> 39
- raw EXCLUDE --> 34.

Weighted diagnostic over the 1,080-case bulk -->

- KEEP --> **49.36%**
- REPAIR --> **27.61%**
- EXCLUDE --> **23.03%**
- unchanged-unsuitable --> **50.64%**
- approximate diagnostic interval for unchanged-unsuitable -->
  **42.79% to 58.49%**;
- weighted factual-risk HIGH --> **21.59%**
- weighted instruction-fit BAD --> **12.89%**
- effective weighted sample size --> approximately 139.2 / 144.

Conclusion -->

**UNCHANGED BULK ADMISSION FAILED.**

The broad V44-derived public bulk cannot be promoted unchanged as positive
supervised training data.

The cumulative audit remains a diagnostic rather than a formal probability
sample because the sampling designs are deterministic.

## Filter-rule mining 001 - CLOSED / LOW RECALL

Simple metadata and text-structure predicates were mined using a deterministic
discovery / holdout split over the 144 reviewed examples.

111 candidate rules were tested.

Only one rule passed the high-precision REPAIR/EXCLUDE gate -->

`PRIORITY=HIGH AND TIME_SENSITIVE_LANGUAGE`

Holdout -->

- precision --> **85.7%**
- recall --> **17.1%**
- flagged --> 7.

Projection -->

- 87 / 1,080 candidates flagged.

No simple rule passed the EXCLUDE gate.

Conclusion -->

- narrow high-precision review triage is possible
- simple rules do not provide enough recall for broad filtering
- automatic exclusion is not supported.

Rule application remains **NOT AUTHORIZED**.

## Supervised text triage 001 - CLOSED / GATE FAILED

A lightweight local multinomial Naive Bayes model used -->

- role-separated USER / ASSISTANT word unigrams and bigrams
- V44/V50 metadata
- five-fold stratified cross-validation
- only public reviewed data
- no external LLM or private corpus.

REPAIR / EXCLUDE target -->

- precision --> **60.3%**
- recall --> **52.1%**
- F1 --> **55.9%**
- TP 38
- FP 25
- FN 35.

Authorization gate --> **FAILED**.

EXCLUDE target -->

- precision --> **16.7%**
- recall --> **8.8%**
- F1 --> **11.5%**
- TP 3
- FP 15
- FN 31.

Authorization gate --> **FAILED**.

The model produced extreme scores despite poor cross-validation performance, so
its numeric output is explicitly treated as **uncalibrated ranking only**.

Automatic REVIEW --> **NOT AUTHORIZED**.

Automatic EXCLUDE --> **NOT AUTHORIZED**.

## Active-Learning Sample 003 - CLOSED

The failed supervised triage was used only to construct a 72-case active
challenge set from previously unreviewed public candidates.

Sample design -->

- 18 HIGH_RISK_RANK
- 18 MIDDLE_RANK
- 18 LOW_RISK_RANK
- 18 DIVERSITY_CONTROL.

Sample 003 is **not** a population-prevalence estimator.

Review result -->

| Bucket | KEEP | REPAIR | EXCLUDE | Unchanged unsuitable |
| --- | ---: | ---: | ---: | ---: |
| HIGH_RISK_RANK | 2 | 15 | 1 | 88.9% |
| MIDDLE_RANK | 10 | 6 | 2 | 44.4% |
| LOW_RISK_RANK | 18 | 0 | 0 | 0.0% |
| DIVERSITY_CONTROL | 11 | 3 | 4 | 38.9% |

Overall -->

- KEEP --> 41
- REPAIR --> 24
- EXCLUDE --> 7.

Total V59 public semantic reviews after Sample 003 -->

- **216 conversations**.

Audit result -->

- ranking direction --> **VALIDATED**
- triage retrain --> **AUTHORIZED**
- automatic filtering --> **NOT AUTHORIZED**.

Interpretation -->

The first classifier is not reliable enough for automatic classification, but
its ordering signal is useful for prioritizing human review. A high score must
not be interpreted as a probability of being bad.

## Persona-first mixture policy

The final public mixture must support the Mini-Kuzai persona rather than maximize
generic technical breadth.

Priority behaviors -->

- identity and character continuity
- curiosity
- uncertainty
- critical thinking
- reasoned disagreement
- opinion formation and revision
- creativity and storytelling
- initiative
- multi-turn contextual adaptation
- correction after user feedback.

Specialist IT or technical competence is secondary.

However -->

**known incorrect supervised targets must be repaired or excluded.**

A technically imperfect example may still contain valuable behavioral structure,
but that does not justify teaching a false answer as correct.

## Data-balance problem still unresolved

Controlled TRAIN contains only **24,539 serialized tokens**.

The broad V59 public candidate population contains approximately **1.73 million
tokens** before final quality filtering.

A simple concatenation would therefore drown the controlled Mini-Kuzai persona
signal.

Before model training, V59 must explicitly define sampling, weighting or epoch
policy that preserves controlled persona influence.

Repeated epochs increase exposure; they do not increase unique-data volume.

## Pause checkpoint - 2026-10-25

Current state -->

```text
V59 segmentation             : CLOSED
Oversized-pair review        : CLOSED
Replacement validation       : CLOSED
Known-negative filtering     : CLOSED

Bulk Sample 001              : CLOSED
Bulk Sample 002              : CLOSED
Cumulative bulk gate         : FAILED
Filter-rule mining 001       : CLOSED / LOW RECALL
Supervised triage 001        : CLOSED / GATE FAILED
Active-Learning Sample 003   : CLOSED

Public semantic reviews      : 216
Ranking direction            : VALIDATED
Triage retrain               : AUTHORIZED / NOT STARTED

Automatic REVIEW             : NOT AUTHORIZED
Automatic EXCLUDE            : NOT AUTHORIZED

V59 final public mix         : NOT FINALIZED
Model training               : NOT STARTED
Model training authorized    : NO
```

## V59 triage retrain + independent holdout 004

Status --> **CLOSED / INDEPENDENT RANKING GATE FAILED**

Retraining used the **216 annotations** from Samples 001, 002 and 003.

Holdout 004 -->

- 72 conversations
- selected from 864 never-reviewed candidates
- deterministic priority x source x turn stratification
- model score not used for selection
- model scores blinded during semantic review
- semantic result --> 43 KEEP / 23 REPAIR / 6 EXCLUDE
- reviewed total after application --> **288**
- never-reviewed remainder --> **792**.

Independent REPAIR / EXCLUDE ranking -->

- AUC --> **0.595**
- top 18 unchanged-unsuitable --> **55.6%**
- bottom 18 unchanged-unsuitable --> **22.2%**
- top-minus-bottom gradient --> **33.3 percentage points**
- ranking gate --> **FAILED**.

Diagnostic threshold 0.75 -->

- precision --> **44.7%**
- recall --> **72.4%**
- F1 --> **55.3%**.

Independent EXCLUDE ranking -->

- AUC --> **0.664**
- diagnostic precision at 0.90 --> **12.5%**
- diagnostic recall at 0.90 --> **33.3%**
- diagnostic F1 --> **18.2%**.

Conclusion -->

The Naive-Bayes ranking does not generalize strongly enough to drive automatic
or ranking-priority corpus selection. Sample 003 demonstrated useful enrichment
inside a model-selected challenge set, but Holdout 004 shows that the effect is
not strong enough on an independent sample.

Therefore -->

- ranking-priority authorization --> **NO**
- automatic REVIEW --> **NOT AUTHORIZED**
- automatic EXCLUDE --> **NOT AUTHORIZED**
- further Naive-Bayes retraining --> **NOT REQUIRED FOR V59 MIX SELECTION**.

GOGIT step -->

`PHASE03-SMOLTALK-V59-TRIAGE-RETRAIN-HOLDOUT-004`

## V59 final mix policy / persona-first pruning

Status --> **CLOSED / POLICY DEFINED / MIX WEIGHTING STILL REQUIRED**

Conservative policy result -->

| Bucket | Conversations | Segments | Tokens |
| --- | ---: | ---: | ---: |
| DIRECT_KEEP | 165 | 238 | 270877 |
| REPAIR_QUEUE | 108 | 161 | 198226 |
| EXCLUDE_REVIEWED | 47 | 61 | 56726 |
| DEFER_UNREVIEWED | 792 | 1094 | 1204585 |

DIRECT_KEEP composition -->

- PERSONA_CORE --> **86 conversations**
- GENERAL_SUPPORT --> **68 conversations**
- LEGACY_STRUCTURED_KEEP --> **11 conversations**.

One historical KEEP with factual risk REVIEW is conservatively redirected out
of direct admission.

Ready-now clean envelope -->

- controlled TRAIN tokens --> **24539**
- clean reviewed public tokens --> **270877**
- combined clean tokens --> **295416**
- combined clean tokens / V58 parameter --> approximately **0.249**.

Guardrails -->

- automatic filtering used --> **NO**
- unreviewed public data admitted --> **NO**
- REPAIR admitted unchanged --> **NO**
- V59 final mix --> **NOT FINALIZED**
- model training --> **NOT AUTHORIZED / NOT STARTED**.

GOGIT step -->

`PHASE03-SMOLTALK-V59-FINAL-MIX-POLICY-001`

## V59 persona-first mix weighting / exposure policy

Status --> **CLOSED / EXPOSURE POLICY FINALIZED**

Unique clean streams -->

| Stream | Conversations | Segments | Unique tokens | Raw share | Target share |
| --- | ---: | ---: | ---: | ---: | ---: |
| CONTROLLED_TRAIN | 107 | 107 | 24539 | 8.31% | **30.00%** |
| PERSONA_CORE | 86 | 142 | 182787 | 61.87% | **46.58%** |
| GENERAL_SUPPORT | 68 | 76 | 63213 | 21.40% | **15.00%** |
| LEGACY_STRUCTURED_KEEP | 11 | 20 | 24877 | 8.42% | **8.42%** |

Persona-oriented exposure -->

**CONTROLLED_TRAIN + PERSONA_CORE = 76.58%**

Reference exposure cycle -->

**295416 tokens**

Equivalent exposure passes per reference cycle -->

- CONTROLLED_TRAIN --> **3.612x**
- PERSONA_CORE --> **0.753x**
- GENERAL_SUPPORT --> **0.701x**
- LEGACY_STRUCTURED_KEEP --> **1.000x**.

Sampler -->

- sampling unit --> SEGMENT_STREAM
- target basis --> TOKEN_EXPOSURE_SHARE
- with replacement --> YES
- shuffle within stream --> YES
- physical duplication --> NO.

Guardrails -->

- REPAIR_QUEUE admitted --> NO
- EXCLUDE_REVIEWED admitted --> NO
- DEFER_UNREVIEWED admitted --> NO
- model training authorized --> NO.

GOGIT step -->

`PHASE03-SMOLTALK-V59-PERSONA-EXPOSURE-POLICY-001`

## V59 training hyperparameters / step budget / authorization preflight

Status --> **CLOSED / PREFLIGHT PASSED / AUTHORIZATION CANDIDATE**

Frozen pilot protocol -->

- model --> V58 MICRO
- parameters --> **1184512**
- dtype --> **BF16**
- optimizer --> **AdamW**
- learning rate --> **3e-4**
- minimum learning rate --> **3e-5**
- betas --> **0.9 / 0.95**
- eps --> **1e-8**
- weight decay --> **0.10**
- gradient clip --> **1.0**
- seed --> **42**
- optimizer-step target --> **8192 non-pad tokens**
- pilot exposure cycles --> **4**
- maximum exposure tokens --> **1181664**
- maximum optimizer steps --> **145**
- warmup steps --> **15**
- scheduler --> linear warmup + cosine decay.

Hardware preflight result -->

- CUDA / BF16 --> PASS
- GPU --> NVIDIA GeForce RTX 5060 Laptop GPU
- full-context microbatch --> 8 x 2048
- finite loss --> YES
- finite gradient norm --> YES
- peak allocated --> **564 MiB**
- peak reserved --> **632 MiB**
- total GPU memory --> **7705 MiB**
- reserved share --> **8.20%**
- memory gate --> **60.00%**
- authorization candidate --> **YES**.

Training remains not started.

GOGIT step -->

`PHASE03-SMOLTALK-V59-TRAINING-PROTOCOL-PREFLIGHT-001`

## V59 final mix freeze + training authorization gate

Status --> **CLOSED / PASSED / BOUNDED PILOT AUTHORIZED**

Terminal GOGIT step -->

`PHASE03-SMOLTALK-V59-FINAL-MIX-FREEZE-AUTHORIZATION-001`

Terminal state -->

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

Frozen training identity -->

- controlled TRAIN --> **107 conversations / 29 semantic groups**
- clean public DIRECT_KEEP --> **165 conversations**
- total training conversations --> **272**
- total unique training segments --> **345**
- total unique clean tokens --> **295416**.

Frozen exposure targets -->

- CONTROLLED_TRAIN --> **30.00%**
- PERSONA_CORE --> **46.58%**
- GENERAL_SUPPORT --> **15.00%**
- LEGACY_STRUCTURED_KEEP --> **8.42%**
- persona-oriented exposure --> **76.58%**.

Explicitly outside the authorized pilot -->

- REPAIR_QUEUE --> **108 conversations**
- EXCLUDE_REVIEWED --> **47 conversations**
- DEFER_UNREVIEWED --> **792 conversations**.

Frozen dependency identity includes SHA-256 fingerprints for -->

- all 19 canonical TRAIN JSONL files
- DIRECT_KEEP source inventory
- V56 tokenizer manifest and tokenizer artifact
- V57 serialization source
- V59 segmentation source
- V58 architecture manifest, config and model source
- final public-mix policy
- persona-first exposure report and sampler policy
- bounded training protocol and hardware-preflight report
- V54 VALIDATION master
- V55 BLIND master
- semantic split manifest.

Authorized pilot limits -->

- architecture --> **V58 MICRO FROZEN**
- dtype --> BF16
- optimizer --> AdamW
- base learning rate --> 3e-4
- minimum learning rate --> 3e-5
- gradient clip --> 1.0
- target non-pad tokens / optimizer step --> 8192
- maximum optimizer steps --> **145**
- maximum exposure tokens --> **1181664**
- reference exposure cycles --> **4**
- VALIDATION --> allowed
- BLIND TEST during training --> **FORBIDDEN**
- BLIND TEST --> reserved for post-training evaluation.

The authorization is invalidated by any corpus, tokenizer, serializer,
segmentation, architecture, exposure-policy or protocol change.

Training has **not** started.

## V59 persistent bounded-pilot trainer - FROZEN / VERIFIED

The persistent trainer is implemented, tested, frozen and published.

Terminal GOGIT step -->

`PHASE03-SMOLTALK-V59-PERSISTENT-TRAINER-FREEZE-001`

Trainer freeze fingerprint -->

`d71fb0fe6e71cbfd46ae06a88ef994b91091c698b8f401237387b5fc7ebe3a84`

Frozen trainer state -->

- trainer implemented --> **YES**
- trainer frozen --> **YES**
- Python compilation --> **PASS**
- unit tests --> **PASS**
- full runtime verification --> **PASS**
- TRAIN segments reconstructed --> **345**
- TRAIN unique tokens reconstructed --> **295416**
- VALIDATION records --> **36**
- VALIDATION segments --> **36**
- VALIDATION tokens --> **9242**
- BLIND TEST access --> **0**
- resume support --> **YES**
- optimizer state checkpointing --> **YES**
- scheduler state checkpointing --> **YES**
- RNG state checkpointing --> **YES**
- sampler state checkpointing --> **YES**
- TRAINING_STARTED --> **0**

Frozen schedule preview -->

- completed sampler cycles --> **4**
- preview segments --> **2263**
- preview exposure tokens --> **1181302**
- maximum authorized exposure tokens --> **1181664**
- maximum stream-share deviation --> **4 basis points**
- maximum optimizer steps --> **145**

The final runtime-only verification also passed on
**NVIDIA GeForce RTX 5060 Laptop GPU**. The canonical run directory
`/root/Mini-Kuzai/runs/v59-bounded-pilot-001` was confirmed absent before the
first real run, so no previous manifest, checkpoint or lock can be resumed
accidentally.

### V54 declaration compatibility discovered during trainer freeze

The trainer initially exposed schema differences between the historical V54
VALIDATION freeze declarations and the stricter V59 runtime checks.

The compatibility path is fail-closed -->

- all **18 VALIDATION declarations** are required
- all **18 historical V54 GOGIT freeze proofs** are required
- all **18 target Git blob identities** must match
- explicit false integrity or review state remains a hard failure
- legacy review-field naming is accepted only when the corresponding immutable
  GOGIT freeze proof is valid
- no VALIDATION corpus file was rewritten

GOGIT compatibility step -->

`PHASE03-SMOLTALK-V59-VALIDATION-COMPATIBILITY-001`

### Frozen-dependency performance experiment

A segmentation token-count cache was tested after a bounded synthetic benchmark
showed redundant tokenization cost. The experimental implementation improved the
synthetic timings, but it changed the frozen segmentation source fingerprint.

The optimization was therefore **reverted** before trainer freeze.

The authorized V59 bounded pilot continues to use the original frozen
segmentation dependency. Performance improvements may be reconsidered only in a
future version with a new authorization freeze.

## Current execution boundary

All data, authorization, trainer-freeze and runtime gates required before the
first optimizer step are now closed.

The next V59 operation is -->

**START THE FIRST REAL V59 BOUNDED PILOT TRAINING RUN**

The first run must use the frozen trainer without `--resume`. BLIND TEST remains
forbidden during training.

Checkpoint -->

[V59 training-authorized checkpoint - 2026-10-28](MINI-KUZAI-PHASE-03-V59-TRAINING-AUTHORIZED-CHECKPOINT-2026-10-28.md)

## References

- [V59 training-authorized checkpoint - 2026-10-28](MINI-KUZAI-PHASE-03-V59-TRAINING-AUTHORIZED-CHECKPOINT-2026-10-28.md)
- [V59 final authorization results](../reviews/smoltalk-v59-final-mix-freeze-authorization/RESULTS-001.md)
- [V59 terminal authorization GOGIT audit](../reports/assistant-results/history/PHASE03-SMOLTALK-V59-FINAL-MIX-FREEZE-AUTHORIZATION-001.json)
- [V59 persistent trainer freeze results](../reviews/smoltalk-v59-persistent-trainer-freeze/RESULTS-001.md)
- [V59 persistent trainer GOGIT audit](../reports/assistant-results/history/PHASE03-SMOLTALK-V59-PERSISTENT-TRAINER-FREEZE-001.json)
- [V59 validation compatibility GOGIT audit](../reports/assistant-results/history/PHASE03-SMOLTALK-V59-VALIDATION-COMPATIBILITY-001.json)
- [V59 pause checkpoint - 2026-10-25](MINI-KUZAI-PHASE-03-V59-PAUSE-CHECKPOINT-2026-10-25.md)
- [Sample 001 results](../reviews/smoltalk-v59-bulk-sample-001/RESULTS-001.md)
- [Sample 002 results](../reviews/smoltalk-v59-bulk-sample-002/RESULTS-002.md)
- [Filter-rule mining results](../reviews/smoltalk-v59-filter-rule-mining/RESULTS-001.md)
- [Supervised triage results](../reviews/smoltalk-v59-supervised-triage/RESULTS-001.md)
- [Active-Learning Sample 003 results](../reviews/smoltalk-v59-active-sample-003/RESULTS-003.md)
- [Active-Learning Sample 003 GOGIT audit](../reports/assistant-results/history/PHASE03-SMOLTALK-V59-ACTIVE-SAMPLE-003.json)

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
