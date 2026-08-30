import torch
import torch.nn as nn

from mini_kuzai import MiniKuzaiPadding


torch.manual_seed(42)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

vocabulary = ["<pad>", "<eos>", "mini", "kuzai", "learns", "from", "data"]
token_to_id = {token: i for i, token in enumerate(vocabulary)}

input_ids = torch.tensor(
    [[
        token_to_id["mini"],
        token_to_id["kuzai"],
        token_to_id["learns"],
        token_to_id["from"],
    ]],
    device=device,
)

targets = torch.tensor(
    [[
        token_to_id["kuzai"],
        token_to_id["learns"],
        token_to_id["from"],
        token_to_id["data"],
    ]],
    device=device,
)

attention_mask = torch.ones_like(input_ids)

model = MiniKuzaiPadding(
    vocab_size=len(vocabulary),
    embedding_dim=8,
    hidden_dim=32,
    num_heads=2,
    num_layers=1,
    max_sequence_length=32,
    pad_token_id=0,
).to(device)

criterion = nn.CrossEntropyLoss(ignore_index=0)
optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)

with torch.no_grad():
    logits = model(input_ids, attention_mask)
    loss_before = criterion(
        logits.reshape(-1, len(vocabulary)),
        targets.reshape(-1),
    ).item()

optimizer.zero_grad()
logits = model(input_ids, attention_mask)
loss = criterion(
    logits.reshape(-1, len(vocabulary)),
    targets.reshape(-1),
)
loss.backward()
optimizer.step()

with torch.no_grad():
    logits = model(input_ids, attention_mask)
    loss_after = criterion(
        logits.reshape(-1, len(vocabulary)),
        targets.reshape(-1),
    ).item()

print("Device      :", device)
print("Loss before :", loss_before)
print("Loss after  :", loss_after)
print("Loss changed:", loss_after != loss_before)
