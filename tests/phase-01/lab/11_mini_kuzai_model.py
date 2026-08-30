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
# Mini-Kuzai Language Model
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

        # Language Model Head
        # Converts each 8-value vector into
        # one score per vocabulary token.
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

        logits = self.lm_head(x)

        return logits


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
# Configuration
# ==================================================

vocab_size = len(vocabulary)

embedding_dim = 8
hidden_dim = 32
max_sequence_length = 32


# ==================================================
# Create model
# ==================================================

model = MiniKuzai(
    vocab_size=vocab_size,
    embedding_dim=embedding_dim,
    hidden_dim=hidden_dim,
    max_sequence_length=max_sequence_length
)


# ==================================================
# Test input
# ==================================================

sentence = "mini kuzai runs on linux"
words = sentence.split()

token_ids = torch.tensor(
    [token_to_id[word] for word in words],
    dtype=torch.long
)

logits = model(token_ids)


# ==================================================
# Statistics
# ==================================================

parameter_count = sum(
    p.numel()
    for p in model.parameters()
)


print("===== MINI-KUZAI LANGUAGE MODEL =====")

print("\nVocabulary size :", vocab_size)
print("Sequence length :", len(token_ids))
print("Embedding size  :", embedding_dim)

print("\nInput IDs:")
print(token_ids.tolist())

print("\nLogits shape:")
print(logits.shape)

print("\nTotal parameters:")
print(parameter_count)

print("\n===== MODEL =====")
print(model)


# ==================================================
# Next-token probabilities
# ==================================================

# The final position is currently "linux".
# Its logits represent Mini-Kuzai's scores
# for the token that should come next.

last_logits = logits[-1]

probabilities = torch.softmax(
    last_logits,
    dim=-1
)

top_probabilities, top_ids = torch.topk(
    probabilities,
    k=5
)


print("\n===== NEXT TOKEN AFTER 'linux' =====")

for probability, token_id in zip(
    top_probabilities,
    top_ids
):
    token = id_to_token[token_id.item()]

    print(
        f"{token:12s} "
        f"{probability.item():.4f}"
    )

print(
    "\nProbability sum:",
    probabilities.sum().item()
)
