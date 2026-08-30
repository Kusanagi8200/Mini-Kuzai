import torch

from mini_kuzai_mha import MiniKuzaiMHA


torch.manual_seed(42)

vocab_size = 48

model = MiniKuzaiMHA(
    vocab_size=vocab_size,
    embedding_dim=8,
    hidden_dim=32,
    num_heads=2,
    max_sequence_length=32
)

token_ids = torch.tensor(
    [23, 18, 33, 27, 21],
    dtype=torch.long
)

logits = model(token_ids)

parameters = sum(
    p.numel()
    for p in model.parameters()
)

print("##### SECTION RESULTS FOR ASSISTANT ######")

print("\n===== MINI-KUZAI MULTI-HEAD MODEL =====")

print("Input shape  :", token_ids.shape)
print("Logits shape :", logits.shape)

print("\nEmbedding dim :", 8)
print("Heads         :", 2)
print("Head dim      :", 4)

print("\nParameters:")
print(parameters)

print("\nAttention:")
print(model.transformer.attention)

print("\nForward pass successful:")
print(logits.shape == torch.Size([5, 48]))
