# Mini-Kuzai - GOGIT: automatic publication of public Phase 03 audit metrics

The local working directory is /root/GitHub-Mini-Kuzai/Mini-Kuzai.
The existing Python environment can be activated from this directory:
source /root/Mini-Kuzai/.venv/bin/activate

## Purpose

One terminal command:
1. Checks Git main is clean and synchronized with origin/main.
2. Runs one committed, reviewed audit from tools/public-audits/.
3. Accepts only explicitly allowlisted KEY: nonnegative-integer results after the exact marker:
   ##### SECTION RESULTS FOR ASSISTANT ######
4. Backs up existing latest reports outside Git.
5. Writes reports/assistant-results/latest.txt, latest.json, and two history files.
6. Stages exactly those four paths, checks the diff, commits, pushes without force.
7. Verifies the remote HEAD and prints GOGIT: READY.

The user then says "gogit" in ChatGPT. ChatGPT reads `latest.json` and, when needed, immutable history records from public GitHub.

## Historical first-run verification (V42 - already completed)

The first successful automatic publication used:

```bash
python tools/gogit_public.py --step PHASE03-SMOLTALK-V42-AUTO-001 --audit tools/public-audits/smoltalk_v42_counts.py
```

Do not rerun this exact command: the historical STEP_ID already exists and the wrapper deliberately refuses to overwrite it.

Each completed run commits and pushes four **public numerical report** files when checks pass. No manual git add, commit or push is needed. Every new run requires a new, unique STEP_ID.

## Current status - 2026-10-25

GOGIT now serves multiple public Phase 03 audit families, not only external SmolTalk review.

Current public sources include:

- external public SmolTalk aggregate audits;
- Phase 03 designed VALIDATION aggregate audits;
- Phase 03 designed BLIND TEST aggregate audits.

The latest published audit state is the V55 global BLIND closure:

`PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001`

It confirms:

```text
TRAIN records                  : 107
TRAIN groups                   : 29
VALIDATION records             : 36
VALIDATION groups              : 18
SEMANTIC_VALIDATION_COMPLETE   : 1
BLIND TEST records frozen      : 36
BLIND behaviors frozen         : 18
cross-split exact collisions   : 0
TRAINING_AUTHORIZED            : 0
```

Global BLIND closure has been published and verified. The controlled corpus boundary is closed, while `TRAINING_AUTHORIZED` remains `0`.

Historical V42-V53 SmolTalk reports and V54 VALIDATION reports remain immutable records. Do not rewrite them or reuse a published STEP_ID.

Use `reports/assistant-results/latest.json` for the newest public numeric audit and `reports/assistant-results/history/` for immutable prior reports.

## Adding a future audit

Create and review a new file under `tools/public-audits/`, commit and push that script first, and ensure it operates only on public repository data appropriate for publication. The script must print only numerical aggregate counters with allowlisted keys after the results marker. Use a new unique `PHASE03-SMOLTALK-...` STEP_ID for each run.

Running a normal Python script directly does NOT automatically publish its output. Use tools/gogit_public.py as the entrypoint. Arbitrary local stdout is never sent to GitHub.

## Privacy and scope

GOGIT publishes only numeric aggregate reports from reviewed public-audit scripts committed under `tools/public-audits/`.

Allowed current use includes public SmolTalk analysis and aggregate integrity/freeze metrics derived from the public Phase 03 designed TRAIN / VALIDATION / BLIND repository artifacts.

Never point a public audit at:

- exported private chats;
- local-only private corpus material;
- personal messages;
- credentials or secrets;
- model logs containing private dialogue;
- any combined public/private source where private-derived metrics would be disclosed.

The allowlist blocks unknown textual output and prevents accidental raw transcript publication. It cannot mathematically verify the provenance of numbers produced by a reviewed audit script, so every new public-audit script must be reviewed before first execution.

Private-source reports stay local and must never be committed. GOGIT publication never authorizes training.

## Failure modes

- Dirty worktree, unsynchronized main, unknown audit, or duplicate STEP_ID: blocked before the report files are modified.
- Unexpected or text-bearing results: blocked before report generation.
- Commit preparation failure: restores the original latest reports and removes provisional history files.
- Push failure after commit: leaves the checked local commit in place. Inspect Git and resolve without force. Do not rerun using the same STEP_ID.
- No GitHub Actions or background schedule is installed. Publication happens only when the wrapper is deliberately executed.
