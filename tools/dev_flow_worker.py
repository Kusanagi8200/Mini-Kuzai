#!/usr/bin/env python3
"""Process explicit Mini-Kuzai START-DEV-FLOW / FINAL-DEV-FLOW requests.

The worker is intentionally inert without a committed request file.  It syncs
main, validates the request, delegates GitHub Discussions writes to the
existing reviewed publisher, and records an auditable receipt only after the
remote publication is verified.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_DIR = ROOT / "automation/dev-flow/requests"
RECEIPT_DIR = ROOT / "automation/dev-flow/receipts"
PUBLISHER = ROOT / "tools/github_discussions_step.py"
PYTHON = Path("/root/Mini-Kuzai/.venv/bin/python")
LOCK = Path("/run/lock/mini-kuzai-dev-flow.lock")

EXPECTED_ACTOR = "Kusanagi8200"
EXPECTED_REMOTE = "origin"
EXPECTED_BRANCH = "main"
STEP_RE = re.compile(r"V(?:[7-9][0-9]|[1-9][0-9]{2})\Z")
REPORT_PREFIX = "reports/assistant-results/history/"
URL_RE = re.compile(
    r"https://github\.com/Kusanagi8200/Mini-Kuzai/discussions/"
    r"[1-9][0-9]*(?:#discussioncomment-[1-9][0-9]*)?\Z"
)


class DevFlowError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise DevFlowError(message)


def run(
    args: list[str],
    *,
    timeout: int = 60,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DevFlowError(f"Command failed to execute: {args[0]}") from exc

    if check and result.returncode != 0:
        raise DevFlowError(
            f"Command returned exit {result.returncode}: {args[0]}"
        )
    return result


def git(*args: str, timeout: int = 60) -> str:
    return run(["git", *args], timeout=timeout).stdout.strip()


def sync_main() -> str:
    if git("branch", "--show-current") != EXPECTED_BRANCH:
        fail("DEV-FLOW requires main branch")

    if git("status", "--porcelain"):
        fail("DEV-FLOW requires a clean worktree")

    git("fetch", "--no-tags", EXPECTED_REMOTE, EXPECTED_BRANCH)

    local = git("rev-parse", "HEAD")
    remote = git("rev-parse", f"{EXPECTED_REMOTE}/{EXPECTED_BRANCH}")

    if local != remote:
        is_ancestor = run(
            ["git", "merge-base", "--is-ancestor", local, remote],
            check=False,
        )
        if is_ancestor.returncode != 0:
            fail("Local main is not a fast-forward ancestor of origin/main")
        git("merge", "--ff-only", f"{EXPECTED_REMOTE}/{EXPECTED_BRANCH}")
        local = git("rev-parse", "HEAD")

    if local != remote or git("status", "--porcelain"):
        fail("Repository synchronization verification failed")

    return local


def github_actor() -> str:
    result = run(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            "query=query { viewer { login } }",
            "--jq",
            ".data.viewer.login",
        ]
    )
    actor = result.stdout.strip()
    if actor != EXPECTED_ACTOR:
        fail("GitHub CLI identity is not the approved publisher")
    return actor


def request_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_request_payload(payload: dict, filename: str) -> dict:
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        fail("Unsupported DEV-FLOW request schema")

    command = payload.get("command")
    step = payload.get("step")

    if command not in {"START-DEV-FLOW", "FINAL-DEV-FLOW"}:
        fail("Unsupported DEV-FLOW command")
    if not isinstance(step, str) or not STEP_RE.fullmatch(step):
        fail("Invalid DEV-FLOW step")

    if command == "START-DEV-FLOW":
        if set(payload) != {"schema_version", "command", "step"}:
            fail("Unexpected START request fields")
        expected_name = f"{step}-start.json"
        action = "start"
        report = None
    else:
        if set(payload) != {"schema_version", "command", "step", "report"}:
            fail("Unexpected FINAL request fields")
        expected_name = f"{step}-final.json"
        action = "close"
        report = payload.get("report")
        if (
            not isinstance(report, str)
            or not report.startswith(REPORT_PREFIX)
            or "\\" in report
            or ".." in Path(report).parts
            or Path(report).is_absolute()
            or not report.endswith(".json")
            or not Path(report).name.startswith(
                f"PHASE03-SMOLTALK-{step}-"
            )
        ):
            fail("Invalid FINAL GOGIT report path")

    if filename != expected_name:
        fail("DEV-FLOW request filename does not match payload")

    return {
        "schema_version": 1,
        "command": command,
        "step": step,
        "action": action,
        "report": report,
    }


def load_committed_request(path: Path) -> tuple[dict, str]:
    if path.is_symlink() or not path.is_file():
        fail("Unsafe DEV-FLOW request file")

    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise DevFlowError("Request outside repository") from exc

    text = path.read_text(encoding="utf-8")
    committed = git("show", f"HEAD:{relative}")

    if committed != text.rstrip("\n"):
        # git show strips the final line terminator from command output.
        if committed + "\n" != text:
            fail("Request differs from committed main")

    try:
        payload = json.loads(text)
    except (OSError, ValueError) as exc:
        raise DevFlowError("Invalid DEV-FLOW JSON") from exc

    return validate_request_payload(payload, path.name), request_sha256(text)


def receipt_path(request: dict) -> Path:
    suffix = "start" if request["action"] == "start" else "final"
    return RECEIPT_DIR / f"{request['step']}-{suffix}.json"


def request_sort_key(path: Path) -> tuple[int, int]:
    match = re.fullmatch(r"V([0-9]+)-(start|final)\.json", path.name)
    if match is None:
        return (10**9, 10)
    return (int(match.group(1)), 0 if match.group(2) == "start" else 1)


def pending_requests() -> list[Path]:
    if not REQUEST_DIR.exists():
        return []
    if REQUEST_DIR.is_symlink() or not REQUEST_DIR.is_dir():
        fail("Unsafe DEV-FLOW request directory")

    pending: list[Path] = []
    for path in sorted(REQUEST_DIR.glob("V*-*.json"), key=request_sort_key):
        try:
            request, _digest = load_committed_request(path)
        except DevFlowError:
            raise
        if not receipt_path(request).exists():
            pending.append(path)
    return pending


def extract_value(output: str, key: str) -> str:
    values = [
        line[len(key) + 1 :].strip()
        for line in output.splitlines()
        if line.startswith(key + "=")
    ]
    if len(values) != 1 or not values[0]:
        fail(f"Publisher output missing {key}")
    return values[0]


def invoke_publisher(request: dict, publish: bool) -> tuple[str, str | None]:
    if not PYTHON.is_file() or not os.access(PYTHON, os.X_OK):
        fail("Mini-Kuzai Python environment unavailable")
    if PUBLISHER.is_symlink() or not PUBLISHER.is_file():
        fail("GitHub Discussions publisher unavailable")

    args = [
        str(PYTHON),
        str(PUBLISHER),
        "--step",
        request["step"],
        "--action",
        request["action"],
    ]

    if request["report"] is not None:
        args.extend(["--report", request["report"]])

    if publish:
        args.append("--publish")

    result = run(args, timeout=120, check=False)

    if result.returncode != 0:
        # Existing publisher error messages contain no credentials.
        detail = result.stderr.strip() or result.stdout.strip()
        raise DevFlowError(
            "GitHub Discussions publisher rejected the request"
            + (f": {detail}" if detail else "")
        )

    output = result.stdout.strip()

    if not publish:
        return output, None

    if "PUBLICATION=VERIFIED" not in output.splitlines():
        fail("GitHub Discussions publication was not verified")

    key = "DISCUSSION_URL" if request["action"] == "start" else "GOGIT_COMMENT_URL"
    url = extract_value(output, key)

    if not URL_RE.fullmatch(url):
        fail("Publisher returned an unexpected GitHub URL")
    if request["action"] == "start" and "#" in url:
        fail("START publication returned a comment URL")
    if request["action"] == "close" and "#discussioncomment-" not in url:
        fail("FINAL publication returned no comment URL")

    return output, url


def ensure_final_has_start_receipt(request: dict) -> None:
    if request["action"] != "close":
        return
    start = RECEIPT_DIR / f"{request['step']}-start.json"
    if start.is_symlink() or not start.is_file():
        fail("FINAL requires a committed START receipt")
    relative = start.relative_to(ROOT).as_posix()
    git("ls-files", "--error-unmatch", "--", relative)


def write_receipt(
    request: dict,
    digest: str,
    source_commit: str,
    url: str,
) -> Path:
    if RECEIPT_DIR.exists() and (
        RECEIPT_DIR.is_symlink() or not RECEIPT_DIR.is_dir()
    ):
        fail("Unsafe DEV-FLOW receipt directory")
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)

    target = receipt_path(request)
    if target.exists() or target.is_symlink():
        fail("DEV-FLOW receipt already exists")

    data = {
        "schema_version": 1,
        "command": request["command"],
        "step": request["step"],
        "request_sha256": digest,
        "source_commit": source_commit,
        "github_url": url,
        "published_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PUBLISHED",
    }

    fd, temporary = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=RECEIPT_DIR,
        text=True,
    )
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

    return target


def commit_receipt(path: Path, request: dict, source_commit: str) -> str:
    remote_now = git(
        "ls-remote",
        EXPECTED_REMOTE,
        f"refs/heads/{EXPECTED_BRANCH}",
    ).split()

    if len(remote_now) != 2 or remote_now[0] != source_commit:
        fail("Remote main changed after publication; receipt deferred")

    relative = path.relative_to(ROOT).as_posix()
    git("add", "--", relative)

    message = (
        f"dev-flow: record {request['step']} "
        f"{'START' if request['action'] == 'start' else 'FINAL'} publication"
    )
    git("commit", "-m", message)
    receipt_commit = git("rev-parse", "HEAD")

    pushed = run(
        ["git", "push", EXPECTED_REMOTE, f"HEAD:{EXPECTED_BRANCH}"],
        timeout=90,
        check=False,
    )
    if pushed.returncode != 0:
        # The GitHub publication is idempotent. Restore the local branch so a
        # future timer run can safely resync and record the receipt.
        git("reset", "--hard", source_commit)
        git("fetch", "--no-tags", EXPECTED_REMOTE, EXPECTED_BRANCH)
        fail("Receipt push failed; request remains retryable")

    remote = git(
        "ls-remote",
        EXPECTED_REMOTE,
        f"refs/heads/{EXPECTED_BRANCH}",
    ).split()
    if len(remote) != 2 or remote[0] != receipt_commit:
        fail("Receipt push verification failed")

    return receipt_commit


def process_one(path: Path, publish: bool) -> None:
    source_commit = git("rev-parse", "HEAD")
    request, digest = load_committed_request(path)
    ensure_final_has_start_receipt(request)

    print(f"REQUEST={path.name}")
    print(f"COMMAND={request['command']}")
    print(f"STEP={request['step']}")
    print(f"MODE={'PUBLISH' if publish else 'DRY_RUN'}")

    output, url = invoke_publisher(request, publish)
    if output:
        print(output)

    if not publish:
        print("DEV_FLOW=DRY_RUN_PASS")
        return

    assert url is not None
    target = write_receipt(request, digest, source_commit, url)

    try:
        receipt_commit = commit_receipt(
            target, request, source_commit
        )
    except Exception:
        if target.exists():
            target.unlink()
        raise

    print(f"DEV_FLOW_URL={url}")
    print(f"RECEIPT={target.relative_to(ROOT).as_posix()}")
    print(f"RECEIPT_COMMIT={receipt_commit}")
    print("DEV_FLOW=VERIFIED")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Process an explicit committed request with live GitHub writes",
    )
    args = parser.parse_args()

    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

        print("##### SECTION RESULTS FOR ASSISTANT ######")
        try:
            head = sync_main()
            actor = github_actor()
            print(f"HEAD={head}")
            print(f"GITHUB_ACTOR={actor}")

            items = pending_requests()
            print(f"PENDING_REQUESTS={len(items)}")

            if not items:
                print("DEV_FLOW=IDLE")
                return 0

            # One request per invocation keeps each publication transaction
            # isolated and makes failures straightforward to diagnose.
            process_one(items[0], args.publish)
            return 0
        except DevFlowError as exc:
            print(f"DEV_FLOW=BLOCKED")
            print(f"ERROR={exc}")
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
