# MINI-KUZAI PHASE 03 - OASST1 TREE AUDIT

Version: 0.1
Status: PASS

## Purpose

Validate OASST1 tree integrity and reconstruct clean English root-to-leaf paths before any candidate pool is built.

## Structural integrity

- input rows: 84437
- unique message IDs: 84437
- message trees: 9846
- roots: 9846
- duplicate message IDs: 0
- missing parent references: 0
- cross-tree parent references: 0
- role non-alternation: 0

## Clean English subset

Filtering used for this audit:

- lang = en
- review_result = true
- deleted != true

Result:

- English messages: 39283
- clean English messages: 37783
- clean assistant messages: 23073
- clean prompter messages: 14710
- eligible clean English roots: 3482
- reachable clean nodes: 37759

## Reconstructed paths

- root-to-leaf paths: 19276
- paths with at least 2 messages: 19275
- paths with at least 4 messages: 12302
- paths with at least 6 messages: 389

Depth distribution:

- depth 1: 1
- depth 2: 2977
- depth 3: 3996
- depth 4: 10131
- depth 5: 1782
- depth 6: 388
- depth 7: 1

## Rank profile

Among reachable clean assistant nodes:

- rank 0: 7827
- ranked above 0: 14098
- rank missing: 1129

The sample paths show that structural cleanliness alone is not sufficient. Some higher-rank assistant branches are clearly off-topic or lower quality while lower-rank branches can be substantially more coherent.

No automatic rank rule is frozen yet.

## Length profile

- median prompter length: 77 characters
- prompter p90: 229 characters
- median assistant length: 586 characters
- assistant p90: 1778 characters

## Decision

OASST1 passes structural reconstruction.

Do not build a training pool yet.

The next operation is a rank and quality audit using the human ranking and quality annotations. The objective is to determine a defensible assistant-branch selection rule before behavioral profiling and candidate extraction.
