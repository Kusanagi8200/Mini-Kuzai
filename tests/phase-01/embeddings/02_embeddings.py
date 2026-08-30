import torch
import torch.nn as nn

sentence_ids = torch.tensor([23, 18, 33, 27, 21])
vocab_size = 47
embedding_dim = 8

embedding = nn.Embedding(vocab_size, embedding_dim)
vectors = embedding(sentence_ids)

print("Input IDs shape :", sentence_ids.shape)
print("Embedding shape :", vectors.shape)
print("First vector    :", vectors[0])
