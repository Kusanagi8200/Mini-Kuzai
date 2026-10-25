# MINI-KUZAI PHASE 03 - V59 TRAINING MIX AND SEGMENTATION

Status: SEGMENTATION CLOSED - PUBLIC MIX QUALITY GATE OPEN - SAMPLE 002 JOB AUTOMATED

V59 is the final data-preparation workstream before any model-training
authorization decision.

Training remains **NOT AUTHORIZED / NOT STARTED**.

## Frozen V59 segmentation policy

The frozen V58 context is 2048 tokens.

V59 segmentation:

- preserves the frozen V57 textual serialization;
- preserves complete USER / MINI-KUZAI pairs;
- cuts only between complete user/assistant pairs;
- greedily packs complete pairs up to 2048 tokens;
- preserves source text and order exactly;
- never truncates source text;
- never silently splits inside a message or pair;
- blocks an individual pair that cannot fit within 2048 tokens.

The segmentation implementation and audit are closed.

Controlled TRAIN remains 107 conversations with no blocked pair.

## Public mix state

Starting public V44 population: 1,139 conversations.

Known structural exclusions:

- 3 conversations blocked by an individual pair over 2048 tokens;
- 2 public sources already represented by controlled TRAIN derivatives.

Known-negative V51/V52 filtering removes a further 22 unique public sources.

The resulting V59 public candidate population is:

- 1,112 candidate conversations;
- 1,554 turn-aware segments;
- 1,730,414 public tokens;
- 1.460 public tokens per model parameter;
- 1,754,953 tokens including controlled TRAIN;
- 1.481 combined tokens per model parameter.

Of these 1,112 candidates, 32 had already passed structured V51/V52 review.
The remaining bulk population for quality estimation is 1,080 conversations.

## Bulk quality Sample 001

Sample 001 reviewed 72 deterministic, stratified public cases.

Observed review outcomes:

- KEEP: 36;
- REPAIR: 19;
- EXCLUDE: 17;
- factual risk HIGH: 18;
- instruction fit BAD: 9.

The weighted diagnostic over the 1,080-case bulk estimated:

- KEEP: 52.00%;
- REPAIR: 26.95%;
- EXCLUDE: 21.05%;
- REPAIR + EXCLUDE: 48.00%.

Approximate 95% interval for unchanged-unsuitable material:
35.63% to 60.38%.

This estimate is diagnostic, not a formal probability-sampling confidence
statement, because Sample 001 used deterministic category-balanced selection.

Conclusion:

**bulk unchanged admission failed.**

The full V44-derived bulk must not be promoted unchanged into supervised
training.

## Sample 002 objective

Sample 002 adds 72 new cases with no overlap with Sample 001.

The cumulative target is 144 reviewed cases.

Unlike Sample 001, Sample 002 allocation is calculated from the real sizes of
the 10 observed strata:

- V50 priority;
- public source subset;
- SINGLE vs MULTITURN.

The cumulative 144-case design is rebalanced toward the real population
distribution while preserving deterministic category diversity inside each
stratum.

Sample 002 also introduces structured defect tags:

- NONE;
- ROLE_CONTAMINATION;
- FACTUAL_ERROR;
- LOGICAL_ERROR;
- TECHNICAL_ERROR;
- INSTRUCTION_FAILURE;
- TIME_SENSITIVE;
- STYLE_QUALITY;
- OTHER.

These tags are intended to support the next filter-rule mining stage.

## Automated next-job workflow

The Sample 002 job is intentionally reduced to two FHC2 commands.

### 1. PREPARE

After synchronizing the repository:

```bash
python3 tools/run_v59_bulk_sample_002_job.py prepare
```

The prepare action:

1. reconstructs the frozen 1,080-case eligible population;
2. verifies Sample 001 is complete;
3. computes cumulative proportional stratum targets;
4. selects 72 new deterministic cases with zero Sample 001 overlap;
5. writes the Sample 002 review packet and sampling plan;
6. commits and pushes the packet to GitHub.

The semantic review is then performed directly from GitHub.

The reviewer publishes:

`reviews/smoltalk-v59-bulk-sample-002/DECISIONS-002.json`

with status:

`REVIEW_COMPLETE_PENDING_APPLICATION`

### 2. FINALIZE

After DECISIONS-002.json has been published and the repository is synchronized:

```bash
python3 tools/run_v59_bulk_sample_002_job.py finalize
```

The finalize action:

1. validates all 72 structured decisions;
2. applies them to the review pages;
3. creates RESULTS-002.md;
4. commits and pushes the reviewed packet;
5. runs the cumulative Sample 001 + Sample 002 weighted audit;
6. publishes the aggregate numeric result through GOGIT using:

`PHASE03-SMOLTALK-V59-BULK-COMBINED-002`

The driver is restart-safe at the stage level:

- an already prepared Sample 002 is not recreated;
- an already applied review is not reapplied;
- an existing GOGIT history step is not overwritten.

## Cumulative quality gate

The cumulative audit measures:

- 144 unique reviewed cases;
- stratum-weighted KEEP / REPAIR / EXCLUDE;
- approximate uncertainty for KEEP and unchanged-unsuitable material;
- weighted factual-risk HIGH rate;
- weighted instruction-fit BAD rate;
- effective weighted sample size.

The cumulative audit remains explicitly diagnostic rather than a formal
probability-sampling estimator.

It does not finalize the training mix automatically.

## Training mixture boundary

The final training mixture continues to follow the persona-first policy:

- prioritize cognitive and creative conversational value;
- prioritize multi-turn continuity, correction and contextual adaptation;
- specialist IT competence is not required;
- never use a known incorrect answer as a correct supervised target;
- preserve provenance and duplicate controls;
- preserve VALIDATION and BLIND TEST isolation;
- exclude private conversation data.

Architecture readiness does not imply training authorization.

Current state:

- V59 segmentation: **CLOSED**;
- oversized-pair decisions: **CLOSED**;
- replacement gate: **CLOSED**;
- known-negative filtering: **CLOSED**;
- Sample 001 review: **CLOSED**;
- Sample 002 workflow: **SCRIPTED / READY**;
- V59 final mix: **NOT FINALIZED**;
- model training: **NOT AUTHORIZED / NOT STARTED**.
