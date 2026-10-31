# Mini-Kuzai Phase 03 - V73 Principal-Axis Attribution 001

Date --> 2026-10-31

Status --> **V73 GPU/GOGIT VERIFIED / V62 FROZEN / NO TRAINING OR BLIND ACCESS**

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

## Published V73 findings

Verified immutable GOGIT --> [V73 principal-axis numeric report](../reports/assistant-results/history/PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.json)

GOGIT commit --> [1dcd4e8dc613](https://github.com/Kusanagi8200/Mini-Kuzai/commit/1dcd4e8dc6138992486f70cdee3620751c4f2940)

On the 9170 frozen lexical VALIDATION positions, the centered PC1 and PC2 explain **82.88%** and **8.47%** of centered hidden-state variance.

| Projection | Distinct argmax IDs | Dominant top-1 share | Correct top-1 | Mean top1/top2 margin |
| --- | ---: | ---: | ---: | ---: |
| CENTER | 15 | 57.88% | 2832 (30.88%) | 0.229 |
| MINUS_PC1 | 522 | 20.74% | 1124 (12.26%) | 0.059 |
| MINUS_PC12 | 715 | 11.80% | 818 (8.92%) | 0.047 |
| PC1_ONLY | 2 | 70.34% | 2455 (26.77%) | Not published |

Changes relative to CENTER --> 6841/9170 (74.60%) argmax predictions switch when PC1 is removed and 8139/9170 (88.76%) when PC1 and PC2 are removed. For MINUS_PC1, switches are split into 3068 true-byte-target positions and 3773 true-merged-BPE-target positions.

The mean absolute cosine between PC1 and the **CENTER-selected** output rows is 0.433; the corresponding mean cosine with true target output rows is 0.274.

**Interpretation -->** Subtracting principal directions decorrelates output prediction counts but removes a large amount of predictive information. PC1_ONLY produces just two top-1 IDs yet 2455 correct positions; this refers to the number of exact top-1 outcomes, not necessarily an overlap of correct positions with CENTER. It is not evidence that 26.77% of arbitrary natural-language questions can be answered with one dimension. The ablations are fitted and scored on the same VALIDATION split and do not prove independent generalization, generation quality or causality.

**Decision -->** Retain the unmodified V62 checkpoint and output projection. Do **not** promote PC1 deletion, PC1-only projections or VALIDATION-fitted mean-centering into a deployment patch. Further work should distinguish representation collapse from class-frequency, teacher-forcing and training-objective effects using a separately reviewed read-only analysis. No new training or BLIND TEST access is authorized.

## Decision criteria

A reduction in top-token concentration accompanied by loss of exact prediction accuracy is not an improvement by default. Because `mu` and the principal axes are fitted on VALIDATION itself, any apparently beneficial change is **in-sample diagnostic evidence only**. A future learned or trained intervention would require a new independent experiment, immutable protocol and explicit authorization; the BLIND split cannot be opened as a convenient evaluation set.

## Implementation status

The implementation is now published and the numerical metric schema is registered -->

- [V73 GPU audit](../tools/public-audits/phase03_v73_principal_axis_attribution_001.py)
- [V73 CPU tests](../tests/test_phase03_v73_principal_axis_attribution_001.py)
- [V73 pinned GOGIT runner](../tools/run_v73_principal_axis_attribution_001_job.py)
- [GOGIT allowlist](../tools/gogit_public.py)

STEP_ID --> `PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001`

The runner checks an approved Git blob for the audit and the original V62 mandatory cycle-2 stop. It executes CPU tests before GPU publication. Any discrepancy, 300-second timeout, nonnumeric output or duplicate STEP_ID blocks new GOGIT output. AUTOPILOT is not modified.

Local fhc2 command, on a synchronized and clean `main` -->

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai && git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v73_principal_axis_attribution_001_job.py
```

The historical local runner has now published a verified immutable numerical GOGIT result. Do not reissue the same STEP_ID or interpret documentation publication as renewed authorization.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
