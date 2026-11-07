# Mini-Kuzai Phase 03 - V79 Same-Path Context-Order Control 001

Date --> 2026-11-07
Frozen review --> 2026-11-07

Status --> **PROTOCOL FROZEN / START NOT AUTHORIZED / NO GPU AUTHORIZATION / NO TRAINING / NO BLIND ACCESS**

## Why V79 follows V78

V77 measured the V76 frequency-residualized PC1 signal under the deterministic `REVERSE_HISTORY_KEEP_LAST` context-order intervention.

Its verified result showed:

- VALIDATION lexical positions --> 9170
- prefixes actually perturbed --> 9062
- unchanged short prefixes --> 108
- FULL_CONTEXT correct --> 2594
- REVERSE_HISTORY_KEEP_LAST correct --> 2594
- prediction changes --> 5
- alpha sign changes --> 5
- absolute alpha correlation --> 9999 basis points
- FULL dominant share --> 7043 basis points
- REVERSE dominant share --> 7046 basis points
- TRAINING_STARTED --> 0
- BLIND access --> 0

However, V77 compared two different execution paths:

- normal FULL_CONTEXT evaluation at batch 4
- prefix/counterfactual evaluation at batch 32

V78 then measured the numerical floor created by those two execution paths while keeping every logical prefix identical.

The verified V78 result is immutable:

- V78 PASS --> 1
- VALIDATION lexical positions --> 9170
- identical prefixes --> 9170
- input matches --> 9170
- PATH_A batch --> 4
- PATH_B batch --> 32
- PATH_A correct --> 2594
- PATH_B correct --> 2594
- PATH_A distinct predicted IDs --> 2
- PATH_B distinct predicted IDs --> 2
- PATH_A dominant share --> 7043 basis points
- PATH_B dominant share --> 7043 basis points
- prediction changes --> 0
- alpha sign changes --> 0
- absolute alpha correlation --> 10000 basis points
- alpha delta above 1e-7 --> 4107
- alpha delta above 1e-6 --> 1226
- alpha delta above 1e-5 --> 1209
- maximum absolute alpha delta --> 10442495 nano-units
- mean absolute alpha delta --> 238663 nano-units
- TRAINING_STARTED --> 0
- BLIND access --> 0

V78 therefore showed that rebatching/execution-path differences create continuous alpha noise but did not change a single top-1 prediction or alpha sign.

The five discrete changes observed in V77 are therefore not explained by rebatching alone.

V79 removes the remaining path asymmetry.

## Frozen scientific question

**When ORIGINAL and REVERSE_HISTORY_KEEP_LAST prefixes are evaluated through the exact same frozen prefix-scoring path, with the same batch size and scoring pipeline, do the five V77 discrete changes persist?**

V79 is a same-path context-order control.

It is not:

- new training
- a tokenizer experiment
- a generation benchmark
- a semantic evaluation
- a BLIND evaluation
- a model patch
- evidence that context sensitivity implies language understanding

## Frozen inheritance

V79 must reuse without modification:

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
- V77 `REVERSE_HISTORY_KEEP_LAST` transformation
- V78 prefix-scoring path
- V77 immutable scientific GOGIT report
- V78 immutable scientific GOGIT report

BLIND remains closed.

Any mismatch in V62, V75, V76, V77 or V78 frozen provenance blocks V79.

## Frozen paired execution

For every frozen VALIDATION lexical target, construct two logical prefixes.

### ORIGINAL_SAME_PATH

Use the original teacher-forced prefix without transformation.

Evaluate it through the exact prefix-scoring path used by V78 PATH_B.

- prefix scorer only
- batch --> 32
- original token order
- original prefix length
- original target
- no generation

### REVERSE_SAME_PATH

Construct the exact V77 deterministic counterfactual:

`p_rev = [BOS] + reverse([x1, ..., x(n-2)]) + [x(n-1)]`

For prefixes shorter than three tokens total, leave the prefix unchanged.

Evaluate the transformed prefix through the **same prefix scorer** used for ORIGINAL_SAME_PATH.

- same prefix scorer
- same batch --> 32
- same target
- same prefix length
- same token multiset
- same BOS
- same immediate preceding token
- no insertion, deletion or replacement
- no generation

The only intended logical difference between the two modes is the order of earlier history tokens.

No FULL_CONTEXT batch-4 path is used for the paired V79 comparison.

## Required replay

Before accepting any V79 context-order metric, ORIGINAL_SAME_PATH must reproduce the verified V78 PATH_B baseline exactly:

- lexical positions --> 9170
- correct --> 2594
- distinct predicted IDs --> 2
- dominant top-1 share --> 7043 basis points
- batch --> 32

The V76 frequency-residualized profile and all V77/V78 provenance gates must also replay successfully.

If ORIGINAL_SAME_PATH fails exact replay, V79 must abort without scientific GOGIT publication.

## Frozen perturbation invariants

Across all 9170 pairs, V79 must verify:

- target unchanged
- prefix length unchanged
- prefix token multiset unchanged
- BOS remains first
- immediate preceding token remains last
- no PAD/BOS/EOS introduced into the interior
- 9062 prefixes are actually perturbed
- 108 prefixes remain unchanged because they are too short

These counts are inherited as required replay invariants from V77.

## Frozen scoring

Let:

- `mu_train` --> frozen TRAIN hidden-state mean
- `u_train` --> frozen TRAIN leading PC1
- `r` --> frozen V76 frequency-residualized output profile
- `h_original` --> hidden state from ORIGINAL_SAME_PATH
- `h_reverse` --> hidden state from REVERSE_SAME_PATH

Define:

`alpha_original = (h_original - mu_train) dot u_train`

`alpha_reverse = (h_reverse - mu_train) dot u_train`

Score:

`logits_original = alpha_original * r`

`logits_reverse = alpha_reverse * r`

The model, target, residual profile, scorer, batch size and execution path are identical across both modes.

Only earlier-context order may differ.

## Frozen numerical comparison

V79 reports:

- top-1 prediction agreement and changes
- correctness retained, lost or gained
- alpha sign agreement and changes
- absolute centered Pearson correlation
- alpha deltas above `1e-7`
- alpha deltas above `1e-6`
- alpha deltas above `1e-5`
- maximum absolute alpha delta in integer nano-units
- mean absolute alpha delta in integer nano-units

The three thresholds are numerical descriptors, not success thresholds.

No raw token text, hidden vectors, alpha vectors or per-position records may be published.

## Frozen 30-field GOGIT schema

STEP_ID --> `PHASE03-SMOLTALK-V79-SAME-PATH-CONTEXT-ORDER-CONTROL-001`

The scientific publication must contain exactly these 30 aggregate nonnegative integer metrics:

1. `SEMANTIC_VALIDATION_COMPLETE`
2. `TRAINING_AUTHORIZED`
3. `TRAINING_STARTED`
4. `V79_PASS`
5. `V79_BLIND_ACCESS`
6. `V79_VAL_LEXICAL`
7. `V79_SAME_PATH_BATCH`
8. `V79_PERTURBED_PREFIXES`
9. `V79_UNCHANGED_PREFIXES`
10. `V79_ORIGINAL_CORRECT`
11. `V79_ORIGINAL_DISTINCT`
12. `V79_ORIGINAL_TOP1_SHARE_BP`
13. `V79_REVERSE_CORRECT`
14. `V79_REVERSE_DISTINCT`
15. `V79_REVERSE_TOP1_SHARE_BP`
16. `V79_PRED_AGREE`
17. `V79_PRED_CHANGED`
18. `V79_SHARED_CORRECT`
19. `V79_ORIGINAL_ONLY_CORRECT`
20. `V79_REVERSE_ONLY_CORRECT`
21. `V79_ALPHA_SIGN_AGREE`
22. `V79_ALPHA_SIGN_CHANGED`
23. `V79_ALPHA_CORR_ABS_BP`
24. `V79_ALPHA_DELTA_GT_1E7`
25. `V79_ALPHA_DELTA_GT_1E6`
26. `V79_ALPHA_DELTA_GT_1E5`
27. `V79_ALPHA_MAX_ABS_NANO`
28. `V79_ALPHA_MEAN_ABS_NANO`
29. `V79_INPUT_INVARIANTS`
30. `V79_COVERAGE_BP`

## Frozen fixed expectations

A successful V79 scientific GOGIT must require:

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V79_PASS=1`
- `V79_BLIND_ACCESS=0`
- `V79_VAL_LEXICAL=9170`
- `V79_SAME_PATH_BATCH=32`
- `V79_PERTURBED_PREFIXES=9062`
- `V79_UNCHANGED_PREFIXES=108`
- `V79_ORIGINAL_CORRECT=2594`
- `V79_ORIGINAL_DISTINCT=2`
- `V79_ORIGINAL_TOP1_SHARE_BP=7043`
- `V79_INPUT_INVARIANTS=9170`
- `V79_COVERAGE_BP=10000`

No expected outcome is frozen for REVERSE accuracy, prediction changes, sign changes, correlation or alpha deltas.

In particular, V79 must **not** require the five V77 changed predictions to reproduce.

## Interpretation rule

V79 directly tests whether the V77 discrete order effect persists after removing the execution-path asymmetry.

If V79 again produces approximately five discrete prediction/sign changes, the evidence for genuine sensitivity to the reverse-history intervention becomes stronger.

If V79 produces zero discrete changes, then the V77 result likely depended on an interaction between the context perturbation and execution-path numerics rather than context order alone.

If V79 produces a different small nonzero count, the correct interpretation is that the residual signal is weakly order-sensitive near decision boundaries, with exact discrete outcomes sensitive to numerical execution details.

Under every outcome:

- V79 remains a teacher-forced numerical diagnostic
- sensitivity does not establish correct context use
- sensitivity does not establish semantic competence
- sensitivity does not establish reasoning
- V79 does not authorize new training

## Frozen CPU implementation review requirements

Before any GPU authorization, CPU-only tests must verify at minimum:

1. exact 30-field schema and GOGIT allowlist compatibility
2. V77/V78 dependency and Git-blob pins
3. exact V78 PATH_B replay requirements
4. exact V77 perturbation counts
5. deterministic REVERSE_HISTORY_KEEP_LAST transformation
6. both modes use the same prefix scorer
7. both modes use batch 32
8. no paired FULL_CONTEXT batch-4 execution
9. target preservation
10. prefix length preservation
11. prefix token-multiset preservation
12. BOS preservation
13. immediate-predecessor preservation
14. unchanged behavior for short prefixes
15. three frozen alpha-delta thresholds
16. nano-unit scaling and overflow bounds
17. alpha sign classification including exact zero
18. paired correctness accounting
19. Pearson correlation numerical gates
20. fail-closed nonfinite handling
21. no BLIND path or import
22. no optimizer, training, generation or checkpoint-write path
23. no raw token text, hidden vectors, alpha vectors or per-position publication
24. scientific GOGIT absent before GPU authorization

CPU preflight is not GPU authorization.

## Frozen runtime and resource boundary

A future V79 scientific implementation must remain bounded and read-only:

- one CUDA device only
- unchanged V62 checkpoint
- evaluation/inference only
- `torch.set_grad_enabled(False)`
- inference/no-grad contexts
- ORIGINAL prefix batch --> 32
- REVERSE prefix batch --> 32
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
- OOM, timeout, nonfinite value, provenance mismatch, replay mismatch or perturbation-invariant failure --> abort without scientific GOGIT

## Authorization boundary

V79 is **prepared only**.

The operator has not authorized START-DEV-FLOW V79.

This preparation permits only:

- committing this frozen protocol
- committing a reviewed V79 START source
- documentation updates describing V79 as prepared

It does not authorize:

- creating a V79 START request
- publishing a V79 GitHub Discussion
- publishing a V79 LinkedIn START
- V79 implementation execution
- V79 CPU preflight execution
- V79 GPU execution
- training or optimizer steps
- checkpoint modification
- BLIND access
- generation
- FINAL-DEV-FLOW V79

A separate explicit operator authorization is required before START-DEV-FLOW V79.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
