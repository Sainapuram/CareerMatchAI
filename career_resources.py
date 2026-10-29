"""CareerMatch AI learning resources and employer discovery.

These links are starting points, NOT verified course enrollments, credentials,
job vacancies, employer endorsements, or work-authorization guarantees.
No resume data is transmitted by this module.
"""
from urllib.parse import quote

# Curated provider home/search pages; availability and prices can change.
LEARNING_PROVIDERS = (
    ("Microsoft Learn", "https://learn.microsoft.com/en-us/search/?terms="),
    ("Coursera", "https://www.coursera.org/search?query="),
)

# Employer-owned career portals. These are discovery links, not live vacancies.
EMPLOYER_PORTALS = (
    ("Microsoft", "https://careers.microsoft.com/"),
    ("IBM", "https://www.ibm.com/careers"),
    ("Accenture", "https://www.accenture.com/us-en/careers"),
    ("Deloitte", "https://www.deloitte.com/us/en/careers.html"),
    ("Amazon", "https://www.amazon.jobs/"),
)


def learning_resources(skills, max_skills=3):
    """Return deduplicated topic searches; do not imply course verification."""
    result, seen = [], set()
    for skill in skills or []:
        if not isinstance(skill, str):
            continue
        skill = skill.strip()[:80]
        if not skill or skill.casefold() in seen:
            continue
        seen.add(skill.casefold())
        result.append({
            "topic": skill,
            "resources": [
                {"provider": provider, "url": prefix + quote(skill)}
                for provider, prefix in LEARNING_PROVIDERS
            ],
        })
        if len(result) >= max_skills:
            break
    return result


def official_employer_portals():
    """Return official company career portals, NOT current job postings."""
    return [{"employer": name, "url": url} for name, url in EMPLOYER_PORTALS]
