
"""
CareerMatch AI - Skill Gap Analysis

Compare candidate skills with occupation skills.
Identify matched and missing skills.
"""

import re


def normalize_skill(skill):
    """Normalize skill names for comparison."""
    if not isinstance(skill, str):
        raise TypeError("Each skill must be a string")

    return re.sub(r"\s+", " ", skill.strip()).casefold()


def extract_occupation_skills(occupation):
    """
    Extract essential skills and software skills
    from an O*NET occupation profile.
    """
    skills = []

    essential_skills = occupation.get("Essential Skills", [])
    software_skills = occupation.get("Software Skills", [])

    if isinstance(essential_skills, list):
        for item in essential_skills:
            if isinstance(item, dict):
                skill = item.get("Element Name")
                if isinstance(skill, str) and skill.strip():
                    skills.append(skill.strip())

    if isinstance(software_skills, list):
        for item in software_skills:
            if isinstance(item, dict):
                skill = item.get("Workplace Example")
                if isinstance(skill, str) and skill.strip():
                    skills.append(skill.strip())

    # Remove duplicates while preserving order
    unique_skills = {}

    for skill in skills:
        key = normalize_skill(skill)
        if key:
            unique_skills.setdefault(key, skill)

    return list(unique_skills.values())


def analyze_skill_gap(candidate_skills, occupation_skills):
    """
    Compare candidate skills against occupation skills.

    Returns matched skills, missing skills, and coverage.
    """

    if not isinstance(candidate_skills, (list, tuple, set)):
        raise TypeError("candidate_skills must be a collection of strings")

    if not isinstance(occupation_skills, (list, tuple, set)):
        raise TypeError("occupation_skills must be a collection of strings")

    candidate_set = {
        normalize_skill(skill)
        for skill in candidate_skills
        if normalize_skill(skill)
    }

    required = {}

    for skill in occupation_skills:
        key = normalize_skill(skill)
        if key:
            required.setdefault(key, skill.strip())

    matched = [
        skill
        for key, skill in required.items()
        if key in candidate_set
    ]

    missing = [
        skill
        for key, skill in required.items()
        if key not in candidate_set
    ]

    coverage = (
        round(len(matched) / len(required) * 100, 2)
        if required else 0.0
    )

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "matched_count": len(matched),
        "missing_count": len(missing),
        "skill_coverage_percent": coverage,
    }
