# Mini-Kuzai Phase 03 - V63 Automatic Language Screen 001

Status --> **AUTOMATED, NONSEMANTIC DIAGNOSTIC PREPARED / NOT YET EXECUTED**

## Why human review was suspended

The initial private semantic review displayed visibly nonsensical output even when EOS was emitted and UTF-8 decoding succeeded. A human rating for every example would add little diagnostic value at this stage. The previous human review pipeline remains intact for auditability but is **not** used here.

This stage tests whether the current V62 cycle-2 model generates recognizable English-like forms under the frozen V63 Top-k / Top-p decoder. It deliberately does not assign human semantic ratings.

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
