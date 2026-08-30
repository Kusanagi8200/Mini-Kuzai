import math
import torch
import torch.nn as nn

torch.manual_seed(42)

# --------------------------------------------------
# Vocabulary
# --------------------------------------------------

with open("corpus.txt", "r", encoding="utf-8") as f:
    text = f.read()

tokens = text.split()
vocabulary = sorted(set(tokens))
token_to_id = {token: i for i, token in enumerate(vocabulary)}

# --------------------------------------------------
# Configuration
# --------------------------------------------------

embedding_dim = 8
hidden_dim = 32
max_sequence_length = 32

# --------------------------------------------------
# Embeddings
# --------------------------------------------------

token_embedding = nn.Embedding(
    len(vocabulary),
    embedding_dim
)

position_embedding = nn.Embedding(
    max_sequence_length,
    embedding_dim
)

# --------------------------------------------------
# Attention projections
# --------------------------------------------------

q_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
k_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
v_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
out_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)

# --------------------------------------------------
# MLP
# --------------------------------------------------

mlp = nn.Sequential(
    nn.Linear(embedding_dim, hidden_dim),
    nn.GELU(),
    nn.Linear(hidden_dim, embedding_dim)
)

# --------------------------------------------------
# Input
# --------------------------------------------------

sentence = "mini kuzai runs on linux"
words = sentence.split()

token_ids = torch.tensor(
    [token_to_id[word] for word in words],
    dtype=torch.long
)

positions = torch.arange(len(token_ids))

x = (
    token_embedding(token_ids)
    + position_embedding(positions)
)

# --------------------------------------------------
# Self-attention
# --------------------------------------------------

Q = q_proj(x)
K = k_proj(x)
V = v_proj(x)

scores = (Q @ K.T) / math.sqrt(embedding_dim)

sequence_length = len(words)

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
attention_output = out_proj(context)

# First residual connection
x_after_attention = x + attention_output

# --------------------------------------------------
# MLP
# --------------------------------------------------

mlp_output = mlp(x_after_attention)

# Second residual connection
x_after_mlp = x_after_attention + mlp_output

# --------------------------------------------------
# Display
# --------------------------------------------------

print("===== MINI-KUZAI MLP =====")

print("\nInput shape              :", x.shape)
print("After attention shape    :", x_after_attention.shape)
print("MLP output shape         :", mlp_output.shape)
print("Final output shape       :", x_after_mlp.shape)

print("\nMLP architecture:")
print(mlp)

position = 2

print("\n===== TOKEN: runs =====")

print("\nBefore MLP:")
print(x_after_attention[position].detach())

print("\nMLP output:")
print(mlp_output[position].detach())

print("\nAfter residual:")
print(x_after_mlp[position].detach())

print("\nVerification:")
print(
    torch.allclose(
        x_after_mlp[position],
        x_after_attention[position]
        + mlp_output[position]
    )
)
