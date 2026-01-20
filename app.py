import streamlit as st
import google.generativeai as genai
import json
from pypdf import PdfReader
from docx import Document
from fpdf import FPDF
import io
import requests
from bs4 import BeautifulSoup
import time
import re
from google.api_core import exceptions

# 1. Configuration
st.set_page_config(page_title="Integrity Debt Diagnostic", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white; color: black; }
    header {visibility: hidden;}
    p, span, h1, h2, h3, h4, li { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. PDF Class
class IntegrityPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'Integrity Debt Audit Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def safe_text(self, text):
        mapping = {150: ',', 151: ',', 8211: ',', 8212: ',', 8216: "'", 8217: "'", 8220: '"', 8221: '"', 8230: '...'}
        return str(text).translate(mapping).encode('latin-1', 'ignore').decode('latin-1')

    def add_summary(self, actual, score, improvements, doc_context):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, "Executive Summary", 0, 1)
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 8, f"Identified Assessment: {self.safe_text(doc_context)}")
        self.cell(0, 8, f"Total Integrity Score: {score}/50", 0, 1)
        self.cell(0, 8, f"Actual Susceptibility: {actual}", 0, 1)
        self.ln(5)

    def add_category(self, name, score, critique, question, quote):
        self.set_fill_color(240, 240, 240)
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, f" {self.safe_text(name)} (Score: {score}/5)", 1, 1, 'L', 1)
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 6, f"Critique: {self.safe_text(critique)}")
        self.ln(2)

# 3. Functions
def extract_text(uploaded_file):
    text = ""
    if uploaded_file.name.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        for page in reader.pages: text += page.extract_text() or ""
    elif uploaded_file.name.endswith('.docx'):
        doc = Document(uploaded_file)
        for para in doc.paragraphs: text += para.text + "\n"
    return text

def clean_json_string(raw_string):
    match = re.search(r'\{.*\}', raw_string, re.DOTALL)
    return match.group(0) if match else raw_string.strip()

# 4. Interface
st.title("Integrity Debt Diagnostic")

st.subheader("1. Setup")
setup_col1, setup_col2 = st.columns(2)
with setup_col1:
    email_user = st.text_input("Your Email:", key="em_k")
with setup_col2:
    expectation = st.selectbox("Predicted Susceptibility:", ["Low", "Medium", "High"], key="exp_k")

st.divider()

with st.sidebar:
    st.header("Authentication")
    api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password", key="sec_k")

st.subheader("2. Assessment Input")
input_type = st.radio("Choose Input Method:", ["File Upload", "Paste Text"], key="in_type")
text_content = ""
if input_type == "File Upload":
    uploaded_file = st.file_uploader("Upload Brief", type=["pdf", "docx"], key="up_k")
    if uploaded_file: text_content = extract_text(uploaded_file)
else:
    text_content = st.text_area("Paste Content:", height=300, key="txt_area")

# 5. Execution
if st.button("Generate Diagnostic Report", key="run_k"):
    if not api_key:
        st.error("Please provide an API Key.")
    elif not text_content or not email_user:
        st.error("Please provide email and assessment content.")
    else:
        with st.spinner("Engaging with synthetic system..."):
            try:
                genai.configure(api_key=api_key)
                # Static fallback to minimize quota-heavy discovery calls
                target_model = 'gemini-1.5-flash'
                model = genai.GenerativeModel(target_model, generation_config={"temperature": 0.0})
                
                prompt = f"""
                You are Professor Sam Illingworth. Perform a triage and audit.
                STEP 1: Identify the most substantive assessment task.
                STEP 2: Audit that task using the 10 categories of Integrity Debt.
                Ground results in text. Return ONLY a JSON object.
                Structure: {{"status": "success", "doc_context": "Title", "audit_results": {{cat: {{score, critique, question, quote}}}}, "top_improvements": [str, str, str]}}
                Text: {text_content[:7000]}
                """
                
                response = model.generate_content(prompt)
                raw_results = json.loads(clean_json_string(response.text))
                
                if raw_results.get("status") == "success":
                    results = raw_results.get("audit_results", {})
                    doc_context = raw_results.get("doc_context", "N/A")
                    top_imps = raw_results.get("top_improvements", ["N/A", "N/A", "N/A"])
                    total_score = sum([int(v.get('score', 0)) for v in results.values()])
                    actual_cat = "Low" if total_score >= 40 else "Medium" if total_score >= 25 else "High"
                    
                    st.info(f"**Diagnostic Focus:** {doc_context}")
                    st.subheader(f"Total Integrity Score: {total_score}/50")
                    
                    for cat, data in results.items():
                        with st.expander(f"{cat} (Score: {data['score']}/5)"):
                            st.write(data['critique'])
                    
                    pdf = IntegrityPDF()
                    pdf.add_page()
                    pdf.add_summary(actual_cat, total_score, top_imps, doc_context)
                    for cat, data in results.items():
                        pdf.add_category(cat, int(data.get('score', 0)), data.get('critique', 'N/A'), data.get('question', 'N/A'), data.get('quote', 'N/A'))
                    
                    st.download_button("Download PDF", data=bytes(pdf.output()), file_name="Audit.pdf")
                else:
                    st.error("No assessment found.")
                    
            except exceptions.ResourceExhausted:
                st.error("The API quota is full. Please wait exactly 60 seconds and try again.")
            except Exception as e:
                st.error(f"Error: {e}")
