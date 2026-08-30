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
# Configuration
# ==================================================

SEED = 42
BATCH_SIZE = 4
LEARNING_RATE = 0.04
PATIENCE = 30
MAX_EPOCHS = 250

PAD = "<pad>"
EOS = "<eos>"

PAD_ID = 0
EOS_ID = 1


# ==================================================
# Determinism
# ==================================================

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
# TRAIN
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


# ==================================================
# VALIDATION
# ==================================================

validation_lines = [
    "a language model uses data",
    "linux can generate text",
    "mini kuzai can learn from data",
]


# ==================================================
# Vocabulary
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
# Dataset
# ==================================================

class TextDataset(Dataset):

    def __init__(self, sentences):
        self.sentences = sentences

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, index):

        tokens = (
            self.sentences[index].split()
            + [EOS]
        )

        return torch.tensor(
            [token_to_id[token] for token in tokens],
            dtype=torch.long
        )


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


train_dataset = TextDataset(train_lines)
validation_dataset = TextDataset(validation_lines)

generator = torch.Generator()
generator.manual_seed(SEED)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
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

criterion = nn.CrossEntropyLoss(
    ignore_index=PAD_ID
)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE
)


# ==================================================
# Validation
# ==================================================

def evaluate():

    model.eval()

    total = 0.0
    batches = 0

    with torch.no_grad():

        for batch in validation_loader:

            input_ids = batch["input_ids"].to(device)
            targets = batch["targets"].to(device)
            attention_mask = batch["attention_mask"].to(device)

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

            total += loss.item()
            batches += 1

    return total / batches


# ==================================================
# Training
# ==================================================

best_validation_loss = float("inf")
best_epoch = 0
best_state = None

without_improvement = 0
history = []

optimizer_steps = 0


for epoch in range(1, MAX_EPOCHS + 1):

    model.train()

    total_train = 0.0
    batches = 0

    for batch in train_loader:

        input_ids = batch["input_ids"].to(device)
        targets = batch["targets"].to(device)
        attention_mask = batch["attention_mask"].to(device)

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

        optimizer_steps += 1

        total_train += loss.item()
        batches += 1

    train_loss = total_train / batches
    validation_loss = evaluate()

    history.append(
        (epoch, train_loss, validation_loss)
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

    if without_improvement >= PATIENCE:
        stopped_epoch = epoch
        break

else:
    stopped_epoch = MAX_EPOCHS


# ==================================================
# Restore best checkpoint
# ==================================================

model.load_state_dict(best_state)

restored_validation_loss = evaluate()


# ==================================================
# Save FINAL frozen model
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

    "batch_size": BATCH_SIZE,
    "learning_rate": LEARNING_RATE,
    "seed": SEED,
    "patience": PATIENCE,

    "best_epoch": best_epoch,
    "stopped_epoch": stopped_epoch,

    "best_validation_loss": best_validation_loss,

    "train_lines": train_lines,
    "validation_lines": validation_lines,
}

torch.save(
    checkpoint,
    "mini-kuzai-final.pt"
)


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== FINAL MINI-KUZAI TRAINING =====")

print("Device              :", device)

if device.type == "cuda":
    print(
        "GPU                 :",
        torch.cuda.get_device_name(0)
    )

print()
print("Parameters          :", parameter_count)
print("Vocabulary          :", len(vocabulary))
print("Batch size          :", BATCH_SIZE)
print("Learning rate       :", LEARNING_RATE)
print("Seed                :", SEED)

print()
print("===== EARLY STOPPING =====")

print("Best epoch          :", best_epoch)
print("Stopped epoch       :", stopped_epoch)

print(
    "Best validation    :",
    f"{best_validation_loss:.6f}"
)

print(
    "Restored validation:",
    f"{restored_validation_loss:.6f}"
)

print(
    "Optimizer steps    :",
    optimizer_steps
)

print()
print("===== CHECKPOINT =====")

print("mini-kuzai-final.pt")

print(
    "Best weights restored:",
    abs(
        restored_validation_loss
        - best_validation_loss
    ) < 1e-6
)

print()
print("INDEPENDENT TEST USED: NO")
