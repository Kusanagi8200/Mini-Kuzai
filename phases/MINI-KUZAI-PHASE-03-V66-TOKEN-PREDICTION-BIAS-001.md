# Mini-Kuzai Phase 03 - V66 Token Prediction Bias 001

Date --> 2026-10-31

Status --> **BOTH PARTS EXECUTED / GOGIT VERIFIED / NO NEW TRAINING**

## Verified V66 execution - 2026-10-31

Both 30-field GOGIT reports were published successfully -->

- [V66-A confusion and probability-mass GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-A-001.json), commit [`b2fdc0abe36c`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/b2fdc0abe36c35f6514453e5dd9c47dec03fdb7e)
- [V66-B detailed frequency GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-B-001.json), commit [`035f299a1399`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/035f299a139965b87dba66c03ce41a0b2ea9ee5f)

The **9170** nonspecial VALIDATION targets contained **4876** true raw-byte and **4294** true merged BPE tokens.

| True target family | Predicted raw-byte | Predicted merged BPE | Predicted special |
| --- | --- | --- | --- |
| Raw-byte | 4438 | 399 | 39 |
| Merged BPE | 2254 | 2029 | 11 |

Total argmax predictions --> **6692 raw-byte**, **2428 merged**, **50 special**. Raw-byte is selected in **72.98%** of all lexical contexts, compared with **53.17%** raw-byte gold targets.

By contrast, full-vocabulary softmax probability mass for gold merged-token contexts was **34.37% raw-byte**, **64.84% merged BPE**, **0.79% special**. The model does **not** globally suppress BPE probability mass, despite frequently selecting raw-byte IDs as argmax.

Fine-grained frequency top-1 accuracy -->

| TRAIN frequency | Raw-byte top-1 | Merged BPE top-1 |
| --- | --- | --- |
| 10-99 | 0% | 0% |
| 100-999 | 0% | 0% |
| 1000+ | 64.64% | 12.97% |

All correct lexical top-1 predictions in these strata are concentrated on tokens seen **at least 1000 times in TRAIN**. The output-token distribution itself has not yet been measured for concentration. **V67 OUTPUT CONCENTRATION 001** is designed to measure distinct predicted token IDs, frequency concentration, gold-token rank and top-k coverage.

Next prepared experiment --> [V67 frozen concentration and rank diagnostic](MINI-KUZAI-PHASE-03-V67-OUTPUT-CONCENTRATION-001.md). No new training is authorized.

## GOGIT 30-metric ceiling incident and partitioned correction

The original V66 audit passed **8 CPU tests**, computed its results, but GOGIT returned `Too many metrics` before committing. GOGIT's established `numeric_metrics()` parser refuses reports containing more than **30 fields**. The original V66 audit produces **57 fields**, so the attempted `PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-001` publication was **NOT_CONFIRMED** and has no successful report.

Correction --> retain the original full audit unchanged, reuse its numeric computation through a reviewed helper, and publish two separate immutable GOGIT reports without changing the global 30-metric limit.

- V66 Part A --> 30 metrics comprising three safety flags, twelve fixed model/reference fields, six top-1 confusion counts, six softmax mass shares and three B0 frequency-stratum fields
- V66 Part B --> 30 metrics comprising the same three safety flags and 27 remaining fine-grained frequency-stratum fields
- Combined unique fields --> **57**, with three safety fields intentionally duplicated
- Both audit producers --> independent frozen GPU inference for identical deterministic model/checkpoint/VALIDATION, no mutable intermediate cache
- If Part A was published successfully but Part B failed, the runner validates existing Part A and safely resumes at Part B
- Each report is individually verified; combined cross-part fields are also checked against V65 reference counts, normalization constraints and safety flags

GOGIT steps -->

- `PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-A-001`
- `PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-PART-B-001`

New components -->

- Partitioning logic --> `tools/phase03_v66_metric_partition.py`
- Audit A --> `tools/public-audits/phase03_v66_token_prediction_bias_part_a_001.py`
- Audit B --> `tools/public-audits/phase03_v66_token_prediction_bias_part_b_001.py`
- New CPU tests --> `tests/test_phase03_v66_metric_partition_001.py`
- One-command resume-safe runner --> `tools/run_v66_token_prediction_bias_partitioned_001_job.py`
- Pre-change immutable backup --> `tools/backups/V66-GOGIT-SPLIT-PRE-FIX-20261031.md`

Historical implementation note --> the split publication was initially prepared before execution. The two audits have now been published and verified, as recorded above. Do not interpret the former eight successful tests as successful GOGIT publication.

## Purpose and V65 prerequisite

V65 GOGIT has confirmed **52.00%** top-1 precision for frequent raw-byte targets compared with **3.27%** for frequent merged BPE targets. Most VALIDATION lexical targets belong to tokens that occur at least ten times in TRAIN. This makes simple absence or rarity insufficient as the entire explanation.

The key unanswered question --> does the frozen V62 model **predict raw-byte tokens disproportionately often** even when the true next token is a merged BPE token?

V66 distinguishes top-1 prediction bias from the total probability mass assigned to each token family, and tests more detailed frequency bands before any decision about changing the tokenizer, architecture or training exposure.

This is a numerical diagnostic of next-token logits. It is **not** a semantic, grammatical, reasoning, persona or conversation-quality evaluation.

## Frozen inputs and safety

- Training model --> V62 cycle-2 checkpoint frozen at 69 optimizer steps and 597982 exposed tokens
- Model --> V58/V60, 1,184,512 parameters, vocabulary 1024
- Tokenizer --> V56 whitespace Byte-BPE, unmodified
- TRAIN frequency reference --> **all 345 frozen TRAIN segments** and 294726 nonspecial token occurrences, 891 observed distinct token IDs
- VALIDATION scoring --> all 36 frozen VALIDATION segments, 9206 total next-token targets, 9170 nonspecial lexical targets
- Terminal EOS control --> 14/36 top-1, matching V63-V65
- Execution --> frozen CUDA/BF16 inference only, four sequences per batch
- BLIND TEST --> not opened
- Training --> disabled; no optimizer steps, no checkpoint writes
- Corpus and checkpoint integrity --> the already successful V64-002 preflight is reused; V65's frozen token-frequency estimator is reused
- GOGIT --> unchanged global execution limit of 300 seconds; numeric-only publication

Previous evidence --> [V65 successful frequency audit](../reports/assistant-results/history/PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001.json)

## Six-class top-1 confusion matrix

The gold next-token type is either **B** (raw-byte token, IDs 3-258) or **M** (BPE-merged token, IDs 259-1023).

The model's argmax prediction is classified as -->

- B --> raw-byte token
- M --> BPE-merged token
- S --> SPECIAL token (PAD, BOS or EOS, IDs 0-2)

For each of the two gold classes, the six confusion counters report the number of positions where the predicted type was B/M/S. Totals must exactly reproduce the V65 gold families --> **4876 B targets + 4294 M targets = 9170**.

**Important** --> a prediction can have the correct token type but the wrong token identity. Confusion by family is therefore not a substitute for exact token top-1 accuracy.

## Softmax mass by gold class

For each gold class B/M, sum the full 1024-way predicted softmax probabilities assigned to -->

- all raw-byte token IDs (B)
- all merged BPE token IDs (M)
- all three special-token IDs (S)

The report contains the average share for each target class, measured in basis points. All three shares for a single gold class should sum to approximately 10000 basis points, subject to integer rounding. Unlike argmax, this shows the **overall model distribution** and not just the highest-scoring token.

The model can favor B in argmax while assigning more total probability to M because M contains 765 possible IDs against 256 B IDs. Both views are necessary.

## Predeclared finer frequency strata

Two token families multiplied by five frequency intervals -->

| Group | Full TRAIN frequency per token |
| --- | --- |
| B0 / M0 | 0 |
| B1_9 / M1_9 | 1-9 |
| B10_99 / M10_99 | 10-99 |
| B100_999 / M100_999 | 100-999 |
| B1000P / M1000P | 1000 or more |

Each stratum reports three metrics -->

- COUNT --> number of VALIDATION next-token target positions in that group
- TOP1_BP --> correct exact token predictions, scaled to 10000
- NLL_X1000 --> mean negative log-likelihood, scaled to 1000

Zero-count categories store zero numeric placeholders for TOP1 and NLL. They are **not** genuine zero-performance results and must be marked N/A when interpreted.

The 10 strata must cover all **9170** lexical VALIDATION targets, and their 0, 1-9 and 10+ sums must exactly match the immutable V65 buckets.

## GOGIT verification and publication

The complete audit computes **57 distinct numeric metrics**, which are split into **two separate 30-field GOGIT publications** -->

- 3 standard safety flags
- 12 fixed V66 study checks and inventory metrics
- 6 family-level confusion counts
- 6 family-level mean probability-mass shares
- 30 detailed token-frequency metrics

Expected safety flags -->

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V66_BIAS_BLIND_ACCESS=0`

Preflight refuses corpus, checkpoint, V65 numeric inventory, VALIDATION CE, EOS or frequency-band inconsistencies. No raw texts, tokens, individual logits, source IDs or private conversations are published.

## Implementation

- Audit --> `tools/public-audits/phase03_v66_token_prediction_bias_001.py`
- CPU unit tests --> `tests/test_phase03_v66_token_prediction_bias_001.py`
- Single-command runner --> `tools/run_v66_token_prediction_bias_001_job.py`
- GOGIT step --> `PHASE03-SMOLTALK-V66-TOKEN-PREDICTION-BIAS-001`
- Original policy backup manifest --> `tools/backups/GOGIT-PRE-V66-TOKEN-BIAS-20261031.md`

Execute on fhc2 from a clean synchronized checkout -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v66_token_prediction_bias_partitioned_001_job.py
```

The partitioned runner performs frozen-run preflight, original and partition CPU tests, two independent CUDA/BF16 inference passes, two numeric-only GOGIT publications and combined remote-history verification. It resumes at the missing part after validating an existing prior part.

## Interpretation gate

A strong raw-byte argmax bias for gold BPE targets, together with low softmax mass on BPE, would support a **model output-class bias** hypothesis. If BPE receives substantial total probability mass but exact BPE accuracy remains weak, the bottleneck may instead involve confusion among many competing merged tokens. The more detailed frequency strata help distinguish broad frequency effects.

These are diagnostic hypotheses, not established outcomes before execution. V65 has not yet demonstrated whether the model's output distribution is systematically biased toward raw bytes.

**No training, tokenizer alteration, BLIND opening or architecture change is authorized by this report.**

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
