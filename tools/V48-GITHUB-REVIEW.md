# Mini-Kuzai Phase 03 - V48 review directly on GitHub

## Purpose

Publish the 68 verified **external public SmolTalk** V46 review candidates into individually editable GitHub Markdown pages.

This mode is separate from the local terminal-review ledger. Do not merge local ledger decisions into these pages automatically. All GitHub review pages start with PENDING, regardless of any terminal or ChatGPT discussion.

Public source --> https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk

The upstream Smol-SmolTalk dataset card declares Apache-2.0 licensing. Keep the source attribution. Review redistribution obligations for particular upstream subsets before any broader dataset release.

## Strict data boundary

- The export reads ONLY the external public SmolTalk 8,000-record pool and the 68-case V46 public-source queue stored on fhc2.
- The exporter verifies record identities, source distribution, source dialogue text, V44 membership and queue categories before generating files.
- The exporter does NOT read private ChatGPT exports, the private conversation corpus or the V48 local human-review ledger.
- The public repository MUST NOT contain private ChatGPT conversation text, excerpts, derived summaries, candidate identifiers, or private review results.
- Do not paste any decision text or justification from a private ChatGPT conversation into a public review case.
- All source dialogue within each case is **public external dataset** material. GitHub is a public website --> published pages can be indexed and cloned.

## Export from the local server

First synchronize the clean main branch, then run this reviewed one-time exporter from the repository root with the existing Python venv -->

    python tools/publish_smoltalk_v48_github_reviews.py

It verifies source provenance, generates 68 Markdown files under -->

    reviews/smoltalk-v48/cases/

and a navigable index under -->

    reviews/smoltalk-v48/README.md

Then it stages **only those 69 files**, commits them, pushes to origin/main without force and verifies the remote revision. Repeated export is blocked if the folder already exists.

No review decision is made automatically.

## Edit reviews directly on GitHub

1. Open the published index at https://github.com/Kusanagi8200/Mini-Kuzai/tree/main/reviews/smoltalk-v48
2. Open a numbered case and read the complete public-source conversation.
3. Click GitHub's pencil editor for that file.
4. Replace the line Review status --> PENDING with Review status --> RETAIN, REJECT or HOLD.
5. Replace Review rationale --> NOT_REVIEWED with an explicit reason (12 to 2000 characters).
6. Commit the file change to main.

The original source conversation must remain unchanged. The audited status reader rejects any unexpected edits beyond those two fields.

Decision semantics -->
- RETAIN --> promising example for further human selection, NOT approved for TRAIN.
- REJECT --> unsuitable for this educational selection.
- HOLD --> needs a fact check, more context or another review.

## Read results using gogit

Once the 68 files have been exported, simply say "gogit" in ChatGPT. The assistant can navigate the public GitHub index, read complete public SmolTalk examples and help with independent quality assessment. The user can edit and approve review decisions through GitHub.

To publish numeric aggregate counters into the existing latest.json and history, run the dedicated approved audit on fhc2 -->

    python tools/gogit_public.py --step PHASE03-SMOLTALK-V48-GITHUB-INIT-001 --audit tools/public-audits/smoltalk_v48_github_progress.py

Each subsequent numeric publication requires an unused STEP_ID.

The GitHub progress script checks -->
- 68 exact cases matching the external public dataset source.
- Exactly one review status and rationale per case.
- Only the two editable lines may change.
- Reviewed statuses require meaningful justification.
- No TRAIN authorization is inferred.

The two review channels (terminal local ledger and GitHub Markdown reviews) are deliberately separate. **GitHub review pages are the canonical V48 workflow after the export**; the local ledger is not imported.

No Phase 03 training, official dataset split modification or tokenizer freeze is authorized by this publication.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
