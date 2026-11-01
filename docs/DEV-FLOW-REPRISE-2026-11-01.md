# Mini-Kuzai - V74 production closure and V75 resumption checkpoint

Date --> 2026-11-01

Status --> **V74 SCIENTIFIC GOGIT VERIFIED / START+FINAL DELIVERED / V75 PROPOSED BUT NOT STARTED / PAUSE**

## Verified two-host publishing topology

```text
Mini-Kuzai / fhc2
  Explicit START-DEV-FLOW or FINAL-DEV-FLOW request on GitHub main
    -> mini-kuzai-dev-flow.timer / approved operator account
    -> GitHub Discussions Development Log #5
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

**Operational status at this checkpoint** --> corrective code and tests have been committed to KUZ-DIN but have **not yet been confirmed deployed on the VPS**. A clean, backup-protected fast-forward update and CPU tests on KUZ-DIN are required before initiating V75 DEV-FLOW. Do not replay either V74 post to verify the formatting change.

## Proposed V75 study - not authorized

- [V75 TRAIN-fitted geometry transfer protocol](../phases/MINI-KUZAI-PHASE-03-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.md)
- [V75 unpublished Discussion START draft](discussions/steps/V75-start.md)

The scientific question is whether output-head PC1 learned solely from TRAIN states transfers to the frozen VALIDATION positions, unlike V72/V73's VALIDATION-fitted geometry. V74's context-free unigram baseline remains a control.

**V75 has not started.** There is no V75 request, execution, training, GOGIT report or GitHub/LinkedIn post. The next operator must approve a frozen metric schema, deterministic TRAIN calibration, 30-field GOGIT gate, reproducibility tests, and bounded GPU runner before any START or GPU analysis. No BLIND access or optimizer use is authorized.

## Exact resumption order

1. On KUZ-DIN, verify the historical V74 journal fingerprint compatibility patch is deployed, CPU regression passes, QUEUE and DELIVERY timers remain active and the journal still has only two PUBLISHED records
2. On Mini-Kuzai, verify the committed V74 immutable reports and completed START/FINAL receipts, with no new requests or active training
3. Review V75 proposed scientific protocol; freeze metrics, provenance, CPU tests, and resource ceilings before requesting any START
4. Only on an explicit later command, create a V75 START request, run the authorized scientific checks, review GOGIT, and separately authorize a V75 FINAL

**PAUSE** --> V74 is finished. V75 remains at the **planning / not-started** boundary. Do not act on a draft or restore a historical checkpoint as implicit permission to train.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
