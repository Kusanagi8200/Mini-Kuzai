# MINI-KUZAI PHASE 03 - V59 TRAINING AUTHORIZED CHECKPOINT - 2026-10-28

Status --> **V59 DATA PREPARATION CLOSED / PERSISTENT TRAINER FROZEN / RUNTIME VERIFIED / TRAINING NOT STARTED**

This checkpoint records the current Phase 03 V59 state after final mix freeze,
bounded-pilot authorization, persistent-trainer freeze and final runtime
verification.

## Terminal GOGIT state

Step -->

`PHASE03-SMOLTALK-V59-FINAL-MIX-FREEZE-AUTHORIZATION-001`

Result -->

```text
SEMANTIC_VALIDATION_COMPLETE = 1
V59_MIX_FINALIZED            = 1
TRAINING_AUTHORIZED          = 1
TRAINING_STARTED             = 0
```

Authorization scope -->

`V59_BOUNDED_PILOT_ONLY`

Freeze fingerprint -->

`40008ff0b106d3c58d2bf8196f539be2bf692d1e8ed3b7cd0e2dd1429b887503`

## Frozen training identity

Final training set -->

- controlled TRAIN --> **107 conversations / 29 semantic groups**
- public DIRECT_KEEP --> **165 conversations**
- total training conversations --> **272**
- total unique training segments --> **345**
- total unique clean tokens --> **295416**.

Controlled TRAIN provenance remains -->

- 105 `phase03-designed`
- 2 admitted public SmolTalk derivatives.

Public material excluded from the authorized pilot -->

- REPAIR_QUEUE --> **108 conversations**
- EXCLUDE_REVIEWED --> **47 conversations**
- DEFER_UNREVIEWED --> **792 conversations**.

No automatic filtering decision is used to admit public training data.

## Frozen exposure policy

Target token-exposure shares -->

| Stream | Target |
| --- | ---: |
| CONTROLLED_TRAIN | **30.00%** |
| PERSONA_CORE | **46.58%** |
| GENERAL_SUPPORT | **15.00%** |
| LEGACY_STRUCTURED_KEEP | **8.42%** |

Persona-oriented exposure -->

**CONTROLLED_TRAIN + PERSONA_CORE = 76.58%**

Sampling policy -->

- stream-level weighted sampling
- token-exposure quotas
- with replacement
- shuffle inside each stream
- no physical corpus duplication.

## Frozen tokenizer / serialization / segmentation / architecture

Tokenizer -->

- V56 `byte_bpe_whitespace`
- vocabulary --> 1024
- merges --> 765
- byte fallback --> enabled
- tokenizer SHA-256 --> `cd511d08430c40069139546c4539d5edb7f3236656ba80ff430a8f3b13d4a97a`
- tokenizer fingerprint --> `62216744c1493d3bd5558120570e0178d6adb94c40311e0639dde245cfab4ee9`.

Serialization -->

- V57 frozen
- textual `USER:` / `MINI-KUZAI:` role labels
- BOS at conversation start
- EOS at conversation end.

Segmentation -->

- V59 pair-preserving segmentation
- context limit --> 2048
- complete USER / MINI-KUZAI pairs preserved
- no arbitrary intra-pair split
- no truncation.

Architecture -->

- V58 MICRO
- decoder-only autoregressive Transformer
- context --> 2048
- d_model --> 128
- heads --> 4
- layers --> 4
- FFN --> 512
- parameters --> **1184512**
- architecture config SHA-256 --> `31c5326222b60316f2dba3285b4626fc81a74cae86ee2c5ba55bad0c81c74e6c`.

## Authorized bounded pilot protocol

Optimizer / schedule -->

- dtype --> BF16
- AdamW
- learning rate --> 3e-4
- minimum learning rate --> 3e-5
- betas --> 0.9 / 0.95
- weight decay --> 0.10
- gradient clip --> 1.0
- seed --> 42
- dynamic accumulation to **8192 non-pad tokens per optimizer step**
- warmup --> 15 steps
- cosine decay after warmup.

Hard authorization limits -->

- maximum optimizer steps --> **145**
- maximum exposure tokens --> **1181664**
- reference exposure cycles --> **4**
- architecture changes --> **NOT AUTHORIZED**
- exposure-policy changes --> **NOT AUTHORIZED**
- corpus changes --> **NOT AUTHORIZED** under this authorization.

Any change to a frozen dependency invalidates this authorization and requires a
new freeze / authorization gate.

## Evaluation boundary

VALIDATION -->

- 36 records / 18 groups
- frozen
- allowed during the pilot.

BLIND TEST -->

- 36 records / 18 groups
- frozen
- **forbidden during training**
- reserved for post-training evaluation.

The BLIND split must not influence optimizer steps, checkpoint selection,
learning-rate decisions, early stopping or model selection during the pilot.

## Hardware preflight

Local RTX 5060 Laptop GPU preflight -->

- CUDA --> PASS
- BF16 --> PASS
- synthetic full-context microbatch --> 8 x 2048
- finite loss --> YES
- finite gradient norm --> YES
- peak allocated --> 564 MiB
- peak reserved --> 632 MiB
- total GPU memory --> 7705 MiB
- reserved share --> 8.20%
- memory gate --> 60.00%.

## Persistent trainer freeze

The bounded-pilot trainer is implemented and frozen.

Trainer freeze fingerprint -->

`d71fb0fe6e71cbfd46ae06a88ef994b91091c698b8f401237387b5fc7ebe3a84`

Freeze verification -->

- Python compilation --> **PASS**
- unit tests --> **PASS**
- full runtime verification --> **PASS**
- reconstructed TRAIN segments --> **345**
- reconstructed TRAIN unique tokens --> **295416**
- reconstructed VALIDATION records --> **36**
- reconstructed VALIDATION segments --> **36**
- reconstructed VALIDATION tokens --> **9242**
- BLIND TEST access --> **0**
- TRAINING_STARTED --> **0**

Schedule preview -->

- sampler cycles --> **4**
- segments --> **2263**
- exposure tokens --> **1181302**
- maximum authorized exposure tokens --> **1181664**
- maximum stream-share deviation --> **4 basis points**

Checkpoint persistence includes optimizer, scheduler, RNG and sampler state.

Terminal trainer GOGIT step -->

`PHASE03-SMOLTALK-V59-PERSISTENT-TRAINER-FREEZE-001`

## VALIDATION compatibility closure

Persistent-trainer implementation exposed historical schema variation in the V54
VALIDATION freeze declarations.

The final compatibility gate requires -->

- **18 / 18** VALIDATION declarations
- **18 / 18** historical GOGIT freeze proofs
- **18 / 18** target Git blob matches
- modern and historical review-field variants to resolve to explicit successful
  review state
- zero cross-split ID collisions
- zero cross-split group collisions
- zero exact user-prompt collisions

No VALIDATION corpus record was rewritten.

GOGIT step -->

`PHASE03-SMOLTALK-V59-VALIDATION-COMPATIBILITY-001`

## Frozen-dependency experiment note

A post-authorization segmentation caching optimization was measured on synthetic
data and reduced the local benchmark cost. It also changed the frozen
segmentation-source fingerprint.

The optimization was therefore reverted.

The persistent trainer was frozen only after restoration of the originally
authorized segmentation dependency.

## Final runtime verification

The frozen CLI `tools/train_v59_bounded_pilot.py --verify-only` passed with -->

- authorization freeze fingerprint --> `40008ff0b106d3c58d2bf8196f539be2bf692d1e8ed3b7cd0e2dd1429b887503`
- trainer freeze fingerprint --> `d71fb0fe6e71cbfd46ae06a88ef994b91091c698b8f401237387b5fc7ebe3a84`
- GPU --> **NVIDIA GeForce RTX 5060 Laptop GPU**
- TRAINING_STARTED --> **0**

The canonical run directory
`/root/Mini-Kuzai/runs/v59-bounded-pilot-001` was confirmed absent immediately
before the first real run.

## Current project boundary

All corpus-selection, mix-weighting, tokenizer, segmentation,
architecture-preflight, authorization, trainer-freeze and runtime-verification
gates are closed for the bounded pilot.

Training has **not** started.

The next operation is the first real V59 bounded-pilot training run. It must use
the frozen trainer without `--resume` and must remain inside the frozen limits.

## Primary evidence

- `reviews/smoltalk-v59-final-mix-freeze-authorization/FINAL-MIX-FREEZE-001.json`
- `reviews/smoltalk-v59-final-mix-freeze-authorization/TRAINING-AUTHORIZATION-001.json`
- `reviews/smoltalk-v59-final-mix-freeze-authorization/REPORT-001.json`
- `reviews/smoltalk-v59-persistent-trainer-freeze/TRAINER-FREEZE-001.json`
- `reviews/smoltalk-v59-persistent-trainer-freeze/RESULTS-001.md`
- `reports/assistant-results/history/PHASE03-SMOLTALK-V59-FINAL-MIX-FREEZE-AUTHORIZATION-001.json`
- `reports/assistant-results/history/PHASE03-SMOLTALK-V59-VALIDATION-COMPATIBILITY-001.json`
- `reports/assistant-results/history/PHASE03-SMOLTALK-V59-PERSISTENT-TRAINER-FREEZE-001.json`

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
