import streamlit as st
import google.generativeai as genai
import json
from pypdf import PdfReader
from docx import Document
from fpdf import FPDF
import io
import requests
from bs4 import BeautifulSoup
import re
from google.api_core import exceptions

# 1. Configuration and Professional CSS
st.set_page_config(page_title="Integrity Debt Diagnostic", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white; color: black; }
    header {visibility: hidden;}
    .reportview-container { background: white; }
    p, span, h1, h2, h3, h4, li { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Professional PDF Class
class IntegrityPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=20)
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
        self.line(20, self.get_y(), 190, self.get_y())
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.set_x(20)
        self.cell(0, 10, f'Slow AI Diagnostic Tool | Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def safe_text(self, text):
        if not text: return "N/A"
        text_str = str(text)
        replacements = {'\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u2022': '*'}
        for char, replacement in replacements.items():
            text_str = text_str.replace(char, replacement)
        return text_str.encode('latin-1', 'replace').decode('latin-1')

    def add_summary(self, actual, score, improvements, doc_context):
        usable_w = 170 
        self.set_x(20)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, "Executive Summary", 0, 1)
        self.ln(2)
        self.set_fill_color(*self.light_grey)
        self.set_draw_color(220, 220, 220)
        box_y = self.get_y()
        self.rect(20, box_y, usable_w, 45, 'FD')
        self.set_xy(25, box_y + 5)
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(35, 8, "Context:", 0, 0)
        self.set_font('helvetica', '', 11)
        self.set_text_color(*self.text_color_val)
        self.multi_cell(125, 8, self.safe_text(doc_context))
        self.set_xy(25, box_y + 28)
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(35, 8, "Integrity Score:", 0, 0)
        sc_col = self.success if score >= 40 else self.warning if score >= 25 else self.danger
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(*sc_col)
        self.cell(30, 8, f"{score}/50", 0, 0)
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(35, 8, "Susceptibility:", 0, 0)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(*sc_col)
        self.cell(30, 8, actual, 0, 1)
        self.set_y(box_y + 50)
        self.set_x(20)
        self.ln(5)
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, "Top 3 Priority Improvements", 0, 1)
        self.set_font('helvetica', '', 11)
        imps = improvements if isinstance(improvements, list) else ["Review findings below"]
        for i, imp in enumerate(imps[:3], 1):
            self.set_x(20)
            self.set_text_color(*self.accent_blue)
            self.cell(10, 8, f"{i}.", 0, 0)
            self.set_text_color(*self.text_color_val)
            self.multi_cell(0, 8, self.safe_text(imp))
        self.ln(10)

    def add_category(self, name, score, critique, question, quote):
        accent = self.success if score == 5 else self.warning if score >= 3 else self.danger
        self.set_x(20)
        start_y = self.get_y()
        self.set_fill_color(*accent)
        self.rect(20, start_y + 2, 2, 8, 'F')
        self.set_xy(23, start_y)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(*self.primary_color)
        self.cell(120, 12, f" {self.safe_text(name)}", 0, 0, 'L')
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*accent)
        self.cell(0, 12, f"Score: {score}/5", 0, 1, 'R')
        self.set_x(20)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 6, "Critique:", 0, 1)
        self.set_font('helvetica', '', 10)
        self.set_text_color(*self.text_color_val)
        self.set_x(20)
        self.multi_cell(0, 6, self.safe_text(critique))
        self.ln(3)
        self.set_x(20)
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, "Dialogue Question:", 0, 1)
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(*self.text_color_val)
        self.set_x(20)
        self.multi_cell(0, 6, self.safe_text(question))
        self.ln(3)
        self.set_x(20)
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, "Evidence Reference:", 0, 1)
        self.set_font('courier', '', 9) 
        self.set_text_color(80, 80, 80)
        self.set_fill_color(250, 250, 250)
        self.set_draw_color(230, 230, 230)
        self.set_x(20)
        self.multi_cell(0, 5, f"\"{self.safe_text(quote)}\"", 1, 'L', True)
        self.ln(8)

    def add_contact_box(self):
        self.ln(10)
        self.set_x(20)
        self.set_fill_color(*self.primary_color)
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, " Strategic Consultancy & Bespoke Support", 0, 1, 'L', True)
        self.set_fill_color(245, 247, 250)
        self.set_text_color(*self.text_color_val)
        self.set_font('helvetica', '', 10)
        self.set_x(20)
        contact_txt = "As a Full Professor with over 20 years experience of working in higher education, I can help interpret your diagnostic results to develop AI-resilient assessments and curricula. Contact me to discuss your specific organisational requirements."
        self.multi_cell(0, 6, self.safe_text(contact_txt), 1, 'L', True)
        self.ln(5)
        self.set_x(20)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 6, "Email: sam.illingworth@gmail.com | Substack: https://samillingworth.substack.com/", 0, 1, 'C')

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
        return "\n".join([t.get_text() for t in tags])
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
        flash = [m for m in models if 'flash' in m]
        return flash[0] if flash else models[0]
    except: return 'models/gemini-1.5-flash'

# 4. Interface
st.title("Integrity Debt Diagnostic")
st.caption("🔒 Privacy Statement: This tool is stateless. Assessment briefs are processed in-memory.")

st.markdown("""
### How to run this diagnostic
Complete the setup fields below. This tool remains inert until you click the final button.
""")

c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("""
    ### Pre-Audit Checklist
    Include the task description, learning outcomes, and submission formats for accurate results.
    
    ### How to Use These Results
    1. **Reflect**: Critically analyse the system generated critiques.
    2. **Dialogue**: Use the dialogue questions in staff or student representative forums.
    3. **Redesign**: Focus on categories marked in **Red** (Vulnerable).
    """)
    st.markdown("[Integrity Debt Audit Report](https://samillingworth.gumroad.com/l/integrity-debt-audit)")
with c2:
    st.info("**The Scoring System**\n* 🟢 5: Resilient\n* 🟡 3-4: Moderate\n* 🔴 1-2: Vulnerable")

st.divider()

with st.form("audit_form"):
    st.subheader("1. Setup")
    sc1, sc2 = st.columns(2)
    with sc1: email_user = st.text_input("Your Email (required):")
    with sc2: expectation = st.selectbox("Predicted Susceptibility:", ["Low", "Medium", "High"])
    st.subheader("2. Assessment Input")
    input_type = st.radio("Choose Input Method:", ["File Upload", "Paste Text or URL"])
    uploaded_file = st.file_uploader("Upload Brief", type=["pdf", "docx"]) if input_type == "File Upload" else None
    raw_input = st.text_area("Paste Content or Public URL:", height=200)
    submit_button = st.form_submit_button("Generate Diagnostic Report")

# 5. Logic
api_key = st.secrets.get("GEMINI_API_KEY")
if submit_button:
    if not api_key or not email_user: st.error("Email and Secrets configuration required.")
    else:
        final_text = extract_text(uploaded_file) if input_type == "File Upload" and uploaded_file else (scrape_url(raw_input) if raw_input.startswith("http") else raw_input)
        if not final_text: st.error("No assessment content provided.")
        else:
            with st.spinner("Running diagnostics."):
                try:
                    target = discover_model(api_key)
                    model = genai.GenerativeModel(target, generation_config={"temperature": 0.0})
                    prompt = f"""
                    You are Professor Sam Illingworth. Perform a combined triage and audit.
                    STEP 1: Identify assessment with highest credit weighting (e.g., Portfolio).
                    STEP 2: Audit using 10 categories of Integrity Debt. 
                    RULES: Ground in text; lock temp 0.0; return ONLY valid JSON; escape values.
                    Text: {final_text[:8000]}
                    """
                    response = model.generate_content(prompt)
                    res_raw = clean_json_string(response.text)
                    try:
                        res_json = json.loads(res_raw)
                    except:
                        rep = res_raw.replace('\n', ' ').replace('\\', '\\\\')
                        res_json = json.loads(rep)
                    
                    if res_json.get("status") == "error": st.error("No task identified.")
                    else:
                        audit_raw = res_json.get("audit_results", {})
                        audit_items = audit_raw if isinstance(audit_raw, list) else list(audit_raw.values())

                        # ARCHITECT-GRADE FAIL-SAFE EXTRACTION
                        total_score = 0
                        # Extract integers adjacent to score-related keys in raw text
                        score_matches = re.findall(r'"(?:score|points|rating|value)"\s*:\s*"?(\d+(?:\.\d+)?)"?', res_raw, re.IGNORECASE)
                        if score_matches:
                            total_score = int(sum(float(s) for s in score_matches))
                        
                        audit_dict = {}
                        for item in audit_items:
                            c_name = item.get('category') or item.get('name') or "Category"
                            audit_dict[c_name] = item

                        ctx = res_json.get("doc_context") or res_json.get("task_title") or "Assessment Audit"
                        imps = res_json.get("top_improvements") or res_json.get("improvements") or ["Review findings below"]
                        cat_res = "Low" if total_score >= 40 else "Medium" if total_score >= 25 else "High"
                        
                        st.divider()
                        st.info(f"**Diagnostic Focus:** {ctx}")
                        st.subheader(f"Total Integrity Score: {total_score}/50")
                        
                        for c_name, d in audit_dict.items():
                            sc = 0
                            item_raw = json.dumps(d)
                            m = re.search(r'"score"\s*:\s*"?(\d+(?:\.\d+)?)"?', item_raw, re.IGNORECASE)
                            if m: sc = int(float(m.group(1)))
                            if sc == 5: st.success(f"🟢 {c_name} ({sc}/5)")
                            elif sc >= 3: st.warning(f"🟡 {c_name} ({sc}/5)")
                            else: st.error(f"🔴 {c_name} ({sc}/5)")
                            st.write(d.get('critique', 'N/A'))
                        
                        pdf = IntegrityPDF()
                        pdf.alias_nb_pages()
                        pdf.add_page()
                        pdf.add_summary(cat_res, total_score, imps, ctx)
                        for c_name, d in audit_dict.items():
                            sc_val = 0
                            item_raw = json.dumps(d)
                            m = re.search(r'"score"\s*:\s*"?(\d+(?:\.\d+)?)"?', item_raw, re.IGNORECASE)
                            if m: sc_val = int(float(m.group(1)))
                            pdf.add_category(c_name, sc_val, d.get('critique', 'N/A'), d.get('question', 'N/A'), d.get('quote', 'N/A'))
                        pdf.add_contact_box()
                        st.download_button("Download PDF Report", data=bytes(pdf.output()), file_name="Integrity_Audit.pdf")
                except Exception as e: st.error(f"Audit failed: {e}")
