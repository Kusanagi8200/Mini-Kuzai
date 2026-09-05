# MINI-KUZAI PHASE 03 - EXTERNAL POOL V0.4 AUDIT

Version: 0.1
Status: NEEDS REVIEW

## Build result

The v0.4 external candidate pool was rebuilt from the v0.3a persona-clean base after applying the validated strict duplicate removals.

Base records after strict duplicate removal: 7903

Replacement requirement:

- smol-magpie-ultra-short: 94
- openhermes-50k: 3
- explore-instruct-rewrite: 0
- self-oss-instruct: 0

All 97 required replacements were found.

Final source counts:

- smol-magpie-ultra-short: 5000
- openhermes-50k: 1500
- explore-instruct-rewrite: 500
- self-oss-instruct: 1000
- total: 8000

## Final audit

The following checks passed:

- duplicate content extra: 0
- duplicate prompt extra: 0
- generic residual: 0
- benchmark residual: 0
- Unicode dash residual: 0
- strict duplicate pairs: 0

The following check failed:

- persona residual: 7

Because persona residual is non-zero, v0.4 is not approved for training.

## Interpretation

The strict deduplication and replacement mechanism behaved correctly. The remaining problem is narrow and isolated to seven records matched by the expanded persona rules.

The next step is a targeted persona audit. It must identify each of the seven records, the exact matched pattern, the source, provenance, and whether the record was retained from v0.3a or added as a v0.4 replacement.

No automatic deletion or training should occur until these seven records have been inspected.
