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

from mini_kuzai.phase03_v62_margin_loss import boundary_margin_loss


class V62MarginLossTests(unittest.TestCase):

    def setUp(self):
        torch.manual_seed(42)
        self.logits = torch.randn(
            2, 4, 8, dtype=torch.float32, requires_grad=True
        )
        self.targets = torch.tensor(
            [[3, 4, 5, 2], [6, 7, 3, 0]],
            dtype=torch.long,
        )
        self.terminal = torch.zeros(2, 4, dtype=torch.bool)
        self.terminal[0, 3] = True
        self.intermediate = torch.zeros(2, 4, dtype=torch.bool)
        self.intermediate[0, 1] = True

    def call(self, logits, margin=0.5, tw=4.0, iw=8.0):
        return boundary_margin_loss(
            logits,
            self.targets,
            terminal_mask=self.terminal,
            intermediate_mask=self.intermediate,
            eos_id=2,
            pad_id=0,
            margin=margin,
            terminal_weight=tw,
            intermediate_weight=iw,
        )

    def test_zero_weights_equal_standard_cross_entropy(self):
        result = self.call(
            self.logits,
            tw=0.0,
            iw=0.0,
        )
        expected = F.cross_entropy(
            self.logits.reshape(-1, 8),
            self.targets.reshape(-1),
            ignore_index=0,
            reduction="mean",
        )
        self.assertTrue(
            torch.allclose(
                result.total,
                expected,
                atol=1e-7,
                rtol=0.0,
            )
        )

    def test_terminal_hinge_pushes_eos_up_when_violated(self):
        logits = torch.zeros(
            2, 4, 8, dtype=torch.float32, requires_grad=True
        )
        result = self.call(logits, margin=0.5, tw=4.0, iw=0.0)
        result.total.backward()

        eos_grad = float(logits.grad[0, 3, 2])
        competitor_grads = logits.grad[0, 3].clone()
        competitor_grads[2] = 0
        self.assertLess(eos_grad, 0.0)
        self.assertGreater(float(competitor_grads.max()), 0.0)
        self.assertEqual(result.terminal_active, 1)

    def test_terminal_hinge_inactive_when_margin_satisfied(self):
        logits = torch.zeros(
            2, 4, 8, dtype=torch.float32, requires_grad=True
        )
        logits.data[0, 3, 2] = 2.0
        result = self.call(logits, margin=0.5, tw=4.0, iw=0.0)
        self.assertEqual(result.terminal_active, 0)
        self.assertEqual(
            float(result.terminal_extra.detach()),
            0.0,
        )

    def test_intermediate_hinge_pushes_true_up_and_eos_down(self):
        logits = torch.zeros(
            2, 4, 8, dtype=torch.float32, requires_grad=True
        )
        result = self.call(logits, margin=0.5, tw=0.0, iw=8.0)
        result.total.backward()

        true_id = int(self.targets[0, 1])
        true_grad = float(logits.grad[0, 1, true_id])
        eos_grad = float(logits.grad[0, 1, 2])
        self.assertLess(true_grad, 0.0)
        self.assertGreater(eos_grad, 0.0)
        self.assertEqual(result.intermediate_active, 1)

    def test_intermediate_hinge_inactive_when_margin_satisfied(self):
        logits = torch.zeros(
            2, 4, 8, dtype=torch.float32, requires_grad=True
        )
        true_id = int(self.targets[0, 1])
        logits.data[0, 1, true_id] = 2.0
        result = self.call(logits, margin=0.5, tw=0.0, iw=8.0)
        self.assertEqual(result.intermediate_active, 0)
        self.assertEqual(
            float(result.intermediate_extra.detach()),
            0.0,
        )

    def test_boundary_inventory_and_pad(self):
        result = self.call(self.logits)
        self.assertEqual(result.valid_tokens, 7)
        self.assertEqual(result.terminal_positions, 1)
        self.assertEqual(result.intermediate_positions, 1)

    def test_masks_must_be_disjoint(self):
        bad = self.intermediate.clone()
        bad[0, 3] = True
        with self.assertRaises(ValueError):
            boundary_margin_loss(
                self.logits,
                self.targets,
                terminal_mask=self.terminal,
                intermediate_mask=bad,
                margin=0.5,
                terminal_weight=1.0,
                intermediate_weight=1.0,
            )

    def test_terminal_requires_eos_target(self):
        bad = self.terminal.clone()
        bad[0, 3] = False
        bad[0, 0] = True
        with self.assertRaises(ValueError):
            boundary_margin_loss(
                self.logits,
                self.targets,
                terminal_mask=bad,
                intermediate_mask=self.intermediate,
                margin=0.5,
                terminal_weight=1.0,
                intermediate_weight=1.0,
            )

    def test_intermediate_rejects_eos_target(self):
        bad = self.intermediate.clone()
        bad[0, 1] = False
        bad[0, 3] = True
        with self.assertRaises(ValueError):
            boundary_margin_loss(
                self.logits,
                self.targets,
                terminal_mask=self.terminal,
                intermediate_mask=bad,
                margin=0.5,
                terminal_weight=1.0,
                intermediate_weight=1.0,
            )


if __name__ == "__main__":
    unittest.main()
