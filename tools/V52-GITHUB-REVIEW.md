# Mini-Kuzai Phase 03 - V52 public semantic-review batch

Status as of 2026-10-11: **32 public V52 review cases exported, individually annotated and published on GitHub (8 A, 12 B, 12 C). Final source-integrity/numeric GOGIT audit remains pending.** See [V52 results](../reviews/smoltalk-v52/RESULTS-001.md).
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

The 32 case pages were originally published with nine `PENDING` review fields: grade, rationale, cognition, creativity, continuity, correction, communication, factual risk, and instruction fit. They have since all been annotated on GitHub. Review the *whole*
original dialogue before assigning A/B/C/HOLD. A factual defect is
not automatically disqualifying for behavioral analysis, but an
uncorrected false assertion is not an approved positive target.
No independent human assessment is implied.

## Execution history and final GOGIT gate

**Completed on fhc2:**

1. The source-verifying exporter published 32 new public V52 cases under GitHub commit [`bef66d09`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/bef66d092f702073072e07084848ef5d3d52fff0).
2. The initial numeric-only GOGIT audit [`PHASE03-SMOLTALK-V52-REVIEW-INIT-001`](../reports/assistant-results/history/PHASE03-SMOLTALK-V52-REVIEW-INIT-001.json) confirmed 32 public cases, initially 32 PENDING.
3. Eight HIGH cases were annotated, and GOGIT [`PHASE03-SMOLTALK-V52-REVIEW-PROGRESS-001`](../reports/assistant-results/history/PHASE03-SMOLTALK-V52-REVIEW-PROGRESS-001.json) captured **8 reviewed / 24 pending**.
4. The remaining 24 public V52 cases were subsequently annotated directly on GitHub; the last case commit is [`7e27e730`](https://github.com/Kusanagi8200/Mini-Kuzai/commit/7e27e73033fdf6ab9bce227c379e4b00794af925). Their individual case pages show 8 A, 12 B, 12 C across the full 32-case batch.

**Still pending:** `PHASE03-SMOLTALK-V52-REVIEW-FINAL-001` was not found in the public audit history as of this documentation checkpoint. The GOGIT `latest.json` record is therefore an earlier 8/32 snapshot, not a contradiction in the case annotations. Never change it by hand to imply an audit that has not run.

At the next authorized resumption, run this **final audit only** on fhc2, from a clean and synchronized `main`:

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai && git pull --ff-only origin main && /root/Mini-Kuzai/.venv/bin/python tools/gogit_public.py --step PHASE03-SMOLTALK-V52-REVIEW-FINAL-001 --audit tools/public-audits/smoltalk_v52_github_progress.py
```

Do not re-run the one-time V52 source exporter: it refuses an already existing destination. GOGIT will verify the source immutability and the nine review fields before writing numerical reports. If it fails, diagnose before retrying; never force-push or forge an audit. No terminal results need to be pasted into ChatGPT: after execution, request `gogit` to inspect the published record.

The [V52 results](../reviews/smoltalk-v52/RESULTS-001.md) and [V52 case index](../reviews/smoltalk-v52/README.md) preserve the current GitHub-annotated status until that final report exists.

## Future steps

The 32 public V52 cases are already annotated. The next required gate is the **one-time final source-integrity/numeric GOGIT audit**, followed by documentation of any discrepancies. Do not re-export or relabel the cases merely to change aggregate totals. Only after that validation should candidate segmentation, factual repair, leakage checks, and broader semantic sampling resume.

Do not change official TRAIN/VALIDATION/BLIND, the final tokenizer, or
model architecture. Phase 03 training remains unauthorized.
