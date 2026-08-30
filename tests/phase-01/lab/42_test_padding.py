import torch
import torch.nn as nn

from mini_kuzai_padding import MiniKuzaiPadding


torch.manual_seed(42)

PAD_ID = 0
VOCAB_SIZE = 26

model = MiniKuzaiPadding(
    vocab_size=VOCAB_SIZE,
    embedding_dim=8,
    hidden_dim=32,
    num_heads=2,
    num_layers=2,
    max_sequence_length=32,
    pad_token_id=PAD_ID
)


# ==================================================
# Variable-length sequences after padding
#
# Sequence 1 = 5 real tokens
# Sequence 2 = 4 real tokens + PAD
# ==================================================

token_ids = torch.tensor([
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, PAD_ID]
])


attention_mask = torch.tensor([
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0]
])


logits = model(
    token_ids,
    attention_mask
)


# ==================================================
# Example shifted targets
# PAD position is ignored by the loss
# ==================================================

targets = torch.tensor([
    [2, 3, 4, 5, PAD_ID],
    [7, 8, 9, PAD_ID, PAD_ID]
])


criterion = nn.CrossEntropyLoss(
    ignore_index=PAD_ID
)


loss = criterion(
    logits.view(-1, VOCAB_SIZE),
    targets.view(-1)
)


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== PADDING SUPPORT =====")

print("Token IDs:")
print(token_ids)

print()
print("Attention mask:")
print(attention_mask)

print()
print("Token IDs shape      :", token_ids.shape)
print("Attention mask shape :", attention_mask.shape)
print("Logits shape         :", logits.shape)

print()
print("PAD token ID         :", PAD_ID)

print(
    "PAD embedding:",
    model.token_embedding.weight[
        PAD_ID
    ].detach()
)

print()
print("Loss with PAD ignored:")
print(loss.item())

print()
print("Expected logits shape: [2, 5, 26]")

print(
    "Forward pass OK      :",
    logits.shape == torch.Size([2, 5, 26])
)

print(
    "PAD embedding zero   :",
    torch.all(
        model.token_embedding.weight[
            PAD_ID
        ] == 0
    ).item()
)

print(
    "Loss finite          :",
    torch.isfinite(loss).item()
)
