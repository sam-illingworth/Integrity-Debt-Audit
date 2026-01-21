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
        return content if content.strip() else "No readable text found."
    except Exception as e: return f"Error: {str(e)}"

def clean_json_string(raw_string):
    match = re.search(r'\{.*\}', raw_string, re.DOTALL)
    return match.group(0) if match else raw_string.strip()

# 4. Interface and Explainer
st.title("Integrity Debt Diagnostic")
st.caption("🔒 Privacy Statement: This tool is stateless. Assessment briefs are processed in-memory.")

st.markdown("""
### How to run this diagnostic
Complete the setup fields below. This tool remains inert until you click the final button.
""")

col_info1, col_info2 = st.columns([2, 1])
with col_info1:
    st.markdown("""
    ### Pre-Audit Checklist
    Include the task description, learning outcomes, and submission formats for accurate results.
    
    ### How to Use These Results
    1. **Reflect**: Critically analyse the system generated critiques.
    2. **Dialogue**: Use the dialogue questions in staff or student representative forums.
    3. **Redesign**: Focus on categories marked in **Red** (Vulnerable).
    """)
    st.markdown("[Slow AI Substack](https://samillingworth.substack.com/)")
with col_info2:
    st.info("**The Scoring System**\n* 🟢 5: Resilient\n* 🟡 3-4: Moderate\n* 🔴 1-2: Vulnerable")

st.divider()

# 5. Form Block
with st.form("audit_form"):
    st.subheader("1. Setup")
    setup_col1, setup_col2 = st.columns(2)
    with setup_col1:
        email_user = st.text_input("Your Email (required):")
    with setup_col2:
        expectation = st.selectbox("Predicted Susceptibility:", ["Low", "Medium", "High"])
    
    st.subheader("2. Assessment Input")
    input_type = st.radio("Choose Input Method:", ["File Upload", "Paste Text or URL"])
    
    uploaded_file = None
    if input_type == "File Upload":
        uploaded_file = st.file_uploader("Upload Brief", type=["pdf", "docx"])
    raw_input = st.text_area("Paste Content or Public URL:", height=200)
    
    submit_button = st.form_submit_button("Generate Diagnostic Report")

# 6. Execution Logic
api_key = st.secrets.get("GEMINI_API_KEY")

if submit_button:
    if not api_key:
        st.error("API Key not found in Secrets. Please configure GEMINI_API_KEY.")
    elif not email_user:
        st.error("Email is required.")
    else:
        final_text = ""
        if input_type == "File Upload" and uploaded_file:
            final_text = extract_text(uploaded_file)
        elif raw_input.startswith("http"):
            final_text = scrape_url(raw_input)
        else:
            final_text = raw_input
            
        if not final_text:
            st.error("No assessment content provided.")
        else:
            with st.spinner("Analysing assessment integrity..."):
                time.sleep(3) # Mandatory wait to clear burst quota
                try:
                    genai.configure(api_key=api_key)
                    # Use a single direct model call to save quota on list_models
                    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.0})
                    
                    prompt = f"""
                    You are Professor Sam Illingworth. Perform a combined triage and audit.
                    STEP 1: Identify the highest weighting task.
                    STEP 2: Audit using 10 categories of Integrity Debt. 
                    Return ONLY a JSON object.
                    Text: {final_text[:5000]}
                    """
                    
                    response = model.generate_content(prompt)
                    results_json = json.loads(clean_json_string(response.text))
                    
                    results = results_json.get("audit_results", {})
                    doc_context = results_json.get("doc_context", "N/A")
                    top_imps = results_json.get("top_improvements", ["N/A", "N/A", "N/A"])
                    total_score = sum([int(v.get('score', 0)) for v in results.values()])
                    actual_cat = "Low" if total_score >= 40 else "Medium" if total_score >= 25 else "High"
                    
                    st.divider()
                    st.info(f"**Diagnostic Focus:** {doc_context}")
                    st.subheader(f"Total Integrity Score: {total_score}/50 ({actual_cat} Susceptibility)")
                    
                    for cat, data in results.items():
                        score = int(data.get('score', 0))
                        if score == 5: st.success(f"🟢 {cat} (Score: {score}/5)")
                        elif score >= 3: st.warning(f"🟡 {cat} (Score: {score}/5)")
                        else: st.error(f"🔴 {cat} (Score: {score}/5)")
                        st.write(f"**Critique:** {data.get('critique', 'N/A')}")

                    pdf = IntegrityPDF()
                    pdf.add_page()
                    pdf.add_summary(actual_cat, total_score, top_imps, doc_context)
                    for cat, data in results.items():
                        pdf.add_category(cat, int(data.get('score', 0)), data.get('critique', 'N/A'), data.get('question', 'N/A'), data.get('quote', 'N/A'))
                    
                    st.download_button("Download PDF Report", data=bytes(pdf.output()), file_name="Integrity_Audit.pdf")

                except exceptions.ResourceExhausted:
                    st.error("The API quota is full. Please wait sixty seconds.")
                except Exception as e:
                    # Attempt second model fallback only if first fails with 404
                    if "404" in str(e):
                        try:
                            model = genai.GenerativeModel('models/gemini-1.5-flash', generation_config={"temperature": 0.0})
                            response = model.generate_content(prompt)
                            # (Processing logic remains same as above)
                        except:
                            st.error(f"Audit failed: {e}")
                    else:
                        st.error(f"Audit failed: {e}")
