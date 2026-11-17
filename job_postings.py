
"""Fetch and conservatively match live job listings for CareerMatch AI."""
import html
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

ADZUNA_API = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

# Occupation-title variants are explicitly labelled as related, not exact matches.
RELATED_TITLES = {
    "data scientist": ("applied scientist", "machine learning scientist"),
    "data analyst": ("analytics analyst", "business intelligence analyst"),
    "software developer": ("software engineer",),
}


def _words(text):
    """Normalize punctuation and simple English plurals in job titles."""
    words = re.findall(r"[a-z0-9]+", str(text).casefold())
    normalized = []

    for word in words:
        if len(word) > 4 and word.endswith("ies"):
            word = word[:-3] + "y"
        elif len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]
        normalized.append(word)

    return normalized


def _match_title(occupation, title):
    """Identify exact occupation-title or explicitly related-title matches."""
    wanted = _words(occupation)
    actual = _words(title)

    if not wanted or not actual:
        return None

    if all(word in actual for word in wanted):
        return "Occupation title match"

    canonical = " ".join(wanted)

    for alternative in RELATED_TITLES.get(canonical, ()):
        if all(word in actual for word in _words(alternative)):
            return "Related job title"

    return None

def clean_job_description(raw_html):
    """Convert Greenhouse HTML descriptions into readable text."""
    if not raw_html:
        return ""

    text = html.unescape(str(raw_html))

    # Preserve separation between paragraphs and list items.
    text = re.sub(
        r"</?(?:p|div|li|br|h[1-6])\b[^>]*>",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    # Remove remaining HTML tags.
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode any remaining HTML entities.
    text = html.unescape(text)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text



def extract_experience_requirements(description):
    """Extract explicitly stated minimum years of experience."""
    if not description:
        return None

    patterns = [
        # Examples: "at least 5 years of experience"
        #           "minimum of 3 years of relevant experience"
        r"\b(?:at least|minimum of)\s+(\d{1,2})\s*\+?\s*years?\s+of\s+(?:relevant\s+|professional\s+|work\s+)?experience\b",

        # Examples: "7+ years of data science, machine learning experience"
        #           "5 years of software development experience"
        r"\b(\d{1,2})\s*\+?\s*years?\s+of\s+[^.!?\n]{0,120}?\bexperience\b",

        # Examples: "3+ years experience"
        #           "5 years relevant experience"
        r"\b(\d{1,2})\s*\+?\s*years?\s+(?:of\s+)?(?:relevant\s+|professional\s+|work\s+)?experience\b",

        # Examples: "5+ years building production ML systems"
        #           "3 years working with Python"
        r"\b(\d{1,2})\s*\+?\s*years?\s+(?:building|developing|working|using|leading|managing)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, description, flags=re.IGNORECASE)
        if match:
            years = int(match.group(1))
            if 0 <= years <= 30:
                return years

    return None



def match_job_skills(description, candidate_skills):
    """
    Find candidate-confirmed skills mentioned in a job description.

    This measures textual overlap, not proficiency or hiring probability.
    """
    if not description or not candidate_skills:
        return {
            "matched_skills": [],
            "match_count": 0,
        }

    description_text = str(description).casefold()
    matched = []
    seen = set()

    for skill in candidate_skills:
        skill_name = str(skill).strip()

        if not skill_name:
            continue

        normalized = skill_name.casefold()

        if normalized in seen:
            continue

        # Match complete terms rather than substrings.
        pattern = (
            r"(?<!\w)"
            + re.escape(normalized)
            + r"(?!\w)"
        )

        if re.search(pattern, description_text):
            matched.append(skill_name)
            seen.add(normalized)

    return {
        "matched_skills": matched,
        "match_count": len(matched),
    }


def detect_job_seniority(title):
    """Estimate job seniority from explicit title indicators."""
    title = str(title).casefold()

    if re.search(r"\b(staff|principal|director|head of|vice president|vp)\b", title):
        return "Advanced"
    if re.search(r"\b(senior|sr\.?|lead|intermediate|mid.level)\b", title):
        return "Senior"
    if re.search(r"\b(junior|jr\.?|entry.level|graduate|intern)\b", title):
        return "Entry-level"
    return "Unspecified"



def detect_job_eligibility(description):
    """Flag explicit eligibility requirements; never infer candidate eligibility."""
    text = re.sub(r"\\s+", " ", str(description or "")).strip()
    if not text:
        return ["Eligibility requirements not verified (description unavailable)"]

    patterns = (
        (
            "U.S. citizenship requirement stated — verify eligibility",
            r"\\b(?:must be|must hold|requires?|required to be|only|need to be)\\s+(?:a\\s+)?(?:u\\.?s\\.?|united states)\\s+citizen\\b"
            r"|\\b(?:u\\.?s\\.?|united states)\\s+citizenship\\s+(?:is\\s+)?(?:required|mandatory)\\b"
            r"|\\b(?:citizenship\\s*:\\s*)(?:u\\.?s\\.?|united states)\\b",
        ),
        (
            "Security clearance requirement stated — verify eligibility",
            r"\\b(?:active|current|existing|must (?:have|hold|possess|obtain)|required|requires?)\\s+"
            r"(?:an?\\s+)?(?:active\\s+|current\\s+)?(?:security\\s+clearance|secret\\s+clearance|top\\s+secret\\s+clearance|ts/sci)\\b"
            r"|\\b(?:security\\s+clearance|secret\\s+clearance|top\\s+secret\\s+clearance|ts/sci)\\s+"
            r"(?:is\\s+)?(?:required|mandatory)\\b",
        ),
        (
            "U.S. work authorization requirement stated — verify eligibility",
            r"\\b(?:must be|required to be)\\s+(?:legally\\s+)?authorized to work in (?:the\\s+)?(?:u\\.?s\\.?|united states)\\b"
            r"|\\b(?:u\\.?s\\.?|united states)\\s+work authorization\\s+(?:is\\s+)?required\\b",
        ),
        (
            "No visa sponsorship stated — verify eligibility",
            r"\\b(?:no|without)\\s+(?:visa\\s+)?sponsorship\\s+(?:is\\s+)?(?:available|provided|offered)\\b"
            r"|\\b(?:will not|do not|does not|cannot|unable to)\\s+(?:provide|offer|support)\\s+(?:visa\\s+)?sponsorship\\b"
            r"|\\b(?:not eligible for|ineligible for)\\s+(?:visa\\s+)?sponsorship\\b",
        ),
    )
    flags = [label for label, pattern in patterns if re.search(pattern, text, re.I)]
    return flags or ["Eligibility requirements not verified in available description"]


def rank_jobs_for_candidate(jobs, candidate_skills, experience_years):
    """
    Rank jobs using candidate skill overlap and experience requirements.

    Jobs with explicitly unmet experience requirements are ranked lower.
    Unknown experience requirements remain unverified.
    """
    try:
        candidate_years = max(0, float(experience_years))
    except (ValueError, TypeError):
        candidate_years = None

    ranked = []

    for job in jobs:
        result = match_job_skills(
            job.get("description", ""),
            candidate_skills
        )

        minimum_years = job.get("minimum_experience_years")

        if minimum_years is None or candidate_years is None:
            experience_status = "Not verified"
            experience_priority = 1
        elif candidate_years >= minimum_years:
            experience_status = "Meets stated minimum"
            experience_priority = 0
        else:
            experience_status = "Below stated minimum"
            experience_priority = 2

        ranked.append({
            **job,
            "matched_skills": result["matched_skills"],
            "match_count": result["match_count"],
            "experience_status": experience_status,
            "seniority_level": detect_job_seniority(job.get("title", "")),
            "eligibility_notices": detect_job_eligibility(job.get("description", "")),
            "_experience_priority": experience_priority,
        })

    def seniority_priority(job):
        level = job["seniority_level"]
        if candidate_years is None:
            return 1
        if candidate_years < 2:
            if level == "Entry-level":
                return 0
            if level == "Unspecified":
                return 1
            return 2
        return 1

    ranked.sort(
        key=lambda job: (
            job["_experience_priority"],
            seniority_priority(job),
            -job["match_count"],
            job["title"].casefold(),
        )
    )

    for job in ranked:
        job.pop("_experience_priority", None)

    return ranked


def fetch_live_jobs(board_tokens=None, occupation="", max_results=10,
                    country="United States", location=""):
    """Search live Adzuna postings without employer-board identifiers.

    Returns (jobs, errors), preserving the interface expected by the app.
    The legacy board_tokens argument is accepted but ignored.
    Requires ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables
    or Streamlit secrets with those names.
    """
    if not _words(occupation):
        return [], ["Select a more specific occupation title."]

    try:
        limit = max(1, min(50, int(max_results)))
    except (TypeError, ValueError):
        limit = 10

    app_id = os.environ.get("ADZUNA_APP_ID", "")
    app_key = os.environ.get("ADZUNA_APP_KEY", "")
    if not app_id or not app_key:
        try:
            import streamlit as st
            app_id = app_id or st.secrets.get("ADZUNA_APP_ID", "")
            app_key = app_key or st.secrets.get("ADZUNA_APP_KEY", "")
        except (ImportError, FileNotFoundError, KeyError):
            pass

    if not app_id or not app_key:
        return [], ["Set ADZUNA_APP_ID and ADZUNA_APP_KEY to enable live job search."]

    country_codes = {
        "United States": "us", "United Kingdom": "gb",
        "Canada": "ca", "Australia": "au",
    }
    code = country_codes.get(country)
    if not code:
        return [], ["The selected country is not configured for Adzuna search."]

    results, seen, errors = [], set(), []
    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # A few pages allow broader discovery without an employer list.
    for page in range(1, 4):
        try:
            response = requests.get(
                ADZUNA_API.format(country=code, page=page),
                params={
                    "app_id": app_id,
                    "app_key": app_key,
                    "what": occupation,
                    "where": location.strip(),
                    "results_per_page": 50,
                    "content-type": "application/json",
                },
                timeout=20,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
            postings = payload.get("results", [])
            if not isinstance(postings, list):
                raise ValueError("Unexpected API response")

            for item in postings:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title") or "").strip()
                match_type = _match_title(occupation, title)
                if match_type is None:
                    continue
                link = str(item.get("redirect_url") or "")
                parsed = urlparse(link)
                if parsed.scheme != "https" or not parsed.netloc:
                    continue
                description = clean_job_description(item.get("description", ""))
                company = item.get("company") or {}
                company_name = str(company.get("display_name") or "Not specified") if isinstance(company, dict) else "Not specified"
                # One role advertised in several cities should appear only once.
                identity = (" ".join(_words(company_name)), " ".join(_words(title)))
                if identity in seen:
                    continue
                seen.add(identity)
                location_data = item.get("location") or {}
                results.append({
                    "title": title,
                    "company": company_name,
                    "location": str(location_data.get("display_name") or "Not specified") if isinstance(location_data, dict) else "Not specified",
                    "url": link,
                    "updated_at": item.get("created"),
                    "retrieved_at": retrieved_at,
                    "source": "Adzuna live job search",
                    "match_type": match_type,
                    "description": description,
                    "minimum_experience_years": extract_experience_requirements(description),
                })
        except (requests.RequestException, ValueError, TypeError) as exc:
            errors.append(f"Live search failed ({type(exc).__name__}); verify Adzuna credentials and API access.")
            break
        if len(results) >= limit:
            break

    results.sort(key=lambda job: (
        job["match_type"] != "Occupation title match",
        job["title"].casefold(),
        job["company"].casefold(),
    ))
    return results[:limit], errors


def categorize_jobs(ranked_jobs, experience_years):
    """Group jobs using experience evidence and cautious seniority signals.

    A title alone does not establish eligibility. Unverified senior/advanced
    postings are flagged for review for candidates reporting under two years.
    """
    potential_matches = []
    needs_review = []
    experience_mismatches = []

    try:
        candidate_years = (
            None if experience_years is None
            else max(0, float(experience_years))
        )
    except (ValueError, TypeError):
        candidate_years = None

    for job in ranked_jobs:
        status = job.get("experience_status", "Not verified")
        seniority = job.get("seniority_level", "Unspecified")

        if status == "Below stated minimum":
            experience_mismatches.append(job)
        elif (
            seniority in ("Senior", "Advanced")
            and candidate_years is not None
            and candidate_years < 2
        ):
            needs_review.append(job)
        else:
            potential_matches.append(job)

    return potential_matches, needs_review, experience_mismatches



# Conservative location assessment: unknown locations are never treated as matches.
COUNTRY_MARKERS = {
    "United States": ("united states", "united states of america", "usa", "u.s.a.", "us", "u.s."),
    "United Kingdom": ("united kingdom", "uk", "england", "scotland", "wales", "london"),
    "Brazil": ("brazil", "brasil", "são paulo", "sao paulo", "campinas"),
}
US_STATE_CODES = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC".split())
US_STATE_NAMES = set("alabama alaska arizona arkansas california colorado connecticut delaware florida georgia hawaii idaho illinois indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan minnesota minnesota mississippi missouri montana nebraska nevada new hampshire new jersey new mexico new york north carolina north dakota ohio oklahoma oregon pennsylvania rhode island south carolina south dakota tennessee texas utah vermont virginia washington west virginia wisconsin wyoming district of columbia".split(" | "))


def assess_job_location(location, preferred_country="United States"):
    """Return Match, Different country, or Needs verification; no geocoding guesses."""
    if preferred_country == "Any country":
        return "Match"
    raw = str(location or "").strip()
    if not raw or raw.casefold() in {"remote", "not specified", "multiple locations", "anywhere", "global", "worldwide"}:
        return "Needs verification"
    lowered = raw.casefold()
    detected = set()
    for country, markers in COUNTRY_MARKERS.items():
        if any(re.search(r"(?<!\w)" + re.escape(marker) + r"(?!\w)", lowered) for marker in markers):
            detected.add(country)
    # US state abbreviations require a comma prefix to avoid treating words like IN as a state.
    if re.search(r",\s*(?:" + "|".join(sorted(US_STATE_CODES)) + r")(?:\b|$)", raw):
        detected.add("United States")
    if re.search(r"\b(?:california|texas|new york|washington|massachusetts|florida|illinois|colorado|georgia|virginia|north carolina|new jersey|oregon|arizona|pennsylvania|ohio|michigan)\b", lowered):
        detected.add("United States")
    if not detected:
        return "Needs verification"
    return ("Needs verification" if len(detected) > 1 else "Match" if preferred_country in detected else "Different country")

def separate_jobs_by_experience(ranked_jobs):
    """Legacy two-group interface retained for existing integrations."""
    potential_matches = []
    experience_mismatches = []
    for job in ranked_jobs:
        if job.get("experience_status") == "Below stated minimum":
            experience_mismatches.append(job)
        else:
            potential_matches.append(job)
    return potential_matches, experience_mismatches
