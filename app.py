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

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title='Integrity Debt Diagnostic', 
    page_icon='⚖️', 
    layout='wide'
)

# Custom CSS for consistent white/black styling
st.markdown("""
    <style>
    .stApp { 
        background-color: white; 
        color: black; 
    }
    header {visibility: hidden;}
    .reportview-container { background: white; }
    p, span, h1, h2, h3, h4, li { color: black !important; }
    
    /* Fix all input elements */
    .stTextInput > div > div > input {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        color: black !important;
    }
    
    /* Fix select/dropdown boxes */
    .stSelectbox > div > div > div {
        background-color: white !important;
        color: black !important;
    }
    
    .stSelectbox [data-baseweb='select'] {
        background-color: white !important;
    }
    
    .stSelectbox [data-baseweb='select'] > div {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
    }
    
    /* Fix file uploader */
    [data-testid='stFileUploader'] {
        background-color: white !important;
        border: 2px dashed #d0d0d0 !important;
    }
    
    [data-testid='stFileUploader'] section {
        background-color: white !important;
        border: none !important;
    }
    
    /* Fix text area */
    .stTextArea textarea {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        color: black !important;
    }
    
    /* Fix buttons */
    .stButton > button {
        background-color: white !important;
        color: #212529 !important;
        border: 2px solid #212529 !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #f8f9fa !important;
        border: 2px solid #000000 !important;
    }
    
    .stFormSubmitButton > button {
        background-color: white !important;
        color: #212529 !important;
        border: 2px solid #212529 !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
    }
    
    .stFormSubmitButton > button:hover {
        background-color: #f8f9fa !important;
        border: 2px solid #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# DATA STRUCTURES
# =============================================================================

# The 10 integrity debt categories
INTEGRITY_CATEGORIES = [
    'Final product weighting',
    'Iterative documentation', 
    'Contextual specificity',
    'Reflective criticality',
    'Temporal friction',
    'Multimodal evidence',
    'Explicit AI interrogation',
    'Real-time defence',
    'Social and collaborative labour',
    'Data recency'
]

# Generic case studies for each score range (~100 words each)
CASE_STUDIES = {
    'Final product weighting': {
        'score_1_2': 'A research project worth 60% is broken into: research plan (10%), annotated bibliography (15%), draft with peer feedback (15%), final submission (20%). No single component dominates. Students must demonstrate iterative development across the semester, with each stage building on feedback from the previous one. This structure makes it impossible to complete the work in a last-minute rush, as each formative component feeds into the next. The emphasis shifts from producing one polished final product to demonstrating sustained engagement with the research process over time.',
        'score_3': 'Students submit a draft for feedback (5%) and then the final essay is worth 55%. The draft feels like a tick-box exercise rather than meaningful scaffolding. Whilst some process evidence is required, the overwhelming weight still rests on the final submission, creating pressure to produce a polished product regardless of how it was achieved. Students could feasibly use AI to generate the draft, receive generic feedback, and then submit an AI-polished final version with only minimal human input.',
        'score_4_5': 'The entire module is assessed by a single essay submitted in week 12. No formative work is required or even encouraged. Students could complete this in 24 hours using AI, with no process evidence, no iterative development, and no opportunity for feedback. This structure incentivises panic submissions and creates the perfect conditions for complete automation. The assessment design essentially rewards the final product whilst ignoring the learning journey entirely.'
    },
    'Iterative documentation': {
        'score_1_2': 'Students maintain a weekly lab book showing false starts, abandoned hypotheses, and evolving thinking. They submit photos of handwritten notes alongside the final polished report. Marks are allocated specifically for documenting failed approaches and explaining why certain ideas were rejected. The messiness of the research process is made visible and valued. This approach makes it extremely difficult to use AI, as the tool would need to simulate authentic confusion, dead ends, and gradual insight development across multiple weeks of documented work.',
        'score_3': 'The submission includes an annotated bibliography explaining source selection, but there is no evidence of the actual research journey or dead ends explored. Students provide brief notes on why they chose each source, which shows some process awareness, but the bulk of the intellectual scaffolding remains hidden. An AI could easily generate plausible source justifications without any genuine research having occurred. The documentation requirement exists but lacks depth and authenticity.',
        'score_4_5': 'A beautifully formatted literature review appears with perfect citations and no trace of how the student actually arrived at their conclusions. Could have been generated in minutes. The final PDF shows no revision marks, no alternative frameworks considered, no methodological pivots, no intellectual struggle. Just polished prose that could easily be the first draft from an AI. There is no way to distinguish between genuine scholarship and complete automation.'
    },
    'Contextual specificity': {
        'score_1_2': 'Apply this week\'s seminar debate about data privacy to the recent council decision on CCTV expansion in our town centre. Reference specific points raised by guest speaker Dr Martinez. The prompt is tethered to events that only students who attended could reference accurately. Local context, recent developments, and specific classroom discussions make generic AI responses impossible. Students must demonstrate they were present, engaged, and thinking critically about the unique circumstances of their learning environment.',
        'score_3': 'Analyse the 2024 supply chain crisis at Company X using Porter\'s Five Forces. The case is specific but widely covered in business news, making AI responses feasible. Whilst the prompt references a particular real-world example from the current year, the analysis framework is standard and the case has been discussed extensively online. An AI with access to recent news could produce a competent response without the student needing to engage deeply with the specific context or apply original thinking.',
        'score_4_5': 'Discuss the main theories of motivation in organisational psychology. This is a textbook question with thousands of pre-existing model answers online and in AI training data. No contextual anchoring, no contemporary application, no local relevance. A student could submit a competent response without having attended a single lecture or read any recent scholarship. The prompt is so generic that it invites generic, automatable responses.'
    },
    'Reflective criticality': {
        'score_1_2': 'Write about a specific moment during your placement where you felt uncomfortable or uncertain. Describe the physical sensations, your immediate thoughts, and how your understanding shifted afterwards. This requires deep personal honesty and sensory specificity that AI cannot fabricate. Students must write in the first person about subjective experience, emotional responses, and the physical reality of confusion or discomfort. The vulnerability and authenticity required makes generic professional language impossible. This is a lived perspective, not a performance.',
        'score_3': 'Use Gibbs\' Reflective Cycle to analyse your group work experience. Students follow the template structure but use generic professional language without genuine introspection. They describe what happened, what they thought, and what they learned, but in sanitised, surface-level terms. Phrases like \'I learned the importance of communication\' appear without any real critical engagement. An AI could easily generate plausible responses that fit the model without any authentic reflection having occurred.',
        'score_4_5': 'Reflect on your learning this semester. Responses are full of clichés like \'this experience taught me valuable lessons\' with no specific, personal detail. Completely automatable. No evidence of genuine critical thinking, no vulnerability, no specific incidents described. Just vague professional platitudes that sound reflective but contain no actual reflection. An AI could produce this in seconds, and many students do exactly that.'
    },
    'Temporal friction': {
        'score_1_2': 'Students interview the same participant three times over six weeks to track changing attitudes. The time gap is mandatory and data-stamped. Cannot be rushed. Each interview must be documented with date/time stamps and show evolution in the participant\'s perspective over time. The longitudinal design makes it physically impossible to complete the work in a single session. Students must return to the same person, demonstrate sustained engagement, and analyse patterns that only emerge across multiple weeks.',
        'score_3': 'Students must consult three physical archive documents not available online. Adds friction but a motivated student could complete this in one intensive day. They need to visit the library, request materials, and photograph or transcribe content, which creates some temporal delay. However, once the materials are accessed, the actual work could still be compressed into a short timeframe. The friction is present but not insurmountable for someone willing to sprint.',
        'score_4_5': 'Review the literature on climate policy and submit by Friday. No staged drafts, no required consultations. A student with access to AI could complete this between midnight and 6am. The entire task can be compressed into a single session with no penalty. No iterative stages, no mandatory gaps for reflection, no checkpoints that enforce sustained engagement. This design actively invites last-minute completion and maximum automation.'
    },
    'Multimodal evidence': {
        'score_1_2': 'Students submit a 1,000-word essay plus a 3-minute audio reflection plus hand-drawn concept maps photographed and annotated. Multiple modes of expression required. Each element must demonstrate understanding in a different way - written analysis, verbal explanation, visual thinking. The combination makes automation significantly harder as each mode requires different types of engagement. An AI can generate text, but integrating audio narration and hand-drawn visuals adds layers of human authenticity.',
        'score_3': 'Students create slides and submit a written script. Both text-based and easily automated. The visual element doesn\'t add meaningful friction. Whilst technically multimodal, both components can be generated by text-based AI tools. PowerPoint templates are formulaic, and written scripts are AI\'s native format. The requirement looks like it adds complexity but in practice offers minimal protection against automation.',
        'score_4_5': 'A traditional essay submitted as a Word file. AI\'s native format. Zero multimodal friction. Pure text, no visuals, no audio, no physical artefacts. This is exactly what large language models are optimised to produce. A student could prompt an AI and submit the output with minimal editing. The assessment design plays to automation\'s strengths whilst ignoring human capabilities for visual, verbal, and physical expression.'
    },
    'Explicit AI interrogation': {
        'score_1_2': 'Use ChatGPT to write a 500-word introduction to your topic. Then write 1,500 words identifying factual errors, biased framing, missing nuance, and citation gaps. Support your critique with academic sources. This assessment requires students to become expert critics of AI output. They must generate AI text, then systematically demonstrate why it\'s insufficient, inaccurate, or incomplete. The task transforms AI from a shortcut into the object of study, requiring deep subject knowledge to identify its failures.',
        'score_3': 'Students append a paragraph stating whether they used AI and how. Transparency is encouraged but there is no critical engagement with the tool\'s limitations. A simple declaration - \'I used ChatGPT to help structure my argument\' - satisfies the requirement without any analytical reflection on what the AI got right or wrong. The requirement acknowledges AI\'s presence but doesn\'t require students to think critically about its output or their reliance on it.',
        'score_4_5': 'Module handbook states \'AI tools are prohibited\' but provides no guidance, no monitoring, and no pedagogical engagement with why this matters. Students use AI anyway. The ban is performative and unenforceable. Without any educational rationale or practical alternatives offered, students simply ignore the rule and hope they don\'t get caught. The policy creates a culture of deception rather than critical engagement with AI\'s role in learning.'
    },
    'Real-time defence': {
        'score_1_2': 'After submitting their dissertation, students defend it in a 15-minute viva with two examiners asking spontaneous questions about methodology, findings, and theoretical framing. Students must think on their feet, justify decisions, explain trade-offs, and demonstrate deep understanding of their work. Questions probe areas of the dissertation that only the actual author would know intimately. This live dialogue reveals whether the student truly owns their work or has outsourced it to AI. Spontaneous synthesis cannot be scripted.',
        'score_3': 'Groups present their project, with one designated speaker delivering a scripted presentation. All members answer questions, but the script could still be AI-generated. Whilst there\'s some live interaction, the prepared nature of the presentation means much of it could be automated. The Q&A adds friction, but if only one person delivers the bulk of the content, individual accountability is reduced. Students can hide behind group dynamics.',
        'score_4_5': 'Students submit their work via Turnitin and receive written feedback two weeks later. Zero human dialogue. The marker has no evidence the student even read the sources. All interaction is asynchronous and text-based. There is no opportunity to ask \'Why did you choose this framework?\' or \'Can you explain this finding in your own words?\'. The assessment is entirely detached from the human being who supposedly did the work.'
    },
    'Social and collaborative labour': {
        'score_1_2': 'Students work in groups during class time under tutor observation. Each member presents their contribution live. Peer feedback forms are completed in class and contribute to individual grades. The collaborative process is visible, documented, and assessed. Individual contributions are witnessed by peers and tutors. Students must negotiate, compromise, explain their thinking, and respond to challenges in real time. This social accountability makes it very difficult to hide AI-generated work or minimal contribution.',
        'score_3': 'Groups submit one document and all receive the same mark. No mechanism to verify individual contribution. One student could use AI to do everything whilst others contribute nothing. The group structure provides cover for individual automation. Without differentiated grading or visible contribution tracking, there\'s no incentive for genuine collaboration. Some students will carry the load, others will disappear, and the assessment structure enables this inequality.',
        'score_4_5': 'Individual essay written alone at home with no required peer discussion, no collaborative drafting, no dialogue. Perfect conditions for complete AI automation. The student works in isolation with no witnesses to their process, no social accountability, no need to explain their thinking to others. This is exactly the condition in which AI automation thrives - solitary, invisible, unverifiable work that could be completed by human or machine with no one the wiser.'
    },
    'Data recency': {
        'score_1_2': 'Analyse this morning\'s inflation data release using the models we studied in weeks 1-5. Submit by 5pm. The data is so fresh that AI training data cannot include it. Students must access new information, apply theoretical frameworks learned in class, and synthesise original analysis within hours. No pre-existing model answers exist. The task requires genuine engagement with current events and immediate application of learning. Time-sensitive prompts create a moving target that automation cannot easily hit.',
        'score_3': 'Discuss the political developments of autumn 2024. Recent enough to show engagement, but AI models trained on rolling data can still synthesise coherent responses. The timeframe is specific but not immediate. Major events from the current semester are likely to have been discussed extensively online, meaning AI tools can draw on commentary, analysis, and frameworks that already exist. The recency adds some friction but not enough to prevent competent automated responses.',
        'score_4_5': 'Explain Maslow\'s Hierarchy of Needs. This is textbook content unchanged since 1943. AI can reproduce perfect answers from millions of training examples. No contemporary engagement required, no current application, no original thinking needed. Students can find thousands of pre-written explanations online or prompt an AI to generate a summary. The content is so static and well-documented that automation is trivial. This is AI\'s comfort zone.'
    }
}

# Improvement actions for each category (3 actions each)
IMPROVEMENT_ACTIONS = {
    'Final product weighting': [
        'Allocate 20% of marks to the initial research plan',
        'Require a \'response to feedback\' log as part of the final submission',
        'Use scaffolded deadlines throughout the module'
    ],
    'Iterative documentation': [
        'Mandate the use of a weekly digital or physical lab book/process log',
        'Include a \'failed paths\' section where students explain ideas they abandoned',
        'Encourage version control or tracked changes as evidence'
    ],
    'Contextual specificity': [
        'Reference a specific guest speaker or seminar debate in the prompt',
        'Require students to apply theory to a local community issue',
        'Update prompts every semester to reflect the current political or social climate'
    ],
    'Reflective criticality': [
        'Ask for \'I\' statements and specific sensory details of the learning experience',
        'Encourage non-standard formats like reflective poetry or audio diaries',
        'Require students to link specific personal values to the academic content'
    ],
    'Temporal friction': [
        'Build in a mandated peer-review cycle in week 6 of a 12-week module',
        'Require data collection that occurs at specific intervals',
        'Design tasks that require sequential steps that cannot be bypassed'
    ],
    'Multimodal evidence': [
        'Replace one essay with a 5-minute narrated video or podcast',
        'Require hand-drawn diagrams or mind maps to be scanned and included',
        'Use pitch sessions where students explain concepts verbally'
    ],
    'Explicit AI interrogation': [
        'Set an assessment where the goal is to break the AI\'s logic',
        'Task students with fact-checking a synthetic essay',
        'Discuss the ethical and environmental costs of AI in the classroom'
    ],
    'Real-time defence': [
        'Implement 10-minute \'flash vivas\' for high-stakes work',
        'Use in-class critique sessions where peers question each other\'s methodology',
        'Record short verbal feedback loops between tutor and student'
    ],
    'Social and collaborative labour': [
        'Grade the quality of the feedback a student gives to their teammates',
        'Use collaborative drafting sessions during seminar time',
        'Require a reflective log on the challenges of the group dynamic'
    ],
    'Data recency': [
        'Use \'this morning\'s headlines\' as the basis for a theory application',
        'Require students to use the most recent 6 months of a specific journal',
        'Set tasks based on live, streaming data or current social media trends'
    ]
}

# =============================================================================
# ENHANCED PDF CLASS
# =============================================================================

class IntegrityPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=20)
        
        # Colour palette
        self.primary_color = (45, 77, 74)      # #2D4D4A (teal)
        self.bg_cream = (247, 243, 233)        # #F7F3E9
        self.text_color_val = (45, 77, 74)     # #2D4D4A
        self.accent_blue = (52, 152, 219)    
        self.success = (39, 174, 96)           # Green (scores 4-5 = good)
        self.warning = (243, 156, 18)          # Amber (score 3 = moderate)
        self.danger = (231, 76, 60)            # Red (scores 1-2 = vulnerable)
        self.light_grey = (245, 247, 250)

    def header(self):
        self.set_fill_color(*self.bg_cream)
        self.rect(0, 0, 210, 35, 'F')
        self.set_y(10)
        self.set_font('helvetica', 'B', 18)
        self.set_text_color(*self.primary_color)
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
        self.cell(0, 10, f'Integrity Debt Audit Report | Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def safe_text(self, text):
        """Convert text to latin-1 safe version"""
        if not text:
            return 'N/A'
        text_str = str(text)
        # Replace smart quotes and special characters
        replacements = {
            '\u2013': '-', '\u2014': '-', 
            '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"',
            '\u2026': '...', '\u2022': '*'
        }
        for char, replacement in replacements.items():
            text_str = text_str.replace(char, replacement)
        return text_str.encode('latin-1', 'replace').decode('latin-1')

    def check_page_break(self, height_needed):
        """Prevent orphaned headings"""
        if self.get_y() + height_needed > self.page_break_trigger:
            self.add_page()

    def add_summary(self, susceptibility, score, improvements, doc_context):
        """Enhanced executive summary"""
        self.set_x(20)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, 'Executive Summary', 0, 1)
        self.ln(2)
        
        # Summary box
        self.set_fill_color(*self.light_grey)
        self.set_draw_color(220, 220, 220)
        box_y = self.get_y()
        self.rect(20, box_y, 170, 45, 'FD')
        
        # Context
        self.set_xy(25, box_y + 5)
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(35, 8, 'Context:', 0, 0)
        self.set_font('helvetica', '', 11)
        self.set_text_color(*self.text_color_val)
        self.multi_cell(125, 8, self.safe_text(doc_context))
        
        # Score and susceptibility
        self.set_xy(25, box_y + 28)
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(35, 8, 'Integrity Score:', 0, 0)
        
        # HIGH score (40-50) = GOOD (green), LOW (10-20) = BAD (red)
        sc_col = self.success if score >= 40 else self.warning if score >= 25 else self.danger
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(*sc_col)
        self.cell(30, 8, f'{score}/50', 0, 0)
        
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(35, 8, 'Susceptibility:', 0, 0)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(*sc_col)
        self.cell(30, 8, susceptibility, 0, 1)
        
        self.set_y(box_y + 50)
        self.set_x(20)
        self.ln(5)
        
        # Top improvements
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, 'Top 3 Priority Improvements', 0, 1)
        self.set_font('helvetica', '', 11)
        
        for i, imp in enumerate(improvements[:3], 1):
            self.set_x(20)
            self.set_text_color(*self.accent_blue)
            self.cell(10, 8, f'{i}.', 0, 0)
            self.set_text_color(*self.text_color_val)
            self.multi_cell(0, 8, self.safe_text(imp))
        
        self.ln(10)

    def add_scoring_scale_visual(self, total_score):
        """Add visual scoring scale showing where they sit"""
        self.check_page_break(40)
        
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, 'Your Score in Context', 0, 1)
        self.ln(5)
        
        # Draw the scale
        scale_y = self.get_y()
        scale_width = 170
        scale_height = 20
        
        # Three zones: 10-24 (red), 25-39 (amber), 40-50 (green)
        zone1_width = (15 / 50) * scale_width  # 10-24 = 15 points
        zone2_width = (15 / 50) * scale_width  # 25-39 = 15 points  
        zone3_width = (11 / 50) * scale_width  # 40-50 = 11 points (adjusted for 50 max)
        
        # Red zone
        self.set_fill_color(*self.danger)
        self.rect(20, scale_y, zone1_width, scale_height, 'F')
        
        # Amber zone
        self.set_fill_color(*self.warning)
        self.rect(20 + zone1_width, scale_y, zone2_width, scale_height, 'F')
        
        # Green zone
        self.set_fill_color(*self.success)
        self.rect(20 + zone1_width + zone2_width, scale_y, zone3_width, scale_height, 'F')
        
        # Draw border
        self.set_draw_color(100, 100, 100)
        self.rect(20, scale_y, scale_width, scale_height, 'D')
        
        # Add labels below
        self.set_y(scale_y + scale_height + 3)
        self.set_font('helvetica', '', 9)
        self.set_text_color(100, 100, 100)
        
        self.set_x(20)
        self.cell(zone1_width, 6, '10-24: Critical Failure', 0, 0, 'C')
        self.set_x(20 + zone1_width)
        self.cell(zone2_width, 6, '25-39: Structural Drift', 0, 0, 'C')
        self.set_x(20 + zone1_width + zone2_width)
        self.cell(zone3_width, 6, '40-50: Sovereignty', 0, 0, 'C')
        
        # Mark their score
        score_position = 20 + (total_score / 50) * scale_width
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(0, 0, 0)
        # Draw arrow pointing down
        arrow_y = scale_y - 8
        self.line(score_position, arrow_y, score_position, scale_y)
        # Triangle
        points = [
            (score_position - 3, arrow_y),
            (score_position + 3, arrow_y),
            (score_position, arrow_y + 5)
        ]
        self.set_xy(score_position - 10, arrow_y - 8)
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(0, 0, 0)
        self.cell(20, 5, f'Your score: {total_score}', 0, 0, 'C')
        
        self.ln(15)

    def add_category_deep_dive(self, name, score, critique, question, quote, case_study, actions):
        """Enhanced category page with case study and improvement actions"""
        self.check_page_break(80)  # Ensure we have space for the full section
        
        # HIGH scores (4-5) are GOOD (resilient) = GREEN
        # LOW scores (1-2) are BAD (vulnerable) = RED
        accent = self.success if score >= 4 else self.warning if score == 3 else self.danger
        status = 'RESILIENT' if score >= 4 else 'MODERATE' if score == 3 else 'VULNERABLE'
        
        # Category header with colored bar
        self.set_x(20)
        start_y = self.get_y()
        self.set_fill_color(*accent)
        self.rect(20, start_y + 2, 2, 8, 'F')
        self.set_xy(23, start_y)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(*self.primary_color)
        self.cell(120, 12, f' {self.safe_text(name)}', 0, 0, 'L')
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*accent)
        self.cell(0, 12, f'Score: {score}/5 | {status}', 0, 1, 'R')
        
        # AI-generated critique
        self.set_x(20)
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, 'Your Assessment Analysis:', 0, 1)
        self.set_x(20)
        self.set_font('helvetica', '', 10)
        self.set_text_color(*self.text_color_val)
        self.multi_cell(0, 6, self.safe_text(critique))
        self.ln(3)
        
        # Generic case study
        self.set_x(20)
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, 'What This Score Means in Practice:', 0, 1)
        self.set_x(20)
        self.set_font('helvetica', '', 9)
        self.set_text_color(*self.text_color_val)
        self.set_fill_color(250, 250, 250)
        self.multi_cell(0, 5, self.safe_text(case_study), 0, 'L', True)
        self.ln(3)
        
        # Improvement actions (contextual if available)
        self.set_x(20)
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, 'To Move Toward Slow AI:', 0, 1)
        
        for i, action in enumerate(actions, 1):
            self.set_x(20)
            self.set_font('helvetica', '', 10)
            self.set_text_color(*self.accent_blue)
            self.cell(7, 6, f'{i}.', 0, 0)
            self.set_text_color(*self.text_color_val)
            self.multi_cell(0, 6, self.safe_text(action))
        
        self.ln(2)
        
        # Reflection question
        self.set_x(20)
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, 'Dialogue Question:', 0, 1)
        self.set_x(20)
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(*self.text_color_val)
        self.multi_cell(0, 6, self.safe_text(question))
        self.ln(3)
        
        # Evidence quote
        self.set_x(20)
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(*self.primary_color)
        self.cell(0, 6, 'Evidence Reference:', 0, 1)
        self.set_x(20)
        self.set_font('courier', '', 9)
        self.set_text_color(80, 80, 80)
        self.set_fill_color(250, 250, 250)
        self.set_draw_color(230, 230, 230)
        self.multi_cell(0, 5, f'"{self.safe_text(quote)}"', 1, 'L', True)
        self.ln(8)

    def add_action_plan(self, results):
        """Pre-filled action plan with their 3 weakest categories"""
        self.check_page_break(80)
        self.add_page()
        
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, 'Your Priority Action Plan', 0, 1)
        self.ln(3)
        
        # Introductory text
        self.set_font('helvetica', '', 11)
        self.set_text_color(*self.text_color_val)
        self.multi_cell(0, 6, 'Focus your improvement efforts on these three categories where your assessment is most vulnerable. Use the suggested actions as a starting point for redesign.')
        self.ln(5)
        
        # Find 3 weakest categories (lowest scores)
        sorted_categories = sorted(results.items(), key=lambda x: x[1]['verified_score'])
        weak_categories = sorted_categories[:3]
        
        for rank, (cat_name, data) in enumerate(weak_categories, 1):
            score = data['verified_score']
            
            # Category header
            self.set_font('helvetica', 'B', 12)
            self.set_text_color(*self.primary_color)
            self.cell(0, 8, f'Priority {rank}: {cat_name} (Score: {score}/5)', 0, 1)
            
            # Actions
            self.set_font('helvetica', '', 10)
            self.set_text_color(*self.text_color_val)
            actions = IMPROVEMENT_ACTIONS.get(cat_name, ['Review this category for specific guidance'])
            
            for i, action in enumerate(actions, 1):
                self.set_x(25)
                self.set_font('helvetica', 'B', 10)
                self.set_text_color(*self.accent_blue)
                self.cell(7, 6, f'{i}.', 0, 0)
                self.set_font('helvetica', '', 10)
                self.set_text_color(*self.text_color_val)
                self.multi_cell(0, 6, self.safe_text(action))
            
            self.ln(5)

    def add_implementation_resources(self):
        """Syllabus clause template"""
        self.check_page_break(80)
        self.add_page()
        
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, 'Implementation Resources', 0, 1)
        self.ln(3)
        
        # Syllabus clause
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(*self.primary_color)
        self.cell(0, 8, 'Recommended Syllabus Language:', 0, 1)
        self.ln(2)
        
        syllabus_text = '''This module prioritises human judgement and intentional learning friction. We view the learning process as a collaborative dialogue. Whilst AI tools may be used for initial brainstorming, all final submissions must provide evidence of your individual intellectual labour. We value the 'messy middle' of learning over a polished, automated product. This focus allows us to engage deeply with your specific cognitive journey. If a submission lacks iterative documentation or a subjective perspective, we will host a formal viva voce. This is an opportunity for you to justify your choices and for us to verify authorship through conversation.'''
        
        self.set_font('helvetica', '', 10)
        self.set_text_color(*self.text_color_val)
        self.set_fill_color(*self.bg_cream)
        self.multi_cell(0, 6, self.safe_text(syllabus_text), 1, 'L', True)
        self.ln(5)
        
        # Adaptation note
        self.set_font('helvetica', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 5, 'Note: Adapt this language to suit your discipline and institutional regulations. Use this text as a starting point for classroom discussion about the value of human labour and the limitations of automation.')
        self.ln(8)

    def add_next_steps(self, total_score):
        """Personalized guidance based on score range"""
        self.check_page_break(60)
        
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, 'Next Steps', 0, 1)
        self.ln(3)
        
        # Personalized advice based on score
        if total_score >= 40:
            title = 'Pedagogical Sovereignty (40-50 points)'
            advice = '''You are prioritising human agency. Your assessments value the learning process over the final product. Students must engage with material personally, temporally, and socially. Continue refining and share your practice with colleagues. Focus on your 1-2 highest-scoring categories - can you push them toward greater resilience?'''
            color = self.success
        elif total_score >= 25:
            title = 'Structural Drift (25-39 points)'
            advice = '''You have integrity debt that will lead to shallow learning. Some protective features exist but significant gaps remain. Students can partially automate your assessments. Immediate redesign of your highest-scoring categories is recommended. Use the Priority Action Plan in this report to focus your efforts on the three weakest areas. Consider consulting with colleagues or educational developers for support.'''
            color = self.warning
        else:
            title = 'Critical Integrity Failure (10-24 points)'
            advice = '''Your degree is currently automatable. Students can complete assessments almost entirely using AI with minimal human input. This poses an existential threat to the value of your qualifications. Urgent and comprehensive redesign is required. Start with your three highest-scoring categories and implement the suggested improvements immediately. Consider booking a strategy call for expert guidance on systematic curriculum redesign.'''
            color = self.danger
        
        # Score interpretation box
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, f' {title}', 0, 1, 'L', True)
        
        self.set_fill_color(250, 250, 250)
        self.set_text_color(*self.text_color_val)
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 6, self.safe_text(advice), 1, 'L', True)
        self.ln(5)
        
        # Understanding the scoring
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(*self.primary_color)
        self.cell(0, 8, 'Understanding Your Scores:', 0, 1)
        
        self.set_font('helvetica', '', 10)
        self.set_text_color(*self.text_color_val)
        
        scoring_text = '''Each category is scored from 1 to 5:
• Scores 1-2 (Red/Vulnerable): High risk of AI automation. Requires urgent attention.
• Score 3 (Amber/Moderate): Some protection but significant gaps remain. Moderate redesign recommended.
• Scores 4-5 (Green/Resilient): Strong AI-resistant design. Continue these practices.

Your total score (out of 50) indicates overall curriculum resilience to AI automation.'''
        
        self.multi_cell(0, 6, scoring_text)
        self.ln(8)

    def add_contact_box(self):
        """Contact information and consultancy CTA"""
        self.check_page_break(50)
        self.ln(10)
        
        self.set_x(20)
        self.set_fill_color(*self.bg_cream)
        self.set_text_color(*self.primary_color)
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, ' Strategic Consultancy & Bespoke Support', 0, 1, 'L', True)
        
        self.set_fill_color(245, 247, 250)
        self.set_text_color(*self.text_color_val)
        self.set_font('helvetica', '', 10)
        self.set_x(20)
        
        contact_txt = '''As a Full Professor with over 20 years experience of working in higher education, I can help interpret your diagnostic results to develop AI-resilient assessments and curricula.

Book a strategy call to plan your curriculum redesign: sam.illingworth@gmail.com

Join the Slow AI community: https://theslowai.substack.com'''
        
        self.multi_cell(0, 6, self.safe_text(contact_txt), 1, 'L', True)
        self.ln(8)

    def add_citation_box(self):
        """Academic citation information"""
        self.check_page_break(40)
        
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(*self.primary_color)
        self.cell(0, 8, 'Cite This Framework:', 0, 1)
        self.ln(2)
        
        citation_text = '''Illingworth, S. (2026). The Integrity Debt Audit: A diagnostic framework for AI-resistant assessment design. https://integrity-debt-audit.streamlit.app/'''
        
        self.set_font('helvetica', '', 10)
        self.set_text_color(*self.text_color_val)
        self.set_fill_color(250, 250, 250)
        self.multi_cell(0, 6, self.safe_text(citation_text), 1, 'L', True)
        self.ln(5)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def extract_text(uploaded_file):
    """Extract text from PDF or DOCX files"""
    text = ''
    try:
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() or ''
        elif uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text + '\n'
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text += cell.text + ' '
                    text += '\n'
    except Exception as e:
        st.error(f'Extraction error: {e}')
    return text

def scrape_url(url):
    """Extract text from a URL"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'li', 'td'])
        return '\n'.join([t.get_text() for t in tags])
    except Exception as e:
        return f'Error: {str(e)}'

def clean_json_string(raw_string):
    """Clean JSON string from AI response"""
    cleaned = re.sub(r'```json\s*|\s*```', '', raw_string)
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    return match.group(0) if match else cleaned.strip()

@st.cache_resource
def discover_model(api_key):
    """Discover available Gemini model"""
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() 
                 if 'generateContent' in m.supported_generation_methods]
        flash = [m for m in models if 'flash' in m]
        return flash[0] if flash else models[0]
    except:
        return 'models/gemini-1.5-flash'

# =============================================================================
# STREAMLIT INTERFACE
# =============================================================================

st.title('Integrity Debt Diagnostic')
st.caption('🔒 Privacy Statement: This tool is stateless. Assessment briefs are processed in-memory.')

st.markdown('''
### Introduction
The **Integrity Debt Audit** is a diagnostic tool for Higher Education professionals to evaluate the resilience of their curriculum against AI automation.

**How it works:**
1. **Upload or paste** your assessment brief (the document you give to students)
2. **Receive automated analysis** across 10 categories of AI vulnerability
3. **Download a comprehensive report** with case studies, improvement strategies, and action plans

This tool analyses your assessment and provides specific, actionable guidance for redesign.

For the complete framework and theoretical background, visit: [Beyond AI Detection](https://samillingworth.gumroad.com/l/integrity-debt-audit).
''')

c1, c2 = st.columns([2, 1])
with c1:
    st.markdown('''
    ### Pre-Audit Checklist
    Include the task description, learning outcomes, and submission formats for accurate results.
    ''')
with c2:
    st.info('**The Scoring System**\n* 🟢 4-5: Resilient\n* 🟡 3: Moderate\n* 🔴 1-2: Vulnerable')

st.divider()

# Session state management
if 'audit_complete' not in st.session_state:
    st.session_state.audit_complete = False

# Form for input
with st.container():
    if not st.session_state.audit_complete:
        with st.form('audit_form'):
            st.subheader('1. Setup')
            sc1, sc2 = st.columns(2)
            with sc1:
                email_user = st.text_input('Your Email (required):')
            with sc2:
                expectation = st.selectbox('Predicted Susceptibility:', ['Low', 'Medium', 'High'])
            
            st.subheader('2. Assessment Input')
            input_type = st.radio('Choose Input Method:', ['File Upload', 'Paste Text or URL'])
            
            uploaded_file = None
            raw_input = ''
            
            if input_type == 'File Upload':
                uploaded_file = st.file_uploader('Upload Brief', type=['pdf', 'docx'])
            else:
                raw_input = st.text_area('Paste Content or Public URL:', height=200)
            
            submit_button = st.form_submit_button('Generate Diagnostic Report')
    else:
        if st.button('Audit New Brief'):
            st.session_state.audit_complete = False
            st.rerun()

# Processing logic
api_key = st.secrets.get('GEMINI_API_KEY')

if not st.session_state.audit_complete and 'submit_button' in locals() and submit_button:
    if not api_key or not email_user:
        st.error('Email and Secrets configuration required.')
    else:
        # Extract text
        if input_type == 'File Upload' and uploaded_file:
            final_text = extract_text(uploaded_file)
        elif raw_input:
            final_text = scrape_url(raw_input) if raw_input.startswith('http') else raw_input
        else:
            final_text = ''
        
        if not final_text:
            st.error('No assessment content provided.')
        else:
            with st.spinner('Analysing your assessment against the Integrity Debt framework...'):
                try:
                    target = discover_model(api_key)
                    model = genai.GenerativeModel(
                        target,
                        generation_config={'temperature': 0.0, 'top_p': 0.1, 'top_k': 1}
                    )
                    
                    # Build prompt
                    cat_list = ', '.join(INTEGRITY_CATEGORIES)
                    
                    prompt = f'''You are Professor Sam Illingworth conducting an Integrity Debt Audit.

Analyse the following assessment brief against these 10 categories: {cat_list}

SCORING RULES (CRITICAL):
- Score 1-2: VULNERABLE (red) - High AI automation risk, weak safeguards
- Score 3: MODERATE (amber) - Some protection but significant gaps
- Score 4-5: RESILIENT (green) - Strong AI-resistant design

For EACH category, provide:
- category: exact name from list
- score: 1-5 (where 1-2=vulnerable, 3=moderate, 4-5=resilient)
- critique: specific analysis of THIS assessment (2-3 sentences)
- question: reflection question for the educator
- quote: brief evidence from the assessment text

Also provide:
- doc_context: brief title/description of the assessment
- top_improvements: array of 3 specific priority actions

Return ONLY valid JSON. No markdown, no preamble.

Format:
{{
  "doc_context": "Assessment title",
  "top_improvements": ["action 1", "action 2", "action 3"],
  "audit_results": [
    {{
      "category": "Final product weighting",
      "score": 2,
      "critique": "Analysis here",
      "question": "Question here",
      "quote": "Evidence here"
    }}
  ]
}}

Assessment text:
{final_text[:8000]}'''
                    
                    response = model.generate_content(prompt)
                    res_raw = clean_json_string(response.text)
                    
                    try:
                        res_json = json.loads(res_raw)
                    except json.JSONDecodeError as json_err:
                        st.error('AI response could not be parsed. This sometimes happens with complex assessments.')
                        st.error('Try: Shortening your assessment text slightly, removing special characters, or trying again.')
                        with st.expander('Show AI Response (for debugging)'):
                            st.code(res_raw)
                        st.stop()
                    
                    # Validate response
                    if not isinstance(res_json, dict):
                        st.error('AI returned invalid response format.')
                        st.stop()
                    
                    if res_json.get('status') == 'error':
                        st.error('No clear assessment task could be identified in the provided text.')
                        st.stop()
                    
                    # Store and display
                    st.session_state.res_json = res_json
                    st.session_state.audit_complete = True
                    st.rerun()
                    
                except Exception as e:
                    st.error(f'Audit failed: {e}')
                    st.error('This may be due to API limits or connectivity issues. Please try again.')

# Display results
if st.session_state.audit_complete:
    res_json = st.session_state.res_json
    
    # Process results
    total_score = 0
    final_audit_results = {}
    audit_list = res_json.get('audit_results', [])
    
    # Ensure audit_list is a list
    if not isinstance(audit_list, list):
        if isinstance(audit_list, dict):
            audit_list = list(audit_list.values())
        else:
            audit_list = []
    
    # Match results to categories
    for cat_name in INTEGRITY_CATEGORIES:
        match = None
        for item in audit_list:
            if not isinstance(item, dict):
                continue
            item_cat = item.get('category', '').lower()
            if cat_name.lower() in item_cat or item_cat in cat_name.lower():
                match = item
                break
        
        if match:
            # Extract score
            score = 0
            for field in ['score', 'points', 'rating']:
                if field in match:
                    try:
                        score = int(match[field])
                        break
                    except (ValueError, TypeError):
                        score_str = str(match[field])
                        score_match = re.search(r'\d+', score_str)
                        if score_match:
                            score = int(score_match.group(0))
                            break
            
            # Clamp score
            score = max(1, min(5, score))
            
            final_audit_results[cat_name] = {
                'verified_score': score,
                'critique': match.get('critique', 'No critique provided'),
                'question': match.get('question', 'No question provided'),
                'quote': match.get('quote', 'No quote provided')
            }
            total_score += score
        else:
            # Placeholder
            final_audit_results[cat_name] = {
                'verified_score': 3,
                'critique': 'Insufficient information provided to evaluate this category.',
                'question': 'How could this category be better addressed in your assessment?',
                'quote': 'N/A'
            }
            total_score += 3
    
    # Get context and improvements
    ctx = res_json.get('doc_context', 'Assessment Audit')
    imps = res_json.get('top_improvements', ['Review individual categories for specific improvements'])
    
    if not isinstance(imps, list):
        imps = [str(imps)]
    
    # Calculate susceptibility
    if total_score >= 40:
        susceptibility = 'Low'
    elif total_score >= 25:
        susceptibility = 'Medium'
    else:
        susceptibility = 'High'
    
    # Display summary
    st.markdown("""
        <style>
        h2, h3 {
            color: #2D4D4A !important;
        }
        [data-testid='stMetricValue'] {
            color: #2D4D4A !important;
            font-size: 2rem !important;
            font-weight: bold !important;
        }
        [data-testid='stMetricLabel'] {
            color: #2D4D4A !important;
            font-weight: 600 !important;
        }
        [data-testid='stExpander'] {
            background-color: #f8f9fa !important;
            border: 1px solid #dee2e6 !important;
        }
        [data-testid='stExpander'] p {
            color: #212529 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.subheader(f'Diagnostic Focus: {ctx}')
    
    col1, col2 = st.columns(2)
    with col1:
        score_color = '🟢' if total_score >= 40 else '🟡' if total_score >= 25 else '🔴'
        st.metric('Integrity Score', f'{score_color} {total_score}/50')
    with col2:
        st.metric('AI Susceptibility', susceptibility)
    
    st.markdown("""
        <p style='color: #856404; background-color: #fff3cd; padding: 12px; border-radius: 4px; border-left: 4px solid #ffc107;'>
        ⚠️ <strong>Note:</strong> The comprehensive PDF report below includes case studies, improvement strategies, and action plans. This browser view is a summary only.
        </p>
    """, unsafe_allow_html=True)
    
    # Generate enhanced PDF
    pdf = IntegrityPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Add all enhanced sections
    pdf.add_summary(susceptibility, total_score, imps, ctx)
    pdf.add_scoring_scale_visual(total_score)
    
    for cat_name, data in final_audit_results.items():
        score = data['verified_score']
        
        # Determine which case study to use
        if score <= 2:
            case_study = CASE_STUDIES[cat_name]['score_1_2']
        elif score == 3:
            case_study = CASE_STUDIES[cat_name]['score_3']
        else:
            case_study = CASE_STUDIES[cat_name]['score_4_5']
        
        # Get improvement actions
        actions = IMPROVEMENT_ACTIONS[cat_name]
        
        pdf.add_category_deep_dive(
            cat_name,
            score,
            data['critique'],
            data['question'],
            data['quote'],
            case_study,
            actions
        )
    
    pdf.add_action_plan(final_audit_results)
    pdf.add_implementation_resources()
    pdf.add_next_steps(total_score)
    pdf.add_contact_box()
    pdf.add_citation_box()
    
    # Download button
    st.markdown("""
        <style>
        .stDownloadButton > button {
            background-color: white !important;
            color: #212529 !important;
            border: 2px solid #212529 !important;
            padding: 16px 32px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            width: 100% !important;
            margin: 20px 0 !important;
        }
        .stDownloadButton > button:hover {
            background-color: #f8f9fa !important;
            border: 2px solid #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.download_button(
        '📥 Download Comprehensive Report (PDF)',
        data=bytes(pdf.output()),
        file_name='Integrity_Debt_Audit_Report.pdf',
        mime='application/pdf'
    )
    
    st.divider()
    
    # Category breakdown
    st.subheader('Category Breakdown')
    
    for cat_name, data in final_audit_results.items():
        score = data['verified_score']
        label = '🟢' if score >= 4 else '🟡' if score == 3 else '🔴'
        
        with st.expander(f'{label} **{cat_name}** ({score}/5)'):
            st.markdown(f'**Analysis:** {data["critique"]}')
            st.markdown(f'**Reflection Question:** {data["question"]}')
            if data['quote'] != 'N/A':
                st.markdown(f'**Evidence:** _{data["quote"]}_')
    
    st.divider()
    st.caption('End of summary. For full case studies, improvement strategies, and action plans, please download the comprehensive PDF report above.')
