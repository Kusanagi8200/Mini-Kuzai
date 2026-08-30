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
# TRAIN DATA
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

# ==================================================
# VALIDATION DATA
# Completely unseen sequences
# but every token exists in training vocabulary.
# ==================================================

validation_lines = [
    "a language model runs on linux",
    "mini kuzai can generate data",
    "a model learns from data",
]

# ==================================================
# Verify there is NO exact train/validation leakage
# ==================================================

duplicates = sorted(
    set(train_lines) & set(validation_lines)
)

# ==================================================
# Vocabulary = TRAIN ONLY
# ==================================================

train_tokens = []

for line in train_lines:
    train_tokens.extend(line.split())
    train_tokens.append(EOS)

vocabulary = sorted(set(train_tokens))

token_to_id = {
    token: i
    for i, token in enumerate(vocabulary)
}

id_to_token = {
    i: token
    for token, i in token_to_id.items()
}

# ==================================================
# Check unknown validation tokens
# ==================================================

unknown_tokens = sorted({
    word
    for line in validation_lines
    for word in line.split()
    if word not in token_to_id
})

if duplicates:
    raise RuntimeError(
        f"Train/validation duplicates: {duplicates}"
    )

if unknown_tokens:
    raise RuntimeError(
        f"Unknown validation tokens: {unknown_tokens}"
    )

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

    total_loss = 0.0

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

    return total_loss / len(dataset)

# ==================================================
# Training
# ==================================================

epochs = 400

history = []

best_epoch = 0
best_validation_loss = float("inf")
best_state = None

for epoch in range(1, epochs + 1):

    model.train()

    total_train_loss = 0.0

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

    train_loss = (
        total_train_loss / len(train_lines)
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

# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== TRUE VALIDATION EXPERIMENT =====")

print("Device              :", device)
print("Vocabulary size     :", len(vocabulary))
print("Unknown validation  :", len(unknown_tokens))
print("Exact duplicates    :", len(duplicates))
print("Training sentences  :", len(train_lines))
print("Validation sentences:", len(validation_lines))

print()
print("===== VALIDATION DATA =====")

for line in validation_lines:
    print("-", line)

print()
print("===== LOSS EVOLUTION =====")

for epoch in [
    1, 5, 10, 25, 50,
    100, 200, 300, 400
]:

    _, train_loss, validation_loss = (
        history[epoch - 1]
    )

    print(
        f"Epoch {epoch:3d} | "
        f"Train {train_loss:.6f} | "
        f"Validation {validation_loss:.6f}"
    )

print()
print("===== BEST VALIDATION =====")

print("Best epoch:", best_epoch)

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
