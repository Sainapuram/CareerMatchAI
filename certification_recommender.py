"""CareerMatch AI: occupation-agnostic credential selection.

Only documented credential skill coverage is used. A missing profile skill is
an unconfirmed skill, not proof that the user lacks it.
"""


def normalize_name(value):
    return " ".join(str(value).strip().casefold().split())


def identify_learning_needs(candidate_skills, occupation_skills, approved_equivalences=None):
    from src.skill_gap import analyze_skill_gap

    result = analyze_skill_gap(
        candidate_skills,
        occupation_skills,
        approved_equivalences=approved_equivalences,
    )
    return result["missing_skills"]


def select_certification(
    candidate_skills,
    occupation_skills,
    catalog,
    career_category=None,  # Retained for backward compatibility; not used.
    approved_equivalences=None,
):
    """Return one credential with an exact documented skill-name overlap.

    Uses the selected occupation's skills, not hardcoded career categories.
    Does not infer proficiency from the number of skills. Prefers free options
    only after comparing relevant skill coverage.
    """
    needs = {
        normalize_name(skill)
        for skill in identify_learning_needs(
            candidate_skills, occupation_skills, approved_equivalences
        )
    }
    if not needs:
        return None

    candidates = []
    for credential in catalog:
        if not isinstance(credential, dict):
            continue
        if not credential.get("name") or not credential.get("official_url"):
            continue
        covered = {
            normalize_name(skill)
            for skill in credential.get("skills", [])
        }
        overlap = needs & covered
        if not overlap:
            continue
        candidates.append((
            -len(overlap),
            credential.get("cost_type") != "free",
            normalize_name(credential["name"]),
            credential,
        ))

    if not candidates:
        return None
    candidates.sort(key=lambda item: item[:3])
    return candidates[0][3]


if __name__ == "__main__":
    demo_catalog = [
        {"name": "Example Excel course", "skills": ["Microsoft Excel"],
         "cost_type": "free", "official_url": "https://example.org"},
        {"name": "Example unrelated course", "skills": ["Photography"],
         "cost_type": "free", "official_url": "https://example.org"},
    ]
    print("Relevant:", select_certification(
        ["Python"], ["Python", "Microsoft Excel"], demo_catalog
    )["name"])
    print("Unrelated:", select_certification(
        ["Python"], ["Python", "Photography skills"], demo_catalog
    ))
