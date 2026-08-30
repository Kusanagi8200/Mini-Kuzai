import os

os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

import copy
import random
import numpy as np
import torch
import torch.nn as nn

from torch.utils.data import Dataset, DataLoader
from mini_kuzai_padding import MiniKuzaiPadding


# ==================================================
# Determinism
# ==================================================

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


# ==================================================
# Data
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

    "linux is a system",
    "mini kuzai uses linux",
    "a model runs using linux",
    "linux can run a model",
    "data helps learning",
    "a model can learn from data",
    "mini kuzai learns using data",
    "data is used by a model",
]

validation_lines = [
    "a language model uses data",
    "linux can generate text",
    "mini kuzai can learn from data",
]


# ==================================================
# Special tokens
# ==================================================

PAD = "<pad>"
EOS = "<eos>"

PAD_ID = 0
EOS_ID = 1


# ==================================================
# Vocabulary from TRAIN only
# ==================================================

words = set()

for sentence in train_lines:
    words.update(sentence.split())

vocabulary = [
    PAD,
    EOS,
] + sorted(words)

token_to_id = {
    token: index
    for index, token in enumerate(vocabulary)
}

id_to_token = {
    index: token
    for token, index in token_to_id.items()
}


# ==================================================
# Check validation vocabulary
# ==================================================

unknown_validation = sorted({
    word
    for sentence in validation_lines
    for word in sentence.split()
    if word not in token_to_id
})

if unknown_validation:
    raise RuntimeError(
        f"Unknown validation tokens: {unknown_validation}"
    )


# ==================================================
# Dataset
# ==================================================

class TextDataset(Dataset):

    def __init__(self, sentences):
        self.sentences = sentences

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, index):

        words = (
            self.sentences[index].split()
            + [EOS]
        )

        return torch.tensor(
            [token_to_id[word] for word in words],
            dtype=torch.long
        )


# ==================================================
# Dynamic padding
# ==================================================

def collate_batch(examples):

    max_length = max(
        len(example) - 1
        for example in examples
    )

    batch_size = len(examples)

    input_ids = torch.full(
        (batch_size, max_length),
        PAD_ID,
        dtype=torch.long
    )

    targets = torch.full(
        (batch_size, max_length),
        PAD_ID,
        dtype=torch.long
    )

    attention_mask = torch.zeros(
        (batch_size, max_length),
        dtype=torch.long
    )

    for row, ids in enumerate(examples):

        inputs = ids[:-1]
        output_targets = ids[1:]

        length = len(inputs)

        input_ids[row, :length] = inputs
        targets[row, :length] = output_targets
        attention_mask[row, :length] = 1

    return {
        "input_ids": input_ids,
        "targets": targets,
        "attention_mask": attention_mask
    }


# ==================================================
# DataLoaders
# ==================================================

train_dataset = TextDataset(train_lines)
validation_dataset = TextDataset(validation_lines)

generator = torch.Generator()
generator.manual_seed(SEED)

train_loader = DataLoader(
    train_dataset,
    batch_size=4,
    shuffle=True,
    collate_fn=collate_batch,
    generator=generator,
    num_workers=0
)

validation_loader = DataLoader(
    validation_dataset,
    batch_size=3,
    shuffle=False,
    collate_fn=collate_batch,
    num_workers=0
)


# ==================================================
# Model
# ==================================================

model = MiniKuzaiPadding(
    vocab_size=len(vocabulary),
    embedding_dim=8,
    hidden_dim=32,
    num_heads=2,
    num_layers=2,
    max_sequence_length=32,
    pad_token_id=PAD_ID
).to(device)

parameter_count = sum(
    p.numel()
    for p in model.parameters()
)


# ==================================================
# Optimizer / loss
# ==================================================

criterion = nn.CrossEntropyLoss(
    ignore_index=PAD_ID
)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.01
)


# ==================================================
# Validation
# ==================================================

def evaluate():

    model.eval()

    total_loss = 0.0
    batches = 0

    with torch.no_grad():

        for batch in validation_loader:

            input_ids = batch[
                "input_ids"
            ].to(device)

            targets = batch[
                "targets"
            ].to(device)

            attention_mask = batch[
                "attention_mask"
            ].to(device)

            logits = model(
                input_ids,
                attention_mask
            )

            loss = criterion(
                logits.reshape(
                    -1,
                    len(vocabulary)
                ),
                targets.reshape(-1)
            )

            total_loss += loss.item()
            batches += 1

    return total_loss / batches


# ==================================================
# Training
# ==================================================

max_epochs = 400
patience = 30

best_validation_loss = float("inf")
best_epoch = 0
best_state = None

without_improvement = 0

history = []

total_optimizer_steps = 0


for epoch in range(1, max_epochs + 1):

    model.train()

    total_train_loss = 0.0
    batches = 0

    for batch in train_loader:

        input_ids = batch[
            "input_ids"
        ].to(device)

        targets = batch[
            "targets"
        ].to(device)

        attention_mask = batch[
            "attention_mask"
        ].to(device)

        optimizer.zero_grad()

        logits = model(
            input_ids,
            attention_mask
        )

        loss = criterion(
            logits.reshape(
                -1,
                len(vocabulary)
            ),
            targets.reshape(-1)
        )

        loss.backward()
        optimizer.step()

        total_optimizer_steps += 1

        total_train_loss += loss.item()
        batches += 1

    train_loss = (
        total_train_loss / batches
    )

    validation_loss = evaluate()

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

        without_improvement = 0

    else:

        without_improvement += 1

    if without_improvement >= patience:
        stopped_epoch = epoch
        break

else:
    stopped_epoch = max_epochs


# ==================================================
# Restore best weights
# ==================================================

model.load_state_dict(
    best_state
)


# ==================================================
# Save checkpoint
# ==================================================

checkpoint = {
    "model_state_dict": best_state,

    "vocabulary": vocabulary,
    "token_to_id": token_to_id,
    "id_to_token": id_to_token,

    "pad_token": PAD,
    "pad_token_id": PAD_ID,

    "eos_token": EOS,
    "eos_token_id": EOS_ID,

    "embedding_dim": 8,
    "hidden_dim": 32,
    "num_heads": 2,
    "num_layers": 2,
    "max_sequence_length": 32,

    "batch_size": 4,

    "best_epoch": best_epoch,
    "best_validation_loss": best_validation_loss,
}

torch.save(
    checkpoint,
    "mini-kuzai-batched.pt"
)


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== MINI-KUZAI BATCH TRAINING =====")

print("Device               :", device)

if device.type == "cuda":
    print(
        "GPU                  :",
        torch.cuda.get_device_name(0)
    )

print()
print("Training sentences   :", len(train_dataset))
print("Validation sentences :", len(validation_dataset))

print("Vocabulary size      :", len(vocabulary))
print("Parameters           :", parameter_count)

print()
print("Batch size           :", 4)
print("Batches / epoch      :", len(train_loader))

print(
    "Old steps / epoch    :",
    len(train_dataset)
)

print(
    "Batch steps / epoch  :",
    len(train_loader)
)

print()
print("===== EARLY STOPPING =====")

print("Best epoch           :", best_epoch)

print(
    "Best validation loss:",
    f"{best_validation_loss:.6f}"
)

print("Stopped epoch        :", stopped_epoch)

print(
    "Optimizer steps used :",
    total_optimizer_steps
)

print()
print("===== LOSS =====")

for epoch in [1, 5, 10, 25]:

    if epoch <= len(history):

        _, train_loss, val_loss = history[
            epoch - 1
        ]

        print(
            f"Epoch {epoch:3d} | "
            f"Train {train_loss:.6f} | "
            f"Validation {val_loss:.6f}"
        )

print()
print("===== CHECKPOINT =====")
print("mini-kuzai-batched.pt")

print()
print(
    "Checkpoint exists:",
    best_state is not None
)
