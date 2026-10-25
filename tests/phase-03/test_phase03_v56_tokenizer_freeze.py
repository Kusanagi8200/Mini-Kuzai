import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

TOKENIZER_PATH = (
    REPO
    / "mini_kuzai"
    / "tokenizer_v56.py"
)

FINAL_PATH = (
    REPO
    / "data/phase-03/tokenizers"
    / "tokenizer-v56-final.json"
)

MANIFEST_PATH = (
    REPO
    / "data/phase-03/manifests"
    / "tokenizer-v56-final.json"
)

SELECTION_PATH = (
    REPO
    / "data/phase-03/reports"
    / "tokenizer-selection-v56.json"
)

SPEC = importlib.util.spec_from_file_location(
    "mini_kuzai_tokenizer_v56_freeze_test",
    TOKENIZER_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        "Unable to load tokenizer_v56.py"
    )

TOK = importlib.util.module_from_spec(SPEC)

sys.modules[SPEC.name] = TOK

SPEC.loader.exec_module(TOK)


class V56TokenizerFreezeTests(
    unittest.TestCase
):

    def setUp(self):
        self.manifest = json.loads(
            MANIFEST_PATH.read_text(
                encoding="utf-8"
            )
        )

        self.selection = json.loads(
            SELECTION_PATH.read_text(
                encoding="utf-8"
            )
        )

        self.value = json.loads(
            FINAL_PATH.read_text(
                encoding="utf-8"
            )
        )

        self.tokenizer = (
            TOK.ByteBPETokenizer.from_dict(
                self.value
            )
        )

    def test_final_identity(self):
        self.assertEqual(
            self.tokenizer.family,
            "byte_bpe_whitespace",
        )

        self.assertEqual(
            self.tokenizer.vocab_size,
            1024,
        )

        self.assertEqual(
            len(self.tokenizer.merges),
            765,
        )

    def test_fingerprint(self):
        expected = (
            "62216744c1493d3bd5558120570e0178d"
            "6adb94c40311e0639dde245cfab4ee9"
        )

        self.assertEqual(
            self.tokenizer.fingerprint(),
            expected,
        )

        self.assertEqual(
            self.manifest[
                "fingerprint"
            ],
            expected,
        )

    def test_file_sha256(self):
        actual = hashlib.sha256(
            FINAL_PATH.read_bytes()
        ).hexdigest()

        self.assertEqual(
            actual,
            self.manifest[
                "tokenizer_sha256"
            ],
        )

    def test_freeze_state(self):
        self.assertEqual(
            self.manifest["status"],
            "FROZEN",
        )

        self.assertTrue(
            self.manifest[
                "tokenizer_finalized"
            ]
        )

        self.assertTrue(
            self.manifest[
                "vocabulary_frozen"
            ]
        )

        self.assertFalse(
            self.manifest[
                "training_authorized"
            ]
        )

    def test_scope_exclusions(self):
        self.assertFalse(
            self.manifest[
                "validation_included"
            ]
        )

        self.assertFalse(
            self.manifest[
                "blind_included"
            ]
        )

        self.assertFalse(
            self.manifest[
                "private_included"
            ]
        )

    def test_selection_evidence(self):
        self.assertEqual(
            self.selection[
                "selection"
            ]["config"],
            "byte_bpe_whitespace_1024",
        )

        self.assertEqual(
            self.selection[
                "benchmark_evidence"
            ][
                "selected_compression_bp"
            ],
            4883,
        )

        self.assertEqual(
            self.selection[
                "benchmark_evidence"
            ]["selected_p95"],
            887,
        )

    def test_roundtrip(self):
        for text in (
            "",
            "Mini-Kuzai",
            "café déjà vu",
            "日本語",
            "🤖🧠",
            "line one\nline two",
        ):
            self.assertEqual(
                self.tokenizer.decode(
                    self.tokenizer.encode(
                        text
                    )
                ),
                text,
            )


if __name__ == "__main__":
    unittest.main()
