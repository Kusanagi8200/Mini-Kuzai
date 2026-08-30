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
max_sequence_length = 32

# --------------------------------------------------
# Layers
# --------------------------------------------------

token_embedding = nn.Embedding(
    len(vocabulary),
    embedding_dim
)

position_embedding = nn.Embedding(
    max_sequence_length,
    embedding_dim
)

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
# Q K V
# --------------------------------------------------

Q = q_proj(x)
K = k_proj(x)
V = v_proj(x)

# --------------------------------------------------
# Attention scores
# Q @ K.T
# --------------------------------------------------

raw_scores = Q @ K.T

scaled_scores = raw_scores / math.sqrt(embedding_dim)

# --------------------------------------------------
# Display
# --------------------------------------------------

print("===== MINI-KUZAI ATTENTION SCORES =====")

print("\nWords:")
print(words)

print("\nQ shape:", Q.shape)
print("K.T shape:", K.T.shape)
print("Scores shape:", scaled_scores.shape)

print("\n===== SCALED ATTENTION SCORE MATRIX =====")
print(scaled_scores.detach())

print("\n===== SCORES FOR TOKEN 'mini' =====")

for word, score in zip(words, scaled_scores[0]):
    print(f"mini -> {word:6s} : {score.item(): .4f}")
