# Mini-Kuzai | V75 - TRAIN-Fitted Geometry Transfer Control

```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : V75
  STATUS   : EXPERIMENT STARTED
========================================================================
```

## Objective

Investigate whether the pronounced leading hidden-state direction observed in V72 and V73 transfers when its mean and principal axis are fitted exclusively on frozen TRAIN states, rather than fitted on the same VALIDATION states used for scoring.

V74 verified that the PC1_ONLY predictor's apparent usefulness is strongly confounded by frequent TRAIN tokens: the context-free unigram baseline achieved 2535 correct predictions versus 2455 for PC1_ONLY, and 2449 PC1 hits were shared.

## Proposed bounded research scope

Use the original stopped V62 cycle-2 checkpoint and unchanged corpus/tokenizer. Determine a deterministic TRAIN-only fitting population, compute aggregate geometry through a bounded read-only inference pass, then apply the fixed resulting mean and PC1 to the same frozen 9170 VALIDATION lexical scoring positions.

The proposed controls compare original logits, TRAIN mean-centered logits, TRAIN-PC1-only logits and TRAIN-minus-PC1 logits, with the frozen V74 frequency baseline and V73 VAL-fitted geometry as predeclared references. Publish only numeric aggregates.

## Safety and review gates

This file is a **review-only draft**, not a claim that V75 has started. Before any START-DEV-FLOW, the operator must explicitly approve the final V75 scientific protocol, metric schema, source fingerprints, tests and GPU limits. No V75 request or GitHub Discussion should be created from this draft alone.

No new training, optimizer step, checkpoint write, BLIND evaluation, private text export, individual token publication or change to existing model weights is authorized. A future GOGIT publication and separate FINAL-DEV-FLOW require their own verified evidence and explicit order.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
