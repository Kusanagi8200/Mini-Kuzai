# Mini-Kuzai V59 - final mix policy 001

Status --> **POLICY DEFINED / MIX NOT FINALIZED / TRAINING NOT AUTHORIZED**

## Conservative admission policy

- DIRECT_KEEP --> only human-reviewed clean examples
- REPAIR_QUEUE --> never admitted unchanged
- EXCLUDE_REVIEWED --> removed from the future V59 training mix
- DEFER_UNREVIEWED --> never-reviewed candidates remain outside the V59 training mix
- persona priority --> HIGH/MEDIUM persona value is prioritized only after quality gates pass

## Candidate accounting

| Bucket | Conversations | Segments | Tokens |
| --- | ---: | ---: | ---: |
| DIRECT_KEEP | 165 | 238 | 270877 |
| REPAIR_QUEUE | 108 | 161 | 198226 |
| EXCLUDE_REVIEWED | 47 | 61 | 56726 |
| DEFER_UNREVIEWED | 792 | 1094 | 1204585 |

## Ready-now data envelope

- controlled TRAIN tokens --> 24539
- clean reviewed public tokens --> 270877
- combined ready-now tokens --> 295416
- public tokens / V58 parameter --> 0.229
- combined tokens / V58 parameter --> 0.249

Automatic filtering used --> **NO**
Unreviewed public data admitted --> **NO**
REPAIR admitted unchanged --> **NO**
V59 final mix --> **NOT FINALIZED**
Model training --> **NOT AUTHORIZED / NOT STARTED**

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
