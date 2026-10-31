# Mini-Kuzai Phase 03 - V73 Principal-Axis Attribution 001

Date --> 2026-10-31

Status --> **RESEARCH PROTOCOL FROZEN / IMPLEMENTATION AND GPU EXECUTION PENDING**

## Scientific objective

V72 demonstrated strong anisotropy in the frozen V62 output-head hidden states: 82.88% of centered covariance spectral mass lies in principal component 1 (PC1), and the centered participation ratio is 1.44 in 128 dimensions. Subtracting the VALIDATION-derived mean vector changes 2889/9170 lexical top-1 predictions. The observation is not evidence that removing PC1 will improve language generation.

V73 isolates the contribution of **the leading centered principal axes** to the tied output-head logits without modifying the saved model or authorizing training. The same 36 frozen VALIDATION sequences and the original stopped V62 cycle-2 checkpoint are used. No BLIND TEST, raw text, token IDs, per-position outputs, weights or eigenvectors are published.

## Four projections from identical frozen states

Let `h` be the output-head hidden state and `mu` the mean of all frozen lexical VALIDATION hidden states. Compute centered covariance in FP64; `u1` and `u2` are the first two eigenvectors, ordered by descending eigenvalue. All subsequent projections use FP32 hidden states and the **unchanged, bias-free tied output matrix W**.

| Mode | Hidden-state input to output head | Purpose |
| --- | --- | --- |
| CENTER | `h - mu` | Exact V72 baseline |
| MINUS_PC1 | `(h - mu) - ((h - mu)·u1)u1` | Remove dominant centered direction |
| MINUS_PC12 | MINUS_PC1 minus centered PC2 projection | Probe residual subspace |
| PC1_ONLY | `((h - mu)·u1)u1` | Measure the predictive concentration of PC1 alone |

These are **temporary, teacher-forced, lexical-only** projections. They do not restore context-aware generation, alter training dynamics, estimate independent generalization or establish causality. Eigenvector signs do not change the corresponding orthogonal projections. No reported metric should be interpreted as production performance.

## Prerequisite gates

- Exact source fingerprint of immutable [V72 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V72-HIDDEN-STATE-ANISOTROPY-001.json)
- Reuse V64 frozen preflight, V67 stable ranker, V69 scoring and the V72 verified VALIDATION geometry definitions
- V62 checkpoint frozen at 69 optimizer steps and 597982 exposed tokens; 345 TRAIN segments verified but never used for inference
- 36 VALIDATION conversations, 9206 complete next-token positions, 9170 lexical positions; 4876 byte and 4294 merged-BPE targets
- Exact V72 replay of original FP32 CE 4.732, argmax 5 and top-token share 72.55%; CENTER argmax 15, top-token share 57.88%, 2832 exact lexical predictions; centered PC1 spectral share 82.88%
- No parameter mutation, gradient, training, BLIND access, sampling or persistence of hidden states

Any mismatch must block the GOGIT publication.

## Public numerical schema

Exactly **30 nonnegative integer fields**, comprising 3 safety fields and 27 `V73_AXIS_*` metrics. The 27 fields report -->

- PASS, BLIND access, lexical denominator and model dimension
- Centered PC1/PC2 spectral mass in basis points
- CENTER distinct predictions, top-token dominance and exact top-1 count
- MINUS_PC1 / MINUS_PC12 distinct predictions, dominance, exact top-1 count and switch counts versus CENTER
- MINUS_PC1 switch counts by gold byte / merged-BPE family
- PC1_ONLY distinct predictions, dominance and exact top-1 count
- Mean top1/top2 logit margin in CENTER, MINUS_PC1 and MINUS_PC12
- Mean absolute cosine alignment of the CENTER winner and gold output-row vectors with PC1, ×1000

GOGIT must never publish individual examples, model activations, eigenvectors, raw cosine signed values, text or token IDs.

## Decision criteria

A reduction in top-token concentration accompanied by loss of exact prediction accuracy is not an improvement by default. Because `mu` and the principal axes are fitted on VALIDATION itself, any apparently beneficial change is **in-sample diagnostic evidence only**. A future learned or trained intervention would require a new independent experiment, immutable protocol and explicit authorization; the BLIND split cannot be opened as a convenient evaluation set.

## Implementation status

Implementation paths, CPU tests and pinned runner will be added and verified before local execution. No V73 GPU result is asserted in this protocol.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
