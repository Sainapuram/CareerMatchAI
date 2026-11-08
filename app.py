import re
import html
import hashlib
from urllib.parse import quote
import streamlit as st
from docx import Document
from pypdf import PdfReader
from src.matching import load_occupation_profiles, build_tfidf_model, recommend_careers
from src.skill_gap import analyze_skill_gap
from ollama_advisor import show_ai_advisor
from career_resources import learning_resources, official_employer_portals
from certification_recommender import select_certification
from certification_catalog import CERTIFICATION_CATALOG
from skill_extractor import build_skill_index, extract_skills_with_evidence
# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="CareerMatch AI | Career Advisor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# ==========================================
# 2. CUSTOM STYLING
# ==========================================
st.markdown(
    """
<style>
:root { color-scheme: light; }
.stApp, [data-testid="stAppViewContainer"] { background: linear-gradient(135deg,#F4F6FF 0%,#EDF3FF 52%,#F5F0FF 100%) !important; color:#24324B !important; }
.block-container { max-width:none !important; width:100% !important; padding:1.5rem clamp(1.5rem,3.5vw,4.5rem) 4rem !important; }
[data-testid="stHeader"] { background:rgba(244,246,255,.94) !important; }
[data-testid="stSidebar"] { background:#F0F2FF !important; }
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp label { color:#24324B !important; }
.stApp h1 {font-size:2.6rem !important;} .stApp h2 {font-size:2rem !important;} .stApp h3 {font-size:1.65rem !important;} .stApp h4 {font-size:1.3rem !important;}
.stApp p,.stApp li,.stApp label,.stApp [data-testid="stMarkdownContainer"] {font-size:1.06rem;line-height:1.65;}
.stApp [data-testid="stCaptionContainer"],.stApp small {color:#52617A !important;font-size:.96rem !important;line-height:1.55 !important;}
.hero {background:linear-gradient(112deg,#4145A4 0%,#6254B8 55%,#8472CC 100%);border:1px solid #8178C7;border-radius:22px;padding:2.3rem clamp(1.7rem,3vw,3rem);margin-bottom:1.5rem;box-shadow:0 14px 35px #3E4C8922;}
.hero h1 {color:#FFFFFF !important;font-size:clamp(2.4rem,3.2vw,3.3rem) !important;margin:0 0 .5rem;}
.hero p {color:#F5F4FF !important;font-size:1.17rem !important;line-height:1.6;margin:0;}
.hero-label {color:#E4DDFF;font-size:.95rem;font-weight:800;letter-spacing:.09em;margin-bottom:.7rem;}
.section-label {color:#5145A5;font-size:1rem;font-weight:800;letter-spacing:.06em;margin-top:1.3rem;}
.section-description {color:#4D5B73;font-size:1.07rem;margin-bottom:1rem;}
[data-testid="stMetric"],[data-testid="stVerticalBlockBorderWrapper"] > div {background:#FFFFFF !important;border:1px solid #D9DEF5 !important;border-radius:16px !important;}
[data-testid="stMetricValue"] {color:#4B49B0 !important;font-size:2.2rem !important;}
.stButton > button[kind="primary"],.stDownloadButton > button {background:#5148B6 !important;color:#FFFFFF !important;border:1px solid #5148B6 !important;border-radius:12px;font-weight:750;min-height:2.9rem;}
.stButton > button[kind="primary"]:hover {background:#3F379B !important;}
.stButton > button,[data-testid="stBaseButton-secondary"] {border-radius:12px;min-height:2.8rem;font-size:1rem !important;}
[data-testid="stTabs"] [data-baseweb="tab-list"] {gap:.75rem;padding:.7rem;background:#E4E8FB;border:1px solid #CDD4F0;border-radius:16px;margin-bottom:1.4rem;}
[data-testid="stTabs"] button[role="tab"] {flex:1;min-height:3.8rem;background:#FFFFFF;border-radius:11px;color:#3E4B6C !important;font-size:1.12rem !important;font-weight:750;padding:.7rem;}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {background:#5148B6 !important;color:#FFFFFF !important;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],[data-testid="stTabs"] [data-baseweb="tab-border"] {display:none;}
[data-testid="stExpander"],[data-testid="stFileUploader"],[data-testid="stDataFrame"],[data-testid="stAlert"] {border-radius:13px;}
[data-testid="stAlert"] {border:1px solid #CED6F2;}
[data-testid="stDataFrame"] {border:1px solid #D4D9EF;}
.stApp input,.stApp textarea {font-size:1.07rem !important;}
.stApp [data-baseweb="input"],.stApp [data-baseweb="textarea"],.stApp [data-baseweb="select"] > div {background:#FFFFFF !important;color:#24324B !important;border-color:#C7D0EA !important;}
.stApp [data-baseweb="tag"] {background:#E4DEFF !important;color:#383078 !important;border-radius:8px;}
.stApp [data-baseweb="tag"] span {color:#383078 !important;}
.stApp [data-baseweb="segmented-control"] button {font-size:1.03rem !important;}
.skill-tag {display:inline-block;background:#E6E5FF;color:#41388D;padding:9px 14px;border:1px solid #B9B5EB;border-radius:22px;font-size:1rem;margin:5px;}
.footer {text-align:center;color:#596681;padding:1.5rem;font-size:1rem;}
a {color:#5148B6 !important;}
/* Readable controls and consistent purple/white contrast */
.stApp p,.stApp li,.stApp label,.stApp [data-testid="stMarkdownContainer"] {font-size:1.12rem !important;line-height:1.65 !important;}
.stApp [data-testid="stCaptionContainer"] {font-size:1rem !important;color:#485779 !important;}
.stApp button {font-size:1.05rem !important;}
.stApp .stButton button[kind="primary"],.stApp .stButton button[kind="primary"] p,
.stApp [data-testid="stTabs"] button[aria-selected="true"],.stApp [data-testid="stTabs"] button[aria-selected="true"] p {color:#FFFFFF !important;}
.stApp [data-testid="stSegmentedControl"] button[aria-pressed="true"],
.stApp [data-testid="stSegmentedControl"] button[aria-pressed="true"] p {background:#5148B6 !important;color:#FFFFFF !important;}
.career-card {background:#FFFFFF;border:1px solid #CDD4F0;border-left:5px solid #6254B8;border-radius:15px;padding:1.1rem 1.35rem;margin:.75rem 0;box-shadow:0 4px 16px #363D7310;}
.career-card h4 {margin:0 0 .3rem !important;color:#30345C !important;font-size:1.4rem !important;}
.career-card p {margin:0 !important;color:#4D5B73 !important;}
.career-card .rank {color:#5148B6;font-weight:800;font-size:.95rem;}
</style>
""", unsafe_allow_html=True,
)
# ==========================================
# 3. RESUME PROCESSING
# ==========================================
def extract_docx_text(uploaded_file):
    document = Document(uploaded_file)
    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
    ]
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                paragraphs.append(cell.text)
    return "\n".join(paragraphs)
def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )
def remove_email(text):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    return re.sub(pattern, "[EMAIL REMOVED]", text)
def remove_phone(text):
    pattern = r"(?<!\w)(?:\+1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\w)"
    return re.sub(pattern, "[PHONE REMOVED]", text)
def clean_resume_text(text):
    text = remove_email(text)
    text = remove_phone(text)
    return text
# ==========================================
# 4. SKILL EXTRACTION
# ==========================================
@st.cache_resource(show_spinner="Loading O*NET and ESCO skill vocabulary...")
def get_skill_index():
    """Load once per Streamlit server session, not on every rerun."""
    return build_skill_index(load_occupation_profiles())
def detect_resume_skills(text):
    """Keep direct matches distinct from review-required ESCO aliases."""
    return extract_skills_with_evidence(text, get_skill_index())
def occupation_names(entries, field):
    """Extract unique O*NET names without changing source data."""
    names = []
    seen = set()
    if not isinstance(entries, list):
        return names
    for item in entries:
        if not isinstance(item, dict):
            continue
        name = item.get(field)
        if isinstance(name, str) and name.strip():
            value = name.strip()
            if value.casefold() not in seen:
                names.append(value)
                seen.add(value.casefold())
    return names
def show_learning_resources(skill):
    """Search links, not verified course or certification endorsements."""
    search_term = quote(skill)
    st.markdown(
        f"[{skill} — Microsoft Learn search]"
        f"(https://learn.microsoft.com/en-us/search/?terms={search_term})"
    )
    st.markdown(
        f"[{skill} — Coursera course search]"
        f"(https://www.coursera.org/search?query={search_term})"
    )
# ==========================================
# 5. SESSION STATE
# ==========================================
if "resume_id" not in st.session_state:
    st.session_state.resume_id = None
if "skills_selection" not in st.session_state:
    st.session_state.skills_selection = []
if "suggested_skill_matches" not in st.session_state:
    st.session_state.suggested_skill_matches = []
if "suggested_skills_selection" not in st.session_state:
    st.session_state.suggested_skills_selection = []
if "direct_skill_matches" not in st.session_state:
    st.session_state.direct_skill_matches = []
if "custom_skills" not in st.session_state:
    st.session_state.custom_skills = []
if "profile_visible" not in st.session_state:
    st.session_state.profile_visible = False
if "career_matches" not in st.session_state:
    st.session_state.career_matches = None
if "career_matches_skills" not in st.session_state:
    st.session_state.career_matches_skills = None

if "approved_skill_equivalences" not in st.session_state:
    st.session_state.approved_skill_equivalences = set()


def update_skill_equivalence(candidate_skill, required_skill, widget_key):
    """Apply or revoke an approved skill-name equivalence across careers."""
    pair = (candidate_skill.casefold(), required_skill.casefold())
    if st.session_state[widget_key]:
        st.session_state.approved_skill_equivalences.add(pair)
    else:
        st.session_state.approved_skill_equivalences.discard(pair)

def add_custom_skill():
    new_skill = st.session_state.custom_skill_input.strip()
    if not new_skill:
        st.session_state.skill_message = "Please enter a skill."
        return
    if len(new_skill) > 60:
        st.session_state.skill_message = "Skill name must be 60 characters or less."
        return
    existing = st.session_state.custom_skills + st.session_state.skills_selection
    existing_match = next((skill for skill in existing
                           if skill.casefold() == new_skill.casefold()), None)
    skill = existing_match or new_skill
    if skill not in st.session_state.custom_skills:
        st.session_state.custom_skills.append(skill)
    if skill not in st.session_state.skills_selection:
        st.session_state.skills_selection.append(skill)
    st.session_state.custom_skill_input = ""
    st.session_state.skill_message = "Skill added successfully."
# ==========================================
# 6. HERO HEADER
# ==========================================
st.markdown(
    """
<div class="hero">
    <div class="hero-label">
        ✦ YOUR INTELLIGENT CAREER COMPANION
    </div>
    <h1>CareerMatch AI</h1>
    <p>
        Explore careers, see your skills, and find your next step.
    </p>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown("**Follow these 3 steps.** Select a numbered tab to move between steps.")
step1, step2, step3 = st.tabs([
    "1  ·  Your goal", "2  ·  Your skills", "3  ·  Your results"
])
with step1:
    # ==========================================
    # 7. CAREER GOAL SELECTION
    # ==========================================
    st.markdown(
        '<div class="section-label">01 / YOUR DIRECTION</div>',
        unsafe_allow_html=True,
    )
    st.subheader("What do you want to do?")
    st.markdown(
        '<div class="section-description">'
        'Choose one option to get started.'
        '</div>',
        unsafe_allow_html=True,
    )
    goal_options = {
        "Explore Career": {
            "icon": "🧭",
            "description": "Discover careers that match your interests.",
        },
        "Change Career": {
            "icon": "🔄",
            "description": "Transition into a different profession.",
        },
        "Grow Career": {
            "icon": "📈",
            "description": "Advance in your current career.",
        },
    }
    career_goal = st.segmented_control(
        "Choose your career path",
        options=list(goal_options.keys()),
        default="Explore Career",
        selection_mode="single",
        width="stretch",
    )
    if career_goal is None:
        career_goal = "Explore Career"
    goal_details = goal_options[career_goal]
    st.info(
        goal_details["icon"] + " " +
        goal_details["description"]
    )
    # ==========================================
    # 8. CAREER PREFERENCES
    # ==========================================
    st.write("")
    st.markdown(
        '<div class="section-label">02 / YOUR AMBITIONS</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Your career goals")
    left_col, right_col = st.columns(2, gap="large")
    with left_col:
        current_career = ""
        if career_goal in ["Change Career", "Grow Career"]:
            current_career = st.text_input(
                "Current profession",
                placeholder="e.g., Teacher, Software Developer",
            )
        target_career = st.text_input(
            "Target career (optional)",
            placeholder="e.g., Data Analyst",
        )
    with right_col:
        experience_years = st.number_input(
            "Years of professional experience",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
        )
        learning_hours = st.number_input(
            "Hours available for learning per week",
            min_value=0,
            max_value=80,
            value=5,
            step=1,
        )
    career_interests = st.text_area(
        "What interests you? (optional)",
        placeholder=(
            "Tell us what you enjoy, what you're good at, "
            "and what kind of career you're looking for."
        ),
        height=110,
    )

    st.info("Next: open **2 · Your skills** to upload a résumé or add skills.")
with step2:
    # ==========================================
    # 9. RESUME UPLOAD
    # ==========================================
    st.write("")
    st.markdown(
        '<div class="section-label">03 / YOUR BACKGROUND</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Upload your résumé")
    st.caption(
        "Optional — PDF or DOCX, maximum 5 MB. "
        "You can also enter your skills manually."
    )
    uploaded_file = st.file_uploader(
        "Upload your résumé",
        type=["pdf", "docx"],
        max_upload_size=5,
        label_visibility="collapsed",
    )
    extracted_skills = []
    resume_text = ""
    if uploaded_file is not None:
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("Maximum file size is 5 MB.")
            st.stop()
        try:
            if uploaded_file.name.lower().endswith(".pdf"):
                resume_text = extract_pdf_text(uploaded_file)
            elif uploaded_file.name.lower().endswith(".docx"):
                resume_text = extract_docx_text(uploaded_file)
            else:
                st.error("Unsupported file format.")
                st.stop()
        except Exception:
            st.error(
                "Unable to process this résumé. "
                "Please upload a valid PDF or DOCX file."
            )
            st.stop()
        if resume_text.strip():
            cleaned_resume = clean_resume_text(resume_text)
            try:
                extraction = detect_resume_skills(cleaned_resume)
            except (FileNotFoundError, ValueError, KeyError) as exc:
                st.error("Could not load the skill vocabulary. Check the ESCO CSV and O*NET dataset.")
                # Technical details are intentionally not shown to end users.
                pass
                st.stop()
            resume_direct_matches = extraction["direct"]
            resume_suggestions = extraction["suggested"]
            extracted_skills = [item["skill"] for item in resume_direct_matches]
            st.success("Résumé uploaded. Review your skills below.")

        else:
            st.warning(
                "No readable text was found. "
                "Scanned PDFs may require OCR."
            )
    # ==========================================
    # 10. SKILL EDITING
    # ==========================================
    st.write("")
    st.markdown(
        '<div class="section-label">04 / YOUR STRENGTHS</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Check your skills")
    st.caption(
        "Review skills found in your résumé, approve suggested "
        "matches, or add skills manually."
    )
    # Identify a new résumé so previous selections do not
    # accidentally carry over to a different uploaded résumé.
    current_resume_id = None
    if uploaded_file is not None and resume_text.strip():
        current_resume_id = hashlib.sha256(
            uploaded_file.getvalue()
        ).hexdigest()
    if current_resume_id != st.session_state.resume_id:
        st.session_state.resume_id = current_resume_id
        st.session_state.approved_skill_equivalences = set()
        for key in list(st.session_state):
            if key.startswith("skill_equivalence_checkbox_"):
                del st.session_state[key]

        st.session_state.direct_skill_matches = list(
            resume_direct_matches
        )
        st.session_state.suggested_skill_matches = list(
            resume_suggestions
        )
        st.session_state.skills_selection = list(extracted_skills)
        st.session_state.suggested_skills_selection = []
        st.session_state.custom_skills = []
        st.session_state.profile_visible = False
        st.session_state.career_matches = None
    # ------------------------------------------
    # A. DIRECT RÉSUMÉ MATCHES
    # ------------------------------------------
    direct_matches = st.session_state.direct_skill_matches
    if direct_matches:
        with st.expander(
            f"Direct résumé matches ({len(direct_matches)})",
            expanded=False,
        ):
            st.caption(
                "These skill names were found in your résumé. "
                "You can remove any incorrect matches below."
            )
            for item in direct_matches:
                st.write(
                    f"{item['skill']} — "
                    f"matched: {item['matched_text']}"
                )
    # ------------------------------------------
    # B. ESCO SUGGESTED MATCHES
    # ------------------------------------------
    suggestions = st.session_state.suggested_skill_matches
    if suggestions:
        st.markdown("Suggested skills for your review")
        st.caption(
            "These were identified using ESCO alternative labels. "
            "Only approve skills that accurately describe your experience."
        )
        suggestion_labels = {
            item["skill"]: (
                f"{item['skill']} "
                f"(résumé phrase: {item['matched_text']})"
            )
            for item in suggestions
        }
        st.multiselect(
            "Approve suggested skills",
            options=list(suggestion_labels.keys()),
            format_func=lambda skill: suggestion_labels[skill],
            key="suggested_skills_selection",
            placeholder="Choose skills to approve",
        )
    # ------------------------------------------
    # C. EDIT DIRECT AND MANUALLY ADDED SKILLS
    # ------------------------------------------
    st.markdown("Edit your skills")
    direct_skill_names = [
        item["skill"] for item in direct_matches
    ]
    # Keep every direct match available even if the user
    # removes it from the selected skills.
    skill_options = sorted(
        set(direct_skill_names)
        | set(st.session_state.custom_skills)
        | set(st.session_state.skills_selection),
        key=str.casefold,
    )
    st.multiselect(
        "Select skills you have",
        options=skill_options,
        key="skills_selection",
        help=(
            "Direct résumé matches start selected. "
            "Remove incorrect skills or add your own below."
        ),
    )
    st.text_input(
        "Add a skill manually",
        placeholder="Enter a skill not identified in your résumé",
        key="custom_skill_input",
    )
    st.button(
        "Add Skill",
        on_click=add_custom_skill,
    )
    if "skill_message" in st.session_state:
        st.info(st.session_state.skill_message)
        del st.session_state.skill_message
    # ------------------------------------------
    # D. COMBINE CONFIRMED SKILLS
    # ------------------------------------------
    # Explicitly approved ESCO suggestions are included
    # alongside the user's selected direct/custom skills.
    # Neither group independently verifies proficiency.
    confirmed_lookup = {}
    for skill in (
        list(st.session_state.skills_selection)
        + list(st.session_state.suggested_skills_selection)
    ):
        normalized = skill.strip().casefold()
        if normalized and normalized not in confirmed_lookup:
            confirmed_lookup[normalized] = skill.strip()
    confirmed_skills = sorted(
        confirmed_lookup.values(),
        key=str.casefold,
    )
    # ------------------------------------------
    # E. CONFIRMED SKILLS DISPLAY
    # ------------------------------------------
    if confirmed_skills:
        st.success(f"{len(confirmed_skills)} skills selected. You can edit them above.")
    else:
        st.info(
            "No skills selected yet. Upload a résumé "
            "or add skills manually."
        )
    st.caption(
        "Selected skills are user-reported and have not "
        "been independently verified."
    )

    st.info("Next: open **3 · Your results** to see your profile and career matches.")
with step3:
    # ==========================================
    # 11. CAREER PROFILE DASHBOARD
    # ==========================================
    st.write("")
    st.markdown(
        '<div class="section-label">05 / YOUR CAREER PROFILE</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Your profile")
    summary1, summary2, summary3 = st.columns(3)
    summary1.metric("Skills selected", len(confirmed_skills))
    summary2.metric("Experience (years)", experience_years)
    summary3.metric("Learning hours/week", learning_hours)
    with st.expander("View your career goal and profile details"):
        st.write("Career goal:", career_goal)
        if current_career.strip():
            st.write("Current career:", current_career)
        if target_career.strip():
            st.write("Career of interest:", target_career)
        if career_interests.strip():
            st.write("Interests:", career_interests)
        st.caption("Experience and interests do not currently affect the career ranking.")
    # ==========================================
    # 12. CAREER RECOMMENDATIONS
    # ==========================================
    st.write("")
    st.markdown(
        '<div class="section-label">06 / YOUR CAREER MATCHES</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Your top career matches")
    st.write("Find five careers related to your selected skills. Select one to see details.")
    with st.expander("How are careers suggested?"):
        st.write("We compare your selected skills with O*NET occupation descriptions using text similarity. These are ideas to explore, not hiring predictions.")
        st.write("For career changes, your target role can influence the results. For career growth, current and target roles can influence them. Experience and interests are not used in ranking.")
    @st.cache_resource(
        show_spinner="Preparing occupation recommendations..."
    )
    def get_career_model():
        occupations = load_occupation_profiles()
        return build_tfidf_model(occupations)
    def build_mode_query(skills, mode, current_role, target_role):
        """Create a transparent, exploratory search query; not a validated career score."""
        query = list(skills)
        if mode == "Change Career" and target_role.strip():
            query.append(target_role.strip())
        elif mode == "Grow Career":
            if current_role.strip():
                query.append(current_role.strip())
            if target_role.strip():
                query.append(target_role.strip())
        return query
    def mode_recommendations(skills, mode, current_role, target_role,
                             profiles, vectorizer, matrix):
        query = build_mode_query(skills, mode, current_role, target_role)
        # Retrieve extra candidates so a career-change search can exclude the
        # user's current occupation without returning fewer than five matches.
        recommendations = recommend_careers(
            query, profiles, vectorizer, matrix, top_n=30
        )
        if mode == "Change Career" and current_role.strip():
            current_normalized = current_role.strip().casefold()
            recommendations = recommendations.loc[
                recommendations["Title"].astype(str).str.strip().str.casefold()
                != current_normalized
            ]
        return recommendations.head(5).copy()
    # Preserve recommendations when Streamlit reruns.
    # Reset recommendations if confirmed skills change.
    current_skills_key = (
        tuple(sorted(set(confirmed_skills), key=str.casefold)),
        career_goal,
        current_career.strip().casefold(),
        target_career.strip().casefold(),
    )
    if st.session_state.career_matches_skills != current_skills_key:
        st.session_state.career_matches = None
        st.session_state.career_matches_skills = current_skills_key
    if not confirmed_skills:
        st.info(
            "Select at least one skill above to see career recommendations."
        )
    else:
        if st.button(
            "🎯 Find 5 careers",
            type="primary",
            use_container_width=True,
        ):
            try:
                profiles, vectorizer, occupation_matrix = (
                    get_career_model()
                )
                matches = mode_recommendations(
                    confirmed_skills,
                    career_goal,
                    current_career,
                    target_career,
                    profiles,
                    vectorizer,
                    occupation_matrix,
                )
                if (
                    matches.empty
                    or matches["Similarity Score"].max() <= 0
                ):
                    st.session_state.career_matches = None
                    st.warning(
                        "No meaningful text overlap was found "
                        "for these skills. Try adding more "
                        "specific skills."
                    )
                else:
                    st.session_state.career_matches = matches.copy()
            except (
                FileNotFoundError,
                ImportError,
                KeyError,
                ValueError,
                TypeError,
            ) as exc:
                st.session_state.career_matches = None
                st.error(
                    "Career recommendations could not be loaded. "
                    "Check that data/processed/occupation_profiles.pkl "
                    "and src/matching.py are present and compatible."
                )
                # Technical details are intentionally not shown to end users.
                pass
        matches = st.session_state.career_matches
        if matches is not None:
            st.markdown("#### Explore your five suggestions")
            for rank, (_, career_row) in enumerate(matches.iterrows(), start=1):
                career_title = html.escape(str(career_row.get("Title", "Career")))
                description = career_row.get("Description", "")
                short_description = ""
                if isinstance(description, str) and description.strip():
                    short_description = description.strip().split(". ")[0].rstrip(".") + "."
                    if len(short_description) > 200:
                        short_description = short_description[:197].rsplit(" ", 1)[0] + "…"
                st.markdown(
                    f'<div class="career-card"><span class="rank">SUGGESTION {rank}</span>'
                    f'<h4>{career_title}</h4><p>{html.escape(short_description or "Explore this career and compare your skills below.")}</p></div>',
                    unsafe_allow_html=True,
                )
            with st.expander("Technical ranking details"):
                st.dataframe(
                    matches[["O*NET-SOC Code", "Title", "Similarity Score"]].rename(
                        columns={"O*NET-SOC Code": "O*NET code", "Title": "Career", "Similarity Score": "Text similarity"}
                    ),
                    hide_index=True,
                    use_container_width=True,
                )
                st.caption("Similarity is not a career-fit percentage or likelihood of employment.")
            # ==================================
            # 13. SKILL-GAP ANALYSIS
            # ==================================
            st.markdown("### Your skills for this career")
            st.caption(
                "Choose a career to explore to compare your "
                "confirmed skills with its O*NET profile."
            )
            # Occupation codes are used to uniquely
            # identify recommended careers.
            career_codes = (
                matches["O*NET-SOC Code"]
                .astype(str)
                .tolist()
            )
            career_labels = dict(
                zip(
                    career_codes,
                    matches["Title"].astype(str).tolist(),
                )
            )
            selected_code = st.selectbox(
                "Choose a career to explore",
                options=career_codes,
                format_func=lambda code: career_labels.get(
                    code, code
                ),
                key="selected_career_code",
            )
            try:
                profiles, _, _ = get_career_model()
                selected_rows = profiles.loc[
                    profiles["O*NET-SOC Code"].astype(str)
                    == selected_code
                ]
                if selected_rows.empty:
                    st.warning(
                        "This occupation could not be found "
                        "in the O*NET data."
                    )
                else:
                    occupation = selected_rows.iloc[0]
                    essential_entries = occupation.get(
                        "Essential Skills", []
                    )
                    software_entries = occupation.get(
                        "Software Skills", []
                    )
                    if not isinstance(essential_entries, list):
                        essential_entries = []
                    if not isinstance(software_entries, list):
                        software_entries = []
                    # Extract essential skill names.
                    essential_names = [
                        item["Element Name"].strip()
                        for item in essential_entries
                        if isinstance(item, dict)
                        and isinstance(
                            item.get("Element Name"), str
                        )
                        and item["Element Name"].strip()
                    ]
                    # Extract software technology names.
                    software_names = [
                        item["Workplace Example"].strip()
                        for item in software_entries
                        if isinstance(item, dict)
                        and isinstance(
                            item.get("Workplace Example"), str
                        )
                        and item["Workplace Example"].strip()
                    ]
                    # Compare both categories with session-wide user approvals.
                    approved_pairs = st.session_state.approved_skill_equivalences

                    essential_result = analyze_skill_gap(
                        confirmed_skills,
                        essential_names,
                        approved_equivalences=approved_pairs,
                    )
                    software_result = analyze_skill_gap(
                        confirmed_skills,
                        software_names,
                        approved_equivalences=approved_pairs,
                    )

                    possible_pairs = {
                        (item["candidate_skill"], item["required_skill"])
                        for result in (essential_result, software_result)
                        for item in result["possible_matches"]
                    }

                    # Display approvals only if both skills are relevant to
                    # the currently selected profile and occupation.
                    candidate_lookup = {
                        skill.casefold(): skill for skill in confirmed_skills
                    }
                    required_lookup = {
                        skill.casefold(): skill
                        for skill in essential_names + software_names
                    }
                    visible_pairs = set(possible_pairs)
                    for candidate_key, required_key in approved_pairs:
                        if (candidate_key in candidate_lookup
                                and required_key in required_lookup):
                            visible_pairs.add((
                                candidate_lookup[candidate_key],
                                required_lookup[required_key],
                            ))

                    if visible_pairs:
                        with st.expander(
                            "Review possible skill equivalences",
                            expanded=bool(possible_pairs),
                        ):
                            st.caption(
                                "These are suggested name equivalences, not "
                                "proof of proficiency. Approve only if both "
                                "names describe a skill you possess. You can "
                                "uncheck an approval at any time."
                            )
                            for candidate_skill, required_skill in sorted(
                                visible_pairs,
                                key=lambda pair: (
                                    pair[0].casefold(), pair[1].casefold()
                                ),
                            ):
                                pair = (
                                    candidate_skill.casefold(),
                                    required_skill.casefold(),
                                )
                                widget_key = (
                                    "skill_equivalence_checkbox_"
                                    + hashlib.sha256(
                                        (pair[0] + "|" + pair[1]).encode("utf-8")
                                    ).hexdigest()[:16]
                                )
                                # Synchronize with stored approvals when a widget
                                # reappears after switching between occupations.
                                if widget_key not in st.session_state:
                                    st.session_state[widget_key] = pair in approved_pairs
                                st.checkbox(
                                    f"{candidate_skill} → {required_skill}",
                                    key=widget_key,
                                    on_change=update_skill_equivalence,
                                    args=(candidate_skill, required_skill, widget_key),
                                )

                    # Recalculate all dependent metrics and learning suggestions
                    # using the latest shared approvals.
                    essential_result = analyze_skill_gap(
                        confirmed_skills,
                        essential_names,
                        approved_equivalences=st.session_state.approved_skill_equivalences,
                    )
                    software_result = analyze_skill_gap(
                        confirmed_skills,
                        software_names,
                        approved_equivalences=st.session_state.approved_skill_equivalences,
                    )

                    st.markdown("### What does this career involve?")
                    description = occupation.get("Description", "")
                    if isinstance(description, str) and description.strip():
                        sentences = re.split(r"(?<=[.!?])\s+", description.strip())
                        st.write(" ".join(sentences[:2]))
                        if len(sentences) > 2:
                            with st.expander("Read full career description"):
                                st.write(description.strip())
                    st.caption("Suggested because your selected skills overlap with this occupation's O*NET text and skills.")
                    # --------------------------
                    # ESSENTIAL SKILLS
                    # --------------------------
                    st.markdown("### Your skills compared")
                    st.markdown("#### Important skills for this career")
                    st.caption(
                        "These results measure overlap with "
                        "declared skills, not verified proficiency "
                        "or job readiness."
                    )
                    if essential_names:
                        essential_col1, essential_col2 = (
                            st.columns(2)
                        )
                        with essential_col1:
                            st.metric(
                                "Skills you listed",
                                essential_result["matched_count"],
                            )
                        with essential_col2:
                            st.metric(
                                "To review",
                                essential_result["missing_count"],
                            )
                        st.markdown("Skills you listed")
                        if essential_result["matched_skills"]:
                            st.success(
                                ", ".join(
                                    essential_result["matched_skills"]
                                )
                            )
                        else:
                            st.info(
                                "No essential skills were matched "
                                "with your confirmed skills."
                            )
                        with st.expander("Skills to review (not necessarily missing)"):
                            if essential_result["missing_skills"]:
                                st.write(", ".join(essential_result["missing_skills"]))
                            else:
                                st.success("All listed skill names matched.")
                    else:
                        st.info(
                            "No essential skills are listed "
                            "for this occupation."
                        )
                    # --------------------------
                    # SOFTWARE SKILLS
                    # --------------------------
                    st.markdown(
                        "#### Tools used in this career"
                    )
                    st.metric(
                        "Tools you already know",
                        software_result["matched_count"],
                    )
                    if software_result["matched_skills"]:
                        st.success(
                            ", ".join(
                                software_result["matched_skills"]
                            )
                        )
                    else:
                        st.info(
                            "No software technologies were matched "
                            "with your confirmed skills."
                        )
                    with st.expander("About these tool matches"):
                        st.write(f"O*NET lists {len(software_names)} software entries for this career. These are examples, not mandatory tools.")
                    # --------------------------
                    # ONE CAREER-AWARE CERTIFICATION
                    # --------------------------
                    st.markdown("### Recommended certification")
                    # Match catalog credentials to unconfirmed occupation skills.
                    # No hardcoded occupation-category restriction is applied.
                    occupation_skill_names = essential_names + software_names
                    certification = select_certification(
                        confirmed_skills,
                        occupation_skill_names,
                        CERTIFICATION_CATALOG,
                        approved_equivalences=st.session_state.approved_skill_equivalences,
                    )
                    if certification is None:
                        st.info(
                            "No credential in our small curated catalog has a direct "
                            "skill-name overlap with the selected occupation's "
                            "unconfirmed skills. This does not mean no suitable "
                            "credential exists."
                        )
                    else:
                        st.markdown(f"#### {certification['name']}")
                        st.write(f"Provider: {certification['provider']}")
                        st.write(f"Cost category: {certification['cost_type'].title()}")
                        st.write(f"Credential type: {certification['credential_type']}")
                        with st.expander("Why this certification?"):
                            st.write("Selected using skill-name overlap with this career. Check eligibility, fees, and current details with the provider.")
                        st.link_button(
                            "View official credential information",
                            certification["official_url"],
                        )
                    # --------------------------
                    # ACTIONABLE LEARNING STARTER PLAN
                    # --------------------------
                    st.markdown("### What to learn next")
                    st.caption("Up to three O*NET skills to review. Not listing a skill doesn't mean you lack it.")
                    missing_lookup = {
                        name.casefold()
                        for name in essential_result["missing_skills"]
                    }
                    priorities = []
                    for entry in essential_entries:
                        if not isinstance(entry, dict):
                            continue
                        name = entry.get("Element Name")
                        if not isinstance(name, str) or name.casefold() not in missing_lookup:
                            continue
                        importance = entry.get("Importance", 0)
                        try:
                            importance = float(importance)
                        except (ValueError, TypeError):
                            importance = 0.0
                        priorities.append((importance, name))
                    priorities.sort(key=lambda item: (-item[0], item[1]))
                    suggested = []
                    seen = set()
                    for _, name in priorities:
                        if name.casefold() not in seen:
                            suggested.append(name)
                            seen.add(name.casefold())
                        if len(suggested) == 3:
                            break
                    if suggested:
                        st.write(
                            f"With {learning_hours} hour(s) per week available, "
                            "consider starting with one topic at a time."
                        )
                        for number, skill in enumerate(suggested, start=1):
                            with st.expander(f"{number}. {skill}", expanded=number == 1):
                                st.write("Try a short lesson, practice the skill on a real example, and note what you learned.")
                                show_learning_resources(skill)
                    else:
                        st.info(
                            "No unmatched essential skill topics were identified. "
                            "Review the occupation description and consider "
                            "your interests and experience before deciding."
                        )
                    occupation_url = (
                        "https://www.onetonline.org/link/summary/"
                        + quote(str(selected_code), safe=".-")
                    )
                    with st.expander("Official O*NET career information"):
                        st.link_button("Open O*NET career profile", occupation_url)
                    st.markdown("### Ask your career advisor")
                    show_ai_advisor(
                        confirmed_skills=confirmed_skills,
                        career_goal=career_goal,
                        current_career=current_career,
                        target_career=target_career,
                        career_interests=career_interests,
                        learning_hours=learning_hours,
                        occupation=occupation,
                        essential_skills=essential_names,
                        software_skills=software_names,
                        onet_url=occupation_url,
                    )
                    # --------------------------------------
                    # LEARNING AND EMPLOYER DISCOVERY
                    # --------------------------------------
                    with st.expander("More learning links and employer websites"):
                        st.caption("These are resource searches and general employer career websites, not verified job vacancies.")
                        topics = suggested if suggested else essential_names[:3]
                        for group in learning_resources(topics, max_skills=3):
                            st.markdown(f"**{group['topic']}**")
                            for resource in group["resources"]:
                                st.link_button(
                                    f"Search {resource['provider']} for {group['topic']}",
                                    resource["url"],
                                )
                        st.markdown("**Employer career websites**")
                        for employer in official_employer_portals():
                            st.link_button(f"Explore {employer['employer']} careers", employer["url"])
            except (
                KeyError,
                ValueError,
                TypeError,
            ) as exc:
                st.error(
                    "Unable to display the skill comparison "
                    "for this occupation."
                )
                # Technical details are intentionally not shown to end users.
                pass
# ==========================================
# 14. FOOTER
# ==========================================
st.write("")
st.divider()
st.markdown(
    """
    <div class="footer">
        CareerMatch AI · Career Exploration ·
        Career Transitions · Professional Growth
    </div>
    """,
    unsafe_allow_html=True,
)
