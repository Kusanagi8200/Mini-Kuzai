# Mini-Kuzai Phase 03 - V53 public corpus consolidation plan

Status: **V53 Gate 1 cross-cycle inventory is completed; Gate 2 behavioral shortlist, audit implementation and execution guide are now documented. Gate 2 GOGIT has not yet been executed and no dataset admission has occurred.**
Scope: previously published, external-public SmolTalk v0.4 reviews only.
This plan does not approve TRAIN, change split assignments, freeze a tokenizer, select an architecture or authorize Phase 03 model training.

## Purpose

Consolidate the evidence accumulated in V48/V49, V51 and V52 before widening semantic sampling or authoring corrected training material. Mini-Kuzai is a persona-first experimental model: cognitive adaptation, creative continuity, curiosity, reasoned disagreement, and correction after feedback take priority over specialist IT proficiency. This priority never permits a known false answer to become an unchanged positive supervision target.

Keep three decisions separate:

1. **Behavioral utility** - does the dialogue demonstrate reasoning, creative development, contextual continuity, relevant initiative or genuine correction?
2. **Answer reliability** - is the response factually supportable and compliant with important user constraints?
3. **Dataset eligibility** - are provenance, permitted usage, deduplication, semantic-family isolation, contamination prevention and target-text quality all verified?

An attractive behavioral grade is evidence for further review, not dataset eligibility.

## Verified public review accounting

| Review cycle | Reviewed distinct cases | Historical grades |
| --- | ---: | --- |
| V48/V49 | 68 | 24 RETAIN; 44 REJECT; 0 HOLD |
| V51 | 24 | 9 A; 8 B; 7 C; 0 HOLD |
| V52 | 32 | 8 A; 12 B; 12 C; 0 HOLD; 0 PENDING |
| **Total distinct public cases** | **124** | **Rubrics are not directly additive as acceptance labels** |

Across V51 and V52 alone: **17 A, 20 B, 19 C, 0 HOLD**, for 56 distinct reviewed cases. These are deliberately stratified, AI-assisted qualitative reviews, not independent human validation or representative acceptance-rate measurements.

The eight-case V50 method pilot re-examined previously published V48/V49 examples and is not counted as eight new cases.

The provisional V44 population remains 1,139. Of the 68 V48 cases, only 44 were already in V44; 24 RESCUE cases were outside it. After excluding 44 prior V48 in-V44 cases, 24 V51 cases and 32 V52 cases, the arithmetic residual is **1,039 V44 candidates not covered by these published reviews**. That residual has not been independently re-audited as a new V53 population.

Source reports:
- [V49 historical dispositions](../reviews/smoltalk-v48/V49-HOLD-RESOLUTION.md)
- [V51 qualitative review](../reviews/smoltalk-v51/RESULTS-001.md)
- [V51 GOGIT numeric history](../reports/assistant-results/history/PHASE03-SMOLTALK-V51-PILOT-REVIEW-001.json)
- [V52 qualitative review](../reviews/smoltalk-v52/RESULTS-001.md)
- [V52 final GOGIT audit](../reports/assistant-results/history/PHASE03-SMOLTALK-V52-REVIEW-FINAL-001.json), published by [commit 8a28e956](https://github.com/Kusanagi8200/Mini-Kuzai/commit/8a28e95637377f29d7204f51d49a174f2518929f)

## Consolidation routes - research labels, not TRAIN decisions

### V51/V52 grade A (17 cases)

Candidate route: inspect first for behavioral coverage and potential usefulness. Check factual-risk notes and instruction compliance rather than assuming grade A means error-free. Verify the entire published public conversation, source identity, deduplication and semantic-family split exclusions before any future target construction. Keep the original review grade immutable.

Examples:
- [V51-017](../reviews/smoltalk-v51/cases/017-fd184c30876d2798.md): strong multi-turn world-building and character continuity, a candidate for creative-behavior quality review.
- [V51-024](../reviews/smoltalk-v51/cases/024-cbafdc84d4b21d68.md): correct algebra explanation and meaningful response to a user's refinement; a useful correction/continuity signal despite low heuristic priority.
- [V51-005](../reviews/smoltalk-v51/cases/005-09ff1301dd61d472.md): conditional reasoning with an initial overstatement and unverified claims; factual-risk REVIEW still applies.
- [V52-021](../reviews/smoltalk-v52/cases/021-79efbbcd0bab95ce.md): promising critical reasoning, but an initially categorical fallacy label requires careful interpretation before any reuse.
- [V52-026](../reviews/smoltalk-v52/cases/026-9e881c798f518582.md): good acceptance of a conceptual challenge and refinement of an initial Python terminology simplification.

### V51/V52 grade B (20 cases)

Candidate route: inspect case by case for valuable spans, explicit error repair, or restricted teaching purpose. Never copy the whole unmodified example into a positive training target. Preserve an immutable link to the original public case and describe every edited claim or segmented context dependency.

Examples:
- [V52-013](../reviews/smoltalk-v52/cases/013-8d1fa4491e9b2ca5.md): creative hypothetical reasoning, but the assistant asserts logical safety without demonstrating it. Any repaired variant must express uncertainty.
- [V52-025](../reviews/smoltalk-v52/cases/025-4bd411ceb95b9b3c.md): adaptive multi-turn statistical dialogue, but the stated average of approximately 69 F is wrong; the 12 provided readings average 68 F. Correct and review the answer before considering any derivative.

### V51/V52 grade C (19 cases)

Candidate route: keep for error analysis, instruction-fidelity tests, or diagnosis. Do not admit unchanged dialogues as positive targets. Reconsider an isolated valuable fragment only through a new, separately reviewed derivative record; a C label is not a ban on the topic itself.

Examples:
- [V52-001](../reviews/smoltalk-v52/cases/001-6d8c964d55c81f74.md): the assistant fails to respect a geometric constraint and compounds errors during a proposed correction.
- [V52-030](../reviews/smoltalk-v52/cases/030-08be411b2d10e024.md): proposed code violates an explicit operator prohibition.

### V48/V49 historical RETAIN (24) and REJECT (44)

Do **not** map RETAIN mechanically to A or REJECT to C. Those decisions used an earlier, largely general-quality rubric. Re-examine their **behavioral value and answer correctness separately** under the V50 persona-first framework without rewriting historical V48/V49 verdicts.

Previously rejected technical responses may retain a valuable correction or creative span, but unreliable claims must not become correct positive targets. Previously retained narrow factual answers may have limited value for persona-oriented training.

## Proposed V53 review gates

Gate 1 - **Cross-cycle inventory, read only.** Confirm exact public case counts, provenance, status fields and absence of duplicate source identifiers across V48/V49, V51 and V52. Record the distinction between the V48/V49 and V51/V52 rubrics. Do not assume report totals prove all semantic quality.

Gate 2 - **Behavior-first shortlist.** Prioritize demonstrable multi-turn dependency, user-led correction, stable fictional setting or character, nuanced uncertainty and change of perspective. Evaluate factual risk separately. Do not force a fixed HIGH/MEDIUM/LOW quota or infer population rates from diagnostic batches.

Gate 3 - **Explicit repair or segmentation planning.** For promising but imperfect conversations, identify exactly which assistant span is wrong, which context is essential, and what verifiable corrected target would be needed. Maintain distinct original and derivative records; do not silently alter published source cases.

Gate 4 - **Independent eligibility controls.** Before any dataset admission, verify permissions/licensing, source identity, duplicate and near-duplicate families, response reliability, semantic leakage against reserved evaluations and any required manual sign-off. Source provenance, review grade and train eligibility must remain separate metadata.

Gate 5 - **Decision summary.** Produce public, non-sensitive aggregate findings only after a reproducible V53 audit. Do not claim a validation outcome, a corrected example or a TRAIN admission without the corresponding completed evidence and authorization.

## Publication and privacy

- All GitHub discussion and reporting in V53 must derive **only from the already published public-external SmolTalk material**.
- No private ChatGPT exports, excerpts, private-source identifiers, private-derived counts, hidden prompts, credentials or locally held private-corpus reports may enter public GitHub.
- Public case dialogue and earlier reports remain immutable. The final V52 report is historical and must not be regenerated under the same STEP_ID.
- A future scripted numeric audit should first be reviewed and committed under `tools/public-audits/`, with any needed allowlist and tests. It may be published using `tools/gogit_public.py` under a **new unique** STEP_ID, from a clean synchronized `main` on fhc2.
- GOGIT runs only when invoked explicitly; it is not scheduled and does not transmit arbitrary terminal output.
- TRAIN, VALIDATION and BLIND assignments, tokenizer, architecture, model checkpoints and private-corpus pipeline are unchanged.
- Phase 03 model training remains **NOT AUTHORIZED**.

## Immediate operational next step

Gate 1 was published as [`PHASE03-SMOLTALK-V53-CROSS-CYCLE-INVENTORY-001`](../reports/assistant-results/history/PHASE03-SMOLTALK-V53-CROSS-CYCLE-INVENTORY-001.json), confirming 124 distinct reviewed public sources and zero cross-cycle duplicates. Gate 2 is documented in [`reviews/smoltalk-v53/SHORTLIST-001.md`](../reviews/smoltalk-v53/SHORTLIST-001.md), implemented in [`tools/public-audits/smoltalk_v53_behavior_shortlist.py`](../tools/public-audits/smoltalk_v53_behavior_shortlist.py), and has a dedicated [GOGIT execution guide](../tools/V53-GATE2-GOGIT.md). The next operational action is the one-time Gate 2 GOGIT execution on a clean synchronized `main` on fhc2. Interpret that published result before authoring any repair derivative.
