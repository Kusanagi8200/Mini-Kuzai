# MINI-KUZAI PHASE 03 - PAUSE CHECKPOINT - 2026-09-27

## Objective

Phase 03 is building a controlled conversational training corpus for Mini-Kuzai before any tokenizer, model architecture, or training decision is made.

The target is not a generic assistant. Mini-Kuzai must preserve a stable core identity while progressively learning conversational behaviors such as curiosity, uncertainty, independent reasoning, disagreement, initiative, creativity, relationship continuity, and multi-turn consistency.

The corpus is designed so that TRAIN teaches the intended behavior while VALIDATION and BLIND TEST keep distinct evaluation scenarios outside training.

## Work completed on 2026-09-27

GitHub work completed during this session:

1. resumed Phase 03 with a repository preflight;
2. created the semantic group inventory v0.1;
3. strengthened the inventory and finalized v0.3;
4. assigned all 65 semantic groups to TRAIN, VALIDATION, or BLIND TEST;
5. defined conversation authoring policy v0.1;
6. authored a six-record TRAIN pilot;
7. manually reviewed the pilot and produced pilot v0.2;
8. authored and reviewed B01 SELF IDENTITY;
9. authored and reviewed B02 ORIGIN AND HOME;
10. authored B03 KUSANAGI8200 RELATIONSHIP;
11. detected semantic leakage in two B03 TRAIN examples and replaced them;
12. created authoring policy v0.2 with an explicit semantic split guard;
13. created a metadata-only semantic exclusion map for B01-B18;
14. authored and reviewed B04 KUZAI / Mini-Kuzai knowledge boundary;
15. authored and reviewed B05 CURIOSITY;
16. paused Phase 03 at a clean corpus checkpoint.

## Semantic inventory

Current inventory:

```text
Inventory version          : 0.3
Semantic groups total      : 65
TRAIN groups               : 29
VALIDATION groups          : 18
BLIND TEST groups          : 18
```

Every semantic group belongs to one split only.

The semantic split guard introduced in authoring policy v0.2 requires each future TRAIN batch to be checked against the VALIDATION and BLIND TEST scenarios of the same behavior family before model-visible conversations are authored.

## TRAIN corpus completed

Reviewed custom TRAIN records:

```text
B01 SELF IDENTITY                  : 8
B02 ORIGIN AND HOME                : 8
B03 KUSANAGI8200 RELATIONSHIP      : 8
B04 KUZAI / Mini-Kuzai BOUNDARY    : 3
B05 CURIOSITY                      : 8
--------------------------------------
TOTAL REVIEWED CUSTOM TRAIN        : 35
```

Completed TRAIN semantic groups:

```text
sg-b01-01
sg-b01-02
sg-b02-01
sg-b02-02
sg-b03-01
sg-b03-02
sg-b04-03
sg-b05-01
sg-b05-02
```

This is 9 of 29 TRAIN semantic groups.

The current authoring plan contains 107 custom TRAIN records. Therefore:

```text
Reviewed custom TRAIN records      : 35 / 107
Remaining custom TRAIN records     : 72
```

## B03 anti-leakage correction

B03 exposed an important dataset-design issue.

Two initial TRAIN conversations instantiated evaluation-specific relationship pressure. They were replaced before B03 was frozen.

This produced authoring policy v0.2 and the semantic exclusion map.

The rule is now explicit:

- canonical facts may appear across splits;
- the distinctive evaluation challenge must not be trained;
- keyword filtering alone is insufficient;
- secondary behaviors must also be checked for semantic leakage;
- every generated TRAIN batch requires manual semantic review.

No known semantic leakage remains in the reviewed B01-B05 TRAIN corpus.

## B05 checkpoint

B05 contains two TRAIN scenarios:

```text
sg-b05-01 unknown_concept_curiosity       : 4 reviewed records
sg-b05-02 unresolved_experiment_followup  : 4 reviewed records
```

The six records authored after the pilot were manually reviewed on 2026-09-27.

Result:

```text
Accepted without change  : 6
Corrected                : 0
Replaced                 : 0
Rejected                 : 0
B05 TRAIN complete       : YES
```

Four of the new B05 records are multi-turn experiment follow-ups.

## Evaluation state

No final evaluation conversations have been authored.

```text
VALIDATION records created     : 0 / 36
BLIND TEST records created     : 0 / 36
BLIND TEST text inspected      : NO
```

This preserves the intended evaluation separation.

## External data state

SmolTalk v0.4 remains the validated primary external reservoir:

```text
Records : 8000
Purpose : general English, dialogue mechanics, technical competence
```

It is not the final training mix and is not allowed to define Mini-Kuzai identity or personality.

OASST1 remains assessed but not selected for the current training mix.

No final custom/external mixture ratio has been selected.

## Model and training state

```text
Phase 01 checkpoint       : FROZEN
Phase 02 KV cache         : PRESERVED
Tokenizer                 : NOT SELECTED
Phase 03 architecture     : NOT SELECTED
Phase 03 training         : NOT STARTED
Training authorized       : NO
```

The tiny Phase 01 architecture remains a pedagogical reference and is not automatically the Phase 03 architecture.

## Pause state

Phase 03 is intentionally paused after the B05 TRAIN review.

The repository is left at a clean methodological checkpoint:

- B01-B05 TRAIN are complete and manually reviewed;
- 35 custom TRAIN conversations are reviewed;
- authoring policy v0.2 is active;
- semantic split guard is active;
- VALIDATION text has not been created;
- BLIND TEST text has not been created;
- tokenizer selection has not started;
- architecture selection has not started;
- training is not authorized.

## Next operation on resume

```text
AUTHOR B06 TRAIN BATCH
```

B06 covers UNKNOWN INFORMATION.

Before authoring B06, read its TRAIN, VALIDATION, and BLIND TEST semantic groups from the exclusion map and apply authoring policy v0.2.
