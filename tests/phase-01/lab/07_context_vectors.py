import math
import torch
import torch.nn as nn

torch.manual_seed(42)

with open("corpus.txt", "r", encoding="utf-8") as f:
    text = f.read()

tokens = text.split()
vocabulary = sorted(set(tokens))
token_to_id = {token: i for i, token in enumerate(vocabulary)}

embedding_dim = 8
max_sequence_length = 32

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

sentence = "mini kuzai runs on linux"
words = sentence.split()

token_ids = torch.tensor(
    [token_to_id[word] for word in words],
    dtype=torch.long
)

positions = torch.arange(len(token_ids))

x = token_embedding(token_ids) + position_embedding(positions)

Q = q_proj(x)
K = k_proj(x)
V = v_proj(x)

scores = (Q @ K.T) / math.sqrt(embedding_dim)

sequence_length = len(words)

mask = torch.triu(
    torch.ones(sequence_length, sequence_length, dtype=torch.bool),
    diagonal=1
)

scores = scores.masked_fill(mask, float("-inf"))

attention_weights = torch.softmax(scores, dim=-1)

# --------------------------------------------------
# Context vectors
# --------------------------------------------------

context = attention_weights @ V

print("===== MINI-KUZAI CONTEXT VECTORS =====")

print("\nAttention shape :", attention_weights.shape)
print("V shape         :", V.shape)
print("Context shape   :", context.shape)

position = 2

print("\n===== TOKEN: runs =====")

print("\nAttention weights:")
for word, probability in zip(words, attention_weights[position]):
    print(f"{word:6s} : {probability.item():.4f}")

print("\nOriginal V vector:")
print(V[position].detach())

print("\nContextualized vector:")
print(context[position].detach())
