# Mini-Kuzai Phase 03 - V49 HOLD resolution

## Scope and audit state

V49 re-examined the 14 remaining HOLD examples in the public external
SmolTalk V48 GitHub review queue. Each case was read directly from the
published public-source conversation and its two editable review fields
were updated in place. Git history retains the earlier V48 justification.

This is **AI-assisted qualitative triage of public external examples**,
not independent human validation, a model-training permission or final
statistical sampling of the wider reservoir.

## Changes from the V48 first pass

| V48 decision | V49 decision | Number |
|---|---|---:|
| HOLD | RETAIN | 1 |
| HOLD | REJECT | 13 |
| HOLD | HOLD | 0 |

The review resolved all outstanding HOLD cases. Key causes for rejection
included unsupported factual assumptions, invented query columns,
unjustified statistical conclusions, instruction-following defects,
contradictions within fiction, and explanations that reached correct
numbers through incorrect or misleading reasoning.

The single newly retained example provides a correct, directly useful
answer to a simple mathematics question, with a minor presentation
limitation. Its retention is provisional.

## Consolidated queue results

| Group | RETAIN | REJECT | HOLD | Total |
|---|---:|---:|---:|---:|
| RELABEL | 5 | 7 | 0 | 12 |
| RESCUE | 8 | 16 | 0 | 24 |
| BASE | 11 | 21 | 0 | 32 |
| **ALL** | **24** | **44** | **0** | **68** |

All 68 cases now have a final first-cycle triage disposition, but
a RETAIN label is **not** approval for TRAIN.

The 68 reviewed cases were intentionally sampled for a quality
diagnostic. They do not demonstrate a 24/68 acceptance probability for
the 1,139-record provisional V44 selection or the full 8,000-record
public-source SmolTalk candidate reservoir.

## Gates still outstanding

1. Reassess provisional V44 selection categories and quotas using
   lessons from the 68-case diagnostic, without artificially filling
   creative quotas.
2. Check deduplication, prompt-family leakage, conversation quality,
   factual validation and reserved evaluation split exclusions for
   candidates considered for final mixture design.
3. Complete representative external pool review rather than
   extrapolating a diagnostic sample rate.
4. Freeze final tokenizer vocabulary only when pool and mixture criteria
   are sufficiently stable.
5. Keep TRAIN, VALIDATION and BLIND allocations unchanged until their
   quality and contamination gates are separately satisfied.
6. Obtain explicit permission before any training run.

## Numeric publication through gogit

After pulling public main on fhc2, use the reviewed public-source audit
with a **fresh, one-time** STEP_ID:

```bash
python tools/gogit_public.py --step PHASE03-SMOLTALK-V49-HOLD-RESOLVED-001 --audit tools/public-audits/smoltalk_v48_github_progress.py
```

The audit checks that the original public dialogue remains identical to
the verified external SmolTalk reservoir, with only the status and
rationale fields changed. It publishes aggregate counters only.

The V48 first-pass report remains available at
[V48-REVIEW-RESULTS.md](V48-REVIEW-RESULTS.md) as historical evidence.
The current case source of truth remains
[the public review index](README.md).

TRAIN approved: zero. Tokenizer frozen: no. Training authorized: no.
