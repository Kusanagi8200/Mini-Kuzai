# Architecture Notes

Mini-Kuzai Phase 01 is a decoder-only autoregressive Transformer implemented directly in PyTorch.

## Data flow

```text
Token IDs
  ↓
Token Embeddings + Positional Embeddings
  ↓
Transformer Block 1
  ├─ LayerNorm
  ├─ Causal Multi-Head Self-Attention
  ├─ Residual connection
  ├─ LayerNorm
  ├─ MLP
  └─ Residual connection
  ↓
Transformer Block 2
  ↓
Final LayerNorm
  ↓
Linear LM Head
  ↓
Logits over vocabulary
```

## Attention

Each attention layer projects the residual stream into Q, K, and V, splits the embedding dimension across multiple heads, applies a causal mask, applies the padding-key mask, computes softmax attention weights, merges the heads, and projects back to the embedding dimension.

## MLP

Each Transformer block contains a two-layer feed-forward network:

```text
embedding_dim → hidden_dim → embedding_dim
```

with GELU activation.

## Residual stream

Attention and MLP outputs are added to the current representation rather than replacing it. Phase 01 includes experiments that trace how these residual updates move the model toward or away from a candidate next token.

## Final LayerNorm

Phase 01 also studies the learned `gamma` and `beta` parameters of the final LayerNorm. In the frozen model, `beta` creates a prompt-independent additive offset after projection through the LM head, while `gamma` acts on the standardized context-dependent representation.
