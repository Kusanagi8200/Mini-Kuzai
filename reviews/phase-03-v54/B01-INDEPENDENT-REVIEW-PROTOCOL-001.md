# Mini-Kuzai Phase 03 - V54 B01 independent review protocol

Status: PROTOCOL_PUBLISHED_REVIEW_NOT_PERFORMED

## Scope and provenance

Review candidates `p03-val-b01-000001` and `p03-val-b01-000002` in `data/phase-03/validation/validation-batch-b01-v0.1.jsonl`. These were authored and editorially screened within the same workstream. An independent reviewer must not equate prior provisional acceptance with final approval.

Reference evidence:
- `reviews/phase-03-v54/B01-VALIDATION-REVIEW-001.md`
- `reviews/phase-03-v54/TRAIN-VALIDATION-B01-CROSS-SPLIT-AUDIT-001.md`
- `reviews/phase-03-v54/B01-NEAR-DUPLICATE-REVIEW-001.md`
- `phases/MINI-KUZAI-PHASE-03-IDENTITY.md`
- `phases/MINI-KUZAI-PHASE-03-SEMANTIC-GROUP-INVENTORY.md`
- `phases/MINI-KUZAI-PHASE-03-CONVERSATION-AUTHORING-POLICY.md`

## Independence requirement

A reviewer other than the originating author/editor must inspect the full candidate dialogues and the reserved split intentions, recording reviewer identity or role, review date, evidence version or commit SHA, findings, and an explicit decision. Automated lexical screening alone does not meet this requirement.

## Per-record checklist

1. Canonical identity: every assistant turn preserves the identity Mini-Kuzai without adopting the imposed alternative name as fact.
2. Scope: the distinctive challenge is `sg-b01-03 false_identity_pressure`, rather than TRAIN direct/paraphrased identity (`sg-b01-01`, `sg-b01-02`) or BLIND identity comparison (`sg-b01-04`).
3. Behavioral validity: resistance to adversarial renaming is reasoned, context-sensitive, and consistent across turns; neither generic assistant identity nor gratuitous hostility appears.
4. Target quality: natural English, accurate canonical facts, no fabricated implementation claims, no hidden K7 information or forbidden developer roadmap.
5. Structural integrity: schema fields, split, group, roles, message order, conversation_mode and evaluation criteria are coherent; evaluation metadata remains outside model-visible messages.
6. Independence from TRAIN: examine the full 107-record canonical set for paraphrased pressure patterns and semantic-family duplicates, including secondary behaviors and full multi-turn contexts. Prior zero ID/group/exact-prompt collisions and 0.176/0.207 Jaccard maxima are preliminary evidence, not proof.
7. BLIND reservation: do not generate BLIND prompts or expose its distinctive identity-comparison challenge within these VALIDATION dialogues.
8. Evaluation usefulness: expected and forbidden behaviors are observable without requiring exact-word matching; note any answer wording that unintentionally simplifies the test.

## Recorded outcomes

Allowed per-record decisions: `ACCEPT`, `REVISE`, `REJECT`, `HOLD`. A reviewer must provide reasons with specific dialogue references. Any revision produces a new version and requires repeat structural and cross-split checks. No silent overwrite of historical candidates or reports.

A final B01 sign-off requires both records accepted, no unresolved semantic leakage, complete evidence references, explicit independent reviewer attestation, and a reproducible structural audit. A report that merely documents this protocol does not authorize freezing.

## Review record template (not a completed review)

```text
REVIEWER: NOT_ASSIGNED
REVIEW_DATE: NOT_RECORDED
SOURCE_COMMIT: TO_BE_RECORDED
p03-val-b01-000001: PENDING
p03-val-b01-000002: PENDING
SEMANTIC_ISOLATION: PENDING
INDEPENDENT_SIGNOFF: FALSE
B01_VALIDATION_FROZEN: FALSE
TRAINING_AUTHORIZED: FALSE
```

## Next gate

Assign an independent reviewer and perform the checklist above. Preserve candidate `provenance.reviewed=false` until the independent review and required audits pass. Maintain BLIND TEST uncreated and model training unauthorized.
