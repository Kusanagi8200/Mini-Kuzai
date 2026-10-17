# Mini-Kuzai Phase 03 - V53 Gate 3 repair-plan GOGIT

Status: **Gate 3 repair plan, audit script and tests are published; the Gate 3 GOGIT audit has not yet been executed.**

## Scope

This gate covers the eight B cases selected by the completed V53 Gate 2 behavioral shortlist.

The detailed repair specification is documented in [V53 REPAIR-PLAN-001](../reviews/smoltalk-v53/REPAIR-PLAN-001.md).

Gate 3 does not create corrected conversations. It verifies that the same eight cases still reconstruct from the public SmolTalk source, still satisfy the Gate 2 repair-priority rule, and still match the documented overlapping repair flags.

Expected metrics:

```text
REPAIR TOTAL                    : 8
SOURCE MATCHED                  : 8
GATE2 PRIORITY CONFIRMED        : 8
SEGMENTATION REQUIRED           : 3
FACTUAL / NUMERIC FIX           : 4
UNCERTAINTY / LOGIC CALIBRATION : 3
WORDING / CONSTRAINT CLEANUP    : 3
TRAIN APPROVED                  : 0
```

The repair flags overlap and therefore do not sum to eight.

## One-time execution

The project shell is already expected to be located at the Mini-Kuzai repository root with the project virtual environment active.

Run:

```bash
git pull --ff-only origin main && python -m py_compile tools/public-audits/smoltalk_v53_repair_plan.py tests/phase-03/test_smoltalk_v53_repair_plan.py tools/gogit_public.py && python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v53_repair_plan.py' -v && python tools/gogit_public.py --step PHASE03-SMOLTALK-V53-REPAIR-PLAN-001 --audit tools/public-audits/smoltalk_v53_repair_plan.py
```

The chain uses `&&`: compilation and tests must succeed before GOGIT executes.

No terminal output needs to be copied into ChatGPT. After completion, request `gogit` so the published result can be inspected directly on GitHub.

## Failure policy

If compilation, tests, source reconstruction, Gate 2 comparison, repair-flag validation, Git preflight, commit or push fails:

- do not force a result;
- do not edit historical reports manually;
- do not re-use a STEP_ID that has already been published;
- diagnose the failing gate before retrying.

## After a successful Gate 3 audit

The next step is **derivative authoring design**, not automatic training admission.

Each future repaired derivative must:

- have a new identifier;
- retain public-source lineage;
- distinguish original from edited text;
- state the repair rationale;
- pass factual and instruction-fit review;
- pass duplicate and semantic split checks;
- remain outside TRAIN until explicit admission is authorized.

TRAIN, VALIDATION and BLIND remain unchanged.
Tokenizer and architecture remain unfrozen.
Phase 03 training remains **NOT AUTHORIZED**.
