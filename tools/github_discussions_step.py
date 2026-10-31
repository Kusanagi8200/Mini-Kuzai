#!/usr/bin/env python3
"""Mini-Kuzai Discussions START Vxx and GOGIT closure. Read-only by default.

The operator reviews a committed start Markdown draft. A closure comment is
generated strictly from the matching, committed public GOGIT history report.
Live writes require --publish. GitHub CLI provides existing authentication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import github_discussions_history as H

ROOT = Path(__file__).resolve().parents[1]
STEP_RE = re.compile(r"V([1-9][0-9]{1,2})\Z")
LINE = "=" * 72
FENCE = chr(96) * 3
FOOTER = "##### **" + chr(96) + "THE KUZ NETWORK - KUSANAGI8200 - @2026" + chr(96) + "**"
START_STATUS = "EXPERIMENT STARTED"
CLOSE_STATUS = "EXPERIMENT COMPLETED - GOGIT VERIFIED"
REPORT_DIR = "reports/assistant-results/history/"

COMMENTS_QUERY = """
query($discussion: ID!, $after: String) {
  node(id: $discussion) {
    ... on Discussion {
      id
      comments(first: 100, after: $after) {
        totalCount
        pageInfo { hasNextPage endCursor }
        nodes { id body url }
      }
    }
  }
}
"""

ADD_COMMENT = """
mutation($discussion: ID!, $body: String!, $mutation: String!) {
  addDiscussionComment(input: {
    discussionId: $discussion, body: $body, clientMutationId: $mutation
  }) {
    comment { id body url }
  }
}
"""


def reject(reason: str):
    raise H.PublicationError(reason)


def checked_step(step: str):
    match = STEP_RE.fullmatch(step)
    if match is None or int(match.group(1)) < 74:
        reject("The Vxx workflow accepts V74 through V999 only")


def header(step: str, status: str) -> str:
    return "\n".join((
        FENCE + "text",
        LINE,
        "  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH",
        LINE,
        "  PROJECT  : THE KUZ NETWORK",
        "  PHASE    : 03",
        f"  STEP     : {step}",
        f"  STATUS   : {status}",
        LINE,
        FENCE,
    ))


def draft(step: str):
    checked_step(step)
    relative = f"docs/discussions/steps/{step}-start.md"
    path = ROOT / relative
    if not path.is_file() or path.is_symlink():
        reject(f"Reviewed, committed Markdown draft required: {relative}")
    body = path.read_text(encoding="utf-8")
    lines = body.splitlines()
    if not lines or not lines[0].startswith(f"# Mini-Kuzai | {step} - "):
        reject("Draft title must be: # Mini-Kuzai | Vxx - meaningful subject")
    title = lines[0][2:]
    content = "\n".join(lines[1:]).strip()
    if not (30 <= len(title) <= 120 and 450 <= len(content) <= 15000):
        reject("Draft title or body length outside allowed limits")
    if not content.startswith(header(step, START_STATUS) + "\n"):
        reject("Start draft is missing the exact approved ASCII header")
    if not content.endswith(FOOTER):
        reject("Start draft missing the project footer")
    if any(x in content for x in ("[TODO]", "[OBJECTIVE]", "TBD", "{{", "}}")):
        reject("Draft contains unresolved placeholders")
    return title, H.normalized(content), path


def run_git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            check=False, capture_output=True, text=True, timeout=40
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise H.PublicationError("Git validation invocation failed") from exc
    if result.returncode:
        reject("Git validation failed; inspect local repository state")
    return result.stdout.strip()


def git_ready(paths: list[Path]) -> str:
    if run_git("rev-parse", "--abbrev-ref", "HEAD") != "main":
        reject("Publication requires main branch")
    head = run_git("rev-parse", "HEAD")
    if head != run_git("rev-parse", "refs/remotes/origin/main"):
        reject("Local main differs from origin/main")
    if run_git("status", "--porcelain"):
        reject("Working tree is not clean")
    remote = run_git("ls-remote", "origin", "refs/heads/main").split()
    if len(remote) != 2 or remote[0] != head:
        reject("Remote main changed; synchronize before publication")
    for path in paths:
        try:
            relative = path.relative_to(ROOT).as_posix()
        except ValueError:
            reject("Path outside Mini-Kuzai working tree")
        run_git("ls-files", "--error-unmatch", "--", relative)
        committed = run_git("show", f"HEAD:{relative}")
        if H.normalized(committed) != H.normalized(
            path.read_text(encoding="utf-8")
        ):
            reject(f"File differs from committed main: {relative}")
    return head


def matching_discussion(step: str, title: str, body: str):
    items = H.list_discussions()
    prefix = f"Mini-Kuzai | {step} - "
    collisions = [d for d in items if (d.get("title") or "").startswith(prefix)]
    if len(collisions) > 1:
        reject("Multiple discussions found for the same version")
    if collisions and collisions[0].get("title") != title:
        reject("An existing Vxx discussion has a different title")
    return H.locate(items, title, body)


def report(step: str, relative: str):
    checked_step(step)
    if not relative or relative.startswith("/") or "\\" in relative:
        reject("An exact relative GOGIT history path is required")
    name = Path(relative)
    if (name.as_posix() != relative or ".." in name.parts
            or not relative.startswith(REPORT_DIR)
            or not relative.endswith(".json")):
        reject("Expected immutable GOGIT JSON from history directory")
    path = ROOT / relative
    if (not name.name.startswith(f"PHASE03-SMOLTALK-{step}-")
            or not path.is_file() or path.is_symlink()):
        reject("GOGIT report absent or version does not match")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise H.PublicationError("Invalid public GOGIT JSON") from exc
    if not isinstance(payload, dict):
        reject("GOGIT report must be an object")
    ident = payload.get("step_id")
    metrics = payload.get("metrics")
    if not (
        isinstance(ident, str)
        and name.name == ident + ".json"
        and ident.startswith(f"PHASE03-SMOLTALK-{step}-")
        and payload.get("project") == "Mini-Kuzai"
        and payload.get("phase") == "03"
        and payload.get("status") == "PUBLIC_AGGREGATE_REVIEW_ONLY"
        and payload.get("private_conversation_data_included") is False
        and isinstance(metrics, dict) and metrics
        and all(re.fullmatch(r"[A-Z][A-Z0-9_]*", k) and type(v) is int
                and 0 <= v <= 100000000 for k, v in metrics.items())
        and any(k.startswith(step + "_") and k.endswith("_PASS") and v == 1
                for k, v in metrics.items())
        and metrics.get("SEMANTIC_VALIDATION_COMPLETE") == 0
        and payload.get("semantic_validation_complete") is False
        and metrics.get("TRAINING_STARTED") is not None
        and metrics.get("TRAINING_AUTHORIZED") is not None
        and any(k.endswith("_BLIND_ACCESS") and v == 0
                for k, v in metrics.items())
        and all(v == 0 for k, v in metrics.items()
                if k.endswith("_BLIND_ACCESS"))
    ):
        reject("GOGIT provenance, safety or PASS metrics not validated")
    producer = payload.get("producer")
    digest = payload.get("producer_sha256")
    if not (
        isinstance(producer, str)
        and producer.startswith("tools/public-audits/")
        and producer.endswith(".py")
        and ".." not in Path(producer).parts
        and re.fullmatch(r"[a-f0-9]{64}", digest or "")
    ):
        reject("GOGIT producer metadata missing or invalid")
    producer_file = ROOT / producer
    if not producer_file.is_file() or producer_file.is_symlink():
        reject("GOGIT producer source missing")
    if hashlib.sha256(producer_file.read_bytes()).hexdigest() != digest:
        reject("GOGIT producer SHA256 mismatch")
    return payload, path, producer_file


def closure_body(step: str, payload: dict, relpath: str, commit: str) -> str:
    url = f"https://github.com/Kusanagi8200/Mini-Kuzai/blob/{commit}/{relpath}"
    metrics = payload["metrics"]
    rows = "\n".join(
        f"| {name} | {value} |" for name, value in sorted(metrics.items())
    )
    return "\n\n".join((
        header(step, CLOSE_STATUS),
        "## GOGIT verification - Public aggregate report",
        f"**STEP_ID:** {payload['step_id']}\n\n"
        f"**Immutable report:** {url}\n\n"
        f"**Producer SHA256:** {payload['producer_sha256']}",
        "### Verified numerical metrics\n\n"
        "| Metric | Value |\n| --- | ---: |\n" + rows,
        "**Interpretation limits:** This public aggregate audit is a technical "
        "verification, not evidence of conversational competence or personality "
        "formation. No BLIND evaluation was authorized for this publication. "
        "Training state is represented solely by the explicit numeric metrics "
        "above. Research conclusions require independent scientific review.",
        "---\n\n" + FOOTER,
    ))


def discussion_comments(ident: str):
    collected = []
    cursor = None
    seen = set()
    total = None
    while True:
        fields = {"discussion": ident}
        if cursor:
            fields["after"] = cursor
        node = H.graphql(COMMENTS_QUERY, **fields).get("node")
        if not isinstance(node, dict) or node.get("id") != ident:
            reject("Discussion identity changed while reading comments")
        data = node.get("comments")
        if not isinstance(data, dict):
            reject("Discussion comment inventory unavailable")
        if total is None:
            total = data.get("totalCount")
        collected.extend(data.get("nodes") or [])
        page = data.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            break
        cursor = page.get("endCursor")
        if not cursor or cursor in seen:
            reject("Discussion comment pagination invalid")
        seen.add(cursor)
    if not isinstance(total, int) or len(collected) != total:
        reject("Incomplete GitHub comment inventory")
    return collected


def matching_comment(items: list[dict], step: str, body: str):
    signature = f"  STEP     : {step}\n  STATUS   : {CLOSE_STATUS}\n"
    choices = [c for c in items
               if signature in (c.get("body") or "")]
    if len(choices) > 1:
        reject("Multiple GOGIT closures found for one version")
    if not choices:
        return None
    comment = choices[0]
    if H.normalized(comment.get("body") or "") != H.normalized(body):
        reject("GOGIT closure already published with different content")
    if not comment.get("id") or not comment.get("url"):
        reject("Existing closure missing ID or URL")
    return comment


def do_start(step: str, publish: bool):
    title, body, path = draft(step)
    git_ready([path])
    prior = matching_discussion(step, title, body)
    print(f"TARGET={H.OWNER}/{H.REPOSITORY}")
    print(f"STEP={step}")
    print(f"MODE={'PUBLISH' if publish else 'DRY_RUN'}")
    print(f"START={'EXISTS_IDENTICAL' if prior else 'READY_TO_CREATE'}")
    if not publish:
        print("PUBLICATION=DISABLED")
        return
    prior = matching_discussion(step, title, body)
    if prior is None:
        prior = H.create_discussion(title, body, step)
    checked = matching_discussion(step, title, body)
    if not checked or checked["id"] != prior["id"]:
        reject("START post-write verification failed")
    print(f"DISCUSSION_URL={checked['url']}")
    print("PUBLICATION=VERIFIED")


def do_close(step: str, relative: str, publish: bool):
    title, body, draft_path = draft(step)
    payload, report_path, producer_path = report(step, relative)
    commit = git_ready([draft_path, report_path, producer_path])
    prior = matching_discussion(step, title, body)
    if prior is None:
        reject("No matching START discussion exists in Development Log")
    comment_body = closure_body(step, payload, relative, commit)
    existing = matching_comment(discussion_comments(prior["id"]),
                                step, comment_body)
    print(f"TARGET={H.OWNER}/{H.REPOSITORY}")
    print(f"STEP={step}")
    print(f"STEP_ID={payload['step_id']}")
    print(f"MODE={'PUBLISH' if publish else 'DRY_RUN'}")
    print(f"DISCUSSION_URL={prior['url']}")
    print(f"GOGIT_CLOSURE={'EXISTS_IDENTICAL' if existing else 'READY_TO_COMMENT'}")
    if not publish:
        print("PUBLICATION=DISABLED")
        return
    verified_start = matching_discussion(step, title, body)
    if verified_start is None or verified_start["id"] != prior["id"]:
        reject("START discussion changed before GOGIT closure")
    existing = matching_comment(discussion_comments(prior["id"]),
                                step, comment_body)
    if existing is None:
        result = H.graphql(ADD_COMMENT, discussion=prior["id"],
                           body=comment_body,
                           mutation=f"mini-kuzai-{step.lower()}-gogit")
        existing = (result.get("addDiscussionComment") or {}).get("comment")
        if not isinstance(existing, dict) or not existing.get("id"):
            reject("GitHub comment creation failed or returned no ID")
    confirmed = matching_comment(discussion_comments(prior["id"]),
                                 step, comment_body)
    if confirmed is None or confirmed["id"] != existing["id"]:
        reject("GOGIT closure post-write verification failed")
    print(f"GOGIT_COMMENT_URL={confirmed['url']}")
    print("PUBLICATION=VERIFIED")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--step", required=True, help="Version, e.g. V74")
    ap.add_argument("--action", required=True, choices=("start", "close"))
    ap.add_argument("--report", help="Exact immutable GOGIT history JSON path")
    ap.add_argument("--publish", action="store_true",
                    help="Explicitly permit GitHub mutation; absent means dry-run")
    opts = ap.parse_args()
    checked_step(opts.step)
    if opts.action == "start":
        if opts.report:
            reject("A START operation must not specify --report")
        do_start(opts.step, opts.publish)
    else:
        if not opts.report:
            reject("A GOGIT closure requires --report")
        do_close(opts.step, opts.report, opts.publish)


if __name__ == "__main__":
    try:
        main()
    except H.PublicationError as exc:
        print(f"PUBLICATION=BLOCKED: {exc}", file=sys.stderr)
        sys.exit(1)
