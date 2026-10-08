
import streamlit as st
from docx import Document
from pypdf import PdfReader


# Function to extract text from DOCX resumes
def extract_docx_text(uploaded_file):
    document = Document(uploaded_file)
    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


# Function to extract text from PDF resumes
def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"

    return text


# Application title
st.title("CareerMatch AI")
st.write("Discover career paths that match your skills.")


# Resume upload section
st.subheader("Upload Your Resume")

uploaded_file = st.file_uploader(
    "Choose your resume (PDF or DOCX)",
    type=["pdf", "docx"]
)


# Check whether a resume was uploaded
if uploaded_file is not None:

    # Maximum file size: 5 MB
    max_size = 5 * 1024 * 1024

    if uploaded_file.size > max_size:
        st.error("File is too large. Maximum allowed size is 5 MB.")
        st.stop()

    st.success("Resume uploaded successfully!")
    st.write("Filename:", uploaded_file.name)

    resume_text = ""

    try:
        # Extract text from DOCX
        if uploaded_file.name.lower().endswith(".docx"):
            resume_text = extract_docx_text(uploaded_file)

        # Extract text from PDF
        elif uploaded_file.name.lower().endswith(".pdf"):
            resume_text = extract_pdf_text(uploaded_file)

        # Check whether text was extracted
        if resume_text.strip():
            st.success("Resume text extracted successfully!")
            st.write("Characters extracted:", len(resume_text))

        else:
            st.warning("No readable text found in the resume.")

    except Exception:
        st.error(
            "Unable to read this file. Please upload a valid PDF or DOCX resume."
        )
