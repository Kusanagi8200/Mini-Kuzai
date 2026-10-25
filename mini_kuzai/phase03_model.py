"""Frozen Phase 03 Mini-Kuzai architecture.

V58 architecture:

vocabulary: 1024
context: 2048
d_model: 128
heads: 4
layers: 4
MLP: 512
pre-norm
GELU
learned positional embeddings
tied token embedding / LM head

The model expects right-padded batches when padding is required.
Padding positions must be excluded from the training loss.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass(frozen=True)
class Phase03Config:
    vocab_size: int = 1024
    context_length: int = 2048
    d_model: int = 128
    num_heads: int = 4
    num_layers: int = 4
    ff_dim: int = 512
    pad_token_id: int = 0

    @property
    def head_dim(self):
        return (
            self.d_model
            // self.num_heads
        )


class CausalSelfAttention(nn.Module):

    def __init__(self, config):
        super().__init__()

        if (
            config.d_model
            % config.num_heads
            != 0
        ):
            raise ValueError(
                "d_model must be divisible by num_heads"
            )

        self.num_heads = (
            config.num_heads
        )

        self.head_dim = (
            config.head_dim
        )

        self.q_proj = nn.Linear(
            config.d_model,
            config.d_model,
            bias=False,
        )

        self.k_proj = nn.Linear(
            config.d_model,
            config.d_model,
            bias=False,
        )

        self.v_proj = nn.Linear(
            config.d_model,
            config.d_model,
            bias=False,
        )

        self.out_proj = nn.Linear(
            config.d_model,
            config.d_model,
            bias=False,
        )

    def forward(self, x):
        batch_size, sequence_length, d_model = (
            x.shape
        )

        def split_heads(value):
            return (
                value.view(
                    batch_size,
                    sequence_length,
                    self.num_heads,
                    self.head_dim,
                )
                .transpose(1, 2)
            )

        q = split_heads(
            self.q_proj(x)
        )

        k = split_heads(
            self.k_proj(x)
        )

        v = split_heads(
            self.v_proj(x)
        )

        context = (
            F.scaled_dot_product_attention(
                q,
                k,
                v,
                dropout_p=0.0,
                is_causal=True,
            )
        )

        context = (
            context
            .transpose(1, 2)
            .contiguous()
            .view(
                batch_size,
                sequence_length,
                d_model,
            )
        )

        return self.out_proj(
            context
        )


class MLP(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.fc1 = nn.Linear(
            config.d_model,
            config.ff_dim,
            bias=True,
        )

        self.fc2 = nn.Linear(
            config.ff_dim,
            config.d_model,
            bias=True,
        )

    def forward(self, x):
        return self.fc2(
            F.gelu(
                self.fc1(x)
            )
        )


class TransformerBlock(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.norm1 = nn.LayerNorm(
            config.d_model
        )

        self.attention = (
            CausalSelfAttention(
                config
            )
        )

        self.norm2 = nn.LayerNorm(
            config.d_model
        )

        self.mlp = MLP(
            config
        )

    def forward(self, x):
        x = (
            x
            + self.attention(
                self.norm1(x)
            )
        )

        x = (
            x
            + self.mlp(
                self.norm2(x)
            )
        )

        return x


class MiniKuzaiPhase03(nn.Module):

    def __init__(
        self,
        config=None,
    ):
        super().__init__()

        if config is None:
            config = Phase03Config()

        self.config = config

        self.token_embedding = nn.Embedding(
            config.vocab_size,
            config.d_model,
            padding_idx=(
                config.pad_token_id
            ),
        )

        self.position_embedding = (
            nn.Embedding(
                config.context_length,
                config.d_model,
            )
        )

        self.blocks = nn.ModuleList(
            [
                TransformerBlock(
                    config
                )
                for _ in range(
                    config.num_layers
                )
            ]
        )

        self.final_norm = nn.LayerNorm(
            config.d_model
        )

        self.lm_head = nn.Linear(
            config.d_model,
            config.vocab_size,
            bias=False,
        )

        self.lm_head.weight = (
            self.token_embedding.weight
        )

    def forward(self, token_ids):
        if token_ids.ndim != 2:
            raise ValueError(
                "token_ids must have shape [batch, sequence]"
            )

        batch_size, sequence_length = (
            token_ids.shape
        )

        if (
            sequence_length
            > self.config.context_length
        ):
            raise ValueError(
                "sequence exceeds frozen context length"
            )

        positions = torch.arange(
            sequence_length,
            device=token_ids.device,
        )

        x = (
            self.token_embedding(
                token_ids
            )
            + self.position_embedding(
                positions
            )[None, :, :]
        )

        for block in self.blocks:
            x = block(x)

        x = self.final_norm(x)

        return self.lm_head(x)


def count_parameters(model):
    return sum(
        parameter.numel()
        for parameter
        in model.parameters()
    )
