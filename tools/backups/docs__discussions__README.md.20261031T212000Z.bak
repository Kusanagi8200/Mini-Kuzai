# Mini-Kuzai - GitHub Discussions publication workflow

Status --> **THREE HISTORICAL POSTS TRANSFERRED / VXX START AND GOGIT CLOSURE PUBLISHER IMPLEMENTED - LOCAL TESTS PENDING**

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

## Future Vxx discussion workflow

The [Vxx publisher](../../tools/github_discussions_step.py) implements two explicit operations. It always targets `Kusanagi8200/Mini-Kuzai`, category `Development Log`. The [historical publisher](../../tools/github_discussions_history.py) remains separate and should not be used to start Vxx research.

An approved, committed start Markdown file is required before publishing a new research step. The script will not invent a scientific objective and does not automatically authorize training or BLIND access. No V74 draft or discussion has been created by this implementation.

### START Vxx - approved Markdown

Prepare `docs/discussions/steps/V74-start.md` on a reviewed commit of main. The filename and version must match the selected Vxx. Example structure, with research-specific text completed and validated before any publication -->

```markdown
# Mini-Kuzai | V74 - Reviewed research objective

```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : V74
  STATUS   : EXPERIMENT STARTED
========================================================================
```

## Objective

Describe the approved scientific question, baseline, frozen data, method, scope, stop conditions and expected validation without claiming any unverified result.

## Protocol

Explain the exact authorized experiment and reproducibility safeguards. Keep private input data, credentials, unpublished conversations and protected evaluation content out of the post.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
```

After the reviewed draft is committed, pull main on fhc2 and run the **read-only simulation** -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_step.py --step V74 --action start
```

Only if the output reports `START=READY_TO_CREATE` or `START=EXISTS_IDENTICAL`, and the draft is correct, explicitly publish -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_step.py --step V74 --action start --publish
```

Both commands require a clean `main` that matches `origin/main`, including a remote SHA check. The existing category is scanned before writes. A changed title or body for an already-published Vxx blocks the operation rather than creating a duplicate.

### GOGIT Vxx - verified aggregate closure

After the GOGIT public audit is published, identify its immutable file under `reports/assistant-results/history/` with the exact `PHASE03-SMOLTALK-V74-...json` filename. The publisher verifies its step identity, public aggregate status, PASS metric, zero BLIND access, producer SHA256, committed-file integrity and absence of private conversation data. It constructs a **numerical evidence comment** automatically with a pinned Git commit URL, the verified metric table and explicit interpretation limits. It does not infer conversational performance from a numeric PASS.

Simulate with the report's full real filename (placeholder shown below) -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_step.py --step V74 --action close --report reports/assistant-results/history/PHASE03-SMOLTALK-V74-REPLACE-WITH-REAL-STEP-ID.json
```

Once validated and deliberately authorized, append the comment **to that same discussion** -->

```bash
/root/Mini-Kuzai/.venv/bin/python tools/github_discussions_step.py --step V74 --action close --report reports/assistant-results/history/PHASE03-SMOLTALK-V74-REPLACE-WITH-REAL-STEP-ID.json --publish
```

An already-identical START or closure is skipped. A conflicting existing comment blocks publication. Closing a step with no corresponding verified START discussion is prohibited. The workflow does not monitor GitHub automatically and does not invoke any paid OpenAI API.

Run the regression suite before using the new workflow -->

```bash
/root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests -p 'test_github_discussions_*.py' -v
```

Tests being present in GitHub is not proof that the local suite passed; record an actual PASS before live deployment.

The fixed ASCII header includes `PROJECT`, `PHASE`, `STEP` and `STATUS`. Research notes and evaluation claims remain subject to review; numerical GOGIT pass metrics do not demonstrate semantic learning or a coherent persona.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
