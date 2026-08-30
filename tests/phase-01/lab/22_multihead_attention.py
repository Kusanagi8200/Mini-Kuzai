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

q_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
k_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
v_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)

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

# --------------------------------------------------
# Attention scores per head
#
# Q : [heads, sequence, head_dim]
# K : [heads, sequence, head_dim]
#
# scores:
# [heads, sequence, sequence]
# --------------------------------------------------

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

print("##### SECTION RESULTS FOR ASSISTANT ######")

print("\n===== MULTI-HEAD ATTENTION =====")

print("Q shape         :", Q.shape)
print("K shape         :", K.shape)
print("V shape         :", V.shape)

print("Scores shape    :", scores.shape)
print("Attention shape :", attention_weights.shape)
print("Context shape   :", context.shape)

print("\n===== HEAD 0 ATTENTION =====")
print(attention_weights[0].detach())

print("\n===== HEAD 1 ATTENTION =====")
print(attention_weights[1].detach())

print("\n===== PROBABILITY SUM CHECK =====")

print(
    "Head 0 / token 4:",
    attention_weights[0, 4].sum().item()
)

print(
    "Head 1 / token 4:",
    attention_weights[1, 4].sum().item()
)
