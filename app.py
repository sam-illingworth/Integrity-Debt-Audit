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
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'Integrity Debt Audit Report', 0, 1, 'C')
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, 'Framework by Professor Sam Illingworth (2026)', 0, 1, 'C')
        self.ln(10)

    def safe_text(self, text):
        """Clean text to prevent latin-1 encoding errors in FPDF"""
        if not text:
            return "N/A"
        # Map common problematic unicode characters to latin-1 equivalents
        mapping = {
            150: '-', 151: '-', 8211: '-', 8212: '-',
            8216: "'", 8217: "'", 8218: "'", 8219: "'",
            8220: '"', 8221: '"', 8222: '"', 8223: '"',
            8230: '...'
        }
        text = text.translate(mapping)
        return text.encode('latin-1', 'ignore').decode('latin-1')

    def add_summary(self, expectation, actual, score):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, "Executive Summary", 0, 1)
        self.set_font('helvetica', '', 10)
        self.cell(0, 8, f"Total Integrity Score: {score}/50", 0, 1)
        self.cell(0, 8, f"Predicted Susceptibility: {expectation}", 0, 1)
        self.cell(0, 8, f"Actual Susceptibility: {actual}", 0, 1)
        if expectation != actual:
            self.set_text_color(200, 0, 0)
            self.cell(0, 8, "Note: An integrity gap was identified between prediction and audit.", 0, 1)
            self.set_text_color(0, 0, 0)
        self.ln(5)

    def add_category(self, name, score, critique, question, quote):
        if score == 5: self.set_fill_color(200, 255, 200) # Green
        elif score >= 3: self.set_fill_color(255, 255, 200) # Yellow
        else: self.set_fill_color(255, 200, 200) # Red
        
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, f" {self.safe_text(name)} - Score: {score}/5", 1, 1, 'L', 1)
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
            You are Professor Sam Illingworth. Audit this assessment brief using the 10 categories of Integrity Debt.
            Return ONLY a valid JSON object. 
            Scoring: 5 (High Structural Resilience/Green) to 1 (High Vulnerability/Red).
            Each category value MUST be a dictionary: {{"score": int, "critique": str, "question": str, "quote": str}}.
            
            Categories: 1. Weighting, 2. Documentation, 3. Context, 4. Reflection, 5. Time, 6. Multimodal, 7. Interrogation, 8. Defence, 9. Collaborative, 10. Recency.
            Brief Text: {text_content[:15000]}
            """
            
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model_id = 'models/gemini-1.5-flash-latest' if 'models/gemini-1.5-flash-latest' in available_models else available_models[0]
                model = genai.GenerativeModel(model_id)
                response = model.generate_content(prompt)
                results = json.loads(response.text.replace('```json', '').replace('```', '').strip())
                
                # SAFE CALCULATION
                total_score = 0
                processed_results = {}
                for cat, val in results.items():
                    if isinstance(val, dict):
                        s = int(val.get('score', 0))
                        processed_results[cat] = val
                    else: 
                        s = int(val)
                        processed_results[cat] = {"score": s, "critique": "N/A", "question": "N/A", "quote": "N/A"}
                    total_score += s

                actual_cat = "Low" if total_score >= 40 else "Medium" if total_score >= 25 else "High"
                st.subheader(f"Total Score: {total_score}/50 ({actual_cat} Susceptibility)")
                
                # UI Display
                for cat, data in processed_results.items():
                    score = int(data.get('score', 0))
                    if score == 5: st.success(f"🟢 {cat}")
                    elif score >= 3: st.warning(f"🟡 {cat}")
                    else: st.error(f"🔴 {cat}")
                    st.write(f"**Dialogue:** {data.get('question', 'N/A')}")

                # PDF Generation
                pdf = IntegrityPDF()
                pdf.add_page()
                pdf.add_summary(expectation, actual_cat, total_score)
                for cat, data in processed_results.items():
                    pdf.add_category(cat, int(data.get('score', 0)), data.get('critique', 'N/A'), data.get('question', 'N/A'), data.get('quote', 'N/A'))
                
                pdf.ln(5); pdf.set_font('helvetica', 'B', 10)
                pdf.cell(0, 10, f"Contact: {email_user} | Framework: sam.illingworth@gmail.com", 0, 1)
                
                pdf_output = pdf.output()
                st.download_button("Download PDF Report", data=bytes(pdf_output), file_name="Integrity_Audit.pdf", mime="application/pdf", key="dl_k")

            except Exception as e:
                st.error(f"Audit failed: {e}")

st.divider()
st.caption("🔒 Privacy: Stateless processing. No data storage.")
