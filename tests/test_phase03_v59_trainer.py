#!/usr/bin/env python3

from __future__ import annotations

import unittest

import torch

from mini_kuzai import phase03_v59_trainer as T


def segment(stream, source, index, length):
    ids = [T.BOS_ID] + [3] * (length - 2) + [T.EOS_ID]
    return T.FrozenSegment(
        stream=stream,
        source_id=source,
        segment_index=index,
        token_ids=tuple(ids),
    )


class FrozenLRScheduleTests(unittest.TestCase):

    def test_warmup_and_floor(self):
        schedule = T.FrozenLRSchedule(
            base_lr=3e-4,
            min_lr=3e-5,
            warmup_steps=15,
            max_steps=145,
        )
        self.assertAlmostEqual(
            schedule.lr_for_step(1),
            2e-5,
        )
        self.assertAlmostEqual(
            schedule.lr_for_step(15),
            3e-4,
        )
        self.assertAlmostEqual(
            schedule.lr_for_step(145),
            3e-5,
        )

    def test_out_of_budget_rejected(self):
        schedule = T.FrozenLRSchedule(
            base_lr=3e-4,
            min_lr=3e-5,
            warmup_steps=15,
            max_steps=145,
        )
        with self.assertRaises(ValueError):
            schedule.lr_for_step(146)


class SamplerResumeTests(unittest.TestCase):

    def make_streams(self):
        return {
            "CONTROLLED_TRAIN": [
                segment("CONTROLLED_TRAIN", "c1", 0, 11),
                segment("CONTROLLED_TRAIN", "c2", 0, 13),
            ],
            "PERSONA_CORE": [
                segment("PERSONA_CORE", "p1", 0, 17),
                segment("PERSONA_CORE", "p2", 0, 19),
            ],
            "GENERAL_SUPPORT": [
                segment("GENERAL_SUPPORT", "g1", 0, 23),
                segment("GENERAL_SUPPORT", "g2", 0, 29),
            ],
            "LEGACY_STRUCTURED_KEEP": [
                segment("LEGACY_STRUCTURED_KEEP", "l1", 0, 31),
                segment("LEGACY_STRUCTURED_KEEP", "l2", 0, 37),
            ],
        }

    def test_resume_preserves_pending_cycle_order(self):
        streams = self.make_streams()
        shares = {
            "CONTROLLED_TRAIN": 3000,
            "PERSONA_CORE": 4658,
            "GENERAL_SUPPORT": 1500,
            "LEGACY_STRUCTURED_KEEP": 842,
        }
        left = T.StreamQuotaSampler(
            streams,
            shares,
            reference_cycle_tokens=200,
            seed=42,
        )
        prefix = [
            left.next_segment(2)
            for _ in range(5)
        ]
        self.assertTrue(all(prefix))

        state = left.state_dict()

        expected = []
        while True:
            item = left.next_segment(2)
            if item is None:
                break
            expected.append(
                (item.stream, item.source_id, item.segment_index)
            )

        right = T.StreamQuotaSampler(
            streams,
            shares,
            reference_cycle_tokens=200,
            seed=42,
        )
        right.load_state_dict(state)

        actual = []
        while True:
            item = right.next_segment(2)
            if item is None:
                break
            actual.append(
                (item.stream, item.source_id, item.segment_index)
            )

        self.assertEqual(actual, expected)


class BatchingTests(unittest.TestCase):

    def test_right_padding_and_token_counts(self):
        values = [
            segment("CONTROLLED_TRAIN", "a", 0, 5),
            segment("CONTROLLED_TRAIN", "b", 0, 8),
        ]
        batch, exposure, predicted = T.pad_batch(
            values,
            torch.device("cpu"),
        )
        self.assertEqual(tuple(batch.shape), (2, 8))
        self.assertEqual(exposure, 13)
        self.assertEqual(predicted, 11)
        self.assertTrue(
            torch.equal(
                batch[0, 5:],
                torch.zeros(3, dtype=torch.long),
            )
        )

    def test_microbatch_limit(self):
        values = [
            segment("CONTROLLED_TRAIN", str(i), 0, 4)
            for i in range(9)
        ]
        with self.assertRaises(ValueError):
            T.pad_batch(
                values,
                torch.device("cpu"),
            )


class ExposureBudgetTests(unittest.TestCase):

    def test_step_never_crosses_global_budget(self):
        values = iter(
            [
                segment("PERSONA_CORE", "a", 0, 40),
                segment("PERSONA_CORE", "b", 0, 40),
                segment("PERSONA_CORE", "c", 0, 40),
            ]
        )
        selected, exposure, hit = T._step_segment_groups(
            values,
            target_tokens=70,
            max_total_tokens=100,
            current_total_tokens=30,
        )
        self.assertEqual(len(selected), 1)
        self.assertEqual(exposure, 40)
        self.assertTrue(hit)


class BlindBoundaryTests(unittest.TestCase):

    def test_trainer_has_no_blind_corpus_path(self):
        source = T.__file__
        text = open(
            source,
            encoding="utf-8",
        ).read()
        self.assertNotIn(
            "data/phase-03/blind-test",
            text,
        )
        self.assertNotIn(
            "/blind-test/",
            text,
        )


if __name__ == "__main__":
    unittest.main()
