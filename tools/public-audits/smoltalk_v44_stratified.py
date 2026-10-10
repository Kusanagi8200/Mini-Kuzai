#!/usr/bin/env python3
"""Phase 03 V44: deterministic, local-only, stratified SmolTalk review candidates.

Class labels are heuristics and carry no factual or TRAIN approval. All source
texts and review artifacts remain outside the public Git working tree. The only
stdout intended for gogit_public.py is an allowlisted numeric aggregate report.
"""

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/root/Mini-Kuzai/data/external/smol-smoltalk')
SOURCE = ROOT / 'candidates/external-candidate-pool-v0.4.jsonl'
OUTPUT = ROOT / 'review/stratified-candidates-v44.jsonl'
REPORT = ROOT / 'review/stratified-audit-v44.json'
SAMPLES = ROOT / 'review/stratified-samples-v44.txt'

SOURCE_QUOTAS = {
    'smol-magpie-ultra-short': 720,
    'openhermes-50k': 330,
    'self-oss-instruct': 100,
    'explore-instruct-rewrite': 50,
}
CATEGORY_QUOTAS = {
    'FOLLOWUP': 90,
    'WRITING': 160,
    'CREATIVE': 130,
    'FACTUAL_QA': 180,
    'MATHEMATICS': 140,
    'PROGRAMMING': 150,
    'PRACTICAL_ADVICE': 150,
    'GENERAL_OTHER': 200,
}
TARGET = sum(CATEGORY_QUOTAS.values())
assert TARGET == sum(SOURCE_QUOTAS.values()) == 1200

WORDS = re.compile(r"[a-z]{3,}")
STOP = set('the and for with that this from have has was were are you your can could would should about into then than they them their what when where which how why more some other also just make made please like does'.split())
REFER = re.compile(r'\b(?:you (?:said|wrote|mentioned|added|used)|your (?:answer|response|explanation|previous|last|wording|version)|(?:this|that|the) (?:answer|response|paragraph|sentence|draft|version|wording|explanation|text)|(?:previous|earlier|above) (?:answer|response|text|sentence|paragraph)|(?:make|keep|rewrite|rephrase|shorten|expand|remove|change|improve) (?:it|that|this)|instead|again|as before)\b',re.I)
PATTERNS = (
    ('PROGRAMMING', re.compile(r'\b(?:python|javascript|typescript|java code|c\+\+|coding|programming|write (?:a |an )?(?:function|program|script)|code snippet|implement (?:a |an )?(?:function|algorithm)|debug|sql query|bash script)\b',re.I)),
    ('MATHEMATICS', re.compile(r'\b(?:derivative|integral|equation|probability|algebra|matrix|matrices|calculus|theorem|polynomial|trigonometry|simplify the expression|solve for x|calculate the|find the value of|arithmetic sequence)\b',re.I)),
    ('CREATIVE', re.compile(r'\b(?:write (?:a |an )?(?:story|poem|novel|song)|short story|fiction|fictional character|fairy tale|creative writing|character development|plot twist|poetry)\b',re.I)),
    ('WRITING', re.compile(r'\b(?:rewrite|rephrase|edit (?:this|the|my|a)|edit and improve|paragraph|essay|grammar|sentence|proofread|cover letter|formal tone|tone of (?:this|the)|writing style|letter of|email draft|transition phrase)\b',re.I)),
    ('PRACTICAL_ADVICE', re.compile(r'\b(?:what should i|how can i|i need advice|give me advice|recommend (?:a|some|the)|how should i|best way to|help me decide|what do you suggest|i am struggling with|i feel|manage my|deal with)\b',re.I)),
    ('FACTUAL_QA', re.compile(r'\b(?:what is|what are|what causes|how does|how do|why does|why do|who (?:was|is)|when (?:was|did)|explain the|describe the|history of|difference between|what were)\b',re.I)),
)


def tokens(text):
    return set(w for w in WORDS.findall(text.lower()) if w not in STOP)


def segment(messages, source):
    first = messages[0]['content'][:1500]
    if source == 'self-oss-instruct':
        return 'PROGRAMMING', False
    if source == 'explore-instruct-rewrite':
        return 'WRITING', False
    followup = len(messages) >= 6 and bool(REFER.search(messages[2]['content'])) and bool(REFER.search(messages[4]['content']))
    # Follow-up quality is unverified; lexical dependency offers a review hint.
    if followup:
        overlap2 = len(tokens(messages[2]['content']) & tokens(messages[1]['content']))
        overlap3 = len(tokens(messages[4]['content']) & tokens(messages[3]['content']))
        if overlap2 >= 1 and overlap3 >= 1:
            return 'FOLLOWUP', True
    for label, pattern in PATTERNS:
        if pattern.search(first):
            return label, followup
    return 'GENERAL_OTHER', followup


def score(row):
    return hashlib.sha256(('MINI-KUZAI-V44-PUBLIC-STRATIFY|' + row['content_sha256']).encode('ascii')).hexdigest()


def main():
    if not SOURCE.is_file():
        raise RuntimeError('Source SmolTalk v0.4 missing')
    if any(p.exists() for p in (OUTPUT, REPORT, SAMPLES)):
        raise RuntimeError('V44 outputs already exist; refusing to overwrite')
    groups = defaultdict(lambda: defaultdict(list))
    available = Counter()
    seen = set()
    sources_seen = Counter()
    records = 0
    with SOURCE.open(encoding='utf-8') as stream:
        for line in stream:
            if not line.strip():
                continue
            rec = json.loads(line)
            records += 1
            source = rec.get('source')
            messages = rec.get('messages')
            fingerprint = rec.get('content_sha256')
            if (source not in SOURCE_QUOTAS or not isinstance(messages, list)
                or len(messages) not in (2, 4, 6)
                or [m.get('role') for m in messages] != ['user','assistant'] * (len(messages) // 2)
                or any(not isinstance(m.get('content'),str) or not m['content'].strip() for m in messages)
                or not isinstance(fingerprint,str) or not re.fullmatch(r'[0-9a-f]{64}',fingerprint)
                or fingerprint in seen):
                raise RuntimeError('Invalid or duplicated source record')
            seen.add(fingerprint)
            sources_seen[source] += 1
            category, refer = segment(messages, source)
            record = {'source':source, 'content_sha256':fingerprint,
                      'heuristic_category':category, 'followup_heuristic':refer,
                      'messages':messages, 'source_record':rec}
            groups[category][source].append(record)
            available[category] += 1
    if records != 8000 or sources_seen != {
        'smol-magpie-ultra-short':5000,'openhermes-50k':1500,
        'self-oss-instruct':1000,'explore-instruct-rewrite':500,
    }:
        raise RuntimeError('Unexpected reservoir size or source mix')

    for per_source in groups.values():
        for rows in per_source.values():
            rows.sort(key=score)
    used_source = Counter()
    selected_by_category = Counter()
    picked = []

    def take(category, source, limit):
        batch = groups[category][source]
        n = min(limit, len(batch), CATEGORY_QUOTAS[category] - selected_by_category[category],
                SOURCE_QUOTAS[source] - used_source[source])
        if n > 0:
            picked.extend(batch[:n])
            del batch[:n]
            used_source[source] += n
            selected_by_category[category] += n

    # Reserve specialized sources before consuming the shared domain quotas.
    take('PROGRAMMING','self-oss-instruct',100)
    take('WRITING','explore-instruct-rewrite',50)

    remaining_sources = ('smol-magpie-ultra-short','openhermes-50k')
    cats = list(CATEGORY_QUOTAS)
    # Prioritize categories with scarce supply relative to their target.
    cats.sort(key=lambda c: (available[c] / CATEGORY_QUOTAS[c], c))
    for category in cats:
        while selected_by_category[category] < CATEGORY_QUOTAS[category]:
            eligible = [s for s in remaining_sources
                        if groups[category][s] and used_source[s] < SOURCE_QUOTAS[s]]
            if not eligible:
                break
            # Equalize the used/target source ratios; ties deterministic.
            src = min(eligible, key=lambda s:(used_source[s] / SOURCE_QUOTAS[s], s))
            take(category, src, 1)

    result = []
    for r in picked:
        result.append({
            'schema':'mini-kuzai.external-v44-stratified-review.local',
            'source':'SmolTalk v0.4',
            'source_dataset':r['source'],
            'source_content_sha256':r['content_sha256'],
            'heuristic_category':r['heuristic_category'],
            'followup_heuristic':r['followup_heuristic'],
            'messages':r['messages'],
            'review_status':'HEURISTIC_SELECTION_ONLY',
            'factual_validation_complete':False,
            'semantic_validation_complete':False,
            'dataset_split_assigned':False,
            'training_approved':False,
        })
    assert len({r['source_content_sha256'] for r in result}) == len(result)
    assert all(not r['training_approved'] for r in result)
    report = {
        'step':'PHASE03-SMOLTALK-V44',
        'candidate_only': True,
        'target_records':TARGET,
        'selected_records':len(result),
        'target_by_category':CATEGORY_QUOTAS,
        'available_by_heuristic_category':dict(available),
        'selected_by_heuristic_category':dict(selected_by_category),
        'underfilled_categories': {c:q-selected_by_category[c] for c,q in CATEGORY_QUOTAS.items() if selected_by_category[c]<q},
        'target_by_source':SOURCE_QUOTAS,
        'selected_by_source':dict(used_source),
        'source_shortfalls': {s:q-used_source[s] for s,q in SOURCE_QUOTAS.items() if used_source[s]<q},
        'selected_turn_structure':dict(Counter(len(x['messages']) for x in result)),
        'semantic_review_complete':False,
        'training_approved':False,
        'tokenizer_vocabulary_finalized':False,
        'note':'All classes are keyword/context heuristics; the selection is not TRAIN-ready.',
    }
    output_lines = ''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in result)
    # Deterministic sample: 2 full conversations per category, locally only.
    sample_lines = ['V44 LOCAL QUALITY SAMPLES - SOURCE TEXT, DO NOT PUSH','']
    for category in CATEGORY_QUOTAS:
        subset = [r for r in result if r['heuristic_category']==category][:2]
        for r in subset:
            sample_lines.append('=== '+category+' ===')
            for m in r['messages']:
                sample_lines.append(m['role'].upper()+': '+m['content']+'\n')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(output_lines,encoding='utf-8')
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    SAMPLES.write_text('\n'.join(sample_lines)+'\n',encoding='utf-8')
    # Only numeric SmolTalk aggregates below the marker may be published.
    public = Counter({
        'TOTAL_SOURCE':records,
        'TOTAL_CANDIDATS':len(result),
        'SINGLE_TURN':sum(len(r['messages'])==2 for r in result),
        'MULTITURN':sum(len(r['messages'])>2 for r in result),
        'FOLLOWUP':selected_by_category['FOLLOWUP'],
        'WRITING':selected_by_category['WRITING'],
        'CREATIVE':selected_by_category['CREATIVE'],
        'FACTUAL_QA':selected_by_category['FACTUAL_QA'],
        'MATHEMATICS':selected_by_category['MATHEMATICS'],
        'PROGRAMMING':selected_by_category['PROGRAMMING'],
        'OTHER':selected_by_category['PRACTICAL_ADVICE']+selected_by_category['GENERAL_OTHER'],
    })
    print('##### SECTION RESULTS FOR ASSISTANT ######')
    for key,val in sorted(public.items()):
        print(f'{key}: {val}')


if __name__ == '__main__':
    main()
