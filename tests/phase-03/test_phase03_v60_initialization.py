import math
import sys
import unittest
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v60_model as MODULE


class V60InitializationTests(unittest.TestCase):

    def setUp(self):
        torch.manual_seed(42)
        self.config = MODULE.Phase03Config()
        self.model = MODULE.MiniKuzaiPhase03V60(self.config)

    def test_architecture_is_unchanged(self):
        self.assertEqual(self.config.vocab_size, 1024)
        self.assertEqual(self.config.context_length, 2048)
        self.assertEqual(self.config.d_model, 128)
        self.assertEqual(self.config.num_heads, 4)
        self.assertEqual(self.config.num_layers, 4)
        self.assertEqual(self.config.ff_dim, 512)
        self.assertEqual(
            MODULE.count_parameters(self.model),
            1184512,
        )

    def test_embedding_and_lm_head_are_tied(self):
        self.assertIs(
            self.model.lm_head.weight,
            self.model.token_embedding.weight,
        )

    def test_pad_embedding_is_zero(self):
        pad = self.model.token_embedding.weight[
            self.config.pad_token_id
        ]
        self.assertEqual(
            int(torch.count_nonzero(pad).item()),
            0,
        )

    def test_embedding_initialization_scale(self):
        values = self.model.token_embedding.weight[1:].detach()
        std = float(values.std())
        self.assertGreater(std, 0.018)
        self.assertLess(std, 0.022)

    def test_position_initialization_scale(self):
        std = float(
            self.model.position_embedding.weight.detach().std()
        )
        self.assertGreater(std, 0.018)
        self.assertLess(std, 0.022)

    def test_residual_projection_scale(self):
        expected = 0.02 / math.sqrt(
            2.0 * self.config.num_layers
        )
        for block in self.model.blocks:
            for weight in (
                block.attention.out_proj.weight,
                block.mlp.fc2.weight,
            ):
                actual = float(weight.detach().std())
                self.assertGreater(actual, expected * 0.85)
                self.assertLess(actual, expected * 1.15)

    def test_forward_shape(self):
        tokens = torch.randint(3, 1024, (2, 32))
        logits = self.model(tokens)
        self.assertEqual(tuple(logits.shape), (2, 32, 1024))


if __name__ == "__main__":
    unittest.main()
