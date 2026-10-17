# Mini-Kuzai Phase 03 - V53 corpus eligibility GOGIT

Status: **eligibility decisions are documented for the first two repaired derivatives; the eligibility GOGIT audit has not yet been executed.**

## Scope

This gate applies provenance/license continuity, duplicate control and semantic split protection to:

- `V53-DERIV-001-V52-025`
- `V53-DERIV-002-V51-013`

The independent derivative-review gate is a required prerequisite.

## Recorded decisions

### V53-DERIV-001-V52-025

- provenance/license: PASS
- exact duplicate: no
- near duplicate: no
- candidate behavior: B07
- TRAIN group considered: `sg-b07-01 incomplete_evidence_hypothesis`
- reserved VALIDATION collision: **YES**
- collision target: `sg-b07-02 hypothesis_plus_test`
- result: **NOT_TRAIN_ELIGIBLE_RESERVED_VALIDATION_COLLISION**

The derivative explicitly combines a tentative linear-model hypothesis with
residual inspection as a verification method. This is too close to the
reserved VALIDATION scenario.

### V53-DERIV-002-V51-013

- provenance/license: PASS
- exact duplicate: no
- near duplicate: no
- candidate behavior: B08
- TRAIN group considered: `sg-b08-01 weak_technical_claim`
- reserved VALIDATION collision: no
- reserved BLIND collision: no
- result: **ELIGIBLE_FOR_ADMISSION_DECISION**

The user's larger-group conclusion is conditionally correct but incomplete
without occupancy constraints. The repaired answer adds the missing condition
without reproducing the reserved B08 evaluation challenges.

## Provenance and license

The public source is `HuggingFaceTB/smol-smoltalk`. The Hugging Face dataset
card was checked on 2026-10-17 and lists license `apache-2.0`.

The audit itself is intentionally offline and deterministic: it validates the
recorded public provenance/license decision and source SHA lineage rather than
performing network access during GOGIT.

## Duplicate control

Canonical controlled TRAIN comparison files:

```text
data/phase-03/train/train-pilot-v0.2.jsonl
data/phase-03/train/train-batch-b01-v0.2.jsonl
data/phase-03/train/train-batch-b02-v0.2.jsonl
data/phase-03/train/train-batch-b03-v0.2.jsonl
data/phase-03/train/train-batch-b04-v0.2.jsonl
data/phase-03/train/train-batch-b05-v0.2.jsonl
```

Expected canonical population: **37 unique records**.

Near-duplicate method:

```text
normalize lowercase alphanumeric tokens
build 5-token shingles
calculate Jaccard similarity
review threshold = 0.20
```

Old `v0.1` source batches are historical and are not treated as current
canonical TRAIN records.

## Expected metrics

```text
ELIGIBILITY TOTAL                 : 2
PROVENANCE PASS                   : 2
LICENSE PASS                      : 2
CANONICAL TRAIN RECORDS           : 37
EXACT DUPLICATE HITS              : 0
NEAR DUPLICATE HITS               : 0
RESERVED VALIDATION COLLISIONS    : 1
SEMANTIC PASS                     : 1
SEMANTIC BLOCKED                  : 1
ADMISSION READY                   : 1
TRAIN APPROVED                    : 0
SPLIT ASSIGNED                    : 0
```

## One-time execution

From the current repository shell with the project virtual environment active:

```bash
git pull --ff-only origin main && python -m py_compile tools/public-audits/smoltalk_v53_eligibility.py tests/phase-03/test_smoltalk_v53_eligibility.py tools/gogit_public.py && python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v53_eligibility.py' -v && python tools/gogit_public.py --step PHASE03-SMOLTALK-V53-ELIGIBILITY-001 --audit tools/public-audits/smoltalk_v53_eligibility.py
```

The command is chained with `&&`: compile and tests must succeed before
GOGIT can publish.

No terminal output needs to be copied into ChatGPT. After completion, request
`gogit`.

## Meaning of a successful audit

A successful audit will establish:

- one derivative blocked by semantic anti-leakage;
- one derivative ready for a separate admission decision;
- zero TRAIN approval;
- zero split assignment.

The next step must be an explicit corpus-admission decision for the single
eligible derivative. Do not silently add it to a TRAIN JSONL file.

Phase 03 training remains **NOT AUTHORIZED**.
