# Mini-Kuzai Phase 03 - V64 Language Learning Diagnostic 001

Status --> **PREPARED / NOT EXECUTED / NO TRAINING AUTHORIZATION**

## Objective

The automatic V63 language screen identified output defects despite 20/24 EOS completions and 0/24 UTF-8 errors. The next task is to characterize whether token fragmentation and next-token prediction are plausible contributors to poor generated language.

This audit does **not** conclude that the tokenizer or architecture is defective. It records quantitative evidence required for the next experimental choice.

## Frozen corpus and model

- Model --> V62 cycle-2 checkpoint at `/root/Mini-Kuzai/runs/v62-margin-001/checkpoint-cycle-02.pt`
- Training state --> STOPPED after 69 optimizer steps, 597982 exposed tokens
- Architecture --> 1184512 parameters, vocabulary 1024, four Transformer blocks
- Tokenizer --> frozen V56 Byte-BPE whitespace, raw-byte IDs 3 through 258, BPE merge IDs 259 through 1023
- TRAIN --> 12 **fixed exploratory** segments, three per frozen training stream, using first/middle/last segment positions
- VALIDATION --> all 36 frozen segments and 9206 supervised next-token targets
- BLIND TEST --> not opened
- Compute --> GPU CUDA BF16 inference only, dynamic right-padding, batches of four sequences
- Training --> no optimizer steps, no state changes, no checkpoints produced

The 12-segment TRAIN sample is deliberately small and not representative of the 345-segment full corpus. Differences between TRAIN and VALIDATION are **descriptive**, not an unbiased estimate of generalization.

## Measured dimensions

**Tokenization**

- Bytes per non-special token for sampled TRAIN and full VALIDATION
- Proportion of single-byte tokens among non-special token occurrences
- BPE vocabulary and merge inventory

**Teacher-forced next-token prediction**

- Mean cross-entropy / next-token NLL across all valid target positions
- Top-1 accuracy for the true next token
- Proportion of raw-byte token targets versus BPE merge targets
- Separate mean NLL for raw-byte targets and merged targets
- Absolute cross-entropy difference between TRAIN sample and VALIDATION, plus sign flag
- EOS top-1 at the 36 validation sequence boundaries, cross-checked against the corrected immutable V63 diagnostic

All token-level loss means are weighted by their number of valid positions. Cross-entropy is computed with FP32 logits following BF16 GPU forward passes and with padding targets ignored.

This diagnostic does not directly evaluate syntax, semantic understanding, persona, or multi-turn conversation. Tokenization fragmentation alone is not evidence of a model defect.

## Fully automated GOGIT pipeline

- Audit --> `tools/public-audits/phase03_v64_language_learning_diagnostic_001.py`
- Unit tests --> `tests/test_phase03_v64_language_learning_diagnostic_001.py`
- Runner --> `tools/run_v64_language_learning_diagnostic_001_job.py`
- GOGIT step --> `PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-001`

Execute once from a clean, synchronized Mini-Kuzai checkout on fhc2 -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v64_language_learning_diagnostic_001_job.py
```

The runner performs immutable-checkpoint and stopped-run verification, checks the V63 automatic language-screen report, runs CPU unit tests, computes GPU diagnostics and publishes exactly 30 numeric-only metrics via GOGIT. It verifies the GitHub push and is idempotent when the report is already valid.

No human scoring, no interactive prompt and no raw TRAIN or VALIDATION content is published.

Report flags -->

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V64_LANG_BLIND_ACCESS=0`

## Decision after GOGIT

Compare tokenization fragmentation, TRAIN/VALIDATION NLL and base-byte versus BPE losses with the historical V62 validation-loss trajectory. If the model's next-token performance remains weak even on the sampled TRAIN sequences, investigate learned representations, model capacity and duration of training before changing EOS or decoder settings.

A separate reviewed protocol is mandatory before any resumed or new training.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
