# MINI-KUZAI PHASE 03 - PRIVATE CORPUS PIPELINE

Status: ACTIVE DESIGN - LOCAL DATA ONLY

## Purpose

Phase 03 can use private local conversation corpora as an additional research source.

The public repository documents only the generic processing methodology. Source conversations, extracted text, derived candidate queues, source-specific statistics, review outputs, and any other information originating from private discussions remain outside Git.

## ChatGPT export as a private source

A personal ChatGPT export can be used locally as a source for building a conversation-specific dataset for Mini-Kuzai.

Its purpose is not to copy the export directly into training. Its value is to provide real conversational structures that are difficult to reproduce with synthetic prompts alone, including:

- multi-turn troubleshooting;
- failed hypotheses followed by correction;
- user feedback after commands or configuration changes;
- explanation and clarification;
- comparison and reasoning;
- planning and decision support;
- conversational continuity;
- technical dialogue;
- general non-technical dialogue;
- writing, reformulation, and language examples.

The export is treated as a private raw reservoir. It must be reconstructed, segmented, reviewed, fact-checked, deduplicated, adapted to the Phase 03 language policy, and mapped to learning objectives before any training integration.

The objective is therefore:

```text
CHATGPT EXPORT
        |
        v
PRIVATE LOCAL CONVERSATION RESERVOIR
        |
        v
CURATION + FACT CHECK + SEMANTIC MAPPING
        |
        v
MINI-KUZAI-SPECIFIC CONVERSATION DATA
```

The resulting dataset is intended to complement, not replace:

- the controlled Mini-Kuzai identity and behavior corpus;
- the general external English reservoir;
- the manually protected VALIDATION and BLIND TEST design.

No source conversation or source-derived information from the ChatGPT export is published in the public repository.

## Public / local boundary

Public repository:

- corpus-processing methodology;
- generic schemas;
- generic curation rules;
- project-level training decisions;
- reusable code that contains no private source material;
- reproducibility rules that do not reveal private corpus content or derived source statistics.

Local workspace only:

- raw private conversations;
- extracted USER / ASSISTANT text;
- conversation titles;
- source metadata;
- logs, commands, addresses, credentials, identifiers, and environment-specific values from source conversations;
- derived episode files;
- source-specific classifications and statistics;
- candidate queues;
- factual-review notes;
- rejected examples;
- curated training candidates before explicit dataset integration.

## Processing pipeline

The private-corpus workflow is:

```text
PRIVATE LOCAL SOURCE
        |
        v
CONVERSATION RECONSTRUCTION
        |
        v
TOPIC / EPISODE SEGMENTATION
        |
        v
QUALITY AND RELEVANCE CLASSIFICATION
        |
        v
FAILED-STEP / CORRECTION CURATION
        |
        v
FACTUAL AND TECHNICAL VALIDATION
        |
        v
SEMANTIC MAPPING
        |
        v
DUPLICATE / NEAR-DUPLICATE CONTROL
        |
        v
LANGUAGE NORMALIZATION OR TRANSLATION DECISION
        |
        v
TRAIN / VALIDATION / BLIND ANTI-LEAKAGE CHECK
        |
        v
EXPLICIT HUMAN APPROVAL
        |
        v
FUTURE PHASE 03 DATASET
```

## Conversation reconstruction

Private dialogue exports must be reconstructed as coherent conversation branches before evaluation.

Isolated later turns must not automatically become independent training records because their meaning may depend on earlier context.

## Episode segmentation

One source conversation may contain several unrelated topics.

Before training integration, a long conversation should be divided into coherent semantic episodes when topic changes would otherwise combine unrelated learning signals.

Episode boundaries are research metadata and remain local until a final approved dataset record is created.

## Failed-step curation

Technical troubleshooting conversations may contain incorrect hypotheses or commands that are later rejected by real feedback.

The pipeline must distinguish:

```text
failed proposal
feedback
revised diagnosis
corrective action
verified result
```

A failed intermediate answer must not be converted into a positive target simply because it occurred before a successful resolution.

When useful, the learning example should preserve the reasoning transition while making the failure status explicit.

## Factual validation

A private-source example is not approved solely because the original conversation ended successfully.

Before dataset integration, relevant claims, commands, configuration syntax, version-dependent behavior, and general explanations must be reviewed for correctness.

Volatile facts must either be removed, normalized, or explicitly labeled according to the Phase 03 knowledge policy.

## Semantic mapping

Approved candidates are mapped to Phase 03 learning objectives rather than to their original source application.

Possible learning dimensions include:

- technical diagnosis;
- explanation;
- reasoning and comparison;
- planning and decision support;
- clarification;
- uncertainty handling;
- correction and revision;
- multi-turn consistency;
- concise factual response;
- step-by-step procedure;
- summarization;
- conversational continuity.

Mapping does not imply TRAIN assignment.

## Split protection

The existing Phase 03 semantic split guard remains authoritative.

A private-source scenario, its paraphrases, corrected versions, and closely related variants must remain within one dataset split.

No private-source item may be used to create or tune a BLIND TEST item after the underlying scenario has already been inspected during training-data development.

## Language policy

Private sources may contain languages different from the initial English-first Phase 03 corpus.

Language handling is a separate design decision.

Possible strategies include:

- controlled English adaptation;
- preserving selected multilingual material;
- running a dedicated multilingual experiment.

Translation must preserve meaning and technical correctness rather than mechanically translate syntax or commands.

## Git policy

The public Mini-Kuzai repository must never contain information originating from private conversations.

This prohibition includes source text and derived source information.

Only generic project-development information about the private-corpus pipeline may be committed.

## Training status

The existence of a private candidate corpus does not authorize model training.

Private-source material can enter a Phase 03 dataset only after explicit review, semantic mapping, split validation, and approval.
