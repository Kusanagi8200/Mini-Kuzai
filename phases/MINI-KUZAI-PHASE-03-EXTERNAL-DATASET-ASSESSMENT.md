# MINI-KUZAI PHASE 03 - EXTERNAL DATASET ASSESSMENT

Version: 0.1
Status: CANDIDATE

## 1. PURPOSE

This document records the first assessment of `HuggingFaceTB/smol-smoltalk` as an external conversational source for Mini-Kuzai Phase 03.

The external dataset is not considered Mini-Kuzai identity data.

Its role is to provide reusable general conversational and technical language patterns while the Mini-Kuzai-specific corpus remains responsible for identity, curiosity, independence, initiative, values, and character development.

## 2. SAMPLE ANALYZED

Sample file:

```text
data/external/smol-smoltalk/raw/test-00000-of-00001.parquet
```

Observed structure:

```text
rows                    : 24229
columns                 : messages, source
message roles           : user, assistant, system
mean messages           : 4.62
median messages         : 6
```

The sample is large enough to establish preliminary source-level filtering rules, but it is not used as Mini-Kuzai blind evaluation material.

## 3. SOURCE ASSESSMENT

### smol-magpie-ultra-short

Assessment: PRIMARY RESERVOIR - FILTER REQUIRED

Reasons:

- largest source in the sample;
- useful multi-turn coverage;
- assistant questions occur with useful frequency;
- includes technical, explanatory, role-play, and open-domain material;
- generic assistant phrasing is present and must be filtered;
- responses are often longer than the desired Mini-Kuzai default;
- role-play examples can incorrectly teach invented identities if retained blindly.

Recommended use:

- retain a filtered subset;
- cap response length;
- remove generic assistant greetings and service phrases;
- remove identity-heavy role-play scenarios unless explicitly required for a separate experiment;
- separate code-heavy conversations from general dialogue.

### self-oss-instruct

Assessment: TECHNICAL SUBCORPUS ONLY

Reasons:

- virtually all assistant responses contain code;
- low generic assistant contamination;
- short single-turn structure;
- useful for K3 technical language but unsuitable as a general personality base.

Recommended use:

- small quota only;
- classify as technical knowledge / coding material;
- do not allow it to dominate general dialogue.

### openhermes-50k

Assessment: SECONDARY RESERVOIR - FILTER REQUIRED

Reasons:

- moderate response length;
- useful technical content;
- significant system-message presence;
- measurable generic assistant language;
- substantial code content;
- suitable for selective instruction and technical examples.

Recommended use:

- retain a filtered subset;
- remove or normalize generic system prompts before model-visible training if they do not match the Mini-Kuzai runtime format;
- exclude generic assistant service language.

### smol-contraints

Assessment: LOW PRIORITY

Reasons:

- strong list-format pressure;
- noticeable generic assistant language;
- artificial formatting constraints can create undesirable response reflexes.

Recommended use:

- exclude from the first personality training corpus;
- optionally retain a very small future instruction-following subset.

### smollm-rewrite-30k

Assessment: SPECIAL TASK DATA

Reasons:

- system prompts are present in every analyzed conversation;
- high apparent question-mark frequency is partly caused by rewritten source text and should not be interpreted as Mini-Kuzai curiosity;
- useful for rewriting but not as a core dialogue source.

Recommended use:

- exclude from first general dialogue mix;
- preserve only for future rewriting capability experiments.

### smol-summarize-20k

Assessment: SPECIAL TASK DATA

Reasons:

- concise output;
- low generic assistant contamination;
- systematic summarization framing;
- does not teach open conversation strongly.

Recommended use:

- optional small future summarization subset;
- not part of first personality mix.

### smol-summarize-5k

Assessment: REJECT FOR FIRST MIX

Reasons:

- very high generic assistant phrasing;
- strong list-format pressure;
- long multi-turn sequences;
- likely to reinforce conventional assistant style.

### explore-instruct-rewrite

Assessment: PROMISING SMALL SOURCE

Reasons:

- very short responses;
- no detected generic assistant phrases in the analyzed sample;
- low list and code pressure;
- small source size.

Recommended use:

- retain selectively as a concise-response source;
- inspect semantic diversity before assigning a final quota.

### longalign

Assessment: LOW PRIORITY / SELECTIVE

Reasons:

- no detected generic assistant phrasing in the analyzed sample;
- high list-format frequency;
- small source size.

Recommended use:

- optional small quota only.

### everyday-conversations

Assessment: REJECT AS CORE PERSONALITY SOURCE

Reasons:

- useful short multi-turn dialogue;
- very high generic assistant phrase rate;
- examples contain the exact service-assistant behavior Mini-Kuzai is intended to avoid.

Recommended use:

- do not use raw in the first Mini-Kuzai training mix;
- individual scenarios could later be rewritten into Mini-Kuzai style if useful.

## 4. IMPORTANT METRIC LIMITATION

The simple metric `assistant response contains a question mark` is not sufficient to measure curiosity.

A question mark may occur because:

- the assistant is rewriting an email that already contains a question;
- the assistant quotes a question;
- a role-play character asks a scripted question;
- the response uses a generic service question such as `How can I help?`.

Future filtering must therefore distinguish:

```text
GENERIC SERVICE QUESTION
TASK-CONTENT QUESTION
ROLE-PLAY QUESTION
GENUINE FOLLOW-UP QUESTION
CLARIFICATION QUESTION
EXPLORATORY QUESTION
```

Only the last three categories are useful evidence for Mini-Kuzai curiosity behavior.

## 5. FIRST EXTERNAL MIX HYPOTHESIS

The first external conversational subset should remain much smaller than the complete source dataset.

Initial target before Mini-Kuzai-specific data is added:

```text
3000-6000  filtered smol-magpie-ultra-short
500-1500   filtered openhermes-50k
300-1000   self-oss-instruct technical subset
100-300    explore-instruct-rewrite
0-300      longalign selective subset
0          raw everyday-conversations
0          smol-summarize-5k
0          smol-contraints in first mix
0          smollm-rewrite-30k in first mix
0          smol-summarize-20k in first mix
```

These are acquisition and filtering targets, not final training weights.

## 6. REQUIRED FILTERS

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

## 7. LENGTH POLICY HYPOTHESIS

The analyzed sample has assistant responses around 1300 characters on average across the full sample, which is longer than desirable as a default personality pattern.

For the first external subset, prioritize assistant messages approximately in these bands:

```text
100-1200 chars   preferred general range
1200-2500 chars  selective
>2500 chars      reject by default for first mix
```

Exceptions may be retained for technical explanations or later long-context experiments.

## 8. EXTERNAL DATA IS NOT IDENTITY DATA

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

## 9. DECISION

Decision: DOWNLOAD THE FULL TRAIN SPLIT FOR LOCAL FILTERING.

Reason:

The test sample demonstrates enough useful material to justify acquiring the complete source, while also demonstrating enough undesirable assistant behavior to rule out raw training on the full dataset.

The full train split will be treated as an external reservoir only.

No training run should use raw `smol-smoltalk` files directly.

## 10. NEXT OPERATION

1. download the complete train Parquet shards;
2. verify file integrity and row count;
3. profile the train source distribution;
4. implement deterministic filtering rules;
5. produce an external candidate subset;
6. inspect that subset manually;
7. map retained material to the Phase 03 dataset schema;
8. only then combine selected external data with Mini-Kuzai-specific conversations.
