# Mini-Kuzai Phase 03 - V83 Post-V81 Refitted-Coordinate Context-Order Control 001

Status --> **PRE-START PROTOCOL FROZEN / EXECUTION NOT STARTED**

Date --> 2026-11-14

## Purpose and causal separation

V82 found 38 prediction changes and 38 alpha-sign changes on 9,170 frozen VALIDATION lexical positions after V81 continuation, versus five of each at V62 cycle 2. V82 reused the **cycle-2 TRAIN-fitted** diagnostic coordinate. V83 asks whether the observed post-V81 sensitivity is robust when the diagnostic coordinate is refitted on the **final V81 model** using the same frozen TRAIN records.

This is a read-only numerical control, not training, semantic evaluation, a generation test, or a new dataset selection.

## Immutable primary evidence

- baseline V62 cycle-2 checkpoint --> `/root/Mini-Kuzai/runs/v62-margin-001/checkpoint-cycle-02.pt`
- post-V81 checkpoint --> `/root/Mini-Kuzai/runs/v62-margin-001/checkpoint-last.pt`
- V81 final optimizer steps --> 136
- V81 final exposure tokens --> 1181302
- V81 training window --> CLOSED
- V81 further training authorized --> 0
- V82 scientific STEP_ID --> `PHASE03-SMOLTALK-V82-POST-CONTINUATION-CONTEXT-ORDER-REPLICATION-001`
- V82 baseline replay changes --> 5
- V82 final changes --> 38
- V82 VALIDATION lexical coverage --> 9170 / 9170
- V82 perturbed prefixes --> 9062
- V82 untouched prefixes --> 108

The V82 report, its underlying protocol and the V81 final closure are immutable dependencies. Any inconsistent dependency blocks V83.

## Frozen input comparison

- frozen TRAIN-only token sample / corpus ordering and train-fitted source constraints inherited from V75-V80
- frozen VALIDATION --> 36 records, 9170 lexical positions
- frozen `ORIGINAL` and `REVERSE_HISTORY_KEEP_LAST` prefix pairs
- same-path scoring, batch 32
- preserve BOS, immediate predecessor, target ID, prefix lengths, token multisets, original split, tokenizer and architecture
- no BLIND records, no new corpus and no per-position public outputs

## Diagnostic arms

A. **Replay old coordinate on final model**. Reproduce the V82 final outcome in the same scoring path: exactly 38 prediction changes and 38 alpha-sign changes out of 9170. All V82 input and safety invariants must match. Abort before B if this replay fails.

B. **Refit the coordinate on final model TRAIN only**. Recompute the final-model TRAIN mean, TRAIN PC1 and the frequency-residualized PC1 output profile, using the exact reviewed V75/V76 methodology, TRAIN token-frequency definition and ordering. Do not use VALIDATION or BLIND to fit, select, align or tune the coordinate.

C. **Evaluate final model with refitted coordinate**. Score the exact same paired VALIDATION prefixes under B and measure prediction/sign changes and decision-boundary diagnostics. Hold the model, input pairs, tokenizer and execution path identical to A: change **only** the diagnostic coordinate.

D. **Coordinate geometry control**. Measure the absolute alignment between original and refitted axes and verify deterministic sign conventions and finite norms; compare final-model old-coordinate versus final-model refitted-coordinate results. Where practical, repeat the refit and ensure it reproduces the same aggregates.

The difference between A and C quantifies coordinate dependence **at the same final checkpoint**. The original cycle-2 versus A comparison remains the already established V82 checkpoint comparison; it must not be conflated with the coordinate change.

## Numerical and integrity gates

- verify Git branch main synchronized with origin/main and worktree clean before running
- verify V81 closure, V82 scientific report, V82 START/FINAL receipts, final step/exposure count and zero further-training authorization
- verify checkpoint-cycle-02.pt, checkpoint-last.pt and checkpoint-best.pt are present and safe
- record local SHA256 values for the checkpoints used; verify no changes after the read-only run
- verify no active training lock and frozen TRAIN/VALIDATION dataset identities
- require exact V82 replay and complete 9170-position coverage
- reject NaN/Inf, unexpected tokenizer/architecture changes, invalid zero-norm geometry or mismatched sample counts
- require deterministic coordinate sign orientation or report only sign-invariant comparisons where applicable
- include numerical sensitivity controls for threshold-near cases; do not interpret small changes in isolation as semantic effects
- abort with a blocked status on any failed gate; never bypass via silent fallback
- no optimizer, scheduler updates, gradient update, checkpoint write, model parameter mutation, generation, corpus injection or BLIND access

## Aggregate-only GOGIT contract

Every published GOGIT STEP_ID must be unique. Output must obey the existing allowlist and 30-nonnegative-integer-metric limit, splitting separate audited reports where necessary rather than discarding safety gates.

Required fields, after registering them explicitly in the reviewed GOGIT schema:
- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V83_BLIND_ACCESS=0`
- `V83_PASS=1` only on all gates passing

Report at least old-coordinate replay agreement, refitted-coordinate prediction/sign changes, matched lexical coverage, altered/unaltered prefixes, finite geometry and alignment, boundary/crossing statistics, and an explicit model/checkpoint integrity gate. Publish **no raw text, tokens, secrets, individual examples, hidden states or per-position data**.

Before execution, implementation, tests, allowlists and a CPU-only safety preflight require separate review; GPU execution is permitted only within the explicit START-approved V83 read-only scope and after CPU preflight passes.

## Interpretation constraints

V83 can establish whether the numerical context-order sensitivity measured after V81 is stable or dependent on a TRAIN-refitted diagnostic coordinate. If an outcome is materially different, the report must attribute that difference to the **coordinate change at the fixed final model**, not to further learning. Neither V82 nor V83 establishes semantic comprehension, conversational ability, reasoning, training readiness, or causal usefulness of earlier context.

## Authorization and public flow

This PRE-START protocol and its START source may be committed and reviewed without starting V83 scientific work. **START-DEV-FLOW V83** requires an explicit future user authorization. Until the START publication is verified, no V83 implementation, CPU/GPU execution or scientific GOGIT may start.

START authorizes only the read-only V83 implementation, controls and VALIDATION diagnostics documented here. It never authorizes training, optimizer steps, checkpoint mutation, BLIND access, new datasets, semantic claims or FINAL publication.

After scientific GOGIT PASS, **FINAL-DEV-FLOW V83** separately requires explicit authorization. The V83+ FINAL media flow must verify GitHub FINAL, YouTube PUBLIC, exactly one LinkedIn native-video post (no FINAL LinkedIn text), media fallback, receipts and automatic read-only FINAL GOGIT. Only after verified FINAL GOGIT may `MAJ-THEKUZNETWORK` run across all five mandated repositories. No V84 START before that maintenance.

## Pre-START exit criteria

- V82 evidence and published closure verified
- backup branch recorded and recoverable
- V83 protocol and V83 START source committed on main
- no V83 execution or training
- pre-START checks recorded, with any missing local checks clearly marked unverified
- explicit operator authorization still required for START

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
