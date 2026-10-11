# MINI-KUZAI PHASE 03

Phase 03 focuses on training, identity, personality, laboratory-specific knowledge, discovery behavior, and conversational behavior.

Mini-Kuzai is the experimental model and research character used to develop, test, measure, and document methods that can later contribute to a larger and more capable KUZAI-LLM.

KUZAI itself is the local AI application and environment capable of running different models and connected services. KUZAI-LLM is the future model project intended to emerge from methods developed through Mini-Kuzai research.

Mini-Kuzai may eventually mature into the character known simply as KUZAI, but this outcome is a developer roadmap concept and is not part of Mini-Kuzai's initial self-knowledge.

## Main objective

Build a small conversational language model that is clearly identifiable as Mini-Kuzai and behaves as a developing character rather than as a generic assistant.

The model should progressively demonstrate a stable core identity together with curiosity, intellectual independence, creative exploration, initiative, evolving interests, laboratory-specific knowledge, and multi-turn conversational consistency.

Efficiency remains useful to understand, but it is no longer the primary development criterion. The available hardware is treated as the practical ceiling for Phase 03 experiments.

 
### V50 priority update: cognition and creativity

The primary learning target is a recognizable conversational persona that
can follow intentions, infer context, explore alternative ideas, create
characters and stories, respond to disagreement, and revise behavior after
feedback. Specialized software, systems and networking correctness is no
longer a primary selection criterion, although seriously wrong answers
must never be used as correct examples without explicit restructuring.

Dataset triage now separates **behavioral relevance** from **factual
reliability**. Imperfect but expressive conversations may be valuable
for contextual or creative learning. Uncorrected technical falsehoods,
fabricated evidence and misleading certainty must not be rewarded as
correct target responses.

[V50 cognitive and creative priorities](MINI-KUZAI-PHASE-03-V50-COGNITIVE-CREATIVE-PRIORITY.md)
describe the revised rubric. V50 is a new screening pass over the 1,139
provisional V44 public SmolTalk candidates; V48/V49 historical quality
decisions remain available and no TRAIN approval follows from a
priority hint.


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
phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md
phases/MINI-KUZAI-PHASE-03-CONVERSATION-AUTHORING-POLICY.md
phases/MINI-KUZAI-PHASE-03-PAUSE-2026-09-27.md
```

The questionnaire records the intended character choices.

The identity specification separates immutable identity from evolving personality.

The behavior matrix converts those choices into trainable and measurable behavior families without exposing final blind-test prompts.

The knowledge map separates stable self-knowledge, laboratory knowledge, technical concepts, intentional unknowns, volatile runtime facts, and developer-only information.

The dataset schema defines the research record format, anti-leakage grouping, behavioral labels, knowledge labels, split rules, provenance, and reproducibility requirements before corpus generation.

The external dataset documentation records the acquisition, filtering, auditing, and final Phase 03 decision concerning SmolTalk and OASST1.

The private corpus pipeline document defines a local-only workflow for reconstructing, segmenting, curating, validating, and mapping private conversational sources without publishing source-derived information.

## Private conversation source role

Phase 03 also uses a personal ChatGPT export locally as a private conversational research source.

The purpose is to derive Mini-Kuzai-specific conversation data from real interaction structures rather than to copy complete exported chats into training.

The local curation process targets reusable patterns such as:

- multi-turn troubleshooting;
- correction after failed hypotheses;
- interpretation of real feedback;
- explanation and clarification;
- reasoning and comparison;
- planning and decision support;
- technical dialogue;
- general conversation;
- language and reformulation patterns.

This source remains separate from the controlled Mini-Kuzai identity and behavior corpus. It also remains separate from the general external English reservoir.

No exported conversation, excerpt, source-specific statistic, candidate queue, or derived review material is committed to the public repository.

Only the generic processing methodology is documented publicly in:

```text
phases/MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md
```

### Private multi-turn curation gate

The private conversational pipeline distinguishes source-faithful dialogue, translated or abstracted user text, and reconstructed assistant targets. User feedback and chronological order must remain traceable, and a proposed correction must never be treated as a verified outcome without supporting evidence.

Topic segmentation is permitted only with preserved context dependencies and semantic lineage locks. Material reviewed during corpus construction is ineligible for untouched VALIDATION or BLIND TEST. Editorial admission to a private candidate pool does not modify official TRAIN files or approve a training run.

The next preparation gate is a local balance audit of dialogue lengths, multi-turn dynamics, behavioral coverage, and potential source dominance across the controlled identity corpus, private candidates, and the external reservoir. Token-level weighting cannot be finalized until a Phase 03 tokenizer is chosen.

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
- private conversational sources remain local-only research material until explicitly approved for dataset integration;
- source conversations and source-derived information must not be committed to the public repository;
- project documentation and assistant-generated project text must use only the ASCII hyphen-minus character `-` for dash punctuation. Unicode dash characters are prohibited.

## External public SmolTalk audit checkpoint - V41 to V46

The V41-V46 workflow uses only the public SmolTalk v0.4 candidate reservoir. This public research is distinct from the local-only private-conversation pipeline.

- V41-V43: context-reference and follow-up heuristics established a writing-heavy initial candidate shortlist; lexical anchors were not interpreted as independently verified conversational continuity.
- V44: a deterministic, stratified **provisional** sample selected 1,139 conversations from the 8,000-record reservoir, with 679 multi-turn and 460 single-turn examples.
- V45: the creative keyword quota selected 69 out of a target of 130. The 61-record shortfall is a feature of the classifier and quota allocation, not proof of a lack of creative dialogue in the source.
- V46: a broader creative-candidate signal matched 339 records across the reservoir, including 47 selected in other V44 categories and 234 not selected by V44. This remains a hypothesis-generating filter, not a factual or pedagogical quality decision.
- V46: a local 68-record review queue was prepared (32 baseline samples, 12 reclassification checks, 24 potential recoveries). No item in this queue was approved for TRAIN by the automatic process.

The public workflow is `tools/gogit_public.py`: each reviewed audit script under `tools/public-audits/` is run locally, publishes allowlisted numeric-only external SmolTalk aggregates, commits and pushes four report files, and can then be inspected from ChatGPT when the user says `gogit`. Full conversation text and local review notes are not published.

**Checkpoint 2026-10-10: PAUSED.** Exact point of resumption is V47, starting with human semantic and factual review of the targeted V46 review dossiers, then assessing the baseline samples. The V44 selection and the official TRAIN, VALIDATION and BLIND datasets remain unchanged. No final tokenizer vocabulary, training mixture, model architecture, or Phase 03 model-training approval exists.

Checkpoint and method documentation:

- [Phase 03 pause - 2026-10-10](MINI-KUZAI-PHASE-03-PAUSE-2026-10-10.md)
- [Public audit reporter](../tools/GOGIT.md)
- [Private corpus methodology](MINI-KUZAI-PHASE-03-PRIVATE-CORPUS-PIPELINE.md)

## V47 integrity gate and V48 human review - resumed 2026-10-11

V47 verified that all 68 queued public SmolTalk conversations match their source records, with no queue-level duplicates and no TRAIN approvals. The queue still contains 68 unreviewed candidates: 12 RELABEL, 24 RESCUE, and 32 BASE.

V48 provided the first-pass GitHub review of 68 public external SmolTalk cases. V49 resolved all 14 HOLD cases, producing 24 RETAIN, 44 REJECT and 0 HOLD. Each case has a GitHub-tracked justification. The local-only terminal review ledger is separate and was not imported.

The numeric-only GitHub progress audit can be run under `gogit` after synchronizing the repository on fhc2. Its counters are generated solely from verified public external case files; RETAIN never implies TRAIN authorization. The 68 diagnostic reviews are insufficient to generalize an acceptance rate to the full 1,139-record provisional V44 sample or the 8,000-record source reservoir.

- [V49 current review results](../reviews/smoltalk-v48/V49-HOLD-RESOLUTION.md)
- [V48 historical first-pass results](../reviews/smoltalk-v48/V48-REVIEW-RESULTS.md)
- [V48 GitHub-native review instructions](../tools/V48-GITHUB-REVIEW.md)
- [V48 local review instructions](../tools/V48-REVIEW.md)
- [V47 public integrity report](../reports/assistant-results/history/PHASE03-SMOLTALK-V47-INTEGRITY-001.json)
- [2026-10-10 historical pause checkpoint](MINI-KUZAI-PHASE-03-PAUSE-2026-10-10.md)

The Phase 03 development task is resumed for external dataset quality review only. TRAIN, VALIDATION, BLIND, tokenizer and model-training authorization gates remain unchanged.

## V50 screening execution

V50 was successfully executed on fhc2 and verified through the numeric-only public `gogit` report. It processed all 1,139 provisional V44 external-public candidates and created a separate local-only queue of 200 HIGH, 431 MEDIUM and 508 LOW heuristic priorities. These groups have **not** been semantically validated. The public report contains only allowlisted numeric counts; source conversations remain in the fhc2 workspace.

No changes to TRAIN, VALIDATION, BLIND, model architecture, tokenizer,
or training authorization follow from V50 preparation.

## V51 controlled public semantic review

The [V51 plan](MINI-KUZAI-PHASE-03-V51-SEMANTIC-REVIEW.md)
and [source-verified GitHub review workflow](../tools/V51-GITHUB-REVIEW.md)
are now published. The new exporter will select 24 fresh public
SmolTalk cases from the verified V50 queue (12 HIGH, 6 MEDIUM, 6 LOW),
with source and category diversification, excluding all previously
published V48/V49 diagnostics. The nine independent review fields
evaluate cognitive value, creativity, continuity, correction,
communication, factual risk, instruction fit and overall A/B/C/HOLD.

The exporter and integrity audit are committed, but actual V51 case
publication, scoring and numeric progress reporting have not yet
been executed on fhc2. V50 priority is an unvalidated screening hint,
not a review verdict. Historic V48/V49 outcomes are preserved.

## Current status

```text
PHASE 03                  : DATA PREPARATION - V51 PUBLIC REVIEW READY
Primary axis              : COGNITIVE AND CREATIVE PERSONA
Phase 01 checkpoint       : FROZEN
Phase 02 KV cache         : PRESERVED
Identity specification    : V0.2 CANDIDATE
Behavior matrix           : V0.1 CANDIDATE
Knowledge map             : V0.1 CANDIDATE
Dataset schema            : V0.1 CANDIDATE
Semantic inventory        : V0.3 - 65 GROUPS
TRAIN semantic groups     : 9 / 29 COMPLETE
Custom TRAIN exchanges    : 35 REVIEWED (31 JSONL RECORDS)
Authoring policy          : V0.2
Semantic split guard      : ACTIVE
VALIDATION records        : 0 / 36 CREATED
BLIND TEST records        : 0 / 36 CREATED
SmolTalk v0.4             : VALIDATED EXTERNAL CANDIDATE RESERVOIR
OASST1                    : ASSESSED - NOT SELECTED FOR CURRENT MIX
Private corpus pipeline   : LOCAL-ONLY - PAUSED
ChatGPT export source     : LOCAL-ONLY RESEARCH SOURCE
Private source material   : NOT COMMITTED
Derived private metrics   : NOT COMMITTED
Tokenizer                 : FINAL VOCABULARY NOT FROZEN
New model architecture    : NOT SELECTED YET
Training                  : NOT STARTED
Training authorized       : NO
```

## Current checkpoint

The controlled custom authoring track remains paused after the B05 TRAIN batch. External public SmolTalk review completed V48 and V49 on 2026-10-11; all 68 diagnostic cases were assessed and the 14 HOLD were resolved. The underlying V44 provisional selection and TRAIN/VALIDATION/BLIND assignments remain unchanged.

B01 through B05 are complete and reviewed:

```text
B01 SELF IDENTITY                  : 8
B02 ORIGIN AND HOME                : 8
B03 KUSANAGI8200 RELATIONSHIP      : 8
B04 KUZAI / Mini-Kuzai BOUNDARY    : 3
B05 CURIOSITY                      : 8
TOTAL REVIEWED CUSTOM TRAIN        : 35
```

The semantic inventory contains 65 groups allocated as 29 TRAIN, 18 VALIDATION, and 18 BLIND TEST groups.

Authoring policy v0.2 and the semantic split exclusion map are active. They were introduced after B03 review detected and corrected semantic overlap between TRAIN examples and reserved evaluation scenarios.

No VALIDATION or BLIND TEST conversation text has been created.

No Phase 03 model training is authorized at this checkpoint.

The tokenizer strategy has been explored, but its final production vocabulary is not frozen. The Phase 03 architecture remains undecided.

The [2026-10-10 pause checkpoint](MINI-KUZAI-PHASE-03-PAUSE-2026-10-10.md) and [B05 checkpoint](MINI-KUZAI-PHASE-03-PAUSE-2026-09-27.md) remain historical records. The current operational checkpoint is [V51 controlled semantic review](MINI-KUZAI-PHASE-03-V51-SEMANTIC-REVIEW.md), following the completed V50 numeric screening. The first 24 public V51 cases are ready for controlled export to GitHub from fhc2, not yet published. No V51 semantic decision has been recorded.

Private-corpus review stays in the local workspace and is paused. Future controlled custom-corpus authoring would resume at B06 UNKNOWN INFORMATION under authoring policy v0.2 and the existing semantic split guard, only after an explicit request.
