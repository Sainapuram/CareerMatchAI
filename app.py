
import re
import html
import hashlib
from urllib.parse import quote

import streamlit as st
from docx import Document
from pypdf import PdfReader

from src.matching import (
    load_occupation_profiles,
    build_tfidf_model,
    recommend_careers,
)
from src.skill_gap import analyze_skill_gap
from career_resources import learning_resources, official_employer_portals


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
    .stApp {
        background-color: #F5F7FB;
    }
    .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        color: #142B45;
        font-family: 'Segoe UI', sans-serif;
    }
    .hero {
        background: linear-gradient(120deg, #10243A, #1E4974);
        border-radius: 20px;
        padding: 38px 42px;
        color: white;
        margin-bottom: 28px;
    }
    .hero h1 {
        color: white !important;
        font-size: 2.6rem;
        margin-bottom: 12px;
    }
    .hero p {
        color: #D7E7F6;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    .hero-label {
        color: #A9D6FF;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }
    .section-label {
        color: #2563EB;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin-top: 8px;
    }
    .section-description {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 14px;
    }
    .stButton > button[kind="primary"] {
        background-color: #2563EB;
        border: none;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        padding: 0.65rem 1.5rem;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8;
        color: white;
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
    }
    .skill-tag {
        display: inline-block;
        background-color: #EAF2FF;
        color: #1D4ED8;
        padding: 7px 13px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
        margin: 4px;
    }
    .footer {
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        padding-top: 22px;
    }
    </style>
    """,
    unsafe_allow_html=True,
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
    pattern = (
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )
    return re.sub(pattern, "[EMAIL REMOVED]", text)


def remove_phone(text):
    pattern = (
        r"(?<!\w)(?:\+1[\s.-]?)?"
        r"\(?\d{3}\)?[\s.-]?\d{3}"
        r"[\s.-]?\d{4}(?!\w)"
    )
    return re.sub(pattern, "[PHONE REMOVED]", text)


def clean_resume_text(text):
    text = remove_email(text)
    text = remove_phone(text)
    return text


# ==========================================
# 4. SKILL EXTRACTION
# ==========================================

SKILLS_LIST = [
    "Python",
    "SQL",
    "Excel",
    "Tableau",
    "Power BI",
    "Machine Learning",
    "Data Analysis",
    "Java",
    "JavaScript",
    "Statistics",
    "Communication",
    "Problem Solving",
    "Project Management",
    "Leadership",
    "Cloud Computing",
    "Deep Learning",
    "Data Visualization",
    "Research",
    "Customer Service",
    "Business Analysis",
    "Data Engineering",
    "Public Speaking",
    "Teamwork",
    "Critical Thinking",
    "Microsoft Office",
    "Git",
    "Docker",
    "AWS",
    "Azure",
    "TensorFlow",
    "PyTorch",
    "FastAPI",
    "Streamlit",
]


def extract_skills(text):
    found_skills = []

    for skill in SKILLS_LIST:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills


# ==========================================
# 4B. CAREER EXPLANATIONS AND RESOURCES
# ==========================================

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

if "custom_skills" not in st.session_state:
    st.session_state.custom_skills = []

if "profile_visible" not in st.session_state:
    st.session_state.profile_visible = False

if "career_matches" not in st.session_state:
    st.session_state.career_matches = None

if "career_matches_skills" not in st.session_state:
    st.session_state.career_matches_skills = None


def add_custom_skill():
    new_skill = st.session_state.custom_skill_input.strip()

    if not new_skill:
        st.session_state.skill_message = "Please enter a skill."
        return

    if len(new_skill) > 60:
        st.session_state.skill_message = (
            "Skill name must be 60 characters or less."
        )
        return

    existing_skills = (
        SKILLS_LIST + st.session_state.custom_skills
    )

    matching_skill = next(
        (
            skill for skill in existing_skills
            if skill.casefold() == new_skill.casefold()
        ),
        None,
    )

    skill_to_add = matching_skill or new_skill

    if (
        skill_to_add not in SKILLS_LIST
        and skill_to_add not in st.session_state.custom_skills
    ):
        st.session_state.custom_skills.append(skill_to_add)

    if skill_to_add not in st.session_state.skills_selection:
        st.session_state.skills_selection.append(skill_to_add)

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
            Your next career move starts here.<br>
            Discover your strengths, explore new career paths,
            and build a future that fits your goals.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 7. CAREER GOAL SELECTION
# ==========================================

st.markdown(
    '<div class="section-label">01 / YOUR DIRECTION</div>',
    unsafe_allow_html=True,
)

st.subheader("What would you like to achieve?")

st.markdown(
    '<div class="section-description">'
    'Choose the journey that best describes your goals.'
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

st.subheader("Tell us about yourself")

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
    "Your interests and career goals",
    placeholder=(
        "Tell us what you enjoy, what you're good at, "
        "and what kind of career you're looking for."
    ),
    height=110,
)


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
        extracted_skills = extract_skills(cleaned_resume)

        st.success(
            "Résumé processed successfully. "
            "Basic email and phone masking applied."
        )

        st.caption(
            f"{len(resume_text):,} characters extracted"
        )

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

st.subheader("Review and personalize your skills")

st.caption(
    "Confirm extracted skills, remove incorrect matches, "
    "or add skills that are missing."
)

current_resume_id = None

if uploaded_file is not None and resume_text.strip():
    current_resume_id = hashlib.sha256(
        uploaded_file.getvalue()
    ).hexdigest()

if current_resume_id != st.session_state.resume_id:
    st.session_state.resume_id = current_resume_id
    st.session_state.skills_selection = list(extracted_skills)

skill_options = sorted(
    set(SKILLS_LIST)
    | set(st.session_state.custom_skills)
    | set(st.session_state.skills_selection)
)

st.multiselect(
    "Select all skills you have",
    options=skill_options,
    key="skills_selection",
    help=(
        "Automatically detected skills are preselected. "
        "Add missing skills or remove incorrect ones."
    ),
)

st.caption(
    "Skills detected from a résumé are suggestions, "
    "not verified proficiency assessments."
)

st.text_input(
    "Add a skill not listed above",
    placeholder="e.g., Healthcare Analytics",
    key="custom_skill_input",
)

st.button(
    "Add Custom Skill",
    on_click=add_custom_skill,
)

if "skill_message" in st.session_state:
    st.info(st.session_state.skill_message)
    del st.session_state.skill_message

confirmed_skills = list(
    st.session_state.skills_selection
)

st.markdown("**Your confirmed skills**")

if confirmed_skills:
    skill_html = "".join(
        '<span class="skill-tag">'
        + html.escape(skill)
        + '</span>'
        for skill in confirmed_skills
    )

    st.markdown(
        skill_html,
        unsafe_allow_html=True,
    )

    st.caption(
        f"{len(confirmed_skills)} skills selected"
    )

else:
    st.info(
        "No skills selected yet. Upload a résumé "
        "or add skills manually."
    )


# ==========================================
# 11. CAREER PROFILE DASHBOARD
# ==========================================

st.write("")

st.markdown(
    '<div class="section-label">05 / YOUR CAREER PROFILE</div>',
    unsafe_allow_html=True,
)

st.subheader("Your personalized career profile")

if st.button(
    "✨ View My Career Profile",
    type="primary",
    use_container_width=True,
):
    st.session_state.profile_visible = True

if st.session_state.profile_visible:

    st.write("")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Confirmed Skills",
            len(confirmed_skills),
        )

    with metric2:
        st.metric(
            "Years of Experience",
            experience_years,
        )

    with metric3:
        st.metric(
            "Learning Hours / Week",
            learning_hours,
        )

    st.write("")

    profile_left, profile_right = st.columns(2)

    with profile_left:
        st.markdown("#### Career Direction")

        st.write("**Goal:**", career_goal)

        if current_career.strip():
            st.write(
                "**Current Profession:**",
                current_career,
            )

        st.write(
            "**Target Career:**",
            target_career.strip() or "Not specified",
        )

    with profile_right:
        st.markdown("#### Your Strengths")

        if confirmed_skills:
            st.write(", ".join(confirmed_skills))
        else:
            st.write("No skills confirmed yet.")

    if career_interests.strip():
        st.markdown("#### Interests and Goals")
        st.write(career_interests)

    st.info(
        "Career recommendations and a preliminary O*NET "
        "skill comparison are available. "
        "Learning-topic suggestions are available with career matches."
    )


# ==========================================
# 12. CAREER RECOMMENDATIONS
# ==========================================

st.write("")

st.markdown(
    '<div class="section-label">06 / YOUR CAREER MATCHES</div>',
    unsafe_allow_html=True,
)

st.subheader("Explore your top career matches")

st.caption(
    "Recommendations use TF-IDF text similarity with O*NET occupations. "
    "Explore uses your skills; Change can include your target role and exclude "
    "an exact current-role title; Grow can include your current and target roles. "
    "These are exploratory text matches, not promotion or hiring predictions."
)

if career_goal == "Explore Career":
    st.info("Explore: find occupations related to your confirmed skills.")
elif career_goal == "Change Career":
    st.info(
        "Change: optionally enter a target career to influence text matching. "
        "An exact match to your current profession is excluded from the results."
    )
else:
    st.info(
        "Grow: optionally enter your current profession and a target career "
        "to explore related roles. This does not infer seniority or promotion readiness."
    )


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
        "🎯 Find My Top 5 Careers",
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

            st.caption(f"Technical detail: {exc}")

    matches = st.session_state.career_matches

    if matches is not None:

        display_matches = matches.rename(
            columns={
                "O*NET-SOC Code": "O*NET Code",
                "Title": "Career",
                "Similarity Score": "Cosine Similarity",
            }
        ).copy()

        display_matches.insert(
            0,
            "Rank",
            range(1, len(display_matches) + 1),
        )

        st.dataframe(
            display_matches,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Cosine Similarity":
                    st.column_config.NumberColumn(
                        format="%.4f"
                    )
            },
        )

        if (matches["Similarity Score"] == 0).any():
            st.caption(
                "Some occupations have zero text similarity; "
                "they should not be interpreted as meaningful matches."
            )

        st.caption(
            "Mode-specific search: Explore uses skills only; Change adds an optional "
            "target title and excludes an exact current-title match; Grow adds "
            "optional current/target titles. Experience and interests are profile "
            "information and do not change ranking. The displayed cosine similarity "
            "reflects the selected query, not a suitability percentage."
        )

        # ==================================
        # 13. SKILL-GAP ANALYSIS
        # ==================================

        st.markdown("### Explore Skill Gaps")

        st.caption(
            "Select a recommended career to compare your "
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
            "Select a recommended career",
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

                # Compare both categories separately.

                essential_result = analyze_skill_gap(
                    confirmed_skills,
                    essential_names,
                )

                software_result = analyze_skill_gap(
                    confirmed_skills,
                    software_names,
                )

                # --------------------------
                # WHY THIS CAREER WAS SUGGESTED
                # --------------------------
                st.markdown("### Why This Career Was Recommended")
                st.write(
                    "This occupation appeared in your top results because "
                    "its O*NET description and associated skill terms "
                    "have text overlap with your confirmed skills."
                )
                description = occupation.get("Description", "")
                if isinstance(description, str) and description.strip():
                    st.markdown("**What people in this occupation do**")
                    st.write(description.strip())

                shared_software = software_result["matched_skills"]
                shared_essential = essential_result["matched_skills"]
                if shared_software:
                    st.markdown("**Software technologies you already listed**")
                    st.write(", ".join(shared_software[:10]))
                if shared_essential:
                    st.markdown("**O*NET essential skill names you already listed**")
                    st.write(", ".join(shared_essential[:10]))
                if not shared_software and not shared_essential:
                    st.info(
                        "No exact or normalized O*NET skill-name overlap was "
                        "identified. The recommendation comes from TF-IDF "
                        "text similarity, not a verified skills assessment."
                    )

                st.caption(
                    "Explanations describe observable text/skill overlap. "
                    "They are not a causal explanation of the full ranking "
                    "and do not indicate hiring eligibility."
                )

                # --------------------------
                # ESSENTIAL SKILLS
                # --------------------------

                st.markdown("#### Essential Skills")

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
                            "Matched Essential Skills",
                            essential_result["matched_count"],
                        )

                    with essential_col2:
                        st.metric(
                            "Not Identified",
                            essential_result["missing_count"],
                        )

                    st.markdown("**Matched Essential Skills**")

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

                    st.markdown(
                        "**Essential Skills Not Identified "
                        "in Your Profile**"
                    )

                    if essential_result["missing_skills"]:
                        st.write(
                            ", ".join(
                                essential_result["missing_skills"]
                            )
                        )
                    else:
                        st.success(
                            "All listed essential skill names "
                            "were matched."
                        )

                else:
                    st.info(
                        "No essential skills are listed "
                        "for this occupation."
                    )

                # --------------------------
                # SOFTWARE SKILLS
                # --------------------------

                st.markdown(
                    "#### Associated Software Technologies"
                )

                st.metric(
                    "Matched Software Technologies",
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

                st.caption(
                    f"O*NET lists {len(software_names)} "
                    "software entries for this occupation. "
                    "These are associated technologies, not "
                    "a list of mandatory tools. Unmatched "
                    "entries do not automatically represent "
                    "skills you need to learn."
                )

                # --------------------------
                # ACTIONABLE LEARNING STARTER PLAN
                # --------------------------
                st.markdown("### Your Skill-Development Starting Points")
                st.caption(
                    "Suggested topics come from O*NET essential skills "
                    "not identified in your confirmed profile. Missing "
                    "from a profile does not mean you lack the skill. "
                    "The order is a simple O*NET importance-based heuristic."
                )

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
                        f"With **{learning_hours} hour(s) per week** available, "
                        "consider starting with one topic at a time."
                    )
                    for number, skill in enumerate(suggested, start=1):
                        with st.expander(f"{number}. {skill}", expanded=number == 1):
                            st.write(
                                "Review the fundamentals, practice with a "
                                "small example, and add the skill to your "
                                "profile only when you can demonstrate it."
                            )
                else:
                    st.info(
                        "No unmatched essential skill topics were identified. "
                        "Review the occupation description and consider "
                        "your interests and experience before deciding."
                    )

                st.markdown("### Explore Official Occupation Information")
                occupation_url = (
                    "https://www.onetonline.org/link/summary/"
                    + quote(str(selected_code), safe=".-")
                )
                st.link_button("View O*NET occupation profile", occupation_url)

                # --------------------------------------
                # LEARNING AND EMPLOYER DISCOVERY
                # --------------------------------------
                st.markdown("### Learning Resources and Employer Career Portals")
                st.caption(
                    "These are topic searches and official employer career portals, "
                    "not verified certifications or currently available vacancies."
                )

                st.markdown("#### Learning resources for your selected career")
                topics = suggested if suggested else essential_names[:3]
                resource_groups = learning_resources(topics, max_skills=3)
                if resource_groups:
                    for group in resource_groups:
                        st.markdown(f"**{group['topic']}**")
                        for resource in group["resources"]:
                            st.link_button(
                                f"Search {resource['provider']} for {group['topic']}",
                                resource["url"],
                            )
                else:
                    st.info("No O*NET learning topics are available for this occupation.")

                st.markdown("#### Explore official employer career websites")
                st.caption(
                    "These employer portals are general starting points. "
                    "They are not matched or verified job openings, and they do not "
                    "establish sponsorship or work-authorization eligibility. "
                    "Review each individual vacancy on the employer's website."
                )
                for employer in official_employer_portals():
                    st.link_button(
                        f"Explore {employer['employer']} careers",
                        employer["url"],
                    )

        except (
            KeyError,
            ValueError,
            TypeError,
        ) as exc:

            st.error(
                "Unable to display the skill comparison "
                "for this occupation."
            )

            st.caption(f"Technical detail: {exc}")


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
