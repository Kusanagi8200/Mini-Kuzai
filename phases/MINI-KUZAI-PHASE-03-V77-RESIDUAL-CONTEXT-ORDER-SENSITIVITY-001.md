# Mini-Kuzai Phase 03 - V77 Residual Context-Order Sensitivity Control 001

Date --> 2026-11-07
Frozen review --> 2026-11-07

Status --> **PROTOCOL FROZEN / START AUTHORIZED BY OPERATOR / START REQUEST MAY BE PUBLISHED / GPU NOT AUTHORIZED / NO TRAINING / NO BLIND ACCESS**

## Why V77 follows V76

V76 decomposed the stable TRAIN-derived PC1 output profile into a TRAIN lexical-frequency component and an orthogonal residual.

The verified V76 result is now immutable:

- V76 PASS --> 1
- VALIDATION lexical positions --> 9170
- V76 PC1 replay correct --> 2457
- V76 PC1 replay distinct predicted IDs --> 2
- V76 PC1 replay dominant top-1 share --> 7043 basis points
- V76 frequency-component correct --> 2451
- V76 frequency-component distinct predicted IDs --> 2
- V76 frequency-residual correct --> 2594
- V76 frequency-residual distinct predicted IDs --> 2
- V76 frequency-residual dominant top-1 share --> 7043 basis points
- V76 unigram correct --> 2535
- V76 residual/unigram agreement --> 6458
- V76 residual/unigram shared correct --> 2451
- V76 axis-frequency absolute correlation --> 2785 basis points
- V76 axis-frequency R2 --> 775 basis points
- V76 residual-energy share --> 9225 basis points
- V76 coverage --> 10000 basis points

The frequency direction therefore explains only 7.75% of the centered PC1 output-profile energy, while 92.25% remains in the orthogonal residual.

The residual also produces more correct frozen VALIDATION predictions than either the full PC1 replay or the static TRAIN unigram.

However, the residual still predicts only two output IDs and remains dominated by one output on 70.43% of positions.

The unresolved question is therefore whether this residual is actually sensitive to preceding context, or whether it behaves like another nearly static output bias.

## Frozen scientific question

**Does the frozen V76 frequency-residualized PC1 signal change when the order of earlier context is perturbed while target token, prefix length, prefix token multiset, BOS and the immediate preceding token are held fixed?**

V77 is a controlled context-order sensitivity study.

It is not:

- new training
- a tokenizer experiment
- a generation benchmark
- a semantic evaluation
- a BLIND evaluation
- a model patch
- a claim that context sensitivity implies language understanding

## Frozen inheritance

V77 must reuse without modification:

- the stopped V62 cycle-2 checkpoint
- V62 optimizer steps --> 69
- V62 exposure tokens --> 597982
- TRAIN lexical positions --> 294726
- TRAIN observed lexical token types --> 891
- VALIDATION lexical positions --> 9170
- hidden dimension --> 128
- output vocabulary --> 1024
- V75 TRAIN mean and PC1 reconstruction method
- V76 TRAIN-only lexical-frequency construction
- V76 FP64 frequency residualization
- V76 residual output profile
- V76 scientific report and fixed replay values

BLIND remains closed.

Any mismatch in V62, V75 or V76 frozen provenance blocks V77.

## Frozen context perturbation

For each frozen VALIDATION lexical target, let the normal teacher-forced input prefix be:

`p = [BOS, x1, x2, ..., x(n-1)]`

where `x(n-1)` is the immediate preceding input token used to predict the current frozen target.

V77 defines one deterministic counterfactual prefix.

### REVERSE_HISTORY_KEEP_LAST

If the prefix contains at least one interior history token, construct:

`p_rev = [BOS] + reverse([x1, ..., x(n-2)]) + [x(n-1)]`

For prefixes with fewer than three tokens total, the prefix is unchanged.

For every position, the implementation must verify exactly:

- same prefix length
- same token multiset
- BOS remains first
- immediate preceding token remains last
- current target token is unchanged
- no PAD, BOS or EOS is introduced into the interior by the transformation
- no token text is required or emitted

This transformation changes only the **order of earlier context**.

It deliberately does not change the immediate preceding token or the inventory of tokens present in the prefix.

## Frozen residual scoring

V77 must recompute the exact V76 TRAIN-derived frequency-residualized output profile before scoring.

Let:

- `mu_train` --> frozen TRAIN hidden-state mean
- `u_train` --> frozen TRAIN leading PC1
- `r` --> frozen V76 frequency-residualized centered output profile
- `h_full` --> hidden state from the original frozen VALIDATION prefix
- `h_rev` --> hidden state from REVERSE_HISTORY_KEEP_LAST

Define:

`alpha_full = (h_full - mu_train) dot u_train`

`alpha_rev = (h_rev - mu_train) dot u_train`

Score:

`logits_full = alpha_full * r`

`logits_rev = alpha_rev * r`

The target and residual profile are identical in both modes.

Only the earlier context order differs.

FULL_CONTEXT must reproduce V76 exactly before any V77 counterfactual metric is accepted:

- correct --> 2594
- distinct predicted IDs --> 2
- dominant top-1 share --> 7043 basis points
- unigram agreement --> 6458
- residual/unigram shared correct --> 2451

## Frozen alpha comparison

V77 measures both discrete prediction changes and continuous PC1-coordinate changes.

For the 9170 paired positions, report:

- absolute centered Pearson correlation between `alpha_full` and `alpha_rev`
- sign agreement and sign change counts
- count of positions with `abs(alpha_full - alpha_rev) > 1e-7`
- top-1 prediction agreement and change counts

The `1e-7` alpha-delta threshold is frozen before execution as a numerical-change threshold only.

It is not a scientific success threshold.

Zero alpha uses the exact sign class zero. Positive, negative and zero are therefore three distinct sign classes.

## Frozen correctness comparison

For FULL_CONTEXT and REVERSE_HISTORY_KEEP_LAST, V77 reports:

- correct predictions
- distinct predicted IDs
- dominant top-1 share
- agreement with the frozen TRAIN unigram
- shared-correct count with the frozen TRAIN unigram

Across the paired modes it also reports:

- positions correct in both modes
- positions correct only in FULL_CONTEXT
- positions correct only in REVERSE_HISTORY_KEEP_LAST

No outcome threshold is predeclared.

## Frozen interpretation rule

Evidence of context-order sensitivity requires only that the measured residual coordinate or its top-1 decision changes under the frozen perturbation.

A substantial change would show that the V76 residual is not purely invariant to earlier-context order.

A weak change would support the interpretation that the residual remains dominated by static or near-static factors.

Neither result establishes:

- semantic competence
- useful long-context reasoning
- causal language understanding
- personality formation
- generalization beyond frozen teacher-forced VALIDATION
- readiness for new training

The reverse-history counterfactual is intentionally artificial and can be out-of-distribution.

Therefore a change proves sensitivity to the intervention, not that the original context was used correctly.

## Frozen 30-field GOGIT schema

STEP_ID --> `PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001`

The scientific publication must contain exactly these 30 aggregate nonnegative integer metrics:

1. `SEMANTIC_VALIDATION_COMPLETE`
2. `TRAINING_AUTHORIZED`
3. `TRAINING_STARTED`
4. `V77_PASS`
5. `V77_BLIND_ACCESS`
6. `V77_VAL_LEXICAL`
7. `V77_HIDDEN_DIM`
8. `V77_VOCAB`
9. `V77_FULL_CORRECT`
10. `V77_FULL_DISTINCT`
11. `V77_FULL_TOP1_SHARE_BP`
12. `V77_FULL_UNIGRAM_AGREE`
13. `V77_FULL_UNIGRAM_SHARED_CORRECT`
14. `V77_REVERSE_CORRECT`
15. `V77_REVERSE_DISTINCT`
16. `V77_REVERSE_TOP1_SHARE_BP`
17. `V77_REVERSE_UNIGRAM_AGREE`
18. `V77_REVERSE_UNIGRAM_SHARED_CORRECT`
19. `V77_PRED_AGREE`
20. `V77_PRED_CHANGED`
21. `V77_FULL_REVERSE_SHARED_CORRECT`
22. `V77_FULL_ONLY_CORRECT`
23. `V77_REVERSE_ONLY_CORRECT`
24. `V77_ALPHA_SIGN_AGREE`
25. `V77_ALPHA_SIGN_CHANGED`
26. `V77_ALPHA_CORR_ABS_BP`
27. `V77_ALPHA_DELTA_NONZERO`
28. `V77_PERTURBED_PREFIXES`
29. `V77_UNCHANGED_PREFIXES`
30. `V77_COVERAGE_BP`

## Frozen fixed expectations

A successful scientific V77 GOGIT must require:

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V77_PASS=1`
- `V77_BLIND_ACCESS=0`
- `V77_VAL_LEXICAL=9170`
- `V77_HIDDEN_DIM=128`
- `V77_VOCAB=1024`
- `V77_FULL_CORRECT=2594`
- `V77_FULL_DISTINCT=2`
- `V77_FULL_TOP1_SHARE_BP=7043`
- `V77_FULL_UNIGRAM_AGREE=6458`
- `V77_FULL_UNIGRAM_SHARED_CORRECT=2451`
- `V77_COVERAGE_BP=10000`

The implementation must also internally reproduce the V76 frequency fit:

- axis-frequency absolute correlation --> 2785 basis points
- axis-frequency R2 --> 775 basis points
- residual-energy share --> 9225 basis points

No expected scientific outcome is frozen for reverse-context accuracy, prediction changes, alpha changes, alpha correlation or correctness migration.

`V77_PASS=1` means only that provenance, replay, perturbation invariants, safety gates, paired accounting and full coverage completed.

## Frozen CPU implementation review requirements

Before any GPU authorization, CPU-only tests must verify at minimum:

1. exact 30-field schema and GOGIT allowlist compatibility
2. V75/V76 dependency and Git-blob pins
3. V76 report replay values
4. deterministic REVERSE_HISTORY_KEEP_LAST transformation
5. prefix length preservation
6. prefix token-multiset preservation
7. BOS preservation
8. immediate-predecessor preservation
9. unchanged behavior for prefixes shorter than three tokens
10. target preservation
11. alpha sign classification including exact zero
12. alpha-delta threshold behavior
13. paired histogram/accounting helpers
14. Pearson correlation numerical gates
15. fail-closed nonfinite handling
16. no BLIND path or import
17. no optimizer or checkpoint-write path
18. no raw token text, hidden vectors or per-position output in public metrics

CPU preflight is not GPU authorization.

## Frozen runtime and resource boundary

A future scientific implementation must remain bounded and read-only:

- one CUDA device only
- unchanged V62 checkpoint
- evaluation/inference mode only
- `torch.set_grad_enabled(False)`
- inference/no-grad contexts
- full VALIDATION batch --> 4
- counterfactual prefix batch --> 32
- score chunk --> 512
- GPU peak-memory hard ceiling --> 6144 MiB
- no optimizer
- no checkpoint write
- no model-weight mutation
- no BLIND access
- no generation
- no raw token text
- no per-position prediction publication
- no hidden-vector publication
- exact 30 allowlisted integer metrics only
- GOGIT process budget --> 300 seconds
- OOM, timeout, nonfinite value, provenance mismatch, replay mismatch or perturbation-invariant failure --> abort without scientific GOGIT

## Authorization boundary

The V77 protocol is frozen and the operator has explicitly authorized **START-DEV-FLOW V77**.

That authorization permits:

- committing the reviewed V77 protocol
- committing the V77 START source
- committing an exact V77 START request
- publishing one V77 START DEV-FLOW event
- preparing implementation and CPU-only preflight after START receipt verification

It does **not** authorize:

- V77 scientific GPU execution
- new model training
- optimizer steps
- checkpoint modification
- BLIND access
- FINAL-DEV-FLOW V77
- any scientific success claim

GPU execution requires a later explicit operator authorization after a verified CPU preflight.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
