import math
import torch
import torch.nn as nn

torch.manual_seed(42)


# ==================================================
# Self-Attention
# ==================================================

class SelfAttention(nn.Module):

    def __init__(self, embedding_dim):
        super().__init__()

        self.embedding_dim = embedding_dim

        self.q_proj = nn.Linear(
            embedding_dim,
            embedding_dim,
            bias=False
        )

        self.k_proj = nn.Linear(
            embedding_dim,
            embedding_dim,
            bias=False
        )

        self.v_proj = nn.Linear(
            embedding_dim,
            embedding_dim,
            bias=False
        )

        self.out_proj = nn.Linear(
            embedding_dim,
            embedding_dim,
            bias=False
        )

    def forward(self, x):

        Q = self.q_proj(x)
        K = self.k_proj(x)
        V = self.v_proj(x)

        scores = (Q @ K.T) / math.sqrt(self.embedding_dim)

        sequence_length = x.shape[0]

        mask = torch.triu(
            torch.ones(
                sequence_length,
                sequence_length,
                dtype=torch.bool,
                device=x.device
            ),
            diagonal=1
        )

        scores = scores.masked_fill(
            mask,
            float("-inf")
        )

        attention_weights = torch.softmax(
            scores,
            dim=-1
        )

        context = attention_weights @ V

        return self.out_proj(context)


# ==================================================
# MLP
# ==================================================

class MLP(nn.Module):

    def __init__(self, embedding_dim, hidden_dim):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, embedding_dim)
        )

    def forward(self, x):
        return self.network(x)


# ==================================================
# Transformer Block
# ==================================================

class TransformerBlock(nn.Module):

    def __init__(self, embedding_dim, hidden_dim):
        super().__init__()

        self.norm1 = nn.LayerNorm(embedding_dim)
        self.attention = SelfAttention(embedding_dim)

        self.norm2 = nn.LayerNorm(embedding_dim)
        self.mlp = MLP(
            embedding_dim,
            hidden_dim
        )

    def forward(self, x):

        x = x + self.attention(
            self.norm1(x)
        )

        x = x + self.mlp(
            self.norm2(x)
        )

        return x


# ==================================================
# Mini-Kuzai
# ==================================================

class MiniKuzai(nn.Module):

    def __init__(
        self,
        vocab_size,
        embedding_dim,
        hidden_dim,
        max_sequence_length
    ):
        super().__init__()

        self.token_embedding = nn.Embedding(
            vocab_size,
            embedding_dim
        )

        self.position_embedding = nn.Embedding(
            max_sequence_length,
            embedding_dim
        )

        self.transformer = TransformerBlock(
            embedding_dim,
            hidden_dim
        )

        self.final_norm = nn.LayerNorm(
            embedding_dim
        )

        self.lm_head = nn.Linear(
            embedding_dim,
            vocab_size,
            bias=False
        )

    def forward(self, token_ids):

        sequence_length = token_ids.shape[0]

        positions = torch.arange(
            sequence_length,
            device=token_ids.device
        )

        x = (
            self.token_embedding(token_ids)
            + self.position_embedding(positions)
        )

        x = self.transformer(x)
        x = self.final_norm(x)

        return self.lm_head(x)


# ==================================================
# Vocabulary
# ==================================================

with open("corpus.txt", "r", encoding="utf-8") as f:
    text = f.read()

tokens = text.split()
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

model = MiniKuzai(
    vocab_size=len(vocabulary),
    embedding_dim=8,
    hidden_dim=32,
    max_sequence_length=32
)


# ==================================================
# Training example
# ==================================================

sentence = "mini kuzai learns from data"

ids = torch.tensor(
    [token_to_id[word] for word in sentence.split()],
    dtype=torch.long
)

# Input:
# mini kuzai learns from

inputs = ids[:-1]

# Targets:
# kuzai learns from data

targets = ids[1:]


print("===== MINI-KUZAI TRAINING STEP =====")

print("\nSentence:")
print(sentence)

print("\nInputs:")
print(
    [id_to_token[i.item()] for i in inputs]
)

print("\nTargets:")
print(
    [id_to_token[i.item()] for i in targets]
)


# ==================================================
# Loss BEFORE training
# ==================================================

criterion = nn.CrossEntropyLoss()

logits = model(inputs)

loss_before = criterion(
    logits,
    targets
)


# ==================================================
# Inspect one weight BEFORE training
# ==================================================

mini_id = token_to_id["mini"]

weight_before = (
    model.token_embedding
    .weight[mini_id, 0]
    .item()
)


# ==================================================
# Backpropagation
# ==================================================

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.01
)

optimizer.zero_grad()

loss_before.backward()


# ==================================================
# Inspect gradient
# ==================================================

gradient = (
    model.token_embedding
    .weight.grad[mini_id, 0]
    .item()
)


# ==================================================
# Update weights
# ==================================================

optimizer.step()


# ==================================================
# Inspect weight AFTER training
# ==================================================

weight_after = (
    model.token_embedding
    .weight[mini_id, 0]
    .item()
)


# ==================================================
# Loss AFTER training
# ==================================================

with torch.no_grad():

    logits_after = model(inputs)

    loss_after = criterion(
        logits_after,
        targets
    )


# ==================================================
# Results
# ==================================================

print("\n===== LOSS =====")

print(
    "Before training:",
    loss_before.item()
)

print(
    "After one step :",
    loss_after.item()
)


print("\n===== ONE MODEL WEIGHT =====")

print(
    "Before:",
    weight_before
)

print(
    "Gradient:",
    gradient
)

print(
    "After :",
    weight_after
)

print(
    "\nWeight changed:",
    weight_before != weight_after
)
