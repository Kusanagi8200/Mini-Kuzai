import os
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

import copy
import random
import numpy as np
import torch
import torch.nn as nn

from torch.utils.data import Dataset, DataLoader
from mini_kuzai_padding import MiniKuzaiPadding


SEED = 42

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

PAD = "<pad>"
EOS = "<eos>"
PAD_ID = 0


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
            [token_to_id[t] for t in tokens],
            dtype=torch.long
        )


def collate_batch(examples):

    max_length = max(
        len(x) - 1
        for x in examples
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


def reset_seed():

    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)


def run_experiment(learning_rate):

    reset_seed()

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

    model = MiniKuzaiPadding(
        vocab_size=len(vocabulary),
        embedding_dim=8,
        hidden_dim=32,
        num_heads=2,
        num_layers=2,
        max_sequence_length=32,
        pad_token_id=PAD_ID
    ).to(device)

    criterion = nn.CrossEntropyLoss(
        ignore_index=PAD_ID
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate
    )

    def evaluate():

        model.eval()

        total = 0.0
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

                total += loss.item()
                batches += 1

        return total / batches


    max_epochs = 250
    patience = 30

    best_loss = float("inf")
    best_epoch = 0
    best_state = None
    without_improvement = 0


    for epoch in range(1, max_epochs + 1):

        model.train()

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


        val_loss = evaluate()


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


    return {
        "lr": learning_rate,
        "best_loss": best_loss,
        "best_epoch": best_epoch,
        "stopped_epoch": stopped_epoch,
        "state": best_state
    }


torch.use_deterministic_algorithms(True)

learning_rates = [
    0.0325,
    0.0350,
    0.0375,
    0.0400,
    0.0425,
    0.0450,
    0.0475,
]

results = []

for lr in learning_rates:

    result = run_experiment(lr)
    results.append(result)


best = min(
    results,
    key=lambda x: x["best_loss"]
)


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== BATCH LEARNING RATE SEARCH =====")

print("Device     :", device)
print("Batch size :", 4)

print()
print("LR          BEST EPOCH     STOPPED     BEST VAL")

for result in results:

    print(
        f"{result['lr']:<10.4f} "
        f"{result['best_epoch']:<14d} "
        f"{result['stopped_epoch']:<11d} "
        f"{result['best_loss']:.6f}"
    )


print()
print("===== BEST CONFIGURATION =====")

print(
    "Learning rate:",
    best["lr"]
)

print(
    "Best epoch   :",
    best["best_epoch"]
)

print(
    "Validation   :",
    f"{best['best_loss']:.6f}"
)

print()
print("TEST DATA USED: NO")
