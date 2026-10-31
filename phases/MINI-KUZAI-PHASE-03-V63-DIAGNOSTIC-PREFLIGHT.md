# Mini-Kuzai - Phase 03 - V63 diagnostic preflight

Status --> **DIAGNOSTIC ONLY / TRAINING STOPPED / BLIND CLOSED**

V62 TRAIN RUN 001 stopped at cycle 2 after 69 optimizer steps and 597982 exposure tokens. Both V62 run and EOS calibration audits were published in GOGIT.

V63 performs a controlled diagnosis of the termination gap between teacher-forced VALIDATION and free autoregressive generation, plus token-level repetition measurements. This stage does not authorize or launch a new training run.

## Frozen inputs

- V62 cycle-2 checkpoint --> \`/root/Mini-Kuzai/runs/v62-margin-001/checkpoint-cycle-02.pt\`
- model architecture --> V60, unchanged
- authorization and trainer fingerprints --> verified using the V62 frozen runtime
- data --> 36 frozen VALIDATION segments, no BLIND access
- references --> V61 and V62 published GOGIT diagnostics, read-only
- decoding --> six fixed VALIDATION prompts, greedy, maximum 96 new tokens

The V61 checkpoint is not loaded and cannot become a V62 or V63 initialization.

## GPU methodology

Teacher-forced inference uses CUDA BF16, right-padded batches of four validation segments, and vectorized nonterminal EOS reductions. The six free-generation prompts are run together on CUDA with dynamic padding and independent EOS stop conditions.

Batched BF16 inference can produce minor numerical changes compared with earlier single-prompt, single-sequence diagnostics. The V63 rollout is therefore explicitly a new diagnostic, **not** a reproduction of V62's original six probe outputs.

Recorded numerical aggregates -->

- terminal EOS top-1 and pairwise margin satisfaction
- intermediate continuation versus EOS, true margin satisfaction
- ordinary nonterminal EOS top-1
- free-rollout EOS completions, ranking and probability
- generated token trigrams repetition, token lengths, entropy
- peak CUDA memory allocation and GPU batch size

No raw prompts or conversation text are published. No training, parameter update, optimizer step, scheduler change, or checkpoint write occurs.

## Runner and publication

On fhc2, in the repository root:

\`\`\`bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v63_diagnostic_preflight_job.py
\`\`\`

Runner gates --> local main clean/synchronized, V62 stopped cycle 2, no lock, existing V62 checkpoints and GOGIT histories. It executes one deterministic, numerical-only GOGIT audit and verifies the published report. Subsequent executions skip the completed stage.

GOGIT step --> \`PHASE03-SMOLTALK-V63-DIAGNOSTIC-PREFLIGHT-001\`

Decision after GOGIT --> interpret new diagnostics and decide V63 experiment design. No V62 cycle-4 resume and no V63 training until a separately frozen objective, protocol and authorization.

---

##### **\`THE KUZ NETWORK - KUSANAGI8200 - @2026\`**
