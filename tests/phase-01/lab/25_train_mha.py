import torch
import torch.nn as nn

from mini_kuzai_mha import MiniKuzaiMHA


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

model = MiniKuzaiMHA(
    vocab_size=len(vocabulary),
    embedding_dim=8,
    hidden_dim=32,
    num_heads=2,
    max_sequence_length=32
).to(device)

parameter_count = sum(
    p.numel()
    for p in model.parameters()
)

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.01
)

epochs = 300

loss_history = []

# ==================================================
# Training
# ==================================================

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

    if epoch == 1 or epoch % 25 == 0:
        print(
            f"Epoch {epoch:3d} | "
            f"Loss {average_loss:.6f}"
        )

# ==================================================
# Save checkpoint
# ==================================================

checkpoint = {
    "model_state_dict": model.state_dict(),
    "vocabulary": vocabulary,
    "token_to_id": token_to_id,
    "id_to_token": id_to_token,
    "embedding_dim": 8,
    "hidden_dim": 32,
    "num_heads": 2,
    "max_sequence_length": 32,
    "eos_token": EOS,
    "loss_history": loss_history
}

torch.save(
    checkpoint,
    "mini-kuzai-mha.pt"
)

# ==================================================
# Results
# ==================================================

print()
print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== MINI-KUZAI MHA TRAINING =====")

print("Device         :", device)

if device.type == "cuda":
    print("GPU            :", torch.cuda.get_device_name(0))

print("Vocabulary     :", len(vocabulary))
print("Parameters     :", parameter_count)
print("Heads          :", 2)
print("Head dimension :", 4)

print()
print("===== LOSS =====")

print(f"Epoch   1 : {loss_history[0]:.6f}")
print(f"Epoch  25 : {loss_history[24]:.6f}")
print(f"Epoch  50 : {loss_history[49]:.6f}")
print(f"Epoch 100 : {loss_history[99]:.6f}")
print(f"Epoch 200 : {loss_history[199]:.6f}")
print(f"Epoch 300 : {loss_history[299]:.6f}")

print()
print("===== CHECKPOINT =====")
print("mini-kuzai-mha.pt")
