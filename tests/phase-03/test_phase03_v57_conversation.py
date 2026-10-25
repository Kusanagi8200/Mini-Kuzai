import importlib.util
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]

PATH = (
    REPO
    / "mini_kuzai"
    / "phase03_conversation.py"
)

SPEC = importlib.util.spec_from_file_location(
    "phase03_conversation_test",
    PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        "Unable to load Phase 03 conversation serializer"
    )

MODULE = importlib.util.module_from_spec(
    SPEC
)

sys.modules[SPEC.name] = MODULE

SPEC.loader.exec_module(MODULE)


class Phase03ConversationTests(
    unittest.TestCase
):

    def test_single_turn_exact(self):
        messages = [
            {
                "role": "user",
                "content": "Hello",
            },
            {
                "role": "assistant",
                "content": "Hi.",
            },
        ]

        self.assertEqual(
            MODULE.serialize_messages(
                messages
            ),
            "USER:\nHello\n\nMINI-KUZAI:\nHi.",
        )

    def test_multiturn_exact(self):
        messages = [
            {
                "role": "user",
                "content": "A",
            },
            {
                "role": "assistant",
                "content": "B",
            },
            {
                "role": "user",
                "content": "C",
            },
            {
                "role": "assistant",
                "content": "D",
            },
        ]

        self.assertEqual(
            MODULE.serialize_messages(
                messages
            ),
            (
                "USER:\nA\n\n"
                "MINI-KUZAI:\nB\n\n"
                "USER:\nC\n\n"
                "MINI-KUZAI:\nD"
            ),
        )

    def test_inference_prompt(self):
        self.assertEqual(
            MODULE.serialize_user_prompt(
                "Hello"
            ),
            (
                "USER:\nHello\n\n"
                "MINI-KUZAI:\n"
            ),
        )

    def test_invalid_roles_rejected(self):
        with self.assertRaises(
            ValueError
        ):
            MODULE.serialize_messages(
                [
                    {
                        "role": "assistant",
                        "content": "No",
                    },
                    {
                        "role": "user",
                        "content": "No",
                    },
                ]
            )


if __name__ == "__main__":
    unittest.main()
