import streamlit as st
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDF text extraction
import google.generativeai as genai

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Initialize Gemini model (text-only)
model = genai.GenerativeModel("gemini-pro")

# Function to extract plain text from PDF using fitz
def extract_text_from_pdf(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"⚠️ Error reading PDF: {e}"

# Function to get Gemini response
def get_gemini_response(job_desc, resume_text, prompt):
    try:
        response = model.generate_content([prompt, job_desc, resume_text])
        return response.text
    except Exception as e:
        return f"⚠️ Error in Gemini response: {e}"

# Streamlit UI setup
st.set_page_config(page_title="ATS Resume Analyzer",layout="wide")
st.title("🧠 ATS Resume Analyzer (Gemini + Streamlit)")

# Inputs
job_description = st.text_area("📄 Paste Job Description")
uploaded_file = st.file_uploader("📁 Upload Resume (PDF only)", type=["pdf"])

# Gemini prompts
input_prompt1 = """
You are an experienced technical human resource manager. Your task is to review the provided resume against the job description for roles in data science, full-stack development, data engineering, cybersecurity, software testing, or quality assurance. Please share a professional evaluation on whether the candidate profile aligns with the job requirements, highlighting strengths and weaknesses.
"""

input_prompt2 = """
You are a skilled ATS system scanner with deep knowledge of resume screening for tech jobs. Evaluate the resume against the job description and provide a percentage match. Mention missing keywords, and suggest improvements.
"""

# Action Buttons
col1, col2 = st.columns(2)
with col1:
    analyze = st.button("📊 Analyze Resume")
with col2:
    match = st.button("✅ Percentage Match")

# Resume Processing Logic
if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)

    if analyze:
        response = get_gemini_response(job_description, resume_text, input_prompt1)
        st.subheader("📋 Resume Analysis")
        st.write(response)

    elif match:
        response = get_gemini_response(job_description, resume_text, input_prompt2)
        st.subheader("📈 Percentage Match & Feedback")
        st.write(response)
else:
    st.info("Please upload a PDF resume to begin.")
