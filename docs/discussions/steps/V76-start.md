# Mini-Kuzai | V76 - Frequency-Residualized PC1 Output Control

```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : V76
  STATUS   : EXPERIMENT STARTED
========================================================================
```

## Objective

Determine how much of the stable TRAIN-derived PC1 output signature is explained by frozen TRAIN lexical target frequency, and whether the frequency-residualized part retains independent predictive concentration on the separate frozen VALIDATION population.

V74 established a strong frequency-prior confound. V75 then showed that the dominant PC1 geometry transfers almost unchanged from TRAIN to VALIDATION. V76 therefore targets the remaining question directly: separate the stable PC1 output profile into a TRAIN-frequency component and an orthogonal residual before scoring either component on VALIDATION.

## Frozen scope

The V76 protocol is frozen before this START.

The study reuses the original stopped V62 cycle-2 checkpoint with 69 optimizer steps and 597982 exposure tokens. No model parameter, tokenizer or corpus file may change.

The complete frozen TRAIN lexical population is used for calibration:

- 294726 lexical positions
- 891 observed lexical token types
- 1024-way output vocabulary
- V65 lexical frequency definition
- TRAIN-derived V75 mean and PC1 geometry

The frozen output-profile decomposition is fitted entirely on TRAIN-derived quantities.

For the 1024 output IDs, V76 constructs:

- centered TRAIN-PC1 output profile
- centered `log1p(TRAIN lexical frequency)`
- deterministic FP64 OLS frequency component
- orthogonal frequency-residualized component

The same 9170 frozen VALIDATION lexical positions are then scored in exactly three diagnostic modes:

- TRAIN_PC1_REPLAY
- FREQ_COMPONENT_ONLY
- FREQ_RESIDUAL_ONLY

TRAIN_PC1_REPLAY must reproduce the frozen V75 result exactly before any new V76 metric is accepted.

One public scientific GOGIT report is predeclared with exactly 30 nonnegative integer metrics. No scientific outcome is predeclared for correlation, R2, decomposed-mode performance or residual energy.

## Safety and execution gates

This START draft does not itself authorize execution.

If START-DEV-FLOW V76 is later explicitly authorized and published, it will open only implementation and CPU-preflight work under the frozen protocol.

It will **not** authorize:

- GPU scientific execution
- model training or any optimizer step
- BLIND evaluation or BLIND file access
- checkpoint write or model-weight mutation
- tokenizer or corpus modification
- FINAL-DEV-FLOW
- a scientific success claim

Before any later GPU authorization, the V76 implementation must pass the frozen CPU regression suite, exact dependency/blob pins, 30-field schema check, no-BLIND/no-training gates, fixed batch/chunk settings and the 6144 MiB GPU memory ceiling.

The implementation must use globally disabled gradients plus inference/no-grad execution. It must not retain the full hidden-state population or publish token text, individual token IDs, per-position predictions, hidden vectors, output-profile vectors or private dialogue.

A provenance mismatch, V75 replay mismatch, decomposition failure, nonfinite value, OOM, timeout, resource-gate failure or attempted BLIND access must abort without scientific GOGIT publication.

This START makes no advance claim about the scientific result. Only immutable GOGIT evidence may be interpreted after a separately authorized controlled run, and FINAL-DEV-FLOW requires another explicit authorization.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
