"""Offline V74 dual-report FINAL preflight, no GitHub or LinkedIn writes."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import github_discussions_step as S
import v74_final_closure as V


def load():
    return (
        json.loads((ROOT / V.CORE).read_text(encoding="utf-8")),
        json.loads((ROOT / V.STRATA).read_text(encoding="utf-8")),
    )


class V74DualFinalTests(unittest.TestCase):
    def test_gogit_commits_are_exactly_pinned(self):
        V.verify_git_pins(ROOT)
        self.assertEqual(len(V.COMMITS), 2)

    def test_both_immutable_reports_validate(self):
        core, strata = load()
        m, n = V.validate_pair(core, strata)
        self.assertEqual(len(m), 30)
        self.assertEqual(len(n), 30)
        self.assertEqual(m["V74_CORE_PC1_CORRECT"], 2455)
        self.assertEqual(m["V74_CORE_UNIGRAM_CORRECT"], 2535)
        self.assertEqual(n["V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT"], 2449)

    def test_compact_linkedin_safe_comment_references_both(self):
        core, strata = load()
        body = V.closure_body(
            core, strata, header=S.header("V74", S.CLOSE_STATUS),
            footer=S.FOOTER,
        )
        self.assertLessEqual(len(body), V.MAX_GITHUB_BODY)
        # KUZ-DIN adds a compact header, discussion title, source link and footer.
        self.assertLess(len(body) + 400, 2800)
        self.assertIn(V.pinned_report_urls()[V.CORE], body)
        self.assertIn(V.pinned_report_urls()[V.STRATA], body)
        self.assertNotIn("/blob/main/", body)
        self.assertIn("2449/2455", body)
        self.assertIn("semantic ability", body)
        self.assertTrue(body.endswith(S.FOOTER))
        self.assertTrue(body.startswith(S.header("V74", S.CLOSE_STATUS)))

    def test_no_single_report_can_satisfy_the_pair(self):
        core, strata = load()
        for changed, field, value in (
            ("CORE", "V74_CORE_PC1_CORRECT", 2454),
            ("CORE", "V74_CORE_PC1_BYTE_CORRECT", 2448),
            ("CORE", "TRAINING_STARTED", 1),
            ("STRATA", "V74_STRATA_PC1_UNIGRAM_SHARED_CORRECT", 2450),
            ("STRATA", "V74_STRATA_F100P_COUNT", 8461),
            ("STRATA", "V74_STRATA_BLIND_ACCESS", 1),
        ):
            a, b = copy.deepcopy(core), copy.deepcopy(strata)
            (a if changed == "CORE" else b)["metrics"][field] = value
            with self.subTest(changed=changed, field=field):
                with self.assertRaises(V.V74ClosureError):
                    V.validate_pair(a, b)

    def test_v74_rejects_strata_as_the_primary_report(self):
        with patch.object(S, "draft", return_value=(
            "Mini-Kuzai | V74 - Frequency-Prior Control",
            "approved", ROOT / "docs/discussions/steps/V74-start.md",
        )):
            with self.assertRaises(S.H.PublicationError):
                S.do_close("V74", V.STRATA, False)

    def test_v74_offline_dry_run_cannot_post(self):
        discussion = {
            "id": "D_mock", "url": "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/5",
        }
        with patch.object(S, "draft", return_value=(
            "Mini-Kuzai | V74 - Frequency-Prior Control",
            "approved", ROOT / "docs/discussions/steps/V74-start.md",
        )), patch.object(S, "git_ready", return_value="a" * 40), \
             patch.object(S, "matching_discussion", return_value=discussion), \
             patch.object(S, "discussion_comments", return_value=[]), \
             patch.object(S.H, "graphql") as mutation, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            S.do_close("V74", V.CORE, False)
        mutation.assert_not_called()
        text = output.getvalue()
        self.assertIn("PUBLICATION=DISABLED", text)
        self.assertIn("GOGIT_CLOSURE=READY_TO_COMMENT", text)
        self.assertIn("V74_FINAL_EVIDENCE=CORE_AND_STRATA_VERIFIED", text)
        self.assertIn("SECONDARY_STEP_ID=", text)
        self.assertIn("GOGIT_COMMENT_LENGTH=", text)


if __name__ == "__main__":
    unittest.main()
