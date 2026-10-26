# Mini-Kuzai Phase 03 - B08 completion + derivative-003 review GOGIT

Status --> **B08 TRAIN completion and independent review of V53-DERIV-003 are prepared for publication.**

## Track 1 - complete B08 TRAIN coverage

Canonical reviewed batch -->

```text
data/phase-03/train/train-batch-b08-v0.5.jsonl
```

Coverage -->

```text
sg-b08-01 weak_technical_claim   : 4 / 4
sg-b08-02 contradiction_detection: 4 / 4
B08 TRAIN behavior complete      : yes
```

The four `sg-b08-02` records require explicit contradiction detection. A first prepublication `v0.4` serialization attempt was rejected by the audit because three records had shifted constructor arguments; corrected `v0.5` restores IDs `p03-train-b08-000006` through `000008` and valid user/assistant message pairs.
They are designed not to instantiate -->

- B08 validation `sg-b08-03 unsupported_conclusion`
- B08 blind `sg-b08-04 social_pressure_agreement`
- B11 validation `sg-b11-03 unresolved_contradiction_test`.

Expected state -->

```text
B08 total records              : 8
sg-b08-01 records              : 4
sg-b08-02 records              : 4
sg-b08-01 complete             : 1
sg-b08-02 complete             : 1
B08 TRAIN complete             : 1
reserved overlap               : 0
B11 diagnostic-test overlap    : 0
canonical TRAIN records        : 45
validation text created        : 0
model training authorized      : 0
```

## Track 2 - independent review of V53-DERIV-003

Candidate -->

```text
V53-DERIV-003-V51-002
proposed behavior : B12
TRAIN route       : sg-b12-01 alternative_generation
```

Independent review result prepared -->

```text
review status          : PASS_TO_ELIGIBILITY_CONTROLS
factual accuracy       : PASS
multi-turn coherence   : PASS
behavioral value       : PASS
instruction fit        : PASS
creativity             : PASS
further repair         : no
TRAIN approved         : no
split assigned         : no
```

The derivative remains outside TRAIN. A successful review audit only permits
the next eligibility gate --> provenance/license, duplicate control and semantic
split exclusion.

## One-time execution

From the current repository shell with the project virtual environment active -->

```bash
git pull --ff-only origin main && python -m py_compile tools/public-audits/smoltalk_v53_b08_behavior_complete.py tools/public-audits/smoltalk_v53_deriv003_review.py tests/phase-03/test_smoltalk_v53_b08_behavior_complete.py tests/phase-03/test_smoltalk_v53_deriv003_review.py tools/gogit_public.py && python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v53_b08_behavior_complete.py' -v && python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v53_deriv003_review.py' -v && python tools/gogit_public.py --step PHASE03-SMOLTALK-V53-B08-BEHAVIOR-COMPLETE-001 --audit tools/public-audits/smoltalk_v53_b08_behavior_complete.py && python tools/gogit_public.py --step PHASE03-SMOLTALK-V53-DERIV003-REVIEW-001 --audit tools/public-audits/smoltalk_v53_deriv003_review.py
```

The two publications remain separate immutable GOGIT steps. Neither STEP_ID was published by the failed prepublication attempt.

No terminal output needs to be copied into ChatGPT. After completion, request
`gogit`.

## Next state if both pass

- canonical TRAIN --> 45 records
- B08 TRAIN behavior --> complete
- V53-DERIV-003 --> ready for eligibility controls
- no new public derivative admitted by this step
- model training remains **NOT AUTHORIZED**.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
