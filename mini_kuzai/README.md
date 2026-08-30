# Mini-Kuzai model code

This directory contains the clean model implementations produced during MINI-KUZAI PHASE 01.

## Implementations

- `mini_kuzai.py` — original single-head, single-block model.
- `mini_kuzai_mha.py` — multi-head attention version.
- `mini_kuzai_deep.py` — stacked Transformer-block version.
- `mini_kuzai_batch.py` — batched model using `[batch, sequence, embedding]` tensors.
- `mini_kuzai_padding.py` — final Phase 01 architecture with batching, padding support, causal masking and padding-key masking.

The final Phase 01 configuration uses two Transformer blocks, two attention heads, an embedding dimension of 8, and an MLP hidden dimension of 32.

The historical source files are also preserved unchanged under `tests/phase-01/lab/`. The copy in this package is the canonical source view for reuse. `mini_kuzai_deep.py` uses a package-relative import so it can be imported normally through `mini_kuzai`.

Example:

```python
from mini_kuzai import MiniKuzaiPadding

model = MiniKuzaiPadding(
    vocab_size=26,
    embedding_dim=8,
    hidden_dim=32,
    num_heads=2,
    num_layers=2,
    max_sequence_length=32,
    pad_token_id=0,
)
```
