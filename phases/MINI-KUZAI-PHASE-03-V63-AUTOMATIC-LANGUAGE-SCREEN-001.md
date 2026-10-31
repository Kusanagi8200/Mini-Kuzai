# Mini-Kuzai Phase 03 - V63 Automatic Language Screen 001

Status --> **EXECUTED / GOGIT PUBLISHED / NONSEMANTIC SCREEN ONLY**

## Why human review was suspended

The initial private semantic review displayed visibly nonsensical output even when EOS was emitted and UTF-8 decoding succeeded. A human rating for every example would add little diagnostic value at this stage. The previous human review pipeline remains intact for auditability but is **not** used here.

This stage tests whether the current V62 cycle-2 model generates recognizable English-like forms under the frozen V63 Top-k / Top-p decoder. It deliberately does not assign human semantic ratings.

## Verified results - 2026-10-31

GOGIT report --> [PHASE03-SMOLTALK-V63-AUTOMATIC-LANGUAGE-SCREEN-001](../reports/assistant-results/history/PHASE03-SMOLTALK-V63-AUTOMATIC-LANGUAGE-SCREEN-001.json)

Commit --> [`91c4a2f37dbe`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/91c4a2f37dbe43696d3d2d1aaa02996fc13a6d77)

| Indicator | Measured |
| --- | --- |
| Private generations analyzed | 24 |
| EOS terminations | 20 / 24 |
| Invalid UTF-8 | 0 / 24 |
| Rule-based suspect outputs | 10 / 24 |
| Outputs with zero regex-recognized words | 2 / 24 |
| Short nonstandard word-fragment ratio | 21.02% |
| Words outside limited 898-word reference lexicon | 41.11% |
| Token trigram repetition | 5.46% |
| Human review scores | 0 |

Result interpretation --> syntax, semantics, coherence and persona were **not** validated. The interrupted human-rating project remains incomplete. This screen provides only observable lexical and token-pattern signals.

The succeeding V64 audit confirmed that the pretrained model reduced next-token cross-entropy but still generated poor language. See [V64 closure and V65 readiness](MINI-KUZAI-PHASE-03-V64-CLOSURE-V65-READINESS-2026-10-31.md).

## Frozen inputs and protections

- Model --> frozen V62 cycle-2 checkpoint, stopped after 69 steps and 597982 exposed tokens
- Samples --> reuse the existing **24 private outputs** from V63 semantic review generation, or generate them once if missing
- Seeds --> 6301, 6303, 6305, 6308
- Prompts --> six fixed VALIDATION prompts, no BLIND TEST
- Decoder --> temperature 0.8, top-k 40, top-p 0.9, maximum 96 new tokens
- GPU --> CUDA/BF16 only if generation is needed
- Training --> no training, no checkpoint changes, no optimizer steps
- Private storage --> `/root/Mini-Kuzai/runs/v63-semantic-generation-review-001`, permissions 0700 and files 0600
- Historical human ratings --> not read, modified or synthesized

## Deterministic proxy metrics

For the 24 outputs, count -->

- EOS termination, UTF-8 validity, role-marker leakage, very short or maximum-length responses
- Token-level diversity and repeated trigrams / 8-grams
- Total words, alphabetic/whitespace character fractions
- Lexical overlap with a reference vocabulary derived from frozen VALIDATION conversations
- Unrecognized word share and short nonstandard word fragments
- Lexical overlap with the corresponding user prompt
- Count of suspicious outputs using predefined lexical-form thresholds

The reference vocabulary is a **bounded domain lexicon**, not a comprehensive English dictionary. Unrecognized words may be perfectly valid, and repeated words or low overlap do not prove lack of understanding. The suspicious-output counter is a screen for degraded surface form, **not a semantic classifier**.

No raw model output, prompt, source conversation, token list or human score is included in GOGIT.

## Run and GOGIT

Runner --> `tools/run_v63_automatic_language_screen_001_job.py`

Audit --> `tools/public-audits/phase03_v63_automatic_language_screen_001.py`

Unit tests --> `tests/test_phase03_v63_automatic_language_screen_001.py`

GOGIT step --> `PHASE03-SMOLTALK-V63-AUTOMATIC-LANGUAGE-SCREEN-001`

Execute from the checked-out Mini-Kuzai repository root on fhc2 -->

```bash
git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/run_v63_automatic_language_screen_001_job.py
```

Pipeline gates --> clean and synchronized Git main, V62 stopped and unlocked, frozen V63 robustness GOGIT report, passing CPU tests, private samples present or safely generated once, valid sample digest, numerical audit, GOGIT public metrics and remote-commit verification. Stop immediately on failure. Re-execution skips successfully published results.

## Interpretation contract

The GOGIT report explicitly sets -->

- `SEMANTIC_VALIDATION_COMPLETE=0`
- `TRAINING_AUTHORIZED=0`
- `TRAINING_STARTED=0`
- `V63_AUTO_HUMAN_RATINGS=0`
- `V63_AUTO_BLIND_ACCESS=0`

ChatGPT can then inspect the published numeric report directly on GitHub and analyze likely language-learning bottlenecks and next diagnostic priorities. It cannot reliably assess the meaning of each **private** response without access to its text and must not claim otherwise.

No new training objective, training run, BLIND access or broader model-quality claim is authorized by this stage.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
