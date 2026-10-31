# Mini-Kuzai Phase 03 - V63 Generation Failure Analysis 001

Status --> **DIAGNOSTIC PREPARED / NOT YET RUN / TRAINING STOPPED**

This stage examines failure modes at the mandatory V62 cycle-2 checkpoint using CUDA/BF16 inference and the frozen VALIDATION corpus. No new training is performed. The BLIND TEST stays closed.

## Evidence and prerequisites

- V62 TRAIN RUN 001 stopped at cycle 2, step 69, 597982 exposed tokens
- V62 EOS calibration history published and valid
- V63 diagnostic preflight 002 published and valid, superseding incorrect terminal-only figures in preflight 001
- V62 model, checkpoint, optimizer and frozen protocol unchanged
- Six fixed validation prompts, greedy generation, maximum 96 new tokens per probe
- All numerical output published through GOGIT with an explicit allowlist

## Analyses

**Teacher-forced VALIDATION**

- Probability that the model assigns to the expected next token, top-1 correctness and prediction entropy
- Mean positive terminal EOS logit deficit versus the best non-EOS competitor
- Mean positive intermediate continuation logit deficit versus EOS
- Terminal and intermediate top-1 and 0.25 margin compliance
- Ordinary nonterminal EOS top-1 frequency

**Free autoregressive generation**

- Mean positive EOS logit deficit against the best non-EOS competitor
- Probability of the selected greedy token and predictive entropy
- Repeated token trigram and 8-gram rates
- Number of probes containing repeated 8-grams
- First repeated 8-gram occurrence measured in generated token positions, averaged only over probes where one occurs
- Per-probe unique generated-token fraction, in basis points
- EOS completion count

GPU computations use the same frozen model and right-padded dynamic batches. The aggregate measurements are distinct from the earlier preflight 002 and are not treated as evidence of successful training.

## Safety and integrity

- The trainer module, model architecture, data splits, optimizer and checkpoints are read-only
- The existing V62 run directory must be stopped, unlocked and consistent with the frozen summary
- The frozen authorization and trainer fingerprints are verified
- The corrected V63 diagnostic 002 and historical V61/V62 GOGIT reports are required
- New teacher-forced top-1 and margin results must match the corrected V63 reference
- Generated EOS and trigram diagnostics must match the prior corrected probe reference
- Any mismatch aborts the audit before publication
- No raw dialogue, prompt or generated response is written to a public report
- No V62 cycle-4 continuation and no new V63 training authorization

## Execution on fhc2

From the Mini-Kuzai repository root -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v63_generation_failure_analysis_001_job.py
```

The runner checks Git synchronization and the V62/V63 frozen evidence, invokes the audit through GOGIT and verifies the committed report. Re-running the script skips a completed and validated publication.

GOGIT step --> `PHASE03-SMOLTALK-V63-GENERATION-FAILURE-ANALYSIS-001`

Next decision --> characterize EOS under-confidence and token loops, then design a new protocol only if the evidence supports it. No training or BLIND opening is allowed by this step.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
