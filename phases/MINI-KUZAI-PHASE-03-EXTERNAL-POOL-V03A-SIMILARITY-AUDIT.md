# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.3A SIMILARITY AUDIT

Version: 0.1
Status: REVIEWED

## 1. PERSONA CLEANUP

Input pool:

```text
8000 records
```

Additional missed persona prompts detected:

```text
74 total
3 openhermes-50k
71 smol-magpie-ultra-short
```

Clean pool after removal:

```text
7926 records
```

The persona filter used in v0.3 was therefore incomplete. Future pool construction must explicitly reject phrases such as `assume the role`, `take the role`, `act like`, `portray`, `impersonate`, and equivalent persona instructions.

## 2. SIMHASH RESULT

The previous SimHash experiment is rejected as an automatic similarity filter.

Reason:

Its normalization caused severe false positives, including unrelated short prompts and mathematical expressions collapsing to identical fingerprints.

Decision:

Do not use the previous SimHash implementation for automatic removal.

## 3. CONSERVATIVE SIMILARITY AUDIT

The replacement audit combines:

- weighted lexical Jaccard similarity;
- sequence similarity;
- rare-token based candidate generation.

Observed result:

```text
candidate pairs checked             : 597760
near duplicate pairs                : 160
near duplicate groups               : 23
records in near duplicate groups    : 83
```

The method successfully identifies true paraphrase families such as:

- snail well problem;
- bat and ball problem;
- coin riddle;
- exam mean and standard deviation variants;
- square-free integer variants;
- repeated probability prompts;
- proof that there is no largest natural number.

## 4. IMPORTANT THRESHOLD FINDING

The method also groups some prompts that are structurally similar but not semantically identical.

Examples include:

- different polynomial remainder problems;
- different improper integrals;
- different circle equation parameters;
- different algebraic equations;
- different probability parameterizations.

Therefore, the current near-duplicate detector is useful for candidate discovery but must not automatically collapse every detected group.

## 5. RECOMMENDED AUTO-DEDUP THRESHOLD

For automatic duplicate removal, use a stricter rule than the discovery audit.

Candidate rule for the next experiment:

```text
weighted Jaccard >= 0.90
AND
sequence similarity >= 0.93
```

This threshold captures the clearest paraphrase duplicates observed in the audit while avoiding most template-level examples that only share a task family.

A lower-confidence range should remain available for manual review:

```text
weighted Jaccard >= 0.76
AND
sequence similarity >= 0.84
```

but must not trigger automatic removal.

## 6. NEXT OPERATION

1. apply the expanded persona filter;
2. rebuild from raw source material rather than treating v0.3a as final;
3. apply exact prompt-family deduplication;
4. apply strict high-confidence paraphrase deduplication only;
5. refill quotas from unused source records;
6. preserve one representative per high-confidence duplicate group;
7. audit source distribution, persona residue, exact duplicates, and high-confidence near duplicates;
8. inspect a deterministic manual sample before accepting the external pool.

No training should use v0.3 or v0.3a directly.
