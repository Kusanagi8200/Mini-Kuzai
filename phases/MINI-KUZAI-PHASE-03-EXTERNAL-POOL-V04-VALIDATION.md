# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.4 VALIDATION

## Status

VALIDATED FOR SEMANTIC COMPOSITION AUDIT

The external candidate pool v0.4 contains 8000 records and preserves the intended source quotas:

- smol-magpie-ultra-short: 5000
- openhermes-50k: 1500
- explore-instruct-rewrite: 500
- self-oss-instruct: 1000

## Build validation

The v0.4 build completed with:

- 8000 selected records
- 0 exact content duplicates
- 0 exact prompt-family duplicates
- 0 generic assistant residuals
- 0 benchmark residuals
- 0 Unicode dash residuals
- 0 strict near-duplicate pairs under the validated conservative threshold

The strict duplicate threshold is:

- weighted Jaccard >= 0.90
- SequenceMatcher >= 0.93

The v0.4 build originally reported 7 persona residual messages. A targeted audit demonstrated that all 7 were false positives caused by overly broad lexical patterns such as `act like`, `portray`, and `play a role` when those expressions were used in ordinary semantic contexts rather than as persona instructions.

Examples of false-positive contexts included:

- `Do I act like nothing is wrong...`
- `How does Dickens portray Nancy...`
- `How does Pascal's Triangle play a role...`
- `How does condensation play a role...`

## Refined persona detector

A context-sensitive detector was introduced and validated against explicit positive and negative controls.

Positive controls: 10/10 detected.

Negative controls: 7/7 rejected correctly.

Full v0.4 scan:

- input records: 8000
- matched persona records: 0
- matched persona user messages: 0

The refined detector therefore resolves the false-positive problem without weakening detection of explicit persona instructions such as:

- Assume the role of...
- Act as...
- Act like you're...
- Pretend you are...
- Respond in character...
- From now on, you are...

## Decision

External candidate pool v0.4 is accepted as the current clean external pool candidate.

It is not yet declared training-ready.

The next required step is semantic composition analysis. The purpose is to verify that the 8000 records are not disproportionately dominated by narrow benchmark-style domains such as arithmetic, algebra, puzzles, coding, rewriting, or other repetitive task families even though exact and near-duplicate checks now pass.

No training is authorized at this stage.
