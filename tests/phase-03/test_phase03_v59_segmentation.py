import importlib.util
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

SEG_PATH = (
    REPO
    / "mini_kuzai"
    / "phase03_segmentation.py"
)

CONV_PATH = (
    REPO
    / "mini_kuzai"
    / "phase03_conversation.py"
)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load {path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


SEG = load_module(
    "phase03_segmentation_test",
    SEG_PATH,
)

CONV = load_module(
    "phase03_conversation_v59_test",
    CONV_PATH,
)


def count_chars(text):
    return len(text)


def pair(user, assistant):
    return [
        {
            "role": "user",
            "content": user,
        },
        {
            "role": "assistant",
            "content": assistant,
        },
    ]


class Phase03SegmentationTests(
    unittest.TestCase
):

    def segment(
        self,
        messages,
        context,
    ):
        return SEG.segment_messages(
            messages,
            serialize_messages=CONV.serialize_messages,
            validate_messages=CONV.validate_messages,
            count_text=count_chars,
            context_length=context,
        )

    def test_single_segment_preserves_messages(self):
        messages = pair(
            "hello",
            "hello back",
        )

        segments = self.segment(
            messages,
            100,
        )

        self.assertEqual(
            len(segments),
            1,
        )

        self.assertEqual(
            list(segments[0].messages),
            messages,
        )

    def test_split_occurs_only_between_pairs(self):
        first = pair(
            "a",
            "b",
        )

        second = pair(
            "c",
            "d",
        )

        messages = first + second

        one_pair_tokens = (
            len(
                CONV.serialize_messages(
                    first
                )
            )
            + 2
        )

        segments = self.segment(
            messages,
            one_pair_tokens,
        )

        self.assertEqual(
            len(segments),
            2,
        )

        self.assertEqual(
            list(segments[0].messages),
            first,
        )

        self.assertEqual(
            list(segments[1].messages),
            second,
        )

    def test_no_message_loss_or_reordering(self):
        messages = (
            pair("u1", "a1")
            + pair("u2", "a2")
            + pair("u3", "a3")
        )

        segments = self.segment(
            messages,
            40,
        )

        flattened = [
            message
            for segment in segments
            for message in segment.messages
        ]

        self.assertEqual(
            flattened,
            messages,
        )

    def test_oversized_pair_is_blocked(self):
        messages = pair(
            "x" * 100,
            "y" * 100,
        )

        with self.assertRaises(
            SEG.OversizedPairError
        ):
            self.segment(
                messages,
                50,
            )

    def test_pair_count_matches_pairs(self):
        messages = (
            pair("one", "two")
            + pair("three", "four")
        )

        counts = SEG.pair_token_counts(
            messages,
            serialize_messages=CONV.serialize_messages,
            validate_messages=CONV.validate_messages,
            count_text=count_chars,
        )

        self.assertEqual(
            len(counts),
            2,
        )

        self.assertTrue(
            all(value > 2 for value in counts)
        )


if __name__ == "__main__":
    unittest.main()
