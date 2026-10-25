
import pandas as pd

from sentence_bert_matcher import (
    build_sbert_model,
    recommend_careers_sbert,
)

# Synthetic occupations for testing only
sample_data = pd.DataFrame([
    {
        "O*NET-SOC Code": "15-2051.00",
        "Title": "Data Scientists",
        "Description": "Analyze data and build machine learning models.",
        "Essential Skills": [
            {"Element Name": "Mathematics"},
            {"Element Name": "Critical Thinking"},
        ],
        "Software Skills": [
            {"Workplace Example": "Python"},
            {"Workplace Example": "SQL"},
        ],
    },
    {
        "O*NET-SOC Code": "15-1252.00",
        "Title": "Software Developers",
        "Description": "Design and develop software applications.",
    },
    {
        "O*NET-SOC Code": "15-1212.00",
        "Title": "Information Security Analysts",
        "Description": "Protect computer systems and networks.",
    },
    {
        "O*NET-SOC Code": "13-2011.00",
        "Title": "Accountants and Auditors",
        "Description": "Prepare and examine financial records.",
    },
    {
        "O*NET-SOC Code": "29-1141.00",
        "Title": "Registered Nurses",
        "Description": "Provide and coordinate patient care.",
    },
])

candidate_skills = [
    "Python",
    "SQL",
    "Machine Learning",
    "Data Analysis",
    "Statistics",
]

profiles, model, embeddings = build_sbert_model(sample_data)

results = recommend_careers_sbert(
    candidate_skills,
    profiles,
    model,
    embeddings,
    top_n=5,
)

print("\nSENTENCE-BERT TEST RESULTS")
print(results.to_string(index=False))

assert len(results) == 5
assert results["O*NET-SOC Code"].nunique() == 5
assert results["Similarity Score"].notna().all()
assert results["Similarity Score"].is_monotonic_decreasing

print("\nTEST PASSED")
