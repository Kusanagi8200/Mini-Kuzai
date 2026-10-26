# MINI-KUZAI PHASE 03 - V59 TRAINING MIX AND SEGMENTATION

Status --> **PAUSED CLEAN - SEGMENTATION CLOSED - PUBLIC MIX NOT FINALIZED**

V59 is the final data-preparation workstream before any model-training
authorization decision.

Training remains **NOT AUTHORIZED / NOT STARTED**.

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

## Resume point

Next authorized workstream -->

**V59 TRIAGE RETRAIN + INDEPENDENT HOLDOUT 004**

Requirements -->

1. train the next triage ranking using all **216 reviewed annotations**
2. select a new independent holdout from previously unreviewed candidates
3. do not reuse Sample 003 as the independent validation set because Sample 003
   was selected from the previous model ranking;
4. evaluate ranking usefulness separately from probability calibration
5. keep automatic filtering unauthorized unless a later explicit gate passes.

After independent validation, V59 still must -->

1. decide the final KEEP / REPAIR / EXCLUDE review policy
2. finalize the public corpus
3. compute final post-filter segment and token counts
4. define controlled-persona versus public-data sampling / weighting
5. reassess the V58 data-to-parameter ratio
6. make a separate explicit model-training authorization decision.

Training remains **NOT AUTHORIZED / NOT STARTED**.

## References

- [V59 pause checkpoint - 2026-10-25](MINI-KUZAI-PHASE-03-V59-PAUSE-CHECKPOINT-2026-10-25.md)
- [Sample 001 results](../reviews/smoltalk-v59-bulk-sample-001/RESULTS-001.md)
- [Sample 002 results](../reviews/smoltalk-v59-bulk-sample-002/RESULTS-002.md)
- [Filter-rule mining results](../reviews/smoltalk-v59-filter-rule-mining/RESULTS-001.md)
- [Supervised triage results](../reviews/smoltalk-v59-supervised-triage/RESULTS-001.md)
- [Active-Learning Sample 003 results](../reviews/smoltalk-v59-active-sample-003/RESULTS-003.md)
- [Active-Learning Sample 003 GOGIT audit](../reports/assistant-results/history/PHASE03-SMOLTALK-V59-ACTIVE-SAMPLE-003.json)

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
