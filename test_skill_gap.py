
from src.skill_gap import analyze_skill_gap

candidate_skills = [
    "Python",
    "SQL",
    "Excel"
]

occupation_skills = [
    "Python",
    "SQL",
    "Machine Learning",
    "Statistics"
]

results = analyze_skill_gap(
    candidate_skills,
    occupation_skills
)

print("\nSKILL GAP ANALYSIS RESULTS")
print("--------------------------")
print("Matched Skills:", results["matched_skills"])
print("Missing Skills:", results["missing_skills"])
print("Matched Count:", results["matched_count"])
print("Missing Count:", results["missing_count"])
print("Skill Coverage:", results["skill_coverage_percent"], "%")

assert results["matched_count"] == 2
assert results["missing_count"] == 2
assert results["skill_coverage_percent"] == 50.0

print("\nTEST PASSED")
