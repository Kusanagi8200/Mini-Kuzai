# Mini-Kuzai Phase 03 - V76 Frequency-Residualized PC1 Output Control 001

Date --> 2026-11-07
Frozen review --> 2026-11-07

Status --> **PROTOCOL FROZEN / START DRAFT MAY BE PREPARED / START NOT AUTHORIZED / GPU NOT AUTHORIZED / NO TRAINING / NO BLIND ACCESS**

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

## Frozen scientific question

**How much of the frozen TRAIN-PC1 output-head signature is explained by TRAIN lexical target frequency, and does the frequency-residualized part retain independent predictive concentration on frozen VALIDATION?**

V76 is an output-profile decomposition study. It is not a hidden-state retraining method, a model patch, a semantic evaluation, a generation benchmark or a causal intervention on learned weights.

## Frozen inheritance from V75

V76 must reuse the unchanged V62 cycle-2 checkpoint and reproduce these verified values before scientific scoring:

- V62 status --> STOPPED
- stop reason --> MILESTONE_REVIEW_REQUIRED
- optimizer steps --> 69
- exposure tokens --> 597982
- TRAIN lexical positions --> 294726
- TRAIN observed lexical token types --> 891
- VALIDATION lexical positions --> 9170
- hidden dimension --> 128
- output vocabulary --> 1024 IDs
- V75 TRAIN PC1 centered variance share --> 9019 basis points
- V75 TRAIN/VALIDATION PC1 absolute cosine --> 9995 basis points
- V75 TRAIN_PC1_ONLY correct --> 2457
- V75 TRAIN_PC1_ONLY distinct predicted IDs --> 2
- V75 TRAIN_PC1_ONLY dominant top-1 share --> 7043 basis points
- V74 TRAIN_UNIGRAM correct --> 2535
- V75 coverage --> 10000 basis points

Any mismatch blocks V76.

BLIND remains closed.

## Frozen reviewed dependencies

The first implementation must fail closed if these reviewed Git blobs change:

- V75 geometry/scoring helper --> `tools/v75_train_fitted_geometry_transfer.py` --> blob `8705d8ca9aebe7281779c704119d26eb82517da2`
- V65 lexical TRAIN frequency audit --> `tools/public-audits/phase03_v65_token_frequency_diagnostic_001.py` --> blob `d88e05933686b369d5236c3bcd465729e2df3407`
- V75 immutable scientific report --> blob `51606f42f60c5e53c437cac0be9bc6459fadbd05`
- V74 CORE immutable report --> blob `8cf575c440d7625bd03d6ce1d77c3951c678f84a`
- V74 STRATA immutable report --> blob `5096c81e32b6140f926930a09e0b6253fa557c01`

The implementation may reuse reviewed V75 helper functions, but it must not modify V75 source or historical reports.

## Frozen TRAIN-only calibration

All calibration occurs on TRAIN only.

### 1. Recompute V75 TRAIN geometry

Recompute the exact V75 streaming FP64 TRAIN mean and leading centered PC1 without retaining the full hidden-state population.

Let:

- `u_train` --> the frozen TRAIN-derived leading unit PC1
- `W` --> the unchanged tied bias-free output matrix
- `a = W u_train` --> raw PC1 output-profile vector over all 1024 output IDs

The V75 geometry and replay invariants above must match before continuing.

### 2. Build the frozen TRAIN lexical frequency vector

Reuse the V65 lexical counting definition exactly:

- count only TRAIN body next-token targets
- exclude PAD, BOS and terminal EOS
- valid lexical IDs --> 3 through 1023
- preserve the complete frozen 345-segment TRAIN stream
- expected lexical total --> 294726
- expected observed lexical types --> 891

Construct a 1024-element count vector over the complete output vocabulary.

For IDs 0, 1 and 2, and for lexical IDs not observed in TRAIN, the count is exactly zero.

For every output ID `t`:

`f_t = log(1 + count_train(t))`

This preserves the exact 1024-way output competition used by V75 while making the frequency source strictly TRAIN-only.

### 3. Remove decision-irrelevant constant output offsets

A constant added to all vocabulary logits cannot alter argmax.

Define the centered PC1 output profile:

`q = a - mean(a)`

Define centered log-frequency:

`g = f - mean(f)`

Require:

- both vectors finite
- `||q|| > 0`
- `||g|| > 0`
- exact length 1024

For any VALIDATION position, `alpha * a` and `alpha * q` differ only by the same scalar offset for every output ID. Their argmax must therefore be identical. The implementation must verify this replay property.

### 4. Fit the frozen frequency component

Fit one deterministic unweighted OLS coefficient in FP64:

`beta = dot(g, q) / dot(g, g)`

Define:

`c = beta * g`

`r = q - c`

where:

- `c` --> frequency-explained centered output profile
- `r` --> frequency-residualized centered output profile

No VALIDATION quantity may influence `beta`, centering, token inclusion, frequency transform or any threshold.

### 5. Frozen numerical decomposition gates

Before VALIDATION scoring, require:

- all `beta`, `c`, `r` values finite
- `max_abs(q - c - r) <= 1e-12` in FP64
- residual orthogonality to the regressor within relative tolerance `1e-10`
- Pearson denominator finite and nonzero
- OLS `R^2` finite and in `[0, 1]` after tolerance
- residual-energy share finite and in `[0, 1]`

Define:

`corr_abs = abs(dot(g,q)) / (||g|| ||q||)`

`R2 = 1 - ||r||^2 / ||q||^2`

`residual_energy_share = ||r||^2 / ||q||^2`

The implementation must internally verify the OLS identity between `R2` and squared Pearson correlation within numerical tolerance. No outcome threshold is used to declare scientific success.

## Frozen VALIDATION scoring

Use the exact frozen 9170 lexical VALIDATION positions from V73-V75.

For every position:

`alpha = (h - mu_train) dot u_train`

Score these 1024-way logit profiles:

| Mode | Logit contribution |
| --- | --- |
| TRAIN_PC1_REPLAY | `alpha * q` |
| FREQ_COMPONENT_ONLY | `alpha * c` |
| FREQ_RESIDUAL_ONLY | `alpha * r` |

By construction:

`TRAIN_PC1_REPLAY = FREQ_COMPONENT_ONLY + FREQ_RESIDUAL_ONLY`

in centered logit space.

TRAIN_PC1_REPLAY must reproduce the frozen V75 TRAIN_PC1_ONLY aggregate exactly:

- correct --> 2457
- distinct predicted IDs --> 2
- dominant top-1 share --> 7043 basis points

The decomposition must never change model weights, checkpoint state, tokenizer files or corpus files.

## Frozen scientific measurements

V76 reports:

- absolute Pearson correlation between centered PC1 output scores and centered `log1p(TRAIN lexical frequency)`
- OLS `R^2`
- residual output-profile energy share
- top-1 accuracy, distinct predicted IDs and dominant-token share for:
  - TRAIN_PC1_REPLAY
  - FREQ_COMPONENT_ONLY
  - FREQ_RESIDUAL_ONLY
- agreement of FREQ_COMPONENT_ONLY and FREQ_RESIDUAL_ONLY with the frozen TRAIN unigram baseline
- shared-correct count between FREQ_RESIDUAL_ONLY and the unigram baseline
- agreement between TRAIN_PC1_REPLAY and FREQ_COMPONENT_ONLY
- exact V75 geometry replay
- full VALIDATION coverage

### Interpretation rule

A high frequency fit together with a weak or highly concentrated residual would support the hypothesis that the stable PC1 output signature is largely explained by a static TRAIN frequency direction.

A residual that retains substantial predictive structure would justify a later, separately designed context-sensitivity test.

Neither outcome establishes semantic competence, causal representation, personality formation or generalization beyond the frozen teacher-forced VALIDATION population.

## Frozen 30-field GOGIT schema

STEP_ID --> `PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001`

The scientific publication must contain exactly these 30 aggregate nonnegative integer metrics:

1. `SEMANTIC_VALIDATION_COMPLETE`
2. `TRAINING_AUTHORIZED`
3. `TRAINING_STARTED`
4. `V76_PASS`
5. `V76_BLIND_ACCESS`
6. `V76_TRAIN_LEXICAL`
7. `V76_TRAIN_TYPES`
8. `V76_VAL_LEXICAL`
9. `V76_HIDDEN_DIM`
10. `V76_FIT_VOCAB`
11. `V76_PC1_CORRECT`
12. `V76_PC1_DISTINCT`
13. `V76_PC1_TOP1_SHARE_BP`
14. `V76_UNIGRAM_CORRECT`
15. `V76_AXIS_FREQ_CORR_ABS_BP`
16. `V76_AXIS_FREQ_R2_BP`
17. `V76_FREQ_COMPONENT_CORRECT`
18. `V76_FREQ_COMPONENT_DISTINCT`
19. `V76_FREQ_COMPONENT_TOP1_SHARE_BP`
20. `V76_FREQ_RESIDUAL_CORRECT`
21. `V76_FREQ_RESIDUAL_DISTINCT`
22. `V76_FREQ_RESIDUAL_TOP1_SHARE_BP`
23. `V76_RESIDUAL_UNIGRAM_AGREE`
24. `V76_RESIDUAL_UNIGRAM_SHARED_CORRECT`
25. `V76_PC1_FREQ_COMPONENT_AGREE`
26. `V76_FREQ_COMPONENT_UNIGRAM_AGREE`
27. `V76_PC1_VAR_SHARE_BP`
28. `V76_TRAIN_VAL_PC1_COS_ABS_BP`
29. `V76_RESIDUAL_ENERGY_SHARE_BP`
30. `V76_COVERAGE_BP`

## Frozen fixed expectations

A successful V76 scientific GOGIT must require exactly:

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V76_PASS=1`
- `V76_BLIND_ACCESS=0`
- `V76_TRAIN_LEXICAL=294726`
- `V76_TRAIN_TYPES=891`
- `V76_VAL_LEXICAL=9170`
- `V76_HIDDEN_DIM=128`
- `V76_FIT_VOCAB=1024`
- `V76_PC1_CORRECT=2457`
- `V76_PC1_DISTINCT=2`
- `V76_PC1_TOP1_SHARE_BP=7043`
- `V76_UNIGRAM_CORRECT=2535`
- `V76_PC1_VAR_SHARE_BP=9019`
- `V76_TRAIN_VAL_PC1_COS_ABS_BP=9995`
- `V76_COVERAGE_BP=10000`

No expected scientific outcome is predeclared for correlation, R2, frequency-component performance, residual performance, agreement metrics or residual-energy share.

`V76_PASS=1` means only that the frozen computation, replay, decomposition, provenance, safety and coverage gates completed. It is not a positive scientific outcome.

## Frozen CPU implementation review requirements

Before any GPU authorization, CPU-only tests must verify at minimum:

1. exact 30-field schema and GOGIT allowlist compatibility
2. dependency/blob pin checks
3. V65 lexical frequency definition and 1024-element zero-filled count-vector construction
4. synthetic centered OLS recovery
5. constant-logit-offset invariance
6. PC1 eigenvector sign invariance
7. exact `q = c + r` decomposition
8. residual orthogonality to centered log-frequency
9. Pearson/R2 identity within tolerance
10. aggregate histogram/accounting helpers
11. fail-closed handling of nonfinite/degenerate inputs
12. no BLIND path or import
13. no optimizer/checkpoint-write path
14. no raw token text, hidden vector or per-position output in public metrics

CPU preflight is not GPU authorization.

## Frozen runtime/resource boundary

A future implementation must remain bounded and read-only:

- one CUDA device only
- unchanged V62 checkpoint
- evaluation/inference mode only
- `torch.set_grad_enabled(False)` plus inference/no-grad contexts
- TRAIN batch size --> 2
- VALIDATION batch size --> 4
- score chunk --> 512
- GPU peak-memory hard ceiling --> 6144 MiB
- no optimizer
- no checkpoint writes
- no model-weight mutation
- no BLIND access
- no full hidden-state accumulation
- no token text, private dialogue, per-position predictions or hidden vectors in GOGIT
- only the exact 30 allowlisted integer metrics
- GOGIT process budget --> 300 seconds
- OOM, timeout, nonfinite value, pin mismatch, replay mismatch or resource-gate failure --> abort without scientific GOGIT

## Authorization boundary

This protocol is now **frozen**, but no execution authorization follows from the freeze.

It does not authorize:

- START-DEV-FLOW V76
- implementation execution
- CPU preflight execution
- GPU execution
- new training
- optimizer steps
- checkpoint modification
- BLIND access
- FINAL-DEV-FLOW
- a scientific conclusion

A reviewed V76 START draft may now be prepared. Creating a START request or publishing the START requires a separate explicit operator authorization.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
