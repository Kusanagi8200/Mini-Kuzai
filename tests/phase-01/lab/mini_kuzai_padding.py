import math
import torch
import torch.nn as nn


# ==================================================
# Multi-Head Attention with padding mask
# ==================================================

class MultiHeadAttention(nn.Module):

    def __init__(self, embedding_dim, num_heads):
        super().__init__()

        assert embedding_dim % num_heads == 0

        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.head_dim = embedding_dim // num_heads

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

    def forward(self, x, attention_mask=None):

        batch_size, sequence_length, _ = x.shape

        Q = self.q_proj(x)
        K = self.k_proj(x)
        V = self.v_proj(x)

        Q = Q.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim
        ).transpose(1, 2)

        K = K.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim
        ).transpose(1, 2)

        V = V.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim
        ).transpose(1, 2)

        scores = (
            Q @ K.transpose(-2, -1)
        ) / math.sqrt(self.head_dim)

        # --------------------------------------------------
        # Causal mask
        # Future tokens cannot be seen
        # --------------------------------------------------

        causal_mask = torch.triu(
            torch.ones(
                sequence_length,
                sequence_length,
                dtype=torch.bool,
                device=x.device
            ),
            diagonal=1
        )

        scores = scores.masked_fill(
            causal_mask,
            float("-inf")
        )

        # --------------------------------------------------
        # Padding mask
        #
        # attention_mask:
        # 1 = real token
        # 0 = padding
        #
        # Shape:
        # [B,T] -> [B,1,1,T]
        # --------------------------------------------------

        if attention_mask is not None:

            key_mask = attention_mask[
                :, None, None, :
            ].bool()

            scores = scores.masked_fill(
                ~key_mask,
                float("-inf")
            )

        weights = torch.softmax(
            scores,
            dim=-1
        )

        context = weights @ V

        context = (
            context
            .transpose(1, 2)
            .contiguous()
            .view(
                batch_size,
                sequence_length,
                self.embedding_dim
            )
        )

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

    def __init__(
        self,
        embedding_dim,
        hidden_dim,
        num_heads
    ):
        super().__init__()

        self.norm1 = nn.LayerNorm(
            embedding_dim
        )

        self.attention = MultiHeadAttention(
            embedding_dim,
            num_heads
        )

        self.norm2 = nn.LayerNorm(
            embedding_dim
        )

        self.mlp = MLP(
            embedding_dim,
            hidden_dim
        )

    def forward(
        self,
        x,
        attention_mask=None
    ):

        x = x + self.attention(
            self.norm1(x),
            attention_mask
        )

        x = x + self.mlp(
            self.norm2(x)
        )

        return x


# ==================================================
# Mini-Kuzai with padding support
# ==================================================

class MiniKuzaiPadding(nn.Module):

    def __init__(
        self,
        vocab_size,
        embedding_dim=8,
        hidden_dim=32,
        num_heads=2,
        num_layers=2,
        max_sequence_length=32,
        pad_token_id=0
    ):
        super().__init__()

        self.pad_token_id = pad_token_id

        self.token_embedding = nn.Embedding(
            vocab_size,
            embedding_dim,
            padding_idx=pad_token_id
        )

        self.position_embedding = nn.Embedding(
            max_sequence_length,
            embedding_dim
        )

        self.blocks = nn.ModuleList([
            TransformerBlock(
                embedding_dim,
                hidden_dim,
                num_heads
            )
            for _ in range(num_layers)
        ])

        self.final_norm = nn.LayerNorm(
            embedding_dim
        )

        self.lm_head = nn.Linear(
            embedding_dim,
            vocab_size,
            bias=False
        )

    def forward(
        self,
        token_ids,
        attention_mask=None
    ):

        batch_size, sequence_length = (
            token_ids.shape
        )

        positions = torch.arange(
            sequence_length,
            device=token_ids.device
        )

        x = (
            self.token_embedding(token_ids)
            + self.position_embedding(positions)
        )

        for block in self.blocks:

            x = block(
                x,
                attention_mask
            )

        x = self.final_norm(x)

        return self.lm_head(x)
