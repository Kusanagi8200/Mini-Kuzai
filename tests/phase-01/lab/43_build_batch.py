import torch
import torch.nn as nn

from mini_kuzai_padding import MiniKuzaiPadding


# ==================================================
# Dataset
# ==================================================

sentences = [
    "mini kuzai runs on linux",
    "a model uses data",
    "linux is a system",
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
# Encode each sentence
#
# sentence:
# mini kuzai runs on linux
#
# becomes:
# mini kuzai runs on linux <eos>
# ==================================================

encoded = []

for sentence in sentences:

    tokens = (
        sentence.split()
        + [EOS]
    )

    ids = [
        token_to_id[token]
        for token in tokens
    ]

    encoded.append(ids)


# ==================================================
# Determine maximum INPUT length
#
# We shift:
#
# INPUT:
# mini kuzai runs on linux
#
# TARGET:
# kuzai runs on linux <eos>
# ==================================================

max_length = max(
    len(ids) - 1
    for ids in encoded
)

batch_size = len(encoded)


# ==================================================
# Allocate padded tensors
# ==================================================

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


# ==================================================
# Fill batch
# ==================================================

for row, ids in enumerate(encoded):

    inputs = ids[:-1]
    output_targets = ids[1:]

    length = len(inputs)

    input_ids[
        row,
        :length
    ] = torch.tensor(inputs)

    targets[
        row,
        :length
    ] = torch.tensor(output_targets)

    attention_mask[
        row,
        :length
    ] = 1


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
)


# ==================================================
# Forward
# ==================================================

logits = model(
    input_ids,
    attention_mask
)


# ==================================================
# Loss
# ==================================================

criterion = nn.CrossEntropyLoss(
    ignore_index=PAD_ID
)

loss = criterion(
    logits.reshape(
        -1,
        len(vocabulary)
    ),
    targets.reshape(-1)
)


# ==================================================
# Human-readable decoding
# ==================================================

def decode_row(row):

    return [
        id_to_token[token_id.item()]
        for token_id in row
    ]


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== AUTOMATIC BATCH =====")

print("Vocabulary size :", len(vocabulary))
print("PAD ID          :", PAD_ID)
print("EOS ID          :", EOS_ID)

print()
print("===== INPUT TEXT =====")

for sentence in sentences:
    print("-", sentence)


print()
print("===== INPUT IDS =====")
print(input_ids)

print()
print("===== TARGET IDS =====")
print(targets)

print()
print("===== ATTENTION MASK =====")
print(attention_mask)


print()
print("===== DECODED INPUTS =====")

for row in input_ids:
    print(decode_row(row))


print()
print("===== DECODED TARGETS =====")

for row in targets:
    print(decode_row(row))


print()
print("===== SHAPES =====")

print(
    "Input IDs      :",
    input_ids.shape
)

print(
    "Targets        :",
    targets.shape
)

print(
    "Attention mask :",
    attention_mask.shape
)

print(
    "Logits         :",
    logits.shape
)


print()
print("===== LOSS =====")

print(loss.item())

print(
    "Loss finite:",
    torch.isfinite(loss).item()
)
