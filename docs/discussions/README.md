# Mini-Kuzai - GitHub Discussions publication workflow

Status --> **THREE HISTORICAL POSTS TRANSFERRED / DEV-FLOW TIMERS ACTIVE / V74 DRAFT NOT STARTED / LINKEDIN LIVE DISABLED**

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

An approved, committed start Markdown file is required before publishing a new research step. The script will not invent a scientific objective and does not automatically authorize training or BLIND access. The [V74 START draft](steps/V74-start.md) is now prepared for review. No V74 discussion or explicit DEV-FLOW START request has been created.

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

After the reviewed draft is committed, pull main on fhc2 and run the **read-only simulation** -->

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

Once validated and deliberately authorized, append the comment **to that same discussion** -->

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

## KUZ-DIN Publisher bridge - deployment checkpoint 2026-11-01

The Discussions publisher is the **upstream research publication source** for a separate, optional LinkedIn distribution pipeline. A GitHub Discussion is not a LinkedIn post. The cross-posting integration runs on the KUZ-DIN VPS and has **not** been authorized to publish to LinkedIn.

Read the [KUZ-DIN Publisher operational documentation](https://github.com/Kusanagi8200/KUZ-DIN/blob/main/docs/MINI-KUZAI-LINKEDIN-PUBLISHER.md) for system architecture, validation coverage, security controls and remaining work. KUZ-DIN is a private repository, so access to that document depends on repository permissions.

### Event mapping and acceptance rules

| Mini-Kuzai event | GitHub action | KUZ-DIN result today |
| --- | --- | --- |
| Approved V74+ START | `--action start --publish` creates a `Development Log` Discussion | Signed `discussion.created` webhook can save private JSON and prepare a LinkedIn candidate |
| Verified V74+ GOGIT | `--action close --report ... --publish` adds a comment to the same Discussion | Signed `discussion_comment.created` webhook can save a separate JSON candidate and prepare a separate SQLite record |
| Historical #2, #3, #4 | Already published | Not automatically replayed |
| Edited, unrelated, outside-category or before V74 | Not eligible | Ignored |
| New research not explicitly authorized | No reviewed START or verified GOGIT | Must not be posted |

KUZ-DIN's webhook requires the exact `Mini-Kuzai | Vxx - ...` title, the approved 72-character ASCII header, matching STEP/STATUS and the project footer. Only `Kusanagi8200` is authorized as event sender and as discussion author, plus comment author for GOGIT. Every inbound request is checked with a shared-secret HMAC-SHA256 signature. Accepted payloads are written as `0600` JSON files, deduplicated by event identity and source SHA256.

The queued LinkedIn formatter preserves the research source URL, status and footer, with a **2800-character cap**. Oversized content is blocked pending an explicitly reviewed excerpt tied to the original content fingerprint. **No silent truncation of scientific findings.**

The `kuz-din-publisher-queue.timer` runs approximately every minute under a dedicated `kuz-din` service identity. Its configured `--prepare` mode writes only eligible events to an SQLite journal with the initial state `PREPARED`. It never calls LinkedIn. Later states `IN_FLIGHT` and `PUBLISHED` are covered by offline tests, not active production posting.

### Evidence and current limits

- Internal signed FastAPI START / GOGIT tests --> PASS
- Synthetic webhook to private JSON and temporary SQLite --> PASS
- Public HTTPS signed ping and rejection of foreign authors --> PASS
- Real GitHub webhook `ping` delivered to KUZ-DIN --> HTTP 200, 2026-10-31 23:29:54 UTC
- Real GitHub START / GOGIT through KUZ-DIN --> **not yet verified**
- An introductory V5 LinkedIn post was separately confirmed (HTTP 201) but no DEV-FLOW GitHub-event-to-LinkedIn delivery has been verified; the automated live gate remains disabled
- Automatic ChatGPT / OpenAI API watcher --> **not configured**
- Mini-Kuzai scientific status --> **V73 last verified GOGIT, V74 protocol and START draft prepared but not authorized or published**

The new Publisher OAuth application uses `openid profile w_member_social` and stores its token encrypted outside Git. A read-only LinkedIn check confirmed `GET /v2/userinfo` HTTP 200 and an OIDC subject match, while `GET /v2/me` returned HTTP 403. The final author URN compatibility must be checked during an explicitly approved live test, not inferred from offline mocks.

### Non-negotiable separation

Publishing a reviewed GitHub START or GOGIT requires the explicit `--publish` flag in the Mini-Kuzai project. This may trigger a **webhook capture**, not a LinkedIn post. Enabling LinkedIn publication is a separate KUZ-DIN deployment decision requiring its own audit and authorization.

No automatic experiment, new training, BLIND TEST access, checkpoint alteration, GOGIT audit or LinkedIn publication is authorized by installing this bridge or editing these documents.

---

## DEV-FLOW delivery checkpoint - 2026-11-01

The [full two-host verification and resumption record](../DEV-FLOW-REPRISE-2026-11-01.md) supersedes earlier deployment snapshots above.

- fhc2 DEV-FLOW worker --> enabled local timer, clean main, no pending START/FINAL request, repeated IDLE
- Real repository webhook --> active ID `705780264`, JSON, SSL verification enabled, both Discussion event types subscribed
- KUZ-DIN public signed ping --> HTTP 200, `ping_ok`, no event created
- Isolated START capture --> HTTP 202, duplicate HTTP 200, invalid HMAC HTTP 401
- Isolated PREPARE and SQLite --> first CREATED/PREPARED, second EXISTS/PREPARED
- Delivery --> 36 offline publisher tests PASS, START and FINAL receipt simulations PASS
- OAuth token --> locally valid at audit, encrypted file `0600`, encryption key `0640`
- Systemd PREPARE and DELIVERY timers --> active, delivery repeatedly `LIVE_DISABLED`
- Activation cutoff --> `2026-11-01T13:38:23+00:00`, only events received on/after are eligible
- Production event directory and SQLite --> not created before first real event
- Live authorization --> **`KUZDIN_PUBLISHER_LIVE_ENABLED=NO`**
- V74 --> [scientific protocol](../../phases/MINI-KUZAI-PHASE-03-V74-FREQUENCY-PRIOR-CONTROL-001.md) and [unpublished START draft](steps/V74-start.md) committed, no START request

Only an explicit user `START-DEV-FLOW` followed by a committed `automation/dev-flow/requests/V74-start.json` can make the fhc2 worker publish the reviewed GitHub Discussion. The resulting receipt is independently required by KUZ-DIN. `FINAL-DEV-FLOW` additionally needs verified real V74 GOGIT. Documentation alone authorizes neither action.

**The complete automation is not production-live.** The first authentic signed GitHub START/FINAL event and a controlled authorized LinkedIn delivery remain to be tested. Earlier V5 introduction confirmation was a separate manual publication, not a DEV-FLOW pipeline test.


---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
