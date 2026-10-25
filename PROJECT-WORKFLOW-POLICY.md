# MINI-KUZAI - PROJECT WORKFLOW POLICY

Version: 0.2
Status: ACTIVE_PROJECT_CONSTRAINT

This policy defines the default execution method for Mini-Kuzai project work.

Its purpose is to reduce unnecessary stop/start cycles while preserving auditability, reproducibility, semantic quality and safe rollback.

## 1. Loop-first execution principle

When several project steps can be evaluated mechanically and executed in a deterministic order, they should be grouped into a single resumable workflow instead of being exposed as separate manual steps.

Prefer:

```text
inspect state
-> execute next missing gate
-> validate
-> publish evidence
-> re-read published state
-> continue while another deterministic gate is available
-> stop only at a real decision boundary
```

over repeated one-command / one-feedback cycles.

This applies across the project, including:

- corpus construction;
- dataset review batches;
- structural validation;
- duplicate and cross-split audits;
- test suites;
- GOGIT publication;
- metadata and manifest consistency;
- deterministic conversions;
- documentation consistency checks;
- training preparation;
- checkpoint/evaluation pipelines where rollback and state validation are defined.

## 2. Resumability and idempotence

A looped workflow must, whenever practical:

1. inspect repository and published state before doing work;
2. detect already completed gates;
3. verify completed gates before skipping them;
4. execute only missing or invalid gates;
5. use immutable STEP_ID/history records where applicable;
6. never overwrite a successful historical GOGIT result;
7. support safe re-execution after interruption;
8. fail closed when state cannot be proven.

A relaunch should continue from the first unvalidated gate rather than repeat all prior work.

## 3. Gate integrity

Looping does not remove gates.

Every important transition must remain independently testable and auditable.

A workflow may chain several gates automatically only when the output of each gate can be verified before the next one begins.

Examples:

- tests must pass before GOGIT publication;
- an integrity STEP_ID must exist and contain expected metrics before a freeze gate;
- a freeze gate must reference the exact reviewed corpus version;
- training authorization must remain false until its own explicit authorization gate exists and passes.

## 4. Automatic retry and correction boundary

The workflow may automatically retry technical operations that are deterministic and safe, such as:

- re-running a failed test after a non-semantic technical correction already encoded in the repository;
- resuming after an interrupted publication;
- skipping a STEP_ID already published and verified;
- repeating read-only audits;
- rebuilding derived metadata from an unchanged canonical source when the transformation is deterministic.

The workflow must not silently change substantive data merely to make a gate pass.

In particular, automatic loops must stop when failure indicates:

- semantic overlap;
- questionable training or validation content;
- factual uncertainty requiring review;
- a changed behavioral decision;
- an unexpected corpus mutation;
- a destructive or irreversible operation;
- missing provenance;
- a secret/private-data exposure risk;
- a split-leakage risk;
- an authorization decision that has not been explicitly granted.

Such failures require review or an explicit corrective artifact before the loop resumes.

## 5. Semantic review rule

Semantic quality remains stronger than automation.

A loop may orchestrate semantic-review artifacts and subsequent deterministic gates, but it must not fabricate an ACCEPT decision merely to continue.

If review produces REVISE, REJECT or HOLD:

```text
stop semantic progression
-> preserve evidence
-> create an explicit corrected version if justified
-> re-review
-> resume deterministic gates only after the new review passes
```

Historical candidates and review evidence must remain traceable.

## 6. GOGIT loop rule

Where GOGIT is used, project workflows should prefer a single resumable runner capable of:

1. validating prerequisites;
2. compiling relevant scripts/tests;
3. running each pending gate;
4. publishing its allowlisted metrics;
5. verifying the GitHub history record;
6. continuing to the next deterministic gate;
7. emitting one final result marker.

The user should normally need to launch the runner once and request `gogit` once after completion.

Each GOGIT gate must still retain its own immutable STEP_ID and history record.

## 7. Safety and rollback

Before changing an existing canonical file, preserve a recoverable prior state through Git history and record the prior blob/commit when the operation is material.

For transformations with elevated risk, create an explicit archived or versioned predecessor instead of overwriting evidence.

Never use force-push as part of an automated project loop.

A dirty worktree, diverged main branch, unexpected staged file, or failed remote verification must block publication.

## 8. Project state must drive execution

Workflow scripts must derive progression from validated state, not from assumptions about what "should" already be complete.

Typical state inputs include:

- Git branch and synchronization;
- committed file hashes;
- manifests;
- review records;
- immutable report history;
- test results;
- explicit frozen/authorized flags.

The loop must verify expected state after every published transition.

## 9. Human interaction minimization

The default objective is to minimize user intervention without weakening control.

Do not stop merely because one small deterministic step completed.

Continue automatically while:

- the next operation is already defined;
- required inputs are present;
- the action is reversible or read-only;
- success criteria are machine-checkable;
- no new semantic or authorization decision is required.

Stop and request intervention only at a genuine boundary.

## 10. Current Phase 03 application

The policy evolved from the V54 per-behavior validation runner into the generic V54/V55 master-loop architecture.

The current reference implementation is the V55 BLIND pipeline:

- one master command for B01-B18;
- prerequisite verification against V54 VALIDATION closure;
- committed canonical batch hashes;
- explicit semantic review evidence;
- integrity gate for each behavior;
- GOGIT publication and verification;
- freeze gate for each behavior;
- second GOGIT publication and verification;
- restart-safe skipping of already verified histories;
- automatic stop on semantic or authorization failure;
- no automatic semantic rewriting;
- immutable correction lineage for revised candidates;
- training authorization preserved at false.

The V55 run completed all 18 behavior-level BLIND freezes and the global BLIND closure gate. The controlled corpus boundary is closed; training authorization remains false.

Future Mini-Kuzai workflows should reuse this state-driven generic pattern where appropriate rather than returning to unnecessary one-command / one-feedback cycles.

## 11. Priority relative to other project constraints

This policy optimizes execution cadence only.

It does not override:

- semantic split protection;
- TRAIN / VALIDATION / BLIND separation;
- provenance requirements;
- private-data restrictions;
- factual-quality requirements;
- immutable historical evidence;
- training authorization gates;
- checkpoint protection;
- reproducibility requirements.

When speed conflicts with one of these constraints, the stronger safety, semantic or reproducibility constraint wins.
