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

# 1. Configuration and Mobile CSS
st.set_page_config(page_title="Integrity Debt Diagnostic", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white; color: black; }
    header {visibility: hidden;}
    .reportview-container { background: white; }
    p, span, h1, h2, h3, h4, li { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. PDF Report Generator Class
class IntegrityPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'Integrity Debt Audit Report', 0, 1, 'C')
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, 'Framework by Professor Sam Illingworth (2026)', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def safe_text(self, text):
        if not text: return "N/A"
        mapping = {150: ',', 151: ',', 8211: ',', 8212: ',', 8216: "'", 8217: "'", 8220: '"', 8221: '"', 8230: '...'}
        return str(text).translate(mapping).encode('latin-1', 'ignore').decode('latin-1')

    def add_summary(self, actual, score, improvements, doc_context):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, "Executive Summary", 0, 1)
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 8, f"Identified Assessment: {self.safe_text(doc_context)}")
        self.cell(0, 8, f"Total Integrity Score: {score}/50", 0, 1)
        self.cell(0, 8, f"Actual Susceptibility: {actual}", 0, 1)
        self.ln(2)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 8, "Top 3 Priority Improvements:", 0, 1)
        self.set_font('helvetica', '', 10)
        for imp in improvements:
            self.multi_cell(0, 6, f"* {self.safe_text(imp)}")
            self.ln(2)
        self.ln(5)

    def add_category(self, name, score, critique, question, quote):
        if score == 5: self.set_fill_color(200, 255, 200) 
        elif score >= 3: self.set_fill_color(255, 255, 200) 
        else: self.set_fill_color(255, 200, 200) 
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, f" {self.safe_text(name)} (Score: {score}/5)", 1, 1, 'L', 1)
        self.ln(2)
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 6, f"Critique: {self.safe_text(critique)}")
        self.ln(1)
        self.set_font('helvetica', 'I', 10)
        self.multi_cell(0, 6, f"Dialogue Question: {self.safe_text(question)}")
        self.ln(2)
        self.set_font('helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 5, f"Evidence: \"{self.safe_text(quote)}\"")
        self.set_text_color(0, 0, 0)
        self.ln(5)

# 3. Utilities
def extract_text(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            for page in reader.pages: text += page.extract_text() or ""
        elif uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            for para in doc.paragraphs: text += para.text + "\n"
    except Exception as e: st.error(f"Extraction error: {e}")
    return text

def scrape_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
        content = "\n".join([t.get_text() for t in tags])
        if not content.strip(): return "No readable text found at URL."
        return content
    except Exception as e: return f"Error retrieving web content: {str(e)}"

def clean_json_string(raw_string):
    try:
        match = re.search(r'\{.*\}', raw_string, re.DOTALL)
        if match: return match.group(0)
        return raw_string.strip()
    except: return raw_string.strip()

# 4. Interface and Explainer
st.title("Integrity Debt Diagnostic")
st.caption("🔒 Privacy Statement: This tool is stateless. Assessment briefs are processed in-memory and are never stored. No database of assessments is created.")

st.markdown("""
### How to run this diagnostic
To begin the audit, you must first complete the **Setup** section below.
1. Provide your **Email Address** for the final report.
2. Select your **Predicted Susceptibility** (how vulnerable you believe the assessment is to AI).
3. Once these are set, upload your file or paste your content to generate the report.
""")

st.divider()

st.subheader("1. Setup")
setup_col1, setup_col2 = st.columns(2)
with setup_col1:
    email_user = st.text_input("Your Email (required for report):", key="em_k")
with setup_col2:
    expectation = st.selectbox("Predicted Susceptibility (required):", ["Low", "Medium", "High"], key="exp_k")

st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
    ### Pre-Audit Checklist
    For an accurate diagnostic, your input should include the task description, learning outcomes, and submission formats.
    
    ### How to Use These Results
    1. **Reflect**: Critically analyse the system generated critiques. Are they fair?
    2. **Dialogue**: Utilise the dialogue questions within staff meetings or student representative forums.
    3. **Redesign**: Focus intervention on categories marked in **Red** (Vulnerable).
    """)
    st.markdown("[More details here](https://samillingworth.gumroad.com/l/integrity-debt-audit) (Open Access Resource)")
with col2:
    st.info("**The Scoring System**\n* 🟢 5: Resilient\n* 🟡 3-4: Moderate\n* 🔴 1-2: Vulnerable")

st.divider()

with st.sidebar:
    st.header("Authentication")
    api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password", key="sec_k")
    if api_key: genai.configure(api_key=api_key)
    else: st.stop()

st.subheader("2. Assessment Input")
input_type = st.radio("Choose Input Method:", ["File Upload", "Paste Text or URL"], key="in_type")
text_content = ""
if input_type == "File Upload":
    uploaded_file = st.file_uploader("Upload Brief", type=["pdf", "docx"], key="up_k")
    if uploaded_file: text_content = extract_text(uploaded_file)
else:
    raw_input = st.text_area("Paste Content or Public URL:", height=300, key="txt_area")
    if raw_input.startswith("http"):
        with st.spinner("Fetching content..."): text_content = scrape_url(raw_input)
    else: text_content = raw_input

# 5. Execution
if text_content and email_user:
    if st.button("Generate Diagnostic Report", key="run_k"):
        with st.spinner("Scanning for substantive assessment tasks..."):
            prompt = f"""
            You are Professor Sam Illingworth. Perform a two-step analysis on the provided text.
            
            STEP 1: TRIAGE AND SELECTION
            Scan the entire text to identify any specific assessment tasks (e.g., portfolios, essays, examinations). 
            - If no assessment tasks are identified, return ONLY a JSON object with: {{"status": "error", "message": "No substantive assessment brief identified in the text. Please ensure the document includes task descriptions or requirements."}}
            - If multiple tasks are present, select the most substantive assessment (e.g., based on word count, percentage weighting, or primary exam status). 
            
            STEP 2: AUDIT (ONLY if Step 1 is successful)
            Analyse the selected task using the 10 categories of Integrity Debt. 
            RULES: Ground exclusively in text; state "No evidence found" if information is absent; lock temperature at 0.0; ignore file metadata.
            
            Return ONLY a valid JSON object.
            
            JSON Structure: 
            {{
                "status": "success",
                "doc_context": "The title or description of the specific task identified for audit",
                "audit_results": {{cat: {{score, critique, question, quote}}}}, 
                "top_improvements": [str, str, str]
            }}
            
            Text: {text_content[:20000]}
            """
            
            max_retries = 3
            for i in range(max_retries):
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                    model = genai.GenerativeModel(model_name, generation_config={"temperature": 0.0})
                    
                    response = model.generate_content(prompt)
                    json_payload = clean_json_string(response.text)
                    raw_results = json.loads(json_payload)
                    
                    if raw_results.get("status") == "error":
                        st.error(raw_results.get("message"))
                        break
                    
                    results = raw_results.get("audit_results", {})
                    doc_context = raw_results.get("doc_context", "N/A")
                    top_imps = raw_results.get("top_improvements", ["N/A", "N/A", "N/A"])
                    total_score = sum([int(v.get('score', 0)) for v in results.values()])
                    actual_cat = "Low" if total_score >= 40 else "Medium" if total_score >= 25 else "High"
                    
                    st.divider()
                    st.info(f"**Diagnostic Focus:** {doc_context}")
                    st.subheader(f"Total Integrity Score: {total_score}/50 ({actual_cat} Susceptibility)")
                    st.markdown("#### Top 3 Priority Improvements")
                    for imp in top_imps: st.write(f"* {imp}")
                    
                    st.divider()
                    for cat, data in results.items():
                        score = int(data.get('score', 0))
                        if score == 5: st.success(f"🟢 {cat} (Score: {score}/5)")
                        elif score >= 3: st.warning(f"🟡 {cat} (Score: {score}/5)")
                        else: st.error(f"🔴 {cat} (Score: {score}/5)")
                        st.write(f"**Critique:** {data.get('critique', 'N/A')}")

                    pdf = IntegrityPDF()
                    pdf.alias_nb_pages(); pdf.add_page()
                    pdf.add_summary(actual_cat, total_score, top_imps, doc_context)
                    for cat, data in results.items():
                        pdf.add_category(cat, int(data.get('score', 0)), data.get('critique', 'N/A'), data.get('question', 'N/A'), data.get('quote', 'N/A'))
                    
                    pdf.add_page(); pdf.set_font('helvetica', 'B', 14); pdf.cell(0, 10, "Curriculum Redesign and Consultancy", 0, 1)
                    pdf.set_font('helvetica', '', 11); pdf.multi_cell(0, 7, "Professor Sam Illingworth provides workshops and strategic support to help professionals move from diagnostic debt to resilient practice.")
                    pdf.ln(10); pdf.cell(0, 8, "Strategy Guide: https://samillingworth.gumroad.com/l/integrity-debt-audit", 0, 1)
                    pdf.cell(0, 8, "Contact for Consultancy: sam.illingworth@gmail.com", 0, 1)
                    
                    st.download_button("Download Full PDF Report", data=bytes(pdf.output()), file_name="Integrity_Audit.pdf", mime="application/pdf", key="dl_k")
                    break

                except exceptions.ResourceExhausted:
                    if i < max_retries - 1:
                        st.warning("Rate limit reached. Retrying...")
                        time.sleep(30)
                    else:
                        st.error("API Quota exceeded. Please try again in one minute.")
                except json.JSONDecodeError:
                    if i < max_retries - 1:
                        st.warning("Structural formatting error. Retrying...")
                        time.sleep(2)
                    else:
                        st.error("The system failed to generate a valid data structure.")
                except Exception as e:
                    st.error(f"Audit failed: {e}")
                    break
else:
    if not email_user:
        st.info("Please enter your email address in the **Setup** section to proceed.")
