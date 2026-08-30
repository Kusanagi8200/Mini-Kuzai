import math
import torch
import torch.nn as nn

torch.manual_seed(42)

embedding_dim = 8
num_heads = 2
head_dim = embedding_dim // num_heads
sequence_length = 5

x = torch.randn(
    sequence_length,
    embedding_dim
)

q_proj = nn.Linear(
    embedding_dim,
    embedding_dim,
    bias=False
)

k_proj = nn.Linear(
    embedding_dim,
    embedding_dim,
    bias=False
)

v_proj = nn.Linear(
    embedding_dim,
    embedding_dim,
    bias=False
)

out_proj = nn.Linear(
    embedding_dim,
    embedding_dim,
    bias=False
)

Q = q_proj(x)
K = k_proj(x)
V = v_proj(x)

Q = Q.view(
    sequence_length,
    num_heads,
    head_dim
).transpose(0, 1)

K = K.view(
    sequence_length,
    num_heads,
    head_dim
).transpose(0, 1)

V = V.view(
    sequence_length,
    num_heads,
    head_dim
).transpose(0, 1)

scores = (
    Q @ K.transpose(-2, -1)
) / math.sqrt(head_dim)

mask = torch.triu(
    torch.ones(
        sequence_length,
        sequence_length,
        dtype=torch.bool
    ),
    diagonal=1
)

scores = scores.masked_fill(
    mask,
    float("-inf")
)

attention_weights = torch.softmax(
    scores,
    dim=-1
)

context = attention_weights @ V

# --------------------------------------------------
# Merge heads
#
# [heads, sequence, head_dim]
#          ↓ transpose
# [sequence, heads, head_dim]
#          ↓ reshape
# [sequence, embedding_dim]
# --------------------------------------------------

merged = (
    context
    .transpose(0, 1)
    .contiguous()
    .view(
        sequence_length,
        embedding_dim
    )
)

output = out_proj(merged)


print("##### SECTION RESULTS FOR ASSISTANT ######")

print("\n===== MULTI-HEAD MERGE =====")

print("Context shape :", context.shape)
print("Merged shape  :", merged.shape)
print("Output shape  :", output.shape)

print("\n===== DIMENSIONS =====")

print("Heads         :", num_heads)
print("Head dim      :", head_dim)
print("Embedding dim :", embedding_dim)

print("\n===== FIRST TOKEN =====")

print("Head 0:")
print(context[0, 0].detach())

print("\nHead 1:")
print(context[1, 0].detach())

print("\nMerged:")
print(merged[0].detach())

print("\nProjected output:")
print(output[0].detach())

print("\nShape restored:")
print(output.shape == x.shape)
