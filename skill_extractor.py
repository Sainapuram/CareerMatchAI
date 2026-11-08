"""CareerMatch AI: O*NET + ESCO skill detection with reviewable suggestions.

Direct matches are explicit mentions of an O*NET name or ESCO preferred label.
Suggested matches arise from ESCO alternative labels and require user review.
Neither category verifies proficiency.
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

from src.matching import load_occupation_profiles

ESCO_CSV = Path(__file__).resolve().parent / 'data' / 'raw' / 'esco' / 'skills_en.csv'
TOKEN_PATTERN = re.compile(r"[\w]+(?:[.+#-][\w]+)*|[+#]+", re.UNICODE)


def normalize_skill(value):
    return ' '.join(str(value).strip().casefold().split())


def build_skill_vocabulary(profiles):
    """Collect distinct O*NET skill and software names."""
    names = {}
    fields = {'Essential Skills': 'Element Name', 'Software Skills': 'Workplace Example'}
    for _, occupation in profiles.iterrows():
        for column, field in fields.items():
            entries = occupation.get(column, [])
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                name = entry.get(field)
                if isinstance(name, str) and name.strip():
                    names.setdefault(normalize_skill(name), name.strip())
    return sorted(names.values(), key=str.casefold)


def load_esco_skills(path=ESCO_CSV):
    """Load ESCO skill labels and alternate labels."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'ESCO skills CSV not found: {path}\nPlace skills_en.csv in data/raw/esco/.')
    skills = []
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        required = {'conceptUri', 'preferredLabel', 'altLabels'}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'ESCO CSV missing columns: {sorted(missing)}')
        for row in reader:
            name = (row.get('preferredLabel') or '').strip()
            if not name or (row.get('status') or 'released').strip().casefold() != 'released':
                continue
            aliases = [a.strip() for a in (row.get('altLabels') or '').splitlines() if a.strip()]
            skills.append({'name': name, 'aliases': aliases, 'uri': row['conceptUri']})
    return skills


def tokenize(text):
    return [m.group().casefold() for m in TOKEN_PATTERN.finditer(text)]


def _token_matches(text):
    """Keep source offsets so suggestions can show the exact résumé wording."""
    return list(TOKEN_PATTERN.finditer(text))


def build_skill_index(profiles, esco_path=ESCO_CSV):
    """Build a searchable trie with direct/alias match provenance.

    Ambiguous terms are excluded. Preferred-label matches take priority over
    alternative labels. Short one-token terms are excluded as before.
    """
    direct = defaultdict(set)
    aliases = defaultdict(set)
    onet = build_skill_vocabulary(profiles)
    esco = load_esco_skills(esco_path)
    for name in onet:
        direct[tuple(tokenize(name))].add(name)
    for record in esco:
        direct[tuple(tokenize(record['name']))].add(record['name'])
        for alias in record['aliases']:
            aliases[tuple(tokenize(alias))].add(record['name'])

    trie = {}
    indexed = 0
    ambiguous = 0
    for tokens in direct.keys() | aliases.keys():
        if not tokens or (len(tokens) == 1 and len(tokens[0]) < 3):
            continue
        # Do not silently choose between multiple distinct skills.
        if tokens in direct:
            names = direct[tokens]
            kind = 'direct'
        else:
            names = aliases[tokens]
            kind = 'suggested'
        if len(names) != 1:
            ambiguous += 1
            continue
        node = trie
        for token in tokens:
            node = node.setdefault(token, {})
        node['_match'] = {'skill': next(iter(names)), 'type': kind}
        indexed += 1
    return {
        'trie': trie,
        'onet_skill_count': len(onet),
        'esco_skill_count': len(esco),
        'indexed_terms': indexed,
        'ambiguous_terms_skipped': ambiguous,
    }


def extract_skills_with_evidence(text, skill_index):
    """Return {'direct': [...], 'suggested': [...]} with evidence.

    Each entry is {'skill': str, 'matched_text': str, 'match_type': str}.
    Results are candidates for user confirmation, not validated abilities.
    """
    result = {'direct': {}, 'suggested': {}}
    if not isinstance(text, str) or not text.strip():
        return {'direct': [], 'suggested': []}
    matches = _token_matches(text)
    tokens = [m.group().casefold() for m in matches]
    trie = skill_index['trie']
    i = 0
    while i < len(tokens):
        node = trie
        best = None
        j = i
        while j < len(tokens) and tokens[j] in node:
            node = node[tokens[j]]
            j += 1
            if '_match' in node:
                best = (j, node['_match'])
        if best is None:
            i += 1
            continue
        end, record = best
        evidence = text[matches[i].start():matches[end - 1].end()]
        kind = record['type']
        name = record['skill']
        key = normalize_skill(name)
        result[kind].setdefault(key, {
            'skill': name,
            'matched_text': evidence,
            'match_type': kind,
        })
        i = end

    # A direct mention of the same skill overrides a suggested mention.
    for key in result['direct']:
        result['suggested'].pop(key, None)
    return {
        kind: sorted(entries.values(), key=lambda item: item['skill'].casefold())
        for kind, entries in result.items()
    }


def extract_skills(text, skill_index):
    """Backward-compatible flat list of candidates (NOT confirmed skills)."""
    result = extract_skills_with_evidence(text, skill_index)
    names = {normalize_skill(item['skill']): item['skill']
             for kind in ('direct', 'suggested') for item in result[kind]}
    return sorted(names.values(), key=str.casefold)


if __name__ == '__main__':
    index = build_skill_index(load_occupation_profiles())
    print('O*NET vocabulary names:', index['onet_skill_count'])
    print('ESCO skills:', index['esco_skill_count'])
    print('Indexed skill terms:', index['indexed_terms'])
    print('Ambiguous terms skipped:', index['ambiguous_terms_skipped'])
    examples = [
        'Experienced with Python, Microsoft Excel, Tableau, Git and project management.',
        'Provided patient care, maintained medical records and supported clinical documentation.',
        'Developed REST APIs using Python, Docker, Git and cloud computing technologies.',
    ]
    for sample in examples:
        print('\nResume:', sample)
        found = extract_skills_with_evidence(sample, index)
        print('Direct:', [(x['skill'], x['matched_text']) for x in found['direct']])
        print('Suggested (review required):',
              [(x['skill'], x['matched_text']) for x in found['suggested']])
