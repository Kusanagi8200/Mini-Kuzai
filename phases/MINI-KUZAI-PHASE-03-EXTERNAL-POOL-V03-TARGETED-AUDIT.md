# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.3 TARGETED AUDIT

Version: 0.1
Status: V0.3 REJECTED FOR TRAINING

## 1. PURPOSE

This document records the targeted audit performed after the first v0.3 diversity pass.

The audit focused on two unresolved risks:

- missed external persona or role-play prompts;
- semantic near-duplicate detection quality.

## 2. MISSED PERSONA RESULT

The v0.3 pool still contained:

```text
MISSED_PERSONA_RECORDS = 74
openhermes-50k = 3
smol-magpie-ultra-short = 71
```

Examples included explicit instructions such as:

```text
Assume the role of a history teacher
Take the role of a prominent economist
Assume the role of an AI therapist
Assume the role of a local fisherman
I'd like you to assume the role of an experienced local surfer
I need you to assume the role of a young medieval apprentice blacksmith
Act like you're a computer science professor
```

Conclusion:

The v0.3 persona filter was incomplete. Patterns such as `assume the role`, `take the role`, `act like`, and similar variants must be rejected before any external pool can be approved.

## 3. SIMHASH RESULT

The first SimHash experiment produced:

```text
CANDIDATE_PAIRS_CHECKED = 1046763
NEAR_DUPLICATE_PAIRS_DISTANCE_LE_6 = 299
DISTANCE_0 = 241
```

Manual inspection showed that many distance-zero pairs were not semantically equivalent.

Examples included unrelated prompts such as:

```text
how are you?
```

being treated as equivalent to arithmetic or algebra prompts.

This happened because the experimental normalization removed too much discriminating information, especially numbers, operators, punctuation, and short-token structure.

Conclusion:

The current SimHash implementation is invalid for automatic filtering and must not be used to remove training records.

## 4. DECISION

External pool v0.3 is rejected for training.

Reasons:

- 74 missed persona prompts remain;
- semantic near-duplicate detection is not yet reliable;
- automatic SimHash filtering could remove unrelated records.

## 5. NEXT METHOD

The next pool version must:

1. extend persona filtering with the newly observed prompt forms;
2. preserve exact prompt-family and content-hash uniqueness checks;
3. keep opening-frequency caps;
4. avoid the failed SimHash filter;
5. introduce a more conservative semantic-family method based on explicit known duplicate templates and token-set similarity only where the comparison is sufficiently informative;
6. inspect resulting duplicate candidates manually before any removal rule is generalized;
7. preserve all previous pool versions as experimental artifacts.

No training should use v0.1, v0.2, or v0.3.
