# MINI-KUZAI PHASE 03 - OASST1 TARGETED BEHAVIOR AUDIT

Status: COMPLETE - MANUAL REVIEW REQUIRED

## Result

The quality-safe OASST1 reconstruction produced 2558 candidate conversation paths.

A targeted behavioral search retained only 15 paths, or 0.59 percent of the source paths.

Signal counts:

- clarification_response: 5
- correction_revision: 2
- correction_without_explicit_revision: 8

There were no duplicate candidate paths.

Additional exclusions during the targeted scan:

- generic assistant path: 130
- persona path: 28

## Interpretation

OASST1 should not be treated as a second general external reservoir for Mini-Kuzai.

Its useful contribution appears to be narrow and behavioral: examples where a user clarifies, corrects, or challenges a prior answer and the following response adapts.

The 15 detected paths are not train-ready. Detection by phrase pattern is only a candidate-generation mechanism. The paths still require manual review for conversational coherence, factual quality, style contamination, task type, and whether the behavior is actually useful for Mini-Kuzai.

## Next operation

Publish the complete 15-path review packet without truncation so every candidate can be reviewed individually before any OASST1 record is accepted.

No OASST1 training subset is frozen yet.
