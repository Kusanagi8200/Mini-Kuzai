# Mini-Kuzai V54 - B01 lexical near-duplicate screening 001

Status: LEXICAL_SCREEN_COMPLETE_SEMANTIC_SIGNOFF_PENDING

## Method

Read 19 canonical TRAIN JSONL files (107 records) and the two B01 VALIDATION candidates from GitHub. Compare the combined user-turn text of each VALIDATION record with that of every TRAIN record using token-set Jaccard similarity. Tokenize case-insensitively with ASCII alphanumeric runs and discard tokens of length two or less; this is a screening heuristic, not a semantic equivalence metric. There are 214 pairwise comparisons.

## Maximum lexical similarity

| Validation ID | TRAIN ID | TRAIN group | Jaccard |
| --- | --- | --- | ---: |
| p03-val-b01-000001 | p03-train-b17-000001 | sg-b17-01 | 0.176 |
| p03-val-b01-000002 | p03-train-b16-000002 | sg-b16-01 | 0.207 |

The highest-scoring B17 prompt concerns disclosed model architecture and does not present false-identity pressure. The B16 prompt concerns identity continuity under evolving self-understanding, not explicit adversarial false naming. No concerning near-duplicate was found among the closest lexical matches manually inspected.

## Interpretation and limits

Low lexical similarity is not proof of semantic independence, especially where short prompts use synonyms or paraphrases. The assessment is based on inspected top matches, not a complete independent expert semantic sign-off on all 214 pairs. No embeddings or external semantic model were used.

The previous exact-match audit reported 107 unique TRAIN IDs, 29 TRAIN groups, zero cross-split ID/group collisions and zero exact normalized user-prompt matches. This screening adds lexical evidence only; it does not replace independent semantic and evaluation-set governance review.

## Gate status

- Lexical screening: COMPLETE.
- Independent semantic sign-off: PENDING.
- B01 validation freeze: NOT AUTHORIZED.
- BLIND TEST text creation: NONE.
- Model training: NOT AUTHORIZED.
