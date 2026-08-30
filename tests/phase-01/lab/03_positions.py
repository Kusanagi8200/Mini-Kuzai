import torch
import torch.nn as nn

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

sentence = "mini kuzai runs on linux"
words = sentence.split()

token_ids = torch.tensor(
    [token_to_id[word] for word in words],
    dtype=torch.long
)

positions = torch.arange(len(token_ids))

token_vectors = token_embedding(token_ids)
position_vectors = position_embedding(positions)

x = token_vectors + position_vectors

print("===== MINI-KUZAI POSITION EMBEDDINGS =====")

print("\nWords     :", words)
print("Token IDs :", token_ids.tolist())
print("Positions :", positions.tolist())

print("\nToken embeddings shape    :", token_vectors.shape)
print("Position embeddings shape :", position_vectors.shape)
print("Combined shape            :", x.shape)

print("\n===== FIRST TOKEN =====")
print("Word     :", words[0])
print("Token ID :", token_ids[0].item())
print("Position :", positions[0].item())

print("\nToken vector:")
print(token_vectors[0].detach())

print("\nPosition vector:")
print(position_vectors[0].detach())

print("\nCombined vector:")
print(x[0].detach())
