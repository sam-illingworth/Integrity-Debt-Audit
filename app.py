import streamlit as st
import google.generativeai as genai
import json
from pypdf import PdfReader
from docx import Document
from fpdf import FPDF
import io

# 1. Configuration
st.set_page_config(page_title="Integrity Debt Diagnostic", page_icon="⚖️", layout="wide")

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
        # Using {nb} placeholder for fpdf2 total page count
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def safe_text(self, text):
        if not text:
            return "N/A"
        mapping = {
            150: '-', 151: '-', 8211: '-', 8212: '-',
            8216: "'", 8217: "'", 8218: "'", 8219: "'",
            8220: '"', 8221: '"', 8222: '"', 8223: '"',
            8230: '...'
        }
        text = str(text).translate(mapping)
        return text.encode('latin-1', 'ignore').decode('latin-1')

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
            # Using epw (effective page width) to prevent horizontal space errors
            self.multi_cell(self.epw, 6, f"- {self.safe_text(imp)}")
        self.ln(5)

    def add_category(self, name, score, critique, question, quote):
        if score == 5: self.set_fill_color(200, 255, 200) 
        elif score >= 3: self.set_fill_color(255, 255, 200) 
        else: self.set_fill_color(255, 200, 200) 
        
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, f" {self.safe_text(name)} - Score: {score}/5", 1, 1, 'L', 1)
        self.ln(2)
        
        self.set_font('helvetica', '', 10)
        self.multi_cell(self.epw, 6, f"Critique: {self.safe_text(critique)}")
        self.ln(1)
        self.set_font('helvetica', 'I', 10)
        self.multi_cell(self.epw, 6, f"Dialogue Question: {self.safe_text(question)}")
        self.ln(2)
        self.set_font('helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.multi_cell(self.epw, 5, f"Evidence: \"{self.safe_text(quote)}\"")
        self.set_text_color(0, 0, 0)
        self.ln(5)

def extract_text(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        st.error(f"Extraction error: {e}")
    return text

# 3. Header & Detailed Interpretation Guide
st.title("Integrity Debt Diagnostic")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### What is Integrity Debt?
    Integrity Debt refers to structural vulnerabilities within an assessment that make it susceptible to automation via AI. High debt is a curriculum design challenge, not a student character flaw.
    
    ### How to Use These Results
    This diagnostic provides a 'Traffic Light' audit of your assessment brief. 
    1. **Reflect**: Review the critiques provided by the AI. Are they fair?
    2. **Dialogue**: Take the 'Dialogue Questions' to your next staff meeting or student rep forum. 
    3. **Redesign**: Focus your energy on the **Red** categories first. These represent the highest risk to academic integrity.
    """)

with col2:
    st.info("""
    **The Scoring System**
    * 🟢 **5 (Resilient)**: Low vulnerability. High structural integrity.
    * 🟡 **3-4 (Moderate)**: Vulnerabilities exist. Requires review.
    * 🔴 **1-2 (Vulnerable)**: High debt. Immediate redesign advised.
    """)

st.divider()

# 4. Sidebar & Authentication
with st.sidebar:
    st.header("Setup")
    api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password", key="sec_k")
    if api_key: genai.configure(api_key=api_key)
    else: st.stop()
    expectation = st.selectbox("Predicted Susceptibility:", ["Low", "Medium", "High"], key="exp_k")
    email_user = st.text_input("Your Email (for report):", key="em_k")

# 5. Execution
uploaded_file = st.file_uploader("Upload Assessment Brief (PDF/DOCX)", type=["pdf", "docx"], key="up_k")

if uploaded_file and email_user:
    if st.button("Generate Diagnostic Report", key="run_k"):
        text_content = extract_text(uploaded_file)
        
        with st.spinner("Professor Illingworth is auditing your curriculum..."):
            prompt = f"""
            Audit this brief using the 10 Integrity Debt categories. 
            Return ONLY a JSON object with two top-level keys:
            1. "audit_results": A dictionary of the 10 categories, each containing {{"score": int, "critique": str, "question": str, "quote": str}}.
            2. "top_improvements": A list of exactly 3 strings (1 sentence each) identifying the highest priority redesign actions.
            
            Scoring: 5 (Resilient) to 1 (Vulnerable).
            Brief Text: {text_content[:15000]}
            """
            
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model_id = 'models/gemini-1.5-flash-latest' if 'models/gemini-1.5-flash-latest' in available_models else available_models[0]
                model = genai.GenerativeModel(model_id)
                response = model.generate_content(prompt)
                raw_results = json.loads(response.text.replace('```json', '').replace('```', '').strip())
                
                results = raw_results.get("audit_results", {})
                top_imps = raw_results.get("top_improvements", ["N/A", "N/A", "N/A"])
                
                total_score = sum([int(v.get('score', 0)) for v in results.values()])
                actual_cat = "Low" if total_score >= 40 else "Medium" if total_score >= 25 else "High"
                
                # App Results Summary
                st.subheader("Diagnostic Results Summary")
                st.warning("Note: This screen provides the score and critique. The full PDF report includes dialogue questions and evidence quotes for each category.")
                st.write(f"**Total Integrity Score:** {total_score}/50 ({actual_cat} Susceptibility)")
                
                st.markdown("#### Top 3 Priority Improvements")
                for imp in top_imps: st.write(f"- {imp}")
                
                st.divider()
                st.markdown("#### Category Breakdown")
                for cat, data in results.items():
                    score = int(data.get('score', 0))
                    if score == 5: st.success(f"🟢 {cat} (Score: {score}/5)")
                    elif score >= 3: st.warning(f"🟡 {cat} (Score: {score}/5)")
                    else: st.error(f"🔴 {cat} (Score: {score}/5)")
                    st.write(f"**Critique:** {data.get('critique', 'N/A')}")

                # PDF Generation
                pdf = IntegrityPDF()
                pdf.alias_nb_pages()
                pdf.add_page()
                pdf.add_summary(actual_cat, total_score, top_imps)
                for cat, data in results.items():
                    pdf.add_category(cat, int(data.get('score', 0)), data.get('critique', 'N/A'), data.get('question', 'N/A'), data.get('quote', 'N/A'))
                
                # Force Page Break for Consultancy
                pdf.add_page()
                pdf.set_font('helvetica', 'B', 14)
                pdf.cell(0, 10, "Curriculum Redesign & Consultancy", 0, 1)
                pdf.set_font('helvetica', '', 11)
                consult_msg = (
                    "The Integrity Debt framework identifies vulnerabilities, but effective redesign "
                    "requires institutional expertise. Professor Sam Illingworth provides bespoke "
                    "workshops, curriculum audits, and strategic support to help Higher Education "
                    "professionals move from diagnostic debt to resilient pedagogical practice."
                )
                pdf.multi_cell(pdf.epw, 7, consult_msg)
                
                pdf.ln(10)
                pdf.set_font('helvetica', 'B', 11)
                pdf.cell(0, 10, "Next Steps", 0, 1)
                pdf.set_font('helvetica', '', 11)
                pdf.cell(0, 8, "Access the Strategy Guide: https://samillingworth.gumroad.com/l/integrity-debt-audit", 0, 1)
                pdf.cell(0, 8, "Contact for Consultancy: sam.illingworth@gmail.com", 0, 1)
                
                pdf_output = pdf.output()
                st.download_button("Download Full PDF Report", data=bytes(pdf_output), file_name="Integrity_Audit.pdf", mime="application/pdf", key="dl_k")

            except Exception as e:
                st.error(f"Audit failed: {e}")

st.divider()
st.caption("🔒 Privacy: Stateless processing. No data storage.")
