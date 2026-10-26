# Mini-Kuzai Phase 03 - first V53 repaired derivatives GOGIT

Status --> **two repaired derivative candidates are published; their numeric integrity audit has not yet been executed.**

## Current derivative candidates

- `V53-DERIV-001-V52-025` --> temperature trend/regression; mean corrected to 68.0 F and model uncertainty calibrated.
- `V53-DERIV-002-V51-013` --> hotel pricing comparison; contradictory wording removed and room-occupancy assumption made explicit.

Both are public-source research candidates only.

Safety state for each derivative -->

```text
status                       : CANDIDATE_REVIEW_REQUIRED
training_approved            : false
dataset_split_assigned       : false
semantic_validation_complete : false
```

The original V51/V52 public review pages remain unchanged.

## One-time audit

From the current repository shell with the project virtual environment already active, run -->

```bash
git pull --ff-only origin main && python -m py_compile tools/public-audits/smoltalk_v53_derivative_candidates.py tests/phase-03/test_smoltalk_v53_derivative_candidates.py tools/gogit_public.py && python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v53_derivative_candidates.py' -v && python tools/gogit_public.py --step PHASE03-SMOLTALK-V53-DERIVATIVE-CANDIDATES-001 --audit tools/public-audits/smoltalk_v53_derivative_candidates.py
```

The command is deliberately chained with `&&` --> compilation and tests must succeed before GOGIT can publish.

Expected public metrics -->

```text
DERIVATIVE TOTAL              : 2
SOURCE MATCHED                : 2
USER SOURCE-NORMALIZED TURNS  : 6
ASSISTANT DERIVATIVE REWRITES : 6
REVIEW PENDING                : 2
TRAIN APPROVED                : 0
SPLIT ASSIGNED                : 0
SEMANTIC VALIDATED            : 0
```

No terminal output needs to be copied into ChatGPT. After completion, request `gogit`.

## What this audit does not do

A successful result does **not** mean that either derivative is admitted to TRAIN.

After this integrity audit, both derivative conversations still require a new semantic/factual review as derivative records. Only then can provenance, near-duplicate and semantic split controls be considered for admission.

Phase 03 training remains **NOT AUTHORIZED**.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
