import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


audit = load(
    REPO
    / "tools/public-audits"
    / "phase03_v56_tokenizer_scope.py",
    "phase03_v56_tokenizer_scope_test",
)

gogit = load(
    REPO / "tools/gogit_public.py",
    "phase03_v56_gogit_test",
)


class V56TokenizerScopeTests(unittest.TestCase):

    def test_canonical_train_file_set_is_explicit(self):
        self.assertEqual(
            len(audit.TRAIN_NAMES),
            19,
        )

        self.assertEqual(
            audit.TRAIN_NAMES[0],
            "train-pilot-v0.2.jsonl",
        )

        self.assertIn(
            "train-batch-b08-v0.5.jsonl",
            audit.TRAIN_NAMES,
        )

        self.assertIn(
            "train-batch-b12-v0.3.jsonl",
            audit.TRAIN_NAMES,
        )

    def test_external_reservoir_is_outside_repo(self):
        self.assertFalse(
            audit.SMOLTALK_POOL.resolve().is_relative_to(
                REPO.resolve()
            )
        )

    def test_v55_closure_is_required(self):
        audit.verify_v55_closure()

    def test_gogit_knows_v56_metrics(self):
        required = {
            "V56_TOKENIZER_SCOPE_TRAIN_MESSAGES",
            "V56_TOKENIZER_SCOPE_SMOLTALK_RECORDS",
            "V56_TOKENIZER_SCOPE_SMOLTALK_MESSAGES",
            "V56_TOKENIZER_SCOPE_SMOLTALK_SOURCES",
            "V56_TOKENIZER_SCOPE_VALIDATION_INCLUDED",
            "V56_TOKENIZER_SCOPE_BLIND_INCLUDED",
            "V56_TOKENIZER_SCOPE_PRIVATE_INCLUDED",
            "V56_TOKENIZER_FINALIZED",
        }

        self.assertTrue(
            required <= gogit.METRIC_KEYS
        )

    def test_gogit_v56_source_isolated(self):
        source = gogit.source_for_audit(
            "tools/public-audits/"
            "phase03_v56_tokenizer_scope.py"
        )

        self.assertEqual(
            source,
            gogit.SOURCE_PHASE03_TOKENIZER,
        )

    def test_gogit_v56_semantic_summary_is_true(self):
        metrics = {
            "SEMANTIC_VALIDATION_COMPLETE": 1,
            "TRAINING_AUTHORIZED": 0,
        }

        self.assertTrue(
            gogit.semantic_validation_complete_for_audit(
                "tools/public-audits/"
                "phase03_v56_tokenizer_scope.py",
                metrics,
            )
        )

    def test_gogit_v56_does_not_require_blind_authoring_metric(self):
        metrics = {
            "SEMANTIC_VALIDATION_COMPLETE": 1,
            "TRAINING_AUTHORIZED": 0,
        }

        self.assertNotIn(
            "BLIND_AUTHORING_AUTHORIZED",
            metrics,
        )

        self.assertTrue(
            gogit.semantic_validation_complete_for_audit(
                "tools/public-audits/"
                "phase03_v56_tokenizer_scope.py",
                metrics,
            )
        )

    def test_gogit_v56_training_authorization_must_remain_false(self):
        metrics = {
            "SEMANTIC_VALIDATION_COMPLETE": 1,
            "TRAINING_AUTHORIZED": 1,
        }

        self.assertFalse(
            gogit.semantic_validation_complete_for_audit(
                "tools/public-audits/"
                "phase03_v56_tokenizer_scope.py",
                metrics,
            )
        )


if __name__ == "__main__":
    unittest.main()
