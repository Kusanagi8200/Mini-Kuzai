# Mini-Kuzai Phase 03 - V69 Output Head Norm Counterfactual 001

Date --> 2026-10-31

Status --> **V69 GPU / GOGIT VERIFIED / V62 FROZEN / NO NEW TRAINING**

## Research objective

V65-V68 show a frozen V62 model concentrating its next-token argmax on **four distinct token IDs** despite **606 distinct expected IDs**. In V68, the average norm of the selected output rows was **0.360**, versus **0.293** for the expected rows. BPE gold-token logits were further below the winning logits than raw-byte gold-token logits, by 3.466 versus 1.174 units on average.

This correlation does not establish that row norms caused the collapse. V69 tests a **read-only in-memory counterfactual** using the same hidden states and the same 36 VALIDATION sequences.

## Exactly defined interventions

The frozen V60 model uses a bias-free output projection tied to the token embedding matrix. Denote the original output row for vocabulary token `i` as `W_i`, its L2 norm as `n_i` and the average norm of all nonzero rows as `n_mean`.

Three scenarios are evaluated -->

- BASE --> unmodified frozen V62 forward pass, using the original CUDA BF16 autocast path
- HALF --> FP32 logits computed from the frozen hidden states using `W_i * (n_mean / n_i)^0.5`
- FULL --> FP32 logits computed from those same hidden states using `W_i * (n_mean / n_i)`

A zero-norm row remains zero. The normalization includes **all 1024 output IDs**, including PAD, EOS and BOS, to avoid selective output manipulation. No gradients or optimizer steps are executed, and the model's embedding and LM-head parameters are never replaced.

**Numerical caveat** --> the counterfactual modes use FP32 matrix products whereas the original baseline is generated under CUDA/BF16. Result differences may therefore combine row-norm equalization and numerical-precision effects. They do not, by themselves, prove a causal change in model training or end-to-end generation quality.

The output-head pre-hook captures a batch's frozen hidden states without persisting them to disk. BASE, HALF and FULL are scored on precisely those positions and the same target tokens. The hook is removed in a `finally` block and the original model weights are checked for exact equality after evaluation.

## Controls before publishing

Required GOGIT references -->

- [V67 frozen output concentration](../reports/assistant-results/history/PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001.json)
- [V68 frozen output-head analysis](../reports/assistant-results/history/PHASE03-SMOLTALK-V68-OUTPUT-HEAD-001.json)

Mandatory baseline replication -->

- 36 frozen VALIDATION segments
- 9206 total next-token positions and 9170 nonspecial lexical positions
- 4294 true BPE target positions
- Original VALIDATION CE --> **4.733**
- Original distinct argmax IDs --> **4**
- Original dominant token share --> **72.58%**
- Original BPE gold-token top-1 coverage --> **3.26%**
- Original BPE gold-token top-5 coverage --> **6.85%**
- Original terminal EOS top-1 --> **14/36**
- Original top-1 predicted family proportions --> 6692 byte, 2428 BPE, 50 special (out of 9170)

Any baseline mismatch or model-weight mutation **blocks GOGIT publication**.

## Public numeric results

One GOGIT step with **exactly 30 numeric fields** -->

- Three immutable safety flags
- Four V69 identification/integrity counters
- Five frozen original-baseline measurements
- Nine HALF measurements
- Nine FULL measurements

For HALF and FULL the nine published values cover CE, distinct predicted IDs, dominant-token fraction, raw-byte and BPE predicted fractions, BPE exact top-1/top-5 coverage, terminal EOS top-1 and overall lexical top-1.

The prefix is `V69_NORM_`. Fractions use basis points (10000 = 100%) and CE is multiplied by 1000. Zero-sized categories are not silently interpreted as valid accuracy figures.

No token IDs, prompts, decoded texts, hidden states, individual logits, source IDs or private training data are included in GOGIT.

## AUTOPILOT V2

New campaign --> `autopilot/campaigns/phase03-autopilot-v2.json`

New campaign ID --> `phase03-norm-v2` (does not overwrite the completed or interrupted V1 state)

The six automatic stages -->

1. Verify the immutable V67 GOGIT result
2. Verify the immutable V68 GOGIT result and tied-head invariants
3. Execute V69 if the prior documented four-token collapse is confirmed
4. Record **potential gain** if FULL yields more than four distinct predictions, BPE gold top-5 improves over 685 bp and CE stays at most 5.000
5. Record **CE regression** if FULL CE is above 5.000
6. Record **persistent collapse** if FULL still predicts at most four distinct tokens

Branches are independently recorded in the local journal. A gain classification is **not** permission to alter weights or train. If none of the predeclared branches matches, the numerical report remains available for manual scientific interpretation.

Each stage performs a GitHub fast-forward synchronization and strict numeric-report verification. The registered V69 runner has an immutable Git blob pin, and GOGIT retains the **30-metric and 300-second limits**.

## Files and run command

- Audit --> `tools/public-audits/phase03_v69_output_norm_counterfactual_001.py`
- CPU unit tests --> `tests/test_phase03_v69_output_norm_counterfactual_001.py`
- GOGIT runner --> `tools/run_v69_output_norm_counterfactual_001_job.py`
- AUTOPILOT V2 unit tests --> `tests/test_mini_kuzai_autopilot_v2.py`
- Numeric report step --> `PHASE03-SMOLTALK-V69-OUTPUT-NORM-COUNTERFACTUAL-001`
- Pre-implementation backup --> `tools/backups/V69-AUTOPILOT-PRE-20261031.md`

From a clean, synchronized local repo on fhc2 -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests -p 'test_phase03_v69_output_norm_counterfactual_001.py' -v && /root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests -p 'test_mini_kuzai_autopilot_v2.py' -v && /root/Mini-Kuzai/.venv/bin/python tools/mini_kuzai_autopilot.py --campaign phase03-autopilot-v2.json
```

**Verified outcome** --> [V69 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V69-OUTPUT-NORM-COUNTERFACTUAL-001.json) is published. BASE BF16 CE 4.733 with 4 predicted IDs, HALF FP32 CE 4.892 with 4 predicted IDs, FULL FP32 CE 5.048 with 7 predicted IDs. FULL BPE top-5 rises from 6.85% to 7.71%, but the CE regression prevents adopting this intervention as a model change. The independent [V70 precision-control GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V70-PRECISION-CONTROL-001.json) subsequently measured original FP32 CE 4.732 and isolated the precision confound. This diagnostic does not authorize training.

## Boundaries

Training permissions remain **disabled**, the historical V62 checkpoint remains **unchanged**, and the BLIND TEST remains closed. The historical V62 authorization does not grant any future training extension. No checkpoint or tokenizer changes are authorized by this experiment.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
