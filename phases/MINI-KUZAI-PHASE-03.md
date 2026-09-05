# MINI-KUZAI PHASE 03

Phase 03 focuses on training, identity, personality, laboratory-specific knowledge, and chatbot behavior.

Mini-Kuzai is the experimental embryo of the future KUZAI model. It is not intended to become a highly optimized production model. Its purpose is to develop, test, measure, and document the methods that can later be reused when building a larger and more capable KUZAI model.

## Main objective

Build a small chatbot that is clearly identifiable as Mini-Kuzai and that can demonstrate specific knowledge, vocabulary, behavior, and identity related to the KUZAI laboratory.

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
- consistent answers to identity questions;
- a controlled conversational style;
- specific knowledge about the KUZAI laboratory;
- specific technical vocabulary related to the local AI stack;
- simple question and answer behavior;
- basic multi-turn conversational behavior;
- measurable retention of training knowledge;
- measurable generalization beyond exact training sentences;
- clean train, validation, and test separation;
- reproducible local training;
- controlled checkpoint evolution;
- an evaluation method for personality and domain knowledge.

## Relationship with the future KUZAI model

Mini-Kuzai is a development laboratory for learning how to build and personalize a model from the ground up.

Phase 03 is intended to produce practical experience with:

- corpus construction;
- tokenizer design;
- conversational data representation;
- personality and identity encoding;
- domain-specific knowledge injection;
- training-data quality;
- overfitting control;
- validation methodology;
- checkpoint management;
- chatbot inference;
- controlled evaluation;
- scaling decisions based on available hardware.

The future KUZAI model can later reuse these methods with a larger tokenizer, a larger corpus, more parameters, a longer context window, and more compute.

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
Checkpoint            : mini-kuzai-final.pt
```

The Phase 01 checkpoint remains frozen and must not be overwritten.

Phase 02 inference work, including the validated KV-cache implementation, is preserved as a separate engineering milestone and does not need to be completed further before Phase 03 training begins.

## Proposed development sequence

The Phase 03 sequence is intentionally training-first:

1. define the Mini-Kuzai identity specification;
2. define what laboratory-specific knowledge the model must demonstrate;
3. design a first conversational corpus;
4. establish a new tokenizer and vocabulary strategy suitable for dialogue;
5. define training, validation, and untouched test sets before training;
6. select a model size that is realistic for the RTX 5060 8 GB GPU;
7. train the first Phase 03 model from scratch;
8. test identity retention and factual recall;
9. test paraphrases and unseen formulations;
10. identify memorization versus generalization;
11. expand the corpus while preserving clean evaluation sets;
12. add more varied conversational behavior;
13. evaluate personality consistency;
14. evaluate multi-turn behavior;
15. iterate architecture and dataset size based on measured results;
16. freeze stable checkpoints at meaningful milestones;
17. document methods that are transferable to the future KUZAI model.

## Methodological constraints

Phase 03 must preserve several lessons learned during Phase 01:

- no validation examples duplicated from training;
- no test prompts used for model selection;
- once a test prompt has been inspected, it becomes diagnostic and is no longer considered blind;
- model comparisons must use pre-defined evaluation criteria;
- broad claims must not be made from tiny datasets;
- personality memorization and genuine compositional behavior must be distinguished;
- the final untouched test set must be defined before the corresponding training run whenever possible.

## Current status

```text
PHASE 03                  : STARTED
Primary axis              : TRAINING AND PERSONALIZATION
Phase 01 checkpoint       : FROZEN
Phase 02 KV cache         : PRESERVED
Training corpus           : TO DESIGN
Identity specification    : NEXT
New model architecture    : NOT SELECTED YET
Training                  : NOT STARTED
```

The next operation is to define the Mini-Kuzai identity specification before generating any new training corpus.
