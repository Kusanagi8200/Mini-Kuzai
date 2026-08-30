import torch
import torch.nn as nn

from mini_kuzai import MiniKuzai

torch.manual_seed(42)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("===== DEVICE =====")
print(device)

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

print("\n===== VOCABULARY =====")
print("Vocabulary size:", len(vocabulary))
print("EOS ID         :", token_to_id[EOS])

# ==================================================
# Model
# ==================================================

model = MiniKuzai(
    vocab_size=len(vocabulary),
    embedding_dim=8,
    hidden_dim=32,
    max_sequence_length=32
).to(device)

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.01
)

# ==================================================
# Training
# ==================================================

epochs = 300

print("\n===== TRAINING =====")

for epoch in range(1, epochs + 1):

    total_loss = 0.0
    examples = 0

    model.train()

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

    if epoch == 1 or epoch % 25 == 0:
        print(
            f"Epoch {epoch:3d} | "
            f"Loss {average_loss:.6f}"
        )

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
    "max_sequence_length": 32,
    "eos_token": EOS
}

torch.save(
    checkpoint,
    "mini-kuzai-eos.pt"
)

print("\n===== SAVED =====")
print("mini-kuzai-eos.pt")
