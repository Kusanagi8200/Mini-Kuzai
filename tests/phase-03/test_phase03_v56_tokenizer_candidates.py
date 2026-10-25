import importlib.util
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

TOKENIZER_PATH = (
    REPO
    / "mini_kuzai"
    / "tokenizer_v56.py"
)

SPEC = importlib.util.spec_from_file_location(
    "mini_kuzai_tokenizer_v56_test",
    TOKENIZER_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        "Unable to load tokenizer_v56.py"
    )

TOKENIZER = importlib.util.module_from_spec(SPEC)

sys.modules[SPEC.name] = TOKENIZER

SPEC.loader.exec_module(TOKENIZER)

BASE_VOCAB_SIZE = TOKENIZER.BASE_VOCAB_SIZE
CANDIDATE_NAMES = TOKENIZER.CANDIDATE_NAMES
ByteBPETokenizer = TOKENIZER.ByteBPETokenizer
ByteTokenizer = TOKENIZER.ByteTokenizer
build_candidate = TOKENIZER.build_candidate


FIXTURE = [
    "Mini-Kuzai is curious.",
    "Mini-Kuzai is curious!",
    "I do not know yet.",
    "I can form a tentative hypothesis.",
    "Better evidence should change my mind.",
    "hello world",
    "hello Mini-Kuzai",
    "café déjà vu",
    "Grenoble -> Linux -> CUDA",
    "print('hello')",
    "emoji: 🤖🧠",
    "line one\nline two",
] * 8


ROUNDTRIP_CASES = [
    "",
    "hello",
    "Mini-Kuzai",
    "spaces   remain",
    "line one\nline two",
    "café déjà vu",
    "naïve façade",
    "日本語",
    "🤖🧠",
    "x = (a+b) / 2;",
    "\tindent\nnext",
]


class V56TokenizerCandidateTests(
    unittest.TestCase
):

    def test_candidate_registry(self):
        self.assertEqual(
            CANDIDATE_NAMES,
            (
                "byte_baseline",
                "byte_bpe_whitespace",
                "byte_bpe_unicode",
            ),
        )

    def test_byte_baseline_vocab(self):
        tokenizer = ByteTokenizer()

        self.assertEqual(
            tokenizer.vocab_size,
            BASE_VOCAB_SIZE,
        )

        self.assertEqual(
            BASE_VOCAB_SIZE,
            259,
        )

    def test_byte_baseline_is_lossless(self):
        tokenizer = ByteTokenizer()

        for text in ROUNDTRIP_CASES:
            self.assertEqual(
                tokenizer.decode(
                    tokenizer.encode(text)
                ),
                text,
            )

    def _train(self, name):
        return build_candidate(
            name,
            texts=FIXTURE,
            target_vocab_size=300,
            min_pair_frequency=2,
        )

    def test_whitespace_bpe_is_lossless(self):
        tokenizer = self._train(
            "byte_bpe_whitespace"
        )

        for text in ROUNDTRIP_CASES:
            self.assertEqual(
                tokenizer.decode(
                    tokenizer.encode(text)
                ),
                text,
            )

    def test_unicode_bpe_is_lossless(self):
        tokenizer = self._train(
            "byte_bpe_unicode"
        )

        for text in ROUNDTRIP_CASES:
            self.assertEqual(
                tokenizer.decode(
                    tokenizer.encode(text)
                ),
                text,
            )

    def test_bpe_training_is_deterministic(self):
        for name in (
            "byte_bpe_whitespace",
            "byte_bpe_unicode",
        ):
            first = self._train(name)
            second = self._train(name)

            self.assertEqual(
                first.to_dict(),
                second.to_dict(),
            )

            self.assertEqual(
                first.fingerprint(),
                second.fingerprint(),
            )

    def test_bpe_serialization_roundtrip(self):
        for name in (
            "byte_bpe_whitespace",
            "byte_bpe_unicode",
        ):
            tokenizer = self._train(name)

            restored = (
                ByteBPETokenizer.from_dict(
                    tokenizer.to_dict()
                )
            )

            self.assertEqual(
                tokenizer.to_dict(),
                restored.to_dict(),
            )

            for text in ROUNDTRIP_CASES:
                self.assertEqual(
                    restored.decode(
                        restored.encode(text)
                    ),
                    text,
                )

    def test_vocab_target_is_upper_bound(self):
        for name in (
            "byte_bpe_whitespace",
            "byte_bpe_unicode",
        ):
            tokenizer = self._train(name)

            self.assertGreaterEqual(
                tokenizer.vocab_size,
                BASE_VOCAB_SIZE,
            )

            self.assertLessEqual(
                tokenizer.vocab_size,
                300,
            )

    def test_bpe_has_byte_fallback(self):
        for name in (
            "byte_bpe_whitespace",
            "byte_bpe_unicode",
        ):
            tokenizer = self._train(name)

            self.assertTrue(
                tokenizer.byte_fallback
            )

            self.assertEqual(
                tokenizer.external_dependencies,
                0,
            )


if __name__ == "__main__":
    unittest.main()
