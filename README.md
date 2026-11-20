
# CareerMatchAI

### Career Recommendation and Skill-Gap Analysis Platform

CareerMatchAI is a privacy-aware, skill-based career recommendation platform designed to help students and early-career job seekers identify suitable occupations, understand their existing skills, and explore opportunities for professional development.

The project uses **O*NET occupational data and ESCO skills terminology** to support career exploration. It combines resume skill extraction, TF-IDF-based career matching, skill-gap analysis, certification recommendations, live Adzuna job discovery, preliminary job eligibility notices, and career development resources through an interactive Streamlit application.

The project was developed collaboratively as part of an academic research initiative at the University of North Texas.

### Live Application

Access the deployed CareerMatchAI application:

[CareerMatch AI — Live Application](https://careermatchai-4rxw2cebpbnvev4bkzfcez.streamlit.app/)

The application is deployed using Streamlit Community Cloud. Optional live job discovery depends on Adzuna API availability and request limits. The Ollama-based career advisor may require additional configuration.

---

## 1. Research Objectives

CareerMatchAI addresses three research questions:

**RQ1 — Skill-Based Career Recommendation:**

How can standardized occupational data support skill-based occupation recommendations?

**RQ2 — Occupation Matching:**

How effectively do different text similarity approaches rank relevant occupations based on candidate skills?

**RQ3 — Skill-Gap Analysis:**

How can occupational skill information be used to identify potential skill gaps and recommend learning resources?

The platform aims to provide interpretable, skill-based career recommendations and actionable career development information.

---

## 2. Key Features

### Resume Processing and Skill Extraction

- Supports resume processing through the Streamlit interface.
- Includes document-reading support for PDF and DOCX files.
- Extracts skills from candidate-provided information.
- Uses standardized ESCO terminology and O*NET-derived skill information.
- Allows candidates to review and modify identified skills.
- Provides confirmed skill information for downstream career matching.

### Career Recommendations

- Uses structured O*NET occupation profiles.
- Represents occupation information using TF-IDF.
- Applies cosine similarity for skill-based matching.
- Ranks occupations based on their similarity to candidate skills.
- Presents the top five recommended occupations.

### Skill-Gap Analysis

- Compares candidate skills with occupational skill information.
- Identifies potential gaps between confirmed skills and occupation requirements.
- Examines essential skills and software skills.
- Supports exploration of skills relevant to career development.

Skills not identified in a candidate's profile should not be interpreted as definitive evidence that the candidate lacks those skills.

### Certification and Learning Resources

- Includes a certification catalog and recommendation module.
- Provides learning resources to support professional development.
- Includes links to official employer career portals.
- Supports career development planning.

### Live Job Discovery and Preliminary Eligibility Checks

- Searches current job advertisements through the Adzuna API for a selected occupation and country.
- Matches occupation titles, reduces repeated employer/title combinations, and ranks results using confirmed skill mentions and available experience signals.
- Displays explicit job-description notices about U.S. citizenship, security clearance, work authorization, and sponsorship when detectable.
- Labels requirements **Not verified** when the available description does not establish them.
- Uses Adzuna redirect links; these are not guaranteed to be direct official employer application pages.
- Live search requires Adzuna API credentials and an active API allowance.
- The optional search does not require `employers.csv`.

Job descriptions may be shortened. A title match or keyword overlap does not establish suitability, eligibility, or hiring probability.

### AI Career Advisor

- Includes an Ollama-based advisor module for additional career guidance.
- Supports career development exploration.
- Operates separately from the core occupation-ranking methodology.
- May require a separately configured local Ollama environment.

These features are represented in the project code. Full end-to-end testing and validation of all optional components remain to be confirmed.

---

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
| Deployment | Streamlit Community Cloud |

---

## 4. Data Sources

### O*NET

O*NET provides structured occupational information used to construct career profiles.

The project uses occupational information such as:

- Occupation titles and descriptions
- Alternate job titles
- Essential skills
- Software skills
- O*NET-SOC occupation codes

The processed dataset contains 1,016 occupational profiles.

### Occupational Data Summary

| Dataset Characteristic | Count |
|---|---:|
| Total occupational profiles | 1,016 |
| Unique O*NET-SOC codes | 1,016 |
| Duplicate occupation codes | 0 |
| Missing essential skill lists | 106 |
| Missing software skill lists | 93 |
| Missing occupation titles | 0 |
| Missing occupation descriptions | 0 |

Occupational profiles with missing skill lists are retained because occupation titles and descriptions still provide useful information for occupation matching.

Missing skill lists are represented as empty lists rather than introducing unverified skill information.

Official source:

https://www.onetcenter.org/

O*NET database downloads:

https://www.onetcenter.org/database.html

### ESCO

ESCO stands for **European Skills, Competences, Qualifications and Occupations**.

ESCO provides standardized terminology for describing skills, competences, and occupations.

CareerMatchAI uses the English ESCO skills vocabulary alongside O*NET-derived occupational skill and software terminology to support candidate skill extraction.

The occupation-profile loading and TF-IDF matching implementation uses O*NET-derived profiles. ESCO is not used as a separately deployed matching model.

Official source:

https://esco.ec.europa.eu/

### Data Governance

O*NET and ESCO provide publicly accessible occupational and skill information through their respective official platforms.

These datasets are used as reference sources for occupational representation and skill standardization.

Users should review the applicable data usage and licensing terms published by the respective data providers.

Standardized occupational taxonomies may not fully represent emerging skills or changing labor market requirements. Periodic dataset updates may improve the relevance of career recommendations.

---

## 5. Project Structure

```text
CareerMatchAI/
│
├── .streamlit/
│   └── config.toml
│
├── data/
│   ├── raw/
│   │   └── esco/
│   │       └── skills_en.csv
│   └── processed/
│       └── occupation_profiles.pkl
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

The structure reflects the locally documented project files. Some experimental files may remain on separate Git branches until they are committed and merged.

---

## 6. Installation and Setup

### Prerequisites

- Python 3
- Git
- A Python-compatible development environment
- Internet access for dependency installation
- Jupyter Notebook, if regenerating the occupational profiles
- Optional Adzuna API credentials for live job discovery
- Optional Ollama environment for AI career guidance

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Sainapuram/CareerMatchAI.git
cd CareerMatchAI
```

### Step 2 — Create a Virtual Environment

For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

For macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
python -m pip install -r requirements.txt
```

The project's required packages include:

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

The current `requirements.txt` should be used as the primary dependency specification.

Package versions are not yet fully pinned. A clean-environment installation has not been independently verified.

---

## 7. Dataset Preparation

### Provided Dataset Files

The following dataset files are tracked in the project:

```text
data/processed/occupation_profiles.pkl
data/raw/esco/skills_en.csv
```

These files support application execution without requiring users to repeat the complete data preprocessing workflow.

After cloning the repository, verify that both files are available in their expected locations.

If both files are present, users can proceed directly to Section 8 to launch the application.

The O*NET data preparation steps below are required only when regenerating the processed occupation profiles or when the processed dataset is unavailable.

### ESCO Skill Vocabulary

CareerMatchAI incorporates the European Skills, Competences, Qualifications and Occupations (ESCO) vocabulary to support resume skill extraction.

The application uses the English ESCO skills dataset (`skills_en.csv`) alongside O*NET-derived occupational skill and software terminology.

**Implementation:**

- **Data source:** ESCO, European Commission
- **Dataset:** `data/raw/esco/skills_en.csv`
- **Processing module:** `skill_extractor.py`
- **Purpose:** Identify skill terminology in candidate resumes to support career recommendations and skill-gap analysis.

ESCO provides standardized skill terminology, while O*NET supplies occupational profiles used for career matching.

Official ESCO website:

https://esco.ec.europa.eu/

The ESCO vocabulary file is tracked in the project to support application execution and Streamlit Cloud deployment.

### Optional Step 1 — Obtain the Original O*NET Datasets

To regenerate the occupational profiles, obtain the following Excel files:

```text
data/raw/
├── Occupation Data.xlsx
├── Job Titles.xlsx
├── Essential Skills.xlsx
└── Software Skills.xlsx
```

These filenames must match those expected by the preprocessing code.

Datasets can be obtained from the official O*NET Resource Center, subject to the relevant data availability and usage terms.

https://www.onetcenter.org/database.html

The original datasets used during project exploration contained:

| Dataset | Number of Entries |
|---|---:|
| Occupation Data | 1,016 |
| Job Titles | 54,269 |
| Essential Skills | 18,200 |
| Software Skills | 31,821 |

Newer dataset releases may contain different numbers of entries.

### Optional Step 2 — Generate Occupation Profiles

The following notebook contains the data preparation workflow:

```text
Notebook/01_onet_exploration.ipynb
```

It integrates occupational information using the O*NET-SOC code and creates structured occupational profiles.

The resulting dataset is saved as:

```text
data/processed/occupation_profiles.pkl
```

**Important working-directory requirement:**

The notebook currently uses `Path.cwd().parent` to identify the project root. It assumes execution with `Notebook/` as the current working directory.

Verify the working directory before executing the notebook.

Notebook execution from a fresh clone has not yet been independently tested.

### Step 3 — Verify the Processed Dataset

The Streamlit application expects:

```text
data/processed/occupation_profiles.pkl
```

The matching module loads this file using `pandas.read_pickle()`.

The processed O*NET occupation profiles and English ESCO skills vocabulary are tracked to support application execution and reproducibility.

Users who wish to regenerate the occupational profiles can download the original O*NET datasets and execute the data preparation notebook.

Only load pickle files from trusted sources.

---

## 8. Running CareerMatchAI

After installing dependencies and verifying that the required dataset files are available, launch the application from the project root:

```bash
streamlit run app.py
```

Streamlit will display the local application address in the terminal.

The application provides an interactive interface for:

1. Uploading a resume.
2. Extracting and reviewing candidate skills.
3. Exploring recommended occupations.
4. Reviewing potential occupational skill gaps.
5. Exploring certifications and learning resources.
6. Searching available job advertisements through Adzuna.
7. Accessing optional AI-assisted career guidance.

Optional functionality may require additional configuration.

### Configure Optional Live Job Search (Adzuna)

1. Obtain an application ID and application key from [Adzuna Developer](https://developer.adzuna.com/).

2. Create the following file in the project root:

   ```text
   .streamlit/secrets.toml
   ```

3. Add your credentials using the following format:

   ```toml
   ADZUNA_APP_ID = "YOUR_APPLICATION_ID"
   ADZUNA_APP_KEY = "YOUR_APPLICATION_KEY"
   ```

4. Confirm `.streamlit/secrets.toml` is listed in `.gitignore`.

5. Restart Streamlit and use the live job-search action after selecting an occupation.

**Never commit API credentials or personal resumes to GitHub.**

Environment variables named `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` are also supported.

For hosted Streamlit environments, configure credentials using the platform's secrets management system. The local secrets file should not be uploaded.

API availability and request quotas depend on the Adzuna account.

The application makes live API requests when searching. It does not guarantee five suitable jobs, and search results may be incomplete or repeated across cities.

### Optional Ollama Career Advisor

The AI career advisor is implemented in:

```text
ollama_advisor.py
```

Ollama-based functionality may require:

- An installed Ollama environment.
- A compatible language model.
- A running Ollama service.
- Appropriate application configuration.

Official Ollama website:

https://ollama.com/

The advisor is an optional component and is separate from the core TF-IDF occupation-matching method.

Availability of the Ollama advisor in the hosted Streamlit environment has not been independently verified.

---

## 9. Career Matching Methodology

The main career-matching module is located at:

```text
src/matching.py
```

It includes three core functions:

- `load_occupation_profiles()` — loads processed O*NET occupation profiles.
- `create_matching_text()` — combines occupational titles, descriptions, alternate titles, essential skills, and software skills into searchable text.
- `build_tfidf_model()` — constructs TF-IDF representations of occupation profiles.

### Occupational Profile Representation

Occupational information is combined into textual representations using:

- Occupation titles
- Occupation descriptions
- Alternate job titles
- Essential skills
- Software skills

The O*NET-SOC code identifies each occupation.

Missing skill lists are represented as empty lists.

### TF-IDF and Cosine Similarity

TF-IDF transforms textual occupation information into numerical feature representations.

The evaluated TF-IDF configurations include English stop-word removal and unigram/bigram text representations.

Cosine similarity measures the similarity between candidate skill representations and occupation profiles.

Occupations are ranked according to their similarity scores.

The primary Streamlit application uses the original TF-IDF matching implementation.

### Skill-Gap Identification

The skill-gap component compares confirmed candidate skills against occupational skill information.

Potential gaps are identified from essential skills and software skills that are not found in the candidate's confirmed skill profile.

The results support career exploration and learning recommendations rather than definitive assessments of professional competence.

---

## 10. Model Evaluation

The research evaluates alternative approaches to occupation matching to investigate differences in ranking performance.

### Evaluated Approaches

| Model | Description |
|---|---|
| Original TF-IDF | Baseline occupation matching |
| Bigram TF-IDF | Alternative TF-IDF representation using unigram and bigram features |
| Sentence-BERT | Semantic matching using sentence embeddings |
| Hybrid | Combines TF-IDF similarity with software-skill overlap |

### Hybrid Matching

The hybrid experiment combines TF-IDF similarity and software-skill overlap using the following fixed weights:

- TF-IDF similarity: 0.7
- Software-skill overlap: 0.3

The weights were used for experimental comparison and were not established through extensive hyperparameter optimization.

### Semantic Matching

The Sentence-BERT experiment uses semantic sentence embeddings to compare candidate skill representations with occupational profiles.

The evaluated model is:

```text
all-MiniLM-L6-v2
```

Sentence-BERT is evaluated as an alternative matching approach rather than the primary deployed matching model.

### Evaluation Setup

The research evaluation uses five synthetic candidate profiles with predefined occupational relevance labels.

Mean Reciprocal Rank at 5 (MRR@5) is used to assess how highly relevant occupations appear in the recommendations.

For each candidate profile, the reciprocal rank is calculated using the position of the first relevant occupation among the top five recommendations.

If no relevant occupation appears in the top five, the reciprocal rank is zero.

MRR@5 is calculated as the mean of the reciprocal ranks across all evaluated candidate profiles.

### Reported Experimental Results

| Matching Approach | MRR@5 |
|---|---:|
| Original TF-IDF | 0.700 |
| Bigram TF-IDF | 0.700 |
| Sentence-BERT | 0.600 |
| Hybrid | 0.700 |

The original TF-IDF, bigram TF-IDF, and hybrid approaches achieved the same MRR@5 score on the evaluated profiles.

Sentence-BERT achieved a lower MRR@5 score on this limited evaluation set.

These findings do not establish that TF-IDF is generally superior to semantic embedding methods.

The original TF-IDF implementation was retained as the primary application matching approach.

These are the reported experimental results from the original research environment, not independently reproduced results from a fresh environment.

The small synthetic evaluation set limits the generalizability of these findings.

The quantitative evaluation focuses on occupation ranking. The skill-gap and learning recommendation components are demonstrated through the application but have not undergone equivalent quantitative validation.

### Evaluation Files

```text
evaluate_models.py
evaluate_hybrid.py
evaluation_profiles.json
sentence_bert_matcher.py
src/sentence_bert_matcher.py
```

The evaluation scripts are separate from the primary Streamlit deployment.

### Running the Evaluation

After installing the required dependencies and verifying the processed occupation profiles, run the following commands from the project root:

```bash
python evaluate_models.py
python evaluate_hybrid.py
```

The evaluation uses synthetic candidate profiles provided in:

```text
evaluation_profiles.json
```

The scripts compare occupation-matching approaches using MRR@5.

The Sentence-BERT experiment may require internet access to obtain the pretrained model during its initial execution.

The reported results are based on the original research environment. Reproduction may depend on dataset versions, dependency versions, and model availability.

---

## 11. Research Scope and Limitations

CareerMatchAI is an academic research prototype intended to explore skill-based career recommendations.

Current limitations include:

- Evaluation based on a small number of synthetic candidate profiles.
- Limited generalizability of experimental results.
- Dependence on the coverage and quality of occupational data.
- Incomplete occupational skill lists.
- Potential differences between terminology in candidate resumes and occupation profiles.
- Limited quantitative validation of skill-gap and learning recommendations.
- Skill similarity does not independently establish job eligibility or hiring suitability.
- Certification and career resource recommendations may require periodic review.
- Optional AI guidance may require additional local configuration.
- Adzuna job descriptions can be abbreviated, limiting experience and eligibility detection.
- Citizenship, clearance, sponsorship, and work-authorization notices are preliminary text detections, not verified legal or hiring determinations.
- Job-title matching and textual skill overlap do not prove a candidate meets job requirements.
- The current job-skill gap display may surface overly broad terms; review suggestions critically.
- Adzuna redirect URLs may lead through aggregators rather than directly to employers.
- API request limits may restrict live job discovery.
- Complete clean-environment reproducibility testing remains outstanding.

### Future Work

Future research may investigate:

- Larger and more diverse evaluation datasets.
- Additional real-world candidate profiles with appropriate privacy safeguards.
- Stronger skill extraction and normalization approaches.
- Improved semantic and hybrid ranking methods.
- Systematic hyperparameter optimization.
- Additional user-based validation.
- Quantitative evaluation of skill-gap recommendations.
- Periodic updates to occupational datasets.
- Improved explanations of occupation recommendations.
- More comprehensive live job-matching validation.

---

## 12. Privacy Considerations

CareerMatchAI is designed with privacy awareness as a project objective.

Users should avoid uploading sensitive personal information unless they understand how the deployment processes and stores it.

The occupational reference datasets are separate from candidate-provided resume information.

Users are advised to remove unnecessary personal details from resumes before uploading them for research demonstrations.

The presence of privacy-related design goals does not constitute a verified guarantee of anonymization, data deletion, or secure processing.

These behaviors require separate implementation review and testing.

API credentials and personal resumes should never be committed to the public repository.

CareerMatchAI is intended to support career exploration and should not be considered an automated hiring decision system.

---

## 13. Team Development

CareerMatchAI was developed collaboratively as an academic research initiative at the University of North Texas.

### Research Team

- Aparna Naredla
- Devi Sri Sagurupilli
- Shruthika Reddy Sainapuram
- Venkata Pranav Kumar Yarragolla

Project contributions include:

- Occupational data exploration and preparation.
- Occupation-profile construction.
- Resume processing and skill extraction.
- Career matching and similarity evaluation.
- Skill-gap analysis.
- Streamlit frontend development and integration.
- Supporting certification and career guidance features.
- Live job discovery integration.
- Application deployment.
- Research documentation and experimental evaluation.

The repository includes work developed across multiple team branches.

---

## 14. Reproducibility and Repository Notes

### Tracked Dataset Files

The processed occupation profiles and ESCO skills vocabulary are tracked in the project to support application execution and research reproducibility.

```text
data/processed/occupation_profiles.pkl
data/raw/esco/skills_en.csv
```

Additional raw O*NET datasets required for regenerating the occupational profiles can be obtained from the official O*NET database.

Users do not need to regenerate the processed occupational profiles when the required tracked dataset files are available.

### Reproducibility Checklist

Before treating the repository as fully reproducible, the following should be verified:

- All required application and evaluation modules are committed and available on the intended repository branch.
- Both tracked dataset files are available after cloning the repository.
- Required original datasets can be obtained and processed using the documented workflow.
- The processed occupation-profile file is generated in the expected directory when preprocessing is repeated.
- Dependencies install successfully in a clean environment.
- The Streamlit application launches successfully.
- The evaluation scripts reproduce the reported results.
- Optional features operate when their required credentials and services are configured.
- No sensitive files, private resumes, or unnecessary generated artifacts are committed.

The exact source dataset release versions and complete dependency versions should be recorded when available to improve long-term reproducibility.

### Source Code

GitHub repository:

https://github.com/Sainapuram/CareerMatchAI

### Deployed Application

https://careermatchai-4rxw2cebpbnvev4bkzfcez.streamlit.app/

---

## 15. References and Resources

### Occupational Data

**O*NET Resource Center**

https://www.onetcenter.org/

**O*NET Database Downloads**

https://www.onetcenter.org/database.html

**ESCO — European Skills, Competences, Qualifications and Occupations**

https://esco.ec.europa.eu/

### Development and Machine Learning

**Streamlit Documentation**

https://docs.streamlit.io/

**scikit-learn Documentation**

https://scikit-learn.org/stable/

**Sentence Transformers Documentation**

https://www.sbert.net/

**Sentence-BERT Research Paper**

Reimers, N., and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.

https://aclanthology.org/D19-1410/

### External Services

**Adzuna Developer API**

https://developer.adzuna.com/

**Ollama**

https://ollama.com/

---

## 16. Project Status

CareerMatchAI is an academic research prototype with:

- An implemented Streamlit frontend.
- O*NET-based occupation profiles.
- ESCO-supported resume skill extraction.
- TF-IDF-based occupation recommendation.
- Occupational skill-gap analysis.
- Certification and career development resources.
- Comparative occupation-ranking experiments.
- A locally tested Adzuna live job-search workflow with preliminary eligibility notices.
- A deployed Streamlit application.

The project demonstrates the integration of standardized occupational information, skill extraction, occupation ranking, and skill-gap analysis within a unified career exploration platform.

The current implementation supports academic research and demonstration purposes.

Further validation, reproducibility testing, and evaluation on larger datasets are necessary before considering the system suitable for broader production use.

---

