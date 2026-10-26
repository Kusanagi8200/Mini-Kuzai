# MINI-KUZAI PHASE 03 - V59 PAUSE CHECKPOINT - 2026-10-25

Status --> **PAUSED CLEAN - V59 PUBLIC MIX QUALITY WORK IN PROGRESS**

This checkpoint records the project state after completion of V59 active-learning
Sample 003. It is a pause point only. It does not authorize training and does
not finalize the public training mixture.

## Controlled corpus

The controlled Mini-Kuzai corpus remains frozen and unchanged -->

- TRAIN --> **107 records / 29 semantic groups**
- VALIDATION --> **36 records / 18 groups - FROZEN**
- BLIND TEST --> **36 records / 18 groups - FROZEN**
- total controlled corpus --> **179 conversations / 65 semantic groups**
- cross-split exact ID collisions --> **0**
- cross-split semantic-group overlap --> **0**
- exact cross-split prompt collisions --> **0**.

TRAIN provenance remains -->

- 105 Phase 03 designed records
- 2 admitted public SmolTalk derivatives.

## Frozen tokenizer, serializer and architecture baseline

- V56 tokenizer --> **FROZEN**
- tokenizer family --> `byte_bpe_whitespace`
- vocabulary --> **1024**
- merge rules --> **765**
- byte fallback --> enabled
- UNK token --> none.

- V57 conversation serialization v1 --> **FROZEN**
- ordinary textual `USER:` and `MINI-KUZAI:` role labels
- BOS at conversation start
- EOS at conversation end.

- V58 architecture baseline --> **FROZEN EXPERIMENTAL BASELINE**
- decoder-only autoregressive Transformer
- context --> **2048**
- `d_model=128`
- 4 attention heads
- 4 Transformer layers
- FFN dimension 512
- parameters --> **1,184,512**.

The V58 baseline remains experimental and is not an irreversible final model-size
decision.

## V59 segmentation

V59 turn-aware segmentation is **CLOSED**.

Policy -->

- preserve complete USER / MINI-KUZAI pairs
- split only between complete pairs
- greedy packing up to 2048 tokens
- no truncation
- no silent intra-message or intra-pair split
- block an individual pair that cannot fit.

Controlled TRAIN has no blocked pair.

Public oversized-pair review is closed -->

- 10 blocked public cases reviewed
- 8 excluded
- 2 behavioral replacements validated through already-present candidates
- no special arbitrary split policy introduced.

## V59 public candidate population

Starting V44 provisional population -->

- 1,139 conversations.

After structural exclusions, controlled-source reuse protection and known-negative
V51/V52 filtering -->

- V59 public candidate population --> **1,112 conversations**
- turn-aware segments --> **1,554**
- public tokens --> **1,730,414**
- public token / parameter ratio --> **1.460**
- controlled TRAIN + public tokens --> **1,754,953**
- combined token / parameter ratio --> **1.481**.

Of the 1,112 candidates -->

- 32 had prior structured V51/V52 review
- 1,080 formed the bulk population used for V59 quality estimation.

## Bulk quality Samples 001 and 002

Sample 001 -->

- 72 reviewed
- KEEP 36
- REPAIR 19
- EXCLUDE 17.

Sample 002 -->

- 72 reviewed
- KEEP 35
- REPAIR 20
- EXCLUDE 17.

Cumulative reviewed quality sample -->

- **144 unique cases**
- raw KEEP 71
- raw REPAIR 39
- raw EXCLUDE 34.

Stratum-weighted diagnostic over the 1,080-case population -->

- KEEP --> **49.36%**
- REPAIR --> **27.61%**
- EXCLUDE --> **23.03%**
- unchanged-unsuitable = REPAIR + EXCLUDE --> **50.64%**
- approximate 95% diagnostic interval for unchanged-unsuitable -->
  **42.79% to 58.49%**;
- weighted factual-risk HIGH --> **21.59%**
- weighted instruction-fit BAD --> **12.89%**.

Conclusion -->

**UNCHANGED BULK ADMISSION FAILED.**

The V44-derived public bulk must not be promoted unchanged into positive
supervised training.

## Simple filter-rule mining

V59 filter-rule mining tested simple metadata/text-structure predicates using a
deterministic discovery/holdout split over the 144 reviewed cases.

Only one high-precision rule survived -->

`PRIORITY=HIGH AND TIME_SENSITIVE_LANGUAGE`

Holdout performance -->

- precision --> **85.7%**
- recall --> **17.1%**
- holdout flagged --> 7
- projected population flagged --> 87.

Conclusion -->

- high-precision triage is possible for a narrow subset
- simple rules do not provide sufficient recall for broad filtering
- automatic EXCLUDE is not supported.

## Supervised text triage 001

A local multinomial Naive Bayes text classifier was evaluated with five-fold
stratified cross-validation on the 144 reviewed examples.

REPAIR / EXCLUDE target -->

- precision --> **60.3%**
- recall --> **52.1%**
- F1 --> **55.9%**
- projected flagged among then-unreviewed candidates --> 473.

EXCLUDE target -->

- precision --> **16.7%**
- recall --> **8.8%**
- F1 --> **11.5%**
- projected exclusions --> 131.

Both authorization gates failed.

Conclusion -->

- classifier probabilities are not calibrated
- automatic REVIEW is not authorized
- automatic EXCLUDE is not authorized
- the ranking may still contain useful ordering information.

## Active-learning Sample 003

Sample 003 used the failed classifier only as an **uncalibrated ranking signal**
to select a 72-case challenge set. It is not a population-prevalence estimator.

Selection -->

- 18 HIGH_RISK_RANK
- 18 MIDDLE_RANK
- 18 LOW_RISK_RANK
- 18 DIVERSITY_CONTROL.

Review results -->

| Bucket | KEEP | REPAIR | EXCLUDE | Unchanged unsuitable |
| --- | ---: | ---: | ---: | ---: |
| HIGH_RISK_RANK | 2 | 15 | 1 | 16/18 = 88.9% |
| MIDDLE_RANK | 10 | 6 | 2 | 8/18 = 44.4% |
| LOW_RISK_RANK | 18 | 0 | 0 | 0/18 = 0.0% |
| DIVERSITY_CONTROL | 11 | 3 | 4 | 7/18 = 38.9% |

Overall Sample 003 -->

- KEEP --> 41
- REPAIR --> 24
- EXCLUDE --> 7.

Total public cases semantically reviewed by the current V59 quality-control
sequence -->

- **216 conversations**.

The Sample 003 audit concluded -->

- ranking direction --> **VALIDATED**
- triage retraining --> **AUTHORIZED**
- automatic filtering --> **NOT AUTHORIZED**.

The ranking is useful for prioritization, but its score must not be interpreted
as a probability.

## Persona-first training-data policy

The project continues to prioritize -->

- identity and character continuity
- curiosity
- uncertainty
- critical thinking
- opinion formation and revision
- creativity and storytelling
- multi-turn contextual adaptation
- useful correction after feedback.

Specialist IT or technical expertise remains secondary.

However -->

**a known incorrect answer must never be used unchanged as a correct supervised
target.**

Technical or factual weakness can lower the importance of an example without
making the persona goal itself invalid, but incorrect positive targets require
repair or exclusion.

## Unresolved pre-training work

At this pause point, the controlled corpus, tokenizer, serializer, architecture
baseline and segmentation policy are ready.

The unresolved boundary is the **public training mixture**.

Still required -->

1. retrain the V59 triage using the **216 reviewed annotations**
2. evaluate the retrained ranking on a **new independent holdout** selected from
   the remaining public candidates;
3. decide how ranking information will be used for human review prioritization
4. determine the final KEEP / REPAIR / EXCLUDE policy for the public bulk
5. produce the final public-corpus manifest and post-filter token accounting
6. define sampling / weighting so the 24,539-token controlled persona corpus is
   not drowned by the much larger public corpus;
7. reassess the final data-to-parameter ratio against V58
8. perform an explicit model-training authorization decision.

## Resume point

Next planned workstream -->

**V59 TRIAGE RETRAIN + INDEPENDENT HOLDOUT 004**

State at pause -->

```text
Phase 03                     : PAUSED CLEAN
V59 segmentation             : CLOSED
Controlled corpus            : CLOSED / FROZEN
Tokenizer                    : V56 FROZEN
Serializer                   : V57 FROZEN
Architecture                 : V58 EXPERIMENTAL BASELINE FROZEN

V59 public candidates        : 1112
V59 bulk estimation pop.     : 1080
Public cases reviewed        : 216

Unchanged bulk admission     : FAILED
Simple rule mining           : CLOSED / LOW RECALL
Supervised triage 001        : CLOSED / GATE FAILED
Active-learning Sample 003   : CLOSED
Ranking direction            : VALIDATED
Triage retrain               : AUTHORIZED / NOT STARTED
Automatic REVIEW             : NOT AUTHORIZED
Automatic EXCLUDE            : NOT AUTHORIZED

V59 final public mix         : NOT FINALIZED
Model training               : NOT STARTED
Model training authorized    : NO
```

Latest V59 audit at this checkpoint -->

`PHASE03-SMOLTALK-V59-ACTIVE-SAMPLE-003`

Training remains **NOT AUTHORIZED / NOT STARTED**.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
