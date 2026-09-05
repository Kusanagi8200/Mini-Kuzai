# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.2 CONTENT AUDIT

Version: 0.1
Status: REQUIRES DIVERSITY REFINEMENT

## 1. PURPOSE

This document records the qualitative content audit of `external-candidate-pool-v0.2.jsonl` before any training use.

The pool remains pre-training material.

## 2. POOL SIZE

```text
records : 8000
```

Source quotas:

```text
smol-magpie-ultra-short  : 5000
openhermes-50k           : 1500
explore-instruct-rewrite : 500
self-oss-instruct        : 1000
```

## 3. LENGTH PROFILE

### explore-instruct-rewrite

```text
median assistant chars : 91
p90 assistant chars    : 210.2
```

This source remains useful as a concise-response counterweight.

### openhermes-50k

```text
median assistant chars : 483
p90 assistant chars    : 1382
```

This source provides moderate response length and broad instruction coverage.

### self-oss-instruct

```text
median assistant chars : 726.5
p90 assistant chars    : 1378
```

This source remains technical-only.

### smol-magpie-ultra-short

```text
median assistant chars : 1084
p90 assistant chars    : 1764
```

This confirms that the primary reservoir still has a strong long-response bias.

## 4. DUPLICATE ANALYSIS

Exact full-conversation duplicates were not found.

However, normalized first-user-prompt analysis found:

```text
duplicate prompt groups         : 39
duplicate prompt extra records  : 651
duplicate conversation groups   : 0
```

The duplicate prompt metric intentionally normalizes numbers and punctuation, so it also detects repeated templates with changed numeric values.

This is useful for Phase 03 because the objective is conversational diversity, not repeated benchmark coverage.

Large repeated families include:

- snail in a well problems;
- bat and ball problems;
- remainder and modular arithmetic prompts;
- repeated probability templates;
- repeated algebraic templates.

Decision: external pool v0.2 is not yet approved for training.

## 5. STYLE CONCENTRATION

The most frequent normalized assistant openings include:

```text
to solve this problem let
to solve this problem we
here s a revised version
to find the derivative of
to find the remainder when
let s break down the
here s how you can
here is a python function
```

These repetitions indicate source-specific response templates.

If retained without control, they may encourage verbal mode collapse and overly predictable openings.

## 6. ARTIFICIAL QUESTION METRIC

Artificial question rates are low in the general pool:

```text
explore-instruct-rewrite : 0.20 percent
openhermes-50k           : 0.47 percent
smol-magpie-ultra-short  : 1.29 percent
self-oss-instruct        : 0.00 percent
```

This is acceptable for the external reservoir.

However, question-mark frequency must still not be interpreted as Mini-Kuzai curiosity.

## 7. SUSPICIOUS OPENINGS

Observed suspicious opening rates:

```text
explore-instruct-rewrite : 0.00 percent
openhermes-50k           : 0.80 percent
smol-magpie-ultra-short  : 0.05 percent
self-oss-instruct        : 17.70 percent
```

The high technical value for `self-oss-instruct` is mainly caused by coding phrases such as `Here's how` or implementation-style openings.

This is not treated as the same risk as generic service-assistant language, but it should be diversity-capped so coding answers do not all begin in the same way.

## 8. MANUAL SAMPLE FINDINGS

The deterministic samples show useful material but also confirm several risks.

Useful material includes:

- concise rewriting examples;
- general factual explanation;
- programming tasks;
- multi-turn reasoning;
- cases where an assistant revises an assumption after user challenge.

Observed risks include:

- heavy math benchmark concentration;
- repeated puzzle families;
- repetitive explanation openings;
- some awkward or low-quality rewritten sentences;
- very long explanatory style in the primary multi-turn source;
- coding answers with highly repetitive implementation framing.

## 9. DECISION FOR V0.3

The next pool version must preserve the current identity and style safety filters while adding diversity controls.

Required changes:

1. allow at most one selected record per normalized first-user-prompt family;
2. cap highly repetitive assistant opening families;
3. preserve source quotas by refilling from the full raw reservoir;
4. preserve deterministic selection;
5. preserve exact source provenance;
6. preserve zero residual persona prompts;
7. preserve zero residual generic-service patterns;
8. preserve zero forbidden Unicode dash characters;
9. keep code isolated to the technical quota;
10. retain v0.2 unchanged for experiment history.

## 10. TARGET V0.3

Target remains:

```text
smol-magpie-ultra-short  : 5000
openhermes-50k           : 1500
explore-instruct-rewrite : 500
self-oss-instruct        : 1000
TOTAL                    : 8000
```

The objective is not to shrink the pool automatically. The objective is to refill each quota using more diverse records from the larger eligible reservoir.

## 11. NEXT OPERATION

Build `external-candidate-pool-v0.3.jsonl` directly from the immutable Parquet source files with:

- the v0.2 safety filters;
- normalized prompt-family uniqueness;
- opening-family caps;
- deterministic ranking;
- full audit counters;
- no modification of v0.1 or v0.2.
