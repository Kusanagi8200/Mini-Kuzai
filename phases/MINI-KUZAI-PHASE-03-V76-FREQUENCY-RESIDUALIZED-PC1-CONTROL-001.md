# Mini-Kuzai Phase 03 - V76 Frequency-Residualized PC1 Output Control 001

Date --> 2026-11-07

Status --> **PROPOSED / NOT FROZEN / START NOT AUTHORIZED / GPU NOT AUTHORIZED / NO TRAINING / NO BLIND ACCESS**

## Why V76 follows V74 and V75

V74 established a strong frequency-prior confound: the context-free TRAIN unigram predicts 2535/9170 frozen VALIDATION lexical targets, while PC1_ONLY predicts 2455/9170, with 2449 shared correct predictions.

V75 then removed the VALIDATION-fit objection. A PC1 fitted exclusively on TRAIN transfers almost unchanged to VALIDATION:

- absolute cosine(TRAIN PC1, VALIDATION PC1) --> 99.95%
- TRAIN_PC1_ONLY correct --> 2457/9170
- TRAIN_PC1_ONLY distinct predicted IDs --> 2
- TRAIN_PC1 centered variance share --> 90.19%
- VALIDATION PC1 centered variance share --> 82.88%

The remaining question is therefore not whether PC1 transfers. It does.

The unresolved question is whether the output profile induced by that stable PC1 contains predictive structure beyond a static TRAIN token-frequency prior.

## Proposed scientific question

**How much of the frozen TRAIN-PC1 output-head signature is explained by TRAIN target frequency, and does the frequency-residualized part retain independent predictive concentration on frozen VALIDATION?**

V76 is an output-profile decomposition study. It is not a hidden-state retraining method, a model patch, a semantic evaluation, a generation benchmark or a causal intervention on learned weights.

## Frozen inheritance from V75

Any future V76 implementation must reuse the unchanged V62 cycle-2 checkpoint and must reproduce these verified values before scoring:

- V62 status --> STOPPED
- stop reason --> MILESTONE_REVIEW_REQUIRED
- optimizer steps --> 69
- exposure tokens --> 597982
- TRAIN lexical positions --> 294726
- TRAIN observed lexical token types --> 891
- VALIDATION lexical positions --> 9170
- hidden dimension --> 128
- V75 TRAIN PC1 centered variance share --> 9019 basis points
- V75 TRAIN/VALIDATION PC1 absolute cosine --> 9995 basis points
- V75 TRAIN_PC1_ONLY correct --> 2457
- V75 TRAIN_PC1_ONLY distinct predicted IDs --> 2
- V75 TRAIN_PC1_ONLY dominant top-1 share --> 7043 basis points
- V74 TRAIN_UNIGRAM correct --> 2535
- V75 coverage --> 10000 basis points

Any mismatch blocks V76.

BLIND remains closed.

## Proposed TRAIN-only calibration

All calibration must occur on TRAIN only.

### 1. Recompute the V75 TRAIN geometry

Recompute the exact V75 streaming FP64 TRAIN mean and leading centered PC1 without retaining the full hidden-state population.

Let:

- `u_train` --> the frozen TRAIN-derived leading unit PC1
- `W` --> the unchanged tied bias-free output matrix
- `a = W u_train` --> the PC1 output-profile vector over the complete output vocabulary

The V75 geometry and replay invariants above must match before continuing.

### 2. Build a static TRAIN frequency feature

From the frozen ordered TRAIN serialization, count every next-token target ID over the complete output vocabulary.

For output token ID `t`:

`f_t = log(1 + count_train(t))`

This count vector is TRAIN-only. VALIDATION must not influence token inclusion, counts, transforms or regression parameters.

### 3. Fit the frequency component of the PC1 output profile

Fit an unweighted ordinary least-squares model over the complete output vocabulary:

`a_t = beta0 + beta1 * f_t + r_t`

where:

- `a_t` is the PC1 output score for token `t`
- `beta0 + beta1*f_t` is the static frequency-explained component
- `r_t` is the frequency-residualized PC1 output profile

The fit is deterministic and uses TRAIN-derived quantities only.

No VALIDATION-derived threshold, fit, normalization or model-selection decision is allowed.

## Proposed VALIDATION scoring

Use the exact frozen 9170 lexical VALIDATION positions from V73-V75.

For every position:

`alpha = (h - mu_train) dot u_train`

The following output-logit profiles are diagnostic decompositions only:

| Mode | Logit contribution |
| --- | --- |
| TRAIN_PC1_ONLY | `alpha * a` |
| FREQ_COMPONENT_ONLY | `alpha * (beta0 + beta1*f)` |
| FREQ_RESIDUAL_ONLY | `alpha * r` |

The decomposition must satisfy numerically:

`TRAIN_PC1_ONLY = FREQ_COMPONENT_ONLY + FREQ_RESIDUAL_ONLY`

up to the predeclared FP64/FP32 implementation tolerance before output ranking.

No model weight, checkpoint, tokenizer or corpus file may be modified.

## Proposed scientific measurements

V76 should quantify:

- absolute Pearson correlation between PC1 output scores and `log1p(TRAIN frequency)`
- OLS coefficient of determination `R^2`
- residual output-profile energy after the frequency fit
- top-1 accuracy, distinct predicted IDs and dominant-token share for:
  - TRAIN_PC1_ONLY replay
  - FREQ_COMPONENT_ONLY
  - FREQ_RESIDUAL_ONLY
- agreement of each decomposed mode with the frozen TRAIN unigram baseline
- agreement between TRAIN_PC1_ONLY and each component
- exact V75 geometry replay and full VALIDATION coverage

### Interpretation rule

A strong frequency fit combined with a weak/concentrated residual would support the hypothesis that the stable PC1 output signature is largely a static frequency-prior direction.

A substantial frequency-residualized signal would justify a later, separately designed test of whether that residual is context-sensitive.

Neither outcome establishes semantic competence, causal representation or generalization beyond the frozen teacher-forced VALIDATION population.

## Proposed 30-field GOGIT schema

A future frozen implementation may publish at most these 30 aggregate integer metrics:

1. `SEMANTIC_VALIDATION_COMPLETE`
2. `TRAINING_AUTHORIZED`
3. `TRAINING_STARTED`
4. `V76_PASS`
5. `V76_BLIND_ACCESS`
6. `V76_TRAIN_LEXICAL`
7. `V76_TRAIN_TYPES`
8. `V76_VAL_LEXICAL`
9. `V76_HIDDEN_DIM`
10. `V76_PC1_CORRECT`
11. `V76_PC1_DISTINCT`
12. `V76_PC1_TOP1_SHARE_BP`
13. `V76_UNIGRAM_CORRECT`
14. `V76_AXIS_FREQ_CORR_ABS_BP`
15. `V76_AXIS_FREQ_R2_BP`
16. `V76_FREQ_COMPONENT_CORRECT`
17. `V76_FREQ_COMPONENT_DISTINCT`
18. `V76_FREQ_COMPONENT_TOP1_SHARE_BP`
19. `V76_FREQ_RESIDUAL_CORRECT`
20. `V76_FREQ_RESIDUAL_DISTINCT`
21. `V76_FREQ_RESIDUAL_TOP1_SHARE_BP`
22. `V76_RESIDUAL_UNIGRAM_AGREE`
23. `V76_RESIDUAL_UNIGRAM_SHARED_CORRECT`
24. `V76_PC1_FREQ_COMPONENT_AGREE`
25. `V76_PC1_FREQ_RESIDUAL_AGREE`
26. `V76_FREQ_COMPONENT_UNIGRAM_AGREE`
27. `V76_PC1_VAR_SHARE_BP`
28. `V76_TRAIN_VAL_PC1_COS_ABS_BP`
29. `V76_RESIDUAL_ENERGY_SHARE_BP`
30. `V76_COVERAGE_BP`

### Proposed fixed replay expectations

If the protocol is later frozen, the following values should be required exactly before any scientific interpretation:

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V76_BLIND_ACCESS=0`
- `V76_TRAIN_LEXICAL=294726`
- `V76_TRAIN_TYPES=891`
- `V76_VAL_LEXICAL=9170`
- `V76_HIDDEN_DIM=128`
- `V76_PC1_CORRECT=2457`
- `V76_PC1_DISTINCT=2`
- `V76_PC1_TOP1_SHARE_BP=7043`
- `V76_UNIGRAM_CORRECT=2535`
- `V76_PC1_VAR_SHARE_BP=9019`
- `V76_TRAIN_VAL_PC1_COS_ABS_BP=9995`
- `V76_COVERAGE_BP=10000`

No expected scientific outcome is predeclared for correlation, R2, frequency-component performance, residual performance, agreement measures or residual energy.

## Resource and privacy boundary

A future implementation must remain bounded and read-only:

- one CUDA device only
- unchanged V62 checkpoint
- evaluation/inference mode only
- gradients globally disabled
- no optimizer
- no checkpoint writes
- no model-weight mutation
- no BLIND access
- no full hidden-state accumulation
- no token text, private dialogue, per-position predictions or hidden vectors in GOGIT
- only aggregate allowlisted integer metrics
- GOGIT process budget <= 300 seconds
- explicit memory ceiling required before GPU authorization

## Authorization boundary

This document is a **proposal only**.

It does not authorize:

- START-DEV-FLOW V76
- implementation execution
- GPU execution
- new training
- optimizer steps
- checkpoint modification
- BLIND access
- FINAL-DEV-FLOW
- a scientific conclusion

The next allowed action is protocol review and freeze. Only after that may a V76 START draft/request be prepared for separate explicit authorization.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
