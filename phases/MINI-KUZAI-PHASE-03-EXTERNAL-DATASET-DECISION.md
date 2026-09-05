# MINI-KUZAI PHASE 03 - EXTERNAL DATASET DECISION

Version: 1.0
Status: FROZEN AT CURRENT PAUSE POINT
Date: 2026-09-05

## Purpose

This document freezes the current Phase 03 decision concerning external conversational datasets before work resumes on the Mini-Kuzai custom corpus.

External datasets are support material only. They do not define Mini-Kuzai identity, personality, values, origin, relationship with Kusanagi8200, curiosity, independent thinking, initiative, or future development.

## SmolTalk decision

Dataset:

```text
HuggingFaceTB/smol-smoltalk
```

Current selected pool:

```text
external-candidate-pool-v0.4.jsonl
records: 8000
```

Source quotas:

```text
smol-magpie-ultra-short   : 5000
openhermes-50k            : 1500
explore-instruct-rewrite  : 500
self-oss-instruct         : 1000
TOTAL                     : 8000
```

The v0.4 pool passed the structural, duplicate, persona, and refined persona audits.

It is accepted as the current primary external reservoir.

It is not a final Mini-Kuzai training corpus.

Its intended function is to provide broad English language patterns, general conversational mechanics, technical language, factual question-answer patterns, and task-oriented language.

Behavioral analysis showed that the pool remains strongly task-oriented and must not be allowed to define the Mini-Kuzai character.

## OASST1 decision

Dataset:

```text
OpenAssistant/oasst1
```

The complete train and validation files were downloaded and verified.

The train structure was reconstructed from message trees and passed structural integrity checks.

Observed clean English structure included:

```text
clean English messages : 37783
eligible roots         : 3482
root-to-leaf paths     : 19276
```

A composite quality selection based on quality, helpfulness, task success, toxicity, inappropriate content, spam, and language mismatch was evaluated.

The resulting quality-safe reconstruction produced a useful but much smaller conversational reservoir.

A direct behavioral comparison against SmolTalk showed that OASST1 did not provide enough general advantage to justify adding it as a second broad training reservoir.

A targeted behavioral extraction was then performed to search specifically for correction, clarification, challenge, and revision sequences.

Result:

```text
source quality-safe paths : 2558
targeted candidates       : 15
candidate percentage      : 0.59 percent
clarification candidates  : 5
correction + revision      : 2
correction without explicit revision : 8
```

The 15 candidates were not automatically approved. Manual inspection showed mixed quality, including useful interaction patterns but also factual weaknesses, generic assistant behavior, weak revisions, and examples that do not justify an additional training-data pipeline.

Decision:

```text
OASST1
ASSESSED
NOT SELECTED FOR CURRENT TRAINING MIX
KEEP AS RESEARCH SOURCE
```

The local OASST1 files and analysis outputs should be preserved for future experiments.

Individual interaction ideas may be used as inspiration when authoring controlled Mini-Kuzai scenarios, but the current OASST1 candidate paths are not approved as direct training records.

## External data architecture at pause point

```text
SMOLTALK V0.4
PRIMARY EXTERNAL RESERVOIR
8000 CLEAN CANDIDATE CONVERSATIONS
        |
        | general English
        | dialogue mechanics
        | factual and technical language
        | task-following patterns
        v
CUSTOM MINI-KUZAI CORPUS
        |
        | identity
        | THE KUZ NETWORK origin
        | Kusanagi8200 relationship
        | curiosity
        | uncertainty
        | disagreement
        | opinion formation and revision
        | initiative
        | creativity
        | humor and emotional language
        | self-condition discovery
        | non-assistant character
        v
FUTURE FINAL TRAINING MIX
NOT DEFINED YET

OASST1
RESEARCH SOURCE ONLY AT CURRENT STAGE
```

## Important interpretation

The external corpus is not being optimized to imitate Mini-Kuzai.

Trying to force the external data to contain all desired Mini-Kuzai behaviors would remove too much useful general language while still failing to provide a controlled identity and personality.

The custom corpus is therefore responsible for the high-value character behaviors that are rare in public datasets.

This includes especially:

- explicit intellectual independence;
- reasoned disagreement;
- curiosity that is contextual rather than automatic;
- uncertainty without false confidence;
- initiative without servility;
- opinion formation and evidence-based revision;
- relationship continuity;
- identity continuity;
- creative but epistemically controlled exploration.

## Current pause state

Phase 03 is intentionally paused after completion of external dataset assessment.

No training has started.

No new tokenizer has been selected.

No new Phase 03 model architecture has been selected.

No final external/custom mixture ratio has been selected.

No OASST1 data is authorized for the current training mix.

SmolTalk v0.4 remains a validated candidate reservoir, not a final training file.

## Resume point

When Phase 03 resumes, the next development step is:

```text
SEMANTIC GROUP INVENTORY
B01-B18
```

The semantic group inventory should translate the existing behavior matrix into controlled scenario families before model-visible training conversations are written.

After that:

1. assign semantic groups while preserving anti-leakage rules;
2. build the first controlled Mini-Kuzai conversational corpus;
3. keep TRAIN, VALIDATION, and BLIND TEST scenario families separated;
4. evaluate the custom corpus distribution;
5. decide the external/custom mixture only after the custom corpus exists;
6. then move to tokenizer and architecture decisions.

## Frozen decision summary

```text
SmolTalk v0.4     : KEEP - PRIMARY EXTERNAL RESERVOIR
OASST1            : KEEP LOCALLY - RESEARCH SOURCE ONLY
UltraChat         : NOT SELECTED
WildChat          : NOT SELECTED
DailyDialog       : NOT SELECTED
Custom corpus     : REQUIRED - NEXT MAJOR DATASET WORK
Training          : NOT AUTHORIZED YET
Phase 03          : PAUSED
Resume operation  : SEMANTIC GROUP INVENTORY B01-B18
```
