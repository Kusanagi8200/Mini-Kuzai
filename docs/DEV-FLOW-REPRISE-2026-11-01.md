# Mini-Kuzai - V74 closure and V75 scientific checkpoint

Date --> 2026-11-01

Status --> **V74 CLOSED / V75 START PUBLISHED / V75 SCIENTIFIC GOGIT VERIFIED / FINAL NOT YET AUTHORIZED**

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

## V75 scientific execution - verified, FINAL pending

- [V75 TRAIN-fitted geometry transfer protocol and verified findings](../phases/MINI-KUZAI-PHASE-03-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.md)
- [V75 START source](discussions/steps/V75-start.md)
- [V75 START receipt](../automation/dev-flow/receipts/V75-start.json)
- [V75 scientific GOGIT](../reports/assistant-results/history/PHASE03-SMOLTALK-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.json)

V75 START was published as [GitHub Discussion #6](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/6). The frozen scientific run then completed against the unchanged V62 checkpoint with no optimizer step and no BLIND access.

Verified scientific result --> TRAIN-derived PC1 and independently fitted VALIDATION PC1 align at **99.95% absolute cosine**. TRAIN_PC1_ONLY produces **2457/9170** correct predictions using only **2 distinct predicted IDs**, closely matching the previous VALIDATION-fitted PC1 replay (**2455/9170**). Removing TRAIN PC1 increases diversity to **663 predicted IDs** but drops top-1 accuracy to **611/9170**. TRAIN PC1 explains **90.19%** of centered TRAIN variance; VALIDATION PC1 explains **82.88%**.

Interpretation boundary --> the dominant anisotropy is stable across TRAIN and VALIDATION and is therefore not primarily a VALIDATION-fit artifact. V74's frequency-prior confound remains active: TRAIN_PC1_ONLY still closely tracks the context-free TRAIN unigram baseline. This is not semantic validation, conversational competence or causal attribution.

Safety state --> `TRAINING_AUTHORIZED=0`, `TRAINING_STARTED=0`, `V75_BLIND_ACCESS=0`, checkpoint unchanged.

## Exact resumption order

1. Keep V62 frozen and BLIND closed
2. Use the immutable V75 scientific GOGIT as the only FINAL scientific evidence
3. Run the V75 FINAL dry-run against clean synchronized `main` and the existing Discussion #6
4. Review the dry-run result
5. Only after a separate explicit operator authorization, create `automation/dev-flow/requests/V75-final.json` and allow the worker to publish FINAL
6. Reconcile the resulting GitHub receipt and KUZ-DIN LinkedIn delivery before any next research step

**PAUSE BOUNDARY** --> V75 scientific work is complete. FINAL-DEV-FLOW is prepared for read-only preflight but is **not yet authorized for publication**.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
