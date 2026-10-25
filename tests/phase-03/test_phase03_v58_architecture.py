import importlib.util
import sys
import unittest
from pathlib import Path

import torch


REPO = Path(__file__).resolve().parents[2]

PATH = (
    REPO
    / "mini_kuzai"
    / "phase03_model.py"
)

SPEC = importlib.util.spec_from_file_location(
    "phase03_model_test",
    PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        "Unable to load Phase 03 model"
    )

MODULE = importlib.util.module_from_spec(
    SPEC
)

sys.modules[SPEC.name] = MODULE

SPEC.loader.exec_module(MODULE)


class Phase03ArchitectureTests(
    unittest.TestCase
):

    def setUp(self):
        self.config = (
            MODULE.Phase03Config()
        )

        self.model = (
            MODULE.MiniKuzaiPhase03(
                self.config
            )
        )

    def test_config(self):
        self.assertEqual(
            self.config.vocab_size,
            1024,
        )

        self.assertEqual(
            self.config.context_length,
            2048,
        )

        self.assertEqual(
            self.config.d_model,
            128,
        )

        self.assertEqual(
            self.config.num_heads,
            4,
        )

        self.assertEqual(
            self.config.num_layers,
            4,
        )

        self.assertEqual(
            self.config.ff_dim,
            512,
        )

        self.assertEqual(
            self.config.head_dim,
            32,
        )

    def test_parameter_count(self):
        self.assertEqual(
            MODULE.count_parameters(
                self.model
            ),
            1184512,
        )

    def test_tied_embedding(self):
        self.assertIs(
            self.model.lm_head.weight,
            self.model.token_embedding.weight,
        )

    def test_forward_shape(self):
        tokens = torch.randint(
            3,
            1024,
            (2, 32),
        )

        logits = self.model(
            tokens
        )

        self.assertEqual(
            tuple(logits.shape),
            (
                2,
                32,
                1024,
            ),
        )

    def test_context_guard(self):
        tokens = torch.zeros(
            (
                1,
                2049,
            ),
            dtype=torch.long,
        )

        with self.assertRaises(
            ValueError
        ):
            self.model(tokens)


if __name__ == "__main__":
    unittest.main()
