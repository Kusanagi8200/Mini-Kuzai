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

## Current status - 2026-11-14

GOGIT publishes public, allowlisted numerical audit reports after local verification.

The latest **scientific** immutable step is -->

`PHASE03-SMOLTALK-V83-POST-V81-REFITTED-COORDINATE-CONTEXT-ORDER-001`

Primary report -->

`reports/assistant-results/history/PHASE03-SMOLTALK-V83-POST-V81-REFITTED-COORDINATE-CONTEXT-ORDER-001.json`

Verified V83 closure -->

- report --> PASS
- training started --> 0
- final optimizer steps --> 136
- final exposure tokens --> 1,181,302
- validation lexical positions --> 9,170
- perturbed prefixes --> 9,062
- inherited-coordinate prediction/sign changes --> 38 / 38
- refitted-coordinate prediction/sign changes --> 34 / 34
- refitted PC1 variance share --> 61.26%
- inherited/refitted PC1 absolute cosine --> 96.45%
- inherited/refitted residual-profile absolute cosine --> 86.58%
- further training authorized --> 0
- BLIND access --> 0
- semantic validation complete --> 0
- semantic claim --> 0

Publication closure -->

- GitHub FINAL --> Discussion #15 comment #19617158
- committed FINAL receipt --> `automation/dev-flow/receipts/V83-final.json`
- YouTube FINAL --> PUBLIC / `iNYNmxaNKbQ`
- LinkedIn native media --> `urn:li:ugcPost:7527431180539867136`
- LinkedIn video asset --> `urn:li:video:D4E10AQHOFgNRwxHSAA`
- GitHub media fallback --> Discussion #15 comment #19617184
- automatic closure GOGIT --> `V83-FINAL-DEV-FLOW-AUTO-VERIFY-001` / PASS

Recent completed scientific stages -->

| Step | Result |
| --- | --- |
| V74 FREQUENCY PRIOR CORE + STRATA | Dual GOGIT verified; TRAIN unigram 2535/9170, PC1_ONLY 2455/9170 |
| V75 TRAIN-FITTED GEOMETRY TRANSFER | TRAIN/VALIDATION PC1 absolute cosine 99.95% |
| V76 FREQUENCY-RESIDUALIZED PC1 CONTROL | Frequency R2 7.75%, residual energy 92.25%, residual 2594/9170 correct with 2 IDs |
| V77 RESIDUAL CONTEXT-ORDER SENSITIVITY | 5/9170 top-1 changes; both paths 2594/9170 correct |
| V78 IDENTICAL-CONTEXT REBATCHING CONTROL | 0/9170 prediction changes and 0 alpha-sign changes |
| V79 SAME-PATH CONTEXT-ORDER CONTROL | Exact five V77 prediction/sign changes reproduced through same batch-32 path |
| V80 DECISION-BOUNDARY PROXIMITY CONTROL | All five changed positions outside frozen 1e-3 near-zero band |
| V81 BOUNDED V62 CONTINUATION | Closed at 136 steps / 1,181,302 exposure tokens; best validation loss 4.030447 |
| V82 POST-CONTINUATION CONTEXT-ORDER REPLICATION | Read-only control; prediction/sign changes increased from 5 to 38 across the frozen diagnostic |
| V83 POST-V81 REFITTED-COORDINATE CONTROL | Read-only TRAIN-only coordinate refit on the same final checkpoint; prediction/sign changes persist at 34 / 34 |

V83 is scientifically and operationally closed. V84 has not started. No further training is authorized and BLIND remains closed. `START-DEV-FLOW V84` must be explicitly requested before V84 scientific work begins.

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

## V77 closed scientific audit and V78 next protocol

V77 is closed.

Scientific STEP_ID -->

`PHASE03-SMOLTALK-V77-RESIDUAL-CONTEXT-ORDER-SENSITIVITY-001`

CPU preflight STEP_ID -->

`PHASE03-SMOLTALK-V77-CPU-PREFLIGHT-001`

Verified V77 findings -->

- FULL correct --> 2594 / 9170
- REVERSE correct --> 2594 / 9170
- top-1 prediction changes --> 5 / 9170
- alpha sign changes --> 5 / 9170
- absolute alpha correlation --> 99.99%
- alpha delta above 1e-7 --> 9123 / 9170
- actually perturbed prefixes --> 9062 / 9170
- no training
- no BLIND access

The next protocol is [V78 Identical-Context Rebatching Numerical Control 001](../phases/MINI-KUZAI-PHASE-03-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.md).

V78 evaluates the exact same logical prefixes through the V77 FULL_CONTEXT batch-4 path and prefix/rebatch batch-32 path. It freezes a 30-field schema measuring prediction, sign and alpha differences at 1e-7, 1e-6 and 1e-5 thresholds.

The [V78 START source](../docs/discussions/steps/V78-start.md) is published in [Discussion #9](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/9), with a committed [START receipt](../automation/dev-flow/receipts/V78-start.json).

V78 START authorizes implementation and CPU-only preflight only. Scientific GPU execution, training, optimizer steps, checkpoint writes and BLIND access remain prohibited.

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
