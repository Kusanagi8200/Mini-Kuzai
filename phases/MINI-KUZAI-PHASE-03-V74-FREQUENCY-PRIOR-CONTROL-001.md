# Mini-Kuzai Phase 03 - V74 Frequency-Prior Control 001

Date --> 2026-11-01

Status --> **START PUBLISHED / NUMERIC SCHEMA FROZEN FOR REVIEW / GPU AUDIT NOT RUN / NO NEW TRAINING / NO BLIND ACCESS**

## Verified motivation

The [V73 verified analysis](MINI-KUZAI-PHASE-03-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.md) reused the frozen V62 checkpoint and 9170 lexical VALIDATION positions. CENTER correctly predicted 2832 tokens across 15 distinct predicted IDs. PC1_ONLY correctly predicted 2455 tokens from only 2 distinct IDs. MINUS_PC1 correctly predicted 1124 tokens across 522 distinct predicted IDs. PC1 accounts for 82.88% of the centered hidden-state variance.

These results were measured by teacher forcing. The principal axes and mean vector were fitted on VALIDATION itself. They are not a measure of independent generalization, a semantic evaluation, or evidence that deleting PC1 improves generation.

## Research question

**How much of PC1_ONLY top-1 correctness can be accounted for by the TRAIN token-frequency prior?**

A collapsed predictor can appear numerically useful by selecting a very common token. V74 should measure that confound rather than declare the dominant direction beneficial or harmful by itself.

## Frozen strictly read-only experiment

| Projection | Definition | Question |
| --- | --- | --- |
| ORIGINAL_FP32 | Unmodified V62 hidden states and tied output matrix | Control from the unchanged model |
| CENTER | Unchanged output matrix on VALIDATION mean-centered states | Replay V73 CENTER |
| PC1_ONLY | Unchanged output matrix on the leading centered principal-axis projection | Replay V73 PC1_ONLY |
| TRAIN_UNIGRAM | One constant most-frequent non-special token determined solely from frozen TRAIN | Context-free frequency-only control |

Use the same 36 frozen VALIDATION conversations and original 9170 lexical positions as V73, with 4876 byte and 4294 merged-BPE gold targets. Reproduce the published V73 aggregate counts before interpreting anything new. Compute TRAIN token frequencies only from the existing frozen authorized TRAIN stream, with deterministic tie resolution. Never choose the most-frequent token using VALIDATION counts.

For each condition report aggregate top-1 accuracy count, number of distinct predicted IDs, dominant predicted share and correct counts separated by byte versus merged-BPE gold targets. Frequency strata are defined using the frequency of the **gold target token in TRAIN**, with fixed bounds F0=0, F1_9=1..9, F10_99=10..99 and F100P>=100. The TRAIN_UNIGRAM predictor is the most frequent **non-special** TRAIN token; ties resolve to the lowest token ID. The same gold-target strata partition all 9170 VALIDATION lexical positions. No token identities, predictions at individual positions, text, activations or eigenvectors are published.

## Predeclared public numerical schema (STEP 10)

Two independent GOGIT records are used to respect the unchanged **30 integers per report** limit, including three common safety fields (0 each). In total they expose 57 unique numeric keys, 54 V74-specific and three safety gates.

| Report | STEP_ID | Numeric fields |
| --- | --- | --- |
| CORE | \`PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001\` | 30 |
| STRATA | \`PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001\` | 30 |

**Both reports** --> \`SEMANTIC_VALIDATION_COMPLETE=0\`, \`TRAINING_AUTHORIZED=0\`, \`TRAINING_STARTED=0\`.

**CORE** --> \`V74_CORE_PASS\`, \`V74_CORE_BLIND_ACCESS\`, \`V74_CORE_VAL_LEXICAL\`, four \`V74_CORE_F*_COUNT\` population fields and, for each of \`ORIG\`, \`CENTER\`, \`PC1\`, \`UNIGRAM\`, the five integers \`CORRECT\`, \`DISTINCT\`, \`TOP1_SHARE_BP\`, \`BYTE_CORRECT\`, \`MERGE_CORRECT\`.

**STRATA** --> \`V74_STRATA_PASS\`, \`V74_STRATA_BLIND_ACCESS\`, \`V74_STRATA_VAL_LEXICAL\`, \`V74_STRATA_TRAIN_LEXICAL\`, \`V74_STRATA_TRAIN_TYPES\`, four \`V74_STRATA_F*_COUNT\` denominators, sixteen per-mode/per-frequency-bin \`CORRECT\` fields, \`V74_STRATA_PC1_UNIGRAM_AGREE\` and \`V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT\`.

The runner must verify full **30-field V73 replay** against the immutable V73 report before scoring V74 and reproduce these exact controls:

- ORIGINAL --> 2673 correct; 5 predicted IDs; 7255 basis-point top1 dominance
- CENTER --> 2832 correct; 15 predicted IDs; 5788 bp top1 dominance
- PC1_ONLY --> 2455 correct; 2 predicted IDs; 7034 bp top1 dominance
- TRAIN --> 294726 lexical tokens, 891 token types
- VALIDATION --> 36 conversations, 9170 lexical targets, 4876 raw-byte and 4294 merged BPE

Both reports must have identical bin denominators. For each projection, CORE \`CORRECT\` must equal the sum of its four STRATA \`CORRECT\` fields; CORE \`BYTE_CORRECT + MERGE_CORRECT\` must also reconcile. \`PC1_UNIGRAM_AGREE\` counts matching argmax IDs; \`PC1_UNIGRAM_SHARED_CORRECT\` counts positions where both choose the gold token.

## Implementation and reproducibility

- Shared, read-only scientific computation --> [\`tools/v74_frequency_prior.py\`](../tools/v74_frequency_prior.py)
- Pinned public CORE audit --> [\`phase03_v74_frequency_prior_core_001.py\`](../tools/public-audits/phase03_v74_frequency_prior_core_001.py)
- Pinned public STRATA audit --> [\`phase03_v74_frequency_prior_strata_001.py\`](../tools/public-audits/phase03_v74_frequency_prior_strata_001.py)
- CPU regression --> [\`test_phase03_v74_frequency_prior_001.py\`](../tests/test_phase03_v74_frequency_prior_001.py)
- Bounded sequential GPU/GOGIT runner --> [\`run_v74_frequency_prior_001_job.py\`](../tools/run_v74_frequency_prior_001_job.py)

The runner runs CPU regressions once, publishes CORE GOGIT, checks the immutable history, then publishes STRATA GOGIT and reconciles both public reports. It stops at the first failure, never retries an existing different history record, and can resume from a verified CORE if STRATA fails. No publication of a GitHub Discussion comment, FINAL-DEV-FLOW, LinkedIn post, new training or BLIND access is part of this runner.

## Mandatory implementation and stop gates

- Verify immutable [V73 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.json) and [V65 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001.json)
- Verify stopped V62 cycle-2 checkpoint at 69 optimizer steps and 597982 exposure tokens, unchanged tokenizer and dataset lineage
- Replay all relevant original V73 projection counts exactly, or fail closed
- Do not mutate parameters, optimizer state, checkpoints, tokenizer or controlled datasets
- Do not start training, reopen BLIND, touch private corpora or sample private text
- Register and review exact aggregate metrics, unit tests and a bounded, pinned runner before a V74 GPU audit
- Keep public GOGIT results numeric and allowlisted, within the 30-metric maximum per result, with explicit no-training and no-BLIND gates
- Stop on any provenance mismatch, unreviewed schema, missing frozen source, timeout or nonnumeric output

A valid outcome may support a frequency-prior explanation, but cannot prove an independent causal role for PC1. No intervention or additional training is authorized by this protocol. The reviewed V74 scientific implementation, pinned CORE/STRATA audits, regression tests and fail-closed runner are staged on GitHub. They have **not yet passed the fhc2 GPU run**. Only a successful dual GOGIT can close the scientific study.

## Publication boundary

The [V74 START source](../docs/discussions/steps/V74-start.md) was reviewed and explicitly published by `START-DEV-FLOW`. [GitHub Discussion #5](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5), its [START receipt](../automation/dev-flow/receipts/V74-start.json), and the corresponding personal LinkedIn post are verified. **Do not issue another START V74.** `FINAL-DEV-FLOW` remains separately prohibited until the CORE and STRATA GOGIT records are authentic, immutable, jointly reviewed and explicitly approved by the operator.

See the [DEV-FLOW resumption checkpoint](../docs/DEV-FLOW-REPRISE-2026-11-01.md).

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
