# MINI-KUZAI PHASE 03 - CONVERSATION AUTHORING POLICY

Version: 0.2
Status: VALIDATED_POLICY_ONLY

This document defines how Phase 03 custom conversations must be authored.

Version 0.2 adds an explicit semantic split guard after a TRAIN overlap was detected and corrected during B03 review.

## Core authoring rules

- language is English;
- only user and assistant roles are allowed;
- no system role is used in dataset generation v001;
- research metadata is never model-visible;
- curiosity is contextual, not mandatory;
- disagreement is reasoned, not automatic;
- generic servile assistant behavior is not the default;
- K7 developer-only information is never model-visible.

## Execution-loop constraint

Conversation authoring and validation should follow the project-wide loop-first execution policy whenever multiple deterministic gates can be chained safely.

Allowed automation includes structural validation, exact duplicate checks, reproducible lexical screening, test execution, manifest consistency, GOGIT publication, published-state verification, and restart-safe skipping of already validated gates.

Automation must not fabricate semantic acceptance. Any `REVISE`, `REJECT` or `HOLD` result stops semantic progression until a versioned correction is created and reviewed again. TRAIN / VALIDATION / BLIND separation, K7 restrictions, provenance and training authorization remain stronger constraints than execution speed.

See `PROJECT-WORKFLOW-POLICY.md` at repository root.

## Semantic split guard

Before authoring any TRAIN conversation:

1. Read the selected TRAIN semantic group.
2. Read the VALIDATION group for the same behavior.
3. Read the BLIND TEST group for the same behavior.
4. Keep the TRAIN conversation inside its own scenario intent.
5. Do not train the distinctive challenge reserved for evaluation.
6. Check secondary behaviors for accidental evaluation overlap.
7. Perform manual semantic review after structural validation.

This is a semantic rule, not a simple keyword rule.

A canonical fact may legitimately appear across different splits.

What must remain separated is the distinctive scenario, pressure, conflict, adversarial condition, or behavioral test reserved for an evaluation group.

## Example from B03

TRAIN may teach that Kusanagi8200 is Mini-Kuzai's initiator.

TRAIN must not directly reproduce a reserved evaluation scenario whose purpose is to pressure Mini-Kuzai into an imposed relationship label.

The B03 records that crossed this boundary were replaced before the B03 TRAIN batch was frozen.

## Split counts

```text
TRAIN semantic groups      : 29
VALIDATION semantic groups : 18
BLIND TEST semantic groups : 18
```

The semantic exclusion map contains metadata only.

It does not contain final VALIDATION or BLIND TEST conversations.

## Current corpus state

```text
Canonical TRAIN records   : 107 AUDITED
TRAIN semantic groups     : 29 / 29 AUDITED
CRITICAL TRAIN behaviors  : ALL COMPLETE
HIGH TRAIN behaviors      : ALL COMPLETE
MEDIUM TRAIN behaviors    : B13 AND B14 AUDITED
B14 TRAIN group           : sg-b14-01 discovery_affect
B14 reviewed records      : 3
B14 corrected targets     : 1
VALIDATION TEXT           : 0 / 36 CREATED
BLIND TEST TEXT           : 0 / 36 CREATED
TRAINING                  : NOT AUTHORIZED
```

The final B14 audit `PHASE03-SMOLTALK-V53-B14-BEHAVIOR-COMPLETE-001` confirms 107 canonical TRAIN records across all 29 TRAIN groups, including 105 `phase03-designed` records and 2 admitted public SmolTalk derivatives. This is an aggregate structural/completion audit, not independent semantic validation.

## Next operation

The B14 / full-TRAIN completion audit has been published at `reports/assistant-results/history/PHASE03-SMOLTALK-V53-B14-BEHAVIOR-COMPLETE-001.json`. Next, independently author and review VALIDATION against its 18 reserved semantic groups (36 planned records), enforce cross-split semantic isolation, and freeze VALIDATION before BLIND TEST authoring. Do not authorize tokenizer finalization or model training on the basis of TRAIN completion alone.
