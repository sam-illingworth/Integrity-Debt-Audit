import streamlit as st
import google.generativeai as genai
import json
from pypdf import PdfReader
from docx import Document
from fpdf import FPDF
import io

# 1. Configuration
st.set_page_config(page_title="Integrity Debt Diagnostic", page_icon="⚖️", layout="wide")

# 2. PDF Generation Function
class IntegrityReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Integrity Debt Audit Report', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, label, score):
        # Traffic Light Logic: 5=Green, 3-4=Yellow, 1-2=Red
        if score == 5:
            self.set_fill_color(200, 255, 200) # Green
        elif score >= 3:
            self.set_fill_color(255, 255, 200) # Yellow
        else:
            self.set_fill_color(255, 200, 200) # Red
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f"{label} (Score: {score}/5)", 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, critique, question, quote):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, f"Critique: {critique}")
        self.ln(1)
        self.set_font('Arial', 'I', 10)
        self.multi_cell(0, 5, f"Dialogue Question: {question}")
        self.ln(1)
        self.set_font('Arial', '', 8)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 5, f"Evidence: \"{quote}\"")
        self.set_text_color(0, 0, 0)
        self.ln(5)

# 3. Sidebar Authentication
with st.sidebar:
    st.header("Authentication")
    api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.stop()
    
    expectation = st.selectbox("Predicted Susceptibility:", ["Low", "Medium", "High"])
    email_user = st.text_input("Your Email:")

# 4. Main UI
st.title("Integrity Debt Diagnostic")
st.markdown("""Use these results to start a dialogue with staff and students regarding assessment resilience.""")

uploaded_file = st.file_uploader("Upload Brief", type=["pdf", "docx"])

if uploaded_file and st.button("Run Audit"):
    # Text Extraction Logic (omitted for brevity, same as previous)
    text_content = "" # (Assumed extraction happens here)
    
    with st.spinner("Analyzing..."):
        # API Call & JSON Parsing Logic (same as previous)
        results = {} # (Assumed AI returns results)
        
        # Display with Traffic Lights
        total_score = 0
        for cat, data in results.items():
            score = int(data.get('score', 0))
            total_score += score
            
            # UI Traffic Light
            if score == 5:
                color = "green"
                icon = "🟢"
            elif score >= 3:
                color = "orange"
                icon = "🟡"
            else:
                color = "red"
                icon = "🔴"
            
            with st.expander(f"{icon} {cat} (Score: {score}/5)"):
                st.write(f"**Critique:** {data.get('critique')}")
                st.info(f"**Dialogue:** {data.get('question')}")

        # PDF Export
        pdf = IntegrityReport()
        pdf.add_page()
        for cat, data in results.items():
            pdf.chapter_title(cat, int(data.get('score', 0)))
            pdf.chapter_body(data.get('critique'), data.get('question'), data.get('quote'))
        
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 10, "Next Steps & Consultancy", 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, "Strategy Guide: https://samillingworth.gumroad.com/l/integrity-debt-audit", 0, 1)
        pdf.cell(0, 10, f"Contact: {email_user} or sam.illingworth@gmail.com", 0, 1)

        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button("Download Professional PDF Report", pdf_output, "Integrity_Audit.pdf", "application/pdf")
