"""Offline tests for public SmolTalk V51 publisher, with synthetic dialogues only."""
import importlib.util
import unittest
from collections import Counter
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "tools/publish_smoltalk_v51_github_reviews.py"
SPEC = importlib.util.spec_from_file_location("v51_publisher", SOURCE)
v51 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v51)


def record(n, priority, category="CREATIVE", source="openhermes-50k"):
    return {
        "source_content_sha256": format(n, "064x"),
        "priority_hint": priority,
        "v44_heuristic_category": category,
        "source_dataset": source,
        "messages": [
            {"role": "user", "content": "Invent <an> imagined character."},
            {"role": "assistant", "content": "The character is <curious>."},
        ],
    }


class V51PublisherTests(unittest.TestCase):
    def sample(self):
        records = []
        for priority, count in (("HIGH", 30), ("MEDIUM", 20), ("LOW", 20)):
            for n in range(count):
                source = list(v51.SOURCE_COUNTS)[n % 4]
                category = ("CREATIVE", "WRITING", "GENERAL_OTHER")[n % 3]
                records.append(record(
                    {"HIGH": 1000, "MEDIUM": 2000, "LOW": 3000}[priority] + n,
                    priority, category, source
                ))
        return records

    def test_balanced_batch_has_24_distinct_candidates(self):
        sample = v51.select_batch(self.sample())
        self.assertEqual(len(sample), 24)
        self.assertEqual(len({r["source_content_sha256"] for r in sample}), 24)
        self.assertEqual(Counter(r["priority_hint"] for r in sample), v51.QUOTAS)

    def test_selection_is_order_independent(self):
        candidates = self.sample()
        a = [r["source_content_sha256"] for r in v51.select_batch(candidates)]
        b = [r["source_content_sha256"] for r in v51.select_batch(list(reversed(candidates)))]
        self.assertEqual(a, b)

    def test_insufficient_priority_is_rejected(self):
        with self.assertRaises(RuntimeError):
            v51.select_batch([record(1, "HIGH")])

    def test_page_is_unreviewed_and_escapes_public_dialogue(self):
        page = v51.case_page(1, record(1000, "HIGH"))
        self.assertIn("V51 grade: PENDING", page)
        self.assertIn("V51 rationale: NOT_REVIEWED", page)
        self.assertIn("V51 cognition: UNREVIEWED", page)
        self.assertIn("&lt;an&gt;", page)
        self.assertNotIn("Invent <an>", page)
        self.assertIn("Public content SHA-256:", page)
        self.assertIn("TRAIN", page)

    def test_all_review_fields_have_single_occurrence(self):
        page = v51.case_page(3, record(10, "LOW"))
        for field in (
            "grade", "rationale", "cognition", "creativity", "continuity",
            "correction", "communication", "factual risk", "instruction fit"
        ):
            self.assertEqual(page.count("V51 " + field + ":"), 1)


if __name__ == "__main__":
    unittest.main()
