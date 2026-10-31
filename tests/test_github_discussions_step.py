"""Offline unit tests for the Vxx GitHub Discussions publishing gates."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import github_discussions_step as S


class StepPublisherTests(unittest.TestCase):
    TITLE = "Mini-Kuzai | V74 - Diagnostic of output concentration"
    STEP_ID = "PHASE03-SMOLTALK-V74-TEST-001"
    REPORT = "reports/assistant-results/history/" + STEP_ID + ".json"

    def sample_draft(self):
        content = (
            "# " + self.TITLE + "\n\n"
            + S.header("V74", S.START_STATUS) + "\n\n"
            + "## Objective\n\n"
            + ("Study next-token prediction distribution without making "
               "claims of conversational competence.\n\n") * 8
            + "---\n\n" + S.FOOTER + "\n"
        )
        return content

    def sample_payload(self):
        return {
            "project": "Mini-Kuzai",
            "phase": "03",
            "step_id": self.STEP_ID,
            "status": "PUBLIC_AGGREGATE_REVIEW_ONLY",
            "semantic_validation_complete": False,
            "private_conversation_data_included": False,
            "producer": "tools/public-audits/phase03_v74_test.py",
            "producer_sha256": "",
            "metrics": {
                "SEMANTIC_VALIDATION_COMPLETE": 0,
                "TRAINING_STARTED": 0,
                "TRAINING_AUTHORIZED": 0,
                "V74_DIAG_PASS": 1,
                "V74_DIAG_BLIND_ACCESS": 0,
                "V74_DIAG_SAMPLES": 36,
            },
        }

    def fake_discussion(self, body=None):
        if body is None:
            body = S.header("V74", S.START_STATUS)
        return {
            "id": "D_mock", "number": 42, "title": self.TITLE,
            "body": body,
            "url": "https://github.com/Kusanagi8200/Mini-Kuzai/discussions/42"
        }

    def test_target_is_mini_kuzai_development_log(self):
        self.assertEqual(S.H.REPOSITORY, "Mini-Kuzai")
        self.assertEqual(S.H.REPOSITORY_ID, "R_kgDOUI2cCw")
        self.assertEqual(S.H.CATEGORY_NAME, "Development Log")
        self.assertEqual(S.H.CATEGORY_ID, "DIC_kwDOUI2cC84DKGl8")

    def test_version_scope_is_future_only(self):
        for invalid in ("V73", "v74", "V0", "V1000", "V74/../../x"):
            with self.assertRaises(S.H.PublicationError):
                S.checked_step(invalid)
        S.checked_step("V74")
        S.checked_step("V999")

    def test_header_matches_official_ascii(self):
        start = S.header("V74", S.START_STATUS)
        close = S.header("V74", S.CLOSE_STATUS)
        self.assertIn("MINI-KUZAI  //  FROM SCRATCH AI RESEARCH", start)
        self.assertIn("STEP     : V74", start)
        self.assertIn("STATUS   : EXPERIMENT STARTED", start)
        self.assertIn("STATUS   : EXPERIMENT COMPLETED - GOGIT VERIFIED", close)
        self.assertEqual(start.count(S.LINE), 3)

    def test_reviewed_draft_and_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "docs/discussions/steps"
            folder.mkdir(parents=True)
            target = folder / "V74-start.md"
            target.write_text(self.sample_draft(), encoding="utf-8")
            with patch.object(S, "ROOT", root):
                title, body, source = S.draft("V74")
                self.assertEqual(title, self.TITLE)
                self.assertIn(S.header("V74", S.START_STATUS), body)
                self.assertEqual(source, target)
                target.write_text(self.sample_draft().replace(
                    "Study next-token", "[TODO] Study next-token"
                ), encoding="utf-8")
                with self.assertRaises(S.H.PublicationError):
                    S.draft("V74")

    def test_missing_draft_blocks_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(S, "ROOT", Path(tmp)):
                with self.assertRaises(S.H.PublicationError):
                    S.draft("V74")

    def test_same_step_with_different_title_blocks(self):
        with patch.object(S.H, "list_discussions", return_value=[
            self.fake_discussion() | {
                "title": "Mini-Kuzai | V74 - Different title"
            }
        ]):
            with self.assertRaises(S.H.PublicationError):
                S.matching_discussion("V74", self.TITLE, "irrelevant")

    def test_start_dry_run_never_creates(self):
        with patch.object(S, "draft", return_value=(
            self.TITLE, "sample body", ROOT / "sample"
        )), patch.object(S, "git_ready", return_value="a" * 40), \
             patch.object(S, "matching_discussion", return_value=None), \
             patch.object(S.H, "create_discussion") as create, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            S.do_start("V74", False)
        create.assert_not_called()
        self.assertIn("START=READY_TO_CREATE", output.getvalue())
        self.assertIn("PUBLICATION=DISABLED", output.getvalue())

    def test_start_publish_verifies_created(self):
        discussion = self.fake_discussion("sample body")
        with patch.object(S, "draft", return_value=(
            self.TITLE, "sample body", ROOT / "sample"
        )), patch.object(S, "git_ready", return_value="a" * 40), \
             patch.object(S, "matching_discussion", side_effect=[
                 None, None, discussion
             ]), patch.object(S.H, "create_discussion",
                             return_value=discussion) as create, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            S.do_start("V74", True)
        create.assert_called_once()
        self.assertIn("PUBLICATION=VERIFIED", output.getvalue())

    def test_start_publish_skips_existing_identical(self):
        discussion = self.fake_discussion("sample body")
        with patch.object(S, "draft", return_value=(
            self.TITLE, "sample body", ROOT / "sample"
        )), patch.object(S, "git_ready", return_value="a" * 40), \
             patch.object(S, "matching_discussion",
                          return_value=discussion), \
             patch.object(S.H, "create_discussion") as create, \
             contextlib.redirect_stdout(io.StringIO()):
            S.do_start("V74", True)
        create.assert_not_called()

    def test_valid_report_producer_digest_and_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = self.sample_payload()
            producer = root / p["producer"]
            producer.parent.mkdir(parents=True)
            producer.write_text("# Reviewed audit\n", encoding="utf-8")
            p["producer_sha256"] = hashlib.sha256(
                producer.read_bytes()
            ).hexdigest()
            out = root / self.REPORT
            out.parent.mkdir(parents=True)
            out.write_text(json.dumps(p), encoding="utf-8")
            with patch.object(S, "ROOT", root):
                got, report_path, producer_path = S.report("V74", self.REPORT)
                self.assertEqual(got["step_id"], self.STEP_ID)
                self.assertEqual(report_path, out)
                self.assertEqual(producer_path, producer)
                p["metrics"]["V74_DIAG_BLIND_ACCESS"] = 1
                out.write_text(json.dumps(p), encoding="utf-8")
                with self.assertRaises(S.H.PublicationError):
                    S.report("V74", self.REPORT)
                p["metrics"]["V74_DIAG_BLIND_ACCESS"] = 0
                p["metrics"]["V74_DIAG_PASS"] = 0
                out.write_text(json.dumps(p), encoding="utf-8")
                with self.assertRaises(S.H.PublicationError):
                    S.report("V74", self.REPORT)
                p["metrics"]["V74_DIAG_PASS"] = 1
                out.write_text(json.dumps(p), encoding="utf-8")
                producer.write_text("# Tampered\n", encoding="utf-8")
                with self.assertRaises(S.H.PublicationError):
                    S.report("V74", self.REPORT)

    def test_invalid_report_paths(self):
        for path in (
            "/etc/passwd", "../history/x.json", "reports/assistant-results/latest.json",
            "reports/assistant-results/history/PHASE03-SMOLTALK-V75-X.json",
        ):
            with self.assertRaises(S.H.PublicationError):
                S.report("V74", path)

    def test_closure_body_uses_pinned_link_not_moving_main(self):
        p = self.sample_payload()
        p["producer_sha256"] = "f" * 64
        rendered = S.closure_body("V74", p, self.REPORT, "a" * 40)
        self.assertIn("/blob/" + "a" * 40 + "/" + self.REPORT, rendered)
        self.assertNotIn("/blob/main/", rendered)
        self.assertIn("| V74_DIAG_PASS | 1 |", rendered)
        self.assertIn("not evidence of conversational competence", rendered)
        self.assertIn(S.header("V74", S.CLOSE_STATUS), rendered)

    def test_duplicate_or_conflicting_closure_blocks(self):
        p = self.sample_payload()
        body = S.closure_body("V74", p, self.REPORT, "a" * 40)
        entry = {"id": "DC_mock", "url": "https://github.com/example/42#comment",
                 "body": body}
        self.assertEqual(S.matching_comment([entry], "V74", body), entry)
        with self.assertRaises(S.H.PublicationError):
            S.matching_comment([entry, entry], "V74", body)
        with self.assertRaises(S.H.PublicationError):
            S.matching_comment([entry], "V74", body + "\nDifferent")

    def test_close_refuses_missing_start(self):
        p = self.sample_payload()
        with patch.object(S, "draft", return_value=(
            self.TITLE, "body", ROOT / "draft.md"
        )), patch.object(S, "report", return_value=(
            p, ROOT / "report.json", ROOT / "audit.py"
        )), patch.object(S, "git_ready", return_value="a" * 40), \
             patch.object(S, "matching_discussion", return_value=None):
            with self.assertRaises(S.H.PublicationError):
                S.do_close("V74", self.REPORT, False)

    def test_close_dry_run_no_mutation(self):
        p = self.sample_payload()
        discussion = self.fake_discussion()
        with patch.object(S, "draft", return_value=(
            self.TITLE, "body", ROOT / "draft.md"
        )), patch.object(S, "report", return_value=(
            p, ROOT / "report.json", ROOT / "audit.py"
        )), patch.object(S, "git_ready", return_value="a" * 40), \
             patch.object(S, "matching_discussion",
                          return_value=discussion), \
             patch.object(S, "discussion_comments", return_value=[]), \
             patch.object(S.H, "graphql") as call, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            S.do_close("V74", self.REPORT, False)
        call.assert_not_called()
        self.assertIn("GOGIT_CLOSURE=READY_TO_COMMENT", output.getvalue())
        self.assertIn("PUBLICATION=DISABLED", output.getvalue())

    def test_close_publish_adds_exactly_one_comment(self):
        p = self.sample_payload()
        discussion = self.fake_discussion()
        expected_body = S.closure_body("V74", p, self.REPORT, "a" * 40)
        created = {
            "id": "DC_mock",
            "body": expected_body,
            "url": discussion["url"] + "#discussioncomment-1",
        }
        with patch.object(S, "draft", return_value=(
            self.TITLE, "body", ROOT / "draft.md"
        )), patch.object(S, "report", return_value=(
            p, ROOT / "report.json", ROOT / "audit.py"
        )), patch.object(S, "git_ready", return_value="a" * 40), \
             patch.object(S, "matching_discussion",
                          return_value=discussion), \
             patch.object(S, "discussion_comments", side_effect=[
                 [], [], [created]
             ]), patch.object(S.H, "graphql", return_value={
                 "addDiscussionComment": {"comment": created}
             }) as call, contextlib.redirect_stdout(io.StringIO()) as output:
            S.do_close("V74", self.REPORT, True)
        call.assert_called_once()
        self.assertIn("PUBLICATION=VERIFIED", output.getvalue())

    def test_incomplete_comments_inventory_blocks(self):
        fake = {"node": {
            "id": "D_mock", "comments": {
                "totalCount": 2, "nodes": [{"id": "DC_1"}],
                "pageInfo": {"hasNextPage": False}
            }
        }}
        with patch.object(S.H, "graphql", return_value=fake):
            with self.assertRaises(S.H.PublicationError):
                S.discussion_comments("D_mock")


if __name__ == "__main__":
    unittest.main()
