# Mini-Kuzai Phase 03 - V78 Identical-Context Rebatching Numerical Control 001

Date --> 2026-11-07
Frozen review --> 2026-11-07

Status --> **PROTOCOL FROZEN / START AUTHORIZED BY OPERATOR / CPU PREFLIGHT ONLY AFTER START / GPU NOT AUTHORIZED / NO TRAINING / NO BLIND ACCESS**

## Why V78 follows V77

V77 tested the frozen V76 frequency-residualized PC1 signal under one deterministic context-order intervention.

The verified V77 result is immutable:

- V77 PASS --> 1
- VALIDATION lexical positions --> 9170
- prefixes actually perturbed --> 9062
- prefixes unchanged because they were too short --> 108
- FULL_CONTEXT correct --> 2594
- REVERSE_HISTORY_KEEP_LAST correct --> 2594
- shared correct --> 2594
- FULL-only correct --> 0
- REVERSE-only correct --> 0
- top-1 prediction agreement --> 9165 / 9170
- top-1 prediction changes --> 5 / 9170
- alpha sign agreement --> 9165 / 9170
- alpha sign changes --> 5 / 9170
- absolute alpha correlation --> 9999 basis points
- positions with alpha delta above 1e-7 --> 9123 / 9170
- FULL dominant share --> 7043 basis points
- REVERSE dominant share --> 7046 basis points
- TRAINING_STARTED --> 0
- BLIND access --> 0

The important numerical observation is that 9123 alpha coordinates changed above 1e-7 while only 9062 prefixes were actually perturbed.

That means the V77 alpha-delta count cannot be interpreted purely as context-order sensitivity. At least some small numerical differences may come from the fact that FULL_CONTEXT and the counterfactual prefix path use different batching/execution shapes on CUDA/BF16.

V78 isolates that numerical floor before any stronger interpretation of V77.

## Frozen scientific question

**When the exact same frozen VALIDATION prefixes are evaluated through the two execution paths used by V77, how much numerical and decision-level variation is produced by rebatching alone?**

V78 is a numerical-control experiment.

It is not:

- a new context perturbation
- new training
- a tokenizer experiment
- a generation benchmark
- a semantic evaluation
- a BLIND evaluation
- a model patch
- a claim about language understanding

## Frozen inheritance

V78 must reuse without modification:

- the stopped V62 cycle-2 checkpoint
- V62 optimizer steps --> 69
- V62 exposure tokens --> 597982
- VALIDATION lexical positions --> 9170
- hidden dimension --> 128
- output vocabulary --> 1024
- V75 TRAIN hidden-state mean and PC1 axis
- V76 TRAIN-only lexical-frequency construction
- V76 FP64 residualization
- V76 frequency-residualized output profile
- V77 exact prefix extraction and prefix-scoring path
- V77 immutable scientific GOGIT report

BLIND remains closed.

Any mismatch in V62, V75, V76 or V77 frozen provenance blocks V78.

## Frozen paired execution paths

For every one of the 9170 frozen VALIDATION lexical targets, V78 evaluates exactly the same logical teacher-forced prefix twice.

### PATH_A_FULL_CONTEXT

Use the normal frozen FULL_CONTEXT evaluation path inherited from V77.

- validation batch --> 4
- original token order
- original target
- no prefix transformation
- no generation

### PATH_B_REBATCH_IDENTICAL

Use the V77 counterfactual-prefix execution path, but do **not** reverse or otherwise modify any token.

- prefix batch --> 32
- exact same prefix tokens as PATH_A
- exact same token order as PATH_A
- exact same prefix length
- exact same target
- exact same BOS and immediate predecessor
- no token insertion, deletion, replacement or reordering

Before inference, V78 must verify for every position that the PATH_B prefix is byte-for-byte / integer-token-for-integer-token identical to the logical PATH_A prefix represented for that target.

The only intended difference is execution shape and batching path.

## Frozen scoring

V78 must recompute the exact V76 frequency-residualized PC1 output profile before paired scoring.

Let:

- `mu_train` --> frozen TRAIN hidden-state mean
- `u_train` --> frozen TRAIN leading PC1
- `r` --> frozen V76 frequency-residualized output profile
- `h_a` --> hidden state produced by PATH_A_FULL_CONTEXT
- `h_b` --> hidden state produced by PATH_B_REBATCH_IDENTICAL

Define:

`alpha_a = (h_a - mu_train) dot u_train`

`alpha_b = (h_b - mu_train) dot u_train`

Score:

`logits_a = alpha_a * r`

`logits_b = alpha_b * r`

The target, logical prefix, residual profile and model weights are identical in both paths.

Only the execution/batching path differs.

## Required replay

Before accepting any V78 numerical-control metric, PATH_A_FULL_CONTEXT must reproduce the verified V76/V77 baseline exactly:

- lexical positions --> 9170
- correct --> 2594
- distinct predicted IDs --> 2
- dominant top-1 share --> 7043 basis points

The V76 frequency-residualized construction must also replay its frozen provenance internally.

If PATH_A fails exact replay, V78 must abort without scientific GOGIT publication.

## Frozen numerical comparison

V78 measures the numerical floor at three alpha thresholds:

- `abs(alpha_a - alpha_b) > 1e-7`
- `abs(alpha_a - alpha_b) > 1e-6`
- `abs(alpha_a - alpha_b) > 1e-5`

It also reports:

- maximum absolute alpha delta, scaled to integer nano-units --> round(max_delta * 1e9)
- mean absolute alpha delta, scaled to integer nano-units --> round(mean_delta * 1e9)
- absolute centered Pearson correlation between PATH_A and PATH_B alpha coordinates
- alpha sign agreement / sign change
- top-1 prediction agreement / change
- paired correctness migration

No raw alpha values or per-position records may be published.

## Frozen 30-field GOGIT schema

STEP_ID --> `PHASE03-SMOLTALK-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001`

The scientific publication must contain exactly these 30 aggregate nonnegative integer metrics:

1. `SEMANTIC_VALIDATION_COMPLETE`
2. `TRAINING_AUTHORIZED`
3. `TRAINING_STARTED`
4. `V78_PASS`
5. `V78_BLIND_ACCESS`
6. `V78_VAL_LEXICAL`
7. `V78_PATH_A_BATCH`
8. `V78_PATH_B_BATCH`
9. `V78_PATH_A_CORRECT`
10. `V78_PATH_A_DISTINCT`
11. `V78_PATH_A_TOP1_SHARE_BP`
12. `V78_PATH_B_CORRECT`
13. `V78_PATH_B_DISTINCT`
14. `V78_PATH_B_TOP1_SHARE_BP`
15. `V78_PRED_AGREE`
16. `V78_PRED_CHANGED`
17. `V78_SHARED_CORRECT`
18. `V78_A_ONLY_CORRECT`
19. `V78_B_ONLY_CORRECT`
20. `V78_ALPHA_SIGN_AGREE`
21. `V78_ALPHA_SIGN_CHANGED`
22. `V78_ALPHA_CORR_ABS_BP`
23. `V78_ALPHA_DELTA_GT_1E7`
24. `V78_ALPHA_DELTA_GT_1E6`
25. `V78_ALPHA_DELTA_GT_1E5`
26. `V78_ALPHA_MAX_ABS_NANO`
27. `V78_ALPHA_MEAN_ABS_NANO`
28. `V78_IDENTICAL_PREFIXES`
29. `V78_INPUT_MATCHES`
30. `V78_COVERAGE_BP`

## Frozen fixed expectations

A successful V78 scientific GOGIT must require:

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V78_PASS=1`
- `V78_BLIND_ACCESS=0`
- `V78_VAL_LEXICAL=9170`
- `V78_PATH_A_BATCH=4`
- `V78_PATH_B_BATCH=32`
- `V78_PATH_A_CORRECT=2594`
- `V78_PATH_A_DISTINCT=2`
- `V78_PATH_A_TOP1_SHARE_BP=7043`
- `V78_IDENTICAL_PREFIXES=9170`
- `V78_INPUT_MATCHES=9170`
- `V78_COVERAGE_BP=10000`

No expected outcome is frozen for PATH_B accuracy, alpha deltas, correlation, sign changes or top-1 changes.

`V78_PASS=1` means only that provenance, exact-input identity, replay, paired accounting, numerical validity, resource limits and full coverage passed.

## Interpretation rule

V78 provides a direct numerical baseline for interpreting V77.

If V78 itself produces top-1 or sign changes under identical logical inputs, then part or all of the five V77 discrete changes may be attributable to execution-path numerics.

If V78 produces no discrete changes and alpha deltas are materially smaller than V77, then the V77 discrete differences become stronger evidence of sensitivity to the reverse-history intervention.

If V78 produces similar alpha-delta counts to V77 but no top-1 changes, then the 1e-7 threshold is primarily measuring low-level numerical noise and should not be used alone as evidence of context sensitivity.

V78 does not establish semantic competence under any outcome.

## Frozen CPU implementation review requirements

Before any GPU authorization, CPU-only tests must verify at minimum:

1. exact 30-field schema and GOGIT allowlist compatibility
2. V76/V77 dependency and Git-blob pins
3. exact V77 report replay values
4. construction of PATH_B without any token mutation
5. exact token-for-token prefix identity across both logical paths
6. exact target identity
7. exact prefix length identity
8. exact BOS and immediate-predecessor identity
9. batch A fixed at 4
10. batch B fixed at 32
11. three frozen alpha-delta thresholds
12. nano-unit scaling and overflow bounds
13. sign classification including exact zero
14. paired correctness accounting
15. Pearson correlation numerical gates
16. fail-closed nonfinite handling
17. no BLIND path or import
18. no optimizer, training, generation or checkpoint-write path
19. no raw token text, hidden vectors, alpha vectors or per-position output in public metrics
20. scientific GOGIT absent before GPU authorization

CPU preflight is not GPU authorization.

## Frozen runtime and resource boundary

A future V78 scientific implementation must remain bounded and read-only:

- one CUDA device only
- unchanged V62 checkpoint
- evaluation/inference only
- `torch.set_grad_enabled(False)`
- inference/no-grad contexts
- PATH_A batch --> 4
- PATH_B batch --> 32
- score chunk --> 512
- GPU peak-memory hard ceiling --> 6144 MiB
- no optimizer
- no checkpoint write
- no model-weight mutation
- no BLIND access
- no generation
- no raw token text
- no per-position publication
- exact 30 allowlisted integer metrics only
- GOGIT process budget --> 300 seconds
- OOM, timeout, nonfinite value, provenance mismatch, replay mismatch or input-identity failure --> abort without scientific GOGIT

## Authorization boundary

The operator has explicitly authorized **START-DEV-FLOW V78**.

That authorization permits:

- committing this frozen V78 protocol
- committing the reviewed V78 START source
- committing an exact V78 START request
- publishing one V78 START DEV-FLOW event
- preparing implementation and CPU-only preflight after START receipt verification

It does **not** authorize:

- V78 scientific GPU execution
- new model training
- optimizer steps
- checkpoint modification
- BLIND access
- generation
- FINAL-DEV-FLOW V78
- any scientific success claim

GPU execution requires a later explicit operator authorization after a verified CPU preflight.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
