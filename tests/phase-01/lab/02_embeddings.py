import torch
import torch.nn as nn

# Load corpus
with open("corpus.txt", "r", encoding="utf-8") as f:
    text = f.read()

tokens = text.split()
vocabulary = sorted(set(tokens))

token_to_id = {token: i for i, token in enumerate(vocabulary)}

# Small embedding dimension for learning purposes
embedding_dim = 8

embedding = nn.Embedding(
    num_embeddings=len(vocabulary),
    embedding_dim=embedding_dim
)

sentence = "mini kuzai runs on linux"

token_ids = torch.tensor(
    [token_to_id[word] for word in sentence.split()],
    dtype=torch.long
)

vectors = embedding(token_ids)

print("===== MINI-KUZAI EMBEDDINGS =====")
print("Vocabulary size :", len(vocabulary))
print("Embedding size  :", embedding_dim)

print("\n===== INPUT =====")
print("Text :", sentence)
print("IDs  :", token_ids.tolist())

print("\n===== SHAPE =====")
print(vectors.shape)

print("\n===== EMBEDDING VECTORS =====")

for word, token_id, vector in zip(
    sentence.split(),
    token_ids.tolist(),
    vectors
):
    print(f"\n{word}")
    print("ID     :", token_id)
    print("Vector :", vector.detach().tolist())
