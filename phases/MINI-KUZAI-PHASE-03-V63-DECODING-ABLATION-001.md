# Mini-Kuzai Phase 03 - V63 DECODING ABLATION 001

Status --> **PREPARED / NOT EXECUTED / NO NEW TRAINING**

Purpose --> isolate the effect of decoding on repetition and EOS completion, without changing the frozen V62 model, training objective, optimizer, data or checkpoint.

## Fixed inputs

- Checkpoint --> `/root/Mini-Kuzai/runs/v62-margin-001/checkpoint-cycle-02.pt`
- Frozen VALIDATION --> six fixed prompts from `T._fixed_probe_segments()`
- Generation --> greedy or sampled, maximum 96 new token IDs per prompt
- Device --> CUDA, inference mode, BF16 autocast
- Prompt batching --> six right-padded prompts, selecting the true final-token position for each
- Sample seed --> 6301, fixed CUDA generator per decoding strategy
- Source GOGIT audit --> `PHASE03-SMOLTALK-V63-GENERATION-FAILURE-ANALYSIS-001`
- Corrected prerequisite --> `PHASE03-SMOLTALK-V63-DIAGNOSTIC-PREFLIGHT-002`
- BLIND TEST --> CLOSED

## Decoding strategies

| Strategy | Configuration |
| --- | --- |
| GREEDY | Argmax logits, unchanged V63 reference |
| TEMP | Temperature 0.8, multinomial sampling across full vocabulary |
| TOPP | Temperature 0.8, top-k 40 then nucleus probability threshold 0.9, multinomial |
| REP | Greedy with repetition penalty 1.2 on previously generated non-special token IDs; prompt tokens are not penalized |

The ablation changes only inference-time token selection. It does **not** change the learned model. Sampling outcomes from six prompts with a single seed are exploratory, not statistically conclusive.

For each strategy, GOGIT publishes only five numeric aggregate measurements -->

- EOS completion count across six prompts
- Repeated generated-token trigram share in basis points
- Repeated generated-token eight-gram share in basis points
- Mean percentage of distinct generated token IDs in basis points
- Mean generated sequence length, times one hundred

Shared metadata --> six probes per mode, CUDA BF16, deterministic seed, PyTorch peak allocated memory, BLIND access flag.

The greedy strategy must reproduce the frozen V63 failure-analysis EOS, trigram and eight-gram numbers exactly or all publication stops. No raw prompts, output text, source IDs or model logits are published.

## Automated pipeline

Code --> `tools/public-audits/phase03_v63_decoding_ablation_001.py`

Runner --> `tools/run_v63_decoding_ablation_001_job.py`

GOGIT step --> `PHASE03-SMOLTALK-V63-DECODING-ABLATION-001`

Execution on fhc2, from the Mini-Kuzai repository root -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v63_decoding_ablation_001_job.py
```

The runner requires clean, synchronized `main`, stopped V62 cycle-2 artifacts, no active training lock, existing V62 and V63 public evidence and a clean tracked audit. It publishes one numeric-only report and verifies the pushed history. A rerun is idempotent if the report is already valid.

## Decision gate

Compare the four strategies after the report is published. Do not interpret a decoding-only improvement as model learning. Do not restart the V62 cycle-4 window or authorize V63 training without a separate objective/protocol freeze and review.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
