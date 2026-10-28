#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import torch
import torch.nn.functional as F


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai.phase03_v61_boundary_loss import (
    boundary_aware_eos_loss,
)


class BoundaryAwareEOSLossTests(unittest.TestCase):

    def setUp(self):
        torch.manual_seed(42)
        self.logits = torch.randn(
            2,
            4,
            8,
            dtype=torch.float32,
            requires_grad=True,
        )
        self.targets = torch.tensor(
            [
                [3, 4, 5, 2],
                [6, 7, 3, 0],
            ],
            dtype=torch.long,
        )
        self.terminal = torch.zeros(
            2,
            4,
            dtype=torch.bool,
        )
        self.terminal[0, 3] = True

        self.intermediate = torch.zeros(
            2,
            4,
            dtype=torch.bool,
        )
        self.intermediate[0, 1] = True

    def test_zero_weights_equal_standard_cross_entropy(self):
        result = boundary_aware_eos_loss(
            self.logits,
            self.targets,
            terminal_mask=self.terminal,
            intermediate_mask=self.intermediate,
            eos_id=2,
            pad_id=0,
            terminal_weight=0.0,
            intermediate_weight=0.0,
        )

        expected = F.cross_entropy(
            self.logits.reshape(-1, 8),
            self.targets.reshape(-1),
            ignore_index=0,
        )
        self.assertTrue(
            torch.allclose(
                result.total,
                expected,
                atol=1e-7,
                rtol=0.0,
            )
        )

    def test_terminal_weight_increases_loss_and_eos_gradient(self):
        plain_logits = self.logits.detach().clone().requires_grad_(True)
        weighted_logits = self.logits.detach().clone().requires_grad_(True)

        plain = boundary_aware_eos_loss(
            plain_logits,
            self.targets,
            terminal_mask=self.terminal,
            intermediate_mask=self.intermediate,
            terminal_weight=0.0,
            intermediate_weight=0.0,
        )
        weighted = boundary_aware_eos_loss(
            weighted_logits,
            self.targets,
            terminal_mask=self.terminal,
            intermediate_mask=self.intermediate,
            terminal_weight=16.0,
            intermediate_weight=0.0,
        )

        plain.total.backward()
        weighted.total.backward()

        self.assertGreater(
            float(weighted.total.detach()),
            float(plain.total.detach()),
        )

        # EOS target gradient is negative. A larger absolute value means
        # stronger pressure to increase EOS probability.
        plain_grad = float(
            plain_logits.grad[0, 3, 2]
        )
        weighted_grad = float(
            weighted_logits.grad[0, 3, 2]
        )
        self.assertLess(weighted_grad, plain_grad)
        self.assertGreater(
            abs(weighted_grad),
            abs(plain_grad) * 10,
        )

    def test_intermediate_weight_pushes_eos_down(self):
        plain_logits = self.logits.detach().clone().requires_grad_(True)
        weighted_logits = self.logits.detach().clone().requires_grad_(True)

        plain = boundary_aware_eos_loss(
            plain_logits,
            self.targets,
            terminal_mask=self.terminal,
            intermediate_mask=self.intermediate,
            terminal_weight=0.0,
            intermediate_weight=0.0,
        )
        weighted = boundary_aware_eos_loss(
            weighted_logits,
            self.targets,
            terminal_mask=self.terminal,
            intermediate_mask=self.intermediate,
            terminal_weight=0.0,
            intermediate_weight=16.0,
        )

        plain.total.backward()
        weighted.total.backward()

        plain_grad = float(
            plain_logits.grad[0, 1, 2]
        )
        weighted_grad = float(
            weighted_logits.grad[0, 1, 2]
        )

        # EOS is not the true target here. Positive gradient lowers EOS logit
        # under gradient descent.
        self.assertGreater(weighted_grad, plain_grad)

    def test_boundary_counts_and_pad_exclusion(self):
        result = boundary_aware_eos_loss(
            self.logits,
            self.targets,
            terminal_mask=self.terminal,
            intermediate_mask=self.intermediate,
            terminal_weight=16.0,
            intermediate_weight=16.0,
        )
        self.assertEqual(result.valid_tokens, 7)
        self.assertEqual(result.terminal_positions, 1)
        self.assertEqual(result.intermediate_positions, 1)

    def test_terminal_mask_requires_eos_target(self):
        bad = self.terminal.clone()
        bad[0, 3] = False
        bad[0, 0] = True

        with self.assertRaises(ValueError):
            boundary_aware_eos_loss(
                self.logits,
                self.targets,
                terminal_mask=bad,
                intermediate_mask=self.intermediate,
                terminal_weight=1.0,
                intermediate_weight=1.0,
            )

    def test_intermediate_mask_rejects_eos_target(self):
        bad = self.intermediate.clone()
        bad[0, 1] = False
        bad[0, 3] = True

        with self.assertRaises(ValueError):
            boundary_aware_eos_loss(
                self.logits,
                self.targets,
                terminal_mask=self.terminal,
                intermediate_mask=bad,
                terminal_weight=1.0,
                intermediate_weight=1.0,
            )

    def test_masks_must_be_disjoint(self):
        bad = self.intermediate.clone()
        bad[0, 3] = True

        with self.assertRaises(ValueError):
            boundary_aware_eos_loss(
                self.logits,
                self.targets,
                terminal_mask=self.terminal,
                intermediate_mask=bad,
                terminal_weight=1.0,
                intermediate_weight=1.0,
            )


if __name__ == "__main__":
    unittest.main()
