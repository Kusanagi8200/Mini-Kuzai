#!/usr/bin/env python3
"""Local terminal review for public SmolTalk V46 candidate conversations.

Records human triage decisions in a local, append-only JSONL ledger. Each
candidate remains unapproved for TRAIN and unassigned to a model dataset split.
Neither original conversation text nor written justifications go to GitHub.
"""

import argparse
import datetime as dt
import fcntl
import json
import os
import re
from collections import Counter
from pathlib import Path

ROOT = Path('/root/Mini-Kuzai/data/external/smol-smoltalk/review')
QUEUE = ROOT / 'v46-manual-review-queue.jsonl'
LEDGER = ROOT / 'v48-human-review-ledger.jsonl'
GROUPS = {'RELABEL': 12, 'RESCUE': 24, 'BASE': 32}
VALID = {'RETAIN', 'REJECT', 'HOLD'}
SHA = re.compile(r'[0-9a-f]{64}\Z')
SCHEMA = 'mini-kuzai.v48.human-review-event.v1'


def load_queue():
    if not QUEUE.is_file():
        raise RuntimeError('Missing local V46 queue')
    rows = []
    seen = set()
    counts = Counter()
    with QUEUE.open(encoding='utf-8') as stream:
        for line in stream:
            if not line.strip():
                continue
            rec = json.loads(line)
            sha = rec.get('source_content_sha256')
            group = rec.get('review_queue_reason')
            msgs = rec.get('messages_original')
            if (not isinstance(sha, str) or not SHA.fullmatch(sha)
                    or sha in seen or group not in GROUPS
                    or rec.get('review_decision') != 'UNREVIEWED'
                    or rec.get('training_approved') is not False
                    or rec.get('dataset_split_assigned') is not False
                    or rec.get('semantic_validation_complete') is not False
                    or not isinstance(msgs, list) or len(msgs) not in (2, 4, 6)
                    or [m.get('role') for m in msgs] != ['user', 'assistant'] * (len(msgs)//2)
                    or any(not isinstance(m.get('content'), str) or not m['content'].strip() for m in msgs)):
                raise RuntimeError('V46 local queue integrity failed')
            rows.append(rec)
            seen.add(sha)
            counts[group] += 1
    if len(rows) != 68 or counts != GROUPS:
        raise RuntimeError('Expected 68 V46 records in groups 12/24/32')
    rows.sort(key=lambda rec: (
        {'RELABEL': 0, 'RESCUE': 1, 'BASE': 2}[rec['review_queue_reason']],
        rec['source_content_sha256'],
    ))
    return rows


def parse_ledger(data, allowed):
    state = {}
    changes = 0
    for line in data.splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        sha = event.get('source_content_sha256')
        if not isinstance(sha, str) or sha not in allowed:
            raise RuntimeError('Unexpected V48 ledger candidate')
        previous = state.get(sha)
        revision = 1 if previous is None else previous['revision'] + 1
        if (event.get('schema') != SCHEMA
            or event.get('review_queue_reason') != allowed[sha]['review_queue_reason']
            or event.get('decision') not in VALID
            or event.get('revision') != revision
            or not isinstance(event.get('justification'), str)
            or not (12 <= len(event['justification'].strip()) <= 2000)
            or not isinstance(event.get('reviewed_at_utc'), str)
            or event.get('training_approved') is not False
            or event.get('dataset_split_assigned') is not False
            or event.get('factual_validation_complete') is not False
            or event.get('semantic_validation_complete') is not False):
            raise RuntimeError('Invalid V48 ledger entry')
        state[sha] = event
        changes += previous is not None
    return state, changes


def read_ledger(allowed):
    if not LEDGER.exists():
        return {}, 0
    if LEDGER.is_symlink():
        raise RuntimeError('Ledger is a symbolic link')
    return parse_ledger(LEDGER.read_text(encoding='utf-8'), allowed)


def save_event(row, decision, reason, expected_revision, allowed):
    flags = os.O_CREAT | os.O_RDWR | os.O_APPEND
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(LEDGER, flags, 0o600)
    try:
        with os.fdopen(fd, 'r+b', buffering=0) as stream:
            fd = -1
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            stream.seek(0)
            state, _ = parse_ledger(stream.read().decode('utf-8'), allowed)
            sha = row['source_content_sha256']
            revision = state[sha]['revision'] + 1 if sha in state else 1
            if revision != expected_revision:
                raise RuntimeError('Review state changed concurrently; decision not saved')
            event = {
                'schema': SCHEMA,
                'source_content_sha256': sha,
                'review_queue_reason': row['review_queue_reason'],
                'revision': revision,
                'decision': decision,
                'justification': reason.strip(),
                'reviewed_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                'semantic_validation_complete': False,
                'factual_validation_complete': False,
                'dataset_split_assigned': False,
                'training_approved': False,
            }
            stream.seek(0, os.SEEK_END)
            stream.write((json.dumps(event, ensure_ascii=False) + '\n').encode('utf-8'))
            stream.flush()
            os.fsync(stream.fileno())
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    finally:
        if fd != -1:
            os.close(fd)


def display(row, index):
    print('\n=== V48 LOCAL REVIEW: {} / 68 ==='.format(index))
    print('Queue reason:', row['review_queue_reason'])
    print('Public dataset:', row['source_dataset'])
    print('V44 category:', row['v44_category'] or 'NOT_SELECTED')
    print('Broad creative signal:', row['broad_creative_signal'])
    print('Identifier:', row['source_content_sha256'])
    print('Read every turn. Check continuity, factual claims, answer quality,')
    print('domain assignment, topic switching and leakage risks.\n')
    for idx, message in enumerate(row['messages_original'], 1):
        role = message['role'].upper()
        # Print the complete original text, escaping only terminal control characters.
        safe_text = ''.join(
            ch if ch in '\n\t' or (ord(ch) >= 32 and ord(ch) != 127)
            else '\\x{:02x}'.format(ord(ch))
            for ch in message['content']
        )
        print('--- TURN {} : {} ---\n{}\n'.format(idx, role, safe_text))


def main():
    parser = argparse.ArgumentParser(description='Human qualitative triage of public SmolTalk V46 queue; LOCAL ONLY')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--status', action='store_true', help='Show totals; no conversation text')
    group.add_argument('--next', action='store_true', help='Read and review next unreviewed conversation')
    group.add_argument('--revise', metavar='SHA_PREFIX', help='Reconsider an existing decision, preserving history')
    args = parser.parse_args()
    queue = load_queue()
    allowed = {r['source_content_sha256']: r for r in queue}
    state, revisions = read_ledger(allowed)
    if args.status:
        by = Counter(e['decision'] for e in state.values())
        print('##### SECTION RESULTS FOR ASSISTANT ######')
        print('V48_QUEUE_TOTAL:', len(queue))
        print('V48_REVIEWED:', len(state))
        print('V48_UNREVIEWED:', len(queue) - len(state))
        for decision in ('RETAIN', 'REJECT', 'HOLD'):
            print('V48_{}: {}'.format(decision, by[decision]))
        print('V48_REVISIONS:', revisions)
        print('TRAIN_APPROVED: 0')
        return
    if args.revise:
        possible = [r for r in queue if r['source_content_sha256'].startswith(args.revise)]
        if len(possible) != 1 or possible[0]['source_content_sha256'] not in state:
            raise RuntimeError('Revision requires a unique SHA prefix of an already reviewed item')
        row = possible[0]
    else:
        row = next((r for r in queue if r['source_content_sha256'] not in state), None)
        if row is None:
            print('All 68 cases have a human triage decision. No TRAIN approval implied.')
            return
    index = next(i for i, r in enumerate(queue, 1) if r['source_content_sha256'] == row['source_content_sha256'])
    display(row, index)
    sha = row['source_content_sha256']
    prior = state.get(sha)
    if prior:
        print('Previous decision:', prior['decision'], '- revision:', prior['revision'])
        print('Previous justification:', prior['justification'])
    action = input('Decision [RETAIN / REJECT / HOLD / SKIP]: ').strip().upper()
    if action in ('SKIP', 'Q', 'QUIT', ''):
        print('No decision recorded')
        return
    if action not in VALID:
        raise RuntimeError('Unsupported decision; no change written')
    reason = input('Justification (12-2000 characters; LOCAL ONLY): ').strip()
    if not (12 <= len(reason) <= 2000):
        raise RuntimeError('Justification too short/long; no change written')
    answer = input('Confirm local decision {}? [yes/no]: '.format(action)).strip().lower()
    if answer != 'yes':
        print('Cancelled; nothing recorded')
        return
    save_event(row, action, reason, 1 if prior is None else prior['revision']+1, allowed)
    print('Saved locally. No GitHub upload and NO TRAIN approval.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit('V48 REVIEW ERROR: {}'.format(exc))
