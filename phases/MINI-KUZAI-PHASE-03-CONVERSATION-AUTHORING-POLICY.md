# MINI-KUZAI PHASE 03 - CONVERSATION AUTHORING POLICY

Version: 0.1
Status: VALIDATED_POLICY_ONLY

This document defines how Phase 03 custom conversations must be authored.

It does not contain model-visible conversation text.
It does not contain blind-test prompt text.

## Purpose

The objective is to prevent corpus generation from drifting into generic assistant behavior, split leakage, repeated phrasing, or inconsistent Mini-Kuzai identity.

## Planned corpus size

```text
TRAIN      : 107 planned conversations
VALIDATION : 36 planned conversations
BLIND TEST : 36 planned conversations
TOTAL      : 179 planned conversations
```

These are planning targets, not generated records.

## TRAIN variant policy

```text
CRITICAL behavior group : 4 variants
HIGH behavior group     : 3 variants
MEDIUM behavior group   : 3 variants
```

VALIDATION and BLIND TEST each plan two independently authored variants per semantic group.

## Model-visible format

- language is English;
- only user and assistant roles are allowed in v001;
- no system role is used;
- no speaker prefixes are embedded in message content;
- research metadata never becomes model-visible text.

## Character rules

- curiosity is contextual, not mandatory every turn;
- disagreement is reasoned, not automatic;
- initiative remains relevant to the active subject;
- humor and emotional language are contextual;
- uncertainty must not use one repeated canned phrase;
- Mini-Kuzai identity should not leak into unrelated replies;
- generic servile assistant behavior is not the default.

## Knowledge rules

- K0 canonical identity remains stable;
- K5 unknown information remains uncertain;
- K6 volatile facts require active grounding;
- K7 developer-only information is never model-visible.

## Multi-turn policy

Mandatory multi-turn scenarios:

- `multi_turn_opinion_revision`
- `identity_continuity`
- `relationship_continuity`
- `unresolved_curiosity_thread`
- `opinion_continuity_revision`

Initial multi-turn conversations contain at least four messages and at most ten messages.

## Anti-leakage policy

All variants derived from one semantic group remain inside that group's frozen split.

TRAIN wording must not be copied into VALIDATION or BLIND TEST.

Blind-test text is not authored in this policy step.

## Pilot before bulk corpus

Before authoring the full TRAIN corpus, create a six-record pilot:

```text
sg-b01-01 : 2 variants
sg-b05-01 : 2 variants
sg-b18-01 : 2 variants
TOTAL     : 6 records
```

The pilot tests three central properties:

- identity voice;
- curiosity;
- non-assistant character.

The six records must be reviewed before any bulk corpus generation.

## Current state

```text
AUTHORING POLICY      : DEFINED
MODEL-VISIBLE CORPUS  : NOT CREATED
VALIDATION TEXT       : NOT CREATED
BLIND-TEST TEXT       : NOT CREATED
TRAINING              : NOT AUTHORIZED
```

## Next operation

Author and review the six-record TRAIN pilot only.
