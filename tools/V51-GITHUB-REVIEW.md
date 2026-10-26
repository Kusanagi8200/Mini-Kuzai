# V51 - Public SmolTalk semantic review on GitHub

This stage follows the confirmed [V50 numeric screening report](../reports/assistant-results/history/PHASE03-SMOLTALK-V50-COGNITIVE-SCREEN-001.json)
and the [V51 semantic review plan](../phases/MINI-KUZAI-PHASE-03-V51-SEMANTIC-REVIEW.md).

V50 processed 1,139 provisional V44 candidates with 200 HIGH, 431
MEDIUM and 508 LOW **heuristic** priority hints. It did not complete
any human or assistant semantic review of those 1,139 cases.

## V51 first batch

The one-time publisher `tools/publish_smoltalk_v51_github_reviews.py`
will create 24 new, independently editable public case files -->

- 12 from HIGH
- 6 from MEDIUM
- 6 from LOW.

It attempts source and V44 category coverage within each band, excludes
all 68 published V48/V49 diagnostic cases and uses a deterministic
public-content SHA-256 ordering. The actual conversations must be read
before assigning any A/B/C grade. A HIGH priority does not mean A
quality, and a LOW priority does not mean C quality.

The publisher reads **only** the public external SmolTalk pool, the
existing V44 and V50 local public-source files, and the previously
published V48 public case filenames. It verifies 8,000 external source
records, 1,139 unchanged V44/V50 candidates, and the V50 priority
counts (200/431/508). It neither reads private ChatGPT exports nor
publishes any private-derived information.

The export is one-time only --> it refuses an existing destination, an
unclean branch, or an unsynchronized main. The new public conversations
will appear under `reviews/smoltalk-v51/cases/` on GitHub.

## Human-style review fields

Each V51 page starts with nine editable fields. The reviewer supplies -->

- `V51 grade` --> A, B, C or HOLD (PENDING before review).
- `V51 rationale` --> specific English explanation, 12-2000 characters.
- `V51 cognition`, `creativity`, `continuity`, `correction`,
  `communication` --> score 0, 1, 2 or 3.
- `V51 factual risk` --> LOW, REVIEW or HIGH.
- `V51 instruction fit` --> GOOD, PARTIAL or BAD.

Only these nine fields may change. The original dialogue, SHA-256,
source, V44 heuristic and V50 priority must remain untouched. A
completed case requires all scores, both final qualifiers and rationale.

A = potentially useful intact behavioral candidate after later data
gates; B = behaviorally useful, but requires explicit segmentation or
repair; C = unsuitable as a positive target; HOLD = unresolved.

The scores measure evidence in text, not mental states. A/B/C is an
AI-assisted research disposition, not independent human validation.

## Run the one-time publisher on fhc2

Execute from `/root/GitHub-Mini-Kuzai/Mini-Kuzai`, with Python at
`/root/Mini-Kuzai/.venv/bin/python`.

First ensure the Git checkout is clean, create a timestamped backup
branch, and fast-forward to current remote main. Run syntax checks and
the offline V51 unit tests before invoking the publisher -->

```bash
/root/Mini-Kuzai/.venv/bin/python -m py_compile tools/publish_smoltalk_v51_github_reviews.py tools/public-audits/smoltalk_v51_github_progress.py tests/phase-03/test_smoltalk_v51_publisher.py tests/phase-03/test_smoltalk_v51_progress.py
/root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v51_*.py' -v
/root/Mini-Kuzai/.venv/bin/python tools/publish_smoltalk_v51_github_reviews.py
```

The publisher commits and pushes ONLY the 24 public case files and
their public review index. It prints `##### SECTION RESULTS FOR ASSISTANT ######`
followed by counts and the Git commit. Do not copy conversations into
the chat, do not rerun the exporter after success, and never force-push.

## After GitHub review

The audit `tools/public-audits/smoltalk_v51_github_progress.py`
recreates the exact 24 public cases, verifies that only nine review
fields differ, validates the scoring rules, and emits numeric counts
only. From a clean synchronized main, publish the final numeric
counters with an unused `--step` identifier -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/gogit_public.py --step PHASE03-SMOLTALK-V51-PILOT-REVIEW-001 --audit tools/public-audits/smoltalk_v51_github_progress.py
```

Do not run the numeric audit before cases exist; subsequent progress
reports require unique STEP_IDs and successful local validation.

TRAIN, VALIDATION and BLIND splits remain unchanged. Final tokenizer
selection and Phase 03 model training remain unauthorized.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
