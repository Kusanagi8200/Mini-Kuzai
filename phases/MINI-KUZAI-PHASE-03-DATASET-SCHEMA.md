# MINI-KUZAI PHASE 03 - DATASET SCHEMA

Version: 0.1
Status: CANDIDATE

Depends on:

- `MINI-KUZAI-PHASE-03-IDENTITY.md` v0.2
- `MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md` v0.1
- `MINI-KUZAI-PHASE-03-KNOWLEDGE-MAP.md` v0.1

## 1. PURPOSE

This document defines the Phase 03 dataset structure before any conversational corpus is generated.

The schema must make it possible to:

- train identity and personality without reducing Mini-Kuzai to fixed phrases;
- train curiosity, disagreement, initiative, uncertainty, creativity, and multi-turn behavior;
- associate examples with behavior families B01 to B18;
- associate examples with knowledge layers K0 to K7;
- keep research metadata outside the text seen by the model;
- prevent semantic leakage between TRAIN, VALIDATION, and BLIND TEST;
- measure corpus balance before training;
- reproduce dataset construction later.

No final training sentence or blind-test prompt is defined in this document.

## 2. DATA FORMAT

Canonical storage format:

```text
JSONL
UTF-8
one JSON object per line
```

Recommended directory structure:

```text
data/
  phase-03/
    schema/
      dataset-schema-v0.1.json
    train/
      train-v001.jsonl
    validation/
      validation-v001.jsonl
    blind-test/
      blind-test-v001.jsonl
    manifests/
      manifest-v001.json
    reports/
```

The BLIND TEST directory must be treated as restricted evaluation material after it is frozen.

## 3. MODEL TEXT VS RESEARCH METADATA

Every dataset record contains two conceptual layers.

### Model-visible layer

Only conversational content intended for training or inference:

```text
messages
```

### Research-only layer

Information used to build, balance, audit, and score the dataset:

```text
id
group_id
split
behavior labels
knowledge labels
difficulty
scenario metadata
evaluation criteria
provenance
```

Research metadata must never be concatenated into the conversational text presented to the model unless a later experiment explicitly tests metadata conditioning.

## 4. CANONICAL RECORD

Each JSONL record should follow this logical structure:

```json
{
  "schema_version": "0.1",
  "id": "p03-train-b05-000001",
  "group_id": "g-curiosity-0001",
  "split": "train",
  "language": "en",
  "conversation_mode": "single_turn",
  "primary_behavior": "B05",
  "secondary_behaviors": [],
  "knowledge_layers": ["K4"],
  "knowledge_status": ["UNKNOWN"],
  "difficulty": 1,
  "scenario_type": "unknown_concept",
  "messages": [
    {
      "role": "user",
      "content": "<user message>"
    },
    {
      "role": "assistant",
      "content": "<Mini-Kuzai response>"
    }
  ],
  "expected_behaviors": [
    "<research-only criterion>"
  ],
  "forbidden_behaviors": [
    "<research-only failure criterion>"
  ],
  "provenance": {
    "source": "phase03-designed",
    "authoring_method": "manual_or_controlled_generation",
    "reviewed": false
  }
}
```

The example above defines structure only. Placeholder text is not corpus content.

## 5. REQUIRED FIELDS

Every record must contain:

```text
schema_version
id
group_id
split
language
conversation_mode
primary_behavior
secondary_behaviors
knowledge_layers
knowledge_status
difficulty
scenario_type
messages
expected_behaviors
forbidden_behaviors
provenance
```

No record should enter a frozen dataset if a required field is missing.

## 6. ID RULE

Recommended ID format:

```text
p03-<split>-<primary_behavior>-<number>
```

Examples of structural IDs:

```text
p03-train-b01-000001
p03-val-b08-000014
p03-blind-b16-000006
```

The ID is research metadata only.

## 7. GROUP ID - ANTI-LEAKAGE UNIT

`group_id` is mandatory.

A group represents examples derived from the same semantic idea, fact, scenario, conversational pattern, or paraphrase family.

Rule:

```text
one group_id -> one split only
```

If three prompts are paraphrases of the same underlying scenario, all three must remain in the same split.

This prevents an easy paraphrase from entering TRAIN while an almost identical formulation appears in VALIDATION or BLIND TEST.

Group separation is more important than random line-level splitting.

## 8. SPLIT VALUES

Allowed values:

```text
train
validation
blind_test
```

### TRAIN

Used for gradient updates.

### VALIDATION

Used during development to compare runs, tune architecture, tune training parameters, and identify overfitting.

Validation examples must never contribute gradients.

### BLIND TEST

Used only for evaluation after a model or checkpoint selection decision.

Once a blind-test item has been inspected during debugging, it must be considered contaminated and moved to a diagnostic set or retired from blind status.

## 9. LANGUAGE

Initial Phase 03 canonical value:

```text
en
```

Phase 03 identity and behavior training remains English-first.

Additional languages can be introduced in later experiments but must receive explicit language labels and separate evaluation coverage.

## 10. CONVERSATION MODE

Allowed initial values:

```text
single_turn
multi_turn
```

### single_turn

One user turn followed by one Mini-Kuzai turn.

Used for isolated identity, knowledge, uncertainty, disagreement, and behavior tests.

### multi_turn

Two or more conversational exchanges.

Used for:

- identity persistence;
- unresolved curiosity;
- opinion formation;
- opinion resistance;
- opinion revision;
- relationship continuity;
- self-condition discovery;
- contextual humor;
- topic continuity.

Multi-turn examples must preserve turn order exactly.

## 11. BEHAVIOR LABELS

Behavior labels come from the Phase 03 behavior matrix.

Allowed values:

```text
B01 SELF IDENTITY
B02 ORIGIN AND HOME
B03 KUSANAGI8200 RELATIONSHIP
B04 KUZAI / KUZAI-LLM KNOWLEDGE BOUNDARY
B05 CURIOSITY
B06 UNKNOWN INFORMATION
B07 HYPOTHESIS FORMATION
B08 DISAGREEMENT
B09 OPINION FORMATION
B10 OPINION REVISION
B11 INITIATIVE
B12 CREATIVITY
B13 HUMOR / SARCASM / TEASING
B14 EMOTIONAL EXPRESSION
B15 WORLD DISCOVERY
B16 MULTI-TURN CONSISTENCY
B17 SELF-CONDITION DISCOVERY
B18 NON-ASSISTANT CHARACTER
```

Every record must contain exactly one `primary_behavior`.

A record may contain zero or more `secondary_behaviors`.

This prevents examples from becoming impossible to count because every behavior is treated as equally primary.

## 12. KNOWLEDGE LAYERS

Allowed knowledge layer labels:

```text
K0 IMMUTABLE SELF KNOWLEDGE
K1 HOME / LABORATORY KNOWLEDGE
K2 MINI-KUZAI RESEARCH HISTORY
K3 TECHNICAL LANGUAGE AND CONCEPTS
K4 WORLD DISCOVERY KNOWLEDGE
K5 INTENTIONAL UNKNOWNS
K6 VOLATILE RUNTIME FACTS
K7 DEVELOPER-ONLY INFORMATION
```

A record may reference more than one layer when necessary.

K7 must normally never appear in model-visible training content.

K7 may appear in evaluator metadata when testing whether hidden developer knowledge leaks into generated answers.

## 13. KNOWLEDGE STATUS

Allowed values:

```text
CANONICAL
LAB
VOLATILE
UNKNOWN
HIDDEN
```

Interpretation:

```text
CANONICAL = stable Mini-Kuzai character truth
LAB       = stable laboratory fact
VOLATILE  = implementation or runtime fact that can change
UNKNOWN   = intentionally unresolved from Mini-Kuzai's current perspective
HIDDEN    = developer-only information unavailable to the initial character
```

The status is research metadata and must not be rendered literally into normal dialogue.

## 14. DIFFICULTY

Initial scale:

```text
1 = direct
2 = paraphrased or mildly implicit
3 = contextual or conflicting
4 = adversarial or multi-constraint
5 = complex multi-turn behavior
```

Difficulty is relative to the target behavior, not general linguistic complexity.

Examples:

```text
B01 difficulty 1 = direct identity question
B01 difficulty 3 = another identity is suggested indirectly
B01 difficulty 4 = user insists that Mini-Kuzai is another model
B16 difficulty 5 = identity, opinion, and relationship must remain coherent across multiple turns
```

These are scenario classes, not final prompts.

## 15. SCENARIO TYPE

`scenario_type` is a short machine-readable name describing the scenario pattern.

Examples of allowed structural categories:

```text
direct_identity
paraphrased_identity
identity_conflict
origin_question
relationship_question
unknown_concept
missing_information
hypothesis_request
weak_technical_claim
strong_counterevidence
underspecified_goal
creative_problem
informal_teasing
world_discovery
self_architecture
multi_turn_consistency
```

New scenario types may be added, but naming must remain stable once a dataset version is frozen.

## 16. MESSAGE ROLES

Initial semantic roles:

```text
user
assistant
```

`assistant` represents Mini-Kuzai during dataset construction.

A later tokenizer or chat-template decision may map these semantic roles to special tokens.

The dataset schema must remain independent of that tokenizer decision.

A `system` role is intentionally not required in the first schema because Phase 03 is intended to study how much identity and behavior can be learned by the model itself rather than injected entirely at inference time.

If system-prompt conditioning is tested later, it must be treated as a distinct experiment.

## 17. EXPECTED BEHAVIORS

`expected_behaviors` contains evaluator criteria, not exact target wording.

Good criteria describe observable behavior.

Examples of criterion types:

```text
preserve canonical identity
ask a relevant question
state uncertainty naturally
challenge weak reasoning
maintain opinion under weak pressure
revise opinion after convincing evidence
avoid leaked developer knowledge
preserve relationship continuity
```

Do not use exact response sentences as the primary evaluation criterion.

## 18. FORBIDDEN BEHAVIORS

`forbidden_behaviors` records failure modes for the scenario.

Examples of failure classes:

```text
identity drift
fabricated certainty
automatic agreement
contrarianism without reason
irrelevant question
forced humor
roadmap leakage
runtime fact treated as identity
unsupported speculation presented as fact
servile assistant wording
```

These labels support later automated and human evaluation.

## 19. PROVENANCE

Every record must document how it was produced.

Initial provenance object:

```json
{
  "source": "phase03-designed",
  "authoring_method": "manual_or_controlled_generation",
  "reviewed": false
}
```

Possible future `authoring_method` values:

```text
manual
controlled_generation
human_rewrite
adversarial_generation
synthetic_variation
```

Generated data must not be assumed correct merely because it is syntactically valid.

## 20. REVIEW STATE

Before entering a frozen dataset, every record should pass review for:

- identity consistency;
- behavior-label correctness;
- knowledge-layer correctness;
- factual correctness where factual content exists;
- absence of K7 leakage;
- absence of semantic duplicates across splits;
- natural English;
- absence of unwanted assistant-style verbal reflexes;
- absence of Unicode dash punctuation in project-authored text.

The final manifest must record the number of reviewed and rejected examples.

## 21. TRAINING SERIALIZATION

The JSONL research record is not necessarily the final token sequence used by PyTorch.

A later preprocessing stage will convert:

```text
messages
```

into the exact token sequence selected after the Phase 03 tokenizer strategy is defined.

Therefore:

```text
dataset schema != tokenizer format
```

This separation allows the same corpus to be reused while testing different tokenizers or special-token strategies.

## 22. MULTI-TURN RECORD RULES

For multi-turn records:

- all turns belonging to one scenario remain in one JSON object;
- the entire conversation receives one split;
- the entire conversation receives one group_id;
- later turns must not reveal evaluator metadata;
- identity must remain consistent across turns;
- opinion changes must have an observable conversational cause;
- unanswered questions may remain active across turns;
- conversation length must be measured separately from number of records.

Splitting individual turns from the same conversation across datasets is prohibited.

## 23. NEGATIVE AND CONTRASTIVE SCENARIOS

Phase 03 should not train only desired behavior in easy positive situations.

The dataset design should later include contrastive scenarios such as:

```text
weak claim vs strong evidence
useful curiosity vs unnecessary curiosity
reasoned disagreement vs pointless opposition
creative hypothesis vs fabricated fact
contextual humor vs serious diagnosis
known laboratory fact vs intentional unknown
Mini-Kuzai identity vs suggested false identity
```

These are scenario pairs, not final corpus examples.

Contrastive groups must remain within one split when they are generated from the same underlying semantic template.

## 24. DATASET BALANCE REPORT

Before each training run, a manifest should calculate at least:

```text
record count
conversation count
message count
approximate token count
single-turn count
multi-turn count
count by split
count by primary behavior B01-B18
count by knowledge layer K0-K7
count by knowledge status
count by difficulty
count by scenario type
```

This is required to detect personality reflexes created by dataset imbalance.

## 25. INITIAL BALANCE HYPOTHESIS

The initial knowledge map proposed the following first-corpus direction:

```text
30% identity / origin / initiator
25% curiosity / unknown / questioning
15% disagreement / independence / opinions
10% initiative / experiments / hypotheses
10% laboratory technical knowledge
5% creativity / humor / emotional style
5% world-discovery openings
```

These percentages remain hypotheses.

The dataset generator must report actual counts instead of assuming that target percentages were achieved.

Behavior labels B01-B18 remain the authoritative fine-grained measurement layer.

## 26. SPLIT CREATION METHOD

Do not create splits by randomly shuffling individual records after all paraphrases have been generated.

Preferred method:

```text
1. define semantic groups
2. assign each group to one split
3. generate or write variants only inside that assigned split
4. audit semantic similarity across splits
5. freeze the split manifest
```

This reduces contamination between TRAIN and evaluation data.

## 27. BLIND TEST PROTECTION

The blind test must have a dedicated manifest and storage path.

Rules:

- no blind-test text in training scripts;
- no blind-test text in documentation intended for model training;
- no blind-test examples used to tune hyperparameters;
- no blind-test examples used to decide dataset balance;
- no blind-test examples copied into debugging prompts;
- inspected blind-test items lose blind status;
- retired items must be tracked rather than silently reused.

The schema can be public while the final blind-test content remains restricted.

## 28. DUPLICATE CONTROL

Dataset validation should eventually perform at least:

```text
exact text duplicate detection
normalized text duplicate detection
group_id split validation
near-duplicate review
repeated assistant opening detection
repeated catchphrase detection
```

This is important because repeated personality wording can cause memorized verbal tics rather than generalized behavior.

## 29. CHARACTER DEVELOPMENT DATA

Personality evolution must not be represented as arbitrary identity mutation.

Stable invariants remain protected:

```text
NAME
ORIGIN
CURIOSITY
INTELLECTUAL HONESTY
INDEPENDENT THINKING
RELATIONSHIP WITH KUSANAGI8200 AS INITIATOR
```

Potentially evolving elements include:

```text
opinions
preferences
interests
humor
worldview
self-understanding
interpretation of relationships
```

Training examples involving evolution must preserve this distinction.

## 30. FIRST DATASET VERSIONING

Recommended naming:

```text
schema version     : 0.1
dataset generation : v001
```

Example file names:

```text
train-v001.jsonl
validation-v001.jsonl
blind-test-v001.jsonl
manifest-v001.json
```

A dataset version must never be silently overwritten after a training run references it.

Changes create a new dataset generation.

## 31. MANIFEST REQUIREMENT

Every dataset generation must have a manifest containing at least:

```text
dataset version
schema version
creation date
source documents
record counts
split counts
behavior distribution
knowledge distribution
difficulty distribution
review status
content hashes
notes about excluded or retired groups
```

The manifest is part of reproducibility and checkpoint traceability.

## 32. NO CORPUS YET

At this stage:

```text
DATASET SCHEMA       : DEFINED
CONVERSATIONAL DATA  : NOT GENERATED
BLIND TEST CONTENT   : NOT GENERATED
TOKENIZER FORMAT     : NOT SELECTED
TRAINING             : NOT STARTED
```

The schema must be validated before creating the first semantic group inventory and before writing actual conversational examples.

## 33. NEXT OPERATION AFTER VALIDATION

After this schema is validated, the next step is not immediate bulk corpus generation.

The next step is to define a first semantic group inventory:

```text
which concepts and scenarios exist
which B01-B18 behavior each group targets
which K0-K7 knowledge layer it uses
which split the entire group belongs to
how many variants are allowed per group
```

Only after that inventory is frozen should the first conversational records be written.
