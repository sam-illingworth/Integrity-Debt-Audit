import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from docx import Document
import json

# Set Page Title and UX
st.set_page_config(page_title="Integrity Debt Diagnostic", layout="wide")

st.markdown("""
# Integrity Debt Diagnostic
**If a machine can pass your assessment, the failure lies in the curriculum design, not the student’s character.**

This tool is a diagnostic for Higher Education professionals to evaluate curriculum resilience. Select one specific assessment brief (e.g., a final module essay) to audit.
""")

# Setup Gemini API - Fetches from "Secrets" in production
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        if api_key:
            genai.configure(api_key=api_key)

# 1. User Context
st.header("1. Module Context")
col1, col2 = st.columns(2)
with col1:
    email = st.text_input("Work Email Address")
with col2:
    role = st.selectbox("Your Role", ["", "Staff / Educator", "Student", "Other"])

expectation = st.selectbox(
    "Initial Assumption: How susceptible is this assessment to AI automation?",
    ["", "Low", "Medium", "High"]
)

# 2. File Ingestion
st.header("2. Upload Assessment Brief")
uploaded_file = st.file_uploader("Upload PDF or DOCX file", type=["pdf", "docx"])

def extract_text(file):
    if file.type == "application/pdf":
        return " ".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return " ".join([para.text for para in Document(file).paragraphs])
    return ""

# 3. Audit Execution
if uploaded_file and expectation and email:
    if st.button("Run Integrity Audit"):
        text_content = extract_text(uploaded_file)
        
        with st.spinner("Analyzing curriculum resilience..."):
            prompt = f"""
            You are Professor Sam Illingworth. Audit this assessment brief using the 10 categories of Integrity Debt (Illingworth, 2026):
            1. Weighting, 2. Documentation, 3. Context, 4. Reflection, 5. Time, 6. Multimodal, 7. Interrogation, 8. Defence, 9. Collaborative, 10. Recency.
            
            Return ONLY a valid JSON object. For each category:
            - "score": (Integer 1-5, or "N/A" if missing)
            - "quote": (Direct quote from the text)
            - "critique": (1-sentence blunt, analytical critique)
            - "question": (Qualifying question if score is N/A)

            Assessment Brief Text: {text_content[:15000]}
            """
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                
                # Clean response for valid JSON
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                results = json.loads(clean_json)
                
                valid_scores = [v['score'] for v in results.values() if isinstance(v['score'], int)]
                total = sum(valid_scores)
                
                st.markdown("---")
                st.subheader(f"Total Integrity Debt Score: {total}/50")
                
                # Gap Analysis
                actual_cat = "Low" if total <= 20 else "Medium" if total <= 35 else "High"
                if actual_cat == expectation:
                    st.success(f"Audit confirms your assessment: {actual_cat} susceptibility.")
                else:
                    st.warning(f"Integrity Gap: You expected {expectation} susceptibility, but the diagnostic reveals it is {actual_cat}.")

                # Result Display
                for cat, data in results.items():
                    with st.expander(f"{cat} - Score: {data['score']}"):
                        st.write(f"**Critique:** {data['critique']}")
                        if data['score'] != "N/A":
                            st.caption(f"Evidence: \"{data['quote']}\"")
                        else:
                            st.write(f"**Qualifying Question:** {data['question']}")

                # Consultancy Link
                st.markdown("---")
                st.markdown("### Strategy & Consultancy")
                st.markdown("High Integrity Debt threatens institutional reputation. **[Download the Strategy Guide](https://samillingworth.gumroad.com/l/integrity-debt-audit)** or email me at [sam.illingworth@gmail.com](mailto:sam.illingworth@gmail.com) to discuss curriculum redesign.")

            except Exception as e:
                st.error(f"Diagnostic failed: {e}")