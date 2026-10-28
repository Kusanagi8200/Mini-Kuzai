# Mini-Kuzai V59 - training hyperparameters / step budget / authorization gate

Status --> **PREFLIGHT_PASSED_AUTHORIZATION_REVIEW_REQUIRED**

## Pilot protocol

- architecture --> V58 MICRO / 1184512 parameters
- dtype --> BF16
- optimizer --> AdamW
- learning rate --> 0.0003
- minimum learning rate --> 3e-05
- betas --> 0.9 / 0.95
- weight decay --> 0.1
- gradient clip --> 1.0
- microbatch --> 8 sequences
- optimizer-step target --> 8192 non-pad tokens
- accumulation --> dynamic until token target
- pilot exposure cycles --> 4
- max exposure tokens --> 1181664
- max optimizer steps --> 145
- exposure tokens / parameter --> 0.998
- unique tokens / parameter --> 0.249

## Evaluation / stopping

- frozen VALIDATION --> used during pilot
- frozen BLIND TEST --> not accessed during pilot
- validation --> every half reference exposure cycle
- checkpoint --> every half reference exposure cycle
- stop on non-finite loss or gradient norm
- stop after two consecutive validation-loss degradations >=5% after at least three evaluations

## Hardware preflight

- passed --> YES
- device --> NVIDIA GeForce RTX 5060 Laptop GPU
- peak reserved MiB --> 632
- total GPU MiB --> 7705
- reserved share --> 8.20%
- memory gate --> 60.00%

Authorization candidate --> **YES**
Training authorized --> **NO**
Training started --> **NO**

A separate explicit authorization step is required before any persistent model training.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
