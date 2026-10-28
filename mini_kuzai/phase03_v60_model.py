"""V60 initialization variant for the frozen Phase 03 architecture.

Architecture is identical to V58. Only parameter initialization changes.

Initialization policy:
- token embeddings: Normal(0, 0.02)
- positional embeddings: Normal(0, 0.02)
- linear weights: Normal(0, 0.02)
- linear biases: zero
- LayerNorm weights: one
- LayerNorm biases: zero
- residual output projections: Normal(0, 0.02 / sqrt(2 * n_layers))
- PAD embedding row: zero
- token embedding and LM head remain tied
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn

from mini_kuzai import phase03_model as V58


Phase03Config = V58.Phase03Config


class MiniKuzaiPhase03V60(V58.MiniKuzaiPhase03):

    INIT_STD = 0.02

    def __init__(self, config=None):
        if config is None:
            config = Phase03Config()
        super().__init__(config)

        self.apply(self._init_module)

        residual_std = (
            self.INIT_STD
            / math.sqrt(2.0 * config.num_layers)
        )
        for block in self.blocks:
            nn.init.normal_(
                block.attention.out_proj.weight,
                mean=0.0,
                std=residual_std,
            )
            nn.init.normal_(
                block.mlp.fc2.weight,
                mean=0.0,
                std=residual_std,
            )

        with torch.no_grad():
            self.token_embedding.weight[
                config.pad_token_id
            ].zero_()

        # Preserve weight tying explicitly after re-initialization.
        self.lm_head.weight = self.token_embedding.weight

    @classmethod
    def _init_module(cls, module):
        if isinstance(module, nn.Embedding):
            nn.init.normal_(
                module.weight,
                mean=0.0,
                std=cls.INIT_STD,
            )
        elif isinstance(module, nn.Linear):
            nn.init.normal_(
                module.weight,
                mean=0.0,
                std=cls.INIT_STD,
            )
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)


def count_parameters(model):
    return V58.count_parameters(model)
