# CareerMatchAI

### Career Recommendation and Skill-Gap Analysis Platform

CareerMatchAI is a privacy-aware, skill-based career recommendation platform designed to help students and early-career job seekers identify suitable occupations, understand their existing skills, and explore opportunities for professional development.

The project uses **O*NET occupational data and ESCO skills terminology** to support career exploration. It combines resume skill extraction, TF-IDF-based career matching, skill-gap analysis, certification recommendations, live Adzuna job discovery, preliminary job eligibility notices, and career development resources through an interactive Streamlit application.

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

### Live Job Discovery and Preliminary Eligibility Checks

- Searches current job advertisements through the Adzuna API for a selected occupation and country.
- Matches occupation titles, reduces repeated employer/title combinations, and ranks results using confirmed skill mentions and available experience signals.
- Displays explicit job-description notices about U.S. citizenship, security clearance, work authorization, and sponsorship when detectable.
- Labels requirements **Not verified** when the available description does not establish them.
- Uses Adzuna redirect links; these are not guaranteed to be direct official employer application pages.
- Live search requires personal Adzuna API credentials and an active API allowance. The optional search does not require `employers.csv`.

Job descriptions may be shortened. A title match or keyword overlap does not establish suitability, eligibility, or hiring probability.

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
| Live job search | Adzuna API, requests |
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
│   ├── sentence_bert_matcher.py
│   ├── live_job_matching.py
│   └── resume_profile.py
│
├── app.py
├── career_resources.py
├── certification_catalog.py
├── certification_recommender.py
├── ollama_advisor.py
├── job_postings.py
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

The dependency file should include the application's required packages (verify the current `requirements.txt` before deployment), including:

```text
streamlit
pandas
numpy
scikit-learn
python-docx
pypdf
sentence-transformers
openpyxl
requests
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

### Configure optional live job search (Adzuna)

1. Obtain an application ID and application key from [Adzuna Developer](https://developer.adzuna.com/). API availability and quotas depend on your account.
2. Create `.streamlit/secrets.toml` in the project root with the following placeholders replaced by your own credentials:

   ```toml
   ADZUNA_APP_ID = "YOUR_APPLICATION_ID"
   ADZUNA_APP_KEY = "YOUR_APPLICATION_KEY"
   ```

3. Confirm `.streamlit/secrets.toml` is listed in `.gitignore`; **never commit credentials or personal résumés**.
4. Restart Streamlit and use the live job-search action after selecting an occupation.

Environment variables named `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` are also supported. If deploying to a hosted Streamlit environment, configure credentials using that environment's secrets management; the local secrets file should not be uploaded.

The application makes live API requests when searching. It does not guarantee five suitable jobs, and search results may be incomplete or repeated across cities.

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
- Adzuna job descriptions can be abbreviated, limiting experience and eligibility detection.
- Citizenship, clearance, sponsorship, and work-authorization notices are preliminary text detections, not verified legal or hiring determinations.
- Job-title matching and textual skill overlap do not prove a candidate meets job requirements.
- The current job-skill gap display may surface overly broad terms; review suggestions critically.
- Adzuna redirect URLs may lead through aggregators rather than directly to employers.
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

CareerMatchAI is an academic research prototype with an implemented Streamlit frontend, occupation matching modules, skill-gap functionality, supporting career guidance components, and a locally tested Adzuna live job-search workflow with preliminary eligibility notices.

The repository is being prepared for research documentation, reproducibility review, and academic submission.