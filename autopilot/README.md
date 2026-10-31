# Mini-Kuzai AUTOPILOT V1 - MODE 2

Status --> **IMPLEMENTATION PUBLISHED / LOCAL CPU + GPU EXECUTION TO BE VERIFIED / TRAINING DISABLED**

Date --> 2026-10-31

## Goal

Replace the manual GO / GOGIT / analysis / GO cycle with an autonomous **local** campaign runner that repeatedly verifies frozen results, decides from predetermined numerical conditions, runs the next reviewed diagnostic, and synchronizes GitHub/GOGIT after each step.

The first campaign is read-only and does not authorize training. Mode 2 provides the framework for future bounded training campaigns, but **a new certified training runner and independent explicit authorization are still required**. The existing V62 checkpoint and stop state are immutable.

## Initial architecture

- Orchestrator --> `tools/mini_kuzai_autopilot.py`, Python standard library
- Frozen pilot campaign --> `autopilot/campaigns/phase03-autopilot-v1.json`
- New diagnostic --> V68 tied output-head and logit-dominance GOGIT audit
- CPU unit tests --> `tests/test_mini_kuzai_autopilot.py` and `tests/test_phase03_v68_output_head_001.py`
- Optional service file --> `autopilot/systemd/mini-kuzai-autopilot.service`, **not installed or started**
- Local-only state --> `/root/Mini-Kuzai/runs/autopilot-v1/phase03-readonly-v1/state.json`
- Local-only audit journal --> `/root/Mini-Kuzai/runs/autopilot-v1/phase03-readonly-v1/events.jsonl`
- Local-only lock --> `/root/Mini-Kuzai/runs/autopilot-v1/phase03-readonly-v1/.autopilot.lock`

GitHub is **not an executable shell queue**. No downloaded manifest may introduce arbitrary commands or shell expressions. Runner keys are a hardcoded, reviewed catalog with pinned Git blob SHA. A changed runner fails closed.

## Autonomous five-step pilot

| Order | Stage | Decision |
| --- | --- | --- |
| 1 | Verify V65 GOGIT frequency diagnostic | Require PASS and 9170 lexical targets |
| 2 | Verify V66-A GOGIT confusion | Require PASS and 4294 merged targets |
| 3 | Verify V66-B GOGIT frequency strata | Require nonzero highly frequent merged targets and paired V66-A safety |
| 4 | Verify V67 GOGIT concentration | Require PASS and frozen VALIDATION inventory |
| 5 | Run V68 output-head diagnostic | **Only if** V67 predicts at most 8 distinct tokens and one token represents at least 70% of lexical argmax predictions |

Stage 5 is a real new CUDA/BF16 diagnostic and uses the reviewed `tools/run_v68_output_head_001_job.py`, which performs eight CPU tests, the GPU audit, GOGIT commit/push and remote report validation. A previously published valid report is reused. No training is invoked.

If the V67 branch condition does not hold, V68 is skipped and the campaign records the deterministic alternative. On any integrity error, drift, timeout or invalid GOGIT data, it stops.

## Git synchronization and run integrity

Before each stage --> validate `main`, exact GitHub origin, clean worktree, fetch `origin/main`, merge only fast-forward, verify V62 stopped checkpoint. Between stages the runner consumes already-published immutable GitHub numeric reports. Missing reports for a registered diagnostic stage trigger the **reviewed local runner**. That runner performs its own GOGIT publication and push.

Validation includes -->

- Exact GOGIT producer path and original producer SHA256 fingerprint
- Numeric-only metrics with no more than 30 fields per publication
- `SEMANTIC_VALIDATION_COMPLETE=0`, `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0`
- Explicit absence of BLIND access; V66-B also requires paired V66-A's verified no-BLIND report
- Conditions evaluated with a six-operator integer-only comparator, never dynamic Python evaluation
- Frozen stopped V62 run identity, checkpoint and absence of a training lock
- Reviewed runner Git blob pinning before execution
- Fixed campaign manifest SHA256 across an in-progress run
- Total campaign wall-time limit --> **7200 seconds**; individual diagnostic subprocess limited to at most 3600 seconds, with its underlying GOGIT limit unchanged at 300 seconds

State is written atomically with restrictive permissions. Every state replacement creates a unique timestamped local backup. The exclusive `flock` prevents simultaneous local orchestrators. On restart, existing GOGIT reports are checked again, so a successful push followed by an interrupted local process does not require republishing the same step.

The immutable reports belong on GitHub. Checkpoints, prompts, raw generated texts, local state, training authorizations and private corpus material stay outside the repository.

## Training - explicit authorization boundary

**TRAINING IN AUTOPILOT V1 IS NOT ENABLED.** The initial `TRAIN_RUNNERS` registry is deliberately empty. Even with `--allow-training`, AUTOPILOT will refuse a `train_window` stage without a new reviewed runner.

The file `autopilot/training-authorization-template.json` is documentation only and contains `approved=false`. It is **not** an authorization.

Before training could be enabled, a separate future version must -->

1. Implement a **new**, independently reviewed and versioned trainer whose own inner optimization loop enforces optimizer-step, token-exposure, wall-time, checkpoint and validation-stop budgets
2. Freeze and publish a **new** protocol containing the exact optimizer, objective, tokenization, training mix, checkpoint lineage and immutable SHA256 identities
3. Authorize its exact scope and bounds locally with an operator-created, root-owned **0600** authorization outside Git
4. Run AUTOPILOT with an explicit `--allow-training` invocation, and only with a pinned, reviewed trainer key
5. Require each training window to stop and verify its frozen validation metrics, checkpoint integrity and absence of BLIND before any next preauthorized window
6. Pause at every scope or budget boundary. A recommendation on GitHub is **not** training authorization

Do not reuse historical V62 authorization, resume `checkpoint-cycle-02.pt`, copy a private source into Git or run an unreviewed training CLI under this orchestrator.

## First local execution on fhc2

From the clean repository root, run -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests -p 'test_mini_kuzai_autopilot.py' -v && /root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests -p 'test_phase03_v68_output_head_001.py' -v && /root/Mini-Kuzai/.venv/bin/python tools/mini_kuzai_autopilot.py --check-only && /root/Mini-Kuzai/.venv/bin/python tools/mini_kuzai_autopilot.py
```

The command stops if any test or preflight fails. The first run of V68 is still pending actual local GPU verification. After GOGIT publication, respond `GOGIT` for review of the numerical result.

The optional systemd unit has **not** been deployed or enabled. Install only after the manual execution and journal have been verified. A systemd service does not itself authorize new experiments.

## Expansion strategy

New autonomous loops should be added by publishing and reviewing a new audit + runner, freezing its Git blob, then adding an explicitly bounded campaign stage and decision rules. Use a new campaign ID when modifying a running campaign. Never modify a running campaign's SHA256 and silently resume.

The intended future improvement is a single-process shared frozen corpus/GPU evaluation batch, avoiding repeated 98-second corpus preparation. This is an optimization opportunity, **not** an implemented cache in AUTOPILOT V1.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
