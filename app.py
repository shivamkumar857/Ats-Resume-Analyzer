
import streamlit as st
import os
from dotenv import load_dotenv
from pdf2image import convert_from_bytes
import google.generativeai as genai
import base64
import io

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Function to get Gemini response
def get_gemini_response(input, pdf_content, prompt):
    """
    Sends the input (job description), PDF content (resume), and prompt to the Gemini model.
    Returns the model's response.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')  # Use the updated model
    response = model.generate_content([input, pdf_content, prompt])  # Generate response
    return response.text  # Return the response text

# # Function to process PDF
# def input_pdf_setup(uploaded_file):
#     if uploaded_file is not None:
#         # Specify the Poppler path
#         poppler_path = r"C:\Users\skshi\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"  # Update this path if needed
        
#         # Convert PDF to image
#         images = convert_from_bytes(uploaded_file.read(), poppler_path=poppler_path)
        
#         # Take the first page of the PDF
#         first_page = images[0]
        
#         # Convert the image to bytes
#         img_byte_arr = io.BytesIO()
#         first_page.save(img_byte_arr, format='JPEG')
#         img_byte_arr = img_byte_arr.getvalue()
        
#         # Encode the image in Base64
#         pdf_part = {
#             "mime_type": "image/jpeg",  # Specify the MIME type
#             "data": base64.b64encode(img_byte_arr).decode()  # Base64-encoded image data
#         }
#         return pdf_part  # Return a single dictionary
#     else:
#         raise FileNotFoundError("No file uploaded")
import fitz  # PyMuPDF
import docx

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1].lower()

        if file_type == "pdf":
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                text = ""
                for page in doc:
                    text += page.get_text()

        elif file_type == "docx":
            doc = docx.Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])

        else:
            raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")

        pdf_part = {
            "mime_type": "text/plain",
            "data": text
        }
        return pdf_part

    else:
        raise FileNotFoundError("No file uploaded")


# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Input Fields
input_text = st.text_area("Job Description: ", key="input")
# uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])
uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)...", type=["pdf", "docx"])


# Submit Buttons
submit1 = st.button("Tell Me About the Resume")
submit2 = st.button("Percentage Match")

# Prompts for Gemini Pro Vision
input_prompt1 = """
You are an experienced technical human resource manager. Your task is to review the provided resume against the job description for roles in data science, full-stack development, and data engineering,cyber Security Jobs,software tester,Quality Assurence. Please share your professional evaluation on whether the candidate profile aligns with the job requirements, highlighting strengths and weaknesses.
"""

input_prompt2 = """
You are a skilled ATS system scanner with a deep understanding of data science and ATS functionality. Your task is to evaluate the resume against the provided job description and provide a percentage match. Highlight missing keywords and provide final thoughts on the resume's suitability.
"""

# Handle Button Clicks
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("Resume Analysis:")
        st.write(response)
    else:
        st.write("Please upload a resume in PDF format.")

elif submit2:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt2, pdf_content, input_text)
        st.subheader("Percentage Match:")
        st.write(response)
    else:
        st.write("Please upload a resume in PDF format.")
