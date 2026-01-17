import streamlit as st
import google.generativeai as genai
import json
from pypdf import PdfReader
from docx import Document
from fpdf import FPDF
import io

# 1. Configuration & Styling
st.set_page_config(page_title="Integrity Debt Diagnostic", page_icon="⚖️", layout="wide")

# 2. PDF Generation Class
class IntegrityPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Integrity Debt Audit Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Framework by Professor Sam Illingworth (2026)', 0, 1, 'C')
        self.ln(10)

    def add_category(self, name, score, critique, question, quote):
        # Color Mapping: 5=Green, 3-4=Yellow, 1-2=Red
        if score == 5:
            self.set_fill_color(200, 255, 200) # Light Green
        elif score >= 3:
            self.set_fill_color(255, 255, 200) # Light Yellow
        else:
            self.set_fill_color(255, 200, 200) # Light Red
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f" {name} - Score: {score}/5", 1, 1, 'L', 1)
        self.ln(2)
        
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, f"Critique: {critique}")
        self.set_font('Arial', 'I', 10)
        self.multi_cell(0, 6, f"Dialogue Question: {question}")
        self.ln(2)
        self.set_font('Arial', '', 8)
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

# 4. Header & Framing
st.title("Integrity Debt Diagnostic")
st.markdown("""
### Start a Dialogue
Use these results not as a final judgment, but as the beginning of a conversation with staff and students about assessment resilience. 

**Traffic Light Legend:**
* 🟢 **Score 5**: High Integrity / Low Debt. Structural resilience is high.
* 🟡 **Score 3-4**: Moderate Debt. Potential for AI exploitation exists.
* 🔴 **Score 1-2**: High Debt / Low Integrity. Immediate redesign recommended.
""")

# 5. Sidebar & Authentication
with st.sidebar:
    st.header("1. Authentication")
    api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Enter Gemini API Key", type="password", key="api_key_input")
    
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.warning("Please provide an API Key.")
        st.stop()

    st.header("2. Audit Parameters")
    expectation = st.selectbox("Predicted Susceptibility:", ["Low", "Medium", "High"], key="exp_select")
    email_user = st.text_input("Your Email (for reporting):", key="email_input")

# 6. Main App Execution
uploaded_file = st.file_uploader("Upload Assessment Brief (PDF/DOCX)", type=["pdf", "docx"], key="file_up")

if uploaded_file and email_user:
    if st.button("Run Integrity Audit", key="run_audit_btn"):
        text_content = extract_text(uploaded_file)
        
        with st.spinner("Analyzing curriculum resilience..."):
            prompt = f"""
            You are Professor Sam Illingworth. Audit this assessment brief using the 10 categories of Integrity Debt.
            Categories: 1. Weighting, 2. Documentation, 3. Context, 4. Reflection, 5. Time, 6. Multimodal, 7. Interrogation, 8. Defence, 9. Collaborative, 10. Recency.
            
            SCORING SCALE (IMPORTANT): 
            1-2: High Vulnerability / Low Integrity
            3-4: Moderate Vulnerability
            5: High Structural Resilience / Low Debt
            
            Return ONLY a valid JSON object with keys as categories. Include 'score' (int), 'quote', 'critique', and 'question'.
            Brief Text: {text_content[:15000]}
            """
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(prompt)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                results = json.loads(clean_json)
                
                # UI Traffic Lights
                st.divider()
                for cat, data in results.items():
                    score = int(data.get('score', 0))
                    if score == 5:
                        st.success(f"🟢 {cat} (Score: {score}/5)")
                    elif score >= 3:
                        st.warning(f"🟡 {cat} (Score: {score}/5)")
                    else:
                        st.error(f"🔴 {cat} (Score: {score}/5)")
                    
                    st.write(f"**Critique:** {data.get('critique')}")
                    st.info(f"**Dialogue Question:** {data.get('question')}")
                
                # PDF Generation
                pdf = IntegrityPDF()
                pdf.add_page()
                for cat, data in results.items():
                    pdf.add_category(cat, int(data.get('score', 0)), data.get('critique'), data.get('question'), data.get('quote'))
                
                # PDF Footer Links
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 10, "Next Steps & Resources", 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 8, "Strategy Guide: https://samillingworth.gumroad.com/l/integrity-debt-audit", 0, 1)
                pdf.cell(0, 8, f"Contact: {email_user} | sam.illingworth@gmail.com", 0, 1)

                pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='ignore')
                st.download_button(
                    label="Download Professional PDF Report",
                    data=pdf_bytes,
                    file_name="Integrity_Debt_Audit.pdf",
                    mime="application/pdf",
                    key="download_pdf_btn"
                )

            except Exception as e:
                st.error(f"Diagnostic failed: {e}")

st.markdown("---")
st.caption("🔒 Documents are processed in-memory and are not stored or used for model training.")
