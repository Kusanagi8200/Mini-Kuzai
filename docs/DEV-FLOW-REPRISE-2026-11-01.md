# Mini-Kuzai - V74 to V78 production checkpoint

Original checkpoint --> 2026-11-01
Updated --> 2026-11-07

Status --> **V74 CLOSED / V75 CLOSED / V76 CLOSED / V77 CLOSED / V78 START PUBLISHED / CPU PREFLIGHT AUTHORIZED / GPU NOT AUTHORIZED**

## Verified two-host publishing topology

```text
Mini-Kuzai / fhc2
  Explicit START-DEV-FLOW or FINAL-DEV-FLOW request on GitHub main
    -> mini-kuzai-dev-flow.timer / approved operator account
    -> GitHub Discussions Development Log
    -> verified matching request receipt committed to GitHub
                         |
                         v
KUZ-DIN / VPS
  HMAC-SHA256 GitHub webhook
    -> approved event JSON (0600)
    -> QUEUE timer + source fingerprint verification
    -> SQLite PREPARED journal
    -> DELIVERY timer + GitHub receipt + cutoff + LIVE gates
    -> LinkedIn personal profile / PUBLISHED unique URN
```

This workflow requires a **separately approved request for every START or FINAL**. A GitHub commit describing research never authorizes a post, training or BLIND access by itself.

## V74 scientific evidence - frozen and closed

| Evidence | Verified checkpoint |
| --- | --- |
| Model | V62 checkpoint stopped after 69 optimizer steps / 597982 exposure tokens |
| TRAIN inventory | 294726 lexical tokens, 891 observed token types |
| VALIDATION | 36 frozen conversations, 9170 lexical positions |
| CORE GOGIT | [`54dace24112f`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/54dace24112f920232cb6106422f6da7ab35d24c), 30 integer metrics, PASS |
| STRATA GOGIT | [`7b36b3fb18c6`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/7b36b3fb18c6f31037f90ada947b56469f73424f), 30 integer metrics, PASS |
| ORIGINAL | 2673 / 9170 correct |
| CENTER | 2832 / 9170 correct |
| PC1_ONLY | 2455 / 9170 correct, 2 distinct predicted IDs |
| TRAIN_UNIGRAM | 2535 / 9170 correct, 1 distinct predicted ID |
| PC1-unigram overlap | 6450 matching argmax predictions, 2449 shared correct predictions |
| Interpretation | Strong frequency-prior confound, not a causal or semantic-generalization finding |
| Safety | New training 0, BLIND access 0, checkpoint unchanged |

The immutable [V74 study and interpretation](../phases/MINI-KUZAI-PHASE-03-V74-FREQUENCY-PRIOR-CONTROL-001.md) explains limitations, including VALIDATION-fitted PCA and the dominance of high-frequency gold tokens.

## V74 real START and FINAL publications

| Control | START | FINAL |
| --- | --- | --- |
| GitHub Discussion | [#5](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5) | [comment #19334374](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5#discussioncomment-19334374) |
| Request | [V74-start.json](../automation/dev-flow/requests/V74-start.json) | [V74-final.json](../automation/dev-flow/requests/V74-final.json) |
| Receipt | [V74-start.json](../automation/dev-flow/receipts/V74-start.json) | [V74-final.json](../automation/dev-flow/receipts/V74-final.json) |
| Event ID | `start-V74-d5` | `close-V74-d5-c19334374` |
| SQLite status | `PUBLISHED` | `PUBLISHED` |
| LinkedIn URN | `urn:li:share:7522669773583872000` | `urn:li:share:7522683502069190656` |

VPS read-only terminal verification confirmed both QUEUE and DELIVERY timers **active**, exactly **two PUBLISHED** rows and **zero PREPARED / IN_FLIGHT** rows. One START and one FINAL were published; neither should be repeated. The V74 final GitHub comment cites **both** CORE and STRATA reports.

## KUZ-DIN publishing safety audit - follow-up

The new condensed LinkedIn title standard was introduced into KUZ-DIN:

| Future event | Title |
| --- | --- |
| START V75+ | `MINI-KUZAI // LLM FROM SCRATCH` then `LIVE DEV FLOW Vxx` |
| FINAL V75+ | `MINI-KUZAI // LLM FROM SCRATCH` then `FLOW Vxx OK` |

The first title version was deployed to VPS `/opt/kuz-din` at commit `59c915fcdaf528d5ae90d991809d8871ce2cdc44` with local tests PASS. A subsequent audit identified that the QUEUE runner repeatedly reformats historical events and SQLite compares `post_sha256`, so applying the new FINAL header retroactively to V74 could block queue processing.

**Corrective action on GitHub** --> KUZ-DIN now preserves `LIVE DEV FLOW V74` for the V74 historical FINAL when rebuilding its fingerprint. New titles apply only to FINAL V75 and higher. A regression test verifies that an already `PUBLISHED` V74 SQLite event remains idempotent after formatting.

**Operational status at this checkpoint** --> the V75 live flow exercised the corrected formatter successfully. KUZ-DIN published both V75 START and FINAL without replaying V74. The V75 FINAL delivery audit confirmed QUEUE and DELIVERY timers enabled+active, LIVE gate enabled, 4 total published DEV-FLOW rows, 0 PREPARED and 0 IN_FLIGHT.

## V75 scientific and production closure - verified

- [V75 TRAIN-fitted geometry transfer protocol and verified findings](../phases/MINI-KUZAI-PHASE-03-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.md)
- [V75 START source](discussions/steps/V75-start.md)
- [V75 START receipt](../automation/dev-flow/receipts/V75-start.json)
- [V75 scientific GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json)
- [V75 FINAL preflight GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V75-FINAL-PREFLIGHT-001.json)
- [V75 FINAL request](../automation/dev-flow/requests/V75-final.json)
- [V75 FINAL receipt](../automation/dev-flow/receipts/V75-final.json)

GitHub START --> [Discussion #6](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6).

GitHub FINAL --> [Discussion #6 comment #19458251](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6#discussioncomment-19458251). Receipt commit --> [`7c1265603ff1`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/7c1265603ff102ebe54d9bd87b845e885c593c8f).

KUZ-DIN FINAL delivery verification --> [`KUZ-DIN-V75-FINAL-DELIVERY-001`](https://github.com/Kusanagi8200/KUZ-DIN/blob/main/reports/assistant-results/history/KUZ-DIN-V75-FINAL-DELIVERY-001.json), GOGIT commit [`e299747256f9`](https://github.com/Kusanagi8200/KUZ-DIN/commit/e299747256f9b9948d80eabfcd3f9c83921c2618). The exact event `close-V75-d6-c19458251` is `PUBLISHED`, a valid LinkedIn URN is present, and there are no PREPARED or IN_FLIGHT records.

Verified scientific result --> TRAIN-derived PC1 and independently fitted VALIDATION PC1 align at **99.95% absolute cosine**. TRAIN_PC1_ONLY produces **2457/9170** correct predictions using only **2 distinct predicted IDs**. Removing TRAIN PC1 increases diversity to **663 predicted IDs** but drops top-1 accuracy to **611/9170**.

Interpretation boundary --> the dominant anisotropy is stable across TRAIN and VALIDATION, but remains strongly associated with output-frequency concentration. This is not semantic validation, conversational competence or causal attribution.

Safety state --> `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0`, `V75_BLIND_ACCESS=0`, checkpoint unchanged.

## V76 scientific and production closure - verified

- [V76 frequency-residualized PC1 protocol and findings](../phases/MINI-KUZAI-PHASE-03-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.md)
- [V76 START source](discussions/steps/V76-start.md)
- [V76 START receipt](../automation/dev-flow/receipts/V76-start.json)
- [V76 CPU preflight GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V76-CPU-PREFLIGHT-001.json)
- [V76 scientific GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V76-FREQUENCY-RESIDUALIZED-PC1-CONTROL-001.json)
- [V76 FINAL request](../automation/dev-flow/requests/V76-final.json)
- [V76 FINAL receipt](../automation/dev-flow/receipts/V76-final.json)

GitHub START --> [Discussion #7](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/7).

GitHub FINAL --> [Discussion #7 comment #19459204](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/7#discussioncomment-19459204).

KUZ-DIN FINAL delivery verification --> [`KUZ-DIN-V76-FINAL-DELIVERY-001`](https://github.com/Kusanagi8200/KUZ-DIN/blob/main/reports/assistant-results/history/KUZ-DIN-V76-FINAL-DELIVERY-001.json). START and FINAL are both PUBLISHED, the FINAL LinkedIn URN is valid, timers are active, and no PREPARED or IN_FLIGHT row remains.

Verified scientific result -->

- frequency OLS R2 --> 7.75%
- residual-energy share --> 92.25%
- PC1 replay correct --> 2457 / 9170
- frequency component correct --> 2451 / 9170
- frequency residual correct --> 2594 / 9170
- TRAIN unigram correct --> 2535 / 9170
- residual predicted IDs --> 2
- residual dominant share --> 70.43%

Interpretation boundary --> the stable PC1 output profile is not mostly explained by static TRAIN lexical frequency. The residual retains predictive concentration but remains extremely low-diversity. V76 does not establish semantics, useful context use or generalization.

Safety state --> `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0`, `V76_BLIND_ACCESS=0`, checkpoint unchanged.

## Exact resumption order

1. Keep V62 frozen and BLIND closed
2. Treat V74, V75, V76 and V77 START/FINAL publications and scientific GOGIT reports as immutable completed history
3. Use the frozen V78 protocol at `phases/MINI-KUZAI-PHASE-03-V78-IDENTICAL-CONTEXT-REBATCHING-NUMERICAL-CONTROL-001.md`
4. Use the committed V78 START source at `docs/discussions/steps/V78-start.md`
5. Treat V78 START [Discussion #9](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/9) and its committed receipt as immutable published history
6. Prepare and execute only the V78 CPU implementation/preflight
7. Do not execute V78 GPU scientific work without a separate explicit authorization after CPU preflight review
8. Do not authorize training, optimizer steps, checkpoint writes or BLIND access from V77 closure

**PAUSE BOUNDARY** --> V77 is fully closed. V78 START is published. CPU-only implementation/preflight is the current authorized boundary; GPU remains separately unauthorized.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
