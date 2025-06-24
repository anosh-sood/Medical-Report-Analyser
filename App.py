import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import tempfile
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("API Key not found. Please check your .env file.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Custom Streamlit Theme
st.set_page_config(
    page_title="Medical Report Analyzer",
    page_icon="🩺",
    layout="wide"
)

# Custom CSS for Full-Height Sidebar Image
st.markdown("""
    <style>
        /* Sidebar container */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            padding: 0;
        }
        
        /* Stretch sidebar image to full height */
        [data-testid="stSidebar"] img {
            width: 100% !important;  /* Stretch width */
            height: 100vh !important;  /* Full viewport height */
            object-fit: cover;  /* Ensure it covers the area */
            border-radius: 0px;
        }

        /* Header */
        .header { 
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            margin-bottom: 20px;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #4CAF50 !important;
            color: white !important;
            font-size: 16px;
            padding: 10px 20px;
            border-radius: 8px;
        }

        /* Text Area */
        .stTextArea textarea {
            background-color: #f4f4f4 !important;
            font-size: 14px !important;
        }

        /* Image & PDF Preview */
        .image-preview {
            border-radius: 12px;
            box-shadow: 2px 2px 15px rgba(0,0,0,0.2);
        }
        
    </style>
""", unsafe_allow_html=True)

# Function to analyze medical report
def analyze_medical_report(content, content_type):
    """Analyzes medical report using Gemini 2.0 Flash (text or image)."""
    prompt = "Analyze this medical report concisely. Provide key findings, diagnoses, and recommendations."
    
    try:
        if content_type == "image":
            response = model.generate_content([prompt, content])
        else:  # text
            response = model.generate_content(f"{prompt}\n\n{content}")

        return response.text if hasattr(response, "text") else "No response received."

    except Exception as e:
        return f"Error: {str(e)}"

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

# Sidebar with full-height and full-width image
with st.sidebar:
    st.image("medical.png", use_container_width=True)  # Sidebar image

# Main layout
st.markdown('<div class="header">🔬 AI Medical Report Analysis</div>', unsafe_allow_html=True)
st.write("Upload a **medical report (Image or PDF)** for AI-powered analysis.")

file_type = st.radio("Select file type:", ("📄 PDF", "🖼️ Image"), horizontal=True)

if file_type == "🖼️ Image":
    uploaded_file = st.file_uploader("Choose a medical report image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        image = Image.open(tmp_file_path)
        st.image(image, caption="Uploaded Medical Report", use_column_width=True, output_format="PNG")

        if st.button("🔍 Analyze Image Report"):
            with st.spinner("Analyzing the medical report image..."):
                analysis = analyze_medical_report(image, "image")
                st.subheader("📋 AI Analysis Results:")
                st.success(analysis)

        os.unlink(tmp_file_path)

else:  # PDF Processing
    uploaded_file = st.file_uploader("Choose a medical report PDF", type=["pdf"])
    if uploaded_file is not None:
        st.success("✅ PDF uploaded successfully.")

        if st.button("🔍 Analyze PDF Report"):
            with st.spinner("Extracting text from PDF..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                with open(tmp_file_path, "rb") as pdf_file:
                    pdf_text = extract_text_from_pdf(pdf_file)

                os.unlink(tmp_file_path)

                # Display Extracted Text Before Analysis
                st.subheader("📜 Extracted Text from PDF:")
                st.text_area("PDF Content", pdf_text, height=300)

                with st.spinner("Analyzing the medical report PDF..."):
                    analysis = analyze_medical_report(pdf_text, "text")
                    st.subheader("📋 AI Analysis Results:")
                    st.success(analysis)
