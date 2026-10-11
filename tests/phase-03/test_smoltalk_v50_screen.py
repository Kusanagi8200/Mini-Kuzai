"""Offline unit tests for V50 public-source screening heuristics.

No server datasets, private conversations, network, or GPU required.
"""
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "tools/public-audits/smoltalk_v50_cognitive_screen.py"
)
SPEC = importlib.util.spec_from_file_location("smoltalk_v50", MODULE_PATH)
v50 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v50)


class V50ScreenTests(unittest.TestCase):
    @staticmethod
    def dialogue(*texts):
        return [
            {"role": "user" if i % 2 == 0 else "assistant", "content": t}
            for i, t in enumerate(texts)
        ]

    def test_creative_context_is_prioritized(self):
        messages = self.dialogue(
            "Help me develop a fictional character.",
            "The character is exploring a deserted city.",
            "Continue this character's story, but change her motivation.",
            "She revises her goal."
        )
        flags = v50.signals(messages, "GENERAL_OTHER")
        self.assertEqual(flags["priority_hint"], "HIGH")
        self.assertTrue(flags["creative_keyword_signal"])
        self.assertTrue(flags["followup_wording_signal"])
        self.assertTrue(flags["user_feedback_wording_signal"])

    def test_reasoning_and_feedback_are_prioritized(self):
        messages = self.dialogue(
            "Compare two possible explanations for this event.",
            "The first interpretation focuses on weather.",
            "I disagree. Can you revise your response?",
            "Here are two different possibilities."
        )
        flags = v50.signals(messages, "FOLLOWUP")
        self.assertEqual(flags["priority_hint"], "HIGH")
        self.assertTrue(flags["cognitive_keyword_signal"])
        self.assertTrue(flags["user_feedback_wording_signal"])

    def test_single_turn_story_is_not_automatically_rejected(self):
        messages = self.dialogue(
            "Write a fantasy story about a lost map.",
            "A cartographer finds the map."
        )
        flags = v50.signals(messages, "GENERAL_OTHER")
        self.assertEqual(flags["priority_hint"], "MEDIUM")
        self.assertTrue(flags["creative_keyword_signal"])

    def test_technical_only_example_is_low_priority_not_rejection(self):
        messages = self.dialogue(
            "Write a Python function that returns 42.",
            "def f(): return 42"
        )
        flags = v50.signals(messages, "PROGRAMMING")
        self.assertEqual(flags["priority_hint"], "LOW")
        self.assertTrue(flags["technical_domain_signal"])
        self.assertNotIn("review_state", flags)

    def test_simple_question_does_not_claim_semantic_quality(self):
        flags = v50.signals(
            self.dialogue("What is 2 plus 2?", "4"), "MATHEMATICS"
        )
        self.assertEqual(flags["priority_hint"], "LOW")
        self.assertFalse(flags["creative_keyword_signal"])
        self.assertFalse(flags["cognitive_keyword_signal"])

    def test_dialogue_shape_validation(self):
        self.assertTrue(v50.valid_messages(self.dialogue("Q", "A", "Q2", "A2")))
        self.assertFalse(v50.valid_messages([{"role": "assistant", "content": "A"}]))
        self.assertFalse(v50.valid_messages(self.dialogue("Q", "   ")))
        self.assertFalse(v50.valid_messages(self.dialogue("Q", "A", "Q2")))


if __name__ == "__main__":
    unittest.main()
