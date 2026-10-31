"""Offline safety tests for the historical GitHub Discussions publisher."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/github_discussions_history.py"
spec = importlib.util.spec_from_file_location("github_discussions_history", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("Historical publisher missing")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


class HistoricalDiscussionsSafetyTests(unittest.TestCase):
    def test_target_is_mini_kuzai_development_log(self):
        self.assertEqual(P.OWNER, "Kusanagi8200")
        self.assertEqual(P.REPOSITORY, "Mini-Kuzai")
        self.assertEqual(P.REPOSITORY_ID, "R_kgDOUI2cCw")
        self.assertEqual(P.CATEGORY_ID, "DIC_kwDOUI2cC84DKGl8")
        self.assertEqual(P.CATEGORY_NAME, "Development Log")
        self.assertIn('repository(owner: "Kusanagi8200", name: "Mini-Kuzai")', P.QUERY)
        self.assertNotIn('name: "KuzAI"', P.QUERY)

    def test_all_three_reviewed_posts_and_ascii_headers(self):
        posts = P.load_posts()
        self.assertEqual(len(posts), 3)
        self.assertEqual(len({title for title, _, _ in posts}), 3)
        for i, (title, body, path) in enumerate(posts, 1):
            self.assertIn(f"  STEP     : HISTORY-0{i}", body)
            self.assertIn("FROM SCRATCH AI RESEARCH", body)
            self.assertTrue(title.startswith(f"Mini-Kuzai | 0{i} - "))
            self.assertTrue((ROOT / path).is_file())

    def test_empty_category_creates_no_false_duplicate(self):
        title, body, _ = P.load_posts()[0]
        self.assertIsNone(P.locate([], title, body))

    def test_identical_existing_is_detected(self):
        title, body, _ = P.load_posts()[0]
        entry = {"id": "D_1", "url": "https://github.com/example/discussions/1",
                 "title": title, "body": body + "\n"}
        self.assertEqual(P.locate([entry], title, body)["id"], "D_1")

    def test_conflicting_existing_blocks(self):
        title, body, _ = P.load_posts()[0]
        entry = {"id": "D_1", "url": "https://github.com/example/discussions/1",
                 "title": title, "body": "Other content"}
        with self.assertRaises(P.PublicationError):
            P.locate([entry], title, body)

    def test_duplicate_exact_titles_block(self):
        title, body, _ = P.load_posts()[0]
        entry = {"id": "D_1", "url": "https://github.com/example/discussions/1",
                 "title": title, "body": body}
        with self.assertRaises(P.PublicationError):
            P.locate([entry, dict(entry)], title, body)

    def test_invalid_repository_or_category_blocks(self):
        def response(repo_id=P.REPOSITORY_ID, cat_id=P.CATEGORY_ID):
            return {"repository": {
                "id": repo_id, "viewerPermission": "ADMIN",
                "hasDiscussionsEnabled": True,
                "discussionCategories": {"nodes": [
                    {"id": cat_id, "name": P.CATEGORY_NAME}]},
                "discussions": {"totalCount": 0, "nodes": [],
                                "pageInfo": {"hasNextPage": False}},
            }}
        with patch.object(P, "graphql", return_value=response()):
            self.assertEqual(P.list_discussions(), [])
        with patch.object(P, "graphql", return_value=response(repo_id="wrong")):
            with self.assertRaises(P.PublicationError):
                P.list_discussions()
        with patch.object(P, "graphql", return_value=response(cat_id="wrong")):
            with self.assertRaises(P.PublicationError):
                P.list_discussions()

    def test_graphql_error_never_becomes_success(self):
        with patch.object(P.subprocess, "run", return_value=type("R", (), {
            "returncode": 0, "stdout": '{"errors":[{"message":"blocked"}]}',
        })()):
            with self.assertRaises(P.PublicationError):
                P.graphql(P.QUERY, category=P.CATEGORY_ID)

    def test_incomplete_pagination_blocks(self):
        r = {"repository": {
            "id": P.REPOSITORY_ID, "viewerPermission": "ADMIN",
            "hasDiscussionsEnabled": True,
            "discussionCategories": {"nodes": [
                {"id": P.CATEGORY_ID, "name": P.CATEGORY_NAME}]},
            "discussions": {
                "totalCount": 2, "nodes": [{"title": "A"}],
                "pageInfo": {"hasNextPage": False}
            },
        }}
        with patch.object(P, "graphql", return_value=r):
            with self.assertRaises(P.PublicationError):
                P.list_discussions()


if __name__ == "__main__":
    unittest.main()
