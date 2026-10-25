# MINI-KUZAI PHASE 03 - V59 TRAINING MIX AND SEGMENTATION

Status: TURN-AWARE SEGMENTATION AUDIT IMPLEMENTED - LOCAL DATA AUDIT PENDING

V59 is the final data-preparation workstream before any model-training
authorization decision.

It has two separate objectives:

1. define the real public training mixture;
2. implement and validate context-safe conversation segmentation for the
   frozen V58 context length of 2048 tokens.

Training remains NOT AUTHORIZED and NOT STARTED.

## Segmentation policy

The V58 report used mathematical contiguous token-window counts only as a
feasibility estimate. V59 replaces that estimate with an explicit
conversation-aware policy.

The V59 segmenter:

- preserves the frozen V57 textual serialization;
- preserves complete USER / MINI-KUZAI pairs;
- cuts only between complete user/assistant pairs;
- greedily packs the maximum number of complete pairs that fit in 2048 tokens;
- preserves message order and text exactly;
- never truncates source text;
- never silently cuts an individual message or pair;
- blocks and reports any individual user/assistant pair that cannot fit in one
  2048-token segment.

A blocked oversized pair requires a separate explicit policy decision. It must
not be repaired automatically by arbitrary token slicing.

## Why this policy

A raw token-window split can create training examples that start in the middle
of an answer, lose the user instruction that motivated the answer, or destroy
the role structure used by the V57 serializer.

Pair-boundary segmentation preserves the smallest complete conversational
unit currently accepted by the Phase 03 schema.

## V59 audit populations

The first V59 segmentation audit measures:

- canonical controlled TRAIN: 107 conversations;
- provisional V44 public SmolTalk population: 1,139 conversations;
- full public SmolTalk reservoir upper bound: 8,000 conversations.

VALIDATION and BLIND TEST are excluded.

Private conversation data are excluded.

## Metrics

For each population the audit records:

- conversation count;
- final segment count;
- conversations requiring more than one segment;
- conversations blocked by an oversized pair;
- oversized pair count;
- maximum complete-pair token length;
- final segment token count;
- segmentation overhead from additional BOS/EOS boundaries.

The controlled TRAIN corpus must remain exactly 107 segments with zero blocked
conversations.

## Training mixture boundary

The segmentation audit does not approve V44 or the full SmolTalk reservoir for
training.

The final training mixture must be decided separately using the existing
persona-first policy:

- prioritize cognitive and creative conversational value;
- prioritize multi-turn continuity, correction and contextual adaptation;
- do not require specialist IT competence;
- never promote a known incorrect answer as a correct supervised target;
- preserve provenance, duplicate controls and split isolation;
- keep VALIDATION and BLIND TEST untouched.

## Decision gate

V59 may recommend a training mixture only after the real segmentation audit is
available.

Architecture readiness does not imply training authorization.

Model training remains NOT AUTHORIZED and NOT STARTED.
