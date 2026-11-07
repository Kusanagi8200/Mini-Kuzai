# Mini-Kuzai | V77 - Residual Context-Order Sensitivity Control

```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : V77
  STATUS   : EXPERIMENT STARTED
========================================================================
```

## Objective

Test whether the predictive signal that remained after V76 frequency residualization actually depends on preceding context order.

V76 showed that TRAIN lexical frequency explains only 7.75% of the centered PC1 output-profile energy. The orthogonal residual retains 92.25% of the energy and reaches 2594/9170 correct frozen VALIDATION predictions, but still collapses to only two predicted output IDs.

V77 therefore asks a narrower question.

Does that residual change when earlier context order changes while the target, prefix length, prefix token inventory, BOS and immediate preceding token remain fixed?

## Frozen counterfactual

For each frozen VALIDATION lexical target, V77 compares the normal teacher-forced prefix with one deterministic counterfactual.

The counterfactual keeps:

- the same target
- the same prefix length
- the same prefix token multiset
- BOS in first position
- the immediate preceding token in last prefix position

Only the earlier history between BOS and the immediate predecessor is reversed.

Prefixes too short to contain an interior history remain unchanged and are counted separately.

The V76 frequency-residualized output profile is frozen and reused unchanged.

Only the hidden-state PC1 coordinate is recomputed under the altered context order.

## Required replay

Before accepting any new V77 measurement, FULL_CONTEXT must reproduce the verified V76 residual result exactly:

- 9170 lexical positions
- 2594 correct predictions
- 2 distinct predicted IDs
- 7043 basis-point dominant top-1 share
- 6458 predictions agreeing with the TRAIN unigram
- 2451 shared-correct predictions with the TRAIN unigram

The V76 frequency fit must also replay exactly:

- axis-frequency correlation --> 2785 basis points
- R2 --> 775 basis points
- residual-energy share --> 9225 basis points

## Measurements

V77 measures only aggregate paired evidence:

- residual top-1 performance under original and reversed-history context
- prediction agreement and changed-position counts
- PC1-coordinate sign agreement
- absolute correlation between original and counterfactual PC1 coordinates
- positions with numerically changed PC1 coordinate
- correctness retained, lost or gained by the perturbation

One public scientific GOGIT is predeclared with exactly 30 nonnegative integer metrics.

No outcome threshold is declared in advance.

## Interpretation limits

If the residual changes under this intervention, V77 will show that it is sensitive to earlier-context order and therefore is not purely invariant to that context.

If little changes, the residual remains compatible with another static or near-static concentration effect.

The reverse-history input is an artificial counterfactual. Sensitivity to it does not establish that the model uses normal context correctly, understands language, generalizes, or has developed semantic competence.

## Safety

V62 remains frozen.

This START authorizes only the V77 development flow and later CPU-only implementation preflight.

It does not authorize:

- GPU scientific execution
- training or optimizer steps
- BLIND access
- checkpoint writes
- tokenizer or corpus modification
- generation
- FINAL-DEV-FLOW
- a scientific success claim

Any provenance mismatch, V76 replay mismatch, context-transformation invariant failure, nonfinite statistic, timeout, OOM or attempted BLIND access must abort without scientific GOGIT publication.

GPU execution requires a separate explicit authorization after CPU preflight verification.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
