# Mini-Kuzai | V74 - Token Frequency versus Principal-Axis Predictions

```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : V74
  STATUS   : EXPERIMENT STARTED
========================================================================
```

## Objective

Investigate whether the apparent usefulness of the leading principal axis in Mini-Kuzai's frozen hidden states can be explained by common TRAIN token frequencies.

V73 observed 2455 correct lexical top-1 outcomes from PC1_ONLY across 9170 frozen VALIDATION positions, even though only two distinct token IDs were predicted. Removing PC1 increased prediction diversity but reduced exact correctness. These are teacher-forced, in-sample findings, not evidence of conversational competence.

## Proposed read-only protocol

Compare the original FP32 model outputs, centered outputs, PC1-only outputs and a context-free TRAIN-unigram control on identical frozen V62 VALIDATION positions. Break down aggregate correct predictions by raw-byte versus merged Byte-BPE targets and by predeclared TRAIN-frequency strata.

Before running a new GPU diagnostic, review and freeze the numerical metric schema, frequency thresholds, reproducible tests and source fingerprints. Failure to reproduce V73 invariants blocks progression.

## Safety

The V62 cycle-2 checkpoint, tokenizer, corpus and weights remain frozen. No new training, BLIND TEST access, checkpoint patch, hidden-state export or individual token publication is permitted. This START notice makes no advance claim of scientific success. Only verified GOGIT evidence and a separate explicit FINAL-DEV-FLOW can close the step.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
