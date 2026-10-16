
import pandas as pd
from pathlib import Path

# Project folder paths
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def load_onet_data(file_path):
    """Load an Excel or CSV dataset."""
    path = Path(file_path)

    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path)
    elif path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    else:
        raise ValueError("Unsupported file format")


def clean_onet_data(df):
    """Clean text, remove duplicates, and validate codes."""
    df = df.copy()

    # Remove spaces from column names
    df.columns = df.columns.str.strip()

    # Remove extra spaces from text values
    for column in df.select_dtypes(include=["object"]):
        df[column] = df[column].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Remove rows without occupation codes
    if "O*NET-SOC Code" in df.columns:
        df = df.dropna(subset=["O*NET-SOC Code"])

    return df


def save_cleaned_data(df, output_path):
    """Save cleaned dataset as CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def main():
    datasets = {
        "Occupation Data.xlsx": "occupation_cleaned.csv",
        "Job Titles.xlsx": "job_titles_cleaned.csv",
        "Essential Skills.xlsx": "essential_skills_cleaned.csv",
        "Software Skills.xlsx": "software_skills_cleaned.csv",
    }

    for input_name, output_name in datasets.items():
        input_path = RAW_DIR / input_name
        output_path = PROCESSED_DIR / output_name

        data = load_onet_data(input_path)
        cleaned = clean_onet_data(data)
        save_cleaned_data(cleaned, output_path)

        print(f"\nDataset: {input_name}")
        print(f"Original rows: {len(data)}")
        print(f"Cleaned rows: {len(cleaned)}")
        print(f"Saved to: {output_path}")

    print("\nAll O*NET datasets processed successfully!")


if __name__ == "__main__":
    main()

