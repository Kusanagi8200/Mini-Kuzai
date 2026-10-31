# Mini-Kuzai Phase 03 - V65 Token Frequency Diagnostic 001

Status --> **AUDIT PUBLISHED / GPU EXECUTION PENDING / NO TRAINING AUTHORIZATION**

Date --> 2026-10-31

## Goal

V64 demonstrated a substantial difference in next-token negative log-likelihood between raw-byte targets and merged Byte-BPE targets. This V65 investigation checks whether part of the difference can be explained by **token frequency in the frozen TRAIN data** before considering tokenizer replacement, architecture changes or further training.

This is a quantitative **token-learning diagnostic**, not a test of reasoning, persona, semantic coherence or linguistic adequacy.

## Frozen experimental protocol

- Model --> frozen V62 cycle-2 checkpoint, 69 optimizer steps, 597982 exposed tokens
- Architecture --> V58/V60 decoder-only, 1,184,512 parameters
- Tokenizer --> V56 byte-level BPE, vocabulary 1024, single-byte token IDs 3 to 258, merged token IDs 259 to 1023
- Frequency reference --> **all 345** frozen TRAIN segments from the four authorized V59 streams, reconstructed exactly once
- Prediction evaluation --> **all 36** frozen VALIDATION segments with 9206 total next-token targets
- Lexical next-token evaluation --> **9170** VALIDATION targets excluding 36 EOS terminal positions
- BLIND TEST --> frozen and closed, no access
- Compute --> CUDA/BF16 inference only, batches of four sequences, right-padding ignored for loss
- GOGIT execution limit --> unchanged at 300 seconds
- Source of frozen model/corpus checks --> successful V64-002 read-only preflight

The TRAIN frequency counts exclude BOS, PAD and EOS. VALIDATION bucket metrics exclude special-token targets, while the full VALIDATION cross-entropy includes terminal EOS as in V64.

## Predeclared frequency strata

| Group | Token kind | Count in full TRAIN |
| --- | --- | --- |
| B0 | Single-byte token | Absent, 0 occurrences |
| B1_9 | Single-byte token | 1 to 9 occurrences |
| B10P | Single-byte token | 10 or more occurrences |
| M0 | Byte-BPE merged token | Absent, 0 occurrences |
| M1_9 | Byte-BPE merged token | 1 to 9 occurrences |
| M10P | Byte-BPE merged token | 10 or more occurrences |

Each category publishes exactly three numeric aggregates -->

- COUNT --> number of matching lexical target positions in frozen VALIDATION
- TOP1_BP --> correct next-token predictions divided by category target positions, scaled by 10000
- NLL_X1000 --> average negative log-likelihood for the true next-token targets, scaled by 1000

For an empty category, COUNT=0 and the other two numbers are stored as **0 as a numeric placeholder**, not as genuine accuracy/loss evidence. Never compare an empty category's zero to other categories.

The full public report also includes the number of TRAIN lexical-token occurrences and distinct token IDs observed in TRAIN, the VALIDATION lexical target count, full VALIDATION CE, EOS top-1 and BF16/GPU checks.

## Validation and strict controls

The V65 audit must -->

1. Verify the completed V64-002 immutable GOGIT report
2. Reuse the exact V64-002 authorization, trainer-freeze, dataset inventory and checkpoint checks
3. Reconstruct TRAIN and VALIDATION **once** without generating the unused training boundary index
4. Freeze frequency thresholds at 0, 1-9 and 10+ before calculating results
5. Confirm all six categories together cover exactly 9170 lexical VALIDATION targets
6. Reproduce the frozen EOS terminal top-1 result of 14/36
7. Reproduce full VALIDATION CE of 4.733 within a rounding tolerance of 0.002
8. Publish **30 integer-only metrics** through GOGIT, without raw tokens, text, transcripts or source IDs

Explicit report flags -->

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V65_FREQ_BLIND_ACCESS=0`

## Implementation

- Audit --> `tools/public-audits/phase03_v65_token_frequency_diagnostic_001.py`
- Unit tests --> `tests/test_phase03_v65_token_frequency_diagnostic_001.py`
- Runner --> `tools/run_v65_token_frequency_diagnostic_001_job.py`
- GOGIT step --> `PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001`
- Original frozen source --> `tools/public-audits/phase03_v64_language_learning_diagnostic_002.py`
- Backup of existing policy --> `tools/backups/GOGIT-PRE-V65-TOKEN-FREQUENCY-20261031.md`

Execute on fhc2 from the clean repository root -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v65_token_frequency_diagnostic_001_job.py
```

The runner checks the frozen V62 state, runs CPU tests, calculates the GPU diagnostics, publishes GOGIT and verifies the remote report. It is idempotent when a valid report already exists.

## Interpretation and next decision

A low-frequency merged-token category with substantially poorer prediction accuracy than frequent merged tokens would support a **token-frequency / sparsity hypothesis**, not prove that the tokenizer is inherently wrong.

Comparisons remain observational. Some token types can be systematically harder regardless of frequency. TRAIN is the source of the frequency distribution, but the prediction scores are measured on held-out VALIDATION. No gradients or additional training are performed.

After the published numeric report is analyzed by ChatGPT, choose the next diagnostic. Do not authorize more optimizer steps, unfreeze the BLIND TEST or change the V56 tokenizer on this evidence alone.

Status at publication --> **the experiment is prepared, not yet measured on fhc2**.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
