# Mini-Kuzai Phase 03 - V53 first corpus admission decision GOGIT

Status: **one derivative is approved for future TRAIN-corpus serialization; the admission-decision GOGIT audit has not yet been executed.**

## Decision

The only eligibility-ready derivative is:

```text
derivative        : V53-DERIV-002-V51-013
decision          : APPROVED_FOR_TRAIN_CORPUS_SERIALIZATION
target split      : train
target group      : sg-b08-01
primary behavior  : B08
scenario          : weak_technical_claim
reserved record id: p03-train-b08-000001
```

The reserved record id is currently unused.

## Important state separation

Corpus admission and model training authorization are different decisions.

Current state:

```text
corpus admission approved        : 1
canonical serialization complete : 0
canonical TRAIN records          : 37
model training authorized        : 0
tokenizer frozen                 : 0
architecture selected            : 0
```

No `data/phase-03/train/*.jsonl` file is changed by this admission decision.

## Audit checks

The audit must verify:

1. the completed V53 eligibility report still has exactly one admission-ready derivative;
2. the current eligibility audit still reproduces its 2-case result;
3. `sg-b08-01` still exists in semantic inventory v0.3 as TRAIN / B08 / `weak_technical_claim`;
4. the six canonical reviewed TRAIN files still contain 37 unique records;
5. `p03-train-b08-000001` is not yet present;
6. the decision still marks serialization incomplete and model training unauthorized.

## Expected metrics

```text
ADMISSION DECISIONS TOTAL        : 1
CORPUS APPROVED                  : 1
TARGET TRAIN                     : 1
GROUP VALID                      : 1
RESERVED ID FREE                 : 1
CANONICAL TRAIN RECORDS          : 37
SERIALIZED                       : 0
MODEL TRAINING AUTHORIZED        : 0
```

## One-time execution

From the current repository shell with the project virtual environment active:

```bash
git pull --ff-only origin main && python -m py_compile tools/public-audits/smoltalk_v53_admission_decision.py tests/phase-03/test_smoltalk_v53_admission_decision.py tools/gogit_public.py && python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v53_admission_decision.py' -v && python tools/gogit_public.py --step PHASE03-SMOLTALK-V53-ADMISSION-DECISION-001 --audit tools/public-audits/smoltalk_v53_admission_decision.py
```

The command is chained with `&&`; GOGIT cannot publish if compile or tests fail.

No terminal output needs to be copied into ChatGPT. After completion, request `gogit`.

## After a successful audit

The next step is **canonical serialization** of the approved derivative as
`p03-train-b08-000001` in a new B08 TRAIN batch, followed by structural and
semantic review of that serialized record.

Do not interpret serialization as permission to train the model.

Phase 03 model training remains **NOT AUTHORIZED**.
