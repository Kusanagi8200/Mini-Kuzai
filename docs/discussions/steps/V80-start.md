# Mini-Kuzai | V80 - Decision-Boundary Proximity Control

```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : V80
  STATUS   : EXPERIMENT STARTED
========================================================================
```

## Objective

Determine whether the five V79 context-order prediction changes are confined to positions close to the frozen residual decision boundary at `alpha=0`.

V79 removed the execution-path asymmetry and still reproduced exactly:

- 5 / 9170 top-1 changes
- 5 / 9170 alpha-sign changes
- 2594 / 9170 correct predictions in ORIGINAL
- 2594 / 9170 correct predictions in REVERSE
- 99.99% absolute alpha correlation

This means the tiny V77 effect persists under the exact same scoring path.

V80 now asks how close those five sign crossings are to the decision boundary.

## Frozen control

V80 replays the exact V79 same-path pair:

- ORIGINAL_SAME_PATH
- REVERSE_HISTORY_KEEP_LAST
- same scorer
- same batch 32
- same V62 checkpoint
- same target
- same prefix length
- same token multiset
- same immediate preceding token
- no generation

Before any new metric is accepted, V79 must replay exactly, including the five prediction changes and five sign changes.

## Boundary measurement

For every paired position:

`boundary_distance = min(abs(alpha_original), abs(alpha_reverse))`

The cumulative frozen proximity thresholds are:

- 1e-7
- 1e-6
- 1e-5
- 1e-4
- 1e-3

V80 counts how many of the five changed positions fall inside each threshold and publishes only aggregate integer metrics.

It also reports aggregate nano-unit summaries for the changed positions.

No raw alpha values, token text, hidden vectors or per-position records are published.

## Interpretation

If all five changes are concentrated extremely close to zero, V79 is best interpreted as weak context-order sensitivity expressed at fragile decision boundaries.

If one or more sign crossings occur substantially farther from zero, the context-order effect is stronger than a near-boundary numerical flip.

Neither outcome establishes semantic competence, reasoning or correct language understanding.

## Safety and authorization

V80 is currently **PREPARED ONLY**.

This preparation does not authorize:

- START-DEV-FLOW V80
- GitHub or LinkedIn publication
- CPU preflight execution
- GPU execution
- training
- optimizer steps
- checkpoint writes
- BLIND access
- generation
- FINAL-DEV-FLOW

A separate explicit operator command `START-DEV-FLOW` is required to start the autonomous publication transaction and authorize implementation / CPU-only preflight scope.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
