import torch
import torch.nn as nn

from .mini_kuzai_mha import TransformerBlock


class MiniKuzaiDeep(nn.Module):

    def __init__(
        self,
        vocab_size,
        embedding_dim=8,
        hidden_dim=32,
        num_heads=2,
        num_layers=2,
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

        # Stack several Transformer blocks
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

        # Sequentially pass through every block
        for block in self.blocks:
            x = block(x)

        x = self.final_norm(x)

        logits = self.lm_head(x)

        return logits
