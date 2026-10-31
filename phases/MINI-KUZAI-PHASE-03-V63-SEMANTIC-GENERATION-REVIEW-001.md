# Mini-Kuzai Phase 03 - V63 Semantic Generation Review 001

Status --> **HUMAN REVIEW SUSPENDED / NOT COMPLETED / NO HUMAN GOGIT REPORT**

## Review suspension and successor

On 2026-10-31 the local evaluation began and the first inspected generation was visibly nonsensical despite valid UTF-8 and EOS termination. The operator explicitly suspended the 24-example rating loop because further subjective scoring of this degree of language degradation was not useful at this stage.

This human review was **not completed**. No human score can be inferred or fabricated. The repository contains **no** successful `PHASE03-SMOLTALK-V63-SEMANTIC-GENERATION-REVIEW-001` GOGIT history.

The process below is preserved as an **archived, opt-in human-review protocol**, not the active procedure. Its 24 private samples were instead inspected by the non-interactive [V63 automatic language screen](MINI-KUZAI-PHASE-03-V63-AUTOMATIC-LANGUAGE-SCREEN-001.md). That published screen is nonsemantic and assigned **zero human ratings**.

Current project checkpoint --> [V64 closure and V65 readiness](MINI-KUZAI-PHASE-03-V64-CLOSURE-V65-READINESS-2026-10-31.md).

## Objective

Qualitatively assess whether generated Top-k / Top-p responses are relevant, coherent and behaviorally appropriate. The prior V63 robustness audit confirmed that EOS termination and UTF-8 validity alone cannot demonstrate conversational quality.

This process is separate from training and must not be treated as a new training authorization.

## Frozen protocol

- Model --> V62 cycle-2 checkpoint, 69 optimizer steps, 597982 tokens exposed
- Source --> six fixed frozen VALIDATION prompts, no BLIND TEST access
- Decoder --> temperature 0.8, top-k 40, top-p 0.9
- Seed subset --> 6301, 6303, 6305, 6308, preselected independently of observed sample quality
- Generated responses --> 24 = four seeds x six prompts
- Maximum new tokens --> 96 per response
- GPU --> CUDA/BF16, batched forward passes with per-seed generators
- Prior evidence --> GOGIT V63 Decoding Robustness 001 and prior frozen V62 artifacts

This is an exploratory qualitative sample, not a representative statistical generalization test.

## Private review and confidentiality

The generator writes private files exclusively outside the Git repository -->

`/root/Mini-Kuzai/runs/v63-semantic-generation-review-001/`

Private files -->

- `samples-private.json` --> frozen prompts, generated text, token IDs and integrity digest
- `ratings-private.json` --> explicitly human-entered ratings keyed to the sample digest
- `backups/` --> timestamped backups created before updating an existing private ratings file

File permissions --> private directory 0700, private JSON 0600. Do not commit or copy these private files into GitHub, public issues or GOGIT.

Samples are immutable after first generation. Human ratings are resumable: quit with `q`, resume with the same runner command, and previously completed ratings are skipped. A missing or invalid sample digest fails closed.

## Human rubric

The operator inspects each local prompt and generated response, then enters four ratings in one line.

| Criterion | Description | Permitted values |
| --- | --- | --- |
| Relevance | Addresses the actual user request | 0, 1, 2 |
| Coherence | Readable, internally coherent response | 0, 1, 2 |
| Cognition | Appropriate reasoning, curiosity, uncertainty and judgment where tested | 0, 1, 2, N/A |
| Persona | Consistent, recognizable Mini-Kuzai expression where tested | 0, 1, 2, N/A |

Scales --> 0 means insufficient, 1 means partial, 2 means adequate. The terminal uses `-` for N/A on Cognition/Persona only. A human must enter all required ratings. Scores are never inferred from EOS, UTF-8, token repetition or model logits.

Continuity across several conversation turns is **not evaluated** by these single-turn probes. It requires a separately designed future review.

The score is a subjective operator judgment, not a claim of verified model intelligence or downstream generalization.

## GOGIT publication gate

GOGIT stage --> `PHASE03-SMOLTALK-V63-SEMANTIC-GENERATION-REVIEW-001`

GOGIT audit reads only the completed local review and publishes exactly 30 numeric metrics -->

- Explicit completeness flags, four selected seeds and 24 manually reviewed responses
- EOS completions, very short responses, UTF-8 failures and role marker counts
- Distributions of human ratings 0/1/2 per dimension
- Non-applicability counts for Cognition and Persona only
- Mean evaluated rating per criterion, multiplied by 100

The numerical report contains **no** prompts, generated responses, reviewer identity, rationale or token IDs. Incomplete human review fails before public publication.

GOGIT records `TRAINING_AUTHORIZED=0` and `TRAINING_STARTED=0`. Its existing `semantic_validation_complete` metadata denotes completion of the specified review gate, **not** satisfactory model performance.

## Execution on fhc2

From the GitHub Mini-Kuzai repository root -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v63_semantic_generation_review_001_job.py
```

The default runner performs all steps serially -->

1. Verify synchronized clean main and frozen V62/V63 reference state
2. Run CPU unit tests
3. Generate or reuse the 24 private GPU samples
4. Present local samples individually for explicit human ratings
5. Save each rating with a backup before changing an existing review file
6. Refuse GOGIT while the review is incomplete
7. Publish numeric aggregates and verify the committed remote GOGIT history

For shorter sessions use `--prepare-only`, then `--review-only`; after all 24 scores are complete, `--publish-only` is available.

A fully published and validated report causes future runs to skip the review stage.

## Next decision

Review distributions before changing any decoding candidate, training objective or dataset. If relevance or coherence scores are low despite successful EOS generation, decoding alone is insufficient. Human-rated response text must stay local; any future repository documentation may discuss aggregates only.

No training restart, cycle-4 extension, new objective freeze or BLIND opening is authorized by this review.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
