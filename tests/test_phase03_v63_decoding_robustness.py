"""CPU-only functional tests of V63 eight-seed decoding robustness.

No CUDA runtime, frozen model checkpoint or validation records accessed.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
SOURCE = (
    REPO / "tools" / "public-audits"
    / "phase03_v63_decoding_robustness_001.py"
)
spec = importlib.util.spec_from_file_location("v63_decoding_robustness_test", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("V63 robustness diagnostic cannot be imported")
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


class RobustnessDecoderTests(unittest.TestCase):

    def test_frozen_strategies_and_seeds(self):
        self.assertEqual(D.MODES, ("TEMP", "TOPP"))
        self.assertEqual(D.SEEDS, tuple(range(6301, 6309)))
        self.assertEqual((D.PROBES, D.MAX_NEW), (6, 96))

    def test_temperature_generator_deterministic_on_cpu(self):
        logits = torch.zeros((6, 1024), dtype=torch.float32)
        logits[:, 10] = 2
        logits[:, 11] = 3
        a = torch.Generator(device="cpu").manual_seed(D.SEEDS[0])
        b = torch.Generator(device="cpu").manual_seed(D.SEEDS[0])
        one = D.sample_logits(logits, "TEMP", a)
        two = D.sample_logits(logits, "TEMP", b)
        self.assertEqual(one.tolist(), two.tolist())
        self.assertEqual(len(one.tolist()), 6)

    def test_nucleus_keeps_highest_token(self):
        logits = torch.full((6, 1024), -100.0)
        logits[:, 23] = 20.0
        logits[:, 24] = 1.0
        rng = torch.Generator(device="cpu").manual_seed(D.SEEDS[0])
        choice = D.sample_logits(logits, "TOPP", rng)
        self.assertEqual(choice.tolist(), [23] * 6)

    def test_repeated_grams(self):
        self.assertEqual(D.repeated_gram_bp([1, 2, 3, 1, 2, 3], 3), 2500)
        self.assertEqual(D.repeated_gram_bp([1, 2, 3], 8), 0)

    def test_aggregation_short_lengths_and_seed_extremes(self):
        samples = [[7, 8, 9, 10] for _ in range(8 * 6)]
        samples[0] = [7, D.T.EOS_ID]
        samples[6] = [7, D.T.EOS_ID]
        with patch.object(
            D.T, "_decode_generated_probe_text", return_value=("text", True)
        ):
            metrics = D.aggregate(samples, object())
        self.assertEqual(len(metrics), 11)
        self.assertEqual(metrics["EOS"], 2)
        self.assertEqual(metrics["MIN_SEED_EOS"], 0)
        self.assertEqual(metrics["MAX_SEED_EOS"], 1)
        self.assertEqual(metrics["SHORT8"], 48)
        self.assertEqual(metrics["SHORT16"], 48)
        self.assertEqual(metrics["UTF8_INVALID"], 0)
        self.assertEqual(metrics["ROLE_LEAK"], 0)

    def test_role_marker_and_utf8_count_without_text_publication(self):
        samples = [[5, 6, 7] for _ in range(8 * 6)]
        with patch.object(D.T, "_decode_generated_probe_text") as decode:
            decode.side_effect = [
                ("USER:\n", False),
                ("MINI-KUZAI:\n", True),
                *[("ordinary", True)] * 46,
            ]
            metrics = D.aggregate(samples, object())
        self.assertEqual(metrics["ROLE_LEAK"], 2)
        self.assertEqual(metrics["UTF8_INVALID"], 1)
        self.assertTrue(all(isinstance(v, int) for v in metrics.values()))

    def test_unknown_decoder_fails(self):
        with self.assertRaises(RuntimeError):
            D.sample_logits(
                torch.zeros((1, 1024)), "UNRECOGNIZED",
                torch.Generator(device="cpu"),
            )


if __name__ == "__main__":
    unittest.main()
