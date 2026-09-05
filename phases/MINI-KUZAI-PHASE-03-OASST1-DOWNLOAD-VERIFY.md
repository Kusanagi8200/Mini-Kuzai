# MINI-KUZAI PHASE 03 - OASST1 DOWNLOAD VERIFY

Version: 0.1
Status: PASS

## Dataset

OpenAssistant/oasst1

License: Apache 2.0

## Train

- rows: 84437
- English messages: 39283
- prompter messages: 31525
- assistant messages: 52912
- root messages: 9846
- assistant ranked: 48730
- assistant unranked: 4182
- review_result true: 82483
- review_result false: 1249
- deleted true: 1485

## Validation

- rows: 4401
- English messages: 2022
- prompter messages: 1645
- assistant messages: 2756
- root messages: 518
- assistant ranked: 2533
- assistant unranked: 223
- review_result true: 4289
- review_result false: 85
- deleted true: 68

## Result

The Parquet files are valid and contain all expected structural fields.

OASST1 is not a flat conversation dataset. Messages belong to conversation trees linked through message_id, parent_id, and message_tree_id.

The next operation is a structural tree reconstruction audit focused on English, reviewed, non-deleted branches before any candidate pool is built.
