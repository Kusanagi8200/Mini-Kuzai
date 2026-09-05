# MINI-KUZAI PHASE 03 - OASST1 BEHAVIORAL VALUE AUDIT

Version: 0.1
Status: VALIDATED FOR TARGETED USE

## Purpose

Evaluate whether OpenAssistant OASST1 adds behavioral value beyond the validated SmolTalk v0.4 external reservoir.

## Input

OASST1 candidate paths were reconstructed from clean English messages using the `quality_safe` rule.

The resulting local path set contains 2558 paths.

SmolTalk comparison uses the validated v0.4 pool with 8000 conversations.

## Main result

OASST1 does not outperform SmolTalk as a general conversational reservoir.

Measured rates:

- multi-turn: OASST1 33.50%, SmolTalk 62.51%
- six or more messages: OASST1 0.86%, SmolTalk 62.50%
- follow-up signal: OASST1 10.79%, SmolTalk 28.34%
- clarification signal: OASST1 0.23%, SmolTalk 0.55%
- user correction signal: OASST1 0.47%, SmolTalk 1.20%
- assistant revision signal: OASST1 0.70%, SmolTalk 1.07%
- assistant question signal: OASST1 12.08%, SmolTalk 10.25%
- initiative signal: OASST1 2.31%, SmolTalk 4.78%
- opinion signal: OASST1 1.17%, SmolTalk 1.34%
- generic assistant signal: OASST1 5.08%, SmolTalk 0.00%

The existing broad assistant disagreement heuristic is not considered reliable enough for final selection because terms such as `however` can produce false positives. It must not be used as an automatic selection rule.

## Interpretation

OASST1 should not become a second general-purpose external reservoir.

SmolTalk v0.4 remains the principal external source for general English, task language, technical language, and multi-turn mechanics.

OASST1 remains useful because manual inspection found a smaller number of interaction patterns that are valuable for Mini-Kuzai, including:

- user correction followed by an adapted response
- explicit clarification requests
- follow-up after misunderstanding
- revision after new information
- challenge and counterargument sequences
- conversational branching with alternative human prompts

These behaviors are more relevant to B06, B08, B10, B11, B16, and B18 than the overall OASST1 distribution is.

## Decision

OASST1 status:

`VALIDATED FOR TARGETED USE`

Use OASST1 only through a targeted behavioral extraction and review step.

Do not merge all 2558 quality-safe paths into the external training reservoir.

Do not use `rank` alone as a selection criterion.

Do not use the broad assistant disagreement heuristic as a selection criterion.

The next operation is a targeted pair-level audit for correction, clarification, challenge, and revision sequences.

No training mixture is frozen by this document.
