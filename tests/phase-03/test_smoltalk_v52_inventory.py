"""Offline tests for V52 public numeric-only inventory and gogit allowlist."""
import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


audit = load(REPO / "tools/public-audits/smoltalk_v52_inventory.py", "v52_inventory")
gogit = load(REPO / "tools/gogit_public.py", "v52_gogit")


class V52InventoryTests(unittest.TestCase):
    @staticmethod
    def row(sha, priority, source, turns):
        return {
            "source_content_sha256": sha,
            "priority_hint": priority,
            "source_dataset": source,
            "messages": [
                {"role": "user" if i % 2 == 0 else "assistant", "content": "sample"}
                for i in range(turns)
            ],
        }

    def test_numeric_metrics_match_gogit_allowlist(self):
        rows = [
            self.row("a" * 64, "HIGH", "smol-magpie-ultra-short", 6),
            self.row("b" * 64, "MEDIUM", "openhermes-50k", 2),
            self.row("c" * 64, "LOW", "self-oss-instruct", 4),
        ]
        metrics = audit.inventory_metrics(rows, 2, 1, population=6)
        self.assertEqual(len(metrics), 30)
        self.assertEqual(set(metrics).difference(gogit.METRIC_KEYS), set())
        self.assertEqual(metrics["V52_AVAILABLE"], 3)
        self.assertEqual(metrics["V52_MULTITURN"], 2)
        self.assertEqual(metrics["V52_HIGH_SMOL_TOTAL"], 1)
        self.assertEqual(metrics["V52_HIGH_SMOL_MULTITURN"], 1)
        self.assertEqual(metrics["V52_MEDIUM_HERMES_MULTITURN"], 0)
        self.assertEqual(metrics["V52_LOW_OSS_MULTITURN"], 1)
        self.assertEqual(metrics["V52_TRAIN_APPROVED"], 0)

    def test_numeric_parser_accepts_v52_schema(self):
        rows = [self.row("a" * 64, "HIGH", "smol-magpie-ultra-short", 2)]
        metrics = audit.inventory_metrics(rows, 0, 0, population=1)
        raw = audit.MARKER + "\n" + "".join(
            f"{name}: {value}\n" for name, value in metrics.items()
        )
        self.assertEqual(gogit.numeric_metrics(raw), metrics)

    def test_v48_review_has_24_rescues_outside_v44(self):
        import re
        index = (REPO / "reviews/smoltalk-v48/README.md").read_text(
            encoding="utf-8"
        )
        reasons = re.findall(
            r"(?m)^\\|\\s*\\d+\\s*\\|\\s*(RELABEL|RESCUE|BASE)\\s*\\|",
            index,
        )
        self.assertEqual(len(reasons), 68)
        self.assertEqual(reasons.count("RELABEL"), 12)
        self.assertEqual(reasons.count("BASE"), 32)
        self.assertEqual(reasons.count("RESCUE"), 24)
        # In-V44 exclusions = BASE + RELABEL, never RESCUE.
        self.assertEqual(reasons.count("BASE") + reasons.count("RELABEL"), 44)

    def test_duplicate_source_is_rejected(self):
        row = self.row("a" * 64, "HIGH", "smol-magpie-ultra-short", 2)
        with self.assertRaises(RuntimeError):
            audit.inventory_metrics([row, row], 0, 0, population=2)

    def test_population_mismatch_is_rejected(self):
        with self.assertRaises(RuntimeError):
            audit.inventory_metrics([], 0, 0, population=1)

    def test_unexpected_source_and_priority_are_rejected(self):
        row = self.row("a" * 64, "UNKNOWN", "smol-magpie-ultra-short", 2)
        with self.assertRaises(RuntimeError):
            audit.inventory_metrics([row], 0, 0, population=1)
        row["priority_hint"] = "HIGH"
        row["source_dataset"] = "PRIVATE_SOURCE"
        with self.assertRaises(RuntimeError):
            audit.inventory_metrics([row], 0, 0, population=1)


if __name__ == "__main__":
    unittest.main()
