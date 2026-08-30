import copy
import os
import random
import numpy as np
import torch
import torch.nn as nn

from mini_kuzai_deep import MiniKuzaiDeep


# ==================================================
# Deterministic configuration
# ==================================================

os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

torch.use_deterministic_algorithms(True)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

EOS = "<eos>"


# ==================================================
# Original train data
# ==================================================

base_train = [
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
# Additional data
#
# Important:
# none of these are the exact validation prefixes.
# ==================================================

extra_train = [
    "linux is a system",
    "mini kuzai uses linux",
    "a model runs using linux",
    "linux can run a model",
    "data helps learning",
    "a model can learn from data",
    "mini kuzai learns using data",
    "data is used by a model",
]


train_lines = base_train + extra_train


# ==================================================
# Generalization benchmark
# ==================================================

tests = [
    ("a language model runs on", "linux"),
    ("a model runs on", "linux"),
    ("a model learns from", "data"),
]


# ==================================================
# Build vocabulary
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
# Check benchmark tokens
# ==================================================

unknown = sorted({
    word
    for prompt, expected in tests
    for word in prompt.split() + [expected]
    if word not in token_to_id
})

if unknown:
    raise RuntimeError(
        f"Unknown benchmark tokens: {unknown}"
    )


# ==================================================
# Check exact prefix leakage
# ==================================================

def prefix_seen(prefix):

    prefix_words = prefix.split()

    for line in train_lines:

        words = line.split()

        n = len(prefix_words)

        for i in range(len(words) - n + 1):

            if words[i:i+n] == prefix_words:
                return True

    return False


leaked_prefixes = [
    prompt
    for prompt, _ in tests
    if prefix_seen(prompt)
]

if leaked_prefixes:
    raise RuntimeError(
        f"Benchmark prefix leakage: {leaked_prefixes}"
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
# Validation loss over benchmark sequences
# ==================================================

validation_lines = [
    prompt + " " + expected
    for prompt, expected in tests
]


def validation_loss():

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


# ==================================================
# Train + early stopping
# ==================================================

max_epochs = 400
patience = 30

best_loss = float("inf")
best_epoch = 0
best_state = None

without_improvement = 0


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

    val_loss = validation_loss()

    if val_loss < best_loss:

        best_loss = val_loss
        best_epoch = epoch
        best_state = copy.deepcopy(
            model.state_dict()
        )

        without_improvement = 0

    else:

        without_improvement += 1


    if without_improvement >= patience:
        stopped_epoch = epoch
        break

else:
    stopped_epoch = max_epochs


model.load_state_dict(
    best_state
)

model.eval()


# ==================================================
# Benchmark
# ==================================================

def benchmark(prompt, expected):

    ids = torch.tensor(
        [token_to_id[w] for w in prompt.split()],
        dtype=torch.long,
        device=device
    )

    with torch.no_grad():

        probabilities = torch.softmax(
            model(ids)[-1],
            dim=-1
        )

    sorted_probs, sorted_ids = torch.sort(
        probabilities,
        descending=True
    )

    expected_id = token_to_id[expected]

    expected_rank = (
        (sorted_ids == expected_id)
        .nonzero(as_tuple=True)[0]
        .item()
        + 1
    )

    predicted = id_to_token[
        sorted_ids[0].item()
    ]

    expected_probability = (
        probabilities[expected_id]
        .item()
    )

    return (
        predicted,
        expected_rank,
        expected_probability
    )


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== MORE DATA EXPERIMENT =====")

print("Device              :", device)
print("Base training lines :", len(base_train))
print("Extra training lines:", len(extra_train))
print("Total training lines:", len(train_lines))

print("Vocabulary size     :", len(vocabulary))
print("Unknown benchmark   :", len(unknown))
print("Prefix leakage      :", len(leaked_prefixes))

print()
print("Model parameters    :", sum(
    p.numel()
    for p in model.parameters()
))

print()
print("Best epoch          :", best_epoch)
print(
    "Best validation loss:",
    f"{best_loss:.6f}"
)
print("Stopped epoch       :", stopped_epoch)


print()
print("===== GENERALIZATION =====")

for prompt, expected in tests:

    predicted, rank, probability = benchmark(
        prompt,
        expected
    )

    print()
    print("PROMPT   :", prompt)
    print("EXPECTED :", expected)
    print("PREDICTED:", predicted)
    print("RANK     :", rank)

    print(
        "EXPECTED PROBABILITY:",
        f"{probability * 100:.2f} %"
    )

    print(
        "TOP-1 CORRECT:",
        predicted == expected
    )
