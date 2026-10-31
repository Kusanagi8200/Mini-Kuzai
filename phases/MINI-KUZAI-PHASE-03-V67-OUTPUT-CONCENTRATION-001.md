# Mini-Kuzai Phase 03 - V67 Output Concentration 001

Date --> 2026-10-31

Status --> **CODE PUBLISHED / GPU EXECUTION PENDING / NO TRAINING AUTHORIZATION**

## Objective

V66 established a bias in the frozen V62 model's top-1 outputs -->

- **6692 / 9170** lexical contexts have raw-byte tokens as the model's predicted class
- **2428 / 9170** predict a merged Byte-BPE token
- **50 / 9170** predict special tokens
- **2254 / 4294** true merged-token contexts are predicted as raw-byte outputs
- The total merged-token softmax probability mass for gold merged-token contexts is still **64.84%**
- The prior frequency audit indicated all lexical top-1 successes were confined to gold tokens with at least 1000 TRAIN occurrences

The immediate V67 question --> is the model's exact predicted vocabulary collapsing onto a small number of high-scoring token IDs, and are the correct gold tokens often near the top even when not rank one?

This diagnostic does not train, decode autoregressively, evaluate semantics or make an architecture decision.

## Frozen resources and safeguards

- Model --> unchanged V62 checkpoint, cycle 2 STOPPED, 69 optimizer steps and 597982 exposure tokens
- TRAIN --> four frozen streams reconstructed once only for integrity checks; no training and no gradients
- VALIDATION --> all 36 frozen segments, 9206 next-token targets
- Lexical positions --> **9170** nonspecial targets, of which **4876** are raw-byte and **4294** are merged BPE
- V56 tokenizer --> vocabulary 1024, unchanged
- V64-002 read-only preflight --> verifies authorization/trainer freeze, TRAIN and VALIDATION inventories, schedule preview and checkpoint identity
- V66-A and V66-B --> both successful immutable GOGIT reports required
- BLIND TEST --> no access
- CUDA/BF16 --> inference only; batch size four
- GOGIT --> original 300-second limit and 30-metric ceiling both unchanged

## Prediction concentration and diversity

At each lexical VALIDATION target position, the full 1024-way next-token logit argmax is counted, **including an argmax to a special token**. Frequency statistics are computed from this distribution of predicted **IDs**, not from generated text.

Metrics -->

- Distinct predicted IDs versus distinct expected gold IDs
- Distinct predicted raw-byte IDs versus distinct predicted merged BPE IDs
- Fraction of lexical positions accounted for by the 1, 5, 10 and 20 most frequently predicted IDs, in basis points
- Empirical Shannon entropy of the argmax token-ID distribution, in natural-log units scaled by 1000

Higher top-k concentration and low distinct-ID count would support the output-vocabulary-collapse hypothesis. Unlike token rarity counts, these measurements directly describe what the model chooses.

## Stable gold-token rank and top-k coverage

Gold next-token ranks are calculated across the **complete 1024-token vocabulary**, including specials.

Definition --> rank 1 plus number of logits strictly above the gold logit plus number of equal-scoring logits with a **smaller token ID**. This stable tie break agrees exactly with the existing argmax's first-ID winner and prevents optimistic rank-one counts when BF16 produces ties.

For raw-byte targets and merged BPE targets separately -->

- Gold token in the model's top 1, top 5, top 10 and top 50
- Median gold-token rank

Metrics are scaled to basis points for the four coverage thresholds, while median ranks remain unscaled integers. The gold groups contain **4876** and **4294** positions respectively. This is teacher-forced evaluation, not free generation.

The measured type-level confusion matrix is checked against V66-A so that any token-position or checkpoint drift fails before publication. Cross-entropy must reproduce **4.733**, and terminal EOS top-1 must reproduce **14/36**.

## GOGIT output contract

The V67 GOGIT record contains **exactly 30 numeric fields** -->

- Three standard safety flags
- Eight V67 pipeline and frozen-reference checks
- Nine diversity and concentration counters
- Eight family-specific top-k rank coverage measures
- Two family-specific median gold ranks

(Note --> the nine concentration counters include distinct predicted/gold IDs, distinct predicted types, four top-frequency shares and entropy; the exact numeric allowlist is authoritative.)

Required flags -->

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V67_CONC_BLIND_ACCESS=0`

Never publish raw token-ID lists, prompts, generated answers, individual logits, ranks per record, source IDs or private conversation content.

## Implementation

- Audit --> `tools/public-audits/phase03_v67_output_concentration_001.py`
- CPU unit tests --> `tests/test_phase03_v67_output_concentration_001.py`
- Runner --> `tools/run_v67_output_concentration_001_job.py`
- GOGIT step --> `PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001`
- Frozen read-only dependency --> V64-002 audit and V66-A/V66-B immutable GOGIT reports
- GOGIT policy backup --> `tools/backups/GOGIT-PRE-V67-CONCENTRATION-20261031.md`

Single command on fhc2, with clean synchronized Git main -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v67_output_concentration_001_job.py
```

The runner performs V62 stop checks, unit tests, the read-only GPU audit, GOGIT publication and remote report verification. It is idempotent if a complete report has already been published.

## Decision after V67, not yet determined

- **High top-1-ID concentration and poor gold top-50 coverage** --> supports restricted output-vocabulary use / insufficient token discrimination
- **High top-1-ID concentration but improved gold top-10 or top-50 coverage** --> suggests the model assigns useful relative rankings to targets but fails to select them as argmax
- **Low concentration and poor top-50** --> suggests more general next-token modeling limits rather than simple argmax collapse

Checkpoint inspection, controlled training-continuation proposals or tokenizer experiments remain **separate subsequent decisions**. V67 does not authorize any additional training, changes to the tokenizer, model-size changes or BLIND access.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
