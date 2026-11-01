# Mini-Kuzai - GitHub Discussions publication workflow

Status --> **HISTORICAL POSTS TRANSFERRED / V74 START #5 PUBLISHED / LINKEDIN LIVE V74 CONFIRMED / TIMERS ACTIVE**

Publication target --> [Kusanagi8200/Mini-Kuzai Discussions](https://github.com/Kusanagi8200/Mini-Kuzai/discussions)

Category --> `Development Log` (`DIC_kwDOUI2cC84DKGl8`)

Source repository --> `Kusanagi8200/Mini-Kuzai` (`R_kgDOUI2cCw`)

## Historical introduction series

| Order | GitHub discussion title | Source | Published discussion |
| --- | --- | --- | --- |
| 01 | Mini-Kuzai - Why Build a Language Model From Scratch? | [Origins](history/01-origins.md) | [Discussion #2](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/2) |
| 02 | Mini-Kuzai - From a Transformer to a Developing AI Personality | [Learning design](history/02-learning-design.md) | [Discussion #3](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/3) |
| 03 | Mini-Kuzai - What the First Training Experiments Revealed | [Training results through V73](history/03-first-training-results.md) | [Discussion #4](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/4) |

The actual GitHub discussion titles use `Mini-Kuzai | 01`, `| 02` and `| 03` for predictable deduplication. Each body starts with the exact ASCII terminal-style header approved for the project. All contents are public and refer only to documented project milestones. Historical publication originally completed on `Kusanagi8200/KuzAI`, with the local `--publish` run reporting `CREATED=3` and `PUBLICATION=VERIFIED`. The operator subsequently transferred the three discussions to `Kusanagi8200/Mini-Kuzai`, selected category `Development Log`, and verified all three destinations using a GitHub GraphQL query. Their current links are recorded above. The central announcement remains [Mini-Kuzai - Live Dev Flow](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/1), in its own category.

## Local execution on fhc2

GitHub CLI `gh` authenticates the GraphQL requests using the operator's existing session. This workflow does not request, store or print a GitHub token or an OpenAI API key.

The historical publisher is [tools/github_discussions_history.py](../../tools/github_discussions_history.py). It is **read-only by default**.

First, run offline CPU tests and an online read-only inventory/preflight -->

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai
/root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests -p 'test_github_discussions_history.py' -v
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_history.py --dry-run
```

Historical posts already exist and were transferred. Do not rerun live publication unless recovering a genuinely missing historical discussion after manual review. For future work, continue with the dedicated Vxx workflow once implemented. The historical script retains the explicit write option -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_history.py --publish
```

The publisher checks repository identity, permission, category and every page of existing discussions; verifies content and the standard ASCII header; compares exact titles and Markdown bodies; refuses to overwrite a conflicting discussion; and rechecks GitHub after each creation. Re-running `--publish` should detect and skip identical discussions. If a discussion title exists with a different body, the script refuses to overwrite it; verify any body differences before attempting a historical recovery. No live historical publication is necessary after transfer.

This script **does not create issues or pull requests** and does not modify Mini-Kuzai model code, datasets, checkpoints or GOGIT reports.

## Future Vxx discussion workflow

The [Vxx publisher](../../tools/github_discussions_step.py) implements two explicit operations. It always targets `Kusanagi8200/Mini-Kuzai`, category `Development Log`. The [historical publisher](../../tools/github_discussions_history.py) remains separate and should not be used to start Vxx research.

An approved, committed start Markdown file is required before publishing a new research step. The script will not invent a scientific objective and does not automatically authorize training or BLIND access. The [V74 START source](steps/V74-start.md) was reviewed and committed. The operator explicitly requested `START-DEV-FLOW`; the fhc2 worker published [V74 Discussion #5](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5) and committed its [V74 START receipt](../../automation/dev-flow/receipts/V74-start.json). Do not publish the V74 START a second time.

### START Vxx - approved Markdown

Review the prepared `docs/discussions/steps/V74-start.md` on clean, synchronized main before authorizing publication. The filename and version must match the selected Vxx. Example structure, with research-specific text completed and validated before any publication -->

~~~~markdown
# Mini-Kuzai | V74 - Reviewed research objective

```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : V74
  STATUS   : EXPERIMENT STARTED
========================================================================
```

## Objective

Describe the approved scientific question, baseline, frozen data, method, scope, stop conditions and expected validation without claiming any unverified result.

## Protocol

Explain the exact authorized experiment and reproducibility safeguards. Keep private input data, credentials, unpublished conversations and protected evaluation content out of the post.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
~~~~

For a **future, not-yet-published step**, after the reviewed draft is committed, pull main on fhc2 and run a **read-only simulation**. Historical V74 example below is not a new instruction to republish -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_step.py --step V74 --action start
```

Only if the output reports `START=READY_TO_CREATE` or `START=EXISTS_IDENTICAL`, and the draft is correct, explicitly publish -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_step.py --step V74 --action start --publish
```

Both commands require a clean `main` that matches `origin/main`, including a remote SHA check. The existing category is scanned before writes. A changed title or body for an already-published Vxx blocks the operation rather than creating a duplicate.

### GOGIT Vxx - verified aggregate closure

After the GOGIT public audit is published, identify its immutable file under `reports/assistant-results/history/` with the exact `PHASE03-SMOLTALK-V74-...json` filename. The publisher verifies its step identity, public aggregate status, PASS metric, zero BLIND access, producer SHA256, committed-file integrity and absence of private conversation data. It constructs a **numerical evidence comment** automatically with a pinned Git commit URL, the verified metric table and explicit interpretation limits. It does not infer conversational performance from a numeric PASS.

Simulate with the report's full real filename (placeholder shown below) -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_step.py --step V74 --action close --report reports/assistant-results/history/PHASE03-SMOLTALK-V74-REPLACE-WITH-REAL-STEP-ID.json
```

Once a genuine V74 GOGIT report exists and the separate `FINAL-DEV-FLOW` authorization is received, append the comment **to that same discussion** -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_step.py --step V74 --action close --report reports/assistant-results/history/PHASE03-SMOLTALK-V74-REPLACE-WITH-REAL-STEP-ID.json --publish
```

An already-identical START or closure is skipped. A conflicting existing comment blocks publication. Closing a step with no corresponding verified START discussion is prohibited. The standalone CLI does not poll automatically, but the enabled `fhc2` DEV-FLOW timer polls explicit committed START/FINAL requests. No paid OpenAI API or automatic ChatGPT watcher is used.

Run the regression suite before using the new workflow -->

```bash
/root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests -p 'test_github_discussions_*.py' -v
```

Tests being present in GitHub is not proof that the local suite passed; record an actual PASS before live deployment.

The fixed ASCII header includes `PROJECT`, `PHASE`, `STEP` and `STATUS`. Research notes and evaluation claims remain subject to review; numerical GOGIT pass metrics do not demonstrate semantic learning or a coherent persona.

---

## KUZ-DIN Publisher bridge - production checkpoint 2026-11-01

The Github Discussions publisher is the upstream **research approval and evidence boundary**. The separate KUZ-DIN VPS performs signed webhook intake, JSON validation, SQLite PREPARE and guarded LinkedIn DELIVERY. This flow was verified with a genuine Mini-Kuzai V74 START; it was not simulated or rebuilt.

See the private [KUZ-DIN Publisher operational documentation](https://github.com/Kusanagi8200/KUZ-DIN/blob/main/docs/MINI-KUZAI-LINKEDIN-PUBLISHER.md) for source and runtime controls.

### Event mapping

| Mini-Kuzai event | GitHub action | KUZ-DIN behavior |
| --- | --- | --- |
| Approved V74+ START | Explicit `START-DEV-FLOW`, committed request, worker creates Discussion | Signed webhook; JSON and SQLite PREPARE; matching committed GitHub receipt; cutoff and LIVE check; guarded LinkedIn post |
| Verified V74+ GOGIT | Explicit `FINAL-DEV-FLOW` only after immutable numeric report; worker adds comment | Independent signed comment event and SQLite record; matching FINAL receipt and identical live safety gates |
| Historical #2, #3, #4 | Already published | No automatic replay |
| Unknown authors, edited or unrelated events | Not eligible | Ignored/rejected |
| Unreviewed scientific step | No authorized request | No GitHub or LinkedIn publication |

Inbound signature checks use HMAC-SHA256, strict approved author/category/headers and a source fingerprint. Accepted events are written as `0600` JSON records. The formatter has a **2800-character cap** and never silently truncates research findings. The SQLite journal transitions `PREPARED -> IN_FLIGHT -> PUBLISHED`, preserves uncertain outcomes, and prevents duplicates through the event ID key.

### Verified real START V74

| Evidence | Result |
| --- | --- |
| Explicit START | User requested `START-DEV-FLOW` |
| GitHub Discussion | [V74 START #5](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5) |
| GitHub receipt | [`V74-start.json`](../../automation/dev-flow/receipts/V74-start.json), `PUBLISHED` |
| VPS event | `start-V74-d5` signed webhook, unique JSON |
| PREPARE | SQLite `PREPARED`, exactly one eligible event |
| Final preflight | 18 checks PASS; no uncertain publications; 1654 characters |
| LIVE gate | `KUZDIN_PUBLISHER_LIVE_ENABLED=YES` with cutoff `2026-11-01T13:38:23+00:00` |
| LinkedIn delivery | One controlled invocation, systemd exit 0 |
| Final SQLite | `PUBLISHED`, no pending or duplicate |
| LinkedIn URN | `urn:li:share:7522669773583872000` |
| Human confirmation | Public post visibly confirmed on personal LinkedIn profile |
| Timer | `kuz-din-publisher-delivery.timer` active/enabled after first post |

The immediate timer snapshot initially showed `NEXT=-`, but a subsequent check verified LAST `2026-11-01 14:51:36 UTC`, NEXT `2026-11-01 14:52:37 UTC`, six successful `STATE=IDLE` cycles and no additional queued post. Timer recurrence is confirmed.

### Pending work and scientific boundaries

- Timer schedule and six clean idle DELIVERY cycles verified; maintain routine monitoring
- Validate the first real FINAL-DEV-FLOW after V74 has a genuine, fully verified immutable GOGIT
- Monitor OAuth validity and never blindly retry an `IN_FLIGHT` or ambiguous LinkedIn publication
- Avoid synchronizing unreviewed VPS source changes from GitHub; the documentation changes are not runtime deployments
- Preserve V62 frozen checkpoint, zero new training and BLIND TEST closure

The V74 START was completed; **do not issue another V74 START request**. The scientific V74 protocol, tests, numeric audit and GOGIT remain outstanding. A GitHub/LinkedIn publication status is not an AI training result or validation of model quality.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
