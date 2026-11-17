
import pandas as pd
from pathlib import Path

# Locate the project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def load_onet_data():
    """Load the four O*NET datasets."""

    occupation_df = pd.read_excel(
        RAW_DATA_DIR / "Occupation Data.xlsx"
    )

    job_titles_df = pd.read_excel(
        RAW_DATA_DIR / "Job Titles.xlsx"
    )

    essential_skills_df = pd.read_excel(
        RAW_DATA_DIR / "Essential Skills.xlsx"
    )

    software_skills_df = pd.read_excel(
        RAW_DATA_DIR / "Software Skills.xlsx"
    )

    return (
        occupation_df,
        job_titles_df,
        essential_skills_df,
        software_skills_df
    )


def process_job_titles(job_titles_df):
    """Group alternate job titles by occupation code."""

    titles = (
        job_titles_df
        .groupby("O*NET-SOC Code")["Title"]
        .agg(list)
        .reset_index()
    )

    return titles

if __name__ == "__main__":
    occupation, job_titles, skills, software = load_onet_data()

    print("Occupations:", occupation.shape)
    print("Job titles:", job_titles.shape)
    print("Essential skills:", skills.shape)
    print("Software skills:", software.shape)

    # Process alternate job titles
    processed_titles = process_job_titles(job_titles)

    print("\nProcessed job titles:")
    print(processed_titles.head())
