"""CareerMatch AI: conservative, user-approved skill equivalence matching."""
import csv
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

ESCO_PATH = Path(__file__).resolve().parents[1] / 'data' / 'raw' / 'esco' / 'skills_en.csv'


def normalize_skill(skill):
    if not isinstance(skill, str):
        raise TypeError('Each skill must be a string')
    return re.sub(r'\s+', ' ', skill.strip()).casefold()


@lru_cache(maxsize=4)
def _esco_concepts(csv_path):
    label_to_uris = defaultdict(set)
    with open(csv_path, encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not {'conceptUri', 'preferredLabel', 'altLabels'}.issubset(reader.fieldnames or []):
            raise ValueError('ESCO CSV is missing required columns')
        for row in reader:
            if row.get('status') and row['status'] != 'released':
                continue
            uri = (row.get('conceptUri') or '').strip()
            if not uri:
                continue
            labels = [row.get('preferredLabel') or '']
            labels.extend((row.get('altLabels') or '').splitlines())
            for label in labels:
                key = normalize_skill(label)
                if key:
                    label_to_uris[key].add(uri)
    return {label: next(iter(uris)) for label, uris in label_to_uris.items() if len(uris) == 1}


def extract_occupation_skills(occupation):
    skills = []
    for column, field in (('Essential Skills', 'Element Name'), ('Software Skills', 'Workplace Example')):
        entries = occupation.get(column, [])
        if isinstance(entries, list):
            for item in entries:
                if isinstance(item, dict):
                    value = item.get(field)
                    if isinstance(value, str) and value.strip():
                        skills.append(value.strip())
    unique = {}
    for skill in skills:
        unique.setdefault(normalize_skill(skill), skill)
    return list(unique.values())


def possible_acronym_equivalence(candidate, required):
    candidate_key = normalize_skill(candidate)
    required_key = normalize_skill(required)
    if not re.fullmatch(r'[a-z]{2,6}', candidate_key):
        return False
    words = re.findall(r'[a-z]+', required_key)
    return (len(words) >= 3 and words[-1] == candidate_key
            and ''.join(word[0] for word in words[:-1]) == candidate_key)


def analyze_skill_gap(candidate_skills, occupation_skills, esco_path=None, approved_equivalences=None):
    """Exact names match automatically; ESCO/acronym suggestions require approval.

    Approvals are directional (candidate skill, O*NET required skill).
    The caller owns storage of approved_equivalences across careers.
    """
    if not isinstance(candidate_skills, (list, tuple, set)):
        raise TypeError('candidate_skills must be a collection')
    if not isinstance(occupation_skills, (list, tuple, set)):
        raise TypeError('occupation_skills must be a collection')

    candidate = {}
    for skill in candidate_skills:
        key = normalize_skill(skill)
        if key:
            candidate.setdefault(key, skill.strip())
    required = {}
    for skill in occupation_skills:
        key = normalize_skill(skill)
        if key:
            required.setdefault(key, skill.strip())

    approved = set()
    for pair in approved_equivalences or []:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError('Each approved equivalence must contain two skills')
        approved.add((normalize_skill(pair[0]), normalize_skill(pair[1])))

    path = Path(esco_path) if esco_path is not None else ESCO_PATH
    concepts = _esco_concepts(str(path.resolve())) if path.is_file() else {}

    matched, missing, possible_matches, applied_approvals = [], [], [], []
    for required_key, required_name in required.items():
        if required_key in candidate:
            matched.append(required_name)
            continue

        approved_candidate = next((key for key in candidate if (key, required_key) in approved), None)
        if approved_candidate is not None:
            matched.append(required_name)
            applied_approvals.append({'candidate_skill': candidate[approved_candidate],
                                      'required_skill': required_name})
            continue

        missing.append(required_name)
        for candidate_key, candidate_name in candidate.items():
            same_concept = (candidate_key != required_key and
                            candidate_key in concepts and required_key in concepts and
                            concepts[candidate_key] == concepts[required_key])
            acronym = possible_acronym_equivalence(candidate_name, required_name)
            if same_concept or acronym:
                possible_matches.append({'candidate_skill': candidate_name,
                                         'required_skill': required_name})

    return {
        'matched_skills': matched,
        'missing_skills': missing,
        'matched_count': len(matched),
        'missing_count': len(missing),
        'skill_coverage_percent': round(100 * len(matched) / len(required), 2) if required else 0.0,
        'possible_matches': possible_matches,
        'approved_equivalences': applied_approvals,
    }


if __name__ == '__main__':
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        esco_file = Path(temp) / 'skills.csv'
        with esco_file.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=['conceptUri', 'preferredLabel', 'altLabels'])
            writer.writeheader()
            writer.writerow({'conceptUri': 'urn:example:clinical',
                             'preferredLabel': 'clinical reports',
                             'altLabels': 'clinical documentation'})
        cases = [
            ('SQL unapproved', ['Python', 'SQL'], ['Python', 'Structured query language SQL'], []),
            ('SQL approved', ['Python', 'SQL'], ['Python', 'Structured query language SQL'],
             [('SQL', 'Structured query language SQL')]),
            ('ESCO unapproved', ['clinical documentation'], ['clinical reports'], []),
            ('ESCO approved', ['clinical documentation'], ['clinical reports'],
             [('clinical documentation', 'clinical reports')]),
            ('Unrelated', ['Python'], ['Mathematics'], []),
        ]
        for title, candidate, required, approvals in cases:
            result = analyze_skill_gap(candidate, required, esco_path=esco_file,
                                       approved_equivalences=approvals)
            print(f"{title}: matched={result['matched_skills']}; "
                  f"possible={result['possible_matches']}; "
                  f"coverage={result['skill_coverage_percent']}%")
