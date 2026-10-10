# MINI-KUZAI PHASE 03 - PAUSE CHECKPOINT 2026-10-10

Status: PAUSED - DATA PREPARATION ONLY
Last public analytical step: `PHASE03-SMOLTALK-V46-CREATIVE-001`
Latest published audit: [SmolTalk V46 numerical report](../reports/assistant-results/history/PHASE03-SMOLTALK-V46-CREATIVE-001.json)

## Scope and publication boundary

This checkpoint records only project status, public external SmolTalk audit aggregates, and the generic workflow. No private conversation text, private-source metadata, private-source statistics, curated private candidates, or private review results are published.

External SmolTalk examples and review queues used for sampling remain on the local server and are not committed to GitHub.

## External SmolTalk progress

The validated SmolTalk v0.4 candidate reservoir contains 8,000 records from four external subsets. The reservoir remains distinct from an approved TRAIN dataset.

| Step | Public result | Interpretation |
| --- | --- | --- |
| V41 | 128 context-reference candidates identified in the multi-turn subset | Lexical heuristic only |
| V42 | 95 two-anchor, 24 partial-anchor, 9 low-anchor candidates | Not a semantic-continuity assessment |
| V43 | Follow-up and writing-related signals reviewed by heuristic classification | Writing-heavy sample; no TRAIN approval |
| V44 | 1,139 / 1,200 stratified candidates, including 679 multi-turn and 460 single-turn | Provisional local selection, not training-ready |
| V45 | 69 / 130 creative-label quota, shortfall 61 | Shortfall reflects the V44 labeling and sampling constraints |
| V46 | 339 broad creative signals across the external reservoir | Broader heuristic may include false positives |

V46 additionally identified 47 broad creative signals among V44 records labeled under other domains and 234 in records not selected by V44. These are potential review candidates, not 281 validated creative examples.

The local V46 review queue contains 68 records: 32 category-baseline samples, 12 possible reclassifications, and 24 possible candidate recoveries. This review has **not** produced human semantic approval, factual approval, or changes to the V44 selection.

## Public reporting workflow - gogit

Working directory: `/root/GitHub-Mini-Kuzai/Mini-Kuzai`.
The Python virtual environment at `/root/Mini-Kuzai/.venv` can be activated while working inside the Git repository.

The public audit publication process is:

```text
reviewed tools/public-audits/*.py on fhc2
    -> local analysis of external public SmolTalk
    -> numeric-only allowlisted result
    -> tools/gogit_public.py
    -> reports/assistant-results/latest.json and latest.txt + history
    -> checked Git commit and push on main
    -> user writes "gogit" to request report retrieval
```

The wrapper publishes only when deliberately invoked; no recurring task is installed. Each new audit script must be reviewed for data provenance before publication. Neither `gogit` nor the numeric-output allowlist is authorization to publish privately sourced results.

See [gogit workflow documentation](../tools/GOGIT.md).

## Project state at pause

- Phase 01 reference checkpoint remains frozen; Phase 02 KV-cache research is preserved.
- Phase 03 custom authoring remains paused after B05. Its existing semantic split guard remains in force.
- SmolTalk v0.4 is a validated external **candidate reservoir**. The V44 subset is **provisional**.
- Private conversation curation is a local-only research workflow. No private-source data or source-derived measurements belong in the public repository.
- VALIDATION and BLIND TEST text sets for the new Phase 03 run have not been completed.
- Tokenizer design is under preparation; the definitive model vocabulary is **not frozen**.
- Phase 03 model architecture and training mixture are not finalized.
- **No Phase 03 model training has started or been authorized.**

## Exact resume point

**V47 - local quality review of the external public dataset**, beginning with the 36 targeted V46 items (12 reclassification candidates and 24 candidate recoveries), then covering the 32 baseline samples.

Review each full conversation for actual multi-turn continuity, educational utility, factual accuracy, domain labeling, topic switching, and overlap with reserved evaluation families. Record reproducible human decisions locally. Do not treat a keyword match, lexical score, or generated answer as approval.

After V47, reconsider the V44 quotas and selection only if supported by the reviewed evidence. Then complete training/validation/blind partition rules, authorize an actual TRAIN corpus, select the representative tokenizer training material, freeze and test the tokenizer, and choose an architecture before asking for separate training authorization.

## Pause rule

Stop work at this checkpoint. Do not launch dataset modification, tokenizer retraining, model training, automated monitoring, or additional GitHub publication until the user explicitly requests resumption.
