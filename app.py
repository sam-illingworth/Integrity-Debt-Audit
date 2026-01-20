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

    def add_summary(self, actual, score, improvements):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, "Executive Summary", 0, 1)
        self.set_font('helvetica', '', 10)
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
        return "\n".join([t.get_text() for t in tags])
    except Exception as e: return f"Error retrieving web content: {str(e)}"

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
    st.markdown("### Pre-Audit Checklist\nFor an accurate diagnostic, your input should include the task description, learning outcomes, and submission formats.")
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

# 5. Execution with Rate Limit Handling
if text_content and email_user:
    if st.button("Generate Diagnostic Report", key="run_k"):
        with st.spinner("Identifying structural vulnerabilities..."):
            prompt = f"""
            You are Professor Sam Illingworth. Analyse this brief using the 10 categories of Integrity Debt.
            RULES: 
            1. Parse Learning Outcomes and Task Descriptions. 
            2. CATEGORY RECENCY: Ignore file dates; focus on whether the task requires live/current data engagement.
            3. Ignore administrative metadata.
            Return ONLY a JSON object: {{"audit_results": {{cat: {{score, critique, question, quote}}}}, "top_improvements": [str, str, str]}}
            Text: {text_content[:15000]}
            """
            
            max_retries = 3
            for i in range(max_retries):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    response = model.generate_content(prompt)
                    raw_results = json.loads(response.text.replace('```json', '').replace('```', '').strip())
                    
                    results = raw_results.get("audit_results", {})
                    top_imps = raw_results.get("top_improvements", ["N/A", "N/A", "N/A"])
                    total_score = sum([int(v.get('score', 0)) for v in results.values()])
                    actual_cat = "Low" if total_score >= 40 else "Medium" if total_score >= 25 else "High"
                    
                    st.divider()
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
                    pdf.add_summary(actual_cat, total_score, top_imps)
                    for cat, data in results.items():
                        pdf.add_category(cat, int(data.get('score', 0)), data.get('critique', 'N/A'), data.get('question', 'N/A'), data.get('quote', 'N/A'))
                    
                    pdf.add_page(); pdf.set_font('helvetica', 'B', 14); pdf.cell(0, 10, "Curriculum Redesign and Consultancy", 0, 1)
                    pdf.set_font('helvetica', '', 11); pdf.multi_cell(0, 7, "Professor Sam Illingworth provides bespoke workshops and strategic support to move from diagnostic debt to resilient practice.")
                    pdf.ln(10); pdf.cell(0, 8, "Strategy Guide: https://samillingworth.gumroad.com/l/integrity-debt-audit", 0, 1)
                    pdf.cell(0, 8, "Contact for Consultancy: sam.illingworth@gmail.com", 0, 1)
                    
                    st.download_button("Download Full PDF Report", data=bytes(pdf.output()), file_name="Integrity_Audit.pdf", mime="application/pdf", key="dl_k")
                    break

                except exceptions.ResourceExhausted:
                    if i < max_retries - 1:
                        st.warning(f"Rate limit reached. Retrying in 30 seconds... (Attempt {i+1}/{max_retries})")
                        time.sleep(30)
                    else:
                        st.error("API Quota exceeded. Please try again in one minute.")
                except Exception as e:
                    st.error(f"Audit failed: {e}")
                    break
else:
    if not email_user:
        st.info("Please enter your email address in the **Setup** section to proceed.")
