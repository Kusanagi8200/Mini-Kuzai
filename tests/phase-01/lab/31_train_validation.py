import copy
import torch
import torch.nn as nn

from mini_kuzai_deep import MiniKuzaiDeep


torch.manual_seed(42)

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

# Fixed split for reproducibility
train_lines = lines[:12]
validation_lines = lines[12:]

# Build vocabulary from complete experimental corpus
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

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.01
)


# ==================================================
# Loss calculation
# ==================================================

def evaluate(dataset):

    model.eval()

    total_loss = 0.0
    examples = 0

    with torch.no_grad():

        for line in dataset:

            words = line.split() + [EOS]

            ids = torch.tensor(
                [token_to_id[word] for word in words],
                dtype=torch.long,
                device=device
            )

            inputs = ids[:-1]
            targets = ids[1:]

            logits = model(inputs)

            loss = criterion(
                logits,
                targets
            )

            total_loss += loss.item()
            examples += 1

    return total_loss / examples


# ==================================================
# Training
# ==================================================

epochs = 400

best_validation_loss = float("inf")
best_epoch = 0
best_state = None

history = []


for epoch in range(1, epochs + 1):

    model.train()

    total_train_loss = 0.0
    examples = 0

    for line in train_lines:

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

        total_train_loss += loss.item()
        examples += 1

    train_loss = total_train_loss / examples

    validation_loss = evaluate(
        validation_lines
    )

    history.append(
        (
            epoch,
            train_loss,
            validation_loss
        )
    )

    if validation_loss < best_validation_loss:

        best_validation_loss = validation_loss
        best_epoch = epoch

        best_state = copy.deepcopy(
            model.state_dict()
        )


# ==================================================
# Save BEST model, not final model
# ==================================================

checkpoint = {
    "model_state_dict": best_state,
    "vocabulary": vocabulary,
    "token_to_id": token_to_id,
    "id_to_token": id_to_token,
    "embedding_dim": 8,
    "hidden_dim": 32,
    "num_heads": 2,
    "num_layers": 2,
    "max_sequence_length": 32,
    "eos_token": EOS,
    "best_epoch": best_epoch,
    "best_validation_loss": best_validation_loss
}

torch.save(
    checkpoint,
    "mini-kuzai-validation-best.pt"
)


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== TRAIN / VALIDATION SPLIT =====")

print("Training sentences   :", len(train_lines))
print("Validation sentences :", len(validation_lines))

print()
print("VALIDATION DATA:")

for line in validation_lines:
    print("-", line)


print()
print("===== LOSS EVOLUTION =====")

for epoch in [1, 25, 50, 100, 200, 300, 400]:

    e, train_loss, validation_loss = history[
        epoch - 1
    ]

    print(
        f"Epoch {e:3d} | "
        f"Train {train_loss:.6f} | "
        f"Validation {validation_loss:.6f}"
    )


print()
print("===== BEST VALIDATION =====")

print("Best epoch           :", best_epoch)
print(
    "Best validation loss:",
    f"{best_validation_loss:.6f}"
)

print()
print("===== FINAL =====")

print(
    "Final train loss     :",
    f"{history[-1][1]:.6f}"
)

print(
    "Final validation loss:",
    f"{history[-1][2]:.6f}"
)

print()
print("Checkpoint:")
print("mini-kuzai-validation-best.pt")
