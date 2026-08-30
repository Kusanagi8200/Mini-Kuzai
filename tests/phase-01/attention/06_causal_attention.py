import math

import torch


torch.manual_seed(42)

sequence_length = 5
embedding_dim = 8

x = torch.randn(sequence_length, embedding_dim)

Wq = torch.randn(embedding_dim, embedding_dim)
Wk = torch.randn(embedding_dim, embedding_dim)
Wv = torch.randn(embedding_dim, embedding_dim)

Q = x @ Wq
K = x @ Wk
V = x @ Wv

scores = (Q @ K.T) / math.sqrt(embedding_dim)

causal_mask = torch.triu(
    torch.ones(sequence_length, sequence_length, dtype=torch.bool),
    diagonal=1,
)

scores = scores.masked_fill(causal_mask, float("-inf"))
weights = torch.softmax(scores, dim=-1)
context = weights @ V

print("Causal mask:")
print(causal_mask.int())
print()
print("Attention weights:")
print(weights)
print()
print("Row sums:", weights.sum(dim=-1))
print("Context shape:", context.shape)
