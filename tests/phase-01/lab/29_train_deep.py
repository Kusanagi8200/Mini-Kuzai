import torch
import torch.nn as nn

from mini_kuzai_deep import MiniKuzaiDeep


torch.manual_seed(42)

# ==================================================
# Device
# ==================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Corpus
# ==================================================

with open("corpus.txt", "r", encoding="utf-8") as f:
    lines = [
        line.strip()
        for line in f
        if line.strip()
    ]

EOS = "<eos>"

all_tokens = []

for line in lines:
    all_tokens.extend(line.split())
    all_tokens.append(EOS)

vocabulary = sorted(set(all_tokens))

token_to_id = {
    token: i
    for i, token in enumerate(vocabulary)
}

id_to_token = {
    i: token
    for token, i in token_to_id.items()
}


# ==================================================
# Model
# ==================================================

model = MiniKuzaiDeep(
    vocab_size=len(vocabulary),
    embedding_dim=8,
    hidden_dim=32,
    num_heads=2,
    num_layers=2,
    max_sequence_length=32
).to(device)

parameter_count = sum(
    p.numel()
    for p in model.parameters()
)


# ==================================================
# Training
# ==================================================

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.01
)

epochs = 300
loss_history = []


for epoch in range(1, epochs + 1):

    model.train()

    total_loss = 0.0
    examples = 0

    for line in lines:

        words = line.split() + [EOS]

        ids = torch.tensor(
            [token_to_id[word] for word in words],
            dtype=torch.long,
            device=device
        )

        inputs = ids[:-1]
        targets = ids[1:]

        optimizer.zero_grad()

        logits = model(inputs)

        loss = criterion(
            logits,
            targets
        )

        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        examples += 1

    average_loss = total_loss / examples
    loss_history.append(average_loss)


# ==================================================
# Save
# ==================================================

checkpoint = {
    "model_state_dict": model.state_dict(),
    "vocabulary": vocabulary,
    "token_to_id": token_to_id,
    "id_to_token": id_to_token,
    "embedding_dim": 8,
    "hidden_dim": 32,
    "num_heads": 2,
    "num_layers": 2,
    "max_sequence_length": 32,
    "eos_token": EOS,
    "loss_history": loss_history
}

torch.save(
    checkpoint,
    "mini-kuzai-deep.pt"
)


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== MINI-KUZAI 2-LAYER TRAINING =====")

print("Device         :", device)

if device.type == "cuda":
    print("GPU            :", torch.cuda.get_device_name(0))

print("Vocabulary     :", len(vocabulary))
print("Transformer blocks:", 2)
print("Heads / block  :", 2)
print("Parameters     :", parameter_count)

print()
print("===== LOSS =====")

for epoch in [1, 25, 50, 100, 200, 300]:
    print(
        f"Epoch {epoch:3d} : "
        f"{loss_history[epoch - 1]:.6f}"
    )

print()
print("===== CHECKPOINT =====")
print("mini-kuzai-deep.pt")
