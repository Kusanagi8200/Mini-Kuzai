# Mini-Kuzai Phase 03 - V52 public semantic-review batch

Status: **32-case exporter and GOGIT progress audit prepared, not yet executed on fhc2**.
The [V52 inventory](../reports/assistant-results/history/PHASE03-SMOLTALK-V52-INVENTORY-001.json)
was published and verified on GitHub under commit `3c1ca914`.

## Why this batch

V52 inventory verified 1,071 eligible V44 candidates after excluding 44
earlier V48 in-V44 cases (32 BASE + 12 RELABEL) and 24 V51 reviewed cases.
The additional 24 V48 RESCUE cases were outside V44, not eligible for
subtraction from its 1,139 candidates.

This 32-case **stratified pilot** allocates 8 HIGH, 12 MEDIUM and 12 LOW
V50 heuristic priorities; 75% comes from MEDIUM/LOW to study false
negatives. Non-Smol-Magpie examples give source diversity but generally
contain only one user/assistant exchange. Hence selection is **not a
representative probability sample**, a measured success rate, or an
admission to TRAIN.

| Source | HIGH | MEDIUM | LOW | Total |
| --- | ---: | ---: | ---: | ---: |
| smol-magpie-ultra-short | 8 | 6 | 6 | 20 |
| openhermes-50k | 0 | 3 | 3 | 6 |
| self-oss-instruct | 0 | 1 | 2 | 3 |
| explore-instruct-rewrite | 0 | 2 | 1 | 3 |
| **Total** | **8** | **12** | **12** | **32** |

The deterministic seed, SHA ordering and per-source quotas are
independent from V51. Within each source/priority stratum, distinct
V44 categories are sampled before filling remaining slots. This is
sampling for **human-style semantic assessment**, not heuristic
selection of verified good conversations.

## Immutable source and privacy boundary

The publisher uses ONLY external-public SmolTalk v0.4 records from
`/root/Mini-Kuzai/data/external/smol-smoltalk`, source-verified
V44/V50 records, prior published V48/V51 public cases, and the V52
numeric inventory history. It refuses an unclean or diverged main,
revalidates all source records and original V51 pages, and refuses to
overwrite an existing V52 export. Git stages only
`reviews/smoltalk-v52/cases/*.md` and the corresponding README.

It does **not** read, inspect, publish or derive information from
private ChatGPT exports. Public reviewed source conversations and
source attribution may be placed on GitHub; all other datasets remain
local. Prior published files remain unchanged.

All 32 newly published cases begin `PENDING` with nine editable V52
fields: grade, rationale, cognition, creativity, continuity, correction,
communication, factual risk, and instruction fit. Review the *whole*
original dialogue before assigning A/B/C/HOLD. A factual defect is
not automatically disqualifying for behavioral analysis, but an
uncorrected false assertion is not an approved positive target.
No independent human assessment is implied.

## One-command fhc2 execution

Run from a clean local main, using the existing verified Python venv.
The command fast-forwards the repository, checks Python syntax, runs
all offline V52 tests, publishes the 32 public review pages with the
source-verifying publisher, and publishes numeric-only pending/progress
counters through GOGIT. Every stage stops on failure.

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai && git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python -m py_compile tools/publish_smoltalk_v52_github_reviews.py tools/public-audits/smoltalk_v52_github_progress.py tools/gogit_public.py tests/phase-03/test_smoltalk_v52_publisher.py && /root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v52_publisher.py' -v && /root/Mini-Kuzai/.venv/bin/python tools/publish_smoltalk_v52_github_reviews.py && /root/Mini-Kuzai/.venv/bin/python tools/gogit_public.py --step PHASE03-SMOLTALK-V52-REVIEW-INIT-001 --audit tools/public-audits/smoltalk_v52_github_progress.py
```

Do not paste terminal results into ChatGPT. Reply `gogit` after execution.
Read the published state directly from:

- `reviews/smoltalk-v52/README.md`
- `reviews/smoltalk-v52/cases/`
- `reports/assistant-results/history/PHASE03-SMOLTALK-V52-REVIEW-INIT-001.json`

GOGIT publishes only approved numeric counters and creates an automatic
local timestamped backup of previous `latest` reports.

If a command fails, the next action is diagnosis, not automatic
retry or force-push. An initial V52 case publication may succeed while
the later GOGIT numeric report fails; inspect GitHub before retrying
a publisher that deliberately refuses any existing V52 cases.

## Future steps

After a 32-case GitHub publication, review the 32 independent cases
for reasoning, creative expression, conversational continuity and
responsive correction. Verify annotations through the immutable-source
numeric audit with a **new** STEP_ID for each report.

Do not change official TRAIN/VALIDATION/BLIND, the final tokenizer, or
model architecture. Phase 03 training remains unauthorized.
