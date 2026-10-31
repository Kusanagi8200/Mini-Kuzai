# Mini-Kuzai Phase 03 - V64 closure and V65 readiness

Date --> 2026-10-31

Status --> **V64 NUMERICAL DIAGNOSTIC COMPLETED / V65 NOT AUTHORIZED TO TRAIN**

## Frozen project baseline

- Model --> 1,184,512 parameters, four Transformer blocks, four heads, d_model 128, context 2048, V58 architecture with V60 corrected initialization
- Tokenizer --> V56 byte-level BPE with whitespace pretokenization, vocabulary 1024 and 765 merges
- V59 mixture --> 272 conversations, 345 TRAIN segments, 295416 unique TRAIN tokens
- Controlled splits --> TRAIN 107 records / 29 groups, VALIDATION 36 / 18, BLIND TEST 36 / 18
- V62 checkpoint --> frozen local cycle-2 checkpoint after 69 optimizer steps and 597982 exposed tokens
- BLIND TEST --> closed throughout V63 and V64
- Historical V62 training authorization --> does not authorize a new V65 training run

## V62 measured learning baseline

| Metric | Verified result |
| --- | --- |
| Initial VALIDATION CE | 6.959721 |
| V62 cycle-2 VALIDATION CE | 4.732514 |
| Relative CE reduction | about 32.0% |
| Terminal EOS top-1 | 14 / 36 |
| Free greedy EOS completions | 0 / 6 |
| Free token trigram repetition | 96.76% |

Source --> [V62 training GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V62-TRAIN-RUN-001.json)

## V63 - decoding and linguistic surface form

The corrected V63 teacher-forced diagnostic found terminal EOS top-1 **14/36**, intermediate EOS top-1 **4/13** and ordinary nonterminal false EOS top-1 **50/9170**. Greedy free generation still showed 0/6 EOS completions and 95.74% repeated token trigrams.

Decoding robustness across eight seeds and six frozen prompts per seed -->

| Metric | Temperature only | Temperature + top-k 40 + top-p 0.9 |
| --- | --- | --- |
| EOS completions | 27/48 = 56.25% | 41/48 = 85.42% |
| Per-seed EOS range | 1 to 5 of 6 | 3 to 6 of 6 |
| Invalid UTF-8 | 32/48 | 0/48 |
| Token trigram repetition | 0.18% | 5.36% |
| Token 8-gram repetition | 0% | 0% |
| Mean generation length | 63.94 tokens | 48.12 tokens |
| Outputs of 16 tokens or fewer | 6/48 | 12/48 |

An initial private human review was suspended after encountering visibly nonsensical text. No completed human-rating GOGIT report exists. Human semantic validation must not be inferred from the decoder metrics.

The automatic V63 screen analyzed 24 private top-k/top-p generations without publishing raw text -->

| Metric | Observed |
| --- | --- |
| EOS | 20/24 |
| Invalid UTF-8 | 0/24 |
| Rule-based suspect outputs | 10/24 |
| Outputs with no regex-recognized words | 2/24 |
| Short nonstandard word fragments | 21.02% |
| Words outside limited 898-word reference lexicon | 41.11% |
| Token trigram repetition | 5.46% |
| Human ratings | 0 |

The word list and rule-based suspicious-output count are **surface-form proxies**, not semantic, grammatical or persona assessments.

Sources -->

- [Corrected EOS preflight](../reports/assistant-results/history/PHASE03-SMOLTALK-V63-DIAGNOSTIC-PREFLIGHT-002.json)
- [Decoding ablation](../reports/assistant-results/history/PHASE03-SMOLTALK-V63-DECODING-ABLATION-001.json)
- [Decoding robustness](../reports/assistant-results/history/PHASE03-SMOLTALK-V63-DECODING-ROBUSTNESS-001.json)
- [Automatic language screen](../reports/assistant-results/history/PHASE03-SMOLTALK-V63-AUTOMATIC-LANGUAGE-SCREEN-001.json)

## V64 - performance incident and completed diagnostic

The original V64 audit 001 passed six unit tests but exceeded GOGIT's 300-second subprocess timeout. A separate 155-second profile confirmed -->
- Frozen TRAIN reconstruction --> 98.270 seconds, including 91.304 seconds loading public streams
- Frozen VALIDATION reconstruction --> 2.765 seconds
- Training boundary-index generation --> in progress when the profiler expired, complete duration unknown
- GPU scoring --> not reached during the bounded trace

V64 audit 002 preserved the original code, removed redundant corpus reconstruction and skipped the boundary index unused by next-token cross-entropy. It successfully published its numeric diagnostics.

| Metric | TRAIN exploratory sample | Frozen VALIDATION |
| --- | --- | --- |
| Segments | 12 | 36 |
| Predicted tokens | 10115 | 9206 |
| Cross-entropy | 4.664 | 4.733 |
| Top-1 next-token accuracy | 33.97% | 29.20% |
| Bytes per non-special token | 1.970 | 1.874 |
| Single-byte token share | 51.23% | 53.17% |
| Single-byte target mean NLL | 3.182 | 3.386 |
| BPE-merged target mean NLL | 6.221 | 6.268 |

Additional controls --> CE gap 0.069 (VALIDATION higher), terminal EOS top-1 14/36, CUDA BF16 PASS, 133 MiB maximum allocated, no BLIND access, no new training.

**Limits** --> The 12 deterministic TRAIN segments are not representative of the 345-segment corpus. A small CE gap does not establish absence of overfitting. The greater merged-token NLL is confounded by token frequency and target distribution, so it does not prove a tokenizer defect. VALIDATION CE reproduced the historical 4.732514 value at three decimal places.

Sources -->

- [Runtime trace GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V64-RUNTIME-TRACE-001.json)
- [Successful V64-002 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002.json)
- [V64-002 implementation record](MINI-KUZAI-PHASE-03-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002.md)

## V65 - proposed diagnostics, not executed

Working title --> **V65 TOKEN LEARNING AND TRAINING READINESS**

1. Measure frozen TRAIN/VALIDATION token-frequency strata and the relative prevalence of raw-byte and BPE-merged units
2. Compare prediction accuracy and negative log-likelihood by token frequency and class, controlling for the frequency imbalance
3. Review the existing checkpoint and evaluation trajectory for learning progress without writing new checkpoints
4. Use consistent and representative sampling for future TRAIN/VALIDATION comparisons before claiming generalization
5. Decide between a newly authorized continuation protocol, tokenizer research or model-capacity change only after the diagnostics

Current decision --> **retain the frozen V56 tokenizer, V58/V60 architecture and V62 checkpoint**. A separate reviewed authorization and freeze are required before any new training. Do not open BLIND and do not equate EOS/UTF-8 validity with linguistic or semantic competence.

The project has established reproducible training and numerical learning, **not** a usable conversational model at this checkpoint.

## GOGIT and privacy status

Latest completed GOGIT step --> `PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002`

V64 latest flags --> `SEMANTIC_VALIDATION_COMPLETE=0`, `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0`, `V64_LANG_BLIND_ACCESS=0`.

The previous V62 training history contains `TRAINING_STARTED=1` for its historical completed training run, not a newly started training session.

Immutable numeric reports remain the source of record. No raw private generation, conversation or source-data payload is published by the V63/V64 diagnostic pipelines.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
