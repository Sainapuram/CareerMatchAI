
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from src.matching import create_matching_text, load_occupation_profiles


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def build_sbert_model(occupation_profiles_df, model_name=MODEL_NAME):
    """Prepare occupation embeddings using Sentence-BERT."""

    profiles = occupation_profiles_df.copy()

    # Reuse exactly the same occupation text as TF-IDF.
    profiles["Matching Text"] = profiles.apply(
        create_matching_text, axis=1
    )

    if profiles.empty:
        raise ValueError("Occupation profiles cannot be empty")

    model = SentenceTransformer(model_name)

    occupation_embeddings = model.encode(
        profiles["Matching Text"].tolist(),
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return profiles, model, occupation_embeddings


def recommend_careers_sbert(
    candidate_skills,
    profiles,
    model,
    occupation_embeddings,
    top_n=5
):
    """Return Top-N occupations ranked by semantic similarity."""

    if isinstance(candidate_skills, list):
        candidate_text = " ".join(map(str, candidate_skills))
    elif isinstance(candidate_skills, str):
        candidate_text = candidate_skills
    else:
        raise TypeError("candidate_skills must be a string or list")

    if not candidate_text.strip():
        raise ValueError("Candidate skills cannot be empty")

    if not 1 <= top_n <= len(profiles):
        raise ValueError("Invalid top_n value")

    candidate_embedding = model.encode(
        [candidate_text],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Dot product of normalized vectors equals cosine similarity.
    scores = np.dot(
        occupation_embeddings,
        candidate_embedding[0]
    )

    top_indices = np.argsort(-scores, kind="stable")[:top_n]

    results = profiles.iloc[top_indices][
        ["O*NET-SOC Code", "Title"]
    ].copy()

    results.insert(0, "Rank", range(1, len(results) + 1))
    results["Similarity Score"] = scores[top_indices]

    return results.reset_index(drop=True)


if __name__ == "__main__":
    profiles_df = load_occupation_profiles()

    profiles, model, embeddings = build_sbert_model(profiles_df)

    candidate_skills = [
        "Python",
        "SQL",
        "Machine Learning",
        "Data Analysis",
        "Statistics"
    ]

    results = recommend_careers_sbert(
        candidate_skills,
        profiles,
        model,
        embeddings
    )

    print("\nTop 5 Sentence-BERT Career Recommendations:")
    print(results.to_string(index=False))
