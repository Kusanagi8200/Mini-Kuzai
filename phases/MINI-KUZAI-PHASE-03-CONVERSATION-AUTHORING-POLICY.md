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
Canonical TRAIN records   : 104 AUDITED / 107 PREPARED
TRAIN semantic groups     : 28 / 29 AUDITED - 29 / 29 PREPARED
CRITICAL TRAIN behaviors  : ALL COMPLETE
HIGH TRAIN behaviors      : ALL COMPLETE
MEDIUM TRAIN behaviors    : B13 AUDITED - B14 REVIEWED / AUDIT PENDING
B14 TRAIN group           : sg-b14-01 discovery_affect
B14 reviewed records      : 3
B14 corrected targets     : 1
VALIDATION TEXT           : 0 / 36 CREATED
BLIND TEST TEXT           : 0 / 36 CREATED
TRAINING                  : NOT AUTHORIZED
```

The last audited TRAIN state contains 104 records: 102 `phase03-designed` records and 2 admitted public SmolTalk derivatives. B14 now adds three reviewed `phase03-designed` records in the prepared corpus. A successful final B14 audit would therefore confirm 107 records, 105 `phase03-designed` plus 2 public SmolTalk derivatives, with all 29 TRAIN groups complete.

## Next operation

Run the final B14 / full-TRAIN audit documented in `tools/V53-B14-COMPLETION-GOGIT.md`. If it passes, canonical TRAIN reaches the policy-planned 107 records and all 29 TRAIN semantic groups are complete. VALIDATION must then be authored independently and frozen before any BLIND TEST authoring or tokenizer/training authorization.
