
from pathlib import Path

import pandas as pd

from src.matching import build_tfidf_model, recommend_careers
from sentence_bert_matcher import (
    build_sbert_model,
    recommend_careers_sbert,
)


OUTPUT_DIR = Path("evaluation_results")


def precision_at_k(recommended, relevant, k=5):
    """Fraction of top-k recommendations that are relevant."""
    recommended = recommended[:k]
    relevant = set(relevant)

    if not recommended:
        return 0.0

    return sum(code in relevant for code in recommended) / k


def reciprocal_rank(recommended, relevant):
    """Reciprocal rank of the first relevant recommendation."""
    relevant = set(relevant)

    for rank, code in enumerate(recommended, start=1):
        if code in relevant:
            return 1.0 / rank

    return 0.0


def evaluate_models(occupation_df, candidates):
    """Compare TF-IDF and Sentence-BERT on identical candidates."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tfidf_profiles, vectorizer, tfidf_matrix = build_tfidf_model(
        occupation_df
    )

    sbert_profiles, sbert_model, sbert_embeddings = build_sbert_model(
        occupation_df
    )

    tfidf_rows = []
    sbert_rows = []
    metric_rows = []

    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        skills = candidate["skills"]
        relevant = candidate["relevant_codes"]

        tfidf_results = recommend_careers(
            skills,
            tfidf_profiles,
            vectorizer,
            tfidf_matrix,
            top_n=5,
        )

        sbert_results = recommend_careers_sbert(
            skills,
            sbert_profiles,
            sbert_model,
            sbert_embeddings,
            top_n=5,
        )

        for model_name, results, rows in [
            ("TF-IDF", tfidf_results, tfidf_rows),
            ("Sentence-BERT", sbert_results, sbert_rows),
        ]:
            codes = results["O*NET-SOC Code"].astype(str).tolist()

            for rank, (_, row) in enumerate(
                results.iterrows(), start=1
            ):
                rows.append({
                    "Candidate ID": candidate_id,
                    "Rank": rank,
                    "O*NET-SOC Code": str(row["O*NET-SOC Code"]),
                    "Title": row["Title"],
                    "Similarity Score": row["Similarity Score"],
                })

            metric_rows.append({
                "Candidate ID": candidate_id,
                "Model": model_name,
                "Precision@5": precision_at_k(codes, relevant),
                "Reciprocal Rank": reciprocal_rank(codes, relevant),
            })

    pd.DataFrame(tfidf_rows).to_csv(
        OUTPUT_DIR / "tfidf_results.csv", index=False
    )

    pd.DataFrame(sbert_rows).to_csv(
        OUTPUT_DIR / "sbert_results.csv", index=False
    )

    metrics_df = pd.DataFrame(metric_rows)

    comparison = (
        metrics_df.groupby("Model", as_index=False)
        .agg({
            "Precision@5": "mean",
            "Reciprocal Rank": "mean",
        })
        .rename(columns={"Reciprocal Rank": "MRR"})
    )

    comparison.to_csv(
        OUTPUT_DIR / "model_comparison.csv", index=False
    )

    print("\nMODEL COMPARISON")
    print(comparison.to_string(index=False))

    return comparison


if __name__ == "__main__":
    # Synthetic occupations for testing only.
    occupations = pd.DataFrame([
        {
            "O*NET-SOC Code": "15-2051.00",
            "Title": "Data Scientists",
            "Description": "Analyze data using Python, SQL, statistics and machine learning.",
        },
        {
            "O*NET-SOC Code": "15-1252.00",
            "Title": "Software Developers",
            "Description": "Develop software applications using programming and coding.",
        },
        {
            "O*NET-SOC Code": "15-1212.00",
            "Title": "Information Security Analysts",
            "Description": "Protect computer systems from cybersecurity threats.",
        },
        {
            "O*NET-SOC Code": "13-2011.00",
            "Title": "Accountants and Auditors",
            "Description": "Analyze financial records, accounting and taxes.",
        },
        {
            "O*NET-SOC Code": "29-1141.00",
            "Title": "Registered Nurses",
            "Description": "Provide patient care and healthcare services.",
        },
    ])

    # Illustrative relevance labels, not human-reviewed ground truth.
    candidates = [
        {
            "candidate_id": "C001",
            "skills": ["Python", "SQL", "Machine Learning", "Statistics"],
            "relevant_codes": ["15-2051.00"],
        },
        {
            "candidate_id": "C002",
            "skills": ["Software Development", "Programming", "Coding"],
            "relevant_codes": ["15-1252.00"],
        },
        {
            "candidate_id": "C003",
            "skills": ["Cybersecurity", "Network Security", "Threat Detection"],
            "relevant_codes": ["15-1212.00"],
        },
    ]

    evaluate_models(occupations, candidates)
