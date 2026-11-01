# Mini-Kuzai - DEV-FLOW checkpoint and V74 resumption

Date --> 2026-11-01

Status --> **LOCAL DEV-FLOW ACTIVE / KUZ-DIN TIMERS ACTIVE / LINKEDIN LIVE DISABLED / V74 NOT STARTED**

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
   -> LinkedIn POST only if independent LIVE gate is explicitly authorized
```

No background ChatGPT watcher, OpenAI API key or paid OpenAI API is used. The local worker polls GitHub after explicit requests and remains inert otherwise.

## Verified deployment gates

| Component | Verified observation |
| --- | --- |
| Research | V73 latest verified GOGIT, V62 frozen after 69 optimizer steps / 597982 exposed tokens |
| fhc2 | `mini-kuzai-dev-flow.timer` active and enabled, worker repeatedly IDLE, GitHub actor `Kusanagi8200`, clean worktree |
| Request queue | No pending request, `automation/dev-flow/requests` absent before this documentation commit |
| GitHub webhook | One matching active hook, ID `705780264`, `discussion` and `discussion_comment`, JSON, SSL verification enabled |
| VPS signed ping | HTTP 200 / `ping_ok`, no events recorded |
| Synthetic START integration | HTTP 202 recorded, duplicate HTTP 200, invalid HMAC HTTP 401 |
| Synthetic SQLite | Event PREPARED then repeat preparation EXISTS/PREPARED, idempotent |
| Publisher regression | 36 of 36 offline tests PASS, START and FINAL receipt mock checks PASS |
| KUZ-DIN service | PREPARE and DELIVERY timers active, delivery one-shot repeatedly `LIVE_DISABLED` |
| Token files | Encrypted token `0600` and key `0640`; local token validation PASS at audit time |
| Production event directory / SQLite | Not created yet, consistent with no real START or FINAL events |
| Activation cutoff | `2026-11-01T13:38:23+00:00` verified in systemd drop-in |
| LinkedIn delivery | **`KUZDIN_PUBLISHER_LIVE_ENABLED=NO`**; no real DEV-FLOW event published |
| LinkedIn historical introduction | One standalone V5 post previously confirmed with HTTP 201, not evidence of automated DEV-FLOW delivery |

## Required checks before production LIVE

- Validate a genuine authorized START/FINAL GitHub webhook event in KUZ-DIN and its SQLite PREPARED record
- Match a published GitHub DEV-FLOW receipt to the exact real GitHub event and cutoff, without exposing credentials
- Review the final post length and LinkedIn profile destination
- Check actual service-account file ownership and recovery of IN_FLIGHT without duplicate posting
- Obtain separate explicit authorization before changing `LIVE=NO`; test one controlled real LinkedIn delivery and verify the provider URN

Timers and the signed webhook are deployed, but **automatic LinkedIn posting is not yet production-ready**. Offline tests do not prove live end-to-end posting. No V74 Discussion has been created.

## V74 proposal and limits

[V74 read-only scientific protocol](../phases/MINI-KUZAI-PHASE-03-V74-FREQUENCY-PRIOR-CONTROL-001.md) proposes testing whether the V73 PC1_ONLY result is dominated by TRAIN unigram frequency. [START Discussion draft](discussions/steps/V74-start.md) is prepared and committed for human review, not published. The GPU audit, frozen numerical metric schema, pinned runner and V74 GOGIT do not exist yet. No new training and no BLIND TEST access are authorized.

## New-chat resumption prompt

> Reprendre Mini-Kuzai Phase 03 après V73 GOGIT vérifié. Le checkpoint V62 est figé à 69 optimizer steps / 597982 tokens. V74 Frequency-Prior Control est proposé, non exécuté. Consulter `phases/MINI-KUZAI-PHASE-03-V74-FREQUENCY-PRIOR-CONTROL-001.md`, `docs/discussions/steps/V74-start.md` et ce checkpoint. Le worker fhc2 DEV-FLOW et les timers KUZ-DIN tournent, mais `KUZDIN_PUBLISHER_LIVE_ENABLED=NO`. Cutoff `2026-11-01T13:38:23+00:00`. Avant de publier un START, vérifier la synchronisation locale, les garde-fous et confirmer explicitement `START-DEV-FLOW`. Ne pas créer de fichier dans `automation/dev-flow/requests/` sans cet ordre. Aucun entraînement ni accès BLIND. `FINAL-DEV-FLOW` seulement après V74 GOGIT réel et vérifié.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
