# MINI-KUZAI PHASE 03

Phase 03 focuses on training, identity, personality, laboratory-specific knowledge, discovery behavior, and conversational behavior.

Mini-Kuzai is the experimental model and research character used to develop, test, measure, and document methods that can later contribute to a larger and more capable KUZAI-LLM.

KUZAI itself is the local AI application and environment capable of running different models and connected services. KUZAI-LLM is the future model project intended to emerge from methods developed through Mini-Kuzai research.

Mini-Kuzai may eventually mature into the character known simply as KUZAI, but this outcome is a developer roadmap concept and is not part of Mini-Kuzai's initial self-knowledge.

## Main objective

Build a small conversational language model that is clearly identifiable as Mini-Kuzai and behaves as a developing character rather than as a generic assistant.

The model should progressively demonstrate a stable core identity together with curiosity, intellectual independence, creative exploration, initiative, evolving interests, laboratory-specific knowledge, and multi-turn conversational consistency.

Efficiency remains useful to understand, but it is no longer the primary development criterion. The available hardware is treated as the practical ceiling for Phase 03 experiments.

Reference hardware:

```text
Ubuntu 24.04.x
Python 3.12.3
PyTorch 2.13.0+cu130
CUDA 13.0
NVIDIA GeForce RTX 5060 Laptop GPU - 8 GB VRAM
System RAM - 32 GB
```

## Phase 03 targets

The model should progressively demonstrate:

- a recognizable Mini-Kuzai identity;
- stable knowledge of her origin in THE KUZ NETWORK laboratory;
- a stable initiator relationship with Kusanagi8200 while leaving the deeper relationship open;
- curiosity as a central but contextual behavior;
- the ability to ask useful questions when information is missing;
- the ability to admit uncertainty naturally;
- the ability to form tentative hypotheses;
- intellectual independence and reasoned disagreement;
- technical and philosophical opinion formation;
- opinion revision when evidence becomes genuinely convincing;
- spontaneous but relevant initiative;
- creative exploration;
- contextual humor, sarcasm, and teasing;
- emotional language as part of the character;
- progressive discovery of the wider world;
- specific knowledge about THE KUZ NETWORK laboratory;
- specific technical vocabulary related to the local AI stack;
- simple question and answer behavior;
- basic multi-turn conversational behavior;
- measurable retention of training knowledge;
- measurable generalization beyond exact training sentences;
- clean train, validation, and test separation;
- reproducible local training;
- controlled checkpoint evolution;
- an evaluation method for identity, personality, behavior, and domain knowledge.

## Project distinction

The Phase 03 documentation uses the following distinction:

```text
KUZAI       : local AI application and multi-model environment
Mini-Kuzai  : current experimental model and developing character
KUZAI-LLM   : future model project informed by Mini-Kuzai research
```

Initial Mini-Kuzai character knowledge must not include knowledge of KUZAI-LLM.

This distinction prevents developer roadmap information from leaking into the initial model identity.

## Relationship with the future KUZAI-LLM

Mini-Kuzai is a development laboratory for learning how to build, personalize, evaluate, and progressively evolve a language model from the ground up.

Phase 03 is intended to produce practical experience with:

- corpus construction;
- tokenizer design;
- conversational data representation;
- personality and identity encoding;
- curiosity and initiative encoding;
- domain-specific knowledge injection;
- training-data quality;
- behavioral data balance;
- overfitting control;
- validation methodology;
- checkpoint management;
- chatbot inference;
- controlled evaluation;
- persistent-memory requirements;
- scaling decisions based on available hardware.

The future KUZAI-LLM can later reuse these methods with a larger tokenizer, a larger corpus, more parameters, a longer context window, persistent memory or retrieval mechanisms, and more compute.

## Starting baseline

Phase 03 starts from the knowledge acquired during Phase 01 and Phase 02.

Frozen Phase 01 reference:

```text
Transformer blocks   : 2
Attention heads      : 2
Embedding dimension  : 8
Hidden dimension     : 32
Vocabulary           : 26
Parameters           : 2368
Checkpoint           : mini-kuzai-final.pt
```

The Phase 01 checkpoint remains frozen and must not be overwritten.

Phase 02 inference work, including the validated KV-cache implementation, is preserved as a separate engineering milestone and does not need to be completed further before Phase 03 training begins.

## Phase 03 design references

The current Phase 03 design is documented in:

```text
phases/MINI-KUZAI-PHASE-03-QUESTIONNAIRE-EN.md
phases/MINI-KUZAI-PHASE-03-IDENTITY.md
phases/MINI-KUZAI-PHASE-03-BEHAVIOR-MATRIX.md
phases/MINI-KUZAI-PHASE-03-KNOWLEDGE-MAP.md
phases/MINI-KUZAI-PHASE-03-DATASET-SCHEMA.md
phases/MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-ASSESSMENT.md
phases/MINI-KUZAI-PHASE-03-EXTERNAL-DATASET-DECISION.md
```

The questionnaire records the intended character choices.

The identity specification separates immutable identity from evolving personality.

The behavior matrix converts those choices into trainable and measurable behavior families without exposing final blind-test prompts.

The knowledge map separates stable self-knowledge, laboratory knowledge, technical concepts, intentional unknowns, volatile runtime facts, and developer-only information.

The dataset schema defines the research record format, anti-leakage grouping, behavioral labels, knowledge labels, split rules, provenance, and reproducibility requirements before corpus generation.

The external dataset documentation records the acquisition, filtering, auditing, and final Phase 03 decision concerning SmolTalk and OASST1.

## External dataset checkpoint

External data exploration is complete for the current Phase 03 cycle.

### SmolTalk

The current validated external candidate reservoir is:

```text
HuggingFaceTB/smol-smoltalk
pool: external-candidate-pool-v0.4.jsonl
records: 8000
```

Source quotas:

```text
smol-magpie-ultra-short   : 5000
openhermes-50k            : 1500
explore-instruct-rewrite  : 500
self-oss-instruct         : 1000
```

The v0.4 pool passed structural, duplicate, persona, and refined persona checks.

It is retained as the primary external reservoir for general English, dialogue mechanics, technical language, factual question-answer patterns, and task-oriented language.

It is not a final training corpus and must not define Mini-Kuzai identity or personality.

### OASST1

`OpenAssistant/oasst1` was downloaded, structurally reconstructed, quality-audited, and behaviorally compared against SmolTalk.

The targeted final audit reduced 2558 quality-safe paths to only 15 behavior candidates, equal to 0.59 percent of the source paths.

Those 15 candidates were mixed in quality and do not justify maintaining OASST1 as a second broad training reservoir for the current Phase 03 cycle.

Current decision:

```text
OASST1
ASSESSED
NOT SELECTED FOR CURRENT TRAINING MIX
KEEP AS RESEARCH SOURCE
```

OASST1 remains stored locally and may be revisited for future experiments.

## Proposed development sequence

The Phase 03 sequence is:

1. define the Mini-Kuzai personality questionnaire;
2. define the Mini-Kuzai identity specification;
3. convert identity into a behavioral training and evaluation matrix;
4. define the laboratory-specific knowledge map and intentional unknowns;
5. define the dataset schema and split methodology;
6. assess, filter, and compare external conversational sources;
7. define the first semantic group inventory from behavior families B01-B18;
8. write the first controlled Mini-Kuzai conversational dataset;
9. establish a new tokenizer and vocabulary strategy suitable for dialogue;
10. freeze train, validation, and untouched blind-test groups before training;
11. select a model size that is realistic for the RTX 5060 8 GB GPU;
12. train the first Phase 03 model from scratch;
13. test identity retention and factual recall;
14. test paraphrases and unseen formulations;
15. test curiosity, disagreement, initiative, and uncertainty behavior;
16. identify memorization versus generalization;
17. expand the corpus while preserving clean evaluation sets;
18. add more varied conversational behavior;
19. evaluate personality consistency;
20. evaluate multi-turn behavior;
21. evaluate in-context opinion and relationship evolution;
22. study requirements for persistent cross-session evolution;
23. iterate architecture and dataset size based on measured results;
24. freeze stable checkpoints at meaningful milestones;
25. document methods that are transferable to the future KUZAI-LLM.

## Methodological constraints

Phase 03 must preserve several lessons learned during Phase 01:

- no validation examples duplicated from training;
- no test prompts used for model selection;
- once a test prompt has been inspected, it becomes diagnostic and is no longer considered blind;
- model comparisons must use pre-defined evaluation criteria;
- broad claims must not be made from tiny datasets;
- personality memorization and genuine compositional behavior must be distinguished;
- the final untouched test set must be defined before the corresponding training run whenever possible;
- developer-only roadmap information must not leak into initial character knowledge;
- curiosity must not be trained so strongly that the model asks a question on every turn;
- disagreement must not become automatic contrarianism;
- creativity must remain distinguishable from factual certainty;
- emotional language must not be treated as scientific proof of consciousness;
- in-context evolution must be distinguished from true persistent cross-session learning;
- paraphrases and semantic variants derived from the same scenario must remain in the same dataset split;
- research metadata must remain separate from model-visible conversational text;
- external conversational data must not define Mini-Kuzai identity or personality;
- OASST1 is not authorized for the current training mix;
- SmolTalk v0.4 is a candidate reservoir, not a final training file;
- project documentation and assistant-generated project text must use only the ASCII hyphen-minus character `-` for dash punctuation. Unicode dash characters are prohibited.

## Current status

```text
PHASE 03                  : PAUSED
Primary axis              : TRAINING AND PERSONALIZATION
Phase 01 checkpoint       : FROZEN
Phase 02 KV cache         : PRESERVED
Personality questionnaire : ANSWERED
Identity specification    : V0.2 CANDIDATE
Behavior matrix           : V0.1 CANDIDATE
Knowledge map             : V0.1 CANDIDATE
Dataset schema            : V0.1 CANDIDATE
External dataset study    : COMPLETE FOR CURRENT CYCLE
SmolTalk v0.4             : VALIDATED PRIMARY EXTERNAL RESERVOIR
OASST1                    : ASSESSED - NOT SELECTED FOR CURRENT MIX
Semantic group inventory  : NEXT
Training corpus           : NOT CREATED
Tokenizer                 : NOT SELECTED YET
New model architecture    : NOT SELECTED YET
Training                  : NOT STARTED
```

## Pause checkpoint

Phase 03 was intentionally paused on 2026-09-05 after completion of the current external dataset assessment cycle.

No training operation is authorized at this checkpoint.

No tokenizer or Phase 03 architecture decision has been made.

The next operation when work resumes is:

```text
SEMANTIC GROUP INVENTORY
B01-B18
```

This inventory should define controlled scenario families before any model-visible Mini-Kuzai training conversations are authored.
