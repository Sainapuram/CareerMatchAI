# CareerMatchAI

### Career Recommendation and Skill-Gap Analysis Platform

CareerMatchAI is a privacy-aware, skill-based career recommendation platform designed to help students and early-career job seekers identify suitable occupations, understand their existing skills, and explore opportunities for professional development.

The project uses **O*NET occupational data and ESCO skills terminology** to support career exploration. It combines resume skill extraction, TF-IDF-based career matching, skill-gap analysis, certification recommendations, and career development resources through an interactive Streamlit application.

The project was developed collaboratively as part of an academic research initiative.

## 1. Research Objectives

CareerMatchAI addresses three research questions:

**RQ1 — Career Recommendation:** Which occupations best match a candidate's existing skills?

**RQ2 — Career Similarity:** How closely do a candidate's skills align with the requirements of recommended occupations?

**RQ3 — Skill-Gap Identification:** Which skills are missing from a candidate's profile relative to the requirements of a target occupation?

The platform aims to provide interpretable, skill-based career recommendations and actionable career development information.

## 2. Key Features

### Resume Processing and Skill Extraction

- Supports resume processing through the Streamlit interface.
- Includes document-reading support for PDF and DOCX files.
- Extracts skills from candidate-provided information.
- Provides skill information for downstream career matching.

### Career Recommendations

- Uses structured O*NET occupation profiles.
- Represents occupation information using TF-IDF.
- Applies cosine similarity for skill-based matching.
- Ranks occupations based on their similarity to candidate skills.

### Skill-Gap Analysis

- Compares candidate skills with occupational skill information.
- Identifies potential gaps between existing skills and occupation requirements.
- Supports exploration of skills relevant to career development.

### Certification and Learning Resources

- Includes a certification catalog and recommendation module.
- Provides learning resources to support professional development.
- Includes links to official employer career portals.

### AI Career Advisor

- Includes an Ollama-based advisor module for additional career guidance.
- May require a separately configured local Ollama environment.

These features are represented in the project code. Full end-to-end testing and validation of all optional components remain to be confirmed.

## 3. Technology Stack

| Category | Technologies |
|---|---|
| Programming language | Python |
| Frontend | Streamlit |
| Data processing | pandas, NumPy |
| Machine learning | scikit-learn |
| Career matching | TF-IDF, cosine similarity |
| Semantic matching experiments | Sentence-BERT |
| Document processing | python-docx, pypdf |
| Excel data loading | openpyxl |
| Occupational data and terminology | O*NET, ESCO |
| Optional AI advisor | Ollama |
| Development | VS Code, Jupyter Notebook, Git, GitHub |

## 4. Data Sources

### O*NET

O*NET provides structured occupational information used to construct career profiles.

The project uses occupational information such as:

- Occupation titles and descriptions
- Alternate job titles
- Essential skills
- Software skills
- O*NET-SOC occupation codes

Official source: https://www.onetcenter.org/

O*NET database downloads: https://www.onetcenter.org/database.html

### ESCO

ESCO stands for **European Skills, Competences, Qualifications and Occupations**.

ESCO provides standardized terminology for describing skills, competences, and occupations.

ESCO terminology was used during CareerMatchAI development alongside O*NET. The repository's verified occupation-profile loading and TF-IDF matching code uses O*NET-derived profiles; ESCO is not presented here as a separately deployed matching model.

Official source: https://esco.ec.europa.eu/

## 5. Project Structure

```text
CareerMatchAI/
│
├── .streamlit/
│   └── config.toml
│
├── data/
│   ├── raw/
│   └── processed/
│
├── Notebook/
│   ├── 01_onet_exploration.ipynb
│   └── 02_career_matching.ipynb
│
├── src/
│   ├── data_processing.py
│   ├── matching.py
│   ├── skill_gap.py
│   └── sentence_bert_matcher.py
│
├── app.py
├── career_resources.py
├── certification_catalog.py
├── certification_recommender.py
├── ollama_advisor.py
├── skill_extractor.py
├── sentence_bert_matcher.py
│
├── evaluate_models.py
├── evaluate_hybrid.py
├── evaluation_profiles.json
│
├── test_matching.py
├── frontend_agent_pseudocode.md
├── requirements.txt
├── .gitignore
└── README.md
```

The structure reflects the locally verified project files. Some files may remain on separate Git branches until they are committed and merged.

## 6. Installation and Setup

### Prerequisites

- Python 3
- Git
- A Python-compatible development environment
- Required O*NET datasets

### Step 1 — Clone the repository

```bash
git clone https://github.com/Sainapuram/CareerMatchAI.git
cd CareerMatchAI
```

### Step 2 — Create a virtual environment

For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3 — Install dependencies

```bash
python -m pip install -r requirements.txt
```

The dependency file should include:

```text
streamlit
pandas
numpy
scikit-learn
python-docx
pypdf
sentence-transformers
openpyxl
```

Package versions are not yet pinned. A clean-environment installation has not been fully verified.

## 7. Dataset Preparation

### Step 1 — Obtain the O*NET datasets

The project expects the following Excel files:

```text
data/raw/
├── Occupation Data.xlsx
├── Job Titles.xlsx
├── Essential Skills.xlsx
└── Software Skills.xlsx
```

These filenames must match those expected by the preprocessing code.

The datasets can be obtained from the official O*NET Resource Center, subject to the relevant data availability and usage terms.

### Step 2 — Generate occupation profiles

The notebook:

```text
Notebook/01_onet_exploration.ipynb
```

contains the data preparation workflow.

It integrates occupational information and creates structured occupation profiles.

The output is saved as:

```text
data/processed/occupation_profiles.pkl
```

**Important working-directory requirement:** The notebook currently uses `Path.cwd().parent` to identify the project root. It assumes execution with `Notebook/` as the current working directory.

Verify the working directory before executing the notebook. The notebook's execution from a fresh clone has not yet been independently tested.

### Step 3 — Verify the processed dataset

The Streamlit application expects:

```text
data/processed/occupation_profiles.pkl
```

The matching module loads this file using `pandas.read_pickle()`.

Raw and processed data directories are excluded from Git tracking. Users must prepare these files locally.

Only load pickle files from trusted sources.

## 8. Running CareerMatchAI

After installing dependencies and preparing the processed occupation profiles, launch the application from the project root:

```bash
streamlit run app.py
```

Streamlit will display the local application address in the terminal.

The application provides an interface for skill-based career exploration and its supporting features.

Optional functionality may require additional configuration. In particular, the Ollama advisor may require a locally installed model and running Ollama service.

## 9. Career Matching Methodology

The main career-matching module is located at:

```text
src/matching.py
```

It includes three core functions:

- `load_occupation_profiles()` — loads processed O*NET occupation profiles.
- `create_matching_text()` — combines occupational titles, descriptions, alternate titles, essential skills, and software skills into searchable text.
- `build_tfidf_model()` — constructs TF-IDF representations of occupation profiles.

The TF-IDF model uses English stop-word removal and unigram/bigram features.

Cosine similarity is used to support ranking of candidate-to-occupation matches.

The primary Streamlit application uses the original TF-IDF matching implementation.

## 10. Model Evaluation

The research also evaluates alternative approaches to occupation matching.

### Evaluated Approaches

| Model | Description |
|---|---|
| Original TF-IDF | Baseline occupation matching |
| Bigram TF-IDF | Alternative TF-IDF representation |
| Sentence-BERT | Semantic matching using sentence embeddings |
| Hybrid | Combines TF-IDF similarity with software-skill overlap |

The hybrid experiment uses a weighting of 0.7 for TF-IDF similarity and 0.3 for software-skill overlap.

### Evaluation Setup

The research evaluation uses five synthetic candidate profiles with provisional relevance labels.

Mean Reciprocal Rank at 5 (MRR@5) is used to assess how highly relevant occupations appear in the recommendations.

### Reported Experimental Results

| Matching approach | MRR@5 |
|---|---:|
| Original TF-IDF | 0.700 |
| Bigram TF-IDF | 0.700 |
| Sentence-BERT | 0.600 |
| Hybrid | 0.700 |

These are the reported experimental results from the project's research evaluation, not independently reproduced results from a fresh environment.

The small synthetic evaluation set limits the generalizability of these findings.

### Evaluation Files

```text
evaluate_models.py
evaluate_hybrid.py
evaluation_profiles.json
sentence_bert_matcher.py
src/sentence_bert_matcher.py
```

The evaluation scripts are separate from the primary Streamlit deployment.

## 11. Research Scope and Limitations

CareerMatchAI is an academic research prototype intended to explore skill-based career recommendations.

Current limitations include:

- Evaluation based on a small number of synthetic candidate profiles.
- Dependence on the coverage and quality of occupational data.
- Potential differences between terminology in candidate resumes and occupation profiles.
- Skill similarity does not independently establish job eligibility or hiring suitability.
- Certification and career resource recommendations may require periodic review.
- Optional AI guidance may require additional local configuration.
- Complete clean-environment reproducibility testing remains outstanding.

Future research may explore larger evaluation datasets, stronger skill normalization, improved ranking methods, and additional user-based validation.

## 12. Privacy Considerations

CareerMatchAI is designed with privacy awareness as a project objective.

Users should avoid uploading sensitive personal information unless they understand how their local deployment processes and stores it.

The presence of privacy-related design goals does not constitute a verified guarantee of anonymization, data deletion, or secure processing. These behaviors require separate implementation review and testing.

## 13. Team Development

CareerMatchAI was developed collaboratively, with contributions across:

- Occupational data exploration and preparation
- Occupation-profile construction
- Career matching and similarity evaluation
- Skill-gap analysis
- Streamlit frontend development and integration
- Supporting certification and career guidance features
- Research documentation and experimental evaluation

The repository includes work developed across multiple team branches.

## 14. Reproducibility and Repository Notes

Before treating the repository as fully reproducible, the following should be verified:

- All required application modules are committed.
- Required datasets can be obtained and processed using the documented workflow.
- The processed occupation-profile file is generated in the expected directory.
- Dependencies install successfully in a clean environment.
- The Streamlit application launches successfully.
- The evaluation scripts reproduce the reported results.
- No sensitive files, private resumes, or unnecessary generated artifacts are committed.

The `.gitignore` excludes raw datasets, processed datasets, and generated pickle files.

## 15. References and Resources

O*NET Resource Center
https://www.onetcenter.org/

ESCO — European Skills, Competences, Qualifications and Occupations
https://esco.ec.europa.eu/

Streamlit Documentation
https://docs.streamlit.io/

scikit-learn Documentation
https://scikit-learn.org/stable/

Sentence Transformers Documentation
https://www.sbert.net/

## 16. Project Status

CareerMatchAI is an academic research prototype with an implemented Streamlit frontend, occupation matching modules, skill-gap functionality, and supporting career guidance components.

The repository is being prepared for research documentation, reproducibility review, and academic submission.