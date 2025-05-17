# import streamlit as st
# import os
# from dotenv import load_dotenv
# import fitz  # PyMuPDF for PDF text extraction
# import google.generativeai as genai

# # Load API key
# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=api_key)

# # Initialize Gemini model (text-only)
# model = genai.GenerativeModel("gemini-pro")

# # Function to extract plain text from PDF using fitz
# def extract_text_from_pdf(uploaded_file):
#     try:
#         doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
#         text = ""
#         for page in doc:
#             text += page.get_text()
#         return text
#     except Exception as e:
#         return f"⚠️ Error reading PDF: {e}"

# # Function to get Gemini response
# def get_gemini_response(job_desc, resume_text, prompt):
#     try:
#         response = model.generate_content([prompt, job_desc, resume_text])
#         return response.text
#     except Exception as e:
#         return f"⚠️ Error in Gemini response: {e}"

# # Streamlit UI setup
# st.set_page_config(page_title="ATS Resume Analyzer",layout="wide")
# st.title("🧠 ATS Resume Analyzer (Gemini + Streamlit)")

# # Inputs
# job_description = st.text_area("📄 Paste Job Description")
# uploaded_file = st.file_uploader("📁 Upload Resume (PDF only)", type=["pdf"])

# # Gemini prompts
# input_prompt1 = """
# You are an experienced technical human resource manager. Your task is to review the provided resume against the job description for roles in data science, full-stack development, data engineering, cybersecurity, software testing, or quality assurance. Please share a professional evaluation on whether the candidate profile aligns with the job requirements, highlighting strengths and weaknesses.
# """

# input_prompt2 = """
# You are a skilled ATS system scanner with deep knowledge of resume screening for tech jobs. Evaluate the resume against the job description and provide a percentage match. Mention missing keywords, and suggest improvements.
# """

# # Action Buttons
# col1, col2 = st.columns(2)
# with col1:
#     analyze = st.button("📊 Analyze Resume")
# with col2:
#     match = st.button("✅ Percentage Match")

# # Resume Processing Logic
# if uploaded_file:
#     resume_text = extract_text_from_pdf(uploaded_file)

#     if analyze:
#         response = get_gemini_response(job_description, resume_text, input_prompt1)
#         st.subheader("📋 Resume Analysis")
#         st.write(response)

#     elif match:
#         response = get_gemini_response(job_description, resume_text, input_prompt2)
#         st.subheader("📈 Percentage Match & Feedback")
#         st.write(response)
# else:
#     st.info("Please upload a PDF resume to begin.")

import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import fitz  # PyMuPDF
from functools import lru_cache

# Load .env API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Setup - Moved to top for better performance
st.set_page_config(
    page_title="ATS Resume Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.title("⚡ ATS Resume Analyzer using Gemini")

# Cache the Gemini model initialization
@st.cache_resource
def load_model():
    return genai.GenerativeModel('gemini-1.5-flash')  # Using faster flash model

# Cache PDF text extraction (stores up to 3 different resumes)
@st.cache_data(max_entries=3, show_spinner="Extracting text from resume...")
def extract_text_from_pdf(uploaded_file):
    resume_text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        resume_text = " ".join(page.get_text() for page in doc)
    return resume_text

# Cache Gemini responses (time-to-live 1 hour)
@st.cache_data(ttl=3600, show_spinner=False)
def get_gemini_response(prompt, jd_text, resume_text):
    model = load_model()
    try:
        response = model.generate_content(
            f"{prompt}\n\nJob Description:\n{jd_text}\n\nResume:\n{resume_text}",
            request_options={"timeout": 10}  # Add timeout
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Improved prompts
analysis_prompt ="""
You are an experienced technical human resource manager. Your task is to review the provided resume against the job description for roles in data science, full-stack development, and data engineering,cyber Security Jobs,software tester,Quality Assurence. Please share your professional evaluation on whether the candidate profile aligns with the job requirements, highlighting strengths and weaknesses.
"""


match_prompt = """
You are a skilled ATS system scanner with a deep understanding of data science and ATS functionality. Your task is to evaluate the resume against the provided job description and provide a percentage match. Highlight missing keywords and provide final thoughts on the resume's suitability.
"""

# Session state to store processed data
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""

# Input fields with better organization
with st.expander("📋 Input Section", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        jd_text = st.text_area(
            "Paste the Job Description:",
            height=200,
            placeholder="Copy-paste the full job description here..."
        )
    with col2:
        uploaded_file = st.file_uploader(
            "Upload your Resume (PDF)",
            type=["pdf"],
            help="Maximum file size: 5MB"
        )

# Process resume once when uploaded
if uploaded_file and not st.session_state.resume_text:
    with st.spinner("Processing resume..."):
        st.session_state.resume_text = extract_text_from_pdf(uploaded_file)

# Action buttons with progress
if st.session_state.resume_text and jd_text:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Analyze Resume", use_container_width=True):
            with st.spinner("Generating analysis..."):
                result = get_gemini_response(analysis_prompt, jd_text, st.session_state.resume_text)
                st.session_state.analysis_result = result
    with col2:
        if st.button("📊 Percentage Match", use_container_width=True):
            with st.spinner("Calculating match..."):
                result = get_gemini_response(match_prompt, jd_text, st.session_state.resume_text)
                st.session_state.match_result = result

# Display results in tabs
if 'analysis_result' in st.session_state or 'match_result' in st.session_state:
    tab1, tab2 = st.tabs(["Analysis Results", "Match Score"])
    
    with tab1:
        if 'analysis_result' in st.session_state:
            st.subheader("🔍 Resume Analysis")
            st.write(st.session_state.analysis_result)
    
    with tab2:
        if 'match_result' in st.session_state:
            st.subheader("📊 Match Score")
            st.write(st.session_state.match_result)

# Clear cache button in sidebar
with st.sidebar:
    st.markdown("### Performance Options")
    if st.button("Clear Cache", help="Use if seeing stale results"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.clear()
        st.rerun()
    st.markdown("---")
    st.info("ℹ️ Using Gemini 1.5 Flash for faster responses")

# Add file size validation
if uploaded_file and uploaded_file.size > 5 * 1024 * 1024:  # 5MB limit
    st.error("File too large! Please upload a PDF smaller than 5MB")
    st.stop()
