
import json

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.matching import (
    load_occupation_profiles,
    build_tfidf_model,
    recommend_careers,
    create_matching_text,
)

from src.skill_gap import analyze_skill_gap

from sentence_bert_matcher import (
    build_sbert_model,
    recommend_careers_sbert,
)


TOP_K = 5
HYBRID_TFIDF_WEIGHT = 0.7
HYBRID_SKILL_WEIGHT = 0.3


def load_evaluation_profiles():
    with open(
        "evaluation_profiles.json",
        "r",
        encoding="utf-8",
    ) as file:
        evaluation = json.load(file)

    return evaluation["profiles"]


def reciprocal_rank_at_k(
    recommended_codes,
    relevant_codes,
    k=TOP_K,
):
    """Reciprocal rank of the first relevant occupation."""
    relevant = set(relevant_codes)

    for rank, code in enumerate(
        recommended_codes[:k],
        start=1,
    ):
        if code in relevant:
            return 1.0 / rank

    return 0.0


def print_results(model_name, results):
    print(f"\n{model_name}")
    print("=" * 50)

    for result in results:
        print(
            f"{result['id']} | "
            f"{result['category']} | "
            f"RR@5: {result['rr']:.3f}"
        )

    mrr = np.mean([result["rr"] for result in results])

    print("=" * 50)
    print(f"{model_name} MRR@5: {mrr:.3f}")

    return float(mrr)


def evaluate_tfidf():
    candidates = load_evaluation_profiles()

    df = load_occupation_profiles()

    profiles, vectorizer, matrix = build_tfidf_model(df)

    results = []

    for candidate in candidates:
        recommendations = recommend_careers(
            candidate["skills"],
            profiles,
            vectorizer,
            matrix,
            top_n=TOP_K,
        )

        recommended_codes = recommendations[
            "O*NET-SOC Code"
        ].tolist()

        rr = reciprocal_rank_at_k(
            recommended_codes,
            candidate["relevant_occupation_codes"],
        )

        results.append({
            "id": candidate["id"],
            "category": candidate["category"],
            "rr": rr,
        })

    return print_results(
        "Original TF-IDF Baseline Evaluation",
        results,
    )


def evaluate_sbert():
    candidates = load_evaluation_profiles()

    df = load_occupation_profiles()

    profiles, model, embeddings = build_sbert_model(df)

    results = []

    for candidate in candidates:
        recommendations = recommend_careers_sbert(
            candidate["skills"],
            profiles,
            model,
            embeddings,
            top_n=TOP_K,
        )

        recommended_codes = recommendations[
            "O*NET-SOC Code"
        ].tolist()

        rr = reciprocal_rank_at_k(
            recommended_codes,
            candidate["relevant_occupation_codes"],
        )

        results.append({
            "id": candidate["id"],
            "category": candidate["category"],
            "rr": rr,
        })

    return print_results(
        "Sentence-BERT Evaluation",
        results,
    )


def evaluate_bigram_and_hybrid():
    candidates = load_evaluation_profiles()

    df = load_occupation_profiles().copy()

    df["Matching Text"] = df.apply(
        create_matching_text,
        axis=1,
    )

    # Shared TF-IDF representation for both experiments.
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
    )

    matrix = vectorizer.fit_transform(
        df["Matching Text"]
    )

    # Extract software names once per occupation.
    occupation_software = []

    for occupation_skills in df["Software Skills"]:
        software_names = []

        if isinstance(occupation_skills, list):
            for item in occupation_skills:
                if isinstance(item, dict):
                    name = item.get("Workplace Example")

                    if isinstance(name, str) and name.strip():
                        software_names.append(name)

        occupation_software.append(software_names)

    bigram_results = []
    hybrid_results = []

    for candidate in candidates:
        skills = candidate["skills"]

        candidate_vector = vectorizer.transform(
            [" ".join(skills)]
        )

        tfidf_scores = cosine_similarity(
            candidate_vector,
            matrix,
        ).flatten()

        skill_scores = []

        for software_names in occupation_software:
            gap = analyze_skill_gap(
                skills,
                software_names,
            )

            score = (
                gap["matched_count"] / len(skills)
                if skills else 0.0
            )

            skill_scores.append(score)

        skill_scores = np.array(skill_scores)

        hybrid_scores = (
            HYBRID_TFIDF_WEIGHT * tfidf_scores
            + HYBRID_SKILL_WEIGHT * skill_scores
        )

        # Both rankings use the same TF-IDF features.
        bigram_ranking = np.argsort(
            -tfidf_scores,
            kind="stable",
        )

        hybrid_ranking = np.argsort(
            -hybrid_scores,
            kind="stable",
        )

        bigram_codes = df.iloc[
            bigram_ranking[:TOP_K]
        ]["O*NET-SOC Code"].tolist()

        hybrid_codes = df.iloc[
            hybrid_ranking[:TOP_K]
        ]["O*NET-SOC Code"].tolist()

        bigram_rr = reciprocal_rank_at_k(
            bigram_codes,
            candidate["relevant_occupation_codes"],
        )

        hybrid_rr = reciprocal_rank_at_k(
            hybrid_codes,
            candidate["relevant_occupation_codes"],
        )

        bigram_results.append({
            "id": candidate["id"],
            "category": candidate["category"],
            "rr": bigram_rr,
        })

        hybrid_results.append({
            "id": candidate["id"],
            "category": candidate["category"],
            "rr": hybrid_rr,
        })

        # Detailed diagnostic for Software Development.
        if candidate["id"] == "P3":
            print("\nSoftware Development: Top 15 Hybrid Rankings")
            print("=" * 90)

            print(
                f"{'Rank':<6}"
                f"{'Occupation':<48}"
                f"{'TF-IDF':>10}"
                f"{'Skill':>10}"
                f"{'Hybrid':>10}"
            )

            for rank, position in enumerate(
                hybrid_ranking[:15],
                start=1,
            ):
                occupation = df.iloc[position]["Title"]

                print(
                    f"{rank:<6}"
                    f"{occupation[:47]:<48}"
                    f"{tfidf_scores[position]:>10.4f}"
                    f"{skill_scores[position]:>10.4f}"
                    f"{hybrid_scores[position]:>10.4f}"
                )

            target_positions = np.flatnonzero(
                df["O*NET-SOC Code"].to_numpy()
                == "15-1252.00"
            )

            if len(target_positions) > 0:
                target_position = target_positions[0]

                target_rank = (
                    np.flatnonzero(
                        hybrid_ranking == target_position
                    )[0] + 1
                )

                print(
                    "\nSoftware Developers actual hybrid rank:",
                    target_rank,
                )

    bigram_mrr = print_results(
        "Bigram TF-IDF Evaluation",
        bigram_results,
    )

    hybrid_mrr = print_results(
        "Experimental Hybrid Evaluation",
        hybrid_results,
    )

    return bigram_mrr, hybrid_mrr


if __name__ == "__main__":
    original_mrr = evaluate_tfidf()

    sbert_mrr = evaluate_sbert()

    bigram_mrr, hybrid_mrr = evaluate_bigram_and_hybrid()

    print("\nFinal Model Comparison")
    print("=" * 50)
    print(f"Original TF-IDF:  {original_mrr:.3f}")
    print(f"Bigram TF-IDF:    {bigram_mrr:.3f}")
    print(f"Sentence-BERT:    {sbert_mrr:.3f}")
    print(f"Hybrid:           {hybrid_mrr:.3f}")
