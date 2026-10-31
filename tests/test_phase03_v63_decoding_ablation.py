"""CPU-only unit tests for V63 diagnostic inference token selection.

No model checkpoint or validation corpus is accessed by these tests.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
AUDIT = REPO / "tools" / "public-audits" / "phase03_v63_decoding_ablation_001.py"
spec = importlib.util.spec_from_file_location("v63_decoder_test_module", AUDIT)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot import V63 ablation diagnostic")
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


class V63DecodingAblationTests(unittest.TestCase):
    def test_token_trigram_repeat(self):
        self.assertEqual(D.repetition_bp([3, 4, 5, 3, 4, 5], 3), 2500)
        self.assertEqual(D.repetition_bp([3, 4, 5], 8), 0)

    def test_greedy_argmax(self):
        scores = torch.zeros((1, 1024))
        scores[0, 7] = 3.0
        outcome = D.decode_logits(
            scores, "GREEDY", [[]], [0], torch.Generator(device="cpu")
        )
        self.assertEqual(int(outcome[0].item()), 7)

    def test_repetition_penalty_only_on_generated_tokens(self):
        scores = torch.zeros((1, 1024))
        scores[0, 7] = 10.0
        scores[0, 8] = 9.0
        rng = torch.Generator(device="cpu")
        before = D.decode_logits(scores, "REP", [[]], [0], rng)
        after = D.decode_logits(scores, "REP", [[7]], [0], rng)
        self.assertEqual(int(before[0].item()), 7)
        self.assertEqual(int(after[0].item()), 8)
        self.assertEqual(float(scores[0, 7].item()), 10.0)

    def test_topk_nucleus_keeps_primary_candidate(self):
        scores = torch.full((2, 1024), -100.0)
        scores[:, 9] = 10.0
        scores[:, 10] = 5.0
        rng = torch.Generator(device="cpu").manual_seed(6301)
        result = D.decode_logits(scores, "TOPP", [[], []], [0, 1], rng)
        self.assertEqual(result.tolist(), [9, 9])

    def test_temperature_sampling_seed_reproducibility(self):
        scores = torch.zeros((3, 1024))
        scores[:, 5] = 2.0
        scores[:, 6] = 1.0
        rng_a = torch.Generator(device="cpu").manual_seed(6301)
        rng_b = torch.Generator(device="cpu").manual_seed(6301)
        result_a = D.decode_logits(scores, "TEMP", [[], [], []], [0, 1, 2], rng_a)
        result_b = D.decode_logits(scores, "TEMP", [[], [], []], [0, 1, 2], rng_b)
        self.assertEqual(result_a.tolist(), result_b.tolist())


if __name__ == "__main__":
    unittest.main()
