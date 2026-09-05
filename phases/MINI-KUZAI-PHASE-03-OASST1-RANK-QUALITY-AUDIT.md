# MINI-KUZAI PHASE 03 - OASST1 RANK QUALITY AUDIT

Version: 0.1
Status: COMPLETED - NO SELECTION RULE FROZEN

## Purpose

Measure whether OASST1 answer rank can be used as a reliable quality filter before extracting a second external conversation reservoir.

## Dataset state

The audit operates on the previously validated clean English OASST1 tree reconstruction.

Reachable clean assistant nodes: 23054.

## Rank quality profile

Rank 0:
- count: 7827
- quality mean: 0.7413
- quality median: 0.75

Rank 1:
- count: 7811
- quality mean: 0.6835
- quality median: 0.75

Rank 2:
- count: 5274
- quality mean: 0.6052
- quality median: 0.6667

Rank 3+:
- count: 1013
- quality mean: 0.5792
- quality median: 0.5833

Unranked:
- count: 1129
- quality mean: 0.6946
- quality median: 0.75

Quality declines clearly as rank worsens, so rank contains useful preference information.

## Direct rank 0 vs rank 1 comparison

Pairs with quality labels: 7625.

- rank 0 quality higher: 3979
- rank 1 quality higher: 2686
- equal quality: 960
- mean quality difference rank0 minus rank1: +0.0578
- median difference: +0.0833

Therefore rank 0 is statistically better on average but is not a sufficient standalone quality rule.

## Candidate path rule experiment

Rank 0 only:
- complete paths: 2136
- paths with at least 4 messages: 1198
- paths with at least 6 messages: 13

Rank 0 or one single unranked answer when no rank 0 exists:
- complete paths: 2466
- paths with at least 4 messages: 1528
- paths with at least 6 messages: 34

A strict rank-only rule discards a large amount of potentially useful conversational material.

## Decision

No extraction rule is frozen yet.

The next operation must compare composite quality rules using at minimum:

- rank
- quality
- helpfulness
- fails_task
- toxicity
- not_appropriate
- spam
- lang_mismatch

The objective is to retain coherent high-quality conversational branches without assuming that rank 0 is always superior.

No OASST1 training pool is created by this audit.
