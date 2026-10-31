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

## Current status - 2026-10-31

GOGIT publishes public, allowlisted numerical audit reports after local verification. The latest completed immutable step is -->

`PHASE03-SMOLTALK-V64-LANGUAGE-LEARNING-DIAGNOSTIC-002`

Verified commit --> [`9d8dcb62b6e9`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/9d8dcb62b6e9bc3826f95eb93953c95c28835132)

Recent completed stages -->

| Step | Result |
| --- | --- |
| V62 TRAIN RUN 001 | Historical controlled training stopped at cycle 2, 69 optimizer steps |
| V63 DECODING ROBUSTNESS 001 | Eight seeds, 41/48 EOS with top-k/top-p |
| V63 AUTOMATIC LANGUAGE SCREEN 001 | 24 generated samples, 10/24 rule-flagged, no human scores |
| V64 RUNTIME TRACE 001 | Bounded 155-second profiler completed and published despite internal timeout |
| V64 LANGUAGE LEARNING DIAGNOSTIC 001 | Six CPU tests passed; original GOGIT process exceeded 300 seconds; **no** successful report |
| V64 LANGUAGE LEARNING DIAGNOSTIC 002 | Optimized GPU diagnostic published, VALIDATION CE 4.733 / top-1 29.20% |

GOGIT's process execution budget remains **300 seconds**. The 155-second V64 stage profiler is a separate worker with its own internal limit, not a change to GOGIT.

Read `reports/assistant-results/latest.json` for the latest published numeric report and `reports/assistant-results/history/` for immutable previous steps. Never overwrite an existing STEP_ID.

A previous `TRAINING_AUTHORIZED=1` in V62 historical run reports is **not** an authorization for a new run. The V64 diagnostic reports `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0`, `SEMANTIC_VALIDATION_COMPLETE=0`. The latter flag expressly states that the numerical learning diagnostic is not human semantic validation.

See [Phase 03 V64 closure and V65 readiness](../phases/MINI-KUZAI-PHASE-03-V64-CLOSURE-V65-READINESS-2026-10-31.md) for evidence and current decision.

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
