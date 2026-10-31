# Mini-Kuzai Phase 03 - V68 tied output head and logit dominance

Status --> **CORRECTED V68 GPU / GOGIT VERIFIED / HISTORICAL FAILURE PRESERVED**

Date --> 2026-10-31

## Confirmed incident and correction

The first AUTOPILOT V1 execution passed eight CPU unit tests but the original V68 audit failed before GOGIT publication. The follow-up [V68 numeric failure probe](../reports/assistant-results/history/PHASE03-SMOLTALK-V68-FAILURE-PROBE-001.json), commit [`73402e216896`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/73402e21689693db8180ae4ab776f3f2be125eb2), identified -->

- `V68_FAIL_ORIGINAL_FAILED=1`
- `V68_FAIL_EXCEPTION_CLASS_ID=1` --> RuntimeError
- `V68_FAIL_CAUSE_ID=5` --> original `Frozen PAD embedding row nonzero` invariant
- `V68_FAIL_SOURCE_FUNCTION_ID=2` --> `summarize_head()`
- `V68_FAIL_SOURCE_LINE=49` --> former check

**Correction** --> `padding_idx` suppresses input embedding gradients for PAD but, under tied output-head weights, PAD remains an output softmax competitor and its shared row can change during training. The output PAD row is therefore required to be **finite**, but not exactly zero.

The new diagnostic publishes `V68_HEAD_NORM_PAD_X1000` (PAD row L2 norm multiplied by 1000), replacing the old `V68_HEAD_NORM_SPECIAL_MEAN_X1000` metric **without changing the report length of 30 fields**. The weight-tied/no-bias checks, finite-row enforcement, V62 frozen checkpoint and VAL/BLIND separation remain intact. Two new CPU cases cover an intentionally nonzero PAD row and an invalid NaN row.

**Verified closure** --> The corrected V68 GPU audit completed and published as immutable [V68 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V68-OUTPUT-HEAD-001.json), commit [3d872b9102f7](https://github.com/Kusanagi8200/Mini-Kuzai/commit/3d872b9102f7708e5bff723ffd0f195ba2e0ee72). It recorded tied head = 1, PAD row norm 0.182, 4 predicted lexical IDs, dominant share 72.58%, CE 4.733, terminal EOS 14/36 and BLIND access 0. The original failed attempt and subsequent failure probe remain preserved as separate historical evidence.

## Research question

V67 found only **4 distinct predicted token IDs** across **9170 lexical VALIDATION positions**, although 606 distinct gold tokens were present. The most frequently predicted token occupied 72.58% of lexical contexts. V66 found an argmax bias toward two raw-byte IDs even where the true target was merged BPE.

V68 asks whether a tied embedding/output projection, its weight norms or unusually large winning-logit margins correlate with this concentration. This does not assume an output-head bug.

## Verified architecture semantics

V60's frozen model defines `lm_head` as a bias-free linear projection, tied directly to `token_embedding.weight`. The checkpoint and class identity are checked by the frozen V64-002 preflight. The output-head analysis therefore measures **embedding/output rows**, not a separate trainable bias vector.

## GPU audit and measures

The program examines -->

- Weight tying and absence of output bias
- Mean row norms for single-byte and merged BPE families, and the measured PAD output-row L2 norm
- Maximum row norm and cross-vocabulary norm dispersion
- Top-1 prediction class and distinct predicted ID count
- Winner-to-runner-up logit margin and its 90th percentile
- Distance from the maximum logit to the actual gold-token logit, by target family
- Mean output-row norms of selected versus expected token IDs
- Exact consistency with V67 GOGIT concentration, cross-entropy and EOS

The original V62 cycle-2 model remains read-only. The decoder uses the V67-compatible stable `argmax()` behavior for tied logits. The previous V67 winner is never assumed from `topk()` indexes.

## Publication

Audit source --> `tools/public-audits/phase03_v68_output_head_001.py`

Tests --> `tests/test_phase03_v68_output_head_001.py`

Runner --> `tools/run_v68_output_head_001_job.py`

GOGIT step --> `PHASE03-SMOLTALK-V68-OUTPUT-HEAD-001`

Exactly 30 numeric GOGIT fields, including the standard three safety flags and explicit `V68_HEAD_NORM_PAD_X1000`. No prompts, decoded text, source token IDs, individual logits or private data.

V68 forms the fifth stage of [AUTOPILOT V1](../autopilot/README.md), triggered only when V67 has at most 8 unique predicted IDs and top-1 concentration at least 70%.

## Decisions after V68

Any conclusion must distinguish output-row weight norms from decoder hidden-state dynamics and optimizer history. Even if norms are highly skewed, this alone would not prove why the model collapsed to four argmax IDs. A separate causal experiment or checkpoint comparison is required before changing the training objective or allowing a fresh bounded pilot.

Training remains disabled. BLIND TEST remains closed. Historical V62 training authorization cannot be reused.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
