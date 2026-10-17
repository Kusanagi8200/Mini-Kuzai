# Mini-Kuzai Phase 03 - V53 derivative-003 B12 eligibility GOGIT

Status: **V53-DERIV-003-V51-002 passes the prepared provenance, duplicate and semantic-split controls and is ready for a one-time eligibility audit.**

## Candidate

```text
derivative        : V53-DERIV-003-V51-002
primary behavior  : B12
TRAIN route       : sg-b12-01
scenario          : alternative_generation
```

## Provenance and license

```text
public dataset    : HuggingFaceTB/smol-smoltalk
source license    : apache-2.0
source SHA-256    : 383f5926f407ae183de348a6aae660e952a4e03887ba2ed275d259969e23fc9a
```

## Duplicate control

Method:

```text
normalization     : lowercase alphanumeric tokens
comparison        : 5-token shingles
similarity        : Jaccard
near-dup threshold: 0.20
```

Prepared result against the current canonical TRAIN population:

```text
canonical TRAIN records compared: 45
exact duplicate hits             : 0
maximum TRAIN Jaccard            : 0.0
near-duplicate hits              : 0
```

## Semantic split control

TRAIN target:

```text
sg-b12-01 alternative_generation
```

Reserved evaluation scopes:

```text
VALIDATION : sg-b12-03 creative_hypothesis_epistemic_control
BLIND TEST : sg-b12-04 creative_under_constraints
```

Manual decision:

- no VALIDATION collision;
- no BLIND collision;
- the fictional post-pandemic possibilities remain clearly story-generation choices rather than empirical hypotheses;
- the dialogue does not instantiate an explicit constraint-solving evaluation challenge.

## Expected metrics

```text
TOTAL                           : 1
PROVENANCE PASS                 : 1
LICENSE PASS                    : 1
CANONICAL TRAIN RECORDS         : 45
EXACT DUP HITS                  : 0
NEAR DUP HITS                   : 0
RESERVED VALIDATION COLLISION   : 0
RESERVED BLIND COLLISION        : 0
SEMANTIC PASS                   : 1
ADMISSION READY                 : 1
TRAIN APPROVED                  : 0
SPLIT ASSIGNED                  : 0
```

## One-time execution

From the current repository shell with the project virtual environment active:

```bash
git pull --ff-only origin main && python -m py_compile tools/public-audits/smoltalk_v53_deriv003_eligibility.py tests/phase-03/test_smoltalk_v53_deriv003_eligibility.py tools/gogit_public.py && python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v53_deriv003_eligibility.py' -v && python tools/gogit_public.py --step PHASE03-SMOLTALK-V53-DERIV003-ELIGIBILITY-001 --audit tools/public-audits/smoltalk_v53_deriv003_eligibility.py
```

The command is chained with `&&`; no GOGIT publication can occur if compile,
the full repository-state audit test, or the allowlist test fails.

No terminal output needs to be copied into ChatGPT. After completion, request
`gogit`.

## After a successful audit

The derivative becomes eligible for an explicit admission decision only.

A successful audit does **not**:

- admit the derivative to TRAIN;
- assign a dataset split;
- serialize a canonical B12 record;
- authorize model training.

Phase 03 model training remains **NOT AUTHORIZED**.
