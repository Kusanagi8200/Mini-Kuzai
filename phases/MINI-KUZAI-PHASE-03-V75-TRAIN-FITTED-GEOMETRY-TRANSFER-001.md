# Mini-Kuzai Phase 03 - V75 TRAIN-Fitted Geometry Transfer 001

Date --> 2026-11-01
Frozen review --> 2026-11-07

Status --> **V75 CLOSED / SCIENTIFIC GOGIT VERIFIED / FINAL GITHUB+LINKEDIN PUBLISHED / NO TRAINING / NO BLIND ACCESS**

## Why V75 follows V74

The [verified V74 frequency-prior audit](MINI-KUZAI-PHASE-03-V74-FREQUENCY-PRIOR-CONTROL-001.md) established that PC1_ONLY correctly predicts 2455 of 9170 frozen VALIDATION lexical targets, while the context-free TRAIN_UNIGRAM predicts 2535. Of the 2455 PC1_ONLY successes, 2449 coincide with unigram successes.

This supports a strong frequency-prior confound. It does not provide a causal explanation of PC1 and does not demonstrate semantic capability.

[V72](MINI-KUZAI-PHASE-03-V72-HIDDEN-STATE-ANISOTROPY-001.md) and [V73](MINI-KUZAI-PHASE-03-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.md) fitted the centered mean and principal directions on VALIDATION itself and then scored the same population. V75 removes that in-sample geometry fit.

## Frozen scientific question

**Do dominant output-head hidden-state directions estimated exclusively from the frozen TRAIN population transfer to the separate frozen VALIDATION population, or was part of the V72/V73 PC1 dominance specific to VALIDATION-fitted geometry?**

V75 is a read-only geometric transfer study. It is not model retraining, a deployment change, a semantic evaluation, a generation benchmark or causal attribution.

## Frozen data and checkpoint boundary

V75 must reuse the original stopped V62 cycle-2 state and the same frozen corpus/tokenizer lineage already verified by V65, V73 and V74.

Mandatory invariants -->

- V62 status --> STOPPED
- Stop reason --> MILESTONE_REVIEW_REQUIRED
- Optimizer steps --> 69
- Exposure tokens --> 597982
- Resume flag --> false
- BLIND access during training --> false
- TRAIN lexical population --> 294726 positions
- TRAIN observed token types --> 891
- VALIDATION lexical scoring population --> exactly 9170 positions
- Hidden dimension --> 128
- V73 VALIDATION-fitted PC1 spectral share --> 8288 basis points
- V73 VALIDATION-fitted PC1_ONLY correct --> 2455
- V74 TRAIN_UNIGRAM correct --> 2535
- Original frozen FP32 correct --> 2673
- Original frozen FP32 distinct predicted IDs --> 5
- Original frozen FP32 dominant top-1 share --> 7255 basis points

Any mismatch blocks V75.

The BLIND TEST remains closed. No BLIND file, record, metric or aggregate may be read.

## Frozen TRAIN calibration population

The calibration population is the complete ordered lexical TRAIN population that reproduces the V65/V74 inventory of **294726 lexical positions and 891 observed token types**.

Use the same lexical inclusion rule already accepted by the frozen token-frequency diagnostics -->

- include only lexical next-token positions from the authorized frozen TRAIN stream
- exclude padding and special/non-lexical positions
- preserve corpus and sequence order
- do not sample, shuffle, rebalance, stratify or tune the population
- do not inspect VALIDATION when deciding the TRAIN calibration population

If the resulting TRAIN position count is not exactly 294726, fail closed.

## Frozen geometry algorithm

For every accepted TRAIN lexical position, run the unchanged V62 model in evaluation and inference-only mode and obtain the 128-dimensional output-head hidden state.

No hidden-state list may be retained. Accumulate only streaming FP64 sufficient statistics in deterministic corpus order using a numerically stable online mean/covariance algorithm.

The frozen computation is -->

1. compute the FP64 TRAIN mean vector `mu_train`
2. compute the centered 128 x 128 FP64 TRAIN covariance
3. require all statistics to be finite and covariance symmetry to pass the implementation tolerance
4. compute the largest centered eigenpair
5. fail if the leading eigenvalue is nonpositive or if the implementation's predeclared spectral-degeneracy gate is triggered
6. retain only the in-memory TRAIN mean and leading unit eigenvector for the scoring stage
7. do not persist hidden states, eigenvectors, prediction vectors, token IDs or private text

Eigenvector sign is scientifically irrelevant because all reported projection and alignment quantities are sign-invariant.

## Frozen VALIDATION scoring

Apply the fixed TRAIN-derived `mu_train` and PC1 to the exact same 9170 frozen lexical VALIDATION positions used in V73/V74.

With `h` the unchanged output-head hidden state, `u_train` the fixed TRAIN PC1 and `W` the unchanged tied bias-free output matrix -->

| Mode | Hidden-state input to output head |
| --- | --- |
| ORIGINAL | `h` |
| TRAIN_CENTER | `h - mu_train` |
| TRAIN_PC1_ONLY | `((h - mu_train)·u_train)u_train` |
| TRAIN_MINUS_PC1 | `(h - mu_train) - ((h - mu_train)·u_train)u_train` |

No VALIDATION-derived quantity may alter `mu_train`, `u_train`, thresholds, hyperparameters, chunking or inclusion rules.

For retrospective comparison only, recompute the V73 VALIDATION-fitted PC1 under the frozen V73 definition and report the absolute cosine alignment with TRAIN PC1. That diagnostic must not feed back into any V75 scoring choice.

## Frozen public numerical schema

V75 uses one immutable GOGIT report with exactly **30 nonnegative integer metrics**.

STEP_ID --> `PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001`

The exact fields are -->

1. `SEMANTIC_VALIDATION_COMPLETE`
2. `TRAINING_AUTHORIZED`
3. `TRAINING_STARTED`
4. `V75_PASS`
5. `V75_BLIND_ACCESS`
6. `V75_TRAIN_LEXICAL`
7. `V75_TRAIN_TYPES`
8. `V75_VAL_LEXICAL`
9. `V75_TRAIN_STATE_COUNT`
10. `V75_HIDDEN_DIM`
11. `V75_ORIG_CORRECT`
12. `V75_ORIG_DISTINCT`
13. `V75_ORIG_TOP1_SHARE_BP`
14. `V75_TRAIN_CENTER_CORRECT`
15. `V75_TRAIN_CENTER_DISTINCT`
16. `V75_TRAIN_CENTER_TOP1_SHARE_BP`
17. `V75_TRAIN_PC1_CORRECT`
18. `V75_TRAIN_PC1_DISTINCT`
19. `V75_TRAIN_PC1_TOP1_SHARE_BP`
20. `V75_TRAIN_MINUS_PC1_CORRECT`
21. `V75_TRAIN_MINUS_PC1_DISTINCT`
22. `V75_TRAIN_MINUS_PC1_TOP1_SHARE_BP`
23. `V75_UNIGRAM_CORRECT`
24. `V75_PC1_UNIGRAM_AGREE`
25. `V75_PC1_UNIGRAM_SHARED_CORRECT`
26. `V75_VAL_PC1_CORRECT`
27. `V75_TRAIN_VAL_PC1_COS_ABS_BP`
28. `V75_TRAIN_PC1_VAR_SHARE_BP`
29. `V75_VAL_PC1_VAR_SHARE_BP`
30. `V75_COVERAGE_BP`

Required fixed values -->

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V75_BLIND_ACCESS=0`
- `V75_TRAIN_LEXICAL=294726`
- `V75_TRAIN_TYPES=891`
- `V75_VAL_LEXICAL=9170`
- `V75_TRAIN_STATE_COUNT=294726`
- `V75_HIDDEN_DIM=128`
- `V75_ORIG_CORRECT=2673`
- `V75_ORIG_DISTINCT=5`
- `V75_ORIG_TOP1_SHARE_BP=7255`
- `V75_UNIGRAM_CORRECT=2535`
- `V75_VAL_PC1_CORRECT=2455`
- `V75_VAL_PC1_VAR_SHARE_BP=8288`
- `V75_COVERAGE_BP=10000`

Basis-point metrics use a denominator of 10000 and deterministic integer rounding. `V75_TRAIN_VAL_PC1_COS_ABS_BP` is the absolute cosine between the unit TRAIN PC1 and the independently recomputed unit VALIDATION PC1, making it sign-invariant.

No outcome value is predeclared for TRAIN_CENTER, TRAIN_PC1_ONLY, TRAIN_MINUS_PC1, TRAIN PC1 spectral share or TRAIN/VAL PC1 alignment.

## Frozen implementation and reproducibility gates

The following implementation files are authorized to be created **after V75 START**, but they do not yet exist at this protocol-freeze checkpoint -->

- shared read-only computation --> `tools/v75_train_fitted_geometry_transfer.py`
- pinned public GOGIT producer --> `tools/public-audits/phase03_v75_train_fitted_geometry_transfer_001.py`
- CPU regression suite --> `tests/test_phase03_v75_train_fitted_geometry_transfer_001.py`
- bounded job runner --> `tools/run_v75_train_fitted_geometry_transfer_001_job.py`

Before any GPU execution, the implementation review must prove -->

- exact 30-field schema and key ordering independent of model results
- synthetic covariance fixture with a known leading axis
- sign invariance of PC1 projection and absolute cosine metric
- deterministic lexical inclusion and denominator reconciliation
- deterministic streaming mean/covariance across the runner's fixed chunking strategy
- no gradient construction and no optimizer/model mutation
- source/report fingerprint verification for V65, V73 and V74
- exact reproduction of all fixed reference values above
- failure on nonfinite state/statistic, denominator mismatch, missing source, changed checkpoint, BLIND access attempt or duplicate GOGIT STEP_ID
- no persistence of hidden states, eigenvectors, token IDs, per-position predictions or private corpus content

CPU regressions must pass before a GPU job can become eligible.

## Frozen resource and execution ceilings

The future runner must remain fail-closed and bounded -->

- one CUDA device only
- `llama-server-a.service` must not be active during the V75 GPU job
- evaluation/inference mode only
- gradients globally disabled
- no optimizer object or optimizer step
- no checkpoint write
- no full hidden-state accumulation in CPU or GPU memory
- only streaming FP64 sufficient statistics plus aggregate integer counters may survive between batches
- GOGIT producer execution remains within the existing 300-second GOGIT process budget
- any CUDA OOM, timeout, nonfinite statistic or resource-gate failure aborts without publication

The implementation must declare its fixed batch/chunk size and measured peak-memory gate before GPU execution. Those runtime constants cannot be tuned against VALIDATION outcomes.

## Interpretation boundary

A successful TRAIN-to-VALIDATION PC1 transfer would show that a dominant direction estimated independently on TRAIN remains measurable on frozen VALIDATION. It would not establish semantic generalization, causal usefulness, generation quality, personality learning or model improvement.

A weak transfer would show that the V72/V73 VALIDATION-fitted geometry was not fully stable across splits. It would not imply that the underlying model representation is useless.

Teacher-forced lexical top-1 scoring remains a narrow diagnostic.

## Verified V75 result - 2026-11-07

Immutable scientific GOGIT --> [PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001](../reports/assistant-results/history/PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json)

Publication commit --> [`187b53ccfd90`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/187b53ccfd90c38ffea32e9eb65e8672caba740b)

The frozen 30-field report passed all declared reference and safety gates.

| Metric | Verified value |
| --- | ---: |
| V75_PASS | 1 |
| TRAIN lexical positions | 294726 |
| VALIDATION lexical positions | 9170 |
| Hidden dimension | 128 |
| ORIGINAL correct | 2673 |
| ORIGINAL distinct predicted IDs | 5 |
| ORIGINAL dominant top-1 share | 72.55% |
| TRAIN_CENTER correct | 2784 |
| TRAIN_CENTER distinct predicted IDs | 16 |
| TRAIN_CENTER dominant top-1 share | 56.76% |
| TRAIN_PC1_ONLY correct | 2457 |
| TRAIN_PC1_ONLY distinct predicted IDs | 2 |
| TRAIN_PC1_ONLY dominant top-1 share | 70.43% |
| TRAIN_MINUS_PC1 correct | 611 |
| TRAIN_MINUS_PC1 distinct predicted IDs | 663 |
| TRAIN_MINUS_PC1 dominant top-1 share | 9.66% |
| TRAIN_UNIGRAM correct | 2535 |
| TRAIN_PC1 / unigram argmax agreement | 6458 |
| TRAIN_PC1 / unigram shared correct | 2451 |
| VALIDATION-fitted PC1 correct replay | 2455 |
| abs cosine(TRAIN PC1, VALIDATION PC1) | 99.95% |
| TRAIN PC1 centered variance share | 90.19% |
| VALIDATION PC1 centered variance share | 82.88% |
| Coverage | 100.00% |
| Training started | 0 |
| BLIND access | 0 |

### Scientific interpretation

The dominant hidden-state direction is **not primarily an artifact of fitting PCA on VALIDATION**. The independently fitted TRAIN PC1 is almost collinear with the VALIDATION-fitted PC1, with an absolute cosine alignment of 99.95%.

The transfer is also visible at the output layer. TRAIN_PC1_ONLY obtains 2457 correct predictions, versus 2455 for the frozen VALIDATION-fitted PC1 replay, with two distinct predicted IDs in both cases and essentially the same dominant-token concentration.

Removing the TRAIN-derived PC1 produces a much more diverse output distribution - 663 distinct predicted IDs - but lexical top-1 accuracy falls to 611/9170. This confirms that the dominant direction carries a large fraction of the model's current teacher-forced predictive behavior.

The result does **not** demonstrate semantic generalization or useful representation quality. V74's frequency-prior control remains highly relevant: TRAIN_PC1_ONLY still closely tracks the context-free TRAIN unigram baseline, with 6458 matching argmax predictions and 2451 shared correct predictions.

The supported conclusion is therefore narrow --> the V72/V73 anisotropy is a stable cross-split geometric property of the frozen V62 representation, strongly associated with output-frequency concentration. It is not evidence of conversational competence, personality formation or a causal semantic feature.

No checkpoint changed. No optimizer step occurred. BLIND remained closed.

### Publication state

V75 is **closed**.

- START --> [GitHub Discussion #6](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6), receipt [V75-start.json](../automation/dev-flow/receipts/V75-start.json)
- Scientific GOGIT --> [PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001](../reports/assistant-results/history/PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json), commit [`187b53ccfd90`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/187b53ccfd90c38ffea32e9eb65e8672caba740b)
- FINAL preflight --> [PHASE03-SMOLTALK-V75-FINAL-PREFLIGHT-001](../reports/assistant-results/history/PHASE03-SMOLTALK-V75-FINAL-PREFLIGHT-001.json), PASS
- FINAL request --> [V75-final.json](../automation/dev-flow/requests/V75-final.json), source commit [`0ddf24b8d3f8`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/0ddf24b8d3f897e15810267658fe24b3d5a1608e)
- GitHub FINAL --> [Discussion #6 comment #19458251](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6#discussioncomment-19458251)
- FINAL receipt --> [V75-final.json](../automation/dev-flow/receipts/V75-final.json), commit [`7c1265603ff1`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/7c1265603ff102ebe54d9bd87b845e885c593c8f)
- KUZ-DIN delivery audit --> [KUZ-DIN-V75-FINAL-DELIVERY-001](https://github.com/Kusanagi8200/KUZ-DIN/blob/main/reports/assistant-results/history/KUZ-DIN-V75-FINAL-DELIVERY-001.json), commit [`e299747256f9`](https://github.com/Kusanagi8200/KUZ-DIN/commit/e299747256f9b9948d80eabfcd3f9c83921c2618)
- LinkedIn FINAL --> journal event `close-V75-d6-c19458251` verified `PUBLISHED`, valid LinkedIn URN present
- KUZ-DIN journal --> 4 total DEV-FLOW publications, 0 PREPARED, 0 IN_FLIGHT; V75 has exactly 2 published events
- QUEUE and DELIVERY timers --> enabled and active

Do not recreate or replay V75 START or FINAL.

## Authorization boundary

Historical V75 authorizations are fully consumed and closed.

START-DEV-FLOW, the bounded read-only GPU scientific run and FINAL-DEV-FLOW were separately authorized and completed. None of these authorizations carries forward to V76 or to any new training run.

V62 remains frozen. No optimizer step, checkpoint modification or BLIND access is authorized by the V75 closure.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
