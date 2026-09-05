# MINI-KUZAI PHASE 03 - EXTERNAL STRICT DEDUP AUDIT

Version: 0.1
Status: VALIDATED

## PURPOSE

Record the strict near-duplicate audit applied to the persona-clean external pool before construction of pool v0.4.

## INPUT

```text
source pool     : external-candidate-pool-v0.3a-persona-clean.jsonl
input records   : 7926
step id         : PHASE03-EXTERNAL-STRICT-DEDUP-001
```

## STRICT THRESHOLD

A pair is considered an automatic near-duplicate only when both conditions are satisfied:

```text
weighted Jaccard >= 0.90
SequenceMatcher  >= 0.93
```

The threshold was selected after manual inspection of a broader similarity audit. Lower similarity pairs included mathematically related but genuinely different problems and were therefore not safe for automatic removal.

## RESULTS

```text
candidate pairs            : 597760
strict duplicate pairs     : 46
strict duplicate groups    : 8
records in strict groups   : 31
records to remove          : 23
records after strict dedup : 7903
```

All 23 removals belong to:

```text
smol-magpie-ultra-short
```

## GROUP QUALITY

The eight strict groups are genuine paraphrase families rather than merely related topics. They include repeated versions of:

- the snail in a well problem;
- the bat and ball problem;
- the two coins riddle;
- proof that there is no largest natural number;
- identical exam-score transformation questions;
- the largest even-digit multiple-of-nine problem;
- identical cubic equation questions;
- the ancient tribe leadership combinatorics problem.

The retained record in each group is selected deterministically by `selection_rank_sha256`.

## DECISION

The strict threshold is approved for automatic deduplication of the current external candidate pool.

Pool v0.4 will:

1. start from the persona-clean v0.3a pool;
2. remove the 23 strict duplicate records;
3. retain one deterministic representative per strict group;
4. refill missing source quotas from the immutable raw Parquet files;
5. apply the expanded persona filter to replacements;
6. reject exact prompt-family and content duplicates;
7. reject replacement candidates that cross the validated strict similarity threshold against retained records;
8. rerun the complete residual and uniqueness audit before approval.

No training is authorized by this result.
