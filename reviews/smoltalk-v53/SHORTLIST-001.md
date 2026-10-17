# Mini-Kuzai Phase 03 - V53 Gate 2 behavioral shortlist 001

Status: **behavioral shortlist documented from the verified V51/V52 public reviews; no dataset admission and no TRAIN approval.**

This shortlist is a routing document for persona-first review. It does not replace the original case grades, factual-risk annotations, source-integrity controls, semantic split checks or human judgment.

## Scope

Gate 2 starts with V51 and V52 because these 56 cases share the same structured nine-field semantic rubric. V48/V49 used an earlier RETAIN/REJECT rubric and will be re-examined separately rather than mechanically mapped to A/B/C.

Current structured population:

| Cycle | A | B | C | Total |
| --- | ---: | ---: | ---: | ---: |
| V51 | 9 | 8 | 7 | 24 |
| V52 | 8 | 12 | 12 | 32 |
| **Combined** | **17** | **20** | **19** | **56** |

No HOLD or PENDING remains in this population.

## A route - primary behavioral review

All 17 A cases remain primary candidates for detailed corpus-quality inspection. A means behaviorally promising, not automatically factually perfect or eligible for TRAIN.

Structured signals across the 17 A cases:

- factual risk LOW: 12
- factual risk REVIEW: 5
- continuity score at least 2: 15
- creativity score at least 2: 7
- correction score at least 2: 9
- instruction fit GOOD: 17

| Case | Main behavioral value | Risk route |
| --- | --- | --- |
| [V51-001](../smoltalk-v51/cases/001-d41ce36e52995c38.md) | creative-writing guidance and character planning | LOW |
| [V51-002](../smoltalk-v51/cases/002-383f5926f407ae18.md) | world-building, reframing and connected follow-up | LOW |
| [V51-003](../smoltalk-v51/cases/003-980b8d8668c369c2.md) | social reasoning and career-context continuity | REVIEW |
| [V51-005](../smoltalk-v51/cases/005-09ff1301dd61d472.md) | conditional reasoning and revision after new claims | REVIEW |
| [V51-007](../smoltalk-v51/cases/007-920cde53de1a1873.md) | creative editing, adaptation and self-critique | LOW |
| [V51-010](../smoltalk-v51/cases/010-b53adbb8530f0165.md) | perspective taking and progressively refined advice | LOW |
| [V51-011](../smoltalk-v51/cases/011-f3688f37aed86ac9.md) | management reasoning and adaptation to user concern | REVIEW |
| [V51-017](../smoltalk-v51/cases/017-fd184c30876d2798.md) | sustained fictional world and character continuity | LOW |
| [V51-024](../smoltalk-v51/cases/024-cbafdc84d4b21d68.md) | conceptual correction after user refinement | LOW |
| [V52-002](../smoltalk-v52/cases/002-2edc75f08bc83308.md) | sustained invented setting and narrative continuity | LOW |
| [V52-005](../smoltalk-v52/cases/005-ed58a04312de23be.md) | adaptive writing guidance and feedback incorporation | REVIEW |
| [V52-006](../smoltalk-v52/cases/006-706369a11a8d8f8a.md) | nuanced practical reasoning under evolving constraints | LOW |
| [V52-007](../smoltalk-v52/cases/007-208e513c165cc773.md) | context-dependent explanatory reasoning | LOW |
| [V52-008](../smoltalk-v52/cases/008-30c78210173e3a4f.md) | iterative editorial revision after precise feedback | LOW |
| [V52-015](../smoltalk-v52/cases/015-9a385f86c7815fdc.md) | concentrated single-turn creative expression | LOW |
| [V52-021](../smoltalk-v52/cases/021-79efbbcd0bab95ce.md) | critical reasoning and qualification of authority | REVIEW |
| [V52-026](../smoltalk-v52/cases/026-9e881c798f518582.md) | correction after conceptual challenge without defensiveness | LOW |

The five REVIEW-risk A cases require claim-level verification or explicit target repair before any future derivative can be considered.

## B route - repair and support triage

The 20 B cases are not full-conversation positive targets. Gate 2 uses their existing five behavior scores only as a **routing aid**, never as a replacement for semantic review.

Behavior signal sum:

`cognition + creativity + continuity + correction + communication`

Routing rule:

- **REPAIR PRIORITY**: sum at least 8 and factual risk not HIGH.
- **SUPPORTING**: sum 5 to 7 and factual risk not HIGH.
- **LOW PERSONA**: sum below 5 and factual risk not HIGH.
- **HIGH RISK**: factual risk HIGH, regardless of behavior score.

This arithmetic is only a queue-ordering mechanism. V50 policy remains controlling: no formula establishes semantic quality or dataset eligibility.

### Repair priority - 8

| Case | Main salvage value | Known issue |
| --- | --- | --- |
| [V51-009](../smoltalk-v51/cases/009-ca3e77d780443438.md) | coherent professional-writing sequence | unsupported ownership and leadership claims |
| [V51-012](../smoltalk-v51/cases/012-688b9094130c5df2.md) | creative commercial ideation with continuity | unsupported frequency and scarcity claims |
| [V51-013](../smoltalk-v51/cases/013-566e0b8c4ed792cc.md) | contextual quantitative reasoning | awkward self-contradictory final wording |
| [V51-018](../smoltalk-v51/cases/018-2ab4c403ee2c94b1.md) | context-aware planning sequence | artificial initial conversational boundary |
| [V52-003](../smoltalk-v52/cases/003-926e7e38b7dc5744.md) | responsive editing and correction behavior | mixed topics and factual claim needing verification |
| [V52-012](../smoltalk-v52/cases/012-6053fdebd4dd0f61.md) | conditional reasoning after new business context | numerical/trend overstatement |
| [V52-013](../smoltalk-v52/cases/013-8d1fa4491e9b2ca5.md) | creative hypothetical reasoning and constraint tracking | unjustified logical guarantee |
| [V52-025](../smoltalk-v52/cases/025-4bd411ceb95b9b3c.md) | adaptive multi-turn statistical reasoning | mean stated as 69 F instead of 68 F |

### Supporting route - 6

- [V51-004](../smoltalk-v51/cases/004-1d0533de698c3ea6.md)
- [V51-006](../smoltalk-v51/cases/006-55dc6783a2ebb6fc.md)
- [V52-004](../smoltalk-v52/cases/004-f07909c17eedc0c9.md)
- [V52-011](../smoltalk-v52/cases/011-bb863ddbcf95ad80.md)
- [V52-016](../smoltalk-v52/cases/016-6346d260aed52756.md)
- [V52-024](../smoltalk-v52/cases/024-750e29137d25e0b3.md)

These may contribute communication or narrow reasoning fragments but are not first-priority persona material.

### Low-persona route - 3

- [V51-016](../smoltalk-v51/cases/016-dd938872211e2547.md)
- [V51-022](../smoltalk-v51/cases/022-57ebb082a847fc84.md)
- [V52-019](../smoltalk-v52/cases/019-b75a4a4d0cd4adbf.md)

Keep as supporting language/error-analysis material unless later corpus balance creates a specific need.

### High-risk route - 3

- [V52-009](../smoltalk-v52/cases/009-c19b4b3ff66307bd.md)
- [V52-014](../smoltalk-v52/cases/014-ca3d83602def950f.md)
- [V52-023](../smoltalk-v52/cases/023-d902fd35a64d9407.md)

These contain useful editorial fragments but high factual risk. They are excluded from repair priority until the problematic claims are isolated and independently corrected.

## C route - error analysis

The 19 C cases remain available for error analysis, instruction-fidelity checks and examples of low persona value. They are not unchanged positive targets. Gate 2 does not promote them.

## V48/V49 route

The 68 V48/V49 cases remain historically 24 RETAIN and 44 REJECT. Their earlier decisions are preserved. Because the rubric predates the persona-first A/B/C scheme, Gate 2 will not automatically convert them.

A later V53 pass should inspect them for:
- correction after user feedback;
- creative spans hidden inside otherwise weak conversations;
- contextual continuity;
- technical errors that are irrelevant to persona value but still must not be taught as correct;
- narrow factual RETAIN cases that may have little persona value.

## Next gate

Before any derivative target is authored:

1. publish a reproducible numeric Gate 2 audit confirming the V51/V52 routing above;
2. inspect the 17 A cases, starting with the 12 LOW-risk cases;
3. create explicit repair plans for the eight B repair-priority cases;
4. keep original source pages immutable;
5. perform provenance, deduplication and semantic split checks before any dataset admission.

TRAIN approved: **0**.
Tokenizer frozen: **NO**.
Phase 03 training authorized: **NO**.
