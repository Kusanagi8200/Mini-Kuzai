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
# --------------------------------------------------

scores = (Q @ K.T) / math.sqrt(embedding_dim)

# --------------------------------------------------
# Causal mask
# --------------------------------------------------

sequence_length = len(words)

mask = torch.triu(
    torch.ones(sequence_length, sequence_length, dtype=torch.bool),
    diagonal=1
)

masked_scores = scores.masked_fill(mask, float("-inf"))

# --------------------------------------------------
# Softmax
# --------------------------------------------------

attention_weights = torch.softmax(masked_scores, dim=-1)

# --------------------------------------------------
# Display
# --------------------------------------------------

print("===== MINI-KUZAI CAUSAL ATTENTION =====")

print("\nWords:")
print(words)

print("\n===== CAUSAL MASK =====")
print(mask.int())

print("\n===== MASKED SCORES =====")
print(masked_scores.detach())

print("\n===== ATTENTION PROBABILITIES =====")
print(attention_weights.detach())

# Examine token "runs", position 2

position = 2

print("\n===== ATTENTION FOR 'runs' =====")

for word, probability in zip(words, attention_weights[position]):
    print(f"runs -> {word:6s} : {probability.item():.4f}")

print(
    "\nProbability sum:",
    attention_weights[position].sum().item()
)
