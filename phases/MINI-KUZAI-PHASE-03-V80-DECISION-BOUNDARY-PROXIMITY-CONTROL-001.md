# Mini-Kuzai Phase 03 - V80 Decision-Boundary Proximity Control 001

Date --> 2026-11-07
Frozen review --> 2026-11-07

Status --> **SCIENTIFIC GOGIT VERIFIED / START PUBLISHED / NO TRAINING / NO BLIND ACCESS / NO GENERATION / FINAL NOT AUTHORIZED**

## Why V80 follows V79

V79 removed the remaining execution-path asymmetry from the V77 reverse-history control.

Its verified result is immutable:

- V79 PASS --> 1
- VALIDATION lexical positions --> 9170
- same-path batch --> 32
- perturbed prefixes --> 9062
- unchanged prefixes --> 108
- ORIGINAL correct --> 2594
- REVERSE correct --> 2594
- ORIGINAL distinct predicted IDs --> 2
- REVERSE distinct predicted IDs --> 2
- ORIGINAL dominant share --> 7043 basis points
- REVERSE dominant share --> 7046 basis points
- prediction changes --> 5
- alpha sign changes --> 5
- shared correct --> 2594
- ORIGINAL-only correct --> 0
- REVERSE-only correct --> 0
- absolute alpha correlation --> 9999 basis points
- alpha delta above 1e-7 --> 9062
- alpha delta above 1e-6 --> 9062
- alpha delta above 1e-5 --> 9057
- maximum absolute alpha delta --> 1086937904 nano-units
- mean absolute alpha delta --> 49932920 nano-units
- TRAINING_STARTED --> 0
- BLIND access --> 0

The five discrete changes therefore persist when ORIGINAL and REVERSE_HISTORY_KEEP_LAST use the exact same scorer and batch size.

Because the frozen residual score is:

`logits = alpha * residual_profile`

and the residual profile yields only two top-1 output IDs, a top-1 switch is expected when the sign of `alpha` crosses zero.

V79 observed exactly five prediction changes and exactly five alpha-sign changes.

The unresolved question is therefore whether those sign crossings occur only very close to the decision boundary or whether the context-order intervention can move the residual coordinate across zero from a substantial distance.

## Frozen scientific question

**Are the five V79 prediction/sign changes confined to positions whose ORIGINAL or REVERSE alpha coordinate is close to zero, or do any sign changes occur far from the alpha=0 decision boundary?**

V80 is a decision-boundary proximity control.

It is not:

- new training
- a semantic evaluation
- a BLIND evaluation
- a generation benchmark
- a model patch
- a causal language-understanding claim
- evidence of reasoning
- evidence that the residual feature should be kept or removed

## Frozen inheritance

V80 must reuse without modification:

- stopped V62 cycle-2 checkpoint
- V62 optimizer steps --> 69
- V62 exposure tokens --> 597982
- VALIDATION lexical positions --> 9170
- hidden dimension --> 128
- output vocabulary --> 1024
- V75 TRAIN hidden-state mean
- V75 TRAIN PC1 axis
- V76 TRAIN-only lexical-frequency construction
- V76 FP64 frequency residualization
- V76 frequency-residualized output profile
- V77 REVERSE_HISTORY_KEEP_LAST transformation
- V79 exact same-path prefix scorer
- V79 batch --> 32
- V79 immutable scientific GOGIT report

BLIND remains closed.

Any mismatch in V62, V75, V76, V77 or V79 frozen provenance blocks V80.

## Frozen paired execution

V80 must reconstruct exactly the V79 pair for all 9170 frozen VALIDATION lexical positions.

### ORIGINAL_SAME_PATH

- original teacher-forced prefix
- frozen V79 prefix scorer
- batch --> 32
- unchanged target
- no generation

### REVERSE_SAME_PATH

`p_rev = [BOS] + reverse([x1, ..., x(n-2)]) + [x(n-1)]`

For prefixes shorter than three tokens total, the prefix remains unchanged.

Both modes must preserve:

- same target
- same prefix length
- same token multiset
- same BOS
- same immediate preceding token
- same scorer
- same batch
- same checkpoint
- no insertion, deletion or replacement
- no generation

## Required V79 replay

Before accepting any V80 boundary metric, the following V79 values must replay exactly:

- lexical positions --> 9170
- batch --> 32
- perturbed prefixes --> 9062
- unchanged prefixes --> 108
- ORIGINAL correct --> 2594
- REVERSE correct --> 2594
- ORIGINAL distinct --> 2
- REVERSE distinct --> 2
- ORIGINAL dominant share --> 7043 basis points
- REVERSE dominant share --> 7046 basis points
- prediction changes --> 5
- alpha sign changes --> 5
- shared correct --> 2594
- ORIGINAL-only correct --> 0
- REVERSE-only correct --> 0
- absolute alpha correlation --> 9999 basis points

If replay fails, V80 must abort without scientific GOGIT publication.

## Frozen scoring

Let:

- `mu_train` --> frozen TRAIN hidden-state mean
- `u_train` --> frozen TRAIN PC1
- `r` --> frozen V76 frequency-residualized output profile
- `h_original` --> ORIGINAL hidden state
- `h_reverse` --> REVERSE hidden state

Define:

`alpha_original = (h_original - mu_train) dot u_train`

`alpha_reverse = (h_reverse - mu_train) dot u_train`

For every pair define:

`boundary_distance = min(abs(alpha_original), abs(alpha_reverse))`

and:

`crossing_span = max(abs(alpha_original), abs(alpha_reverse))`

A sign-changing pair is a pair where the exact three-class sign differs:

- negative
- zero
- positive

## Frozen boundary thresholds

Boundary proximity is measured using cumulative thresholds frozen before execution:

- <= 1e-7
- <= 1e-6
- <= 1e-5
- <= 1e-4
- <= 1e-3

These thresholds are descriptive only.

They are not pass/fail success thresholds and may not be adjusted after seeing the results.

## Frozen measurements

V80 reports:

- exact V79 replay counts
- number of all positions within each boundary-distance threshold
- number of the five changed predictions within each threshold
- number of the five sign changes within each threshold
- maximum boundary distance among changed positions
- mean boundary distance among changed positions
- maximum crossing span among changed positions
- mean crossing span among changed positions

Distances and spans are published only as integer nano-units.

No raw alpha values, token text, hidden vectors, per-position predictions or per-position records may be published.

## Frozen 30-field GOGIT schema

STEP_ID --> `PHASE03-SMOLTALK-V80-DECISION-BOUNDARY-PROXIMITY-CONTROL-001`

The scientific publication must contain exactly these 30 aggregate nonnegative integer metrics:

1. `SEMANTIC_VALIDATION_COMPLETE`
2. `TRAINING_AUTHORIZED`
3. `TRAINING_STARTED`
4. `V80_PASS`
5. `V80_BLIND_ACCESS`
6. `V80_VAL_LEXICAL`
7. `V80_SAME_PATH_BATCH`
8. `V80_PERTURBED_PREFIXES`
9. `V80_UNCHANGED_PREFIXES`
10. `V80_V79_PRED_CHANGED_REPLAY`
11. `V80_V79_SIGN_CHANGED_REPLAY`
12. `V80_V79_ORIGINAL_CORRECT_REPLAY`
13. `V80_V79_REVERSE_CORRECT_REPLAY`
14. `V80_ALL_WITHIN_1E7`
15. `V80_ALL_WITHIN_1E6`
16. `V80_ALL_WITHIN_1E5`
17. `V80_ALL_WITHIN_1E4`
18. `V80_ALL_WITHIN_1E3`
19. `V80_CHANGED_WITHIN_1E7`
20. `V80_CHANGED_WITHIN_1E6`
21. `V80_CHANGED_WITHIN_1E5`
22. `V80_CHANGED_WITHIN_1E4`
23. `V80_CHANGED_WITHIN_1E3`
24. `V80_SIGN_WITHIN_1E7`
25. `V80_SIGN_WITHIN_1E6`
26. `V80_SIGN_WITHIN_1E5`
27. `V80_BOUNDARY_MAX_NANO_CHANGED`
28. `V80_BOUNDARY_MEAN_NANO_CHANGED`
29. `V80_CROSSING_MAX_NANO_CHANGED`
30. `V80_CROSSING_MEAN_NANO_CHANGED`

## Frozen fixed expectations

A successful V80 scientific GOGIT must require:

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V80_PASS=1`
- `V80_BLIND_ACCESS=0`
- `V80_VAL_LEXICAL=9170`
- `V80_SAME_PATH_BATCH=32`
- `V80_PERTURBED_PREFIXES=9062`
- `V80_UNCHANGED_PREFIXES=108`
- `V80_V79_PRED_CHANGED_REPLAY=5`
- `V80_V79_SIGN_CHANGED_REPLAY=5`
- `V80_V79_ORIGINAL_CORRECT_REPLAY=2594`
- `V80_V79_REVERSE_CORRECT_REPLAY=2594`

No scientific outcome is frozen for the boundary-distance counts or nano-unit summaries.

`V80_PASS=1` means only that provenance, exact V79 replay, boundary accounting, numerical safety and full coverage completed.

## Interpretation rule

If all five changed/sign-changing positions fall within the smallest boundary bins, the correct interpretation is that the V79 discrete effect is concentrated at numerically fragile decision boundaries.

If the changes require progressively wider bins but remain close to zero relative to the observed alpha scale, the correct interpretation is weak context-order sensitivity expressed primarily near the decision boundary.

If one or more sign changes remain outside 1e-3, the intervention has moved the residual coordinate across zero from a materially larger distance and the weak-order-sensitivity interpretation should be revisited.

Under every outcome:

- V80 remains teacher-forced
- V80 does not establish semantic competence
- V80 does not establish correct context use
- V80 does not establish reasoning
- V80 does not authorize training
- V80 does not authorize BLIND access

## Frozen CPU implementation review requirements

Before any GPU authorization, CPU-only tests must verify at minimum:

1. exact 30-field schema
2. GOGIT allowlist compatibility
3. V79 report dependency and immutable provenance
4. exact V79 replay requirements
5. exact same-path scorer and batch 32
6. deterministic REVERSE_HISTORY_KEEP_LAST transformation
7. exact three-class sign handling including zero
8. boundary-distance definition
9. crossing-span definition
10. cumulative threshold behavior
11. threshold immutability
12. nano-unit integer scaling
13. bounded integer publication range
14. empty-changed-set fail-closed handling
15. nonfinite fail-closed handling
16. no BLIND path or import
17. no optimizer
18. no training path
19. no generation
20. no checkpoint write
21. no raw alpha/vector/token publication
22. scientific GOGIT absent before GPU authorization

CPU preflight is not GPU authorization.

## Frozen runtime and resource boundary

A future V80 scientific implementation must remain bounded and read-only:

- one CUDA device only
- unchanged V62 checkpoint
- evaluation/inference only
- `torch.set_grad_enabled(False)`
- inference/no-grad contexts
- ORIGINAL batch --> 32
- REVERSE batch --> 32
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
- OOM, timeout, nonfinite value, provenance mismatch or replay mismatch --> abort without scientific GOGIT

## Authorization boundary

The operator explicitly authorized **START-DEV-FLOW V80**.

Verified START state:

- START request --> committed
- GitHub Discussion --> #11
- START receipt --> `PUBLISHED`
- source commit --> `06ea2aa2cea7290aa6c53a2944e5c2ed91ce52b9`
- LinkedIn START --> published through KUZ-DIN
- publisher journal --> 13 PUBLISHED / 0 PREPARED / 0 IN_FLIGHT
- QUEUE timer --> active
- DELIVERY timer --> active

This START authorization permits:

- V80 implementation preparation
- CPU-only regression development
- CPU-only preflight execution
- immutable CPU preflight GOGIT publication

It does not authorize:

- V80 scientific GPU execution
- training or optimizer steps
- checkpoint modification
- BLIND access
- generation
- FINAL-DEV-FLOW V80
- any scientific success claim before a future verified scientific GOGIT

GPU scientific execution was explicitly authorized by the operator after the verified V80 CPU preflight. This authorization is limited to the frozen read-only V80 scientific control and does not authorize training, optimizer steps, checkpoint writes, BLIND access, generation or FINAL-DEV-FLOW V80.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**


## Verified V80 scientific result

Scientific GOGIT --> `PHASE03-SMOLTALK-V80-DECISION-BOUNDARY-PROXIMITY-CONTROL-001`

Verified replay:

- V80 PASS --> 1
- VALIDATION lexical positions --> 9170
- same-path batch --> 32
- perturbed prefixes --> 9062
- unchanged prefixes --> 108
- V79 prediction changes replay --> 5
- V79 alpha-sign changes replay --> 5
- ORIGINAL correct replay --> 2594
- REVERSE correct replay --> 2594
- training authorized --> 0
- training started --> 0
- BLIND access --> 0

Decision-boundary result:

- all positions within 1e-7 --> 0
- all positions within 1e-6 --> 0
- all positions within 1e-5 --> 0
- all positions within 1e-4 --> 0
- all positions within 1e-3 --> 0
- changed positions within 1e-7 through 1e-3 --> 0
- sign-changing positions within 1e-7 through 1e-5 --> 0
- maximum boundary distance among changed positions --> 59604287 nano-units
- mean boundary distance among changed positions --> 30173315 nano-units
- maximum crossing span among changed positions --> 249839202 nano-units
- mean crossing span among changed positions --> 150983569 nano-units

Interpretation -->

The five V79 prediction/sign changes are not confined to numerically tiny neighborhoods of the frozen residual decision boundary. Every changed position remains outside the widest frozen proximity threshold of 1e-3.

The earlier interpretation of the V79 effect as merely a near-zero fragile flip is therefore not supported by V80. The reverse-history intervention moves the residual coordinate across zero from materially larger distances in the measured residual coordinate.

This strengthens evidence for a real context-order sensitivity in the frozen residual diagnostic, but it still does not establish semantic competence, correct contextual reasoning, useful generation quality or a causal semantic feature.

V62 remains frozen. No training, optimizer step, checkpoint write, BLIND access or generation was performed.

