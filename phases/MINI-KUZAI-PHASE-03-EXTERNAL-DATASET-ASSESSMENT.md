# MINI-KUZAI PHASE 03 - EXTERNAL DATASET ASSESSMENT

Version: 0.2
Status: VALIDATED FOR FILTERED USE

## 1. PURPOSE

This document records the assessment of `HuggingFaceTB/smol-smoltalk` as an external conversational source for Mini-Kuzai Phase 03.

The external dataset is not considered Mini-Kuzai identity data.

Its role is to provide reusable general conversational and technical language patterns while the Mini-Kuzai-specific corpus remains responsible for identity, curiosity, independence, initiative, values, and character development.

## 2. DATA ACQUIRED AND VERIFIED

Local files:

```text
data/external/smol-smoltalk/raw/test-00000-of-00001.parquet
data/external/smol-smoltalk/raw/train-00000-of-00004.parquet
data/external/smol-smoltalk/raw/train-00001-of-00004.parquet
data/external/smol-smoltalk/raw/train-00002-of-00004.parquet
data/external/smol-smoltalk/raw/train-00003-of-00004.parquet
```

The four train shards were verified by SHA256 and parsed successfully as Apache Parquet.

Observed train size:

```text
train rows              : 460341
train shards            : 4
external local storage  : approximately 926 MB
```

The original raw files are treated as immutable external source material.

## 3. TEST SAMPLE STRUCTURE

Observed test structure:

```text
rows                    : 24229
columns                 : messages, source
message roles           : user, assistant, system
mean messages           : 4.62
median messages         : 6
```

The test file was used only for preliminary source inspection. It is not Mini-Kuzai blind evaluation material.

## 4. FULL TRAIN PROFILE

The complete train split contains:

```text
TOTAL_ROWS  : 460341
user        : 1032124 messages
assistant   : 1031866 messages
system      : 70484 messages
```

A deterministic first-pass filter was evaluated without modifying the raw files.

First-pass surviving pools:

```text
GENERAL_CANDIDATES_TOTAL   : 158228
TECHNICAL_CANDIDATES_TOTAL : 47748
```

This confirms that Phase 03 does not need to train on the full external dataset. A much smaller controlled subset can be selected while preserving substantial source diversity.

## 5. SOURCE ASSESSMENT

### smol-magpie-ultra-short

Full train observations:

```text
conversations               : 270838
messages mean               : 6
assistant length mean       : 1450.22 chars
assistant question percent  : 18.96
 generic phrase percent      : 4.21
code percent                : 9.79
list percent                : 16.99
role-play percent           : 1.85
general candidates          : 85395
general candidate percent   : 31.53
```

Assessment: PRIMARY RESERVOIR - FILTER REQUIRED

Reasons:

- by far the largest source;
- useful multi-turn coverage;
- broad semantic diversity;
- enough clean material remains after filtering;
- generic assistant phrasing is present;
- responses are often longer than the desired Mini-Kuzai default;
- code, list-heavy output, and role-play material must be separated or removed.

Recommended use:

- primary general conversational reservoir;
- deterministic length and style filters;
- source quota to prevent dominance;
- manual sample inspection after selection.

### self-oss-instruct

Full train observations:

```text
conversations               : 48071
messages mean               : 2
assistant length mean       : 810.09 chars
code percent                : 100.0
technical candidates        : 47748
```

Assessment: TECHNICAL SUBCORPUS ONLY

Reasons:

- almost every record contains code;
- very low generic assistant contamination;
- useful for technical and programming language;
- unsuitable as a general personality source.

Recommended use:

- small technical quota only;
- keep separate from the general dialogue reservoir;
- do not allow coding style to dominate Phase 03.

### openhermes-50k

Full train observations:

```text
conversations               : 47492
messages mean               : 2.4
assistant length mean       : 909.83 chars
assistant question percent  : 7.33
generic phrase percent      : 4.77
code percent                : 20.51
list percent                : 18.76
role-play percent           : 0.96
general candidates          : 27685
general candidate percent   : 58.29
```

Assessment: SECONDARY RESERVOIR - FILTER REQUIRED

Recommended use:

- filtered secondary source;
- reject generic service language;
- reject or isolate code-heavy examples;
- inspect system-prompt influence before final conversion.

### smol-contraints

Full train observations:

```text
conversations               : 34433
generic phrase percent      : 6.91
list percent                : 37.91
general candidates          : 920
general candidate percent   : 2.67
```

Assessment: REJECT FOR FIRST GENERAL MIX

Reason:

The source produces strong formatting and list pressure and contributes very little clean material under the current filter.

### smollm-rewrite-30k

Full train observations:

```text
conversations               : 26657
assistant question percent  : 46.49
generic phrase percent      : 12.98
general candidates          : 22790
general candidate percent   : 85.49
```

Assessment: SPECIAL TASK DATA - NOT GENERAL PERSONALITY DATA

The high candidate count does not mean it should dominate the pool. Its rewrite task structure can produce misleading question statistics and task-specific behavior.

Recommended use:

- exclude from the first external general pool;
- preserve for later rewriting experiments.

### smol-summarize-20k

Full train observations:

```text
conversations               : 19272
assistant length mean       : 459.31 chars
generic phrase percent      : 0.04
list percent                : 0.60
general candidates          : 18122
general candidate percent   : 94.03
```

Assessment: HIGH QUALITY SPECIAL TASK SOURCE

The source is clean and concise, but it primarily teaches summarization rather than general dialogue.

Recommended use:

- exclude from the first general personality pool;
- optionally introduce later with a small summarization quota.

### smol-summarize-5k

Full train observations:

```text
conversations               : 4749
generic phrase percent      : 40.70
list percent                : 65.53
general candidates          : 338
```

Assessment: REJECT FOR FIRST MIX

### longalign

Full train observations:

```text
conversations               : 3560
code percent                : 9.10
list percent                : 33.99
general candidates          : 0
```

Assessment: REJECT FOR FIRST GENERAL MIX

### explore-instruct-rewrite

Full train observations:

```text
conversations               : 3017
assistant length mean       : 121.05 chars
generic phrase percent      : 0.30
code percent                : 0.0
list percent                : 0.76
role-play percent           : 0.13
general candidates          : 2978
general candidate percent   : 98.71
```

Assessment: HIGH VALUE SMALL SOURCE

Reasons:

- very concise output;
- extremely low generic assistant contamination;
- almost no list or code pressure;
- useful counterweight to the long-response bias of the main reservoir.

Recommended use:

- retain a controlled quota;
- inspect semantic diversity before final selection.

### everyday-conversations

Full train observations:

```text
conversations               : 2252
messages mean               : 7.75
assistant length mean       : 126.71 chars
assistant question percent  : 28.91
generic phrase percent      : 27.55
general candidates          : 0
```

Assessment: REJECT AS RAW CORE PERSONALITY SOURCE

The source contains short multi-turn dialogue but strongly reinforces conventional service-assistant behavior.

Individual scenarios may later be rewritten into Mini-Kuzai style if needed.

## 6. IMPORTANT METRIC LIMITATION

The metric `assistant response contains a question mark` is not sufficient to measure curiosity.

A question mark may occur because:

- the assistant is rewriting an email that already contains a question;
- the assistant quotes a question;
- a role-play character asks a scripted question;
- the response uses a generic service question such as `How can I help?`.

Future classification must distinguish:

```text
GENERIC SERVICE QUESTION
TASK-CONTENT QUESTION
ROLE-PLAY QUESTION
GENUINE FOLLOW-UP QUESTION
CLARIFICATION QUESTION
EXPLORATORY QUESTION
```

Only the last three categories are useful evidence for Mini-Kuzai curiosity behavior.

## 7. FIRST EXTERNAL POOL TARGET

The full profile shows that there is no need to retain all 158228 clean general candidates.

The first external pool should be deliberately small and balanced.

Target v0.1:

```text
smol-magpie-ultra-short      : 5000
openhermes-50k               : 1500
explore-instruct-rewrite     : 1000
self-oss-instruct technical  : 1000
                              -----
TOTAL TARGET                 : 8500
```

These are candidate-pool quotas, not final training weights.

Excluded from candidate pool v0.1:

```text
smol-contraints
smollm-rewrite-30k
smol-summarize-20k
smol-summarize-5k
longalign
everyday-conversations
```

The excluded sources remain available locally for future controlled experiments.

## 8. REQUIRED FILTERS

A candidate external conversation should be rejected or downgraded when it contains one or more of the following unless the example has a specific experimental purpose:

- generic service greetings;
- `How can I help you today?` style language;
- `Feel free to ask` closing phrases;
- excessive `Certainly`, `Of course`, `Absolutely`, or similar assistant markers;
- excessive politeness;
- excessive list-first structure;
- marketing or customer-service tone;
- fixed third-party role-play identity;
- very long responses unsuitable for the target context window;
- low-information filler;
- duplicated or near-duplicated scenarios;
- system prompts unrelated to the future Mini-Kuzai runtime format.

## 9. LENGTH POLICY

For the first external subset, prioritize assistant messages approximately in these bands:

```text
100-1200 chars   preferred general range
1200-2000 chars  selective general range
2000-2500 chars  technical only when justified
>2500 chars      reject by default for first mix
```

The first pool should intentionally include both concise and moderately detailed responses instead of teaching one fixed response length.

## 10. EXTERNAL DATA IS NOT IDENTITY DATA

The external subset must not define:

- Mini-Kuzai's name;
- THE KUZ NETWORK origin;
- Kusanagi8200 relationship;
- personal values;
- personality invariants;
- worldview;
- future identity;
- KUZAI-LLM roadmap.

Those elements remain under the dedicated Mini-Kuzai corpus and behavior design.

## 11. DECISION

Decision: USE `smol-smoltalk` AS A FILTERED EXTERNAL RESERVOIR.

The full train split is validated for local filtering.

No training run should use the raw Parquet files directly.

The first external pool will target 8500 records selected deterministically from four approved source classes.

The pool remains pre-training material until it passes manual inspection, duplicate analysis, schema conversion, and compatibility review with the Mini-Kuzai behavior matrix.

## 12. NEXT OPERATION

1. create external candidate pool v0.1 with deterministic quotas;
2. preserve source row identifiers and provenance;
3. compute hashes for selected conversational content;
4. inspect pool distribution and random deterministic samples;
5. detect exact duplicates and near-duplicates;
6. approve or revise the external pool;
7. map retained records to the Phase 03 dataset schema;
8. only then combine external data with Mini-Kuzai-specific conversations.
