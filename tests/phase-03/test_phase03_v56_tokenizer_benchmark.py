import importlib.util
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

PATH = (
    REPO
    / "tools"
    / "phase03_v56_tokenizer_benchmark.py"
)

SPEC = importlib.util.spec_from_file_location(
    "phase03_v56_tokenizer_benchmark_test",
    PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        "Unable to load V56 benchmark module"
    )

MODULE = importlib.util.module_from_spec(
    SPEC
)

sys.modules[SPEC.name] = MODULE

SPEC.loader.exec_module(MODULE)


class V56TokenizerBenchmarkTests(
    unittest.TestCase
):

    def test_targets(self):
        self.assertEqual(
            MODULE.TARGETS,
            (
                512,
                1024,
                2048,
            ),
        )

    def test_learning_scope(self):
        self.assertEqual(
            len(MODULE.TRAIN_NAMES),
            19,
        )

        self.assertEqual(
            MODULE.EXPECTED_SMOLTALK_SOURCES,
            {
                "smol-magpie-ultra-short":
                    5000,
                "openhermes-50k":
                    1500,
                "self-oss-instruct":
                    1000,
                "explore-instruct-rewrite":
                    500,
            },
        )

    def test_fast_engine_matches_reference(self):
        MODULE.self_test()


if __name__ == "__main__":
    unittest.main()
