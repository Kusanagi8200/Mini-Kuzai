# Mini-Kuzai Phase 03 - V72 Hidden-State Anisotropy 001

Date --> 2026-10-31

Status --> **GPU GOGIT VERIFIED / V62 CHECKPOINT FROZEN / TRAINING DISABLED**

## Scientific question

Does extreme output-token concentration in the stopped V62 model correlate with a narrow distribution of decoder hidden-state directions, especially a dominant mean-vector component?

Historical evidence -->

- [V70 FP32 precision control](../reports/assistant-results/history/PHASE03-SMOLTALK-V70-PRECISION-CONTROL-001.json) --> original FP32 CE 4.732 and five distinct lexical argmax IDs
- [V71 output dominance attribution](../reports/assistant-results/history/PHASE03-SMOLTALK-V71-OUTPUT-DOMINANCE-ATTRIBUTION-001.json) --> only 275 of 9170 lexical predictions change under FULL output-row norm equalization; the winner/target cosine gap alone is not causal evidence of a hidden-state defect

V72 investigates representations **without changing stored weights, the tokenizer, the V62 checkpoint or any training settings**. The frozen BLIND TEST remains inaccessible.

## Frozen data and architecture

- 36 frozen VALIDATION sequences and 9170 lexical next-token positions
- Original V62 cycle-2 checkpoint, 69 optimizer steps, 597982 exposed tokens
- 128-dimensional states immediately before the tied, bias-free output projection
- CUDA BF16 model forward, identical V71/V70-style captured hidden states converted to FP32 for output-logit reproduction
- TRAIN is rebuilt only by the established V64 preflight to check the signed 345-segment inventory; **no TRAIN inference or optimization**
- No human semantic assessment, text generation, BLIND access or model save

Before publishing, V72 must reproduce original FP32 CE **4.732**, distinct argmax **5**, dominant token share **72.55%** and original top-1 correctness **2673/9170** from the immutable V71 report. Prior GOGIT report and producer SHA256 integrity checks are mandatory.

## Spectral analysis

Let H have one row per lexical VALIDATION hidden state (9170 x 128), and let μ be its mean vector.

V72 computes two 128 x 128 second-moment matrices -->

1. **Uncentered** --> HᵀH / N, retaining the common mean direction
2. **Centered** --> (H - μ)ᵀ(H - μ) / N, removing the common mean direction

For both, eigenvalue decompositions in FP64 measure -->

- Fraction of spectral mass in the largest eigenvalue and largest five eigenvalues
- Participation ratio --> (Σ eigenvalues)² / Σ(eigenvalues²), expressed as ×100
- Energy share attributable to the mean vector
- Mean pairwise cosine similarity, computed from normalized-state sums without publishing or storing individual pairs
- Absolute cosine between μ and the strongest centered principal direction

These are descriptive properties of the frozen VALIDATION representation, not independent explanations of training failure.

## Mean-center output control

A separate temporary counterfactual calculates (h - μ)Wᵀ for lexical positions, using the **original, unchanged output matrix W**.

It aggregates -->

- Number of changed top-1 predictions and counts by true byte / merged-BPE target family
- Distinct top-1 IDs and share of the most frequent predicted ID
- Original versus mean-centered exact top-1 correctness
- Mean winning-versus-gold logit deficit for byte and merged-BPE targets

The mean-centered projection is **not a deployment patch**. It changes the logit baseline across vocabulary IDs, may favor PAD or other special output IDs, and cannot be judged by top-1 diversity alone. It does not compute generation quality or a full-sequence mean-centered CE, and does not apply to EOS analysis.

## Public GOGIT record

Exactly 30 nonnegative integer fields -->

- Three standard flags --> semantic validation 0, training authorized 0, training started 0
- Twenty-seven `V72_GEOM_*` fields --> audit PASS, BLIND access 0, frozen denominators, V71 original controls, uncentered/centered spectral shares, participation ratios, mean-vector measures, centered top-1 distribution, correctness and per-family switch/deficit counts

Units -->

- `*_BP` --> basis points (10000 = 100%)
- `*_X100` --> value multiplied by 100
- `*_X1000` --> value multiplied by 1000
- `PAIR_COS_SHIFT_X1000` --> 1000 × (1 + mean pair cosine) to remain nonnegative
- `MEAN_PC1_ABS_COS_X1000` --> 1000 × absolute cosine

No raw hidden states, eigenvectors, individual logits, model weights, token IDs, source text, prompts, private messages or per-position observations may be published.

## Implementation and gating

- [V72 GPU audit](../tools/public-audits/phase03_v72_hidden_state_anisotropy_001.py)
- [CPU unit tests](../tests/test_phase03_v72_hidden_state_anisotropy_001.py)
- [Pinned V72 GOGIT runner](../tools/run_v72_hidden_state_anisotropy_001_job.py)
- [GOGIT numeric allowlist](../tools/gogit_public.py)

STEP_ID --> `PHASE03-SMOLTALK-V72-HIDDEN-STATE-ANISOTROPY-001`

The runner requires clean/synchronized `main`, validated V62 stopped state, exact approved audit Git blob, successful CPU tests, immutable predecessor reports and final GOGIT history verification. GOGIT limits each audit subprocess to 300 seconds; a timeout is a failure, not a result.

AUTOPILOT V3 is unchanged and does not register a V72 run. No autonomous monitoring, training permission or BLIND access is activated.

## Local fhc2 command

After a successful clean fast-forward synchronization -->

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai && git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v72_hidden_state_anisotropy_001_job.py
```

The pinned local command has now produced a verified immutable V72 numeric GOGIT report. It should **not** be rerun to overwrite the existing STEP_ID; the command above is retained for historical reproducibility. The public report demonstrates completion of the numeric GPU diagnostic, not independent conversational or semantic validation.

## Published V72 findings

Immutable numeric result --> [V72 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V72-HIDDEN-STATE-ANISOTROPY-001.json)

Verified commit --> [41aed7aef84c](https://github.com/Kusanagi8200/Mini-Kuzai/commit/41aed7aef84c832e78ae2ac7bfc2f8cd681bd1b7)

| Measure | Verified result |
| --- | ---: |
| Frozen lexical VALIDATION positions | 9170 |
| Output-head hidden dimension | 128 |
| Original FP32 CE | 4.732 |
| Mean-vector energy share | 72.19% |
| Raw / uncentered PC1 energy share | 74.51% |
| Raw / uncentered first-five energy share | 99.15% |
| Raw / uncentered participation ratio | 1.67 |
| Centered PC1 variance share | 82.88% |
| Centered first-five variance share | 97.38% |
| Centered participation ratio | 1.44 |
| Mean pairwise hidden-state cosine | 0.721 |
| Mean hidden-state L2 norm | 11.665 |
| Mean-vector L2 norm | 9.911 |
| Absolute cosine: mean vector vs centered PC1 | 0.257 |
| Original -> centered top-1 distinct lexical IDs | 5 -> 15 |
| Original -> centered dominant-token share | 72.55% -> 57.88% |
| Original -> centered lexical correct top-1 | 2673 -> 2832 |
| Argmax changes after centering | 2889 / 9170 = 31.50% |
| Changes for byte / merged-BPE gold targets | 1353 / 1536 |
| BLIND access / new training | 0 / 0 |

**Reading -->** Most energy is aligned with a shared mean vector, but centered covariance is still extremely anisotropic: PC1 explains 82.88% of its variance in 128 dimensions and participation ratio is only 1.44. The mean-center counterfactual changes about one-third of lexical winners and yields +159 exact top-1 decisions without any change to frozen weights. This does **not** demonstrate better generation or performance on independent data. The mean was estimated from the same VALIDATION split used to score the counterfactual, so it is not a held-out estimator.

**Decision -->** Preserve the V62 checkpoint and original projection. The next read-only research question is whether centered PC1/PC2 directions and token-specific output alignment explain the residual anisotropy. Any future intervention must be a separately reviewed experiment, with no implicit training authorization or BLIND use.

## Decision boundary

Interpret the spectral concentration and mean-center differences alongside V70/V71. Select the next experiment only after numeric GOGIT verification, and require an independently reviewed, frozen protocol and explicit new authorization before any future training.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
