import os

# Must be set before CUDA operations
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

import copy
import random
import numpy as np
import torch
import torch.nn as nn

from mini_kuzai_deep import MiniKuzaiDeep


# ==================================================
# Deterministic configuration
# ==================================================

SEED = 42

torch.use_deterministic_algorithms(True)

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


tokens = []

for line in train_lines:
    tokens.extend(line.split())
    tokens.append(EOS)

vocabulary = sorted(set(tokens))

token_to_id = {
    token: i
    for i, token in enumerate(vocabulary)
}


# ==================================================
# Seed reset
# ==================================================

def reset_seed():

    random.seed(SEED)
    np.random.seed(SEED)

    torch.manual_seed(SEED)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)


# ==================================================
# One complete experiment
# ==================================================

def run_experiment():

    reset_seed()

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

    def evaluate():

        model.eval()

        total = 0.0

        with torch.no_grad():

            for line in validation_lines:

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

        return total / len(validation_lines)


    max_epochs = 150
    patience = 30

    best_loss = float("inf")
    best_epoch = 0
    best_state = None

    epochs_without_improvement = 0


    for epoch in range(1, max_epochs + 1):

        model.train()

        for line in train_lines:

            words = line.split() + [EOS]

            ids = torch.tensor(
                [token_to_id[w] for w in words],
                dtype=torch.long,
                device=device
            )

            optimizer.zero_grad()

            logits = model(ids[:-1])

            loss = criterion(
                logits,
                ids[1:]
            )

            loss.backward()
            optimizer.step()


        validation_loss = evaluate()


        if validation_loss < best_loss:

            best_loss = validation_loss
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


    return {
        "best_epoch": best_epoch,
        "best_loss": best_loss,
        "stopped_epoch": stopped_epoch,
        "state": best_state
    }


# ==================================================
# Run twice
# ==================================================

run1 = run_experiment()
run2 = run_experiment()


# ==================================================
# Compare model weights
# ==================================================

weights_identical = True

for key in run1["state"]:

    if not torch.equal(
        run1["state"][key],
        run2["state"][key]
    ):
        weights_identical = False
        break


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== DETERMINISTIC REPRODUCIBILITY =====")

print("Device:", device)
print("Seed  :", SEED)

print()
print("RUN 1")
print("Best epoch   :", run1["best_epoch"])
print("Best loss    :", f'{run1["best_loss"]:.9f}')
print("Stopped epoch:", run1["stopped_epoch"])

print()
print("RUN 2")
print("Best epoch   :", run2["best_epoch"])
print("Best loss    :", f'{run2["best_loss"]:.9f}')
print("Stopped epoch:", run2["stopped_epoch"])

print()
print("===== COMPARISON =====")

print(
    "Same best epoch:",
    run1["best_epoch"] == run2["best_epoch"]
)

print(
    "Same best loss :",
    run1["best_loss"] == run2["best_loss"]
)

print(
    "Weights identical:",
    weights_identical
)
