# Mini-Kuzai - gogit: automatic publication of PUBLIC audit metrics

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

The user then says "gogit" in ChatGPT. ChatGPT reads latest.json from public GitHub.

## Historical first-run verification (V42 - already completed)

The first successful automatic publication used:

```bash
python tools/gogit_public.py --step PHASE03-SMOLTALK-V42-AUTO-001 --audit tools/public-audits/smoltalk_v42_counts.py
```

Do not rerun this exact command: the historical STEP_ID already exists and the wrapper deliberately refuses to overwrite it.

Each completed run commits and pushes four **public numerical report** files when checks pass. No manual git add, commit or push is needed. Every new run requires a new, unique STEP_ID.

## Pause status - 2026-10-10

Phase 03 is paused after public external SmolTalk audit `PHASE03-SMOLTALK-V46-CREATIVE-001`. The current published report is under `reports/assistant-results/history/` and `latest.json`.

The exact next project step is V47: a local qualitative review of V46 candidates. No new audit, commit, push, tokenizer operation, or training run is scheduled while paused.

Resume only when explicitly requested by the user. New V47 publication, if authorized, must use a reviewed public SmolTalk-only audit script, an unused STEP_ID, and the same restricted numerical-output policy. The local review queue and full conversations stay outside Git.

See [Phase 03 pause checkpoint](../phases/MINI-KUZAI-PHASE-03-PAUSE-2026-10-10.md).

## Adding a future audit

Create and review a new file under tools/public-audits/, restricted to the external public SmolTalk dataset, then commit and push that SCRIPT first. Ensure the script prints only numerical aggregate counters with allowed keys after the results marker. Use a new PHASE03-SMOLTALK-... STEP_ID for the next run.

Running a normal Python script directly does NOT automatically publish its output. Use tools/gogit_public.py as the entrypoint. Arbitrary local stdout is never sent to GitHub.

## Privacy and scope

This publisher is intentionally ONLY for reports derived from public SmolTalk datasets. NEVER point a public audit at an exported private chat, private corpus, personal messages, private ChatGPT dataset, model logs carrying private dialogue, local credentials, or a combined public/private corpus.

The allowlist blocks unknown textual output and prevents accidental raw transcript publication. It cannot mathematically verify the origin of numbers in user-supplied audit code. Every new public-audits script must be reviewed before its first run.

Private-source reports stay local and must never be committed. No training is authorized by this publishing workflow.

## Failure modes

- Dirty worktree, unsynchronized main, unknown audit, or duplicate STEP_ID: blocked before the report files are modified.
- Unexpected or text-bearing results: blocked before report generation.
- Commit preparation failure: restores the original latest reports and removes provisional history files.
- Push failure after commit: leaves the checked local commit in place. Inspect Git and resolve without force. Do not rerun using the same STEP_ID.
- No GitHub Actions or background schedule is installed. Publication happens only when the wrapper is deliberately executed.
