import torch
import torch.nn as nn

torch.manual_seed(42)

embedding_dim = 8
num_heads = 2

assert embedding_dim % num_heads == 0

head_dim = embedding_dim // num_heads

sequence_length = 5

# Fake input:
# 5 tokens, each represented by 8 values
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

Q = q_proj(x)
K = k_proj(x)
V = v_proj(x)

print("===== BEFORE HEAD SPLIT =====")

print("X :", x.shape)
print("Q :", Q.shape)
print("K :", K.shape)
print("V :", V.shape)

# --------------------------------------------------
# Split into heads
#
# [sequence, embedding]
#       ↓
# [sequence, heads, head_dim]
#       ↓
# [heads, sequence, head_dim]
# --------------------------------------------------

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

print("\n===== AFTER HEAD SPLIT =====")

print("Number of heads :", num_heads)
print("Head dimension  :", head_dim)

print("Q :", Q.shape)
print("K :", K.shape)
print("V :", V.shape)

print("\n===== HEAD 0 / TOKEN 0 =====")
print("Q:", Q[0, 0])

print("\n===== HEAD 1 / TOKEN 0 =====")
print("Q:", Q[1, 0])
