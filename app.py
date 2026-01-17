import streamlit as st
import google.generativeai as genai
import json
from pypdf import PdfReader
from docx import Document
import io

# 1. Configuration & Persona
st.set_page_config(page_title="Integrity Debt Diagnostic", page_icon="⚖️", layout="wide")

# Custom CSS for readability
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 900px; }
    .stAlert { border-radius: 0px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. Header & Interpretation Guide
st.title("Integrity Debt Diagnostic")
st.markdown("""
**"If a machine can pass your assessment, the failure lies in the curriculum design, not the student’s character."**

### How to use this tool
This diagnostic is not a 'policing' tool. It is designed to expose **Integrity Debt**—structural vulnerabilities in assessment design that make them susceptible to AI automation. 

**Use these results to:**
* **Start a Dialogue**: Share the report with colleagues to discuss curriculum redesign.
* **Engage Students**: Use the 'Qualifying Questions' to discuss why certain assessment formats are chosen.
* **Prioritize Change**: Identify which modules require immediate intervention versus those with inherent resilience.
""")

st.divider()

# 3. Sidebar Configuration
with st.sidebar:
    st.header("1. Authentication")
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.warning("Please provide an API Key to proceed.")
        st.stop()

    st.header("2. Audit Parameters")
    expectation = st.selectbox(
        "Predicted Susceptibility:",
        ["Low", "Medium", "High"],
        help="What is your gut feeling about this assessment's vulnerability to AI?"
    )
    email = st.text_input("Email (for consultancy follow-up):")

# 4. Core Logic Functions
def extract_text(uploaded_file):
    text = ""
    if uploaded_file.name.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text()
    elif uploaded_file.name.endswith('.docx'):
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

def create_report_text(results, total_score):
    report = f"INTEGRITY DEBT AUDIT REPORT\nTotal Score: {total_score}/50\n\n"
    for cat, data in results.items():
        report += f"--- {cat} ---\nScore: {data.get('score')}\nCritique: {data.get('critique')}\nQuestion: {data.get('question')}\n\n"
    return report

# 5. File Upload & Execution
uploaded_file = st.file_uploader("Upload Assessment Brief (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file and expectation and email:
    if st.button("Run Integrity Audit"):
        text_content = extract_text(uploaded_file)
        
        with st.spinner("Analyzing curriculum resilience..."):
            prompt = f"""
            You are Professor Sam Illingworth. Audit this assessment brief using the 10 categories of Integrity Debt (Illingworth, 2026).
            Categories: 1. Weighting, 2. Documentation, 3. Context, 4. Reflection, 5. Time, 6. Multimodal, 7. Interrogation, 8. Defence, 9. Collaborative, 10. Recency.
            
            Return ONLY a valid JSON object. Keys must be category names. Values must include:
            - "score": (Integer 1-5, where 5 is high debt/vulnerability)
            - "quote": (Short evidence quote from text)
            - "critique": (1-sentence blunt, pedagogical critique)
            - "question": (A qualifying question for staff-student dialogue)

            Brief Text: {text_content[:15000]}
            """
            
            try:
                # Robust Model Selection
                model_name = 'gemini-1.5-flash-latest'
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                except Exception:
                    valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model = genai.GenerativeModel(valid_models[0])
                    response = model.generate_content(prompt)

                # JSON Parsing
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                results = json.loads(clean_json)
                
                # Scoring
                valid_scores = [int(v.get('score', 0)) for v in results.values() if str(v.get('score')).isdigit()]
                total = sum(valid_scores)
                
                st.subheader(f"Total Integrity Debt Score: {total}/50")
                
                # Gap Analysis
                actual_cat = "Low" if total <= 20 else "Medium" if total <= 35 else "High"
                if actual_cat == expectation:
                    st.success(f"Audit confirms your assessment: {actual_cat} susceptibility.")
                else:
                    st.warning(f"Integrity Gap: You expected {expectation}, but findings suggest {actual_cat}.")

                # Display Results
                for cat, data in results.items():
                    with st.expander(f"{cat} (Score: {data.get('score', 'N/A')}/5)"):
                        st.write(f"**Critique:** {data.get('critique')}")
                        st.write(f"**Dialogue Question:** *{data.get('question')}*")
                        st.caption(f"Evidence: \"{data.get('quote')}\"")

                # Report Download
                report_data = create_report_text(results, total)
                st.download_button(
                    label="Download Audit Report (.txt)",
                    data=report_data,
                    file_name="integrity_audit_report.txt",
                    mime="text/plain"
                )

                st.divider()
                st.markdown("### Strategy & Consultancy")
                st.markdown("High Integrity Debt threatens institutional reputation. **[Download the Strategy Guide](https://samillingworth.gumroad.com/l/integrity-debt-audit)** or email [sam.illingworth@gmail.com](mailto:sam.illingworth@gmail.com).")

            except Exception as e:
                st.error(f"Diagnostic failed: {e}")

# Footer for Privacy
st.markdown("---")
st.caption("🔒 **Privacy Note**: Uploaded documents are processed in-memory for the audit and are not stored or used for model training.")
