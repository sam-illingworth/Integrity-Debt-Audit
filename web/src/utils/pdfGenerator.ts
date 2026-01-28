import jsPDF from "jspdf";
import type { AuditResult } from "../types";
import { PEDAGOGICAL_CONTEXT, IMPROVEMENT_ACTIONS } from "../types";

export function generatePDF(
  auditResult: AuditResult
): jsPDF {
  const pdf = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  });

  const pageHeight = pdf.internal.pageSize.getHeight();
  const pageWidth = pdf.internal.pageSize.getWidth();
  const margin = 20;
  const contentWidth = pageWidth - margin * 2;

  let currentY = margin;

  // Colors
  const primaryColor: [number, number, number] = [45, 77, 74];
  const bgCream: [number, number, number] = [247, 243, 233];
  const textColor: [number, number, number] = [45, 77, 74];
  const accentBlue: [number, number, number] = [52, 152, 219];
  const successGreen: [number, number, number] = [39, 174, 96];
  const warningOrange: [number, number, number] = [243, 156, 18];
  const dangerRed: [number, number, number] = [231, 76, 60];

  function checkPageBreak(height: number) {
    if (currentY + height > pageHeight - margin) {
      pdf.addPage();
      currentY = margin;
    }
  }

  function safeText(text: string | null): string {
    if (!text) return "N/A";
    return String(text)
      .replace(/[\u2013\u2014]/g, "-")
      .replace(/[\u2018\u2019]/g, "'")
      .replace(/[\u201c\u201d]/g, '"')
      .replace(/[\u2026]/g, "...")
      .replace(/[\u2022]/g, "*");
  }

  // Header
  pdf.setFillColor(...bgCream);
  pdf.rect(0, 0, pageWidth, 35, "F");
  pdf.setTextColor(...primaryColor);
  pdf.setFontSize(18);
  pdf.setFont("helvetica", "bold");
  pdf.text("Integrity Debt Audit Report", margin, 12);
  pdf.setFontSize(11);
  pdf.setFont("helvetica", "italic");
  pdf.text("Framework by Professor Sam Illingworth", margin, 20);
  currentY = 40;

  // Executive Summary
  checkPageBreak(60);
  pdf.setFontSize(16);
  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...primaryColor);
  pdf.text("Executive Summary", margin, currentY);
  currentY += 10;

  // Summary Box
  pdf.setFillColor(...[245, 247, 250]);
  pdf.setDrawColor(220, 220, 220);
  pdf.rect(margin, currentY, contentWidth, 40, "FD");

  pdf.setFontSize(11);
  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...primaryColor);
  pdf.text("Context:", margin + 5, currentY + 8);
  pdf.setFont("helvetica", "");
  pdf.setTextColor(...textColor);
  const contextLines = pdf.splitTextToSize(
    safeText(auditResult.doc_context),
    contentWidth - 10
  );
  pdf.text(contextLines, margin + 35, currentY + 8);

  const scoreColor =
    auditResult.total_score! >= 40
      ? successGreen
      : auditResult.total_score! >= 25
        ? warningOrange
        : dangerRed;

  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...primaryColor);
  pdf.text("Integrity Score:", margin + 5, currentY + 28);
  pdf.setTextColor(...scoreColor);
  pdf.setFontSize(14);
  pdf.setFont("helvetica", "bold");
  pdf.text(`${auditResult.total_score}/50`, margin + 50, currentY + 28);

  pdf.setFontSize(11);
  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...primaryColor);
  pdf.text("Susceptibility:", margin + 100, currentY + 28);
  pdf.setTextColor(...scoreColor);
  pdf.text(
    auditResult.susceptibility!.split("(")[0].trim(),
    margin + 135,
    currentY + 28
  );

  currentY += 50;

  // Top 3 Priority Improvements
  checkPageBreak(30);
  pdf.setFontSize(14);
  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...primaryColor);
  pdf.text("Top 3 Priority Improvements", margin, currentY);
  currentY += 8;

  pdf.setFontSize(11);
  pdf.setFont("helvetica", "");
  for (let i = 0; i < Math.min(3, auditResult.top_improvements.length); i++) {
    pdf.setTextColor(...accentBlue);
    pdf.text(`${i + 1}.`, margin, currentY);
    pdf.setTextColor(...textColor);
    const impLines = pdf.splitTextToSize(
      safeText(auditResult.top_improvements[i]),
      contentWidth - 10
    );
    pdf.text(impLines, margin + 7, currentY);
    currentY += impLines.length * 5 + 3;
  }

  currentY += 5;

  // Category Deep Dives
  for (const result of auditResult.audit_results) {
    checkPageBreak(70);

    const catScore = result.verified_score || result.score;
    const catAccent =
      catScore >= 4
        ? successGreen
        : catScore === 3
          ? warningOrange
          : dangerRed;
    const status = catScore >= 4 ? "RESILIENT" : catScore === 3 ? "MODERATE" : "VULNERABLE";

    // Category Header
    pdf.setFillColor(...catAccent);
    pdf.rect(margin, currentY + 2, 2, 8, "F");

    pdf.setFontSize(12);
    pdf.setFont("helvetica", "bold");
    pdf.setTextColor(...primaryColor);
    pdf.text(safeText(result.category), margin + 5, currentY + 8);

    pdf.setTextColor(...catAccent);
    pdf.text(`Score: ${catScore}/5 | ${status}`, pageWidth - margin - 40, currentY + 8);

    currentY += 12;

    // Critique
    pdf.setFontSize(10);
    pdf.setFont("helvetica", "bold");
    pdf.setTextColor(...primaryColor);
    pdf.text("Your Assessment Analysis:", margin, currentY);
    currentY += 6;

    pdf.setFont("helvetica", "");
    pdf.setTextColor(...textColor);
    const critiqueLines = pdf.splitTextToSize(
      safeText(result.critique),
      contentWidth
    );
    pdf.text(critiqueLines, margin, currentY);
    currentY += critiqueLines.length * 5 + 3;

    // Pedagogical Context
    const context =
      PEDAGOGICAL_CONTEXT[result.category] ||
      "No pedagogical context available.";
    pdf.setFont("helvetica", "bold");
    pdf.setTextColor(...primaryColor);
    const theoryHeader =
      catScore >= 4
        ? "Why This Strength Matters:"
        : catScore === 3
          ? "Why Addressing This Gap Matters:"
          : "Why This Vulnerability Is Critical:";
    pdf.text(theoryHeader, margin, currentY);
    currentY += 6;

    pdf.setFont("helvetica", "");
    pdf.setTextColor(...textColor);
    pdf.setFillColor(...bgCream);
    const contextLines = pdf.splitTextToSize(safeText(context), contentWidth);
    pdf.text(contextLines, margin, currentY);
    currentY += contextLines.length * 5 + 4;

    // Practical Steps
    pdf.setFont("helvetica", "bold");
    pdf.setTextColor(...primaryColor);
    pdf.text("Practical Steps to Strengthen This:", margin, currentY);
    currentY += 6;

    const actions = IMPROVEMENT_ACTIONS[result.category] || [];
    pdf.setFont("helvetica", "");
    for (let i = 0; i < actions.length; i++) {
      pdf.setTextColor(...accentBlue);
      pdf.text(`${i + 1}.`, margin, currentY);
      pdf.setTextColor(...textColor);
      const actionLines = pdf.splitTextToSize(
        safeText(actions[i]),
        contentWidth - 7
      );
      pdf.text(actionLines, margin + 7, currentY);
      currentY += actionLines.length * 5 + 2;
    }

    currentY += 3;

    // Discuss With Team
    pdf.setFont("helvetica", "bold");
    pdf.setTextColor(...primaryColor);
    pdf.text("Discuss With Your Team:", margin, currentY);
    currentY += 6;

    pdf.setFont("helvetica", "italic");
    pdf.setTextColor(...textColor);
    const questionLines = pdf.splitTextToSize(
      safeText(result.question),
      contentWidth
    );
    pdf.text(questionLines, margin, currentY);
    currentY += questionLines.length * 5 + 3;

    // Evidence Quote
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(9);
    pdf.setTextColor(...primaryColor);
    pdf.text("Where We Found This in Your Brief:", margin, currentY);
    currentY += 6;

    pdf.setFont("courier", "");
    pdf.setTextColor(80, 80, 80);
    pdf.setFillColor(250, 250, 250);
    pdf.setDrawColor(230, 230, 230);
    const quoteLines = pdf.splitTextToSize(
      `"${safeText(result.quote)}"`,
      contentWidth - 2
    );
    pdf.text(quoteLines, margin + 1, currentY);
    pdf.rect(margin, currentY - 5, contentWidth, quoteLines.length * 5 + 4, "D");

    currentY += quoteLines.length * 5 + 8;
  }

  // Next Steps
  pdf.addPage();
  currentY = margin;

  pdf.setFontSize(16);
  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...primaryColor);
  pdf.text("What To Do Next", margin, currentY);
  currentY += 12;

  const steps = [
    {
      title: "Step 1: Review Your Priority Actions",
      text: "Focus on the priority first. Pick one concrete action from that category and implement it in your next assessment iteration. Do not try to fix everything at once.",
    },
    {
      title: "Step 2: Share This Report",
      text: "Bring this PDF to your next curriculum planning meeting. Use the reflection questions in each category to start conversations with colleagues about assessment redesign.",
    },
    {
      title: "Step 3: Re-Audit After Changes",
      text: "After implementing improvements, run your revised assessment through the tool again to measure progress. Track your score over time.",
    },
    {
      title: "Step 4: Get Support If Needed",
      text: "If you are facing institutional resistance or need help prioritising across multiple modules, consider booking a strategy call.",
    },
  ];

  pdf.setFontSize(10);
  for (const step of steps) {
    checkPageBreak(20);
    pdf.setFont("helvetica", "bold");
    pdf.setTextColor(...primaryColor);
    pdf.text(step.title, margin, currentY);
    currentY += 6;

    pdf.setFont("helvetica", "");
    pdf.setTextColor(...textColor);
    const stepLines = pdf.splitTextToSize(step.text, contentWidth);
    pdf.text(stepLines, margin, currentY);
    currentY += stepLines.length * 5 + 4;
  }

  // Citation
  checkPageBreak(15);
  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...primaryColor);
  pdf.text("Cite This Framework", margin, currentY);
  currentY += 8;

  pdf.setDrawColor(200, 200, 200);
  pdf.setFillColor(250, 250, 250);
  pdf.rect(margin, currentY, contentWidth, 15, "FD");

  pdf.setFontSize(9);
  pdf.setFont("helvetica", "");
  pdf.setTextColor(...textColor);
  pdf.text("Illingworth, S. (2026). The Integrity Debt Audit.", margin + 3, currentY + 4);
  pdf.setFont("helvetica", "underline");
  pdf.setTextColor(0, 0, 255);
  pdf.text(
    "https://integrity-debt-audit.streamlit.app/",
    margin + 3,
    currentY + 9
  );

  // Contact
  checkPageBreak(20);
  currentY += 20;

  pdf.setFillColor(...bgCream);
  pdf.rect(margin, currentY, contentWidth, 3, "F");
  pdf.setFontSize(12);
  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...primaryColor);
  pdf.text("Need Support with Implementation?", margin + 3, currentY + 2);
  currentY += 8;

  pdf.setFontSize(10);
  pdf.setFont("helvetica", "");
  pdf.setTextColor(...textColor);
  pdf.setFillColor(245, 247, 250);
  pdf.setDrawColor(220, 220, 220);
  const contactText =
    "As a Full Professor with over 20 years experience working in higher education, I can help you interpret your results and redesign your assessments for AI resilience.";
  const contactLines = pdf.splitTextToSize(contactText, contentWidth - 2);
  pdf.text(contactLines, margin + 2, currentY);
  pdf.rect(margin, currentY - 4, contentWidth, contactLines.length * 5 + 3, "D");

  currentY += contactLines.length * 5 + 8;

  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...textColor);
  pdf.text("Book a strategy call:", margin, currentY);
  pdf.setFont("helvetica", "underline");
  pdf.setTextColor(0, 0, 255);
  pdf.text("sam.illingworth@gmail.com", margin + 50, currentY);

  currentY += 6;
  pdf.setFont("helvetica", "bold");
  pdf.setTextColor(...textColor);
  pdf.text("Join Slow AI:", margin, currentY);
  pdf.setFont("helvetica", "underline");
  pdf.setTextColor(0, 0, 255);
  pdf.text("theslowai.substack.com", margin + 35, currentY);

  return pdf;
}
