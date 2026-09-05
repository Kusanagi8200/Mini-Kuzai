# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.3 AUDIT

Version: 0.1
Status: REJECTED FOR TRAINING

## 1. SUMMARY

External candidate pool v0.3 contains 8000 records and passes exact structural checks, but it is not approved for training.

Observed source quotas:

```text
smol-magpie-ultra-short     : 5000
openhermes-50k              : 1500
explore-instruct-rewrite    : 500
self-oss-instruct           : 1000
TOTAL                       : 8000
```

Exact audit results:

```text
unique prompt families      : 8000
exact prompt duplicates     : 0
exact content duplicates    : 0
persona residual detected   : 0
generic residual detected   : 0
benchmark residual detected : 0
Unicode dash residual       : 0
```

These checks are necessary but not sufficient.

## 2. PERSONA FILTER GAP

The top user-opening audit exposed prompts such as:

```text
I'd like you to assume the role ...
I want you to assume the role ...
I would like you to assume the role ...
```

These are third-party persona prompts and must not enter the Mini-Kuzai external training pool.

The v0.3 persona patterns did not include `assume the role` and related formulations, therefore the reported `PERSONA_RESIDUAL = 0` is a false sense of completeness rather than proof that the pool is persona-free.

Pool v0.4 must add explicit detection for:

```text
assume the role
assume role
adopt the role
adopt a persona
take the role
take on the role
act in the role
act like
act as if you are
portray
impersonate
simulate being
respond in character
stay in character
```

## 3. SEMANTIC REPETITION GAP

Exact normalized first-prompt deduplication removed literal families, but semantically equivalent variants remain.

Examples include multiple variants of:

```text
snail climbing a well
bat and ball price problem
derivative exercises
remainder exercises
probability exercises
exam-score statistics
```

This means a hash of normalized text is not a semantic deduplication mechanism.

Pool v0.4 must introduce an additional concept-level fingerprint or near-duplicate check so that small lexical changes do not allow the same exercise family to dominate the pool.

## 4. OPENING PHRASE BIAS

The v0.3 pool still contains frequent assistant openings such as:

```text
to solve this problem we
here's how you can
here's how we can
here is a python function
here is the implementation of
```

The repetition is lower than v0.2 but still strong enough to teach response templates.

The v0.3 caps were applied per source. The same opening can therefore accumulate across several sources.

Pool v0.4 must apply global caps in addition to source-level caps.

## 5. LENGTH PROFILE

Observed overall assistant length:

```text
median : 1078 chars
p90    : 1765 chars
```

This remains acceptable for an external knowledge and reasoning reservoir, but it is longer than the desired default conversational style for Mini-Kuzai.

This does not require immediate rejection because the Mini-Kuzai-specific corpus will later provide short, direct, personality-bearing dialogue. However, response-length balance must be reviewed again before final training weights are chosen.

## 6. DECISION

Decision: DO NOT TRAIN ON V0.3.

The pool is retained as an experimental artifact only.

Required v0.4 changes:

1. expand persona detection to `assume the role` and related forms;
2. add concept-level near-duplicate control;
3. apply global assistant-opening caps;
4. apply global user-opening caps where appropriate;
5. retain exact provenance and deterministic selection;
6. preserve zero exact duplicates;
7. preserve zero generic-assistant markers;
8. preserve zero benchmark markers;
9. preserve ASCII hyphen-minus only.

## 7. NEXT OPERATION

Build external candidate pool v0.4 from the immutable raw Parquet files, not by editing v0.3 in place.

V0.1, v0.2, and v0.3 remain preserved for comparison and audit history.
