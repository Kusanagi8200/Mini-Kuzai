# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.4 BEHAVIORAL UTILITY AUDIT

Version: 0.1
Status: VALIDATED EXTERNAL RESERVOIR

## Purpose

This document records the behavioral utility audit of the cleaned external candidate pool `external-candidate-pool-v0.4.jsonl`.

The purpose of this audit is not to decide final training weights. It is to determine what the external pool can safely contribute to Mini-Kuzai Phase 03 and what must instead come from the custom Mini-Kuzai corpus.

## Input

Pool:

`/root/Mini-Kuzai/data/external/smol-smoltalk/candidates/external-candidate-pool-v0.4.jsonl`

Total records: 8000

Source distribution:

- `smol-magpie-ultra-short`: 5000
- `openhermes-50k`: 1500
- `self-oss-instruct`: 1000
- `explore-instruct-rewrite`: 500

## Behavioral classes

- natural dialogue: 1840 - 23.00 percent
- programming task: 1740 - 21.75 percent
- single turn other: 1121 - 14.01 percent
- multi turn other: 1111 - 13.89 percent
- factual QA: 556 - 6.95 percent
- personal advice: 537 - 6.71 percent
- general task: 386 - 4.83 percent
- text transformation: 280 - 3.50 percent
- academic problem: 234 - 2.92 percent
- creative dialogue: 195 - 2.44 percent

Aggregated indicators:

- natural candidate total: 2572 - 32.15 percent
- task oriented total: 2640 - 33.00 percent
- multi turn total: 5001 - 62.51 percent
- followup signal total: 2267 - 28.34 percent
- challenge signal total: 132 - 1.65 percent
- assistant question total: 820 - 10.25 percent
- conversational signal total: 795 - 9.94 percent
- task start total: 1778 - 22.23 percent
- factual start total: 1285 - 16.06 percent

## Source behavior profile

### smol-magpie-ultra-short

This is the only source in v0.4 with a strong natural dialogue component.

- natural dialogue: 1840 - 36.80 percent of source
- multi turn other: 1111 - 22.22 percent
- programming task: 546 - 10.92 percent
- personal advice: 521 - 10.42 percent
- factual QA: 462 - 9.24 percent
- creative dialogue: 195 - 3.90 percent
- academic problem: 175 - 3.50 percent
- general task: 142 - 2.84 percent
- text transformation: 8 - 0.16 percent

### self-oss-instruct

This source is almost purely a programming task reservoir.

- programming task: 991 - 99.10 percent of source
- single turn other: 8 - 0.80 percent
- academic problem: 1 - 0.10 percent

It must not be interpreted as general conversational data.

### openhermes-50k

This source is mostly single turn or task oriented material.

- single turn other: 876 - 58.40 percent of source
- general task: 202 - 13.47 percent
- programming task: 198 - 13.20 percent
- factual QA: 94 - 6.27 percent
- text transformation: 59 - 3.93 percent
- academic problem: 57 - 3.80 percent
- personal advice: 14 - 0.93 percent

### explore-instruct-rewrite

This source is primarily rewrite and transformation material.

- single turn other: 237 - 47.40 percent of source
- text transformation: 213 - 42.60 percent
- general task: 42 - 8.40 percent
- programming task: 5 - 1.00 percent
- personal advice: 2 - 0.40 percent
- academic problem: 1 - 0.20 percent

## Interpretation

The pool is technically clean and behaviorally diverse enough to be useful, but it is not a final conversational corpus.

The external pool has three useful roles:

1. English language mechanics and general response formation.
2. Generic multi turn dialogue mechanics, mainly from `smol-magpie-ultra-short`.
3. Technical and task competence, especially programming, factual QA, writing transformation, and academic reasoning.

The external pool is weak for the behaviors that define Mini-Kuzai as a distinct entity:

- disagreement
- independent reasoning
- initiative
- curiosity
- explicit challenge
- opinion formation
- opinion revision
- self condition discovery
- relationship development
- recognizable Mini-Kuzai personality

The challenge signal is only 1.65 percent. This is far too low to use external data as the main source for Mini-Kuzai disagreement and independent thinking.

A high multi turn percentage does not by itself prove natural conversation. Many multi turn records are still task sequences or academic interactions.

## Decision

`external-candidate-pool-v0.4.jsonl` is accepted as a validated external reservoir.

It is not accepted as a final training corpus and it is not assigned final training weights at this stage.

No further blind filtering will be applied merely to force the external pool to resemble Mini-Kuzai. Doing so would risk discarding useful general language and technical competence.

The custom Mini-Kuzai corpus remains responsible for identity and behavioral shaping.

The final training mixture will be decided only after the custom corpus exists and can be measured against this external reservoir.

## Phase 03 consequence

External dataset assessment and filtering is complete for the first reservoir version.

Next work moves to the semantic group inventory for the custom Mini-Kuzai corpus, using the existing identity specification, behavior matrix, knowledge map, and dataset schema.

No training begins yet.
