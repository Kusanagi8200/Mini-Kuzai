# Mini-Kuzai Phase 03 - V48 human review (local only)

Status --> tool published; review progress is **not** automatically assumed.
Prerequisite --> V47 local integrity audit of the V46 SmolTalk queue passed.

## Purpose

V48 is a **human qualitative triage** of 68 conversations from the public external SmolTalk v0.4 reservoir. The priority order is 12 RELABEL, 24 RESCUE, then 32 BASE reference cases.

Human review is needed to evaluate real continuity, useful corrections, domain classification, answer quality, factual claims, topic shifts, and split/contamination risks. Heuristic source labels alone do not approve any example.

## Local files and security boundary

The interactive reader is `tools/local-review/smoltalk_v48_review.py`.
It reads the complete conversation from the existing local
`/root/Mini-Kuzai/data/external/smol-smoltalk/review/v46-manual-review-queue.jsonl`.

The first confirmed decision creates this **local-only** append-only ledger -->

```text
/root/Mini-Kuzai/data/external/smol-smoltalk/review/v48-human-review-ledger.jsonl
```

Each event holds only the public-source conversation fingerprint, decision, human justification, timestamp and revision. Corrections append another event instead of destroying history. The review ledger, justifications and complete conversations stay outside the public Git checkout.

Each decision has three possible values -->
- `RETAIN` --> a human thinks the example is useful for further selection.
- `REJECT` --> a human rejects the example.
- `HOLD` --> the example needs additional investigation, especially factual checking.

**RETAIN does not authorize TRAIN**, does not assign a training/validation/blind split, and does not certify factual accuracy. Those gates remain separate.

## Terminal workflow on fhc2

From the Git repository root, with the existing venv active -->

```bash
python tools/local-review/smoltalk_v48_review.py --status
python tools/local-review/smoltalk_v48_review.py --next
```

`--next` prints one entire conversation locally and prompts for a decision and a mandatory justification, followed by an explicit confirmation. `SKIP` leaves the candidate unreviewed. Run again to review the next candidate. To change a recorded decision and keep its history -->

```bash
python tools/local-review/smoltalk_v48_review.py --revise UNIQUE_SHA_PREFIX
```

Back up the local ledger outside Git before administrative file operations. Never add this ledger or any full source conversation to the public repository.

## Public progress publication

The read-only `tools/public-audits/smoltalk_v48_progress.py` reads the V46 queue and the local V48 ledger, validates the decision-event schema and publishes **numbers only**.

To publish a first baseline report (a STEP_ID may only be used once) -->

```bash
python tools/gogit_public.py --step PHASE03-SMOLTALK-V48-INIT-001 --audit tools/public-audits/smoltalk_v48_progress.py
```

Subsequent progress publications use a distinct new STEP_ID for each run, such as `PHASE03-SMOLTALK-V48-REVIEW-002`.

After a successful verified push, write `gogit` in the ChatGPT conversation to request reading `reports/assistant-results/latest.json`.

This process is manually triggered and has no automatic schedule. No private conversation source or private-derived statistic may be used as an input to public audit scripts.

## Next scientific gates

1. Finish priority triage (36 records), then inspect the 32 category-baseline cases.
2. Verify the rationale, possible false positives, factual claims and class distribution.
3. Reconsider the V44 provisional selection using evidenced human decisions, without auto-filling quotas.
4. Separate TRAIN, VALIDATION and BLIND examples and complete contamination controls.
5. Freeze a representative tokenizer vocabulary and select model architecture **only after** the dataset quality decisions.
6. Require explicit authorization before any Phase 03 training.

Latest historical V47 integrity results can be found under `reports/assistant-results/history/PHASE03-SMOLTALK-V47-INTEGRITY-001.json`.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
