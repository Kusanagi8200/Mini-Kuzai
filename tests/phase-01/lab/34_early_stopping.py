import copy
import torch
import torch.nn as nn

from mini_kuzai_deep import MiniKuzaiDeep


torch.manual_seed(42)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

EOS = "<eos>"


# ==================================================
# Dataset
# ==================================================

train_lines = [
    "mini kuzai runs on linux",
    "mini kuzai learns from data",
    "mini kuzai can generate text",
    "mini kuzai is a language model",
    "a language model learns from data",
    "a language model can generate text",
    "linux runs a model",
    "data helps a model learn",
    "mini kuzai uses a model",
    "a model uses data",
    "a model uses linux",
    "text uses data",
]

validation_lines = [
    "a language model runs on linux",
    "mini kuzai can generate data",
    "a model learns from data",
]


# ==================================================
# Vocabulary
# ==================================================

tokens = []

for line in train_lines:
    tokens.extend(line.split())
    tokens.append(EOS)

vocabulary = sorted(set(tokens))

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
# Evaluation
# ==================================================

def evaluate(dataset):

    model.eval()

    total = 0.0

    with torch.no_grad():

        for line in dataset:

            words = line.split() + [EOS]

            ids = torch.tensor(
                [token_to_id[w] for w in words],
                dtype=torch.long,
                device=device
            )

            logits = model(ids[:-1])

            loss = criterion(
                logits,
                ids[1:]
            )

            total += loss.item()

    return total / len(dataset)


# ==================================================
# Training + Early Stopping
# ==================================================

max_epochs = 400
patience = 30

best_validation_loss = float("inf")
best_epoch = 0
best_state = None

epochs_without_improvement = 0

history = []


for epoch in range(1, max_epochs + 1):

    model.train()

    train_total = 0.0

    for line in train_lines:

        words = line.split() + [EOS]

        ids = torch.tensor(
            [token_to_id[w] for w in words],
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

        train_total += loss.item()

    train_loss = (
        train_total / len(train_lines)
    )

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

        epochs_without_improvement = 0

    else:

        epochs_without_improvement += 1


    if epochs_without_improvement >= patience:

        stopped_epoch = epoch
        break

else:
    stopped_epoch = max_epochs


# ==================================================
# Restore BEST weights
# ==================================================

model.load_state_dict(
    best_state
)

restored_validation_loss = evaluate(
    validation_lines
)


# ==================================================
# Save
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
    "mini-kuzai-best.pt"
)


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== EARLY STOPPING =====")

print("Device              :", device)
print("Maximum epochs      :", max_epochs)
print("Patience            :", patience)

print()
print("Stopped at epoch    :", stopped_epoch)
print("Best epoch          :", best_epoch)

print(
    "Best validation loss:",
    f"{best_validation_loss:.6f}"
)

print(
    "Restored val loss   :",
    f"{restored_validation_loss:.6f}"
)

print()
print("Epochs avoided      :", max_epochs - stopped_epoch)

print()
print("Checkpoint          : mini-kuzai-best.pt")

print()
print("Best weights restored:")
print(
    abs(
        restored_validation_loss
        - best_validation_loss
    ) < 1e-6
)
