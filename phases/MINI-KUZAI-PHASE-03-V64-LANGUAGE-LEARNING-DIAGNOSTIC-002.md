# Mini-Kuzai Phase 03 - V64 Language Learning Diagnostic 002

Status --> **CODE PUBLISHED / GPU EXECUTION NOT YET CONFIRMED**

## Incident and confirmed evidence

- V64 language diagnostic 001 --> six unit tests PASS, GOGIT 300-second subprocess timeout, no published diagnostic report
- V64 runtime trace 001 --> reached 155-second bounded profiler limit while constructing training boundary index, before checkpoint scoring
- Frozen TRAIN rebuild --> 98270 ms, including 91304 ms for public streams
- Frozen VALIDATION rebuild --> 2765 ms
- Training boundary-index operation --> active at trace timeout; no completed duration available
- Duplicate reconstruction --> present in original V64 code because `T.verify_runtime()` rebuilds frozen streams, and the V64 audit repeats them afterward

No training, BLIND access, optimizer step or checkpoint modification occurred during those diagnostic attempts.

## Backup and non-destructive correction

- Original script --> `tools/public-audits/phase03_v64_language_learning_diagnostic_001.py` remains **unchanged**
- Frozen original Git commit --> `12a08e915f4c0b48885190958d1432cf286f51fb`
- Original script Git blob --> `987de8ef28a647de25306f2a35d50564ad3fbfa1`
- Timestamped immutable backup manifest --> `tools/backups/V64-ORIGINAL-20261031T163000-CET.md`
- GOGIT policy backup manifest --> `tools/backups/V64-GOGIT-PRE-V002-20261031T163000-CET.md`
- New audit --> `tools/public-audits/phase03_v64_language_learning_diagnostic_002.py`
- New tests --> `tests/test_phase03_v64_language_learning_diagnostic_002.py`
- New runner --> `tools/run_v64_language_learning_diagnostic_002_job.py`

The corrected audit uses the existing, separately checked model/checkpoint/runtime but calls `T.verify_authorization()`, `T.verify_trainer_freeze()` and `T.load_protocol()` directly.

It builds TRAIN once and VALIDATION once. Both freshly computed inventories are compared in full with their frozen trainer inventories. The original schedule preview is independently compared with the frozen schedule preview. It does not rebuild the training boundary index, which the standard next-token cross-entropy diagnostic does not consume.

## Unchanged evaluation specification

- V62 cycle-2 stopped checkpoint, 69 optimizer steps and 597982 exposure tokens
- Byte-BPE vocabulary 1024
- 12 deterministically sampled TRAIN segments (first/middle/last per four streams)
- All 36 VALIDATION segments, 9206 predicted next-token positions
- CUDA/BF16 read-only model inference
- TRAIN/VALIDATION next-token cross-entropy, top-1 and byte-versus-merged-token losses
- Terminal EOS top-1 expected 14/36 from corrected historical V63 diagnostic
- 30 numerical metrics; no raw user prompts, conversations, model generations or BLIND data
- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0`
- GOGIT global process timeout **unchanged at 300 seconds**

The TRAIN sample is exploratory and must not be treated as a statistically representative estimation of the training loss.

## Run on fhc2

From the repository root -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v64_language_learning_diagnostic_002_job.py
```

This runner requires a clean synchronized main branch, frozen V62 run and V63 GOGIT prerequisites, CPU unit tests, the v002 GPU audit, successful numeric-only GOGIT publication and remote-history verification. It is idempotent for an already published validated result.

Step ID --> `PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002`

A new timeout or integrity failure is diagnostic evidence. Do not raise GOGIT's timeout without further profiling. The next decision about training, tokenizer and model size depends on the published numerical results.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
