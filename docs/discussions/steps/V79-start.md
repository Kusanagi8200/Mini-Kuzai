# Mini-Kuzai | V79 - Same-Path Context-Order Control

```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : V79
  STATUS   : EXPERIMENT STARTED
========================================================================
```

## Objective

Test whether the tiny context-order effect observed in V77 persists when ORIGINAL and REVERSE_HISTORY_KEEP_LAST prefixes are evaluated through exactly the same execution path.

V77 changed only 5 of 9170 top-1 predictions, but it compared two different execution paths.

V78 then showed that rebatching alone creates continuous numerical alpha noise while changing:

- 0 top-1 predictions
- 0 alpha signs
- 0 correctness outcomes

V79 therefore removes the remaining execution-path asymmetry.

## Frozen control

Both modes use the same frozen prefix scorer and the same batch size of 32.

ORIGINAL_SAME_PATH:

- original teacher-forced prefix
- prefix scorer
- batch 32
- unchanged target

REVERSE_SAME_PATH:

- same prefix scorer
- same batch 32
- same target
- same prefix length
- same token multiset
- same BOS
- same immediate preceding token
- only earlier-history order is reversed

No FULL_CONTEXT batch-4 path is used in the paired comparison.

## Required replay

Before any context-order result is accepted, ORIGINAL_SAME_PATH must reproduce the verified V78 PATH_B baseline exactly:

- 9170 lexical positions
- 2594 correct predictions
- 2 distinct predicted IDs
- 70.43% dominant top-1 share

The V77 perturbation inventory must also replay:

- 9062 actually perturbed prefixes
- 108 unchanged short prefixes

## Measurements

V79 is designed to compare:

- top-1 prediction agreement and changes
- correctness retained, lost or gained
- alpha sign agreement and changes
- alpha correlation
- alpha deltas above 1e-7, 1e-6 and 1e-5
- maximum and mean alpha delta

One future GOGIT report is limited to exactly 30 aggregate integer metrics.

No token text, hidden vectors, alpha vectors or per-position records may be published.

## Interpretation

If the V77 discrete changes persist under the same execution path, evidence for sensitivity to earlier-context order becomes stronger.

If they disappear, the V77 effect was likely dependent on an interaction between the perturbation and numerical execution details.

Either result remains a teacher-forced numerical diagnostic.

V79 cannot establish semantic competence, reasoning ability, correct context use or generalization.

## Safety and authorization

V79 is currently **PREPARED ONLY**.

This preparation does not authorize:

- START-DEV-FLOW V79
- GitHub or LinkedIn publication
- implementation execution
- CPU preflight
- GPU execution
- training
- optimizer steps
- checkpoint writes
- BLIND access
- generation
- FINAL-DEV-FLOW

A separate explicit operator authorization is required before V79 START.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
