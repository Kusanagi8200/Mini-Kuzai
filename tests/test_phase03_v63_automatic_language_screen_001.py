"""CPU-only V63 linguistic proxy screening tests; no private sample files."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO))
FILE=REPO/"tools"/"public-audits"/"phase03_v63_automatic_language_screen_001.py"
spec=importlib.util.spec_from_file_location("v63_auto_screen",FILE)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot load V63 automatic screen")
A=importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


class AutoLanguageScreenTests(unittest.TestCase):
    def test_word_case_normalization(self):
        self.assertEqual(A.word_tokens("Hello, MINI-KUZAI! I can't"),
                         ["hello","mini","kuzai","i","can't"])

    def test_ngram_recurrence(self):
        self.assertEqual(A.gram_repetition_bp([11,12,13,11,12,13],3),2500)
        self.assertEqual(A.gram_repetition_bp([11,12,13],8),0)

    def test_detect_unknown_word_fragments(self):
        words={"the","and","hello","world"}
        item=A.analyze_text(
            "the foobarbazz knsxy blorpy aee zopqq lorem", words
        )
        self.assertEqual(item["words"],7)
        self.assertEqual(item["known"],1)
        self.assertEqual(item["suspect"],1)

    def test_normal_sentence_not_suspect(self):
        words={"the","quick","brown","fox","jumps","over","a","dog"}
        result=A.analyze_text("The quick brown fox jumps over a dog.",words)
        self.assertEqual(result["suspect"],0)
        self.assertEqual(result["known"],8)

    def test_numeric_aggregate_and_no_human_scores(self):
        samples=[
            {
                "output":"The quick brown fox jumps over a dog.",
                "prompt":"What does the fox do?",
                "eos":True,
                "utf8_valid":True,
                "role_leak":False,
                "tokens":[11,12,13,14,15,16,A.T.EOS_ID],
            }
            for _ in range(24)
        ]
        result=A.compute(samples,{"the","quick","brown","fox","jumps","over","a","dog"})
        self.assertEqual(len(result),25)
        self.assertEqual(result["AUTO_SAMPLES"],24)
        self.assertEqual(result["AUTO_EOS"],24)
        self.assertEqual(result["AUTO_HUMAN_RATINGS"],0)
        self.assertEqual(result["AUTO_SUSPECT_OUTPUTS"],0)
        self.assertTrue(all(type(v) is int and v>=0 for v in result.values()))

    def test_no_recognizable_words_is_reported_not_hidden(self):
        samples=[
            {
                "output":"???", "prompt":"What?",
                "eos":True, "utf8_valid":True, "role_leak":False,
                "tokens":[11,12,A.T.EOS_ID],
            }
            for _ in range(24)
        ]
        result=A.compute(samples,{"the","hello"})
        self.assertEqual(result["AUTO_WORDS"],0)
        self.assertEqual(result["AUTO_ZERO_WORD_OUTPUTS"],24)
        self.assertEqual(result["AUTO_SUSPECT_OUTPUTS"],24)
        self.assertEqual(result["AUTO_REF_WORD_COVER_BP"],0)

    def test_review_is_not_a_semantic_classifier(self):
        result=A.analyze_text("The quick brown fox jumps over a dog.",
                              {"the","quick","brown","fox","jumps","over","a","dog"})
        self.assertNotIn("semantic_score",result)
        self.assertNotIn("persona_score",result)


if __name__=="__main__":
    unittest.main()
