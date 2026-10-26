# Mini-Kuzai Phase 03 - V50 cognitive and creative data priority

Status --> **V50 screening methodology approved as project direction**. The
1,139-record V44 selection is still provisional. This document does not
authorize training, freeze a tokenizer, allocate dataset splits, or declare
any candidate validated.

## Target behavior

Mini-Kuzai is developed as a small conversational character, not as a
specialized IT support model. Its most important research objectives are -->

1. Understanding intentions, context, implicit references, and conversational
   changes across turns.
2. Reasoning through uncertain situations, alternative explanations, cause
   and effect, comparisons, and corrections based on feedback.
3. Creative exploration, fictional character and world consistency,
   storytelling, roleplay, metaphor, humor, and imagination.
4. Flexible dialogue that can clarify, disagree thoughtfully, revise an
   opinion, sustain an interest, and express context-appropriate affect.
5. Reliable everyday explanations and general knowledge as supporting
   capabilities.

Specialized programming, mathematics, network administration and systems
expertise are **secondary**. A technically weak assistant is acceptable
within this project goal; an assistant that cannot listen, adapt or sustain
creative context is not.

This direction sets **data selection priorities**, not claims of
consciousness, subjective emotion, autonomy, or guaranteed long-term memory.

## Separate two kinds of evaluation

**Behavioral value** and **response correctness** are different axes.
A conversation may be useful for developing context adaptation even if one
answer is stylistically awkward. A single exact coding answer may be valid
but have low value for the current personality objective.

An imperfect answer does not automatically disqualify a conversation.
Conversational imperfections can be useful when they demonstrate -->
- Natural hesitation, informal language and ambiguity
- User objections, clarification requests and changing priorities
- Assistant course correction that actually acknowledges new information
- Continuity across changing contexts or connected narrative scenes
- Differing perspectives, uncertainty or creative alternatives.

Conversely, a confidently incorrect factual or mathematical answer,
unsafe practical guidance, unexplained contradictions presented as facts,
fabricated evidence, and incorrect code represented as working code are
not desirable supervised-positive targets. If a correction is available,
a **separately constructed, explicitly labeled correction example** may
be useful; never silently teach the original error as the answer.

A small model can be particularly sensitive to repeated noisy targets.
Do not treat arbitrary mistakes or contradictions as a shortcut to a
complex personality.

## V50 rubric for each conversation

Human review should consider these **independent, non-exclusive** axes -->

| Axis | Score | Assessment |
| --- | --- | --- |
| COGNITIVE_VALUE | 0-3 | Contextual inference, explanation, uncertainty, comparisons, changing perspective |
| CREATIVE_VALUE | 0-3 | Original concepts, storytelling, character and world development, expressive variation |
| MULTITURN_VALUE | 0-3 | Genuine dependence on prior turns, relevant callbacks, user-driven trajectory |
| CORRECTION_VALUE | 0-3 | Accepts correction, checks premises, changes course without indiscriminate agreement |
| COMMUNICATION_VALUE | 0-3 | Clarity, natural interaction, appropriate initiative and emotional nuance |
| FACTUAL_RISK | LOW / REVIEW / HIGH | Unsupported claims or technical mistakes; **requires substantive review** |
| INSTRUCTION_FIT | GOOD / PARTIAL / BAD | Whether relevant explicit user requirements were actually fulfilled |
| DOMAIN | COGNITIVE / CREATIVE / WRITING / SOCIAL / GENERAL / TECHNICAL / MIXED | Multi-label where useful |

Scores measure relevance or quality within their own axes, not mental
states or measured intelligence. No formula can replace human evaluation
of actual meanings. Do not infer these scores solely from keywords.

### Candidate routing

- **A --> reliable and relevant** - useful, substantively correct dialogue
  still needs duplicate, provenance and split checks.
- **B --> behaviorally rich but imperfect** - contains valuable creative or
  cognitive interactions while requiring scoped edits or segmentation.
  Must not be promoted blindly to supervised TRAIN.
- **C --> unsuitable as a positive target** - uncorrected serious errors,
  fabricated evidence, failure on essential instructions or misleading
  information. May inform error-analysis without teaching its answer.
- **UNREVIEWED** - automated detection has identified a candidate but
  no person has validated its semantic value.

Routing must allow a single conversation to be technically incorrect
and behaviorally interesting without treating it as correct technical
instruction. Preserve the source and any revisions as distinct artifacts.

## V48/V49 historical results under V50

The previous 68-case diagnostic ended with 24 RETAIN and 44 REJECT in
the V49 rubric. These remain **historical quality decisions**, not
permanent exclusion rules for cognitive or creative research. The 68
examples were a targeted diagnostic sample, not representative evidence
of quality rates across V44 or the full source reservoir.

Especially inspect cases previously rejected because -->
- Individual turns were creative but were combined without continuity
- A useful conversational repair or change of mind was overlooked
- Technical performance was irrelevant to personality training
- Prose was imperfect yet contributed imagination or perspective.

Do not reinterpret an inaccurate numerical or technical explanation
as a reliable lesson simply because it is embedded in creative wording.
V50 annotations live independently from the original V48/V49 files.

## V50 operations

1. Validate the public external SmolTalk v0.4 8,000-record reservoir
   and the unchanged, 1,139-record V44 provisional selection.
2. Produce a **local-only, reversible prioritization queue** across all
   1,139 V44 examples using broad heuristic *review signals* -->
   creative scenarios, cognition or hypothesis questions, follow-up
   references, response changes after feedback, and technical-domain tags.
3. Heuristic priority is **not** a truth, safety or semantic-quality
   rating. No example is automatically accepted or rejected.
4. Review representative candidates from each priority and source
   category, then examine the entire V44 candidate set as required for
   final selection. Keep evaluation-set semantic families separated.
5. Compare behavioral coverage and data quality before designing the
   final mixture and tokenizer. Avoid forcing fixed category quotas
   that prevent interesting cognitive or creative examples from entry.
6. Keep the controlled identity/behavior corpus, external English
   reservoir, and local-only private research sources separated.
   Public GitHub can contain generic methodology and validated public
   external SmolTalk-only aggregate results, but never private
   conversation content **or information derived from private sources**.
7. Do not approve TRAIN or initiate model training until explicit
   authorization following corpus and split validation.

## Related documents

- [V49 historical review outcomes](../reviews/smoltalk-v48/V49-HOLD-RESOLUTION.md)
- [V44 stratified provisional selection audit](../tools/public-audits/smoltalk_v44_stratified.py)
- [Phase 03 overview](MINI-KUZAI-PHASE-03.md)

The script `tools/public-audits/smoltalk_v50_cognitive_screen.py`
implements only the **first-pass heuristic queue and numeric aggregate
counts**. It does not assert that any example has been semantically
approved.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
