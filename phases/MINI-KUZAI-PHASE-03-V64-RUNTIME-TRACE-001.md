# Mini-Kuzai Phase 03 - V64 Runtime Trace 001

Status --> **PREPARED / NOT YET EXECUTED**

## Incident

The existing V64 `LANGUAGE-LEARNING-DIAGNOSTIC-001` passed six CPU unit tests but exceeded the immutable GOGIT subprocess timeout of 300 seconds. The reported result was `PUSH: NOT_CONFIRMED`. No V64 learning-diagnostic history was published.

Changing the timeout without evidence would risk masking an expensive or stalled stage.

## Verified code-level concern

`T.verify_runtime()` rebuilds all frozen TRAIN streams, VALIDATION, the schedule preview, and boundary inventory. After its preflight, the V64 audit calls `T.build_training_streams()` and `T.build_validation_segments()` again. This duplication is present in the source, but it is **not** proof of the actual timeout cause.

## Read-only profiling protocol

A separate immutable GOGIT stage profiles the unchanged V64 audit, intercepting only function-entry and function-exit timing messages.

- Original V64 audit --> left unchanged
- Profiler --> `tools/public-audits/phase03_v64_runtime_trace_001.py`
- Runner --> `tools/run_v64_runtime_trace_001_job.py`
- Unit tests --> `tests/test_phase03_v64_runtime_trace_001.py`
- GOGIT step --> `PHASE03-SMOLTALK-V64-RUNTIME-TRACE-001`
- Worker budget --> 155 seconds, below the unchanged GOGIT 300-second limit
- Process --> child subprocess, terminated after worker budget when incomplete
- Corpus --> existing frozen TRAIN and VALIDATION only
- Checkpoint --> frozen V62 cycle 2, no update
- BLIND TEST --> closed
- No training, no optimizer step, no grading, no raw conversation publication

Instrumented stages with numeric codes -->

| Code | Stage |
| --- | --- |
| 1 | PREFLIGHT |
| 2 | VERIFY_RUNTIME |
| 3 | BUILD_TRAIN |
| 4 | BUILD_VAL |
| 5 | LOAD_POOL |
| 6 | LOAD_PUBLIC |
| 7 | LOAD_CONTROLLED |
| 8 | SCHEDULE |
| 9 | BOUNDARY |
| 10 | LOAD_TOKENIZER |
| 11 | TOKEN_STATS |
| 12 | SCORE |
| 13 | CHECKPOINT_LOAD |

The parent publishes numeric elapsed milliseconds for **completed** spans, the code for the last started span, and the code for the innermost active unfinished span if its 155-second budget expires. Nested durations are inclusive and must not be summed to infer total runtime.

`V64_TRACE_PASS=1` means the bounded profiler produced a valid trace. `V64_TRACE_TIMEOUT=1` means the **instrumented diagnostic itself did not finish**. Neither flag means the original V64 diagnostic passed.

The profiler explicitly publishes -->

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V64_TRACE_BLIND_ACCESS=0`

## Run on fhc2

From the root of the Mini-Kuzai Git checkout -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v64_runtime_trace_001_job.py
```

The runner performs clean-Git, frozen-run and preceding V63 checks, executes the parser unit tests, captures the bounded stage trace, publishes only numeric metrics with GOGIT, and checks the remote report. No human output copying is required.

## Decision gate

Read the published trace before changing anything in the original V64 audit. If the bottleneck is repeated frozen corpus verification, consider a validated once-only runtime preparation design. If the bottleneck is model inference, consider reducing right-padding, microbatch dimensions or redundant forward work, while retaining numerical-equivalence tests. GOGIT's global timeout stays unchanged.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
