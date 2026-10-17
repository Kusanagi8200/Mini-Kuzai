# Mini-Kuzai V53 corpus admission decisions

Status: **two public SmolTalk derivatives have explicit corpus-admission decisions. The first is already serialized in canonical B08 TRAIN; the second is approved for future B12 serialization but is not yet serialized.**

## Decision 1 - B08

[V53-ADMIT-001-V51-013](V53-ADMIT-001-V51-013.json) approved
`V53-DERIV-002-V51-013` for canonical TRAIN serialization in:

- split: `train`
- semantic group: `sg-b08-01`
- primary behavior: `B08`
- scenario: `weak_technical_claim`
- record ID: `p03-train-b08-000001`

That decision has already completed serialization and is part of the audited B08 corpus.

## Decision 2 - B12

[V53-ADMIT-002-V51-002](V53-ADMIT-002-V51-002.json) approves
`V53-DERIV-003-V51-002` for future canonical TRAIN serialization in:

- split: `train`
- semantic group: `sg-b12-01`
- primary behavior: `B12`
- scenario: `alternative_generation`
- reserved record ID: `p03-train-b12-000001`

The reserved B12 ID was checked as unused before this decision.

Current state:

```text
explicit admission decisions       : 2
previously serialized admissions   : 1
new B12 admission prepared         : 1
B12 canonical serialization        : 0
canonical TRAIN records            : 45
model training authorized          : false
tokenizer frozen                    : false
architecture selected               : false
```

The B12 decision changes corpus-admission state only. It does not itself
modify `data/phase-03/train/*.jsonl`.

The next operation is a reproducible admission-decision audit for
`V53-ADMIT-002-V51-002`. Only after that audit should
`p03-train-b12-000001` be serialized into a new canonical B12 TRAIN batch
and reviewed structurally and semantically.

Phase 03 model training remains **NOT AUTHORIZED**.
