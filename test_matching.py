
import pandas as pd
from src.matching import build_tfidf_model, recommend_careers

sample_data = pd.DataFrame({
    "O*NET-SOC Code": ["TEST-0", "TEST-1", "TEST-2", "TEST-3", "TEST-4"],
    "Title": [
        "Data Scientists",
        "Software Developers",
        "Database Architects",
        "Statisticians",
        "Computer Systems Analysts"
    ],
    "Description": [
        "Python machine learning statistics data analysis",
        "Software development Java programming",
        "SQL database design management",
        "Statistical analysis mathematics R",
        "Business systems analysis requirements"
    ],
    "Alternate Job Titles": [[] for _ in range(5)],
    "Essential Skills": [[] for _ in range(5)],
    "Software Skills": [[] for _ in range(5)]
})

profiles, vectorizer, matrix = build_tfidf_model(sample_data)

results = recommend_careers(
    "Python machine learning statistics SQL",
    profiles,
    vectorizer,
    matrix,
    top_n=5
)

print("\nTOP 5 CAREER RECOMMENDATIONS")
print(results.to_string(index=False))

assert len(results) == 5
assert "Similarity Score" in results.columns

print("\nTEST PASSED")
