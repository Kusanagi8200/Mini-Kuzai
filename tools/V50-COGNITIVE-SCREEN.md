# V50 - cognitive/creative screening of the public V44 selection

This tool follows the [V50 selection direction](../phases/MINI-KUZAI-PHASE-03-V50-COGNITIVE-CREATIVE-PRIORITY.md).

## What it does

`tools/public-audits/smoltalk_v50_cognitive_screen.py` validates the entire
8,000-record **public external** SmolTalk v0.4 reservoir and the unchanged
1,139-record V44 provisional selection. Every V44 candidate must match the
original public record, its known source, its original user/assistant turns,
and its non-TRAIN status. The historical selected turn structure must remain
679 multi-turn plus 460 single-turn.

It then creates a deterministic local review queue for **all 1,139 V44
candidates** ordered by recall-oriented priority hints, not by demonstrated
quality:

- HIGH: creative or cognitive user signals plus multi-turn feedback or
  an explicit follow-up reference;
- MEDIUM: creative/cognitive signals or weaker dialogue references;
- LOW: other items, including many narrow technical questions.

Technical examples are not automatically rejected. A keyword hit does
not demonstrate genuine reasoning, coherence or successful correction,
and keyword absence does not demonstrate the opposite.

The tool does **not** grade accuracy, assign A/B/C quality labels,
approve TRAIN, alter V44, freeze a tokenizer, or change any model weights.

## Output boundary

The complete queue and its structured hints remain on `fhc2`, outside
the Git repository:

```text
/root/Mini-Kuzai/data/external/smol-smoltalk/review/v50-cognitive-review-priority.jsonl
/root/Mini-Kuzai/data/external/smol-smoltalk/review/v50-cognitive-review-summary.json
```

The queue contains the public external conversation text for human review.
It must **not** be copied into public reports by the audit command.

Only numeric counters are eligible for public `gogit`:
queue length, priority groups, the prevalence of lexical signals, number
of multi-turn items, zero reviewed, and zero approved for TRAIN.

No private ChatGPT export, private-derived data, or private source
statistics are used. The original V48/V49 GitHub case decisions and
their commit history remain unchanged.

## Execute on fhc2

Requirements: local Python venv `/root/Mini-Kuzai/.venv`, clean
`main` branch at `/root/GitHub-Mini-Kuzai/Mini-Kuzai`, and existing
public SmolTalk v0.4 source and V44 files.

1. Create a timestamped Git backup branch, then update from the remote
   using `git pull --ff-only origin main`.
2. Validate syntax and run the six **offline** unit tests:

```bash
/root/Mini-Kuzai/.venv/bin/python -m py_compile tools/public-audits/smoltalk_v50_cognitive_screen.py tests/phase-03/test_smoltalk_v50_screen.py
/root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v50_screen.py' -v
```

3. Run this one-time audit from the clean repository root:

```bash
/root/Mini-Kuzai/.venv/bin/python tools/gogit_public.py --step PHASE03-SMOLTALK-V50-COGNITIVE-SCREEN-001 --audit tools/public-audits/smoltalk_v50_cognitive_screen.py
```

The audit will create local-only queue artifacts, then commit and push
four **numeric-only** `reports/assistant-results` files using the
existing controlled `gogit` mechanism. Do not rerun the one-time
screening after success: existing queue files intentionally block
overwriting. If any command fails, inspect the reported error and
do not delete an existing queue without assessing its state.

4. Request `gogit` to confirm the published numeric counters.

## After the numeric audit

The 1,139 records are **prioritized, not semantically evaluated**.
Actual V50 work must sample and inspect complete conversations from
different priority groups and source categories. Keep the quality rubric
independent from the V48/V49 historical verdicts. Only subsequently
reviewed, public-external cases may be published for direct GitHub
discussion, and no publication may include private-source text or
derived private information.

Never claim that a high-priority hint means a high-quality model target.
The V50 heuristics do not grant permission to start training.
