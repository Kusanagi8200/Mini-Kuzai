import torch

from mini_kuzai_batch import MiniKuzaiBatch


torch.manual_seed(42)

model = MiniKuzaiBatch(
    vocab_size=25,
    embedding_dim=8,
    hidden_dim=32,
    num_heads=2,
    num_layers=2,
    max_sequence_length=32
)

# Two sequences, five tokens each
token_ids = torch.tensor([
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10]
])

logits = model(token_ids)

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== BATCH SUPPORT =====")

print("Token IDs shape :", token_ids.shape)

print(
    "Embedding shape :",
    model.token_embedding(token_ids).shape
)

print("Logits shape    :", logits.shape)

print()
print("Batch size      :", token_ids.shape[0])
print("Sequence length :", token_ids.shape[1])

print("Embedding dim   :", 8)
print("Vocabulary size :", 25)

print()
print("Expected logits : [2, 5, 25]")

print(
    "Forward pass OK :",
    logits.shape == torch.Size([2, 5, 25])
)

print()
print("Parameters      :", sum(
    p.numel()
    for p in model.parameters()
))
