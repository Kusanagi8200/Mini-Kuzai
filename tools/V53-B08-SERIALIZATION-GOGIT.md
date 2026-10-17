# Mini-Kuzai Phase 03 - V53 B08 canonical serialization GOGIT

Status: **the first admitted public derivative is serialized and reviewed as a B08 TRAIN record; the serialization GOGIT audit has not yet been executed.**

## Canonical record

```text
record id        : p03-train-b08-000001
group id         : sg-b08-01
split            : train
primary behavior : B08
secondary        : B16
scenario         : weak_technical_claim
conversation     : multi_turn
```

Source lineage:

```text
derivative       : V53-DERIV-002-V51-013
admission        : V53-ADMIT-001-V51-013
public source    : HuggingFaceTB/smol-smoltalk
```

## Serialization versions

`train-batch-b08-v0.1.jsonl` is the initial canonical serialization from the
admission decision.

Its review detected one research-metadata issue:

```text
knowledge_status: LAB -> VOLATILE
```

Hotel pricing and occupancy constraints are real-world contextual information,
not stable laboratory facts.

`train-batch-b08-v0.2.jsonl` contains that metadata correction.

**The six model-visible messages are unchanged between v0.1, v0.2 and the
independently reviewed derivative.**

## B08 completion state

This one record does not complete behavior B08.

```text
current sg-b08-01 records : 1
planned variants          : 4
remaining planned         : 3
B08 TRAIN complete        : false
```

The current canonical TRAIN population becomes 38 reviewed records when the
v0.2 B08 record is included.

## Expected GOGIT metrics

```text
SERIALIZED RECORDS          : 1
REVIEWED RECORDS            : 1
METADATA CORRECTIONS        : 1
MODEL-VISIBLE CHANGES       : 0
GROUP TRAIN VALID           : 1
RESERVED OVERLAP            : 0
CANONICAL TRAIN RECORDS     : 38
B08 GROUP CURRENT           : 1
B08 GROUP PLANNED           : 4
B08 TRAIN COMPLETE          : 0
MODEL TRAINING AUTHORIZED   : 0
```

## One-time execution

From the current repository shell with the project virtual environment active:

```bash
git pull --ff-only origin main && python -m py_compile tools/public-audits/smoltalk_v53_b08_serialization.py tests/phase-03/test_smoltalk_v53_b08_serialization.py tools/gogit_public.py && python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v53_b08_serialization.py' -v && python tools/gogit_public.py --step PHASE03-SMOLTALK-V53-B08-SERIALIZATION-001 --audit tools/public-audits/smoltalk_v53_b08_serialization.py
```

The command is chained with `&&`; GOGIT cannot publish unless compilation
and tests succeed.

No terminal output needs to be copied into ChatGPT. After completion, request
`gogit`.

## After a successful audit

The public external derivative will then be fully represented in the canonical
TRAIN corpus as one reviewed B08 record.

That does **not** mean B08 is complete and does **not** authorize model
training.

The next corpus-building decision should consider whether to continue the
remaining B08 TRAIN coverage or return to the broader V53 public-candidate
pipeline.

Phase 03 model training remains **NOT AUTHORIZED**.
