"""CPU-only checks for private V63 human-review integrity and aggregation."""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load V63 review module")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


D = module("v63_human_private_review", "tools/phase03_v63_semantic_generation_review_001.py")
A = module("v63_human_audit", "tools/public-audits/phase03_v63_semantic_generation_review_001.py")


def synthetic_samples():
    entries = []
    for index, (seed, slot) in enumerate(
        ((s, p) for s in D.SEEDS for p in range(D.N_PROMPTS)), 1
    ):
        entries.append({
            "id": f"S{index:03d}", "seed": seed, "slot": slot,
            "prompt": "synthetic prompt", "output": "synthetic output",
            "tokens": [50, 51],
            "eos": False, "utf8_valid": True, "role_leak": False,
        })
    sample = {
        "schema": D.SCHEMA, "seeds": list(D.SEEDS),
        "decoder": "TOPP", "max_new": D.MAX_NEW, "entries": entries,
    }
    sample["digest"] = D.sha(sample)
    return sample


class HumanReviewTests(unittest.TestCase):
    def test_sample_protocol_and_digest(self):
        sample = synthetic_samples()
        self.assertEqual(len(D.check_samples(sample)), 24)
        sample["entries"][0]["output"] = "tampered"
        with self.assertRaises(RuntimeError):
            D.check_samples(sample)

    def test_manual_grades_and_n_a(self):
        good = {
            "relevance": 2, "coherence": 1,
            "cognition": 3, "persona": 0, "human_confirmed": True,
        }
        self.assertTrue(D.check_rating(good))
        self.assertFalse(D.check_rating({**good, "relevance": 3}))
        self.assertFalse(D.check_rating({**good, "human_confirmed": False}))
        self.assertFalse(D.check_rating({**good, "unexpected": 1}))

    def test_distribution_excludes_nonapplicable(self):
        entries = [
            {"relevance": 0, "cognition": 3},
            {"relevance": 2, "cognition": 2},
            {"relevance": 1, "cognition": 1},
        ]
        counts, average = A.distribution(entries, "relevance")
        self.assertEqual((counts[0], counts[1], counts[2]), (1, 1, 1))
        self.assertEqual(average, 100)
        counts, average = A.distribution(entries, "cognition")
        self.assertEqual(counts[3], 1)
        self.assertEqual(average, 150)

    def test_atomic_private_saves_and_backs_up(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "private"
            target = root / "ratings-private.json"
            with patch.object(D, "PRIVATE", root):
                D.atomic_private(target, {"version": 1})
                self.assertEqual(target.stat().st_mode & 0o777, 0o600)
                D.atomic_private(target, {"version": 2})
                backups = list((root / "backups").glob("*.bak"))
                self.assertEqual(len(backups), 1)
                self.assertEqual(backups[0].stat().st_mode & 0o777, 0o600)
                self.assertEqual(D.read_json(target)["version"], 2)

    def test_reviews_are_keyed_to_exact_samples(self):
        sample = synthetic_samples()
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "ratings-private.json"
            os.chmod(temporary, 0o700)
            target.write_text(
                '{"schema":"'+D.SCHEMA+'","samples_digest":"bad","ratings":{}}',
                encoding="utf-8",
            )
            os.chmod(target, 0o600)
            with patch.object(D, "REVIEWS", target):
                with self.assertRaises(RuntimeError):
                    D.load_review_state(sample)


if __name__ == "__main__":
    unittest.main()
