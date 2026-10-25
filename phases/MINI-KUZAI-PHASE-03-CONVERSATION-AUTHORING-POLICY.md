# MINI-KUZAI PHASE 03 - CONVERSATION AUTHORING POLICY

Version: 0.6
Status: ACTIVE_POLICY

This document defines how Phase 03 custom conversations must be authored.

Version 0.2 added an explicit semantic split guard after a TRAIN overlap was detected and corrected during B03 review.

Version 0.3 added the project-wide loop-first execution constraint: deterministic gates should be chained into resumable workflows whenever this does not weaken semantic review or authorization controls.

Version 0.4 recorded the completed V54 VALIDATION closure and opened BLIND TEST authoring while keeping model training unauthorized.

Version 0.5 recorded the completed V55 behavior-level BLIND freeze and preserved the B02/B03 correction lineage.

Version 0.6 records successful global BLIND closure through `PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001` while preserving `training_authorized=false`.

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
Canonical TRAIN records      : 107 AUDITED
TRAIN semantic groups        : 29 / 29 AUDITED
TRAIN provenance             : 105 PHASE03-DESIGNED / 2 SMOLTALK

VALIDATION records           : 36 / 36 FROZEN
VALIDATION semantic groups   : 18 / 18 FROZEN
VALIDATION freeze histories  : 18 / 18
VALIDATION semantic passes   : 18 / 18
SEMANTIC VALIDATION COMPLETE : YES

BLIND TEST records           : 36 / 36 FROZEN
BLIND TEST semantic groups   : 18 / 18 FROZEN
BLIND behavior freezes       : 18 / 18
BLIND global closure         : COMPLETE

TOTAL controlled corpus      : 179 RECORDS / 65 GROUPS
TRAINING                     : NOT AUTHORIZED
```

The V53 TRAIN completion audit confirms 107 canonical TRAIN records across all 29 TRAIN groups, including 105 `phase03-designed` records and 2 admitted public SmolTalk derivatives.

The V54 closure gate `PHASE03-SMOLTALK-V54-VALIDATION-CLOSURE-001` confirms that all 36 VALIDATION records across all 18 reserved validation groups are frozen, semantically signed off, and free of exact TRAIN collisions.

V55 then froze all 36 BLIND TEST records across all 18 reserved blind groups. B02 and B03 were explicitly revised and rereviewed before freeze after semantic screening detected excessive proximity to existing same-behavior material. The final V55 behavior-level freeze step is `PHASE03-SMOLTALK-V55-B18-BLIND-FREEZE-001`.

The BLIND master manifest is now `CLOSED` through `PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001`. This status does not authorize training.

See `MINI-KUZAI-PHASE-03-V54-VALIDATION-CLOSURE.md` and `MINI-KUZAI-PHASE-03-V55-BLIND-FREEZE.md`.

## BLIND TEST authoring rules

BLIND authoring is complete, but the future BLIND evaluation must remain untouched by model development.

During BLIND authoring, the workflow required:

1. Read the selected BLIND semantic group.
2. Read the same behavior's TRAIN and VALIDATION groups.
3. Do not paraphrase an existing TRAIN or VALIDATION prompt into BLIND.
4. Preserve the distinctive BLIND challenge rather than recycling another split's challenge.
5. Keep canonical identity facts separate from scenario-specific evaluation pressure.
6. Do not use BLIND examples for tokenizer selection, model selection, training, tuning, or checkpoint choice.
7. If a BLIND prompt is later inspected during model development, it loses untouched-test status and must be reclassified as diagnostic.
8. Any `REVISE`, `REJECT`, or `HOLD` semantic decision stops automated progression until corrected and rereviewed.

## Current post-closure boundary

BLIND TEST authoring, review, behavior-level freeze and global closure are complete.

The controlled corpus now contains 107 TRAIN, 36 VALIDATION and 36 BLIND records across 65 semantic groups.

The BLIND evaluation boundary remains untouched by model development.

No tokenizer finalization, architecture selection, training-mixture finalization or model training is authorized by the V55 closure itself.

Any later training authorization must remain a distinct explicit gate.
