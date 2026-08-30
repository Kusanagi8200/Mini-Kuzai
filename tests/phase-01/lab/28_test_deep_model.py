import torch

from mini_kuzai_deep import MiniKuzaiDeep


torch.manual_seed(42)

model = MiniKuzaiDeep(
    vocab_size=48,
    embedding_dim=8,
    hidden_dim=32,
    num_heads=2,
    num_layers=2,
    max_sequence_length=32
)

token_ids = torch.tensor(
    [1, 2, 3, 4, 5],
    dtype=torch.long
)

logits = model(token_ids)

parameters = sum(
    p.numel()
    for p in model.parameters()
)

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== MINI-KUZAI 2-LAYER MODEL =====")

print("Input shape    :", token_ids.shape)
print("Logits shape   :", logits.shape)

print()
print("Transformer blocks:", len(model.blocks))

for index, block in enumerate(model.blocks):
    block_parameters = sum(
        p.numel()
        for p in block.parameters()
    )

    print(
        f"Block {index + 1} parameters:",
        block_parameters
    )

print()
print("Total parameters:", parameters)

print()
print("===== ARCHITECTURE =====")
print(model)

print()
print("Forward pass successful:")
print(logits.shape == torch.Size([5, 48]))
