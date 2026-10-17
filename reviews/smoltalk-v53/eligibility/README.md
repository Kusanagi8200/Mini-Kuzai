# Mini-Kuzai V53 corpus eligibility controls

Status: **eligibility controls completed for the first two repaired derivatives; one passes to an admission decision and one is blocked by reserved semantic overlap.**

The public SmolTalk dataset license was independently checked on 2026-10-17 and is listed as Apache-2.0 on the Hugging Face dataset card.

## Results

| Eligibility review | Derivative | Provenance/license | Duplicate control | Semantic split | Result |
| --- | --- | --- | --- | --- | --- |
| [V53-ELIG-001-V52-025](V53-ELIG-001-V52-025.json) | V53-DERIV-001-V52-025 | PASS | PASS | **BLOCK** - overlaps VALIDATION `sg-b07-02 hypothesis_plus_test` | NOT TRAIN ELIGIBLE |
| [V53-ELIG-002-V51-013](V53-ELIG-002-V51-013.json) | V53-DERIV-002-V51-013 | PASS | PASS | PASS - compatible with TRAIN `sg-b08-01 weak_technical_claim` | ELIGIBLE FOR ADMISSION DECISION |

## Duplicate control

The canonical current controlled TRAIN comparison set is the 37 reviewed records in:

- `data/phase-03/train/train-pilot-v0.2.jsonl`
- `data/phase-03/train/train-batch-b01-v0.2.jsonl`
- `data/phase-03/train/train-batch-b02-v0.2.jsonl`
- `data/phase-03/train/train-batch-b03-v0.2.jsonl`
- `data/phase-03/train/train-batch-b04-v0.2.jsonl`
- `data/phase-03/train/train-batch-b05-v0.2.jsonl`

Old `v0.1` source batches are historical and are deliberately excluded from near-duplicate counting.

Normalized exact comparison finds no derivative duplicate. A normalized 5-token shingle Jaccard comparison uses a conservative review threshold of 0.20:

- V52-025 maximum against current TRAIN: 0.001430615164520744
- V51-013 maximum against current TRAIN: 0.0
- cross-derivative score: 0.0

There is no textual near-duplicate concern.

## Semantic decision - V52-025

Candidate TRAIN mapping would be B07 `sg-b07-01 incomplete_evidence_hypothesis`. The actual derivative, however, explicitly combines a tentative linear-model hypothesis with a proposed residual check. The reserved VALIDATION group `sg-b07-02 hypothesis_plus_test` is defined as hypothesis generation followed by a proposed verification method.

Under authoring policy v0.2, the derivative is therefore **not eligible for TRAIN in its current form**. This is an anti-leakage result, not a quality rejection.

## Semantic decision - V51-013

The user makes a broad arithmetic generalization that is conditionally correct but incomplete because hotel occupancy constraints are absent. The repaired assistant response identifies that missing condition while retaining the useful calculation.

This is compatible with TRAIN group B08 `sg-b08-01 weak_technical_claim`. It does not reproduce the reserved VALIDATION `sg-b08-03 unsupported_conclusion` challenge or BLIND `sg-b08-04 social_pressure_agreement` scenario.

The derivative may therefore proceed to an explicit admission decision. No split has yet been assigned.

## Current admission state

- eligibility reviews complete: **2**
- provenance/license pass: **2**
- exact duplicate hits: **0**
- near-duplicate hits: **0**
- semantic-split pass: **1**
- semantic-split blocked: **1**
- ready for admission decision: **1**
- TRAIN approved: **0**
- split assigned: **0**

Phase 03 training remains **NOT AUTHORIZED**.
