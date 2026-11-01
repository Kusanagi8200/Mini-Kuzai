# Mini-Kuzai - DEV-FLOW checkpoint and V74 resumption

Date --> 2026-11-01

Status --> **V74 START PUBLISHED ON GITHUB AND LINKEDIN / LIVE DELIVERY ACTIVE / V74 DIAGNOSTICS PENDING**

## Architecture

```text
Explicit user START-DEV-FLOW / FINAL-DEV-FLOW in ChatGPT
   -> GitHub main committed automation/dev-flow/requests/Vxx-start|final.json
   -> fhc2 mini-kuzai-dev-flow.timer (30-second configuration)
   -> GitHub Discussions Development Log START / GOGIT comment
   -> signed GitHub webhook to https://link.kuzai.org/webhooks/github/mini-kuzai
   -> VPS KUZ-DIN private JSON events
   -> PREPARE timer -> SQLite PREPARED
   -> delivery timer -> check matching GitHub DEV-FLOW receipt and cutoff
   -> guarded LinkedIn POST if independent LIVE gate and DEV-FLOW receipt match
   -> SQLite PUBLISHED (or IN_FLIGHT for ambiguous provider outcome)
```

No background ChatGPT watcher, OpenAI API key or paid OpenAI API is used. The local worker polls GitHub after explicit requests and remains inert otherwise.

## Verified deployment gates

| Component | Verified observation |
| --- | --- |
| Research | V73 latest verified GOGIT, V62 frozen after 69 optimizer steps / 597982 exposed tokens |
| fhc2 | `mini-kuzai-dev-flow.timer` active and enabled, worker repeatedly IDLE, GitHub actor `Kusanagi8200`, clean worktree |
| Request queue | START V74 committed as `automation/dev-flow/requests/V74-start.json`, processed by fhc2 worker; receipt committed as `automation/dev-flow/receipts/V74-start.json` |
| GitHub webhook | One matching active hook, ID `705780264`, `discussion` and `discussion_comment`, JSON, SSL verification enabled |
| VPS signed ping | HTTP 200 / `ping_ok`, no events recorded |
| Synthetic START integration | HTTP 202 recorded, duplicate HTTP 200, invalid HMAC HTTP 401 |
| Synthetic SQLite | Event PREPARED then repeat preparation EXISTS/PREPARED, idempotent |
| Publisher regression | 36 of 36 offline tests PASS, START and FINAL receipt mock checks PASS |
| KUZ-DIN service | PREPARE and DELIVERY timers active, delivery one-shot repeatedly `LIVE_DISABLED` |
| Token files | Encrypted token `0600` and key `0640`; local token validation PASS at audit time |
| Production event directory / SQLite | Exactly one V74 START event/row verified, after one real delivery status `PUBLISHED`, no pending/IN_FLIGHT rows |
| Activation cutoff | `2026-11-01T13:38:23+00:00` verified in systemd drop-in |
| LinkedIn delivery | `KUZDIN_PUBLISHER_LIVE_ENABLED=YES`, first real START V74 sent once and visually confirmed; URN `urn:li:share:7522669773583872000` |
| LinkedIn historical introduction | One standalone V5 post previously confirmed with HTTP 201, not evidence of automated DEV-FLOW delivery |

## First production START / LinkedIn delivery - VERIFIED

- Explicit user order --> `START-DEV-FLOW` for V74
- GitHub request --> [`V74-start.json`](../automation/dev-flow/requests/V74-start.json), commit `70384c5cfdbb091cd210d6b19e33647f5aa43ca3`
- GitHub discussion --> [Mini-Kuzai V74 START #5](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5), published 2026-11-01 at 14:18:04 UTC
- GitHub receipt --> [`automation/dev-flow/receipts/V74-start.json`](../automation/dev-flow/receipts/V74-start.json), status `PUBLISHED`, commit `13599845831ed66f213690bda341d7cc79299ada`
- VPS signed webhook --> real START recorded exactly once as `start-V74-d5`
- PREPARE --> one SQLite event, `PREPARED`, no blocked entries
- Final production preflight --> **18 checks PASS**, only one post eligible; text 1654 characters; no previous `IN_FLIGHT`
- Production cutoff --> `2026-11-01T13:38:23+00:00` retained
- LIVE activation --> `KUZDIN_PUBLISHER_LIVE_ENABLED=YES`; timer stopped for controlled first send
- VPS timestamped activation backup --> `/root/kuz-din-linkedin-live-20261101T144224Z-IDxsWG`
- Controlled delivery --> `SYSTEMD_START_EXIT=0`, `Result=success`, `ExecMainStatus=0`
- SQLite --> `start-V74-d5` status `PUBLISHED`, zero pending/uncertain publications
- LinkedIn --> first V74 post visually verified by operator, provider URN `urn:li:share:7522669773583872000`
- Delivery timer --> **active and enabled**, LIVE=YES; follow-up observed LAST `2026-11-01 14:51:36 UTC`, NEXT `2026-11-01 14:52:37 UTC`, six subsequent `STATE=IDLE` runs; SQLite still exactly one `PUBLISHED` row, PENDING=0, IN_FLIGHT=0

**The end-to-end GitHub -> KUZ-DIN -> LinkedIn START path has passed a real production publication.** Existing journal idempotency prevents V74 duplicates. A real FINAL-DEV-FLOW/GOGIT publication has not yet been tested in production. No automatic ChatGPT watcher or separate OpenAI API charge is involved.

## Outstanding operations

1. The timer recurrence check is complete: a concrete next trigger and six idle DELIVERY cycles confirm continuous operation. Continue standard operational monitoring.
2. Verify a subsequent *genuine and separately authorized* FINAL-DEV-FLOW/GOGIT event. No fabricated experiment result.
3. Maintain OAuth token expiration monitoring and manual review of uncertain LinkedIn POST outcomes before any reattempt.
4. Keep a verified source/runtime reconciliation procedure before deploying application code to `/opt/kuz-din`; documentation commits do not modify the VPS.
5. Execute the reviewed [V74 two-report GPU/GOGIT job](../tools/run_v74_frequency_prior_001_job.py) on fhc2 after fast-forward synchronization; it runs CPU tests, freezes V62/V65/V73 and commits immutable CORE/STRATA GOGIT results with fail-closed controls. No training or BLIND TEST access is authorized.

## V74 proposal and limits

[V74 read-only scientific protocol](../phases/MINI-KUZAI-PHASE-03-V74-FREQUENCY-PRIOR-CONTROL-001.md) proposes testing whether the V73 PC1_ONLY result is dominated by TRAIN unigram frequency. [START Discussion source draft](discussions/steps/V74-start.md) is committed; the real [GitHub Discussion #5](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5) has been published. The frozen numerical schema (CORE 30 metrics / STRATA 30 metrics), pinned public audits, CPU regression and two-stage runner are now committed to GitHub. The fhc2 GPU run and V74 GOGIT reports are **not yet verified**. No new training and no BLIND TEST access are authorized.

## New-chat resumption prompt

> Reprendre Mini-Kuzai Phase 03 V74 après START-DEV-FLOW du 2026-11-01. GitHub Discussion #5 et reçu START publiés, webhook KUZ-DIN reçu, journal SQLite `start-V74-d5` PUBLISHED, LinkedIn `urn:li:share:7522669773583872000` visuellement confirmé. Livraison LIVE=YES, timer actif/activé, échéance suivante vérifiée 2026-11-01 14:52:37 UTC, six cycles IDLE et zéro doublon. V73 GOGIT demeure la base scientifique, checkpoint V62 figé à 69 optimizer steps / 597982 tokens. V74 Frequency-Prior Control dispose désormais de deux schémas de métriques gelés, tests CPU et runner GPU/GOGIT à exécuter sur fhc2; résultats numériques non publiés à ce stade. Aucun nouvel entraînement ni accès BLIND. FINAL-DEV-FLOW uniquement après GOGIT V74 réel vérifié et autorisation distincte; ne jamais recréer un START pour V74.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
