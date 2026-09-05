# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.4 SEMANTIC AUDIT

Version: 0.1
Status: VALIDATED AUDIT - REBALANCING DECISION PENDING

## Scope

This document records the semantic composition audit of the external candidate pool v0.4.

The pool remains an external candidate reservoir. It is not yet approved as a final training mixture.

## Pool size and source composition

Total records: 8000

- smol-magpie-ultra-short: 5000 - 62.50%
- openhermes-50k: 1500 - 18.75%
- self-oss-instruct: 1000 - 12.50%
- explore-instruct-rewrite: 500 - 6.25%

## Primary semantic categories

- general_other: 2617 - 32.71%
- programming: 1740 - 21.75%
- mathematics: 1234 - 15.43%
- writing_editing: 618 - 7.72%
- career_business: 522 - 6.53%
- personal_advice: 296 - 3.70%
- creative_fiction: 267 - 3.34%
- science: 160 - 2.00%
- technology: 160 - 2.00%
- history_society: 115 - 1.44%
- health: 96 - 1.20%
- reasoning_puzzle: 91 - 1.14%
- literature_language: 84 - 1.05%

Programming plus mathematics account for 37.18% of the pool by primary classification.

## Source specialization

self-oss-instruct is almost entirely programming:

- programming: 991 / 1000 - 99.10%

smol-magpie-ultra-short contains substantial academic and technical density:

- mathematics: 1098 / 5000 - 21.96%
- programming: 546 / 5000 - 10.92%

openhermes-50k remains broad but task-oriented:

- general_other: 49.80%
- programming: 13.20%
- mathematics: 8.93%
- writing_editing: 7.73%

explore-instruct-rewrite remains heavily transformation-oriented:

- general_other: 51.00%
- writing_editing: 25.60%

## Dialogue structure

- multi-turn records: 5001 - 62.51%
- first prompt containing a question: 3928 - 49.10%
- imperative first prompts: 1760 - 22.00%
- assistant responses containing a question: 820 - 10.25%
- explicit conversational signal: 677 - 8.46%
- explicit challenge signal: 380 - 4.75%

Median conversation length is 6 messages.

Median combined assistant text per record is 2439.5 characters.

## Prompt-template concentration

The most frequent opening is:

- write a python function: 488 records - 6.10%

Other recurring openings include:

- create a python function
- implement a python function
- design a python function
- develop a python function
- what is the probability
- what is the derivative
- please answer the following

This confirms that exact deduplication and opening caps do not by themselves remove broader task-style concentration.

## Interpretation

The pool is technically much cleaner than v0.1 through v0.3:

- quotas complete
- exact content duplicates removed
- exact prompt-family duplicates removed
- strict near-duplicate audit clean
- broad generic assistant phrases removed
- benchmark residue filtered
- Unicode dash residue removed
- refined persona detector passes control tests and finds no persona contamination

However, technical cleanliness is not equivalent to conversational suitability.

The current v0.4 composition is too heavily weighted toward programming, mathematics, academic tasks, and text transformation to be accepted automatically as Mini-Kuzai's generic conversational base.

The 62.51% multi-turn rate is useful structurally, but the low explicit conversational signal rate shows that multi-turn alone cannot be used as a proxy for natural dialogue.

## Decision

Do not train from v0.4 yet.

Do not discard v0.4.

Treat v0.4 as a validated clean reservoir from which a more behaviorally balanced external subset can be selected.

Before changing source quotas, perform a behavioral-utility audit that separates at least:

- natural conversation
- factual question-answering
- academic problem solving
- programming tasks
- text transformation tasks
- advice and personal discussion
- creative discussion
- multi-turn follow-up behavior
- disagreement or challenge behavior
- assistant follow-up questions
- highly templated task behavior

The next decision must be based on behavioral usefulness for Mini-Kuzai rather than topic labels alone.

## Training status

Training remains blocked.

No architecture, tokenizer, final mixture, or training weight decision is made by this audit.
