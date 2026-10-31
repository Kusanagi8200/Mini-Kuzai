# Mini-Kuzai Phase 03 - V63 Decoding Robustness 001

Status --> **PREPARED / NOT EXECUTED / TRAINING STOPPED**

This diagnostic checks whether the favorable Top-k / Top-p termination result from the initial six-prompt, one-seed ablation reproduces across independent random seeds.

## Frozen inputs

- V62 checkpoint --> `/root/Mini-Kuzai/runs/v62-margin-001/checkpoint-cycle-02.pt`
- Mandatory V62 stop --> cycle 2, 69 optimizer steps, 597982 exposed tokens
- Corpus --> frozen VALIDATION, six fixed prompts
- BLIND TEST --> CLOSED
- Training --> DISABLED
- Device --> CUDA, BF16 inference
- Deterministic seeds --> integers 6301 through 6308 inclusive
- Maximum generation --> 96 new tokens per prompt
- Samples --> 8 seeds x 6 prompts x 2 decoding modes = 96 trajectories

## Two controlled strategies

| Mode | Specification |
| --- | --- |
| TEMP | Temperature 0.8, multinomial over complete vocabulary |
| TOPP | Temperature 0.8, top-k 40, nucleus threshold 0.9, multinomial |

Both strategies preserve the frozen V63 decoding-ablation sampling logic. Each seed gets an independent CUDA random generator and generates the same six prompts in order.

**GPU optimization** --> Run all active seed/prompt trajectories through the model together, dynamically right-padded. Select the true last-logit index for each prompt. Use one independent sampler per seed so its random-number stream is not shared with other seeds. Logits can exhibit minor BF16 differences from a six-prompt-only run due to the new batch dimensions. Do not require exact reproducibility of the original single-seed results. The immutable GOGIT ablation history remains a prerequisite.

## Public numerical metrics

Across the 48 trajectories per mode -->

- EOS completion count and minimum/maximum completions per seed (each seed has six prompts)
- Number of outputs with no more than 8 and 16 generated tokens, including EOS
- Mean number of generated tokens
- Repeated token trigram and eight-gram fractions, in basis points
- Mean unique generated-token fraction, in basis points
- Number of nonvalid UTF-8 outputs
- Number of outputs containing serialized `USER:` or `MINI-KUZAI:` role markers

The latter two measures only detect specific surface-form failures. They do not demonstrate semantic correctness, consistency or Mini-Kuzai persona fidelity.

**Statistical limitation** --> Eight seeds and six fixed VALIDATION prompts provide a reproducibility screen, not a generalization claim. Do not infer a universal 100% EOS rate or high-quality conversation from the audit.

## GOGIT pipeline

- Audit --> `tools/public-audits/phase03_v63_decoding_robustness_001.py`
- CPU tests --> `tests/test_phase03_v63_decoding_robustness.py`
- Runner --> `tools/run_v63_decoding_robustness_001_job.py`
- Step --> `PHASE03-SMOLTALK-V63-DECODING-ROBUSTNESS-001`

To run from the Mini-Kuzai repository root on fhc2 -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v63_decoding_robustness_001_job.py
```

The runner verifies clean synchronized Git, the V62 stopped run state and frozen checkpoint, the prior V63 GOGIT ablation, then runs CPU unit tests before GPU work. GOGIT accepts 30 approved numeric metrics only, performs a time-bounded audit, commits and pushes results and verifies the remote HEAD. A rerun of a validated report is idempotent.

## Decision after results

Review mode-by-mode EOS stability, per-seed range, short outputs, repetition, diversity, UTF-8 and role leakage. A separate supervised human review of locally retained private generations may be needed before assessing semantic coherence and personality. No raw text is published by GOGIT.

No V62 cycle 4 continuation, new trainer, optimizer changes, checkpoint replacement or V63 model training is authorized by this step.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
