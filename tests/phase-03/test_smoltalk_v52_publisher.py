"""Offline synthetic-data tests for V52 public review publisher and GOGIT."""
import importlib.util
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


publisher = load(
    REPO / "tools/publish_smoltalk_v52_github_reviews.py", "v52_test_publisher"
)
v51 = load(REPO / "tools/publish_smoltalk_v51_github_reviews.py", "v52_test_v51")
progress = load(
    REPO / "tools/public-audits/smoltalk_v52_github_progress.py",
    "v52_test_progress",
)
gogit = load(REPO / "tools/gogit_public.py", "v52_test_gogit")
v51_progress = load(
    REPO / "tools/public-audits/smoltalk_v51_github_progress.py",
    "v52_test_v51_progress",
)


def example(number, priority, source, category="CREATIVE", turns=2):
    return {
        "source_content_sha256": format(number, "064x"),
        "priority_hint": priority,
        "source_dataset": source,
        "v44_heuristic_category": category,
        "messages": [
            {
                "role": "user" if i % 2 == 0 else "assistant",
                "content": "Invent <a> character and expand its world.",
            }
            for i in range(turns)
        ],
    }


class V52PublisherTests(unittest.TestCase):
    @staticmethod
    def candidates():
        rows = []
        for group_no, ((priority, source), quota) in enumerate(
            publisher.QUOTAS.items(), 1
        ):
            for i in range(quota + 3):
                rows.append(example(
                    group_no * 100 + i,
                    priority,
                    source,
                    category=("CREATIVE", "FOLLOWUP", "WRITING", "GENERAL_OTHER")[
                        i % 4
                    ],
                    turns=6 if source == "smol-magpie-ultra-short" else 2,
                ))
        return rows

    def test_stratification_and_unique_candidates(self):
        selected = publisher.select_batch(self.candidates())
        self.assertEqual(len(selected), 32)
        self.assertEqual(
            len({r["source_content_sha256"] for r in selected}), 32
        )
        self.assertEqual(
            Counter((r["priority_hint"], r["source_dataset"])
                    for r in selected),
            publisher.QUOTAS,
        )
        self.assertEqual(
            sum(len(r["messages"]) > 2 for r in selected), 20
        )

    def test_selection_order_independent(self):
        records = self.candidates()
        forward = [r["source_content_sha256"]
                   for r in publisher.select_batch(records)]
        backward = [r["source_content_sha256"]
                    for r in publisher.select_batch(list(reversed(records)))]
        self.assertEqual(forward, backward)

    def test_exhausted_stratum_fails_closed(self):
        records = self.candidates()
        records = [
            row for row in records
            if not (row["priority_hint"] == "MEDIUM"
                    and row["source_dataset"] == "self-oss-instruct")
        ]
        with self.assertRaises(RuntimeError):
            publisher.select_batch(records)

    def test_public_page_escapes_source_and_starts_pending(self):
        page = publisher.case_page(
            1, example(1, "LOW", "openhermes-50k"), v51
        )
        for name, default in publisher.RUBRIC_DEFAULTS.items():
            self.assertEqual(page.count(name + ": " + default), 1)
        self.assertIn("&lt;a&gt;", page)
        self.assertNotIn("Invent <a>", page)
        self.assertIn("V52 grade: PENDING", page)
        self.assertIn("No independent human validation", page)

    def test_normalization_preserves_source_and_detects_edits(self):
        row = example(1, "LOW", "openhermes-50k")
        original = publisher.case_page(1, row, v51)
        edited = original.replace("V52 grade: PENDING", "V52 grade: A")
        fields, normalized = progress.extract_and_normalize(
            edited, publisher.RUBRIC_DEFAULTS
        )
        self.assertEqual(fields["V52 grade"], "A")
        self.assertEqual(normalized, original)
        _, tampered = progress.extract_and_normalize(
            edited.replace("&lt;a&gt;", "&lt;b&gt;"),
            publisher.RUBRIC_DEFAULTS,
        )
        self.assertNotEqual(tampered, original)

    def test_shared_grade_validator_rejects_partial_review(self):
        fields = dict(publisher.RUBRIC_DEFAULTS)
        self.assertEqual(progress.grade_review(fields, v51_progress), "PENDING")
        fields["V52 cognition"] = "2"
        with self.assertRaises(RuntimeError):
            progress.grade_review(fields, v51_progress)

    def test_public_numeric_allowlist_exact(self):
        rows = publisher.select_batch(self.candidates())
        totals = Counter((r["priority_hint"], r["source_dataset"]) for r in rows)
        for (priority, source), required in publisher.QUOTAS.items():
            self.assertEqual(totals[(priority, source)], required)
        keys = {
            "V52_PUBLIC_" + name
            for name in (
                "QUEUE_TOTAL", "PENDING", "REVIEWED", "A", "B", "C", "HELD",
                "HIGH", "MEDIUM", "LOW", "SMOL", "HERMES", "OSS", "REWRITE",
                "MULTITURN", "TRAIN_APPROVED",
            )
        }
        self.assertEqual(len(keys), 16)
        self.assertTrue(keys <= gogit.METRIC_KEYS)
        fake = {key: 0 for key in keys}
        fake["V52_PUBLIC_QUEUE_TOTAL"] = 32
        fake["V52_PUBLIC_PENDING"] = 32
        raw = progress.MARKER + "\n" + "".join(
            f"{name}: {value}\n" for name, value in sorted(fake.items())
        )
        self.assertEqual(gogit.numeric_metrics(raw), dict(sorted(fake.items())))


if __name__ == "__main__":
    unittest.main()
