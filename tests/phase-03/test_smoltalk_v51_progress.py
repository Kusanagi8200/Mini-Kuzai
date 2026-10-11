"""Offline syntax and review-field validation for public V51 progress audit."""
import importlib.util
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[2] / "tools/public-audits/smoltalk_v51_github_progress.py"
spec = importlib.util.spec_from_file_location("v51_progress", AUDIT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class V51ProgressTests(unittest.TestCase):
    def reviewed(self):
        fields = dict(audit.FIELDS)
        fields.update({
            "V51 grade": "B",
            "V51 rationale": "Creative value despite incomplete instruction compliance.",
            "V51 cognition": "2",
            "V51 creativity": "3",
            "V51 continuity": "1",
            "V51 correction": "0",
            "V51 communication": "2",
            "V51 factual risk": "REVIEW",
            "V51 instruction fit": "PARTIAL",
        })
        return fields

    def test_pending_defaults_are_valid(self):
        self.assertEqual(audit.validate(dict(audit.FIELDS)), "PENDING")

    def test_complete_review_is_valid(self):
        self.assertEqual(audit.validate(self.reviewed()), "B")

    def test_pending_partial_edit_is_invalid(self):
        fields = dict(audit.FIELDS)
        fields["V51 cognition"] = "2"
        with self.assertRaises(RuntimeError):
            audit.validate(fields)

    def test_grade_requires_substantive_rationale(self):
        fields = self.reviewed()
        fields["V51 rationale"] = "wrong"
        with self.assertRaises(RuntimeError):
            audit.validate(fields)

    def test_scores_must_be_0_to_3(self):
        fields = self.reviewed()
        fields["V51 creativity"] = "8"
        with self.assertRaises(RuntimeError):
            audit.validate(fields)

    def test_immutable_body_is_detectable(self):
        original = "\n".join(f"{key}: {val}" for key, val in audit.FIELDS.items())
        original += "\n\nPublic source content: untouched\n"
        changed = original.replace("V51 grade: PENDING", "V51 grade: A")
        fields, normalized = audit.extract_and_normalize(changed)
        self.assertEqual(fields["V51 grade"], "A")
        self.assertEqual(normalized, original)
        amended = changed.replace("untouched", "altered")
        _, normalized_bad = audit.extract_and_normalize(amended)
        self.assertNotEqual(normalized_bad, original)


if __name__ == "__main__":
    unittest.main()
