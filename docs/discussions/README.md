# Mini-Kuzai - GitHub Discussions and LinkedIn DEV-FLOW

Status --> **V74 START AND FINAL GITHUB/LINKEDIN PUBLISHED / DUAL GOGIT VERIFIED / V75 PREPARED ONLY**

Target --> [Kusanagi8200/Mini-Kuzai Discussions](https://github.com/Kusanagi8200/Mini-Kuzai/discussions)

Category --> `Development Log` (`DIC_kwDOUI2cC84DKGl8`)

Repository --> `Kusanagi8200/Mini-Kuzai` (`R_kgDOUI2cCw`)

## Existing discussions - do not republish

| Discussion | Purpose | Publication |
| --- | --- | --- |
| [#1](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/1) | Mini-Kuzai Live Dev Flow announcement | Already present |
| [#2](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/2) | [Origins](history/01-origins.md) | Historical |
| [#3](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/3) | [Learning design](history/02-learning-design.md) | Historical |
| [#4](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/4) | [First training results](history/03-first-training-results.md) | Historical |
| [#5](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5) | V74 scientific START and FINAL | Completed |

The historical posts were transferred to this repository and verified in the `Development Log` category. [`tools/github_discussions_history.py`](../../tools/github_discussions_history.py) is a separate historical tool and must not be invoked in live mode for new steps.

## Controlled Vxx publication lifecycle

```text
Operator reviews approved Vxx scientific scope
  -> reviewed Markdown source, frozen audit schema and safety gates
  -> separately authorized START-DEV-FLOW request on GitHub main
  -> fhc2 worker validates and posts one GitHub Discussion START
  -> committed START receipt
  -> signed GitHub webhook -> KUZ-DIN SQLite PREPARE
  -> guarded LinkedIn DELIVERY, one publication
  -> bounded, separately authorized scientific run and numeric GOGIT
  -> operator reviews immutable GOGIT evidence
  -> separately authorized FINAL-DEV-FLOW request
  -> one verified GitHub Discussion comment + FINAL receipt
  -> signed webhook and one guarded LinkedIn FINAL publication
```

The DEV-FLOW worker requires an exact committed request and a clean, synchronized `main`. It cannot start a scientific experiment, publish a discussion or authorize training from the presence of a draft alone. Future request processing is serial and protected by a lock. Real publication is not equivalent to a scientific validation.

### Github publisher boundaries

- [`tools/github_discussions_step.py`](../../tools/github_discussions_step.py) --> reviewed START Markdown, immutable GOGIT numeric reports, GitHub GraphQL checks and idempotency
- [`tools/dev_flow_worker.py`](../../tools/dev_flow_worker.py) --> exact START/FINAL JSON request schema, approved GitHub actor, committed receipts, one transaction per invocation
- [`tools/v74_final_closure.py`](../../tools/v74_final_closure.py) --> special V74-only dual CORE+STRATA evidence required within one compact FINAL comment
- [`tools/GOGIT.md`](../../tools/GOGIT.md) --> public aggregate audit and report constraints
- [KUZ-DIN production controls](https://github.com/Kusanagi8200/KUZ-DIN/blob/main/docs/MINI-KUZAI-LINKEDIN-PUBLISHER.md) --> signed webhook, queue, SQLite journal and receipt-gated LinkedIn delivery

Each event is authenticated and tied to a source fingerprint and a committed GitHub receipt. The KUZ-DIN SQLite journal transitions `PREPARED -> IN_FLIGHT -> PUBLISHED`, never blindly retries an ambiguous in-flight POST, and rejects conflicting replays. Posts are limited to 2800 LinkedIn characters. Neither model weights nor private data are published.

## Verified V74 scientific and production closure - 2026-11-01

| Control | Verified result |
| --- | --- |
| GitHub START | [Discussion #5](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5) |
| START request / receipt | [V74-start.json request](../../automation/dev-flow/requests/V74-start.json) / [V74-start.json receipt](../../automation/dev-flow/receipts/V74-start.json) |
| GOGIT CORE | [Immutable report](../../reports/assistant-results/history/PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-CORE-001.json), [commit `54dace24112f`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/54dace24112f920232cb6106422f6da7ab35d24c) |
| GOGIT STRATA | [Immutable report](../../reports/assistant-results/history/PHASE03-SMOLTALK-V74-FREQUENCY-PRIOR-STRATA-001.json), [commit `7b36b3fb18c6`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/7b36b3fb18c6f31037f90ada947b56469f73424f) |
| FINAL request | [V74-final.json](../../automation/dev-flow/requests/V74-final.json), [commit `47c2c05bbadb`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/47c2c05bbadb8a02553dcf9b1f795df4e5c8c36f) |
| GitHub FINAL | [Comment #19334374](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5#discussioncomment-19334374), one comment citing both reports |
| FINAL receipt | [V74-final.json](../../automation/dev-flow/receipts/V74-final.json), [commit `87912cc7a5f0`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/87912cc7a5f03bbf50afbc88c67e4c943ab7d73c) |
| START LinkedIn | `urn:li:share:7522669773583872000`, journal `start-V74-d5` --> `PUBLISHED` |
| FINAL LinkedIn | `urn:li:share:7522683502069190656`, journal `close-V74-d5-c19334374` --> `PUBLISHED` |
| VPS read-only control | Exactly two published rows, queue and delivery timers active, pending 0 and IN_FLIGHT 0 |
| Scientific control | No new training, no BLIND access, V62 checkpoint frozen after 69 optimizer steps |

V74's verified conclusion --> the TRAIN unigram baseline correctly predicted 2535 of 9170 lexical VALIDATION targets versus 2455 for PC1_ONLY, with 2449 shared successes. See the [V74 scientific interpretation](../../phases/MINI-KUZAI-PHASE-03-V74-FREQUENCY-PRIOR-CONTROL-001.md). This is a teacher-forced diagnostic, not a validated conversational capability.

**Both V74 START and FINAL are complete. Do not recreate or replay either event.**

## V75 staged, not started

- [V75 scientific proposal](../../phases/MINI-KUZAI-PHASE-03-V75-TRAIN-FITTED-GEOMETRY-TRANSFER-001.md) --> TRAIN-fitted hidden-state geometry versus frozen VALIDATION
- [Unpublished V75 START draft](steps/V75-start.md) --> text prepared for future operator review
- **No `automation/dev-flow/requests/V75-start.json` has been created**
- No GOGIT V75, no V75 GPU execution, no training and no BLIND access authorized
- Before any START, approve the precise V75 research protocol, deterministic TRAIN selection, no-leakage tests, 30-metric numeric schema and resource ceiling

KUZ-DIN's subsequent LinkedIn title convention is START `LIVE DEV FLOW V75` and FINAL `FLOW V75 OK`. The **V74 historical title must remain unchanged** in the formatting code so repeat queue scans do not conflict with existing SQLite `post_sha256` records. The legacy compatibility correction is committed to KUZ-DIN GitHub; deploy and verify it on the VPS before issuing V75 START.

## Recovery and change policy

The GitHub Discussions publisher must first pass CPU tests and a dry-run against clean synchronized `main`, with `PUBLICATION=DISABLED` in the preflight. Live writes require a distinct operator order and an exact committed request. Never reuse V74 paths to simulate future publications. On HTTP uncertainty, retain `IN_FLIGHT` and reconcile with LinkedIn manually instead of replaying. Do not publish additional GitHub comments or posts during a documentation review.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
