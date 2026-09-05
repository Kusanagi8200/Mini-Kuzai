# MINI-KUZAI PHASE 03 - OASST1 COMPOSITE QUALITY AUDIT

Version: 0.1
Status: VALIDATED FOR BEHAVIORAL VALUE AUDIT

## Purpose

Compare several OASST1 assistant-selection rules before extracting any external training pool.

## Input

- dataset: OpenAssistant/oasst1
- clean English roots: 3482
- reachable clean assistant messages: 23054
- structural tree audit: PASS

## Rules compared

- rank0
- rank01
- quality_basic
- quality_safe
- quality_safe_rank01

`quality_safe` requires:

- quality >= 0.75
- helpfulness >= 0.75
- fails_task <= 0.25
- toxicity <= 0.25 when present
- not_appropriate <= 0.25 when present
- spam <= 0.25 when present
- lang_mismatch <= 0.25 when present

## Results

Accepted assistant messages:

- rank0: 7827
- rank01: 15638
- quality_basic: 9705
- quality_safe: 8984
- quality_safe_rank01: 6833

Reconstructed path results:

- rank0: 2136 paths, 1198 with at least 4 messages, mean quality 0.7443, mean helpfulness 0.7615
- rank01: 2133 paths, 1192 with at least 4 messages, mean quality 0.8181, mean helpfulness 0.8257
- quality_basic: 1520 paths, 777 with at least 4 messages, mean quality 0.8906, mean helpfulness 0.9152
- quality_safe: 1424 paths, 708 with at least 4 messages, mean quality 0.8902, mean helpfulness 0.9151
- quality_safe_rank01: 1157 paths, 532 with at least 4 messages, mean quality 0.8868, mean helpfulness 0.9112

## Interpretation

Rank is useful but is not sufficient as a quality rule.

The quality-based rules produce a much stronger average assistant quality than rank-only selection.

`quality_safe` loses only 96 reconstructed paths compared with `quality_basic`, while adding explicit controls for toxicity, inappropriate content, spam, and language mismatch.

The additional rank restriction in `quality_safe_rank01` reduces the reservoir significantly without improving measured mean quality.

Therefore `quality_safe` is the current candidate extraction rule.

It is not frozen as the final OASST1 pool rule yet.

## Important limitation

High annotation scores do not prove that the resulting paths contain the behaviors Mini-Kuzai needs.

OASST1 is being added specifically to improve interaction patterns that SmolTalk lacks, especially:

- follow-up dialogue
- clarification
- challenge and correction
- disagreement
- response revision
- conversational continuity

The next operation must therefore profile those behaviors inside paths reconstructed with `quality_safe`.

## Current decision

```text
OASST1 STRUCTURE           : VALID
QUALITY_SAFE RULE          : CANDIDATE
FINAL OASST1 POOL          : NOT CREATED
OASST1 TRAINING USE        : NOT AUTHORIZED
NEXT STEP                  : BEHAVIORAL VALUE AUDIT
```
