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

    def add_category(self, name, score, critique, question, quote):
        # Traffic Light Logic: 5=Green (Resilient), 3-4=Yellow (Moderate), 1-2=Red (Vulnerable)
        if score == 5:
            self.set_fill_color(200, 255, 200) # Green
        elif score >= 3:
            self.set_fill_color(255, 255, 200) # Yellow
        else:
            self.set_fill_color(255, 200, 200) # Red
        
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, f" {name} - Score: {score}/5", 1, 1, 'L', 1)
        self.ln(2)
        
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 6, f"Critique: {critique}")
        self.ln(1)
        self.set_font('helvetica', 'I', 10)
        self.multi_cell(0, 6, f"Dialogue Question for Staff/Students: {question}")
        self.ln(2)
        self.set_font('helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 5, f"Evidence: \"{quote}\"")
        self.set_text_color(0, 0, 0)
        self.ln(5)

# 3. Text Extraction Logic
def extract_text(uploaded_file):
    text = ""
    if uploaded_file.name.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif uploaded_file.name.endswith('.docx'):
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

# 4. Header & Detailed Interpretation Guide
st.title("Integrity Debt Diagnostic")

# Two-column layout for the guide
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### What is Integrity Debt?
    Integrity Debt refers to the structural vulnerabilities within an assessment that make it susceptible to automation via Generative AI. High debt is not a student failure; it is a curriculum design challenge.
    
    ### How to Use These Results
    This diagnostic provides a 'Traffic Light' audit of your assessment brief. 
    1. **Reflect**: Review the critiques provided by the AI. Are they fair?
    2. **Dialogue**: Take the 'Dialogue Questions' to your next staff meeting or student rep forum. 
    3. **Redesign**: Focus your energy on the **Red** categories first. These are your highest risks.
    """)

with col2:
    st.info("""
    **The Scoring System**
    * 🟢 **5 (Resilient)**: Low vulnerability.
    * 🟡 **3-4 (Moderate)**: Vulnerabilities exist.
    * 🔴 **1-2 (Vulnerable)**: High debt. Redesign advised.
    """)

st.divider()

# 5. Sidebar & Authentication
with st.sidebar:
    st.header("1. Setup")
    api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Enter Gemini API Key", type="password", key="key_in")
    
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.warning("Please provide an API Key.")
        st.stop()

    st.header("2. Context")
    expectation = st.selectbox("Predicted Susceptibility:", ["Low", "Medium", "High"], key="exp_in")
    email_user = st.text_input("Your Email (for the report):", key="email_in")

# 6. Main App Execution
uploaded_file = st.file_uploader("Upload Assessment Brief (PDF/DOCX)", type=["pdf", "docx"], key="file_in")

if uploaded_file and email_user:
    if st.button("Generate Diagnostic Report", key="btn_in"):
        text_content = extract_text(uploaded_file)
        
        with st.spinner("Professor Illingworth is auditing your curriculum..."):
            prompt = f"""
            You are Professor Sam Illingworth. Audit this assessment brief using the 10 categories of Integrity Debt.
            Categories: 1. Weighting, 2. Documentation, 3. Context, 4. Reflection, 5. Time, 6. Multimodal, 7. Interrogation, 8. Defence, 9. Collaborative, 10. Recency.
            
            SCORING LOGIC: 
            5: High Structural Resilience (Green)
            3-4: Moderate Vulnerability (Yellow)
            1-2: High Vulnerability / High Debt (Red)
            
            Return ONLY a valid JSON object. Keys must be the 10 categories.
            Values must include: 'score' (int), 'quote' (short string), 'critique' (1 sentence), 'question' (1 dialogue question).
            
            Brief Text: {text_content[:15000]}
            """
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(prompt)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                results = json.loads(clean_json)
                
                # Visual UI
                st.subheader("Diagnostic Results")
                for cat, data in results.items():
                    score = int(data.get('score', 0))
                    if score == 5:
                        st.success(f"🟢 {cat} (Score: {score}/5)")
                    elif score >= 3:
                        st.warning(f"🟡 {cat} (Score: {score}/5)")
                    else:
                        st.error(f"🔴 {cat} (Score: {score}/5)")
                    
                    st.write(f"**Critique:** {data.get('critique')}")
                    st.write(f"**Dialogue:** {data.get('question')}")
                
                # PDF Generation
                pdf = IntegrityPDF()
                pdf.add_page()
                for cat, data in results.items():
                    pdf.add_category(cat, int(data.get('score', 0)), data.get('critique'), data.get('question'), data.get('quote'))
                
                # PDF Final Section
                pdf.ln(10)
                pdf.set_font('helvetica', 'B', 10)
                pdf.cell(0, 10, "Consultancy & Redesign Resources", 0, 1)
                pdf.set_font('helvetica', '', 10)
                pdf.cell(0, 8, "Integrity Debt Strategy Guide: https://samillingworth.gumroad.com/l/integrity-debt-audit", 0, 1)
                pdf.cell(0, 8, f"Facilitator: {email_user} | Framework by: sam.illingworth@gmail.com", 0, 1)

                pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='ignore')
                st.download_button(
                    label="Download Audit Report (PDF)",
                    data=pdf_bytes,
                    file_name="Integrity_Debt_Audit.pdf",
                    mime="application/pdf",
                    key="dl_btn"
                )

            except Exception as e:
                st.error(f"Audit failed: {e}")

st.markdown("---")
st.caption("🔒 Privacy: This tool is stateless. Uploaded documents are not stored or used for model training.")
