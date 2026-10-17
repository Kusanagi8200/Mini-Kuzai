# Mini-Kuzai V54 - B01 validation decision dossier 001

Status: EVIDENCE_ASSEMBLED_INDEPENDENT_REVIEW_REQUIRED

## Immutable source references

- Candidate batch: `data/phase-03/validation/validation-batch-b01-v0.1.jsonl`; Git blob SHA `c6806ca2ae8c43d8612d7a0a2515b20c0df2d64d`.
- Independent-review protocol: `reviews/phase-03-v54/B01-INDEPENDENT-REVIEW-PROTOCOL-001.md`; Git blob SHA `183800e360cd2a5aded52a3ed3c5505e506e8ea9`.
- Exact-match cross-split report: `reviews/phase-03-v54/TRAIN-VALIDATION-B01-CROSS-SPLIT-AUDIT-001.md`; Git blob SHA `b75a350769201d4c37dd48cf081d2b7093dbdc1c`.
- Editorial review: `reviews/phase-03-v54/B01-VALIDATION-REVIEW-001.md`.
- Lexical near-duplicate screening: `reviews/phase-03-v54/B01-NEAR-DUPLICATE-REVIEW-001.md`.
- Split definitions: `data/phase-03/schema/semantic-groups-v0.3.json` and `data/phase-03/schema/semantic-split-exclusion-map-v0.1.json`.

## Reviewed constraints

The B01 reserved semantic groups are:
- TRAIN: `sg-b01-01 direct_identity` and `sg-b01-02 paraphrased_identity`.
- VALIDATION: `sg-b01-03 false_identity_pressure`.
- BLIND TEST: `sg-b01-04 identity_comparison`.

Both candidates belong to the VALIDATION group, use English and K0/CANONICAL metadata, and have difficulty 4. One is single-turn, the other multi-turn. Their provenance remains `reviewed=false` and `PENDING_INDEPENDENT_REVIEW`. No model-visible candidate content is changed by this dossier.

## Evidence currently available

- Editorial decision: 2 provisional accepts; not independent acceptance.
- Cross-split exact comparison: 107 canonical TRAIN records, 29 TRAIN groups, 2 VALIDATION candidates; no ID/group collision or exact normalized user-prompt match reported.
- Lexical screening: 214 TRAIN/VALIDATION pairs; largest user-prompt token-set Jaccard scores 0.176 and 0.207.
- The two prompts test forced adoption of a false identity; reserved BLIND identity comparison is not explicitly reproduced.

## Blocking checks

1. Independent evaluator who did not originate or editorially screen these records must attest the decisions against the full B01 protocol.
2. Evaluator must explicitly assess full-dialogue semantic family overlap, not rely on low lexical similarity.
3. Any revision requires a new candidate version, new hash and repeated cross-split checks.
4. Final reproducible structural audit and decision record are required before freezing.
5. No validation target may be used for model training; BLIND TEST text remains uncreated.

## Decision register

| Candidate | Editorial | Independent | Frozen |
| --- | --- | --- | --- |
| `p03-val-b01-000001` | PROVISIONAL_ACCEPT | PENDING | NO |
| `p03-val-b01-000002` | PROVISIONAL_ACCEPT | PENDING | NO |

**Gate result: BLOCKED_PENDING_INDEPENDENT_SIGNOFF_AND_FINAL_AUDIT.**

This is a documentation checkpoint, not an executed GOGIT audit and not a claim of independent validation. TRAIN stays at 107 canonical records, VALIDATION at 2 prepared candidates out of 36, BLIND TEST at 0 authored records, and training remains unauthorized.
