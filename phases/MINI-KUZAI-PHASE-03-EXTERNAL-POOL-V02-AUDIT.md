# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.2 AUDIT

Version: 0.1
Status: STRUCTURAL AUDIT PASSED - CONTENT AUDIT NEXT

## 1. POOL

Source dataset: `HuggingFaceTB/smol-smoltalk`

Candidate file:

```text
data/external/smol-smoltalk/candidates/external-candidate-pool-v0.2.jsonl
```

Observed pool:

```text
smol-magpie-ultra-short   : 5000
openhermes-50k            : 1500
explore-instruct-rewrite  : 500
self-oss-instruct         : 1000
TOTAL                     : 8000
```

Class distribution:

```text
general   : 7000
technical : 1000
```

Pool SHA256:

```text
5a4dbdb1e27a8bfc1b8464e45abd35c5a75e1090c14259e11f0a36a4915ba600
```

## 2. STRUCTURAL AUDIT

The following checks passed:

```text
UNIQUE_CONTENT_HASHES   : 8000
EXACT_DUPLICATE_RECORDS : 0
PERSONA_RESIDUAL        : 0
GENERIC_RESIDUAL        : 0
UNICODE_DASH_RESIDUAL   : 0
```

The v0.2 role-play filter removed large numbers of explicit external persona prompts before selection, including:

```text
smol-magpie-ultra-short  : 40354
openhermes-50k           : 893
explore-instruct-rewrite : 0
self-oss-instruct        : 150
```

This confirms that explicit persona contamination was a material risk in the source dataset and that filtering it before Mini-Kuzai training is necessary.

## 3. IMPORTANT CONTENT OBSERVATIONS

Structural validation is not sufficient to approve the pool for training.

The first selected records show several remaining content characteristics that require measurement:

- some general responses remain long and strongly explanatory;
- some conversations contain classic puzzle and reasoning tasks;
- some OpenHermes responses include artificial task framing or generated follow-up questions;
- the rewrite source is concise but semantically narrow;
- the technical source is useful but must remain a limited quota;
- semantic near-duplicates may still exist even though exact content hashes are unique.

Therefore pool v0.2 is not yet approved as a final training source.

## 4. NEXT AUDIT

Before schema conversion, measure:

1. conversation and assistant length distributions by source;
2. number of turns by source;
3. repeated normalized user prompts;
4. repeated normalized assistant openings;
5. approximate near-duplicate conversations;
6. residual generic style not covered by the first phrase blacklist;
7. artificial assistant-generated questions;
8. deterministic manual samples from every source;
9. source-specific semantic narrowness.

Only after this content audit should pool v0.2 be accepted, revised, or reduced.
