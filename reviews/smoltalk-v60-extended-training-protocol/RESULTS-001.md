# Mini-Kuzai V60 - extended local training protocol

Status --> **PROTOCOL DEFINED / TRAINING NOT AUTHORIZED**

## Initial training window

- reference cycle --> **295416 tokens**
- milestones --> **1 / 4 / 8 / 16 cycles**
- initial window --> **4726656 exposure tokens**
- initial optimizer-step ceiling --> **577**
- extension block --> **8 cycles**
- extension beyond cycle 16 --> **new protocol freeze required**

## Optimization

- optimizer --> **AdamW**
- base learning rate --> **0.0003**
- minimum learning rate --> **0.00003**
- warmup --> **20 optimizer steps**
- scheduler --> **linear warmup + cosine decay**
- gradient clip --> **1.0**
- microbatch --> **8 sequences**
- optimizer target --> **8192 non-pad tokens**

## Evaluation policy

- VALIDATION --> every half reference cycle
- fixed generation probes --> every validation point
- BLIND TEST --> closed during training
- mandatory milestone reviews --> cycles 1 / 4 / 8 / 16
- degradation stop --> 5 percent over best for 3 consecutive evaluations
- plateau review --> less than 0.5 percent validation improvement across 4 evaluations after cycle 4
- continuation decision --> VALIDATION plus generation quality

TRAINING_AUTHORIZED --> **0**
TRAINING_STARTED --> **0**

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
