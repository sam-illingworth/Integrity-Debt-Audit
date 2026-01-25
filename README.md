# Integrity Debt Audit

**"If a machine can pass your assessment, the failure lies in the curriculum design, not the student's character."**

[**Try the Audit Tool**](https://integrity-debt-audit.streamlit.app/) | [**Download the Strategy Guide**](https://samillingworth.gumroad.com/l/integrity-debt-audit) | [**Contact for Consultancy**](mailto:sam.illingworth@gmail.com)

---

![Integrity Debt Diagnostic Interface](screenshot.png)

The **Integrity Debt Audit** is an AI-powered tool for Higher Education professionals to audit assessment briefs against the **10 Categories of Integrity Debt** (Illingworth, 2026). It identifies vulnerabilities to AI automation and provides analytical critiques to support curriculum redesign.

## Core Methodology

The audit evaluates uploaded documents (PDF/DOCX) across ten critical dimensions:

1.  **Final product weighting**: Proportion of credit distributed across formative vs. summative stages.
2.  **Iterative documentation**: Requirement for evidence of the messy middle of learning (drafts, rejected ideas, process logs).
3.  **Contextual specificity**: Connection to specific local, temporal, or classroom contexts that AI cannot access.
4.  **Reflective criticality**: Requirement for deep, subjective personal synthesis rather than generic reflection.
5.  **Temporal friction**: Time-based constraints that make rapid completion physically impossible.
6.  **Multimodal evidence**: Requirement for non-textual outputs (audio, physical artifacts, hand-drawn elements).
7.  **Explicit AI interrogation**: Requirement for students to critique or analyze AI-generated outputs.
8.  **Real-time defence**: Presence of live interaction (viva, presentation, unscripted Q&A).
9.  **Social and collaborative labour**: Requirement for verified group work and peer accountability.
10. **Data recency**: Reliance on events, datasets, or information from the last fortnight to two weeks.

Each category is scored from 1 (Slow AI/Resilient) to 5 (Fast AI/Vulnerable), with a total possible score of 50.

## Scoring Interpretation

- **10–20: Pedagogical Sovereignty** — Your assessment prioritizes human agency and is resilient to AI automation.
- **21–35: Structural Drift** — Your assessment has integrity debt that may lead to shallow learning and automation risk.
- **36–50: Critical Integrity Failure** — Your assessment is currently highly vulnerable to AI automation.

## Technical Configuration

### Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create `.streamlit/secrets.toml` and add: `GEMINI_API_KEY = "your_key"`.
4. Run: `streamlit run app.py`.

### Deployment
* **Platform**: Streamlit Cloud.
* **API**: Google AI Studio (Gemini 1.5 Flash).
* **Secrets**: Add `GEMINI_API_KEY` in the Streamlit Cloud dashboard under **Advanced Settings > Secrets**.

## Intellectual Property & Consultancy

This tool is a proof-of-concept for the **Integrity Debt** framework. High scores indicate high vulnerability, threatening institutional reputation and pedagogical validity.

* **Strategy Guide**: [Download the full guide](https://samillingworth.gumroad.com/l/integrity-debt-audit)
* **Consultancy**: Contact [sam.illingworth@gmail.com](mailto:sam.illingworth@gmail.com) for curriculum audit and redesign workshops.
