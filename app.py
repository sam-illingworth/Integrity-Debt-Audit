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

# 2. Professional PDF Report Generator Class
class IntegrityPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(15, 20, 15)
        self.set_auto_page_break(auto=True, margin=20)
        # Professional Color Palette
        self.primary_color = (44, 62, 80)    
        self.text_color_val = (50, 50, 50)       
        self.accent_blue = (52, 152, 219)    
        self.success = (39, 174, 96)         
        self.warning = (243, 156, 18)        
        self.danger = (231, 76, 60)          
        self.light_grey = (245, 247, 250)    

    def header(self):
        self.set_fill_color(*self.primary_color)
        self.rect(0, 0, 210, 35, 'F')
        self.set_y(10)
        self.set_font('helvetica', 'B', 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'Integrity Debt Audit Report', 0, 1, 'L')
        self.set_font('helvetica', 'I', 11)
        self.cell(0, 8, 'Framework by Professor Sam Illingworth', 0, 1, 'L')
        self.ln(20)

    def footer(self):
        self.set_y(-18)
        self.set_draw_color(200, 200, 200)
        self.line(15, self.get_y(), 195, self.get_y())
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Slow AI Diagnostic Tool | Private & Confidential | Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def safe_text(self, text):
        if not text: return "N/A"
        text_str = str(text)
        replacements = {
            '\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'", 
            '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u2022': '*'
        }
        for char, replacement in replacements.items():
            text_str = text_str.replace(char, replacement)
        return text_str.encode('latin-1', 'replace').decode('latin-1')

    def add_summary(self, actual, score, improvements, doc_context):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, "Executive Summary", 0, 1)
        self.ln(2)

        self.set_fill_color(*self.light_grey)
        self.set_draw_color(220, 220, 220)
        box_start_y = self.get_y()
        self.rect(15, box_start_y, 180, 40, 'FD')
        
        self.set_xy(20, box_start_y + 5)
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(45, 8, "Assessed Context:", 0, 0)
        self.set_font('helvetica', '', 11)
        self.set_text_color(*self.text_color_val)
        self.multi_cell(125, 8, self.safe_text(doc_context))

        current_y = self.get_y() + 2
        self.set_xy(20, current_y)
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(45, 8, "Total Integrity Score:", 0, 0)
        
        score_color = self.success if score >= 40 else self.warning if score >= 25 else self.danger
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(*score_color)
        self.cell(30, 8, f"{score}/50", 0, 0)
        
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(35, 8, "Susceptibility:", 0, 0)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(*score_color)
        self.cell(40, 8, actual, 0, 1)
        
        self.set_y(box_start_y + 45)
        self.ln(5)

        self.set_font('helvetica', 'B', 14)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, "Top 3 Priority Improvements", 0, 1)
        self.set_font('helvetica', '', 11)
        for i, imp in enumerate(improvements, 1):
            self.set_text_color(*self.accent_blue)
            self.cell(10, 8, f"{i}.", 0, 0)
            self.set_text_color(*self.text_color_val)
            self.multi_cell(0, 8, self.safe_text(imp))
            self.ln(1)
        self.ln(5)
        self.set_draw_color(220,220,220)
        self.line(15, self.get_y(), 195, self.get_y()) 
        self.ln(10)

    def add_category(self, name, score, critique, question, quote):
        if score == 5:
            accent = self.success
            status = "RESILIENT"
        elif score >= 3:
            accent = self.warning
            status = "MODERATE"
        else:
            accent = self.danger
            status = "VULNERABLE"

        start_y = self.get_y()
        self.set_fill_color(*accent)
        self.rect(15, start_y+2, 2, 8, 'F')

        self.set_xy(18, start_y)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(*self.primary_color)
        self.cell(130, 12, f" {self.safe_text(name)}", 0, 0, 'L')
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*accent)
        self.cell(0, 12, f"Score: {score}/5 | {status}", 0, 1, 'R')
        self.ln(2)

        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, "Critique:", 0, 1)
        self.set_font('helvetica', '', 10)
        self.set_text_color(*self.text_color_val)
        self.multi_cell(0, 6, self.safe_text(critique))
        self.ln(3)

        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, "Dialogue Question:", 0, 1)
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(*self.text_color_val)
        self.multi_cell(0, 6, self.safe_text(question))
        self.ln(3)

        self.set_font('helvetica', 'B', 9)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, "Evidence Reference:", 0, 1)
        self.set_font('courier', '', 9) 
        self.set_text_color(80, 80, 80)
        self.set_fill_color(250, 250, 250)
        self.set_draw_color(230, 230, 230)
        self.multi_cell(0, 5, f"\"{self.safe_text(quote)}\"", 1, 'L', True)
        self.ln(8)

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
        tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'li', 'td'])
        content = "\n".join([t.get_text() for t in tags])
        return content if content.strip() else "No readable text found."
    except Exception as e: return f"Error: {str(e)}"

def clean_json_string(raw_string):
    cleaned = re.sub(r'```json\s*|\s*```', '', raw_string)
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    return match.group(0) if match else cleaned.strip()

@st.cache_resource
def discover_model(api_key):
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m for m in models if 'flash' in m]
        return flash_models[0] if flash_models else models[0]
    except:
        return 'models/gemini-1.5-flash'

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
            with st.spinner("Running diagnostics."):
                try:
                    target_model = discover_model(api_key)
                    model = genai.GenerativeModel(target_model, generation_config={"temperature": 0.0})
                    
                    prompt = f"""
                    You are Professor Sam Illingworth. Perform a combined triage and audit.
                    
                    STEP 1: IDENTIFICATION
                    Identify the assessment task with highest credit weighting (e.g., "Portfolio").
                    If no task exists, return JSON status: "error".
                    
                    STEP 2: AUDIT
                    Analyse that task using the 10 categories of Integrity Debt. 
                    - Ground in text.
                    - Lock temperature 0.0.
                    - Ensure ALL text values are properly escaped for JSON.
                    
                    Return ONLY valid JSON.
                    Structure: {{"status": "success", "doc_context": "Task title", "audit_results": {{cat: {{score, critique, question, quote}}}}, "top_improvements": [str, str, str]}}
                    Text: {final_text[:8000]}
                    """
                    
                    response = model.generate_content(prompt)
                    try:
                        results_json = json.loads(clean_json_string(response.text))
                    except json.JSONDecodeError:
                        repaired = response.text.replace('\n', ' ').replace('\\', '\\\\')
                        results_json = json.loads(clean_json_string(repaired))
                    
                    if results_json.get("status") == "error":
                        st.error("No substantive assessment task identified.")
                    else:
                        results = results_json.get("audit_results", {})
                        doc_context = results_json.get("doc_context", "N/A")
                        top_imps = results_json.get("top_improvements", ["N/A", "N/A", "N/A"])
                        total_score = sum([int(v.get('score', 0)) for v in results.values()])
                        actual_cat = "Low" if total_score >= 40 else "Medium" if total_score >= 25 else "High"
                        
                        st.divider()
                        st.info(f"**Diagnostic Focus:** {doc_context}")
                        st.subheader(f"Total Integrity Score: {total_score}/50")
                        
                        for cat, data in results.items():
                            score = int(data.get('score', 0))
                            if score == 5: st.success(f"🟢 {cat} (Score: {score}/5)")
                            elif score >= 3: st.warning(f"🟡 {cat} (Score: {score}/5)")
                            else: st.error(f"🔴 {cat} (Score: {score}/5)")
                            st.write(f"**Critique:** {data.get('critique', 'N/A')}")

                        pdf = IntegrityPDF()
                        pdf.alias_nb_pages()
                        pdf.add_page()
                        pdf.add_summary(actual_cat, total_score, top_imps, doc_context)
                        for cat, data in results.items():
                            pdf.add_category(cat, int(data.get('score', 0)), data.get('critique', 'N/A'), data.get('question', 'N/A'), data.get('quote', 'N/A'))
                        
                        st.download_button("Download PDF Report", data=bytes(pdf.output()), file_name="Integrity_Audit.pdf")

                except exceptions.ResourceExhausted:
                    st.error("The API quota is full. Please wait sixty seconds.")
                except Exception as e:
                    st.error(f"Audit failed: {e}")
