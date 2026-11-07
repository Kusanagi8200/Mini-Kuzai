# Mini-Kuzai - GOGIT --> automatic publication of public Phase 03 audit metrics

The local working directory is /root/GitHub-Mini-Kuzai/Mini-Kuzai.
The existing Python environment can be activated from this directory -->
source /root/Mini-Kuzai/.venv/bin/activate

## Purpose

One terminal command -->
1. Checks Git main is clean and synchronized with origin/main.
2. Runs one committed, reviewed audit from tools/public-audits/.
3. Accepts only explicitly allowlisted KEY --> nonnegative-integer results after the exact marker -->
   ##### SECTION RESULTS FOR ASSISTANT ######
4. Backs up existing latest reports outside Git.
5. Writes reports/assistant-results/latest.txt, latest.json, and two history files.
6. Stages exactly those four paths, checks the diff, commits, pushes without force.
7. Verifies the remote HEAD and prints GOGIT --> READY.

The user then says "gogit" in ChatGPT. ChatGPT reads `latest.json` and, when needed, immutable history records from public GitHub.

## Historical first-run verification (V42 - already completed)

The first successful automatic publication used -->

```bash
python tools/gogit_public.py --step PHASE03-SMOLTALK-V42-AUTO-001 --audit tools/public-audits/smoltalk_v42_counts.py
```

Do not rerun this exact command --> the historical STEP_ID already exists and the wrapper deliberately refuses to overwrite it.

Each completed run commits and pushes four **public numerical report** files when checks pass. No manual git add, commit or push is needed. Every new run requires a new, unique STEP_ID.

## Current status - 2026-11-07

GOGIT publishes public, allowlisted numerical audit reports after local verification. The latest **scientific** immutable step is -->

`PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001`

The V76 CPU-only report `PHASE03-SMOLTALK-V76-CPU-PREFLIGHT-001` verified implementation and safety gates before the separately authorized GPU run.

Verified state --> V76 scientific GOGIT, GitHub FINAL receipt and KUZ-DIN LinkedIn delivery are complete. V76 is CLOSED. V77 START is published in Discussion #8 with a committed receipt; implementation and CPU-only preflight are prepared. GPU, training and BLIND access remain unauthorized.

Recent completed stages -->

| Step | Result |
| --- | --- |
| V62 TRAIN RUN 001 | Historical controlled training stopped at cycle 2, 69 optimizer steps |
| V63 DECODING ROBUSTNESS 001 | Eight seeds, 41/48 EOS with top-k/top-p |
| V63 AUTOMATIC LANGUAGE SCREEN 001 | 24 generated samples, 10/24 rule-flagged, no human scores |
| V64 RUNTIME TRACE 001 | Bounded 155-second profiler completed and published despite internal timeout |
| V64 LANGUAGE LEARNING DIAGNOSTIC 001 | Six CPU tests passed; original GOGIT process exceeded 300 seconds; **no** successful report |
| V64 LANGUAGE LEARNING DIAGNOSTIC 002 | Optimized GPU diagnostic published, VALIDATION CE 4.733 / top-1 29.20% |
| V65 TOKEN FREQUENCY DIAGNOSTIC 001 | Frozen token-frequency audit, raw-byte 52.00% vs BPE 3.27% frequent top-1 |
| V66 TOKEN PREDICTION BIAS original | Eight unit tests passed but **57 metrics exceeded the 30-field GOGIT cap**; no successful original report |
| V66 TOKEN PREDICTION BIAS Part A | 30 numeric fields published, family confusion and full-vocabulary softmax mass |
| V66 TOKEN PREDICTION BIAS Part B | 30 numeric fields published, detailed token-frequency accuracy and NLL |
| V67 OUTPUT CONCENTRATION 001 | Executed and published, 4 distinct argmax token IDs / 606 distinct gold IDs, dominant share 72.58% |
| V68 OUTPUT HEAD 001 | Published after PAD zero-assumption correction, selected norm 0.360 vs gold norm 0.293, PAD norm 0.182 |
| V69 OUTPUT NORM COUNTERFACTUAL 001 | Verified: BASE CE 4.733, HALF 4.892, FULL 5.048; 4/4/7 predicted IDs, BPE top-5 improves modestly |
| V70 PRECISION CONTROL 001 | **GPU/GOGIT verified**; BF16 original CE 4.733, FP32 original CE 4.732, FULL CE 5.048, no new training or BLIND access |
| V71 OUTPUT DOMINANCE ATTRIBUTION 001 | **GPU/GOGIT verified**; 275 of 9170 lexical top-1 predictions changed (3.00%), 5 to 7 distinct predicted IDs, CE worsened 4.732 to 5.048 |
| V72 HIDDEN-STATE ANISOTROPY 001 | **GPU/GOGIT verified**; centered PC1 82.88%, effective rank 1.44 and 2889/9170 predictions changed under mean-centering |
| V73 PRINCIPAL AXIS ATTRIBUTION 001 | **GPU/GOGIT verified**; CENTER 2832 correct / 15 distinct IDs, MINUS_PC1 1124 / 522, MINUS_PC12 818 / 715, PC1_ONLY 2455 / 2 |
| V74 FREQUENCY PRIOR CORE + STRATA | **Dual GOGIT verified**; TRAIN unigram 2535/9170, PC1_ONLY 2455/9170, 2449 shared correct predictions |
| V75 CPU PREFLIGHT 001 | **CPU/GOGIT verified**; 13 tests, exact 30-field schema, no GPU/training/BLIND |
| V75 TRAIN-FITTED GEOMETRY TRANSFER 001 | **GPU/GOGIT verified**; TRAIN/VALIDATION PC1 abs cosine 99.95%, TRAIN_PC1_ONLY 2457/9170 with 2 IDs, TRAIN_MINUS_PC1 611/9170 with 663 IDs |
| V75 FINAL PREFLIGHT 001 | **CPU/read-only GOGIT verified**; report, START receipt and Discussion #6 validated; publication disabled during preflight; later FINAL completed separately |
| V76 CPU PREFLIGHT 001 | **CPU/GOGIT verified**; 15 tests, exact 30-field schema, dependency pins, zero GPU execution/training/BLIND |
| V76 FREQUENCY-RESIDUALIZED PC1 CONTROL 001 | **GPU/GOGIT verified**; frequency R2 7.75%, residual energy 92.25%, residual 2594/9170 correct with only 2 predicted IDs |

GOGIT's process execution budget remains **300 seconds**, and the parser rejects more than **30 metrics per publication**. V66 therefore published two validated 30-field reports with three repeated safety fields, preserving 57 unique fields. V67 through V73 have each published exactly 30 allowlisted numerical metrics; no training or semantic validation follows from these read-only diagnostics. The 155-second V64 stage profiler is a separate worker with its own internal limit, not a change to GOGIT.

Read `reports/assistant-results/latest.json` for the latest published numeric report and `reports/assistant-results/history/` for immutable previous steps. Never overwrite an existing STEP_ID.

A previous `TRAINING_AUTHORIZED=1` in V62 historical run reports is **not** an authorization for a new run. The V64 diagnostic reports `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0`, `SEMANTIC_VALIDATION_COMPLETE=0`. The latter flag expressly states that the numerical learning diagnostic is not human semantic validation.

See [verified V73 GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.json) and the [V73 research record](../phases/MINI-KUZAI-PHASE-03-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.md). The [pinned V73 runner](run_v73_principal_axis_attribution_001_job.py) executed independently of AUTOPILOT. Its result does not authorize any training or access to BLIND TEST.

## ChatGPT review workflow and interactive-shell safety

For operator-driven steps, successful aggregate results should be published through GOGIT and then reviewed from GitHub. The normal interaction is -->

```text
run reviewed local command
  -> GOGIT commits/pushes numeric report
  -> operator writes: GOGIT
  -> ChatGPT reads reports/assistant-results/latest.json or the immutable history report
```

Do not copy successful terminal output into ChatGPT when a GOGIT report was published. Terminal copy/paste is reserved for a local failure that prevented GOGIT publication and therefore left no GitHub evidence to inspect.

Commands that enable strict Bash options must never alter the parent interactive shell. Use a subshell -->

```bash
( set -euo pipefail; command1; command2 )
```

Do not issue a top-level `set -u`, `set -e` or `exit` in an interactive SSH shell used by the operator. This prevents prompt plugins or PS1 helpers with unset variables from terminating the session after the command finishes.

### V75 CPU preflight GOGIT

The CPU-only V75 implementation/safety preflight has its own immutable STEP_ID -->

`PHASE03-SMOLTALK-V75-CPU-PREFLIGHT-001`

Reviewed producer -->

`tools/public-audits/phase03_v75_cpu_preflight_001.py`

It runs the frozen V75 CPU regression suite and publishes only aggregate numeric status. It explicitly reports zero GPU execution, zero BLIND access and zero training authorization/start. It does not execute the scientific V75 GPU study.

Run it from a synchronized repository with -->

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai && ( set -euo pipefail; git pull --ff-only origin main; /root/Mini-Kuzai/.venv/bin/python tools/gogit_public.py --step PHASE03-SMOLTALK-V75-CPU-PREFLIGHT-001 --audit tools/public-audits/phase03_v75_cpu_preflight_001.py )
```

After a successful publication, the operator only needs to request `GOGIT` in ChatGPT.

## V75 FINAL DEV-FLOW preflight

After the verified V75 scientific GOGIT, FINAL preparation uses a separate read-only GOGIT preflight.

STEP_ID --> `PHASE03-SMOLTALK-V75-FINAL-PREFLIGHT-001`

Producer --> `tools/public-audits/phase03_v75_final_preflight_001.py`

The audit validates the immutable 30-field V75 scientific report, the published V75 START receipt, the existing Discussion #6 and a `github_discussions_step.py` close dry-run. It requires `GOGIT_CLOSURE=READY_TO_COMMENT` and `PUBLICATION=DISABLED`.

It explicitly requires both `automation/dev-flow/requests/V75-final.json` and `automation/dev-flow/receipts/V75-final.json` to be absent. It never supplies `--publish` and therefore cannot create the FINAL comment.

Run from synchronized `main` -->

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai && ( set -euo pipefail; git fetch --no-tags origin main; git pull --ff-only origin main; test -z "$(git status --porcelain)"; /root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests -p 'test_phase03_v75_final_preflight_001.py' -v >/dev/null; /root/Mini-Kuzai/.venv/bin/python tools/gogit_public.py --step PHASE03-SMOLTALK-V75-FINAL-PREFLIGHT-001 --audit tools/public-audits/phase03_v75_final_preflight_001.py )
```

After successful publication, the operator requests `GOGIT` in ChatGPT. A PASS result means only that FINAL is technically ready for a later explicit authorization. It does not authorize or publish FINAL.

## V76 closed scientific audit and V77 next protocol

V76 is closed.

Scientific STEP_ID -->

`PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001`

CPU preflight STEP_ID -->

`PHASE03-SMOLTALK-V76-CPU-PREFLIGHT-001`

Verified V76 findings -->

- axis-frequency absolute correlation --> 27.85%
- frequency OLS R2 --> 7.75%
- residual-energy share --> 92.25%
- residual correct --> 2594 / 9170
- residual distinct predicted IDs --> 2
- residual dominant share --> 70.43%
- no training
- no BLIND access

The next protocol is [V77 Residual Context-Order Sensitivity Control 001](../phases/MINI-KUZAI-PHASE-03-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001.md).

V77 freezes an exact 30-field scientific schema around a deterministic `REVERSE_HISTORY_KEEP_LAST` counterfactual. The transform preserves target, prefix length, token multiset, BOS and immediate preceding token while reversing only earlier context order.

The [V77 START source](../docs/discussions/steps/V77-start.md) is published in [Discussion #8](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/8), with a committed [START receipt](../automation/dev-flow/receipts/V77-start.json).

V77 implementation and CPU-only preflight are now prepared. START does not authorize scientific GPU execution, training, optimizer steps, checkpoint writes or BLIND access.

## Adding a future audit

Create and review a new file under `tools/public-audits/`, commit and push that script first. Audit inputs may include frozen public corpus material or private local inference artifacts **only where the reviewed protocol authorizes numeric-only aggregates and explicitly prohibits raw text, identity and secrets from publication**. The GOGIT mechanism does not authorize training or disclose the underlying data. The script must print only numerical aggregate counters with allowlisted keys after the results marker. Use a new unique `PHASE03-SMOLTALK-...` STEP_ID for each run.

Running a normal Python script directly does NOT automatically publish its output. Use tools/gogit_public.py as the entrypoint. Arbitrary local stdout is never sent to GitHub.

## Privacy and scope

GOGIT publishes only numeric aggregate reports from reviewed public-audit scripts committed under `tools/public-audits/`.

Allowed use includes approved SmolTalk/controlled-corpus integrity audits and aggregate metrics from frozen checkpoints, TRAIN/VALIDATION evaluation and locally stored generation probes. V63/V64 outputs publish only reviewed aggregate numeric metrics, never raw prompts or private generated text. The frozen BLIND TEST must not be accessed by new V63/V64 inference audits.

Never point a public audit at -->

- exported private chats
- local-only private corpus material
- personal messages
- credentials or secrets
- model logs containing private dialogue
- any mixed public/private source where sensitive information, identity or text could be inferred from published aggregates

The allowlist blocks unknown textual output and prevents accidental raw transcript publication. It cannot mathematically verify the provenance of numbers produced by a reviewed audit script, so every new public-audit script must be reviewed before first execution.

Private-source reports stay local and must never be committed. GOGIT publication never authorizes training.

## Failure modes

- Dirty worktree, unsynchronized main, unknown audit, or duplicate STEP_ID --> blocked before the report files are modified.
- Unexpected or text-bearing results --> blocked before report generation.
- Commit preparation failure --> restores the original latest reports and removes provisional history files.
- Push failure after commit --> leaves the checked local commit in place. Inspect Git and resolve without force. Do not rerun using the same STEP_ID.
- No GitHub Actions or background schedule is installed. Publication happens only when the wrapper is deliberately executed.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
