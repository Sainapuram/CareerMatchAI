
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.matching import load_occupation_profiles, create_matching_text
from src.skill_gap import analyze_skill_gap


# Sample candidate profiles for testing
TEST_PROFILES = {
    "Data Science": ["Python", "SQL", "Machine Learning"],
    "Business Analytics": ["Excel", "SQL", "Power BI", "Tableau"],
}


def evaluate_profile(skills, df, vectorizer, matrix):
    """Compare baseline TF-IDF, bigram TF-IDF, and hybrid rankings."""

    candidate_text = " ".join(skills)

    candidate_vector = vectorizer.transform([candidate_text])
    tfidf_scores = cosine_similarity(candidate_vector, matrix).ravel()

    skill_scores = []

    for _, row in df.iterrows():
        software = row["Software Skills"]

        software_names = [
            item.get("Workplace Example", "")
            for item in software
            if isinstance(item, dict)
        ] if isinstance(software, list) else []

        result = analyze_skill_gap(skills, software_names)
        skill_scores.append(result["matched_count"] / len(skills))

    skill_scores = np.array(skill_scores)

    hybrid_scores = 0.7 * tfidf_scores + 0.3 * skill_scores

    indices = np.argsort(-hybrid_scores, kind="stable")[:5]

    results = df.iloc[indices][["Title"]].copy()
    results["TF-IDF"] = tfidf_scores[indices]
    results["Skill Match"] = skill_scores[indices]
    results["Hybrid Score"] = hybrid_scores[indices]

    return results


def main():
    df = load_occupation_profiles()
    texts = df.apply(create_matching_text, axis=1)

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform(texts)

    print(f"Loaded {len(df)} occupations.")

    for profile_name, skills in TEST_PROFILES.items():
        print(f"\n{'=' * 60}")
        print(f"Candidate Profile: {profile_name}")
        print(f"Skills: {', '.join(skills)}")
        print(f"{'=' * 60}")

        results = evaluate_profile(skills, df, vectorizer, matrix)
        print(results.to_string(index=False))


if __name__ == "__main__":
    main()
