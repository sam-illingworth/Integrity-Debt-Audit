import type { AuditResult } from "../types";
import { INTEGRITY_CATEGORIES } from "../types";

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_SUPABASE_ANON_KEY;

export async function analyzeAssessment(
  assessmentText: string
): Promise<AuditResult> {
  if (!assessmentText || assessmentText.trim().length < 100) {
    throw new Error(
      "Assessment content is too short. Please provide at least 100 characters."
    );
  }

  const apiUrl = `${SUPABASE_URL}/functions/v1/analyze-assessment`;

  const response = await fetch(apiUrl, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      assessmentText: assessmentText.substring(0, 8000),
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to analyze assessment");
  }

  const data = await response.json();

  // Validate and process results
  const processedResults = processAuditResults(data);
  return processedResults;
}

function processAuditResults(data: any): AuditResult {
  let auditList = data.audit_results || [];

  // Ensure audit_list is an array
  if (!Array.isArray(auditList)) {
    if (typeof auditList === "object") {
      auditList = Object.values(auditList);
    } else {
      auditList = [];
    }
  }

  const finalResults: any = {};
  let totalScore = 0;

  // Match results to categories
  for (const catName of INTEGRITY_CATEGORIES) {
    let match = null;

    for (const item of auditList) {
      if (typeof item !== "object" || !item) continue;

      const itemCat = (item.category || "").toLowerCase();
      if (catName.toLowerCase() === itemCat || itemCat.includes(catName.toLowerCase())) {
        match = item;
        break;
      }
    }

    if (match) {
      let score = 0;

      // Extract score from various possible fields
      for (const field of ["score", "points", "rating"]) {
        if (field in match) {
          try {
            score = parseInt(match[field], 10);
            break;
          } catch {
            const scoreStr = String(match[field]);
            const scoreMatch = scoreStr.match(/\d+/);
            if (scoreMatch) {
              score = parseInt(scoreMatch[0], 10);
              break;
            }
          }
        }
      }

      // Clamp score to 1-5
      score = Math.max(1, Math.min(5, score));

      finalResults[catName] = {
        verified_score: score,
        critique: match.critique || "No critique provided",
        question: match.question || "No question provided",
        quote: match.quote || "N/A",
      };

      totalScore += score;
    } else {
      // Default placeholder
      finalResults[catName] = {
        verified_score: 3,
        critique: "Insufficient information provided to evaluate this category.",
        question: "How could this category be better addressed in your assessment?",
        quote: "N/A",
      };
      totalScore += 3;
    }
  }

  // Calculate susceptibility
  let susceptibility = "";
  if (totalScore >= 40) {
    susceptibility = "Low (Pedagogical Sovereignty)";
  } else if (totalScore >= 25) {
    susceptibility = "Medium (Structural Drift)";
  } else {
    susceptibility = "High (Critical Integrity Failure)";
  }

  return {
    doc_context: data.doc_context || "Assessment Audit",
    top_improvements: Array.isArray(data.top_improvements)
      ? data.top_improvements
      : ["Review individual categories for specific improvements"],
    audit_results: Object.entries(finalResults).map(([cat, data]: any) => ({
      category: cat,
      score: data.verified_score,
      critique: data.critique,
      question: data.question,
      quote: data.quote,
      verified_score: data.verified_score,
    })),
    total_score: totalScore,
    susceptibility: susceptibility,
  };
}
