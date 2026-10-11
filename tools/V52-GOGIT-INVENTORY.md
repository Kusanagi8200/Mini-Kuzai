# Mini-Kuzai Phase 03 - V52 public inventory through GOGIT

Status: audit script and offline checks published; **V52 inventory not yet executed**.

## Scope

This is a numeric-only inventory for the next persona-first semantic-review batch. It uses only the already verified public external SmolTalk v0.4 reservoir, V44/V50 provisional queue, 68 public V48/V49 review dossiers, and 24 public V51 reviews. It neither reads private ChatGPT conversations nor publishes dialogue excerpts, identifiers, SHA hashes or sample contents.

The audit revalidates source integrity and exact V51 published cases before excluding cases previously published in V48 or V51. It emits exactly 30 allowlisted counters: total V50 population, earlier exclusions, remaining candidates, multi-turn count, and a per-priority / per-source total and multi-turn breakdown. The numbers are **heuristic candidate inventory only**, never semantic quality or permission for training.

The results are published using the existing `tools/gogit_public.py`, with its clean-synchronized-main preflight, timestamped backup of previous latest reports, numeric-only validation, restricted four-file commit, push, and remote confirmation.

## Execution on fhc2

Working tree: `/root/GitHub-Mini-Kuzai/Mini-Kuzai`.
Python: `/root/Mini-Kuzai/.venv/bin/python`.

First update only a clean checkout from the remote main:

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai && git pull --ff-only origin main
```

Then run the offline tests and publish the one-time result (only if tests succeed):

```bash
cd /root/GitHub-Mini-Kuzai/Mini-Kuzai && /root/Mini-Kuzai/.venv/bin/python -m py_compile tools/public-audits/smoltalk_v52_inventory.py tools/gogit_public.py tests/phase-03/test_smoltalk_v52_inventory.py && /root/Mini-Kuzai/.venv/bin/python -m unittest discover -s tests/phase-03 -p 'test_smoltalk_v52_inventory.py' -v && /root/Mini-Kuzai/.venv/bin/python tools/gogit_public.py --step PHASE03-SMOLTALK-V52-INVENTORY-001 --audit tools/public-audits/smoltalk_v52_inventory.py
```

**No terminal results need to be pasted into ChatGPT.** Read the result directly from GitHub after the command:

- `reports/assistant-results/latest.json`
- `reports/assistant-results/history/PHASE03-SMOLTALK-V52-INVENTORY-001.json`

If publication fails, GOGIT does not claim success. Check the local failure before attempting any change; never force-push or rerun an already published STEP_ID.

## Next decision

Use confirmed inventory counts to design a distinct, stratified V52 semantic review, with deliberate attention to LOW/MEDIUM false negatives, context retention, behavioral self-correction, humor and creative continuity. Maintain source balance and review the full examples before grading.

TRAIN, VALIDATION, BLIND and the tokenizer remain unchanged. Model training is not authorized.
