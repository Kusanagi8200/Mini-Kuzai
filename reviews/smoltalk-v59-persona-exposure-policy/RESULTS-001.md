# Mini-Kuzai V59 - persona-first mix weighting / exposure policy

Status --> **POLICY DEFINED / TRAINING NOT AUTHORIZED**

The policy uses weighted stream sampling. No training record is physically duplicated.

## Unique clean data

| Stream | Conversations | Segments | Unique tokens | Raw share |
| --- | ---: | ---: | ---: | ---: |
| CONTROLLED_TRAIN | 107 | 107 | 24539 | 8.31% |
| PERSONA_CORE | 86 | 142 | 182787 | 61.87% |
| GENERAL_SUPPORT | 68 | 76 | 63213 | 21.40% |
| LEGACY_STRUCTURED_KEEP | 11 | 20 | 24877 | 8.42% |

## Persona-first exposure target

| Stream | Target share | Reference-cycle tokens | Equivalent passes |
| --- | ---: | ---: | ---: |
| CONTROLLED_TRAIN | 30.00% | 88624 | 3.612x |
| PERSONA_CORE | 46.58% | 137606 | 0.753x |
| GENERAL_SUPPORT | 15.00% | 44312 | 0.701x |
| LEGACY_STRUCTURED_KEEP | 8.42% | 24874 | 1.000x |

Persona-oriented exposure (CONTROLLED + PERSONA_CORE) --> **76.58%**
Reference exposure cycle --> **295416 tokens**

Constraints -->
- CONTROLLED_TRAIN >= 30%
- CONTROLLED_TRAIN + PERSONA_CORE >= 75%
- GENERAL_SUPPORT <= 15%
- LEGACY_STRUCTURED_KEEP <= 10%

Guardrails -->
- REPAIR_QUEUE admitted --> NO
- EXCLUDE_REVIEWED admitted --> NO
- DEFER_UNREVIEWED admitted --> NO
- physical duplication --> NO
- training authorized --> NO
- training started --> NO

This policy defines relative exposure only. Optimizer, learning-rate, batch, step count and training authorization remain separate decisions.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
