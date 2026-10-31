# Mini-Kuzai - GitHub Discussions publication workflow

Status --> **THREE HISTORICAL POSTS TRANSFERRED TO MINI-KUZAI / FUTURE VXX WORKFLOW NOT YET IMPLEMENTED**

Publication target --> [Kusanagi8200/Mini-Kuzai Discussions](https://github.com/Kusanagi8200/Mini-Kuzai/discussions)

Category --> `Development Log` (`DIC_kwDOUI2cC84DKGl8`)

Source repository --> `Kusanagi8200/Mini-Kuzai` (`R_kgDOUI2cCw`)

## Historical introduction series

| Order | GitHub discussion title | Source | Published discussion |
| --- | --- | --- | --- |
| 01 | Mini-Kuzai - Why Build a Language Model From Scratch? | [Origins](history/01-origins.md) | [Discussion #2](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/2) |
| 02 | Mini-Kuzai - From a Transformer to a Developing AI Personality | [Learning design](history/02-learning-design.md) | [Discussion #3](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/3) |
| 03 | Mini-Kuzai - What the First Training Experiments Revealed | [Training results through V73](history/03-first-training-results.md) | [Discussion #4](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/4) |

The actual GitHub discussion titles use `Mini-Kuzai | 01`, `| 02` and `| 03` for predictable deduplication. Each body starts with the exact ASCII terminal-style header approved for the project. All contents are public and refer only to documented project milestones. Historical publication originally completed on `Kusanagi8200/KuzAI`, with the local `--publish` run reporting `CREATED=3` and `PUBLICATION=VERIFIED`. The operator subsequently transferred the three discussions to `Kusanagi8200/Mini-Kuzai`, selected category `Development Log`, and verified all three destinations using a GitHub GraphQL query. Their current links are recorded above. The central announcement remains [Mini-Kuzai - Live Dev Flow](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/1), in its own category.

## Local execution on fhc2

GitHub CLI `gh` authenticates the GraphQL requests using the operator's existing session. This workflow does not request, store or print a GitHub token or an OpenAI API key.

The historical publisher is [tools/github_discussions_history.py](../../tools/github_discussions_history.py). It is **read-only by default**.

First, run offline CPU tests and an online read-only inventory/preflight -->

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai
/root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests -p 'test_github_discussions_history.py' -v
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_history.py --dry-run
```

Historical posts already exist and were transferred. Do not rerun live publication unless recovering a genuinely missing historical discussion after manual review. For future work, continue with the dedicated Vxx workflow once implemented. The historical script retains the explicit write option -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_history.py --publish
```

The publisher checks repository identity, permission, category and every page of existing discussions; verifies content and the standard ASCII header; compares exact titles and Markdown bodies; refuses to overwrite a conflicting discussion; and rechecks GitHub after each creation. Re-running `--publish` should detect and skip identical discussions. If a discussion title exists with a different body, the script refuses to overwrite it; verify any body differences before attempting a historical recovery. No live historical publication is necessary after transfer.

This script **does not create issues or pull requests** and does not modify Mini-Kuzai model code, datasets, checkpoints or GOGIT reports.

## Future Vxx discussions

With historical publication completed, the intended workflow is one discussion per Vxx: initial post at the start of a step, then a comment after its GOGIT numerical report is independently verified. Future step-opening/comment-closing commands need separate implementation and verification; the historical publisher does not claim to support them yet.

The fixed ASCII heading uses `PROJECT`, `PHASE`, `STEP`, and `STATUS`, with status changed for started, blocked, or GOGIT-verified experiments. A numeric GOGIT PASS must never be presented as semantic or conversational validation without independent evidence.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
