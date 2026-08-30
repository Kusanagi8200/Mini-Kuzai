# MINI-KUZAI PHASE 01 — original lab snapshot

This directory preserves the Python source snapshot recovered from the local `/root/Mini-Kuzai` laboratory at the end of MINI-KUZAI PHASE 01.

It contains:

- 67 numbered experiment scripts: `01_tokenizer.py` through `67_beta_additive_identity.py`;
- the original `corpus.txt`;
- the original short `README.txt`, stored here as `README_ORIGINAL.txt`;
- the historical model implementations used by the numbered scripts.

The files are intentionally kept in one flat directory because many scripts use local imports such as:

```python
from mini_kuzai_padding import MiniKuzaiPadding
```

Keeping the historical modules beside the experiments preserves that execution model.

The `.pt` checkpoints referenced by later scripts are not committed to normal Git. Their SHA-256 inventory is stored in `technical/checkpoints/README.md`.

To run early experiments that only need the corpus:

```bash
cd tests/phase-01/lab
python 01_tokenizer.py
```

Later checkpoint-based experiments additionally require the matching local `.pt` file to be copied into this directory or otherwise made available under the filename expected by the script.
