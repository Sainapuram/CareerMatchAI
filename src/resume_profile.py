import re


SECTION_NAMES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "career summary",
        "objective",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "skills and tools",
        "technical proficiencies",
    ],
    "education": [
        "education",
        "academic background",
        "academic qualifications",
    ],
    "work_experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "relevant experience",
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "relevant projects",
    ],
    "certifications": [
        "certifications",
        "licenses and certifications",
        "certifications and training",
    ],
}


def extract_resume_sections(resume_text):
    """Group résumé text under recognized section headings."""

    sections = {
        section: []
        for section in SECTION_NAMES
    }
    sections["other"] = []

    current_section = "other"

    for line in resume_text.splitlines():
        line = line.strip()

        if not line:
            continue

        heading = re.sub(r"[:\s]+$", "", line).casefold()

        matched_section = None

        for section, headings in SECTION_NAMES.items():
            if heading in headings:
                matched_section = section
                break

        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(line)

    return sections


def build_candidate_profile(resume_text):
    """Build a structured profile from résumé sections."""

    sections = extract_resume_sections(resume_text)

    profile = {
        "summary": " ".join(sections["summary"]),
        "skills": sections["skills"],
        "education": sections["education"],
        "work_experience": sections["work_experience"],
        "projects": sections["projects"],
        "certifications": sections["certifications"],
    }

    return profile