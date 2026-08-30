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

        output = self.out_proj(context)

        return output


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

        # Attention + residual
        x = x + self.attention(
            self.norm1(x)
        )

        # MLP + residual
        x = x + self.mlp(
            self.norm2(x)
        )

        return x


# ==================================================
# Test
# ==================================================

embedding_dim = 8
hidden_dim = 32

block = TransformerBlock(
    embedding_dim,
    hidden_dim
)

# Simulate 5 token embeddings
x = torch.randn(5, embedding_dim)

output = block(x)

print("===== MINI-KUZAI TRANSFORMER BLOCK =====")

print("\nInput shape  :", x.shape)
print("Output shape :", output.shape)

print("\n===== ARCHITECTURE =====")
print(block)

print("\n===== FIRST TOKEN =====")

print("\nInput:")
print(x[0].detach())

print("\nOutput:")
print(output[0].detach())

print("\nSame shape:")
print(x.shape == output.shape)
