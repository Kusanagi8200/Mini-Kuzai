# Mini-Kuzai Phase 03 - V75 TRAIN-Fitted Geometry Transfer 001

Date --> 2026-11-01

Status --> **PROTOCOL PROPOSAL ONLY / NOT AUTHORIZED / NOT STARTED / NO GOGIT / NO TRAINING / NO BLIND ACCESS**

## Why V75 follows V74

The [verified V74 frequency-prior audit](MINI-KUZAI-PHASE-03-V74-FREQUENCY-PRIOR-CONTROL-001.md) established that PC1_ONLY correctly predicts 2455 of 9170 VALIDATION lexical targets, while a context-free TRAIN_UNIGRAM predicts 2535. Of the 2455 PC1_ONLY successes, 2449 coincide with unigram successes. This supports a strong frequency-prior confound, not a causal explanation of PC1 or a semantic capability claim.

[V72](MINI-KUZAI-PHASE-03-V72-HIDDEN-STATE-ANISOTROPY-001.md) and [V73](MINI-KUZAI-PHASE-03-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.md) estimated mean and principal directions **on VALIDATION itself**, then scored those same positions. Such in-sample geometric fitting may overstate the transferability of the measured directions.

## Proposed scientific question

**Do the dominant hidden-state directions estimated exclusively from frozen TRAIN states transfer to the separate frozen VALIDATION population, or is the observed PC1 dominance partly an artifact of VAL-fitted geometry?**

The test concerns **geometric transfer**, not model retraining, deployment changes, causal attribution or independent language competence.

## Proposed strictly read-only study

1. Verify the original frozen V62 cycle-2 checkpoint, dataset/tokenizer lineage and original V65, V72, V73 and V74 immutable GOGIT metrics and source fingerprints
2. Define the TRAIN calibration population **before execution**, using only frozen authorized TRAIN records and a deterministic lexical token-position inclusion rule. Verify its size and disjoint split identity without exporting raw text or token IDs
3. Run one bounded, inference-only pass over frozen TRAIN, capturing only the 128-dimensional output-head hidden states needed to accumulate the FP64 mean and covariance. Use bounded chunks, no gradients, no optimization, no tensor artifacts and no activation exports
4. Compute a TRAIN-fitted centered mean and PC1 once, **without consulting VALIDATION to fit or select axes, thresholds or hyperparameters**
5. Apply the fixed TRAIN mean and PC1 to the exact 9170 lexical positions of frozen VALIDATION. Compare ORIGINAL, TRAIN_CENTER, TRAIN_PC1_ONLY and TRAIN_MINUS_PC1 using the unchanged tied output matrix
6. Predeclare the relevant fixed V73 VAL-fitted metrics as descriptive references, and the V74 TRAIN_UNIGRAM baseline as an explicit frequency-only control. Quantify the TRAIN-PC1 versus VAL-PC1 unsigned cosine alignment only as a retrospective, non-tuning diagnostic
7. Report aggregate top-1 accuracy, distinct predicted IDs, top-token dominance, gold byte/merged-BPE correct counts, and TRAIN-prior overlaps without exposing per-position outputs or content
8. Publish only strictly allowlisted, nonnegative integer aggregate metrics through GOGIT after a frozen protocol, exact schema, reproducibility tests and authorization have passed

## Mandatory scientific controls

- Preserve **V62** after 69 optimizer steps and 597982 exposed tokens. Never resume V61, train, update weights, optimizer, model state, checkpoints or dataset
- Keep the **BLIND TEST closed**. TRAIN is the geometric fitting population and VALIDATION is the only scoring population. Do not use VALIDATION for fitting, selecting or refitting TRAIN axes
- Preserve original V72/V73 VALIDATION-fit numbers for audit comparison. A new TRAIN-fit result need not equal those values and must not be tuned to match them
- Fail closed on missing data provenance, inconsistent lexical denominator, unexpected model/source hash, CUDA errors, nonfinite statistics or resource limit
- Predeclare numerical metric names, units, strict `30 metrics per GOGIT report` limit, orientation/sign-invariant comparisons, stop gates and expected sample coverage **before running GPU inference**
- Require independent offline tests of covariance accumulation, projection algebra, deterministic selection, spectral degeneracy, source immutability, and error gates
- No GitHub public source can include private conversations, examples, raw hidden states, tokenizer IDs, model weights, prediction vectors or training data
- Declare that teacher-forced VALIDATION scoring remains limited. Even a successful TRAIN-fit transfer does not demonstrate generation quality, conversation skills or persona learning

## Current authorization boundary

This document is **planning material only**. It is not a frozen implementation specification and does not authorize launching an audit, GPU work, training, accessing BLIND or publishing START-DEV-FLOW. The exact schema, computation resources and leakage gates require a separate review in the next discussion.

A [V75 START draft](../docs/discussions/steps/V75-start.md) is prepared for future review. It **must not be published until the operator explicitly requests START-DEV-FLOW for V75** after accepting the proposed scope. No `V75-start.json`, `V75-final.json`, run, checkpoint or GOGIT is created by this preparation.

## Recommended next steps

1. Confirm the two-host DEV-FLOW pipeline remains healthy after the KUZ-DIN legacy V74 hash-compatibility patch
2. Review and freeze V75 protocol, TRAIN-only fit selection, deterministic algorithm, GPU resource budget and 30-field public GOGIT schema
3. Create CPU-only unit tests and a fail-closed read-only GPU runner
4. Only after explicit approval, publish V75 START and perform the controlled study, followed by numeric GOGIT and a separately authorized FINAL

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
