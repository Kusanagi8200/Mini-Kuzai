# Mini-Kuzai Phase 03 - V74 Frequency-Prior Control 001

Date --> 2026-11-01

Status --> **PROPOSED / NOT STARTED / NO NEW TRAINING / NO BLIND ACCESS**

## Verified motivation

The [V73 verified analysis](MINI-KUZAI-PHASE-03-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.md) reused the frozen V62 checkpoint and 9170 lexical VALIDATION positions. CENTER correctly predicted 2832 tokens across 15 distinct predicted IDs. PC1_ONLY correctly predicted 2455 tokens from only 2 distinct IDs. MINUS_PC1 correctly predicted 1124 tokens across 522 distinct predicted IDs. PC1 accounts for 82.88% of the centered hidden-state variance.

These results were measured by teacher forcing. The principal axes and mean vector were fitted on VALIDATION itself. They are not a measure of independent generalization, a semantic evaluation, or evidence that deleting PC1 improves generation.

## Research question

**How much of PC1_ONLY top-1 correctness can be accounted for by the TRAIN token-frequency prior?**

A collapsed predictor can appear numerically useful by selecting a very common token. V74 should measure that confound rather than declare the dominant direction beneficial or harmful by itself.

## Proposed strictly read-only experiment

| Projection | Definition | Question |
| --- | --- | --- |
| ORIGINAL_FP32 | Unmodified V62 hidden states and tied output matrix | Control from the unchanged model |
| CENTER | Unchanged output matrix on VALIDATION mean-centered states | Replay V73 CENTER |
| PC1_ONLY | Unchanged output matrix on the leading centered principal-axis projection | Replay V73 PC1_ONLY |
| TRAIN_UNIGRAM | One constant most-frequent non-special token determined solely from frozen TRAIN | Context-free frequency-only control |

Use the same 36 frozen VALIDATION conversations and original 9170 lexical positions as V73, with 4876 byte and 4294 merged-BPE gold targets. Reproduce the published V73 aggregate counts before interpreting anything new. Compute TRAIN token frequencies only from the existing frozen authorized TRAIN stream, with deterministic tie resolution. Never choose the most-frequent token using VALIDATION counts.

For each condition report aggregate top-1 accuracy count, number of distinct predicted IDs, dominant predicted share and correct counts separated by byte versus merged-BPE gold targets. Compare also predeclared TRAIN-frequency strata, reporting the population denominator in each. Fix thresholds and the exact numerical metric schema before running the audit, rather than selecting them post hoc. Do not expose token identities, predictions at individual positions, text, activations or eigenvectors.

## Mandatory implementation and stop gates

- Verify immutable [V73 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.json) and [V65 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V65-TOKEN-FREQUENCY-DIAGNOSTIC-001.json)
- Verify stopped V62 cycle-2 checkpoint at 69 optimizer steps and 597982 exposure tokens, unchanged tokenizer and dataset lineage
- Replay all relevant original V73 projection counts exactly, or fail closed
- Do not mutate parameters, optimizer state, checkpoints, tokenizer or controlled datasets
- Do not start training, reopen BLIND, touch private corpora or sample private text
- Register and review exact aggregate metrics, unit tests and a bounded, pinned runner before a V74 GPU audit
- Keep public GOGIT results numeric and allowlisted, within the 30-metric maximum per result, with explicit no-training and no-BLIND gates
- Stop on any provenance mismatch, unreviewed schema, missing frozen source, timeout or nonnumeric output

A valid outcome may support a frequency-prior explanation, but cannot prove an independent causal role for PC1. No intervention or additional training is authorized by this protocol. A V74 implementation, test runner and GOGIT STEP_ID **do not yet exist**.

## Publication boundary

The [V74 START draft](../docs/discussions/steps/V74-start.md) is committed **for review only**. No `START-DEV-FLOW` request, GitHub Discussion, training operation or LinkedIn publication is authorized by this document. An explicit future user command and the worker's committed request file are required before posting START. `FINAL-DEV-FLOW` requires a separate authentic V74 numerical GOGIT report.

See the [DEV-FLOW resumption checkpoint](../docs/DEV-FLOW-REPRISE-2026-11-01.md).

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
