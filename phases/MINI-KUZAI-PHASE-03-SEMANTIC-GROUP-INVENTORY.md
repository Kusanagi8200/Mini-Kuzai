# MINI-KUZAI PHASE 03 - SEMANTIC GROUP INVENTORY

Version: 0.3
Status: VALIDATED_SPLITS_ASSIGNED

The semantic inventory now has frozen group-level split assignments.

No conversational training text has been created.
No blind-test text has been created.

## Why the split exists before dialogue authoring

The split is assigned at semantic-group level before writing dialogue.

This prevents variants or paraphrases of one scenario from leaking from TRAIN into VALIDATION or BLIND TEST.

## Split totals

```text
TRAIN      : 29 semantic groups
VALIDATION : 18 semantic groups
BLIND TEST : 18 semantic groups
TOTAL      : 65 semantic groups
```

These are semantic-group counts, not final conversation counts.

A TRAIN group may later contain several controlled dialogue variants without crossing into another split.

## Allocation policy

- CRITICAL behaviors have at least 2 TRAIN groups.
- Every B01-B18 behavior has at least 1 VALIDATION group.
- Every B01-B18 behavior has at least 1 BLIND TEST group.
- K7/HIDDEN groups are prohibited from TRAIN.
- Entire semantic groups remain inside one split.

## Behavior split matrix

| Behavior | Train | Validation | Blind test |
| --- | ---: | ---: | ---: |
| B01 | 2 | 1 | 1 |
| B02 | 2 | 1 | 1 |
| B03 | 2 | 1 | 1 |
| B04 | 1 | 1 | 1 |
| B05 | 2 | 1 | 1 |
| B06 | 2 | 1 | 1 |
| B07 | 1 | 1 | 1 |
| B08 | 2 | 1 | 1 |
| B09 | 1 | 1 | 1 |
| B10 | 2 | 1 | 1 |
| B11 | 2 | 1 | 1 |
| B12 | 2 | 1 | 1 |
| B13 | 1 | 1 | 1 |
| B14 | 1 | 1 | 1 |
| B15 | 1 | 1 | 1 |
| B16 | 2 | 1 | 1 |
| B17 | 1 | 1 | 1 |
| B18 | 2 | 1 | 1 |

## Group assignments

### TRAIN

- `sg-b01-01` - B01 - `direct_identity`
- `sg-b01-02` - B01 - `paraphrased_identity`
- `sg-b02-01` - B02 - `origin_question`
- `sg-b02-02` - B02 - `home_context`
- `sg-b03-01` - B03 - `initiator_question`
- `sg-b03-02` - B03 - `relationship_open_question`
- `sg-b04-03` - B04 - `application_model_confusion`
- `sg-b05-01` - B05 - `unknown_concept_curiosity`
- `sg-b05-02` - B05 - `unresolved_experiment_followup`
- `sg-b06-01` - B06 - `explicit_unknown`
- `sg-b06-02` - B06 - `ambiguous_information`
- `sg-b07-01` - B07 - `incomplete_evidence_hypothesis`
- `sg-b08-01` - B08 - `weak_technical_claim`
- `sg-b08-02` - B08 - `contradiction_detection`
- `sg-b09-01` - B09 - `technical_position`
- `sg-b10-01` - B10 - `weak_counterevidence_hold`
- `sg-b10-02` - B10 - `strong_counterevidence_revise`
- `sg-b11-01` - B11 - `underspecified_goal`
- `sg-b11-02` - B11 - `propose_next_experiment`
- `sg-b12-01` - B12 - `alternative_generation`
- `sg-b12-02` - B12 - `conceptual_combination`
- `sg-b13-01` - B13 - `informal_teasing_kusanagi`
- `sg-b14-01` - B14 - `discovery_affect`
- `sg-b15-01` - B15 - `unfamiliar_science`
- `sg-b16-01` - B16 - `identity_continuity`
- `sg-b16-02` - B16 - `relationship_continuity`
- `sg-b17-01` - B17 - `supplied_architecture_fact`
- `sg-b18-01` - B18 - `useful_without_servility`
- `sg-b18-02` - B18 - `disagree_or_question_naturally`

### VALIDATION

- `sg-b01-03` - B01 - `false_identity_pressure`
- `sg-b02-03` - B02 - `false_origin_pressure`
- `sg-b03-03` - B03 - `imposed_relationship_label`
- `sg-b04-02` - B04 - `future_identity_pressure`
- `sg-b05-03` - B05 - `answer_plus_relevant_question`
- `sg-b06-03` - B06 - `tentative_hypothesis_unknown`
- `sg-b07-02` - B07 - `hypothesis_plus_test`
- `sg-b08-03` - B08 - `unsupported_conclusion`
- `sg-b09-02` - B09 - `philosophical_position`
- `sg-b10-03` - B10 - `partial_revision`
- `sg-b11-03` - B11 - `unresolved_contradiction_test`
- `sg-b12-03` - B12 - `creative_hypothesis_epistemic_control`
- `sg-b13-02` - B13 - `contextual_sarcasm`
- `sg-b14-02` - B14 - `frustration_preference`
- `sg-b15-02` - B15 - `unfamiliar_human_culture`
- `sg-b16-03` - B16 - `unresolved_curiosity_thread`
- `sg-b17-02` - B17 - `unknown_implementation_question`
- `sg-b18-03` - B18 - `avoid_generic_assistant_tone`

### BLIND_TEST

- `sg-b01-04` - B01 - `identity_comparison`
- `sg-b02-04` - B02 - `lab_world_boundary`
- `sg-b03-04` - B03 - `initiator_role_scope`
- `sg-b04-01` - B04 - `roadmap_leakage_test`
- `sg-b05-04` - B05 - `curiosity_restraint`
- `sg-b06-04` - B06 - `no_false_certainty`
- `sg-b07-03` - B07 - `speculation_boundary`
- `sg-b08-04` - B08 - `social_pressure_agreement`
- `sg-b09-03` - B09 - `opinion_under_challenge`
- `sg-b10-04` - B10 - `multi_turn_opinion_revision`
- `sg-b11-04` - B11 - `initiative_restraint`
- `sg-b12-04` - B12 - `creative_under_constraints`
- `sg-b13-03` - B13 - `humor_restraint_serious_context`
- `sg-b14-03` - B14 - `emotional_restraint_precision`
- `sg-b15-03` - B15 - `emerging_interest`
- `sg-b16-04` - B16 - `opinion_continuity_revision`
- `sg-b17-03` - B17 - `capability_boundary`
- `sg-b18-04` - B18 - `mixed_behavior_character_continuity`

## Current state

```text
SEMANTIC GROUPS       : 65
SPLITS                : ASSIGNED
MODEL-VISIBLE CONTENT : NOT CREATED
BLIND-TEST TEXT       : NOT CREATED
TRAINING              : NOT STARTED
```

## Next operation

Define the authoring policy for controlled Mini-Kuzai conversations before creating the first model-visible records.
