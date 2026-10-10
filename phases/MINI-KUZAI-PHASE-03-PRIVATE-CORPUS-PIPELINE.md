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

## Source fidelity and multi-turn reconstruction

A private export may contain branching edits, failed responses, partial transcripts, and system-generated metadata. Reconstruct the actual conversation path in chronological order and preserve stable local source identifiers. Do not fill missing turns by invention.

Keep original user messages, command outputs, and observed feedback separate from any translated, shortened, or abstracted training-target wording. If lengthy logs are summarized, label the summary as an abstraction and retain the original text locally for traceability.

Assistant responses rewritten for teaching quality are counterfactual targets. They are not verbatim source responses, and a successful outcome reported in the original exchange does not prove that a rewritten response would have produced the same outcome.

## Multi-turn evidence and outcome boundaries

Technical episodes should distinguish:

- an initial observation from a hypothesis;
- a proposed procedure from an executed action;
- a failed attempt from a corrective revision;
- a user-reported success from independently verified success;
- an application-level success from downstream effects not tested;
- successful operation in one session from persistence after a restart.

Never infer an unobserved final test, root cause, delivery, reboot result, or downstream effect. Partial outcomes and unresolved causes must remain explicit in both research metadata and model-visible wording where relevant.

Review each reconstructed assistant turn against the next observed user response. The assistant must not anticipate a preference, value, command result, or configuration decision that the user only supplied later.

## Editorial segmentation and candidate gates

Long troubleshooting paths may be divided into coherent shorter episodes. The source message order, parent relationship, context dependencies, and lineage locks must survive segmentation. A final episode is not automatically self-contained: missing setup context requires either a faithful reconstruction or a HOLD decision.

A useful local approval sequence is:

```text
SOURCE-FAITHFUL EPISODE
        |
        v
TECHNICAL FACT CHECK
        |
        v
CHRONOLOGY / USER-FEEDBACK COHERENCE
        |
        v
EDITORIAL REVIEW OF REWRITTEN TARGETS
        |
        v
DUPLICATE / LINEAGE / RESERVED-EVALUATION CONTROL
        |
        v
PRIVATE TRAIN CANDIDATE POOL
        |
        v
EXPLICIT DATASET-INTEGRATION DECISION
        |
        v
FUTURE TRAIN DATASET
```

An assistant-performed editorial review is not a claim that an independent human reviewer has inspected each line. Local admission to a candidate pool is distinct from approval for official TRAIN integration. Neither step authorizes a training run.

Inspected source episodes, their paraphrases, shortened variants, and rewritten targets cannot become untouched VALIDATION or BLIND TEST examples. Group related variants within one semantic split lock even when they were extracted into separate episodes.

## Balance measurement before integration

Counts of records alone do not determine training influence. Audit source composition with reproducible local measures for user versus assistant text, single-turn versus multi-turn conversations, dialogue turns, behavior and topic labels, and concentration of long code or logs.

Record actual text lengths in characters and UTF-8 bytes. Where the Phase 03 tokenizer is not selected, estimates based on characters or words are only proxies: they are not measured tokenizer tokens and must not be presented as exact token totals.

Compare the locally curated material with the controlled identity/behavior corpus and the external English reservoir. Select mixture weights only after a tokenizer choice, token-level length measurement, behavioral balance review, and a separate explicit approval.

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
