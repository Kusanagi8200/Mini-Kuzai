# Mini-Kuzai | V75 - TRAIN-Fitted Geometry Transfer Control

```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : V75
  STATUS   : EXPERIMENT STARTED
========================================================================
```

## Objective

Determine whether the dominant output-head hidden-state direction transfers from the frozen TRAIN population to the separate frozen VALIDATION population when the geometry is fitted exclusively on TRAIN.

V74 showed that the earlier VALIDATION-fitted PC1_ONLY result was strongly confounded by TRAIN token frequency. V75 therefore removes the VALIDATION-fit bias before making any further interpretation of the dominant direction.

## Frozen scope

The V75 protocol is frozen before this START.

The study reuses the original stopped V62 cycle-2 checkpoint with 69 optimizer steps and 597982 exposure tokens. The complete frozen TRAIN lexical population is the calibration set and the same 9170 frozen VALIDATION lexical positions are the scoring set.

The TRAIN mean and leading principal direction must be estimated without consulting VALIDATION. The fixed TRAIN geometry is then applied to ORIGINAL, TRAIN_CENTER, TRAIN_PC1_ONLY and TRAIN_MINUS_PC1 controls. The frozen V74 TRAIN_UNIGRAM result and the V73 VALIDATION-fitted geometry remain descriptive references only.

One public GOGIT report is predeclared with exactly 30 nonnegative integer metrics, including explicit no-training and no-BLIND gates.

## Safety and execution gates

This START opens the V75 development and research flow. It does not authorize model training or BLIND evaluation.

Before any GPU execution, the V75 implementation, CPU regression tests, source fingerprints, fixed batch/chunk strategy and measured resource gate must be reviewed and pass fail-closed preflight.

No optimizer step, checkpoint write, model-weight change, tokenizer/corpus modification, hidden-state export, private text publication, individual token publication or per-position prediction publication is authorized.

A GPU failure, provenance mismatch, denominator mismatch, nonfinite statistic, timeout, changed checkpoint or attempted BLIND access must abort without GOGIT publication.

This START makes no advance claim about the scientific result. Only immutable GOGIT evidence can be reviewed after the controlled study, and FINAL-DEV-FLOW requires a separate explicit authorization.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
