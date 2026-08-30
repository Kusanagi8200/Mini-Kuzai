import math
import torch
import torch.nn as nn


class SelfAttention(nn.Module):

    def __init__(self, embedding_dim):
        super().__init__()

        self.embedding_dim = embedding_dim

        self.q_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.k_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.v_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.out_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)

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

        scores = scores.masked_fill(mask, float("-inf"))

        attention_weights = torch.softmax(scores, dim=-1)

        context = attention_weights @ V

        return self.out_proj(context)


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


class TransformerBlock(nn.Module):

    def __init__(self, embedding_dim, hidden_dim):
        super().__init__()

        self.norm1 = nn.LayerNorm(embedding_dim)
        self.attention = SelfAttention(embedding_dim)

        self.norm2 = nn.LayerNorm(embedding_dim)
        self.mlp = MLP(embedding_dim, hidden_dim)

    def forward(self, x):

        x = x + self.attention(self.norm1(x))
        x = x + self.mlp(self.norm2(x))

        return x


class MiniKuzai(nn.Module):

    def __init__(
        self,
        vocab_size,
        embedding_dim=8,
        hidden_dim=32,
        max_sequence_length=32
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
