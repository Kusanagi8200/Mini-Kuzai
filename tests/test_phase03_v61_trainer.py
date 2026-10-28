#!/usr/bin/env python3

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v61_trainer as T


class V61TrainerTests(unittest.TestCase):

    def test_scheduler_shape(self):
        schedule = T.FrozenLRSchedule(
            base_lr=3e-4,
            min_lr=3e-5,
            warmup_steps=20,
            max_steps=577,
        )
        self.assertAlmostEqual(schedule.lr_for_step(1), 1.5e-5)
        self.assertAlmostEqual(schedule.lr_for_step(20), 3e-4)
        self.assertGreater(schedule.lr_for_step(145), 3e-5)
        self.assertAlmostEqual(schedule.lr_for_step(577), 3e-5)
        with self.assertRaises(ValueError):
            schedule.lr_for_step(578)

    def test_boundary_masks_terminal_and_intermediate(self):
        segments = [
            T.FrozenSegment(
                stream="CONTROLLED_TRAIN",
                source_id="a",
                segment_index=0,
                token_ids=(1, 10, 11, 12, 2),
            ),
            T.FrozenSegment(
                stream="PERSONA_CORE",
                source_id="b",
                segment_index=1,
                token_ids=(1, 20, 21, 2),
            ),
        ]
        token_ids = torch.tensor(
            [
                [1, 10, 11, 12, 2],
                [1, 20, 21, 2, 0],
            ],
            dtype=torch.long,
        )
        boundary_index = {
            ("CONTROLLED_TRAIN", "a", 0): (1,),
            ("PERSONA_CORE", "b", 1): (),
        }

        terminal, intermediate = T.build_boundary_masks(
            segments,
            token_ids,
            boundary_index,
        )

        self.assertTrue(bool(terminal[0, 3]))
        self.assertTrue(bool(terminal[1, 2]))
        self.assertEqual(int(terminal.sum()), 2)
        self.assertTrue(bool(intermediate[0, 1]))
        self.assertEqual(int(intermediate.sum()), 1)

        targets = token_ids[:, 1:]
        self.assertTrue(
            bool((targets[terminal] == T.EOS_ID).all())
        )
        self.assertTrue(
            bool((targets[intermediate] != T.EOS_ID).all())
        )

    def test_boundary_masks_require_index(self):
        segment = T.FrozenSegment(
            stream="CONTROLLED_TRAIN",
            source_id="missing",
            segment_index=0,
            token_ids=(1, 10, 2),
        )
        token_ids = torch.tensor(
            [[1, 10, 2]],
            dtype=torch.long,
        )
        with self.assertRaises(RuntimeError):
            T.build_boundary_masks(
                [segment],
                token_ids,
                {},
            )

    def test_boundary_objective_gradient_direction(self):
        logits = torch.randn(
            1,
            4,
            16,
            requires_grad=True,
        )
        targets = torch.tensor(
            [[5, 6, 7, T.EOS_ID]],
            dtype=torch.long,
        )
        terminal = torch.tensor(
            [[False, False, False, True]]
        )
        intermediate = torch.tensor(
            [[False, True, False, False]]
        )

        result = T.BOUNDARY.boundary_aware_eos_loss(
            logits,
            targets,
            terminal_mask=terminal,
            intermediate_mask=intermediate,
            eos_id=T.EOS_ID,
            pad_id=T.PAD_ID,
            terminal_weight=16.0,
            intermediate_weight=16.0,
        )
        result.total.backward()

        terminal_grad = float(
            logits.grad[0, 3, T.EOS_ID]
        )
        intermediate_grad = float(
            logits.grad[0, 1, T.EOS_ID]
        )

        self.assertLess(terminal_grad, 0.0)
        self.assertGreater(intermediate_grad, 0.0)

    def test_step_group_respects_global_limit(self):
        segments = [
            T.FrozenSegment(
                stream="CONTROLLED_TRAIN",
                source_id=str(index),
                segment_index=0,
                token_ids=tuple(
                    [1]
                    + [3] * 98
                    + [2]
                ),
            )
            for index in range(4)
        ]
        selected, exposure, hit = T._step_segment_groups(
            iter(segments),
            target_tokens=250,
            max_total_tokens=250,
            current_total_tokens=0,
        )
        self.assertEqual(len(selected), 2)
        self.assertEqual(exposure, 200)
        self.assertTrue(hit)

    def test_plateau_policy(self):
        protocol = {
            "exposure": {
                "reference_cycle_tokens": 100,
            },
            "evaluation": {
                "plateau_review": {
                    "minimum_cycle": 2,
                    "window_evaluations": 4,
                    "minimum_validation_improvement_bp": 50,
                }
            },
        }
        flat = [
            {"validation_loss": 3.0000},
            {"validation_loss": 2.9995},
            {"validation_loss": 2.9990},
            {"validation_loss": 2.9988},
        ]
        self.assertTrue(
            T._plateau_review_required(
                flat,
                exposure_tokens=250,
                protocol=protocol,
            )
        )

        improving = [
            {"validation_loss": 3.0},
            {"validation_loss": 2.9},
            {"validation_loss": 2.8},
            {"validation_loss": 2.7},
        ]
        self.assertFalse(
            T._plateau_review_required(
                improving,
                exposure_tokens=250,
                protocol=protocol,
            )
        )


if __name__ == "__main__":
    unittest.main()
