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
# Q / K / V projections
# --------------------------------------------------

q_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
k_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
v_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)

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
# Create Q, K and V
# --------------------------------------------------

Q = q_proj(x)
K = k_proj(x)
V = v_proj(x)

# --------------------------------------------------
# Display
# --------------------------------------------------

print("===== MINI-KUZAI Q K V =====")

print("\nInput shape :", x.shape)
print("Q shape     :", Q.shape)
print("K shape     :", K.shape)
print("V shape     :", V.shape)

print("\n===== FIRST TOKEN =====")
print("Word:", words[0])

print("\nInput X:")
print(x[0].detach())

print("\nQuery Q:")
print(Q[0].detach())

print("\nKey K:")
print(K[0].detach())

print("\nValue V:")
print(V[0].detach())
