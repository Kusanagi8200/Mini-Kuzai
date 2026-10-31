#!/usr/bin/env python3
"""Publish the three reviewed Mini-Kuzai historical GitHub Discussions.

Read-only by default. --publish is explicit. Authentication is delegated
to GitHub CLI. No access tokens are printed, accepted, or stored.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER = "Kusanagi8200"
REPOSITORY = "Mini-Kuzai"
REPOSITORY_ID = "R_kgDOUI2cCw"
CATEGORY_ID = "DIC_kwDOUI2cC84DKGl8"
CATEGORY_NAME = "Development Log"

POSTS = (
    ("Mini-Kuzai | 01 - Why Build a Language Model From Scratch?",
     "docs/discussions/history/01-origins.md", "HISTORY-01"),
    ("Mini-Kuzai | 02 - From a Transformer to a Developing AI Personality",
     "docs/discussions/history/02-learning-design.md", "HISTORY-02"),
    ("Mini-Kuzai | 03 - What the First Training Experiments Revealed",
     "docs/discussions/history/03-first-training-results.md", "HISTORY-03"),
)

QUERY = """
query($category: ID!, $after: String) {
  repository(owner: "Kusanagi8200", name: "Mini-Kuzai") {
    id
    hasDiscussionsEnabled
    viewerPermission
    discussionCategories(first: 25) { nodes { id name } }
    discussions(first: 100, categoryId: $category, after: $after) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { id number title body url }
    }
  }
}
"""

CREATE = """
mutation($repository: ID!, $category: ID!, $title: String!, $body: String!,
         $mutation: String!) {
  createDiscussion(input: {
    repositoryId: $repository, categoryId: $category,
    title: $title, body: $body, clientMutationId: $mutation
  }) {
    discussion { id number title body url }
  }
}
"""


class PublicationError(RuntimeError):
    pass


def graphql(query: str, **fields: str) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in fields.items():
        args.extend(["-f", f"{key}={value}"])
    try:
        completed = subprocess.run(
            args, capture_output=True, text=True, check=False, timeout=45
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PublicationError("GitHub CLI invocation failed or timed out") from exc
    if completed.returncode:
        # Do not print raw stderr, environment, or authentication details.
        raise PublicationError(
            f"GitHub GraphQL request failed (exit {completed.returncode})"
        )
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise PublicationError("GitHub GraphQL returned non-JSON data") from exc
    if not isinstance(data, dict) or data.get("errors"):
        raise PublicationError("GitHub GraphQL reported an API or permission error")
    if not isinstance(data.get("data"), dict):
        raise PublicationError("GitHub GraphQL response missing data")
    return data["data"]


def list_discussions() -> list[dict]:
    """Inspect all category pages, never just the first 50 discussions."""
    items = []
    cursor = None
    seen_cursors = set()
    total = None
    while True:
        fields = {"category": CATEGORY_ID}
        if cursor:
            fields["after"] = cursor
        repo = graphql(QUERY, **fields).get("repository")
        if not isinstance(repo, dict):
            raise PublicationError("Target GitHub repository unavailable")
        if (repo.get("id") != REPOSITORY_ID
                or repo.get("hasDiscussionsEnabled") is not True
                or repo.get("viewerPermission") not in ("ADMIN", "MAINTAIN", "WRITE")):
            raise PublicationError(
                "Repository identity, Discussions or permission gate failed"
            )
        if not any(
            entry.get("id") == CATEGORY_ID and entry.get("name") == CATEGORY_NAME
            for entry in repo.get("discussionCategories", {}).get("nodes", [])
        ):
            raise PublicationError("Expected GitHub discussion category changed")
        listing = repo.get("discussions")
        if not isinstance(listing, dict):
            raise PublicationError("GitHub discussions list missing")
        if total is None:
            total = listing.get("totalCount")
        items.extend(listing.get("nodes") or [])
        page = listing.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            break
        new_cursor = page.get("endCursor")
        if not new_cursor or new_cursor in seen_cursors:
            raise PublicationError("Invalid GitHub discussion pagination")
        seen_cursors.add(new_cursor)
        cursor = new_cursor
    if not isinstance(total, int) or len(items) != total:
        raise PublicationError("GitHub category discussion inventory incomplete")
    return items


def normalized(body: str) -> str:
    return body.replace("\r\n", "\n").rstrip("\n")


def load_posts() -> list[tuple[str, str, str]]:
    posts = []
    fence = chr(96) * 3
    footer = "##### **" + chr(96) + \
             "THE KUZ NETWORK - KUSANAGI8200 - @2026" + chr(96) + "**"
    for title, path, step in POSTS:
        source = ROOT / path
        if not source.is_file() or source.is_symlink():
            raise PublicationError(f"Missing or unsafe post file: {path}")
        body = source.read_text(encoding="utf-8")
        if not (
            body.startswith(fence + "text\n" + "=" * 72 + "\n")
            and "  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH\n" in body
            and f"  STEP     : {step}\n" in body
            and "  PROJECT  : THE KUZ NETWORK\n" in body
            and body.strip().endswith(footer)
            and "\n" + fence + "\n" in body
            and len(body) > 1000
        ):
            raise PublicationError(
                f"ASCII header or body integrity failed: {path}"
            )
        posts.append((title, normalized(body), path))
    if len(set(title for title, _, _ in posts)) != len(posts):
        raise PublicationError("Historical discussion titles are not unique")
    return posts


def locate(discussions: list[dict], title: str, body: str) -> dict | None:
    matched = [item for item in discussions if item.get("title") == title]
    if len(matched) > 1:
        raise PublicationError(
            f"Multiple GitHub discussions share this title: {title}"
        )
    if not matched:
        return None
    existing = matched[0]
    if normalized(existing.get("body") or "") != body:
        raise PublicationError(
            f"Existing discussion differs, refusing overwrite: {title}"
        )
    if not existing.get("id") or not existing.get("url"):
        raise PublicationError("Existing discussion missing ID or canonical URL")
    return existing


def create_discussion(title: str, body: str, step: str) -> dict:
    response = graphql(
        CREATE, repository=REPOSITORY_ID, category=CATEGORY_ID,
        title=title, body=body, mutation=f"mini-kuzai-{step.lower()}-20261031"
    )
    result = (response.get("createDiscussion") or {}).get("discussion")
    if not isinstance(result, dict) or not (
        result.get("id") and result.get("url")
        and result.get("title") == title
        and normalized(result.get("body") or "") == body
    ):
        raise PublicationError(
            "GitHub returned an unexpected discussion; inspect remotely"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mini-Kuzai historical GitHub Discussions publisher"
    )
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "--dry-run", action="store_true",
        help="Check all posts without publishing (default)"
    )
    actions.add_argument(
        "--publish", action="store_true",
        help="Explicitly create missing discussions"
    )
    args = parser.parse_args()

    posts = load_posts()
    existing = list_discussions()
    print(f"TARGET={OWNER}/{REPOSITORY}")
    print(f"CATEGORY={CATEGORY_NAME}")
    print(f"EXISTING_DISCUSSIONS={len(existing)}")
    print(f"MODE={'PUBLISH' if args.publish else 'DRY_RUN'}")
    for number, (title, body, path) in enumerate(posts, start=1):
        found = locate(existing, title, body)
        state = "EXISTS_IDENTICAL" if found else "READY_TO_CREATE"
        print(
            f"POST_{number}={state} | {title} | chars={len(body)} | {path}"
        )
    if not args.publish:
        print("PUBLICATION=DISABLED")
        return 0

    created = 0
    for number, (title, body, _path) in enumerate(posts, start=1):
        # Re-read remote before each mutation: restart-safe after partial failures.
        current = locate(list_discussions(), title, body)
        if current is None:
            current = create_discussion(title, body, POSTS[number - 1][2])
            created += 1
        verified = locate(list_discussions(), title, body)
        if not verified or verified["id"] != current["id"]:
            raise PublicationError("Post-write GitHub verification failed")
        print(f"POST_{number}_URL={verified['url']}")
    print(f"CREATED={created}")
    print("PUBLICATION=VERIFIED")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PublicationError as exc:
        print(f"PUBLICATION=BLOCKED: {exc}", file=sys.stderr)
        sys.exit(1)
