# Mini-Kuzai Phase 03 - V70 Precision-Control 001

Date --> 2026-10-31

Status --> **CODE / TESTS / AUTOPILOT V3 PUBLISHED; LOCAL CPU + GPU EXECUTION PENDING**

## Scientific question

V69 measured row-norm equalization on the frozen V62 model. HALF and FULL improved the BPE top-5 target coverage from 6.85% to 7.27% and 7.71%, while CE deteriorated from 4.733 to 4.892 and 5.048. The argmax token inventory increased from 4 IDs in BASE to 7 IDs in FULL.

The V69 baseline was calculated under CUDA/BF16, whereas the counterfactual projections were FP32. Therefore the reported differences combine a possible norm effect with a numerical-precision change.

**V70 isolates that confound without any model update.**

## Frozen comparison

All four variants use the same 36 frozen VALIDATION records, tokenization, V62 checkpoint and hidden states. The V64 model preflight and V67 stable gold-rank function are reused.

| Mode | Hidden states | Output projection |
| --- | --- | --- |
| BF16 | From frozen original forward | Original autocast BF16 |
| FP32 | Same captured hidden states | Original weight matrix, FP32 |
| HALF | Same captured hidden states | V69 alpha 0.5 normalized rows, FP32 |
| FULL | Same captured hidden states | V69 alpha 1.0 normalized rows, FP32 |

The *FP32* mode is the precision-only control. Comparing FULL against FP32 is therefore a more appropriate test of the row-norm effect than comparing FULL against BF16 alone.

The experiment does not change the training objective, optimizer, tokenizer, recorded weights or checkpoint.

## Verification gates

The V69 immutable GOGIT report must be present and valid, including its original source SHA256. All frozen reference and current training safety flags must indicate that no new training or BLIND access occurred.

**Before any V70 GOGIT publication**, the audit must exactly reproduce the already published V69 BF16, HALF and FULL metrics, including relevant accuracy, cross-entropy, top-token share and EOS values. The BF16 baseline must also reproduce V67/V68 CE **4.733**, argmax distinct IDs **4**, dominant share **72.58%**, BPE top-1 **3.26%**, BPE top-5 **6.85%** and terminal EOS **14/36**.

All output head matrices remain temporary; a pre-hook captures frozen hidden states and is removed on exit. Final weight equality to the original checkpoint is checked.

## Exactly 30 public numeric metrics

The report uses -->

- Three standard flags --> `SEMANTIC_VALIDATION_COMPLETE=0`, `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0`
- Three V70 integrity counters --> `V70_CTRL_PASS`, `V70_CTRL_BLIND_ACCESS`, `V70_CTRL_VAL_LEXICAL`
- Six per-mode fields × four modes --> cross-entropy ×1000, distinct top-1 IDs, dominant-token share in basis points, BPE gold top-1 in basis points, BPE gold top-5 in basis points and EOS top-1 count

No individual token IDs, prompts, private data, logits or checkpoint tensors are committed to GitHub.

GOGIT retains the **30-field limit** and **300-second subprocess limit**.

## AUTOPILOT V3

The reviewed campaign [`phase03-autopilot-v3.json`](../autopilot/campaigns/phase03-autopilot-v3.json) contains six predetermined stages -->

1. Reverify V68 output-head GOGIT
2. Reverify V69 norm-counterfactual GOGIT
3. Execute V70 only if V69 passed, then publish and validate its GOGIT report
4. Classify the FP32 baseline as near BF16 if CE ≤ 4.800 and at most six distinct predicted IDs
5. Classify an FP32 CE drift if CE > 4.800
6. Classify a prediction-diversity drift if FP32 exceeds six distinct predicted IDs

The three classifications can coexist or be skipped. They are observations only, not optimization or training authorizations.

**Training remains unregistered, V62 frozen, BLIND closed.** The original V69 campaign and archived reports are left untouched.

## Sources

- [V69 published GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V69-OUTPUT-NORM-COUNTERFACTUAL-001.json)
- Code --> `tools/public-audits/phase03_v70_precision_control_001.py`
- GPU/GOGIT runner --> `tools/run_v70_precision_control_001_job.py`
- CPU test suite --> `tests/test_phase03_v70_precision_control_001.py`
- AUTOPILOT V3 tests --> `tests/test_mini_kuzai_autopilot_v3.py`
- Pre-change backup --> `tools/backups/V70-PRECISION-CONTROL-PRE-20261031.md`

To run the new V3 campaign from a synchronized clean repository -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/mini_kuzai_autopilot.py --campaign phase03-autopilot-v3.json
```

The V70 GPU audit is not complete merely because source code was published. Wait for the immutable `PHASE03-SMOLTALK-V70-PRECISION-CONTROL-001` GOGIT report before interpreting any counterfactual.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
