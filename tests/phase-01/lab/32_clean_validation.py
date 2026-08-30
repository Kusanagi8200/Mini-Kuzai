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
# Controlled dataset
# ==================================================

train_lines = [
    "mini kuzai runs on linux",
    "mini kuzai learns from data",
    "mini kuzai can generate text",
    "mini kuzai is a language model",
    "a language model learns from data",
    "a language model can generate text",
    "linux runs a language model",
    "data helps a language model learn",
    "mini kuzai uses a model",
    "a model runs on linux",
    "a model uses data",
    "mini kuzai uses data",
]

validation_lines = [
    "mini kuzai generates text",
    "a language model runs on linux",
    "mini kuzai learns from data",
]


# ==================================================
# Normalize one intentional vocabulary issue
# ==================================================
#
# We want validation vocabulary entirely contained
# in training vocabulary.
#
# "generates" would be unseen, so use "generate".
# ==================================================

validation_lines[0] = "mini kuzai can generate text"


# ==================================================
# Vocabulary from TRAIN ONLY
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
# Verify validation vocabulary
# ==================================================

unknown_tokens = set()

for line in validation_lines:
    for word in line.split():

        if word not in token_to_id:
            unknown_tokens.add(word)


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

def evaluate(lines):

    model.eval()

    total = 0.0

    with torch.no_grad():

        for line in lines:

            words = line.split() + [EOS]

            ids = torch.tensor(
                [token_to_id[w] for w in words],
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

            total += loss.item()

    return total / len(lines)


# ==================================================
# Training
# ==================================================

epochs = 400

history = []

best_validation_loss = float("inf")
best_epoch = None
best_state = None


for epoch in range(1, epochs + 1):

    model.train()

    total_train = 0.0

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

        total_train += loss.item()

    train_loss = total_train / len(train_lines)

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
print("===== CLEAN VALIDATION EXPERIMENT =====")

print("Device              :", device)
print("Vocabulary size     :", len(vocabulary))
print("Unknown validation  :", len(unknown_tokens))
print("Training sentences  :", len(train_lines))
print("Validation sentences:", len(validation_lines))

print()
print("===== VALIDATION DATA =====")

for line in validation_lines:
    print("-", line)

print()
print("===== LOSS EVOLUTION =====")

for epoch in [1, 5, 10, 25, 50, 100, 200, 300, 400]:

    _, train_loss, val_loss = history[
        epoch - 1
    ]

    print(
        f"Epoch {epoch:3d} | "
        f"Train {train_loss:.6f} | "
        f"Validation {val_loss:.6f}"
    )

print()
print("===== BEST VALIDATION =====")

print("Best epoch:", best_epoch)
print(
    "Best loss :",
    f"{best_validation_loss:.6f}"
)

print()
print("===== FINAL =====")

print(
    "Train      :",
    f"{history[-1][1]:.6f}"
)

print(
    "Validation :",
    f"{history[-1][2]:.6f}"
)
