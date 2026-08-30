import torch
from torch.utils.data import Dataset, DataLoader


# ==================================================
# Training corpus
# ==================================================

sentences = [
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
# Special tokens
# ==================================================

PAD = "<pad>"
EOS = "<eos>"

PAD_ID = 0
EOS_ID = 1


# ==================================================
# Vocabulary
# ==================================================

words = set()

for sentence in sentences:
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

class MiniKuzaiDataset(Dataset):

    def __init__(self, sentences):
        self.sentences = sentences

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, index):

        sentence = self.sentences[index]

        tokens = sentence.split() + [EOS]

        ids = [
            token_to_id[token]
            for token in tokens
        ]

        return torch.tensor(
            ids,
            dtype=torch.long
        )


dataset = MiniKuzaiDataset(
    sentences
)


# ==================================================
# Dynamic batch padding
# ==================================================

def collate_batch(examples):

    # Longest INPUT sequence in this batch
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

        input_ids[
            row,
            :length
        ] = inputs

        targets[
            row,
            :length
        ] = output_targets

        attention_mask[
            row,
            :length
        ] = 1


    return {
        "input_ids": input_ids,
        "targets": targets,
        "attention_mask": attention_mask
    }


# ==================================================
# DataLoader
# ==================================================

generator = torch.Generator()
generator.manual_seed(42)

loader = DataLoader(
    dataset,
    batch_size=4,
    shuffle=True,
    collate_fn=collate_batch,
    generator=generator
)


# ==================================================
# Inspect first two batches
# ==================================================

def decode(row):

    return [
        id_to_token[token.item()]
        for token in row
    ]


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== PYTORCH DATALOADER =====")

print("Dataset sentences :", len(dataset))
print("Vocabulary size   :", len(vocabulary))
print("Batch size        :", 4)
print("Expected batches  :", len(loader))


for batch_number, batch in enumerate(loader, start=1):

    print()
    print(
        f"===== BATCH {batch_number} ====="
    )

    print(
        "Input shape :",
        batch["input_ids"].shape
    )

    print(
        "Target shape:",
        batch["targets"].shape
    )

    print(
        "Mask shape  :",
        batch["attention_mask"].shape
    )

    print()
    print("INPUTS:")

    for row in batch["input_ids"]:
        print(decode(row))

    print()
    print("TARGETS:")

    for row in batch["targets"]:
        print(decode(row))

    print()
    print("MASK:")
    print(batch["attention_mask"])


    # Only inspect first two batches
    if batch_number == 2:
        break
