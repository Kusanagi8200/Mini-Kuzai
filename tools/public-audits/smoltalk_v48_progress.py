#!/usr/bin/env python3
"""V48 numeric-only publication of human review progress on public SmolTalk.

Reads ONLY the V46 public-source review queue and the local V48 review ledger.
No conversation, identifier, timestamp, or justification is ever printed.
No model TRAIN approval is derived from a human triage decision.
"""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path('/root/Mini-Kuzai/data/external/smol-smoltalk/review')
QUEUE = ROOT / 'v46-manual-review-queue.jsonl'
LEDGER = ROOT / 'v48-human-review-ledger.jsonl'
SCHEMA = 'mini-kuzai.v48.human-review-event.v1'
VALID = {'RETAIN', 'REJECT', 'HOLD'}
GROUPS = {'RELABEL': 12, 'RESCUE': 24, 'BASE': 32}
SHA = re.compile(r'[0-9a-f]{64}\Z')


def main():
    if not QUEUE.is_file():
        raise RuntimeError('Missing V46 public SmolTalk queue')
    queue = {}
    counts = Counter()
    with QUEUE.open(encoding='utf-8') as src:
        for line in src:
            if not line.strip():
                continue
            rec = json.loads(line)
            sha = rec.get('source_content_sha256')
            reason = rec.get('review_queue_reason')
            if (not isinstance(sha, str) or not SHA.fullmatch(sha)
                or sha in queue or reason not in GROUPS
                or rec.get('review_decision') != 'UNREVIEWED'
                or rec.get('training_approved') is not False
                or rec.get('dataset_split_assigned') is not False):
                raise RuntimeError('Invalid V46 queue')
            queue[sha] = reason
            counts[reason] += 1
    if len(queue) != 68 or counts != GROUPS:
        raise RuntimeError('V46 queue distribution changed')

    latest = {}
    revisions = 0
    if LEDGER.is_symlink():
        raise RuntimeError('Ledger path must not be a symbolic link')
    if LEDGER.exists():
        with LEDGER.open(encoding='utf-8') as src:
            for line in src:
                if not line.strip():
                    continue
                event = json.loads(line)
                sha = event.get('source_content_sha256')
                if not isinstance(sha, str) or sha not in queue:
                    raise RuntimeError('Foreign candidate in V48 ledger')
                prior = latest.get(sha)
                expected_revision = prior['revision'] + 1 if prior else 1
                justification = event.get('justification')
                if (event.get('schema') != SCHEMA
                    or event.get('review_queue_reason') != queue[sha]
                    or event.get('decision') not in VALID
                    or event.get('revision') != expected_revision
                    or not isinstance(justification, str)
                    or not (12 <= len(justification.strip()) <= 2000)
                    or not isinstance(event.get('reviewed_at_utc'), str)
                    or event.get('training_approved') is not False
                    or event.get('dataset_split_assigned') is not False
                    or event.get('semantic_validation_complete') is not False
                    or event.get('factual_validation_complete') is not False):
                    raise RuntimeError('Invalid ledger entry')
                latest[sha] = event
                revisions += bool(prior)

    decisions = Counter(e['decision'] for e in latest.values())
    reviewed_by_reason = Counter(queue[sha] for sha in latest)
    reviewed = len(latest)
    if sum(decisions.values()) != reviewed or reviewed > 68:
        raise RuntimeError('V48 review totals inconsistent')
    public = {
        'TOTAL_CANDIDATS': 68,
        'V48_QUEUE_TOTAL': 68,
        'V48_REVIEWED': reviewed,
        'V48_UNREVIEWED': 68 - reviewed,
        'V48_PRIORITY_REVIEWED': reviewed_by_reason['RELABEL'] + reviewed_by_reason['RESCUE'],
        'V48_BASELINE_REVIEWED': reviewed_by_reason['BASE'],
        'V48_RETAINED': decisions['RETAIN'],
        'V48_REJECTED': decisions['REJECT'],
        'V48_HELD': decisions['HOLD'],
        'V48_REVISIONS': revisions,
        'V48_TRAIN_APPROVED': 0,
    }
    print('##### SECTION RESULTS FOR ASSISTANT ######')
    for key, value in sorted(public.items()):
        print(f'{key}: {value}')


if __name__ == '__main__':
    main()
