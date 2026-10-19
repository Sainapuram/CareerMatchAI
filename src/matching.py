from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def create_matching_text(row):
    """Combine occupation information into searchable text."""

    alternate_titles = row.get("Alternate Job Titles", [])
    essential_skills = row.get("Essential Skills", [])
    software_skills = row.get("Software Skills", [])

    if not isinstance(alternate_titles, list):
        alternate_titles = []

    if not isinstance(essential_skills, list):
        essential_skills = []

    if not isinstance(software_skills, list):
        software_skills = []

    titles_text = " ".join(str(title) for title in alternate_titles)

    skills_text = " ".join(
        str(skill.get("Element Name", ""))
        for skill in essential_skills
        if isinstance(skill, dict)
    )

    software_text = " ".join(
        str(software.get("Workplace Example", ""))
        for software in software_skills
        if isinstance(software, dict)
    )

    return " ".join([
        str(row.get("Title", "") or ""),
        str(row.get("Description", "") or ""),
        titles_text,
        skills_text,
        software_text,
    ])


def load_occupation_profiles(data_path=None):
    """Load the processed O*NET occupation profiles."""

    if data_path is None:
        data_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "processed"
            / "occupation_profiles.pkl"
        )

    return pd.read_pickle(data_path)


def build_tfidf_model(occupation_profiles_df):
    """Build the TF-IDF model from occupation profiles."""

    profiles = occupation_profiles_df.copy()

    profiles["Matching Text"] = profiles.apply(
        create_matching_text, axis=1
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english"
    )

    occupation_matrix = vectorizer.fit_transform(
        profiles["Matching Text"]
    )

    return profiles, vectorizer, occupation_matrix


def recommend_careers(
    candidate_skills,
    profiles,
    vectorizer,
    occupation_matrix,
    top_n=5
):
    """Return the highest-ranking career matches."""

    if isinstance(candidate_skills, list):
        candidate_text = " ".join(map(str, candidate_skills))
    elif isinstance(candidate_skills, str):
        candidate_text = candidate_skills
    else:
        raise TypeError("candidate_skills must be a string or list")

    if not candidate_text.strip():
        raise ValueError("Candidate skills cannot be empty")

    if not 1 <= top_n <= len(profiles):
        raise ValueError("top_n must be between 1 and the number of profiles")

    candidate_vector = vectorizer.transform([candidate_text])

    scores = cosine_similarity(
        candidate_vector, occupation_matrix
    ).flatten()

    top_indices = scores.argsort()[-top_n:][::-1]

    results = profiles.iloc[top_indices][
        ["O*NET-SOC Code", "Title"]
    ].copy()

    results["Similarity Score"] = scores[top_indices]

    return results.reset_index(drop=True)
