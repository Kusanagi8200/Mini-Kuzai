# Mini-Kuzai Phase 03 - V64 Language Learning Diagnostic 002

Status --> **GPU EXECUTION COMPLETED / GOGIT PUBLISHED / V64 CLOSED**

## Verified V64-002 results - 2026-10-31

Successful GOGIT report --> [PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002](../reports/assistant-results/history/PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002.json)

Commit --> [`9d8dcb62b6e9`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/9d8dcb62b6e9bc3826f95eb93953c95c28835132)

| Indicator | TRAIN exploratory sample | Frozen VALIDATION |
| --- | --- | --- |
| Segments | 12 | 36 |
| Next-token targets | 10115 | 9206 |
| Cross-entropy | 4.664 | 4.733 |
| Top-1 accuracy | 33.97% | 29.20% |
| Bytes per non-special token | 1.970 | 1.874 |
| Single-byte token share | 51.23% | 53.17% |
| Raw-byte target mean NLL | 3.182 | 3.386 |
| BPE-merged target mean NLL | 6.221 | 6.268 |

Additional verified metrics --> absolute VALIDATION minus sampled-TRAIN CE difference **0.069**, VALIDATION terminal EOS top-1 **14/36**, CUDA/BF16 PASS, GPU peak allocated **133 MiB**.

The TRAIN sample comprises 12 deliberately chosen segments, not a statistically representative corpus sample. A small cross-entropy difference cannot establish generalization. The raw-byte/BPE NLL gap may partly reflect token frequency and target distribution and is **not** proof that the tokenizer must be replaced.

GOGIT records `SEMANTIC_VALIDATION_COMPLETE=0`, `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0` and `V64_LANG_BLIND_ACCESS=0`. No new training was started. The next step is the proposed [V65 readiness study](MINI-KUZAI-PHASE-03-V64-CLOSURE-V65-READINESS-2026-10-31.md), not an automatic training continuation.

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
