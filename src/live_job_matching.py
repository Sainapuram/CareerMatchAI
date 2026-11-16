
import re
import html
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clean_text(value):
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]*>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def official_url(url, provider):
    """Accept only HTTPS links on the provider's official job domain."""
    parsed = urlparse(str(url or ""))
    host = (parsed.hostname or "").lower()

    if parsed.scheme != "https":
        return False

    if provider == "greenhouse":
        return (
            host == "greenhouse.io"
            or host.endswith(".greenhouse.io")
        )

    if provider == "lever":
        return (
            host == "lever.co"
            or host.endswith(".lever.co")
        )

    return False


def fetch_greenhouse(company, board):
    endpoint = (
        f"https://boards-api.greenhouse.io/v1/boards/"
        f"{board}/jobs"
    )

    response = requests.get(
        endpoint,
        params={"content": "true"},
        timeout=20,
    )
    response.raise_for_status()

    jobs = []

    for item in response.json().get("jobs", []):
        url = item.get("absolute_url", "")

        if not official_url(url, "greenhouse"):
            continue

        description = clean_text(item.get("content"))

        if not description:
            continue

        location = item.get("location") or {}

        jobs.append({
            "id": f"greenhouse:{board}:{item.get('id')}",
            "title": item.get("title", ""),
            "company": company,
            "location": location.get("name", ""),
            "description": description,
            "url": url,
            "source": "Greenhouse",
            "updated_at": item.get("updated_at"),
        })

    return jobs


def fetch_lever(company, board):
    endpoint = (
        f"https://api.lever.co/v0/postings/{board}"
    )

    response = requests.get(
        endpoint,
        params={"mode": "json"},
        timeout=20,
    )
    response.raise_for_status()

    jobs = []

    for item in response.json():
        url = item.get("hostedUrl", "")

        if not official_url(url, "lever"):
            continue

        description = clean_text(
            item.get("descriptionPlain")
            or item.get("description")
        )

        for section in item.get("lists", []):
            description += " " + clean_text(
                section.get("content")
            )

        if not description.strip():
            continue

        categories = item.get("categories") or {}

        jobs.append({
            "id": f"lever:{board}:{item.get('id')}",
            "title": item.get("text", ""),
            "company": company,
            "location": categories.get("location", ""),
            "description": description,
            "url": url,
            "source": "Lever",
            "updated_at": item.get("createdAt"),
        })

    return jobs


def fetch_employer_jobs(employers):
    """
    employers is a list of dictionaries:
    company, provider, board

    Retrieve current postings from configured official APIs.
    No job titles or career families are hardcoded.
    """
    jobs = []
    errors = []
    seen = set()

    for employer in employers:
        company = employer["company"]
        provider = employer["provider"].lower()
        board = employer["board"]

        try:
            if provider == "greenhouse":
                retrieved = fetch_greenhouse(company, board)
            elif provider == "lever":
                retrieved = fetch_lever(company, board)
            else:
                errors.append(
                    f"{company}: unsupported provider"
                )
                continue

            for job in retrieved:
                if job["id"] not in seen:
                    seen.add(job["id"])
                    job["checked_at"] = (
                        datetime.now(timezone.utc).isoformat()
                    )
                    jobs.append(job)

        except (requests.RequestException, ValueError) as exc:
            errors.append(
                f"{company}: {type(exc).__name__}"
            )

    return jobs, errors


def extract_minimum_experience(description):
    """
    Extract a clearly stated minimum number of years.
    None means the requirement could not be determined.
    """
    patterns = [
        r"\bminimum(?: of)?\s+(\d{1,2})\+?\s+years?",
        r"\bat least\s+(\d{1,2})\+?\s+years?",
        r"\b(\d{1,2})\+?\s+years?\s+of\s+"
        r"(?:relevant |professional |work )?experience\b",
    ]

    text = clean_text(description).lower()

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    return None


def rank_jobs(
    jobs,
    candidate_skills,
    occupation_profiles,
    experience_years=0,
    top_n=5,
    minimum_similarity=0.08,
):
    """
    Compare actual job descriptions with candidate skills
    and O*NET occupation text.

    occupation_profiles: list of strings representing
    the top recommended O*NET occupations.

    Similarity is a ranking signal, not hiring probability.
    """
    if not jobs:
        return []

    skills_text = " ".join(
        str(skill) for skill in candidate_skills
    )

    occupation_text = " ".join(
        str(profile) for profile in occupation_profiles
    )

    if not skills_text.strip() and not occupation_text.strip():
        return []

    documents = [
        skills_text,
        occupation_text,
    ]

    documents.extend(
        clean_text(job["title"] + " " + job["description"])
        for job in jobs
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=15000,
        sublinear_tf=True,
    )

    matrix = vectorizer.fit_transform(documents)

    skill_scores = cosine_similarity(
        matrix[2:], matrix[0:1]
    ).ravel()

    occupation_scores = cosine_similarity(
        matrix[2:], matrix[1:2]
    ).ravel()

    results = []

    for index, job in enumerate(jobs):
        skill_score = float(skill_scores[index])
        occupation_score = float(occupation_scores[index])

        # Both signals contribute to the ranking.
        score = (
            0.7 * skill_score
            + 0.3 * occupation_score
        )

        minimum_years = extract_minimum_experience(
            job["description"]
        )

        if (
            minimum_years is not None
            and minimum_years > experience_years
        ):
            continue

        if score < minimum_similarity:
            continue

        ranked_job = dict(job)
        ranked_job["similarity"] = round(score, 4)
        ranked_job["minimum_experience_years"] = minimum_years
        ranked_job["experience_verified"] = (
            minimum_years is not None
        )

        results.append(ranked_job)

    results.sort(
        key=lambda job: job["similarity"],
        reverse=True,
    )

    return results[:top_n]
