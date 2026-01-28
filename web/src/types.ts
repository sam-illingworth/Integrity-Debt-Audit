export interface CategoryResult {
  category: string;
  score: number;
  critique: string;
  question: string;
  quote: string;
  verified_score?: number;
}

export interface AuditResult {
  doc_context: string;
  top_improvements: string[];
  audit_results: CategoryResult[];
  email?: string;
  total_score?: number;
  susceptibility?: string;
}

export const INTEGRITY_CATEGORIES = [
  "Final product weighting",
  "Iterative documentation",
  "Contextual specificity",
  "Reflective criticality",
  "Temporal friction",
  "Multimodal evidence",
  "Explicit AI interrogation",
  "Real-time defence",
  "Social and collaborative labour",
  "Data recency",
];

export const PEDAGOGICAL_CONTEXT: Record<string, string> = {
  "Final product weighting":
    "When all the marks sit on a single final deadline, students feel pressure to deliver a polished product at any cost. That makes AI tempting. If you spread the marks across drafts, feedback responses, and planning stages, you reward the actual learning journey. Students cannot fake sustained engagement over weeks. The process becomes more valuable than the final polish.",
  "Iterative documentation":
    "AI tools hide their tracks. They produce seamless, polished text instantly. Real human learning is messy. It involves false starts, abandoned ideas, and gradual improvements. When you ask students to show this messiness through lab books, draft annotations, or revision logs, you make AI automation much harder. The struggle to develop an idea cannot be faked overnight.",
  "Contextual specificity":
    "AI models train on generic textbook knowledge. They excel at broad theoretical questions. They struggle with specific contexts like your classroom debate last Tuesday, the local council decision students witnessed, or the guest speaker who challenged conventional thinking. When you anchor assessments in unique moments and places, AI cannot replicate that specificity without the student having actually been there.",
  "Reflective criticality":
    "Generic professional reflection is easy to automate. AI can produce convincing statements like 'I learned the importance of teamwork.' But genuine reflection requires vulnerability. It asks students to describe specific moments of confusion, physical sensations of discomfort, and how their values shifted. AI cannot fabricate lived experience. Only humans can connect theory to what it felt like to fail and try again.",
  "Temporal friction":
    "If an assessment can be completed in one night, it will be. AI thrives on speed. Building in time delays makes automation much harder. Longitudinal studies require data collection over weeks. Peer review cycles force students to wait for feedback before progressing. Sequential deadlines prevent sprinting. When time itself becomes part of the assessment structure, students must engage with the material over the long term.",
  "Multimodal evidence":
    "Text is AI's native format. Word documents are trivially easy to automate. But when you ask for a hand-drawn concept map photographed and annotated, a 3-minute audio reflection, or a physical model presented in class, you move students beyond the textbox. These modes require different types of engagement. They add layers of human authenticity that pure text cannot match.",
  "Explicit AI interrogation":
    "Banning AI does not work. Students use it anyway. Instead, bring the tool into the classroom as something to study and critique. Ask students to generate AI content, then spend the assessment identifying its errors, biases, and missing nuance. This transforms AI from a hidden shortcut into the object of critical analysis. It teaches students that human expertise matters because AI fails in predictable ways.",
  "Real-time defence":
    "Live conversation reveals understanding in ways written text cannot. AI can draft perfect scripts. It cannot handle spontaneous questions about methodology. It cannot justify choices on the spot. A 10-minute viva, a live presentation with Q&A, or peer critique sessions force students to think aloud. This shifts the dynamic from surveillance to dialogue. Authentic ownership becomes visible through unscripted speech.",
  "Social and collaborative labour":
    "Automation is solitary. Genuine learning thrives in groups. When students must explain their thinking to peers, respond to challenges, give feedback, and negotiate ideas together, they create witnesses to their process. Verified group work, observed collaboration, and graded peer feedback make it much harder to outsource the task to AI. Social friction creates accountability.",
  "Data recency":
    "AI training data is always historical. It knows the past well but struggles with the present. When you ask students to analyse this morning's headlines, this week's policy change, or datasets released in the last fortnight, you create a knowledge barrier. AI will hallucinate or guess. Students must engage with current events. This tethers assessments to the living world rather than static textbook content.",
};

export const IMPROVEMENT_ACTIONS: Record<string, string[]> = {
  "Final product weighting": [
    "Allocate 20% of marks to the initial research plan",
    "Require a 'response to feedback' log as part of the final submission",
    "Use scaffolded deadlines throughout the module",
  ],
  "Iterative documentation": [
    "Mandate the use of a weekly digital or physical lab book/process log",
    "Include a 'failed paths' section where students explain ideas they abandoned",
    "Encourage version control or tracked changes as evidence",
  ],
  "Contextual specificity": [
    "Reference a specific guest speaker or seminar debate in the prompt",
    "Require students to apply theory to a local community issue",
    "Update prompts every semester to reflect the current political or social climate",
  ],
  "Reflective criticality": [
    "Ask for 'I' statements and specific sensory details of the learning experience",
    "Encourage non-standard formats like reflective poetry or audio diaries",
    "Require students to link specific personal values to the academic content",
  ],
  "Temporal friction": [
    "Build in a mandated peer-review cycle in week 6 of a 12-week module",
    "Require data collection that occurs at specific intervals",
    "Design tasks that require sequential steps that cannot be bypassed",
  ],
  "Multimodal evidence": [
    "Replace one essay with a 5-minute narrated video or podcast",
    "Require hand-drawn diagrams or mind maps to be scanned and included",
    "Use pitch sessions where students explain concepts verbally",
  ],
  "Explicit AI interrogation": [
    "Set an assessment where the goal is to break the AI's logic",
    "Task students with fact-checking a synthetic essay",
    "Discuss the ethical and environmental costs of AI in the classroom",
  ],
  "Real-time defence": [
    "Implement 10-minute 'flash vivas' for high-stakes work",
    "Use in-class critique sessions where peers question each other's methodology",
    "Record short verbal feedback loops between tutor and student",
  ],
  "Social and collaborative labour": [
    "Grade the quality of the feedback a student gives to their teammates",
    "Use collaborative drafting sessions during seminar time",
    "Require a reflective log on the challenges of the group dynamic",
  ],
  "Data recency": [
    "Use 'this morning's headlines' as the basis for a theory application",
    "Require students to use the most recent 6 months of a specific journal",
    "Set tasks based on live, streaming data or current social media trends",
  ],
};
